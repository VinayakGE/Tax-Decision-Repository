# Tax Decision Journey

> The bridge between what a taxpayer asks and what the engine answers.

Rules answer questions. This document maps the questions users actually ask to the journeys those questions trigger. Every journey follows the same arc — but the entry point, evidence, and decision are different for each question.

This is a product document, not a technical one. It is written in the language of the taxpayer, not the rule engine.

---

## The Universal Journey Arc

Every tax question — no matter how simple or complex — moves through the same seven stages.

```
Question
    ↓
Evidence Required
    ↓
Evidence Validation
    ↓
Applicable Rules
    ↓
Tax Decision
    ↓
Confidence
    ↓
Explanation → Required Actions
```

The engine executes stages 2–6 deterministically. Stages 1 and 7 are the user-facing surfaces — the question asked and the answer delivered.

---

## Journey 1: "Should I choose the New Regime or Old Regime?"

**Who asks this:** Every salaried taxpayer, every year. The default is New Regime — but that is not always the right answer.

### Question
> "Which regime saves me more tax this year?"

### Evidence Required

| Document | Why it's needed |
|----------|----------------|
| Form 16 | Gross salary, existing TDS, employer's regime assumption |
| Proof of 80C investments | EPF, PPF, ELSS, LIC premium — only matter in Old Regime |
| NPS statement | 80CCD(1B) deduction — available in both regimes |
| Rent receipts + landlord PAN | HRA exemption — only in Old Regime |
| Home loan statement | 24(b) interest deduction — only in Old Regime |
| Health insurance receipts | 80D — only in Old Regime |

Minimum viable evidence: Form 16 only. The engine can produce a regime recommendation with Form 16 alone, but will flag it as "estimated — deductions unverified."

### Evidence Validation

The engine runs Wave 2 checks before computation:
- AIS and 26AS salary figures reconcile (R-0007)
- No duplicate salary entries from multiple employers (R-0010)
- Form 16 PAN matches 26AS (R-0013)

If AIS shows income not in Form 16, it asks the user before proceeding.

### Applicable Rules

| Step | Rule | What happens |
|------|------|-------------|
| 1 | R-0015 | Assembles total income by head; applies standard deduction (₹75K New / ₹50K Old) |
| 2 | R-0017 | Computes New Regime tax on assembled income using Finance Act 2024 slabs |
| 3 | R-0016 | Computes Old Regime tax — adjusts for age bracket if taxpayer is 60+ |
| 4 | R-0019 | Applies Section 87A rebate to each regime (₹60K / ₹12L for New; ₹12.5K / ₹5L for Old) |
| 5 | R-0021 | Applies surcharge if income > ₹50L |
| 6 | R-0020 | Applies 4% cess to both |
| 7 | R-0018 | Compares the two final figures; produces recommendation and savings amount |

### Tax Decision

```
Regime: NEW REGIME  (or OLD REGIME)
New Regime total tax: ₹44,200
Old Regime total tax: ₹61,880
You save: ₹17,680 under New Regime
```

Or:

```
Regime: OLD REGIME
New Regime total tax: ₹1,24,800
Old Regime total tax: ₹96,200
You save: ₹28,600 under Old Regime
Switch requires: Inform employer by March 31 (Form 12BAA)
```

### Confidence

- **High (Band A):** Form 16 + all deduction proofs uploaded and verified against AIS
- **Medium (Band B):** Form 16 uploaded; deductions declared by user but not evidenced
- **Low (Band C):** Form 16 only; no deduction information — estimate flagged

### Explanation

> "Your salary is ₹12,00,000. Under the New Regime, after a ₹75,000 standard deduction, your taxable income is ₹11,25,000. This falls within the 15% slab bracket, giving a slab tax of ₹1,01,250 — but wait: your total income is ₹12L which is exactly at the 87A rebate limit, so you receive a ₹60,000 rebate, reducing tax to ₹41,250. With 4% cess, total = ₹42,900."
>
> "Under the Old Regime, your deductions total ₹2,75,000 (₹1.5L 80C + ₹50K NPS + ₹50K standard deduction + ₹25K 80D). Taxable income = ₹9,25,000. Slab tax = ₹1,02,500. No 87A rebate (income > ₹5L). With cess, total = ₹1,06,600."
>
> "**New Regime saves ₹63,700.** Your deductions are not large enough to make Old Regime beneficial."

### Required Actions

- If staying in New Regime: No action needed (it is the default).
- If switching to Old Regime: Submit Form 12BAA to employer before March 31 of the financial year.
- If employer has already deducted TDS on Old Regime basis: Claim refund by filing ITR under New Regime.

---

## Journey 2: "Can I claim HRA?"

**Who asks this:** Salaried taxpayers paying rent who have not opted for the New Regime, or are deciding whether Old Regime is worth switching to.

### Question
> "How much HRA can I claim? Is it worth switching to Old Regime for this?"

### Evidence Required

