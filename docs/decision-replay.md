# Decision Replay

> Every case processed by Jarviz produces an immutable replay record.
> The replay record is the audit trail, the regression corpus, and the feedback loop.

---

## Purpose

A Decision Replay record captures everything that happened during a single pipeline execution: the raw evidence that was provided, every decision made, every rule evaluated, every validation run, every question asked, and the final outcome. It also stores — after the fact — what the taxpayer actually filed and whether a notice was received.

The replay record serves four functions:

1. **Audit trail** — "Why did Jarviz recommend ITR-4?" is always answerable from the replay.
2. **Regression corpus** — Replay records become test cases for future rule changes.
3. **Benchmark source** — Gold Standard Set cases in the JAB are built from verified replay records.
4. **Feedback loop** — When a user says "the CA told me to file ITR-3", that correction is recorded in the replay and triggers rule review.

---

## Relationship to Decision Execution Log (DEL)

The replay record and the DEL are separate objects stored together:

| Object | Purpose | When created | Mutability |
|--------|---------|-------------|-----------|
| DEL | Per-execution operational log | During pipeline run | Immutable after Stage 14 |
| Replay | Case outcome record | During + after pipeline run | Append-only (outcome fields added post-filing) |

The DEL records *how* the pipeline ran. The replay records *what was decided and what happened*.

Both share the same `execution_id`. The DEL is the technical record; the replay is the knowledge record.

---

## Storage

Replay records are stored in `replays/` using the execution ID as the filename:

```
replays/
  DEL-2026-0000001.json
  DEL-2026-0000002.json
  ...
```

Replay records must never be deleted. If a case contained errors, add a `correction` entry to the record — do not modify existing fields.

---

## Schema

```json
{
  "execution_id": "DEL-2026-0000001",
  "assessment_year": "AY2025-26",
  "created_at": "2026-03-15T10:01:22Z",
  "pipeline_version": "1.3.0",
  "case_ref": "C-000001",

  "evidence_loaded": [
    {
      "evidence_ref": "E-001",
      "source": "AIS",
      "loaded": true,
      "fields_extracted": 14,
      "parse_warnings": []
    },
    {
      "evidence_ref": "E-002",
      "source": "26AS",
      "loaded": true,
      "fields_extracted": 8,
      "parse_warnings": []
    },
    {
      "evidence_ref": "E-003",
      "source": "Prefill JSON",
      "loaded": true,
      "fields_extracted": 22,
      "parse_warnings": []
    },
    {
      "evidence_ref": "E-004",
      "source": "Form 16",
      "loaded": true,
      "fields_extracted": 6,
      "parse_warnings": []
    }
  ],

  "pattern_matching": {
    "suggested_pattern": "PAT-002",
    "confirmation_questions_asked": 3,
    "confirmed_pattern": "PAT-002",
    "pattern_confidence": 93,
    "escalated": false
  },

  "completeness_check": {
    "evidence_completeness_score": 91,
    "confidence_band": "A",
    "fields_missing": [],
    "fields_user_declared": ["business_receipts_digital_pct"],
    "halted": false
  },

  "conflicts_found": [],

  "intake_questions": [
    {
      "question_id": "Q-PAT002-1",
      "question": "What was your approximate freelance/business turnover for FY 2024-25?",
      "user_answer": "320000",
      "field_populated": "income.business_turnover_44AD",
      "answer_source": "user_typed"
    }
  ],

  "decisions": [
    {
      "decision_ref": "D-001",
      "engine": "ITR-SELECTION",
      "outcome": "ITR-4",
      "rules_evaluated": [
        { "rule_id": "R-0001", "result": true, "outcome_text": "ITR-1 eliminated — business income exists" },
        { "rule_id": "R-0004", "result": true, "outcome_text": "ITR-4 eligible — presumptive income under Section 44AD" }
      ],
      "rules_skipped": [
        { "rule_id": "R-0003", "reason": "No foreign assets declared" }
      ],
      "disqualifiers_checked": [
        { "flag": "is_director", "value": false, "triggered": false },
        { "flag": "holds_unlisted_shares", "value": false, "triggered": false },
        { "flag": "has_foreign_assets", "value": false, "triggered": false }
      ],
      "confidence": 97
    },
    {
      "decision_ref": "D-002",
      "engine": "INCOME-CLASSIFICATION",
      "outcome": "new",
      "regime_comparison": {
        "new_regime_tax": 0,
        "old_regime_tax": 13042,
        "saving": 13042
      },
      "confidence": 95
    }
  ],

  "tax_computation": {
    "regime": "new",
    "gross_total_income": 802200,
    "deductions_allowed": 75000,
    "taxable_income": 802200,
    "slab_tax": 30400,
    "rebate_87A": 30400,
    "tax_after_rebate": 0,
    "surcharge": 0,
    "cess": 0,
    "total_tax_liability": 0,
    "tds_credit": 30400,
    "total_taxes_paid": 30400,
    "refund": 30400,
    "tax_due": 0
  },

  "validations_run": [
    { "validation_ref": "V-001", "result": "pass", "severity": "critical" },
    { "validation_ref": "V-002", "result": "fail", "severity": "critical", "blocking": true,
      "details": "AIS shows FD interest ₹18,000 from HDFC Bank not included in return." },
    { "validation_ref": "V-003", "result": "fail", "severity": "high", "blocking": false,
      "details": "No pre-validated bank account found for refund ₹30,400." }
  ],

  "validation_summary": {
    "total_run": 4,
    "passed": 2,
    "failed": 2,
    "critical_failures": 1,
    "blocked": true
  },

  "explanation_generated": true,
  "explanation_sections": ["summary", "itr_form_explanation", "regime_explanation", "income_breakdown", "tax_computation", "validation_summary", "confidence_statement", "what_to_do_next"],

  "pipeline_timing": {
    "total_ms": 4200,
    "stage_1_ms": 210,
    "stage_2_ms": 180,
    "stage_3_ms": 90,
    "stage_4_ms": 120,
    "stage_5_ms": 2100,
    "stage_6_ms": 15,
    "stage_7_ms": 10,
    "stage_8_ms": 230,
    "stage_9_ms": 85,
    "stage_10_ms": 140,
    "stage_11_ms": 60,
    "stage_12_ms": 40,
    "stage_13_ms": 880,
    "stage_14_ms": 40
  },

  "final_recommendation": {
    "itr_form": "ITR-4",
    "regime": "new",
    "refund_or_due": "refund",
    "amount": 30400,
    "blocked_by_validation": true,
    "blocking_validation": "V-002"
  },

  "post_filing_outcome": {
    "recorded_at": null,
    "actual_form_filed": null,
    "actual_regime_filed": null,
    "jarviz_accepted": null,
    "override_reason": null,
    "notice_received": null,
    "outcome_category": null,
    "notes": null
  },

  "corrections": []
}
```

