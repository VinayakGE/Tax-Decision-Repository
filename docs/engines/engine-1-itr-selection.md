# Engine 1 — ITR Selection Engine

> Sprint 1, Priority 1.
> This is the first engine to build. Every other decision depends on knowing which form must be filed.

---

## Purpose

Given a taxpayer's complete evidence profile, determine which ITR form is legally required for AY2025-26.

---

## Pipeline Stage

Stage 8 (Decision Engine), first decision executed: **D-001**

---

## Contract

### Input

```json
{
  "taxpayer": {
    "resident_status": "ROR | RNOR | NR",
    "age": "integer",
    "is_director": "boolean",
    "holds_unlisted_shares": "boolean",
    "has_foreign_assets": "boolean",
    "has_foreign_income": "boolean",
    "has_foreign_signing_authority": "boolean"
  },
  "income": {
    "salary": "number | null",
    "pension": "number | null",
    "business_regular": "number | null",
    "business_presumptive_44AD": "boolean",
    "business_turnover_44AD": "number | null",
    "business_presumptive_44ADA": "boolean",
    "business_receipts_44ADA": "number | null",
    "capital_gains_stcg": "number | null",
    "capital_gains_ltcg": "number | null",
    "house_property_count": "integer",
    "house_property_letout_exists": "boolean",
    "other_sources_interest": "number | null",
    "other_sources_dividend": "number | null",
    "other_sources_lottery": "boolean",
    "total_income": "number"
  }
}
```

### Output

```json
{
  "engine": "ITR-SELECTION",
  "decision_ref": "D-001",
  "outcome": {
    "recommended_form": "ITR-4",
    "confidence_band": "A",
    "confidence_score": 97
  },
  "alternatives": [
    {
      "form": "ITR-3",
      "condition": "If capital gains income exists, ITR-4 is invalid. Use ITR-3."
    }
  ],
  "rule_trace": [
    {
      "rule_id": "R-0001",
      "condition_evaluated": "business_income > 0",
      "result": true,
      "outcome": "ITR-1 eliminated",
      "legal_citation": "Section 139(1) read with ITR-1 Instructions"
    },
    {
      "rule_id": "R-0004",
      "condition_evaluated": "presumptive_44AD == true AND total_income <= 5000000 AND no_disqualifiers",
      "result": true,
      "outcome": "ITR-4 eligible",
      "legal_citation": "Section 44AD, ITR-4 Instructions AY2025-26"
    }
  ],
  "disqualifiers_checked": [
    { "flag": "is_director", "value": false, "disqualifies": ["ITR-1", "ITR-4"], "triggered": false },
    { "flag": "holds_unlisted_shares", "value": false, "disqualifies": ["ITR-1", "ITR-4"], "triggered": false },
    { "flag": "has_foreign_assets", "value": false, "disqualifies": ["ITR-1", "ITR-4"], "triggered": false },
    { "flag": "resident_status", "value": "ROR", "disqualifies": [], "triggered": false }
  ],
  "eliminated_forms": [
    { "form": "ITR-1", "reason": "Business income exists (R-0001)" }
  ]
}
```

---

## Algorithm

```
function selectITRForm(taxpayer, income):

  // Step 1: Hard disqualifiers — check before anything else
  if taxpayer.resident_status in ["RNOR", "NR"]:
    eliminate ITR-1, ITR-4
    minimum_form = ITR-2

  if taxpayer.has_foreign_assets OR taxpayer.has_foreign_income:
    eliminate ITR-1, ITR-4          // Rule R-0003
    minimum_form = ITR-2

  if taxpayer.is_director:
    eliminate ITR-1, ITR-4

  if taxpayer.holds_unlisted_shares:
    eliminate ITR-1, ITR-4

  // Step 2: Business income check
  if income.business_regular > 0:
    return ITR-3                    // Non-presumptive business → ITR-3

  if income.business_presumptive_44AD OR income.business_presumptive_44ADA:
    if income.capital_gains_stcg > 0 OR income.capital_gains_ltcg > 0:
      return ITR-3                  // CG + presumptive → ITR-3, not ITR-4
    if income.total_income > 5000000:
      return ITR-3                  // Ceiling breached
    if no disqualifiers:
      return ITR-4                  // Rule R-0004

  // Step 3: Capital gains check (no business income)
  if income.capital_gains_stcg > 0 OR income.capital_gains_ltcg > 0:
    return ITR-2

  // Step 4: ITR-1 eligibility
  if income.total_income <= 5000000
    AND income.house_property_count <= 1
    AND NOT income.other_sources_lottery
    AND taxpayer.resident_status == "ROR"
    AND no disqualifiers:
    return ITR-1                    // Rule R-0002

  // Default fallback
  return ITR-2
```

---

## Missing Field Handling

| Missing Field | Action |
|---------------|--------|
| `is_director` | Cannot assume false. Ask before deciding. Confidence drops to Band C. |
| `holds_unlisted_shares` | Cannot assume false. Ask. Confidence drops to Band C. |
| `has_foreign_assets` | Cannot assume false. Ask. Confidence drops to Band D. |
| `resident_status` | Cannot proceed without this. Confidence Band E — halt. |
| `total_income` | Cannot evaluate ITR-1 ceiling without this. Ask. |
| `capital_gains_*` | If AIS loaded and shows no capital gains entries, treat as 0. Else ask. |
| `business_presumptive_44AD` | If AIS shows no business receipts and user has not indicated business income, treat as false. |

---

## Rules Referenced

| Rule ID | Title | Applies When |
|---------|-------|-------------|
| R-0001 | ITR-1 Ineligible — Business Income | Any business income exists |
| R-0002 | ITR-1 Eligible — Salary Only | All eligibility conditions pass |
| R-0003 | ITR-2 Required — Foreign Assets | Foreign assets or NR status |
| R-0004 | ITR-4 Eligible — Presumptive Income | 44AD/44ADA + no disqualifiers |

---

## Test Requirements

Minimum test cases before this engine is marked production-ready:

| # | Scenario | Expected |
|---|----------|----------|
| 1 | Salary only, ROR, income ₹8L, no complications | ITR-1 |
| 2 | Salary + freelance (44AD), no capital gains | ITR-4 |
| 3 | Salary + capital gains | ITR-2 |
| 4 | Salary + regular business | ITR-3 |
| 5 | Salary + freelance + capital gains | ITR-3 |
| 6 | Director with salary only | ITR-2 |
| 7 | Foreign assets with salary | ITR-2 |
| 8 | NRI with Indian income | ITR-2 |
| 9 | Income > ₹50L, salary only | ITR-2 |
| 10 | Presumptive (44AD) turnover > ₹3 Cr | ITR-3 |
| 11 | Super senior citizen (age ≥ 80) | ITR-2 (ITR-1 not available) |
| 12 | Salary + lottery income | ITR-2 |

---

## JAB Metrics for This Engine

- **ITR Accuracy**: `correct_itr_recommendations / total_cases` → Target: ≥ 99%
- **False ITR-1 Rate**: Cases where ITR-1 was recommended but ITR-2+ was correct → Target: 0%
- **Average questions asked**: Questions asked before ITR decision → Target: ≤ 3
