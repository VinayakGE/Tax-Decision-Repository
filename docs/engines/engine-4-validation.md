# Engine 4 — Validation Engine

> Sprint 1, Priority 4.
> Finds everything wrong with the return before the taxpayer files it.
> The most user-valuable engine — catching a mismatch here saves a notice later.

---

## Purpose

Given all prior stage outputs (evidence, decisions, tax computation), run every applicable validation and produce a severity-ranked list of issues, each with a remediation action.

---

## Pipeline Stage

Stage 10 (Validation Engine). Runs after Tax Calculator.

---

## Contract

### Input

```json
{
  "evidence_object": { ... },
  "decisions": { "D-001": "ITR-4", "D-002": "new", ... },
  "tax_computation": { "total_tax": 0, "refund": 30400, ... },
  "conflict_log": [],
  "matched_pattern": "PAT-002"
}
```

### Output

```json
{
  "engine": "VALIDATION",
  "validation_results": [
    {
      "validation_ref": "V-001",
      "title": "TDS Mismatch — Form 16 vs 26AS",
      "result": "pass",
      "severity": "critical",
      "details": null,
      "remediation": null
    },
    {
      "validation_ref": "V-002",
      "title": "Income in AIS Not Reported in Return",
      "result": "fail",
      "severity": "critical",
      "details": "AIS shows FD interest ₹18,000 from HDFC Bank. This has not been included in the return.",
      "remediation": "Add ₹18,000 FD interest to Head 5 (Other Sources). Verify amount against Form 16A if available.",
      "blocking": true
    }
  ],
  "summary": {
    "total_run": 5,
    "passed": 4,
    "failed": 1,
    "critical_failures": 1,
    "high_failures": 0,
    "medium_failures": 0,
    "low_failures": 0,
    "blocked": true,
    "blocking_validation": "V-002"
  }
}
```

---

## Validation Selection Logic

Not all validations run for every case. The engine selects validations based on:

1. **Pattern-specific**: Validations listed in the matched pattern's `common_validations`
2. **Decision-triggered**: Validations linked to the decisions that were made (from `validation_registry.json`)
3. **Universal**: Validations that always run regardless of pattern (V-002, V-003)

```
function selectValidations(pattern, decisions, evidence):
  validations = []
  validations.add(pattern.common_validations)
  for each decision in decisions:
    validations.add(validation_registry.findByDecision(decision.id))
  validations.add(universal_validations)  // always-run list
  return deduplicated(validations)
```

---

## Core Validations (Sprint 1)

### V-001: TDS Mismatch — Form 16 vs 26AS (Critical)

```
Condition:
  for each employer TAN in Form 16:
    delta = |form16_tds - 26as_tds| / max(form16_tds, 26as_tds)
    if delta > 0.01: FAIL

Failure message:
  "TDS in Form 16 (₹{form16_tds}) does not match 26AS (₹{26as_tds})
  for TAN {tan}. You can only claim ₹{26as_tds} as TDS credit."

Remediation:
  "Contact your employer to verify the TDS has been deposited. The
  shortfall must be deposited before you file."
```

### V-002: AIS Income Not in Return (Critical)

```
Condition:
  for each income_entry in AIS:
    if income_entry.amount > THRESHOLD[income_entry.type]:
      if income_entry not covered by any head in classified_income:
        FAIL

THRESHOLDS:
  salary: > 0
  interest: > 0
  dividend: > 10
  business_receipts: > 0
  capital_gains: > 0
  rent: > 0

Failure message:
  "AIS shows {income_type} of ₹{amount} from {source} that is not
  included in your return. The IT Department will flag this automatically."

Remediation:
  "Either add this income to your return, or submit an AIS feedback
  disputing this entry on the IT Portal before filing."
```

### V-003: Refund Bank Account Not Pre-Validated (High)

