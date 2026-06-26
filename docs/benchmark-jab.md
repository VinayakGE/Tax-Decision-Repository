# Jarviz Accuracy Benchmark (JAB)

> Every release of Jarviz must produce a JAB report before it is declared production-ready.
> The JAB report is the single source of truth for whether the system is fit to assist with tax filing.

---

## Purpose

The JAB measures nine dimensions of accuracy across a gold standard case set. It answers one question:

**Does Jarviz produce advice that a competent tax professional would agree with?**

The JAB is not a unit test suite. Unit tests verify that individual engines execute correctly. The JAB verifies that the end-to-end system produces correct outcomes on real-world inputs.

---

## Gold Standard Case Set

All JAB measurements run against the **Jarviz Gold Standard Set (GSS)**, a curated collection of tax cases where the correct outcome is known and has been independently verified by at least one qualified tax professional (CA, CMA, or Advocate).

### GSS Requirements

| Requirement | Value |
|------------|-------|
| Minimum cases for v1.x | 100 |
| Minimum cases for v2.x | 500 |
| Minimum cases for production release | 1,000 |
| CA verification per case | Required |
| AY coverage | All AYs supported by the release |
| Pattern coverage | All 8 patterns represented |
| Edge case fraction | ≥ 20% must be non-standard edge cases |

### Case Sources

In priority order:
1. Real filer cases (anonymized, with consent) — highest weight
2. CA-constructed synthetic cases with known ground truth
3. Published ITAT rulings used to derive expected outcomes

### Case Storage

Gold standard cases are stored in `benchmarks/gss/` using the same schema as `cases/` with an additional `ground_truth` block (see schema).

---

## The Nine Metrics

### M-01: ITR Form Accuracy

**What it measures:** Whether Jarviz recommends the legally correct ITR form.

```
ITR_Accuracy = (cases where recommended_form == ground_truth_form) / total_cases × 100
```

**Target:** ≥ 99%

**Failure classification:**
- **Critical miss:** Jarviz recommends a simpler form than required (e.g., ITR-1 when ITR-2 is required). These are P0 bugs.
- **Over-filing miss:** Jarviz recommends a more complex form than required (e.g., ITR-2 when ITR-1 is valid). These are P1 bugs.

**Measurement method:** Engine 1 output `recommended_form` vs `ground_truth.itr_form` in each GSS case.

---

### M-02: Refund Computation Accuracy

**What it measures:** Whether the tax computation is arithmetically correct.

```
Refund_Error_Rate = mean(|computed_refund - actual_refund| / max(actual_refund, 1)) × 100
```

**Target:** < 0.5% mean error (across all GSS cases with refund/due position)

**Zero tolerance:** Any case where `computed_refund` and `actual_refund` differ by more than ₹500 is flagged as a computation defect regardless of percentage error.

**Measurement method:** Engine 3 output `refund` vs `ground_truth.refund` in GSS. The comparison ignores 234B/234C interest if the GSS case does not include it.

---

### M-03: Income Classification Accuracy

**What it measures:** Whether every rupee of income is assigned to the correct head and sub-head.

```
Classification_Accuracy = (correctly_classified_items) / (total_classified_items) × 100
```

An item is "correctly classified" if:
1. It is placed under the correct head (H1–H5)
2. The amount matches ground truth within ₹1 (rounding tolerance)
3. For capital gains: the applicable section (111A, 112A, 112, etc.) is correct

**Target:** ≥ 98%

**Sub-metric — Missed Income Rate:**
```
Missed_Income_Rate = (income_items_in_ground_truth_not_classified) / total_ground_truth_items × 100
```
**Target:** 0% — no income may be silently dropped.

**Measurement method:** Engine 2 output `classified_income` vs `ground_truth.classified_income` in GSS.

---

### M-04: Validation Precision

**What it measures:** What fraction of validations flagged as failures are genuine failures.

```
Validation_Precision = True_Positives / (True_Positives + False_Positives) × 100
```

A "false positive" is a validation failure Jarviz raises where the ground truth shows the return is actually correct.

**Target:** ≥ 97%

**Why this matters:** False positives cause taxpayer panic and destroy trust. A validation that fires when nothing is wrong is worse than useless.

---

### M-05: Validation Recall

**What it measures:** What fraction of actual return defects Jarviz catches.

```
Validation_Recall = True_Positives / (True_Positives + False_Negatives) × 100
```

A "false negative" is a genuine defect in the return that Jarviz did not flag.

**Target:** ≥ 99%

**Sub-metric — Critical Validation Miss Rate:**
```
Critical_Miss_Rate = (Critical_failures_not_caught) / (Total_critical_failures_in_GSS) × 100
```
**Target:** 0% — no critical validation may be silently missed.

---

### M-06: False Positive Rate

**What it measures:** The proportion of all validation results that are false positives.

```
False_Positive_Rate = False_Positives / (False_Positives + True_Negatives) × 100
```

**Target:** < 1%

**Relationship to M-04:** M-04 (Precision) is computed from a failure-first perspective. M-06 is computed from a population perspective. Both must pass.

---

### M-07: Average Questions Asked

**What it measures:** How many questions Jarviz asks the user before reaching a decision, averaged across all GSS cases.

```
Avg_Questions = sum(questions_asked_per_case) / total_cases
```

**Target:** ≤ 3 questions on average

**P95 target:** ≤ 7 questions in 95th percentile of cases

**Why this matters:** Every question asked is friction. If Jarviz asks 12 questions when a CA would ask 2, the product is not useful.

**Measurement method:** Count of `intake_engine.questions_asked` in the replay record for each GSS case.