| Document | Why it's needed |
|----------|----------------|
| Form 16 | HRA component of salary, basic salary figure |
| Rent receipts | 12 monthly receipts for the year |
| Landlord PAN | Mandatory if annual rent > ₹1,00,000 (₹8,333/month) |
| Rental agreement | Corroborates rent amount and address |

HRA is **not available under the New Regime.** If the user is in New Regime, this journey ends with: "HRA exemption is not available in the New Regime. Consider whether switching to Old Regime would benefit you — see Journey 1."

### Evidence Validation

- Form 16 HRA component vs AIS (R-0007/R-0008 reconciliation)
- Landlord PAN authenticity check (R-0013)
- Rent amount consistency: receipts vs rental agreement (R-0013)

### Applicable Rules

Wave 3B (Tax Adjustment Engine) handles HRA computation. This journey is **planned** — it will be available once Wave 3B rules are authored.

The formula, when implemented:

```
HRA Exempt = min(
  actual_HRA_received_from_employer,
  50% of basic salary (metro) OR 40% (non-metro),
  actual_rent_paid - 10% of basic salary
)
```

Metro cities: Delhi, Mumbai, Chennai, Kolkata.

### Tax Decision *(Wave 3B — Planned)*

```
HRA exemption: ₹1,44,000
HRA taxable: ₹36,000
Net tax saving vs New Regime: ₹43,200 (15% slab rate on ₹1,44,000)
Old Regime is beneficial: Yes — see Journey 1 for full comparison
```

### Required Actions

- Collect 12 months of rent receipts.
- If rent > ₹1L/year: obtain landlord PAN.
- Submit rent receipts to employer for TDS adjustment, or claim at ITR filing time.
- Declare Old Regime to employer if switching (Form 12BAA before March 31).

---

## Journey 3: "Why is my refund ₹X — I expected more?"

**Who asks this:** Taxpayers who have checked their 26AS or Form 16, roughly estimated their refund, and find the Jarviz number doesn't match their expectation.

### Question
> "I expected a refund of ₹50,000. Jarviz says ₹31,200. Why?"

### Evidence Required

The engine already has this information if the return has been computed. This journey is a **replay query**, not a new computation.

### Evidence Validation (Replay)

The engine reviews the Decision Execution Log (DEL) for this case and checks:

1. Was there a reconciliation discrepancy? (R-0007: AIS vs 26AS variance)
2. Was any TDS credit excluded because it was only in Prefill, not in 26AS? (R-0009: unclaimed_credit_risk)
3. Was any income added from AIS that wasn't in Form 16? (V-002 candidate)
4. Was interest under 234A/B/C added to the demand? (R-0022)
5. Was any special-rate income (LTCG, lottery) taxed separately?

### Applicable Rules (Trace)

The engine walks the Evidence Lineage DAG (R-0014) backwards from the refund figure:

```
Refund: ₹31,200
    ↑
Total Tax: ₹33,800  (R-0020, R-0021, R-0019)
    ↑
TDS Credit: ₹65,000  (R-0023 — sourced from 26AS only)
    ↑
Taxable Income: ₹9,25,000  (R-0015)
    ↑
Salary: ₹10,00,000  (Form 16 → AIS → 26AS reconciled at R-0007)
    ↑
FD Interest: ₹22,000  (AIS — not in Prefill; added per R-0008)
                       ↑ This is often the surprise
```

### Tax Decision (Explanation of Gap)

The engine identifies the specific reason(s) the refund differs from the user's expectation:

| Reason | Amount | Rule |
|--------|--------|------|
| FD interest added from AIS (not in Form 16) | +₹3,300 tax | R-0008 |
| Prefill TDS of ₹5,000 not in 26AS — excluded | -₹5,000 refund | R-0009 |
| Interest u/s 234B (advance tax shortfall on FD income) | -₹660 | R-0022 |
| **Total gap vs expectation** | **-₹18,960** | |

### Confidence

High — this journey replays a completed computation. The lineage DAG makes every number traceable.

### Explanation

> "You expected ₹50,000 back, but the actual refund is ₹31,200. Here is exactly why:
>
> 1. Your AIS shows FD interest income of ₹22,000 that wasn't in your Form 16. This income is taxable and adds ₹3,300 to your tax.
>
> 2. Your Prefill JSON showed a TDS credit of ₹5,000, but this entry does not appear in your 26AS. Under CBDT Circular 2/2021, only TDS in 26AS can be claimed as a credit. This ₹5,000 cannot be used, reducing your refund by ₹5,000.
>
> 3. Because you had income outside salary (FD interest), advance tax applies. You didn't pay advance tax on this income, so ₹660 interest under Section 234B has been added.
>
> Total adjustments: ₹3,300 + ₹5,000 + ₹660 = ₹8,960 less than you expected. Plus your original tax estimate may have been based on a rough calculation."

### Required Actions

