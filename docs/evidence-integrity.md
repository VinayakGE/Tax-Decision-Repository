# Wave 2 — Evidence Integrity Engine

> Rules R-0007 through R-0014.
> Every downstream decision depends on the evidence being trustworthy.
> This wave answers: "Can I trust the evidence before I use it?"

---

## Motivation

Wave 1 (R-0001 through R-0006) established what income is and which decision path applies. Wave 2 asks a harder question: is the evidence that produced those classifications accurate, complete, internally consistent, and traceable?

A perfect tax computation on corrupted input is worse than no computation — it produces a confidently wrong answer.

The Evidence Integrity Engine runs as part of Pipeline Stage 7 (Conflict Resolver) and Stage 11 (Trace Generator). Its outputs feed directly into:

- **Confidence Model**: integrity failures reduce ECS and lower the confidence band
- **Conflict Log**: discrepancies become typed conflict entries
- **Validation Engine**: some integrity failures trigger validations (V-001, V-002)
- **Explanation Engine**: the lineage graph answers "why is my refund X?"

---

## Four Submodules

### Module A — Source Reconciliation (R-0007, R-0008, R-0009, R-0010, R-0011)

Compare all evidence sources against each other. Determine whether they agree, whether discrepancies are minor (auto-resolved) or major (conflict), and whether the same income is being double-counted.

**Reconciliation Status Values:**

| Status | Delta | Meaning | Action |
|--------|-------|---------|--------|
| `reconciled` | < 1% | Sources agree within rounding | Proceed; use higher-authority source value |
| `minor_variance` | 1%–5% | Small discrepancy | Flag for review; proceed with warning; notify in confidence report |
| `major_variance` | > 5% | Significant discrepancy | Add to conflict log; reduce ECS; ask user |
| `presence_mismatch` | N/A | Entry in one source, absent in other | Add to conflict log; trigger V-002 if income missing from AIS |
| `duplicate` | N/A | Same item counted in two sources | Remove one; log the resolution |

**Evidence Authority Hierarchy** (from `docs/confidence-model.md`):
```
26AS > AIS ≈ Form 16 > Prefill JSON > User declaration
```
When two sources conflict, the higher-authority source wins.

---

### Module B — Evidence Completeness (R-0012)

Determine whether the evidence that *should* exist for this taxpayer's profile actually exists. Absence of evidence is not the same as evidence of absence.

**Completeness classification per missing item:**

| Missing Evidence | Classification | ECS Impact |
|-----------------|---------------|-----------|
| 26AS not loaded | `critical_missing` | −30 |
| AIS not loaded | `critical_missing` | −25 |
| Form 16 absent when 192 TDS in 26AS | `expected_missing` | −15 |
| Broker statement absent when AIS shows capital gains | `expected_missing` | −20 |
| Form 16A absent when TDS u/s 194A/194J in 26AS | `expected_missing` | −10 |
| Prefill JSON not loaded | `acceptable_absent` | −5 |
| Form 26QB absent when property sale in AIS | `expected_missing` | −10 |

---

### Module C — Evidence Authenticity (R-0013)

Determine whether each document is internally valid. These are data quality checks, not tax decisions.

**Authenticity checks:**

| Check | What it validates | Failure type |
|-------|-----------------|-------------|
| PAN consistency | PAN in all documents matches the filing PAN | `pan_mismatch` |
| TAN format | TAN follows `AAAA99999A` format (4 alpha + 5 numeric + 1 alpha) | `invalid_tan` |
| Assessment year | All documents reference the current AY | `ay_mismatch` |
| Duplicate TDS entries | No two entries in 26AS share the same TAN + quarter + amount | `duplicate_tds_entry` |
| Duplicate AIS entries | No two AIS entries share the same source + category + amount | `duplicate_ais_entry` |
| Prefill JSON version | Prefill JSON schema version is current (not from prior AY) | `stale_prefill` |
| Form 16 employer TAN | TAN on Form 16 matches 26AS TDS entry for the same employer | `tan_mismatch` |

---

### Module D — Evidence Lineage (R-0014)

Build the computation provenance graph. Every computed value in the system — from gross income to final refund — must trace back to a specific field in a specific evidence document, or to a specific rule applied to evidence.

This is what makes Jarviz explainable without generating explanations. When a user asks "why is my refund ₹56,310?", Stage 13 traverses the lineage graph rather than asking the AI to reason about it.

**Lineage Node Types:**

| Type | Meaning |
|------|---------|
| `evidence` | Leaf node — a raw field from a document |
| `rule_applied` | Internal node — a rule transformed inputs to an output |
| `computed` | Internal node — arithmetic on children (sum, subtract, etc.) |
| `user_declared` | Leaf node — a value provided by the user in response to an intake question |

**Lineage Graph Shape (example):**
```
refund: 30400 [computed]
├── total_tax: 0 [computed]
│   ├── slab_tax: 30400 [computed, rule: R-XXXX]
│   │   └── taxable_income: 802200 [computed]
│   │       ├── head_1_salary: 765000 [computed]
│   │       │   ├── gross_salary: 840000 [evidence: E-004/Form16.gross_salary]
│   │       │   └── standard_deduction: 75000 [rule_applied: tax-tables/AY2025-26]
│   │       ├── head_3_business: 19200 [computed, rule: R-0004]
│   │       │   └── turnover: 320000 [evidence: E-001/AIS.business_receipts]
│   │       └── head_5_other_sources: 18000 [computed]
│   │           └── fd_interest: 18000 [evidence: E-001/AIS.interest_fd]
│   └── rebate_87A: 30400 [rule_applied: R-XXXX, Section 87A]
│       └── eligibility: income 802200 ≤ 1200000 limit [rule_applied: tax-tables]
└── tds_credit: 30400 [computed]
    ├── tds_192: 28600 [evidence: E-002/26AS.tds[TAN=BLRX12345A]]
    └── tds_194A: 1800 [evidence: E-002/26AS.tds[TAN=HDFC0001]]
```

---

## Sequencing

The four modules run in this order within the pipeline:

```
Stage 7: Conflict Resolver
  → Module A: Source Reconciliation (R-0007, R-0008, R-0009)
  → Module A: Duplicate Detection (R-0010, R-0011)
  → Module B: Completeness Check (R-0012)
  → Module C: Authenticity Validation (R-0013)

Stage 11: Trace Generator
  → Module D: Evidence Lineage Generation (R-0014)
```

Modules A, B, and C must complete before Stage 8 (Decision Engine) runs. Module D runs after Stage 10 (Validation Engine) completes, using all outputs from Stages 8–10.

---

## JAB M-07: Evidence Integrity Score

The benchmark metric for this wave:

```
Evidence_Integrity_Score = cases where all integrity checks pass / total_cases × 100
```

A case passes integrity if: Modules A, B, C all return no unresolved conflicts (minor_variance and acceptable_absent are permitted; major_variance, critical_missing, or any authenticity failure is not).

**Target:** ≥ 95%

**Why this precedes all accuracy metrics:** If M-07 is low, improving M-01 (ITR accuracy) or M-02 (refund accuracy) won't help — the engine is reasoning over inconsistent evidence. Evidence integrity is a prerequisite for decision accuracy.