---

### M-08: Processing Time (End-to-End)

**What it measures:** How long the pipeline takes from document upload to final explanation, excluding user think time.

```
P50_Processing_Time = median(stage_1_start to stage_14_end) across all GSS cases (milliseconds)
P95_Processing_Time = 95th percentile of same
```

**Targets:**
| Metric | Target |
|--------|--------|
| P50 | < 8,000 ms |
| P95 | < 20,000 ms |
| Stage 13 (AI) alone | < 5,000 ms |
| Stages 1–12 combined | < 3,000 ms |

**Note:** Stage 13 (Explanation Engine) calls an external AI API and dominates processing time. The deterministic stages (1–12) must complete in under 3 seconds to leave headroom for the AI call.

---

### M-09: Human Override Rate

**What it measures:** The fraction of cases where a human (CA or taxpayer) rejected Jarviz's final recommendation and filed differently.

```
Override_Rate = (cases_where_actual_filed_differs_from_recommended) / (cases_with_filing_outcome_known) × 100
```

This metric requires real-world outcome data and only becomes meaningful after live deployment. For synthetic GSS cases, this metric is marked `pending`.

**Target:** < 2%

**Override categories (must be logged per case):**
| Category | Meaning |
|----------|---------|
| `jarviz_error` | Jarviz was wrong; human was right |
| `human_preference` | Jarviz was correct; human chose differently |
| `data_not_provided` | Override due to evidence Jarviz never received |
| `ambiguous` | Outcome unclear |

**Why this matters:** Override rate is the ultimate product metric. Everything else is internal. If qualified professionals routinely override Jarviz, the system is not ready.

---

## JAB Report Format

Every release produces a JAB report in `benchmarks/reports/JAB-vX.Y.Z.json`.

```json
{
  "report_id": "JAB-v1.3.0",
  "assessment_year": "AY2025-26",
  "version": "1.3.0",
  "generated_at": "2025-07-15T09:00:00Z",
  "gss_case_count": 100,
  "gss_version": "GSS-001",
  "metrics": {
    "M01_itr_accuracy": {
      "value": 99.0,
      "target": 99.0,
      "passed": true,
      "critical_misses": 0,
      "over_filing_misses": 1,
      "details": "1 case where ITR-2 recommended when ITR-1 was valid"
    },
    "M02_refund_accuracy": {
      "value": 0.21,
      "target": 0.5,
      "passed": true,
      "mean_error_pct": 0.21,
      "cases_above_500_rupee_threshold": 0
    },
    "M03_classification_accuracy": {
      "value": 98.7,
      "target": 98.0,
      "passed": true,
      "missed_income_rate": 0.0
    },
    "M04_validation_precision": {
      "value": 98.3,
      "target": 97.0,
      "passed": true,
      "false_positives": 2
    },
    "M05_validation_recall": {
      "value": 99.5,
      "target": 99.0,
      "passed": true,
      "false_negatives": 1,
      "critical_miss_rate": 0.0
    },
    "M06_false_positive_rate": {
      "value": 0.4,
      "target": 1.0,
      "passed": true
    },
    "M07_avg_questions": {
      "value": 2.7,
      "target": 3.0,
      "passed": true,
      "p95_questions": 6
    },
    "M08_processing_time_ms": {
      "p50": 6200,
      "p95": 14800,
      "target_p50": 8000,
      "target_p95": 20000,
      "passed": true,
      "stages_1_to_12_p50": 980
    },
    "M09_human_override_rate": {
      "value": null,
      "target": 2.0,
      "passed": null,
      "status": "pending",
      "cases_with_outcome_data": 0
    }
  },
  "overall_passed": true,
  "blocking_failures": [],
  "release_recommendation": "APPROVED",
  "signed_off_by": null,
  "notes": ""
}
```

### Release Gate Rules

| Condition | Action |
|-----------|--------|
| All 8 measurable metrics pass | Release APPROVED |
| Any of M01, M02, M03, M05 fail | Release BLOCKED — these are core accuracy metrics |
| M04, M06, M07, M08 fail | Release WARNED — engineering discretion to override |
| M09 pending (first release) | Permitted — mark as pending |
| M09 > 2% after live data available | Release BLOCKED |

---

## Benchmark Cadence

| Event | Action |
|-------|--------|
| Every tagged release (vX.Y.Z) | Full JAB run required |
| Rule change (single rule edit) | Re-run affected M01, M02, M03 cases for the changed rule |
| AY rollover (new assessment year) | New GSS required; all metrics re-established from baseline |
| After CA review of 10+ override cases | M09 recalculated; report updated |

---

## Benchmark Schema

All JAB reports conform to `schemas/benchmark-schema.json`.

GSS cases are stored in `benchmarks/gss/` as `GSS-XXXXXX.json` files.

Reports are stored in `benchmarks/reports/` as `JAB-vX.Y.Z.json`.

A `benchmarks/README.md` describes how to run the benchmark and add cases to the GSS.

---

## Authoring New GSS Cases

To add a case to the Gold Standard Set:

1. Process the case through Jarviz and save the replay record.
2. Have a qualified CA independently determine the correct outcome.
3. Record the ground truth in the `ground_truth` block of the GSS case file.
4. If Jarviz and the CA disagree, investigate before adding the case:
   - If Jarviz was wrong: log the bug, fix the rule, then add the case.
   - If Jarviz was right: document why the CA concurred after review.
5. Commit the case to `benchmarks/gss/` with a reference to the CA's sign-off (initials + date).

GSS cases with `jarviz_error` category overrides are the highest-value cases for finding rule gaps. Add them first.