- Verify the FD interest in AIS is correct; if wrong, raise a feedback on the IT portal.
- Resolve the missing 26AS TDS entry with the deductor (your bank), or write off the ₹5,000 credit.
- To avoid 234B interest next year: pay advance tax in September if you have income outside salary exceeding ₹10,000 tax liability.

---

## Journey 4: "Which ITR form should I file?"

**Who asks this:** Taxpayers who are unsure whether they need ITR-1, ITR-2, or ITR-4 — especially when they have more than one income source.

### Question
> "I have salary income and some interest income and one FD. Which form do I file?"

### Evidence Required

| Document | Why it's needed |
|----------|----------------|
| AIS | Lists all income types reported for the year |
| Form 16 | Confirms salary income and employer |
| 26AS | Confirms TDS entries and income sources |

Minimum viable: AIS alone. The engine can determine ITR form eligibility from income types listed in AIS.

### Evidence Validation

- AIS completeness check (R-0012): is AIS loaded?
- Pattern matching: which of the 8 patterns does this case match?

### Applicable Rules

| Rule | What it decides |
|------|----------------|
| R-0006 | Classifies each income item by head |
| R-0001 | Disqualifies ITR-1 if business/profession income exists |
| R-0002 | Confirms ITR-1 eligibility: salary + HP + other sources, income ≤ ₹50L |
| R-0003 | Requires ITR-2 if foreign assets or foreign income present |
| R-0004 | Routes to ITR-4 if presumptive income (44AD/44ADA) elected |

### Tax Decision

```
Income sources found: Salary (Form 16), FD Interest (AIS)
Head 1 — Salary: ₹8,40,000
Head 5 — Other Sources (FD interest): ₹28,000
Total income: ₹8,68,000

ITR Form: ITR-1 (Sahaj)
Reason: Salary + other sources only, income ≤ ₹50L, no foreign assets,
        no capital gains, no business income.
```

### Confidence

High if AIS is complete and no ambiguous income categories exist.

### Explanation

> "Your income has two sources: salary from your employer and FD interest from your bank. Both fall under ITR-1 (Sahaj). You do not have capital gains, business income, foreign assets, or more than one house property — all the situations that would require a more complex form. ITR-1 is the simplest form and is filed entirely online."

### Required Actions

- File ITR-1 before 31 July 2025.
- Verify bank account is pre-validated on the IT portal for refund credit (V-003).
- Cross-check that 26AS TDS entries match what your employer and bank deducted.

---

## Mapping: Customer Questions to Journeys

| Customer Question | Journey | Engine Capability |
|------------------|---------|------------------|
| "New Regime or Old Regime?" | Journey 1 | ✅ Wave 3A complete |
| "Can I claim HRA?" | Journey 2 | ⏳ Wave 3B planned |
| "Why is my refund X?" | Journey 3 | 🟡 Requires replay + lineage |
| "Which ITR form?" | Journey 4 | ✅ Wave 1 complete |
| "Am I eligible for 80C?" | — | ⏳ Wave 3B planned |
| "Do I need to pay advance tax?" | — | 🟡 R-0022 models this |
| "My AIS shows income I don't recognize" | — | 🟡 V-002 candidate |
| "Why was my previous year's refund smaller?" | — | ⏳ Requires Decision Replay |
| "I got a notice from IT dept — what do I do?" | — | ❌ Not in current scope |

---

## The Question Layer

The journeys above reveal a pattern: before the engine can run, it needs to know what the user is asking. This is the **Question Layer** — the layer that sits above Evidence, above Rules, above everything.

```
Customer Question
        ↓
Intent Classification
(What decision is the user trying to make?)
        ↓
Evidence Checklist
(What documents are required for this specific question?)
        ↓
[Jarviz Engine: Evidence → Classification → Integrity → Computation]
        ↓
Answer in the user's language
```

The Intent Classification step is where Jarviz identifies: is this a regime selection question? A refund explanation? An ITR eligibility check? Once the intent is known, the engine fetches the right evidence checklist and routes to the right pipeline stages.

This is the next product design challenge — and it is a product design challenge, not an architecture challenge. The rule engine underneath is already capable of answering all of these questions. The work remaining is building the front door that routes the user's natural language question to the right journey.

---

## Design Principle: Rules Answer Questions; Journeys Connect Them to Customers

The Tax Decision Engine is complete only when:

1. The rule produces a decision
2. The decision traces back to evidence
3. The evidence traces back to a question the customer actually asked
4. The explanation is in language the customer understands

Point 4 is not the Explanation Engine's job alone. It starts here — in how journeys are designed. An explanation that says "R-0019 rebate applied per Section 87A, income ≤ threshold" is not an explanation. An explanation that says "Your income is exactly ₹12L, which qualifies you for a ₹60,000 rebate — your tax bill drops to ₹20,000 instead of ₹80,000" is.

Every journey in this document is a specification for what the Explanation Engine must produce.

---

*Last updated: 2026-06-26 (Wave 3A — Tax Computation Engine)*