---

## Post-Filing Outcome Fields

These fields are populated after the taxpayer files the return:

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| `actual_form_filed` | string | ITR-1, ITR-2, ITR-3, ITR-4 | Form the taxpayer actually filed |
| `actual_regime_filed` | string | new, old | Regime actually selected |
| `jarviz_accepted` | boolean | true/false | Whether taxpayer filed exactly as Jarviz recommended |
| `override_reason` | string | see table below | Why the recommendation was not followed |
| `notice_received` | boolean | true/false/null | Whether an IT notice was received for this AY |
| `outcome_category` | string | see table below | Final outcome classification |

### Override Reason Values

| Value | Meaning |
|-------|---------|
| `jarviz_error` | Jarviz was wrong; taxpayer/CA corrected it |
| `human_preference` | Jarviz was correct; taxpayer chose differently |
| `data_not_provided` | Override due to evidence Jarviz never received |
| `ca_disagreed` | CA reviewed and disagreed with Jarviz without identifying a specific error |
| `ambiguous` | Outcome unclear |

### Outcome Category Values

| Value | Meaning |
|-------|---------|
| `accepted_no_notice` | Filed as recommended, no notice received |
| `accepted_notice` | Filed as recommended, notice received (rule review required) |
| `overridden_jarviz_error` | Jarviz was wrong; creates a feedback case |
| `overridden_human_preference` | Jarviz was correct; user chose differently |
| `pending` | Return not yet filed or outcome not yet reported |

---

## Corrections Block

The `corrections` array is append-only. If a replay record contains an error (e.g., the wrong evidence was loaded), add a correction entry instead of editing existing fields:

```json
{
  "corrections": [
    {
      "corrected_at": "2026-04-01T14:00:00Z",
      "corrected_by": "admin",
      "field": "evidence_loaded[1].fields_extracted",
      "old_value": 8,
      "new_value": 9,
      "reason": "26AS parser missed one TDS entry in original run; re-parsed manually"
    }
  ]
}
```

---

## Feedback Loop to Rule Authoring

When `outcome_category == "accepted_notice"` or `outcome_category == "overridden_jarviz_error"`, the replay record is escalated to the Rule Authoring team:

1. The replay ID is added to the rule's `test_refs` list.
2. The case is investigated to identify which rule produced the wrong outcome.
3. If the rule logic is incorrect: the rule enters the lifecycle at `peer_reviewed` → `legal_reviewed` → `active`.
4. If the rule was correct but evidence was missing: an intake question is added to the relevant pattern.
5. The GSS is updated with the corrected case and the JAB is re-run.

This is how real-world outcomes improve the rule repository over time.

---

## Query Patterns

Common queries on the replay store:

| Query | Use Case |
|-------|---------|
| All replays where `R-0004` was evaluated | Impact analysis before editing R-0004 |
| All replays where `V-002` failed | Find cases to verify AIS matching logic |
| All replays with `jarviz_accepted == false` | Human override analysis for M-09 |
| All replays for `PAT-002` in AY2025-26 | Pattern accuracy analysis |
| All replays where `total_ms > 15000` | Performance regression detection |
| All replays with `notice_received == true` | Rules that may have produced incorrect advice |

---

## Replay Schema

All replay records conform to `schemas/replay-schema.json`.