```
Condition:
  if tax_computation.refund > 0:
    if NOT taxpayer.bank_account.pre_validated:
      FAIL

Failure message:
  "You are due a refund of ₹{refund} but no pre-validated bank
  account is linked to your PAN."

Remediation:
  "Log in to incometax.gov.in → My Profile → Bank Account.
  Pre-validate your bank account. Refunds are only credited to
  pre-validated accounts."
```

### V-004: ITR Form Mismatch (Critical) — NEW in Sprint 1

```
Condition:
  if user_selected_form != engine_recommended_form:
    FAIL

Failure message:
  "You have selected {user_form} but based on your income profile,
  {recommended_form} is required. Filing the wrong form is invalid
  and will be rejected."

Remediation:
  "Change the ITR form to {recommended_form} before filing."
```

### V-005: Advance Tax Default (High) — NEW in Sprint 1

```
Condition:
  if tax_computation.total_tax > 10000:
    if tax_computation.advance_tax_paid == 0:
      if taxpayer.income.has_business OR taxpayer.income.has_capital_gains:
        FAIL

Failure message:
  "Your tax liability is ₹{total_tax} but no advance tax was paid
  during the year. Interest u/s 234B may be charged at 1% per month
  on the unpaid amount."

Remediation:
  "Pay self-assessment tax before filing. Compute 234B interest
  from April 1 to the date of payment and include it in your return."
```

### V-006: Presumptive Scheme Threshold Check (Critical) — NEW in Sprint 1

```
Condition:
  if income.business_presumptive_44AD:
    if income.business_turnover > 30000000:
      FAIL
  if income.business_presumptive_44ADA:
    if income.professional_receipts > 7500000:
      FAIL

Failure message:
  "Your {turnover|receipts} of ₹{amount} exceeds the ₹{limit}
  threshold for presumptive taxation under Section {44AD|44ADA}.
  You cannot use ITR-4."

Remediation:
  "Switch to ITR-3 and declare actual income from books of accounts.
  Audit under Section 44AB may be required."
```

---

## Severity Levels and Blocking Rules

| Severity | Definition | Blocks Final Report? | Blocks Filing? |
|----------|-----------|---------------------|---------------|
| Critical | Return is invalid or will generate a notice if filed as-is | Yes | Yes |
| High | Material issue that should be resolved before filing | No | Recommended |
| Medium | Advisory — affects accuracy but return is valid | No | No |
| Low | Informational — best practice suggestion | No | No |

**Blocking behavior:** If any critical validation fails, the Final Report is generated with a BLOCKED status. The taxpayer sees the failure and remediation steps. They must resolve and re-run the pipeline before filing.

---

## Output Ordering

Validation results are always presented in this order:
1. Critical failures (highest urgency)
2. High failures
3. Medium failures
4. Low failures
5. Passes (collapsed by default in UI)

Within each severity level, order by validation ID (V-001 before V-002).

---

## Test Requirements

| # | Scenario | Expected |
|---|----------|----------|
| 1 | Form 16 TDS matches 26AS exactly | V-001 PASS |
| 2 | Form 16 TDS ₹28,600, 26AS shows ₹27,000 | V-001 FAIL (critical) |
| 3 | AIS shows interest ₹18,000, not in return | V-002 FAIL (critical) |
| 4 | All AIS income accounted for | V-002 PASS |
| 5 | Refund ₹30,400, no pre-validated bank | V-003 FAIL (high) |
| 6 | Tax liability ₹45,000, no advance tax, has business income | V-005 FAIL (high) |
| 7 | 44AD turnover ₹3.1 Cr | V-006 FAIL (critical) |
| 8 | User selected ITR-1 but has business income | V-004 FAIL (critical) |

---

## JAB Metrics for This Engine

- **Validation precision**: True failures caught / (true failures + false positives) → Target: ≥ 97%
- **Validation recall**: True failures caught / (true failures + false negatives) → Target: ≥ 99%
- **False positive rate**: Validations that fail when return is actually correct → Target: < 1%
- **Critical validation miss rate**: Critical validations that did not trigger when they should have → Target: 0%
