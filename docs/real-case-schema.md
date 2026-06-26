# Real-Case Schema — AY2025-26

**Schema version**: 1.0.0  
**Status**: FROZEN  
**Location**: `cases/real/RC-*.json`

This schema is frozen. Treat it like an API contract. Once CA firms begin
contributing cases, changing field names or semantics becomes expensive.
To extend: add new optional fields only. Never rename or remove existing fields.

---

## Top-Level Fields

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `schema_version` | string | yes | Must be `"1.0.0"` |
| `case_id` | string | yes | Format: `RC-XXXX` (zero-padded, 4 digits) |
| `source` | string | yes | `"real"` or `"synthetic"` |
| `anonymized` | boolean | yes | Must be `true` for real cases before sharing |
| `assessment_year` | string | yes | `"AY2025-26"` |
| `submitted_by` | string | no | Submitter identifier (anonymized) |
| `verified` | boolean | yes | `false` until reviewed by a second CA |
| `taxpayer` | object | yes | See below |
| `evidence` | object | yes | See below |
| `human_expected` | object | yes | See below (may have all-null values when first submitted) |
| `lv_classification` | string | no | Set after review. See Learning Velocity section. |
| `notes` | string | no | Free text. Case context, source documents, anomalies. |
| `entity_pressure_observed` | array[string] | no | EP identifiers from the Entity Pressure Log. |

---

## `taxpayer` Object

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `name` | string | yes | Anonymized (e.g., "Anonymized-01") |
| `age` | integer | yes | Age in years as of April 1 of assessment year |
| `age_bracket` | string | yes | `"general"` (< 60), `"senior"` (60–79), `"super_senior"` (≥ 80) |

---

## `evidence` Object

These are the engine input fields. All are optional except where noted; omit fields that are not applicable rather than setting them to `null` in most cases.

### Required for any run
| Field | Type | Notes |
|-------|------|-------|
| `classified_income` | object | See Income Heads below |
| `evidence_integrity_checks_passed` | boolean | Set `true` if Form 16 + 26AS match |
| `income_classification_complete` | boolean | Set `true` when all heads classified |
| `tds_credits_from_26AS` | array | `[{tan, section, amount, employer}]` |
| `regime_chosen` | string | `"old_regime"` or `"new_regime"` |
| `return_filed_date` | string | ISO 8601, e.g. `"2025-07-15"` |
| `due_date` | string | ISO 8601, typically `"2025-07-31"` |
| `income_type` | string | `"salary_only"`, `"salary_fd"`, etc. |

### Income Heads (`classified_income`)
```json
{
  "head_1_salary":       [{ "source", "gross_salary", "employer", "tan" }],
  "head_2_house_property": [],
  "head_3_business":     [],
  "head_4_capital_gains": [],
  "head_5_other_sources": []
}
```

### HRA (Section 10(13A)) — optional
| Field | Type | Notes |
|-------|------|-------|
| `basic_salary` | integer | Annual basic salary |
| `hra_actual` | integer | HRA component received from employer |
| `rent_paid` | integer | Annual rent paid |
| `city_type` | string | City name or `"metro"` / `"non_metro"` |

### Chapter VI-A Deductions — optional (old regime only)
| Field | Type | Notes |
|-------|------|-------|
| `investments_80C` | integer | Total 80C investments (capped at ₹1.5L by engine) |
| `nps_contribution_80ccd1b` | integer | Additional NPS (capped at ₹50K by engine) |
| `deduction_80d_self_premium` | integer | Health insurance for self/family |
| `deduction_80d_parents_premium` | integer | Health insurance for parents |
| `parent_age_bracket` | string | `"below_60"` or `"senior"` |

### Advance tax and TDS
| Field | Type | Notes |
|-------|------|-------|
| `advance_tax_paid` | integer | Total advance tax paid during the year |
| `self_assessment_tax_paid` | integer | Self-assessment tax at time of filing |

---

## `human_expected` Object

Provide any subset of these fields. The engine validates only the fields present.
All amount fields use rupees (integers). Tolerance: ±₹1 for rounding.

| Field | Type | Notes |
|-------|------|-------|
| `taxable_income_old_regime` | integer | After all Chapter VI-A deductions |
| `taxable_income_new_regime` | integer | After standard deduction only |
| `total_tax_old_regime` | integer | Slab tax + surcharge + cess |
| `total_tax_new_regime` | integer | Slab tax + surcharge + cess |
| `regime_recommendation` | string | `"old_regime"` or `"new_regime"` |
| `outcome` | string | `"refund"`, `"demand"`, or `"nil"` |
| `refund_amount` | integer | 0 if not a refund case |
| `demand_amount` | integer | 0 if not a demand case |
| `total_interest` | integer | Section 234A/B/C interest (0 if on-time) |

---

## Learning Velocity Classification

Set `lv_classification` after reviewing the comparison report.

| Value | Meaning |
|-------|---------|
| `"match"` | Engine and human agree on all validated fields |
| `"conservative"` | Engine asked for more evidence than necessary (over-cautious completeness check) |
| `"rule_gap"` | Mismatch because a deduction/rule is not yet implemented |
| `"defect"` | Mismatch because the engine computed incorrectly (logic error) |

If the human calculation was wrong and the engine was right, still record the
original human_expected and set `lv_classification: "match"` after correction.
Add a note explaining the human error — these become demonstration cases.

---

## Entity Pressure Fields

The `entity_pressure_observed` array records which Entity Pressure Log entries
were encountered while encoding this case. Use the EP identifier codes.

```json
"entity_pressure_observed": ["EP-001", "EP-003"]
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-06-26 | Initial frozen schema |
