# Engine 3 — Tax Computation Engine

> Sprint 1, Priority 3.
> Pure deterministic computation. No AI. No interpretation. No ambiguity.
> If this engine has a bug, it is a software bug, not a knowledge gap.

---

## Purpose

Given classified income and elected deductions, compute the exact tax liability under both Old and New Regimes, apply all rebates, compute TDS credit, and produce the final refund or balance due.

---

## Pipeline Stage

Stage 9 (Tax Calculator). Runs after all income is classified by Engine 2.

---

## Design Principle

This engine contains no rules from the rule repository. Tax computation is arithmetic, not policy. All inputs — slabs, surcharge rates, cess rate, rebate limits — are stored in version-controlled data tables at `/data/AY-XXXX-XX/tax-tables.json` and loaded at runtime.

When slabs change (Finance Act), only the data file changes. The computation logic is unchanged.

---

## Data File: `/data/AY2025-26/tax-tables.json`

This file must be created as part of Sprint 1. It contains:

```json
{
  "assessment_year": "AY2025-26",
  "financial_year": "FY2024-25",

  "new_regime": {
    "standard_deduction": 75000,
    "slabs": [
      { "from": 0,       "to": 300000,  "rate": 0.00 },
      { "from": 300001,  "to": 700000,  "rate": 0.05 },
      { "from": 700001,  "to": 1000000, "rate": 0.10 },
      { "from": 1000001, "to": 1200000, "rate": 0.15 },
      { "from": 1200001, "to": 1500000, "rate": 0.20 },
      { "from": 1500001, "to": null,    "rate": 0.30 }
    ],
    "rebate_87A": {
      "income_limit": 1200000,
      "max_rebate": 60000
    },
    "allowed_deductions": ["80CCD2", "standard_deduction"]
  },

  "old_regime": {
    "standard_deduction": 50000,
    "slabs": {
      "general": [
        { "from": 0,      "to": 250000,  "rate": 0.00 },
        { "from": 250001, "to": 500000,  "rate": 0.05 },
        { "from": 500001, "to": 1000000, "rate": 0.20 },
        { "from": 1000001,"to": null,    "rate": 0.30 }
      ],
      "senior": [
        { "from": 0,      "to": 300000,  "rate": 0.00 },
        { "from": 300001, "to": 500000,  "rate": 0.05 },
        { "from": 500001, "to": 1000000, "rate": 0.20 },
        { "from": 1000001,"to": null,    "rate": 0.30 }
      ],
      "super_senior": [
        { "from": 0,      "to": 500000,  "rate": 0.00 },
        { "from": 500001, "to": 1000000, "rate": 0.20 },
        { "from": 1000001,"to": null,    "rate": 0.30 }
      ]
    },
    "rebate_87A": {
      "income_limit": 500000,
      "max_rebate": 12500
    }
  },

  "special_rates": {
    "stcg_111A": 0.20,
    "ltcg_112A": 0.125,
    "ltcg_112A_exemption": 125000,
    "ltcg_112": 0.125,
    "stcg_other": "slab",
    "lottery_115BB": 0.30,
    "crypto_115BBH": 0.30
  },

  "surcharge": [
    { "income_above": 5000000,  "income_upto": 10000000, "rate": 0.10 },
    { "income_above": 10000000, "income_upto": 20000000, "rate": 0.15 },
    { "income_above": 20000000, "income_upto": 50000000, "rate": 0.25 },
    { "income_above": 50000000, "income_upto": null,     "rate": 0.37 }
  ],
  "surcharge_cap_112A": 0.15,

  "cess_rate": 0.04,

  "alternate_minimum_tax": {
    "rate": 0.185,
    "applicable_to": ["LLP", "non-company"]
  }
}
```

---

## Computation Algorithm

```
function computeTax(classified_income, deductions, regime, taxpayer):

  // Step 1: Build Gross Total Income
  GTI = sum(all income heads)
  // Note: Special rate income (CG, lottery) is separated after this step

  // Step 2: Apply deductions (regime-specific)
  if regime == NEW:
    allowed = deductions.standard_deduction + deductions.nps_employer_80ccd2
  else:
    allowed = deductions.standard_deduction
             + deductions.nps_employer_80ccd2
             + deductions.chapter_via   // 80C + 80D + 80E + etc.
             + deductions.hra_exempt
             + deductions.lta_exempt
             + deductions.interest_24b  // for SOP (cap ₹2L) or LOP (uncapped)

  deductions_allowed = min(allowed, GTI)  // cannot exceed GTI

  // Step 3: Taxable Income
  taxable_income = GTI - deductions_allowed

  // Step 4: Separate special rate income
  // Special rate income is taxed at flat rates regardless of slab
  normal_income = taxable_income - special_rate_income_total
  special_income = {
    stcg_111A, ltcg_112A, ltcg_112, lottery, crypto
  }

  // Step 5: Compute tax on normal income (slab rate)
  slab_tax = apply_slabs(normal_income, regime, taxpayer.age_category)

  // Step 6: Compute tax on special rate income
  special_tax = 0
  special_tax += max(0, ltcg_112A - exemption_125000) × rate_112A
  special_tax += stcg_111A × rate_111A
  special_tax += ltcg_112 × rate_112
  special_tax += lottery × rate_115BB
  special_tax += crypto × rate_115BBH

  // Step 7: Gross tax
  gross_tax = slab_tax + special_tax

  // Step 8: Rebate u/s 87A
  // Rebate applies only on slab_tax, not special rate tax
  rebate = 0
  if taxable_income <= rebate_87A.income_limit:
    rebate = min(slab_tax, rebate_87A.max_rebate)

  tax_after_rebate = max(0, gross_tax - rebate)

  // Step 9: Surcharge
  surcharge = compute_surcharge(taxable_income, tax_after_rebate)
  // Cap surcharge at 15% for 112A income

  // Step 10: Cess
  cess = (tax_after_rebate + surcharge) × cess_rate

  // Step 11: Total tax liability
  total_tax = tax_after_rebate + surcharge + cess

  // Step 12: TDS / Advance Tax credit
  tds_credit = sum(verified_tds_from_26AS)
  advance_tax = sum(advance_tax_from_26AS)
  sat = sum(self_assessment_tax_from_26AS)

  total_paid = tds_credit + advance_tax + sat

  // Step 13: Final position
  if total_paid > total_tax:
    refund = total_paid - total_tax
    tax_due = 0
  else:
    refund = 0
    tax_due = total_tax - total_paid

  // Step 14: Interest on shortfall (u/s 234B / 234C)
  // Only compute if advance tax was required and not paid
  interest_234B = compute_234B(total_tax, advance_tax, advance_tax_due_dates)
  interest_234C = compute_234C(advance_tax_installments, tax_liability)

  return {
    gross_total_income: GTI,
    deductions_allowed: deductions_allowed,
    taxable_income: taxable_income,
    slab_tax: slab_tax,
    special_tax: special_tax,
    gross_tax: gross_tax,
    rebate_87A: rebate,
    tax_after_rebate: tax_after_rebate,
    surcharge: surcharge,
    cess: cess,
    total_tax_liability: total_tax,
    tds_credit: tds_credit,
    advance_tax_paid: advance_tax,
    total_taxes_paid: total_paid,
    refund: refund,
    tax_due: tax_due,
    interest_234B: interest_234B,
    interest_234C: interest_234C
  }
```

---

## Regime Comparison

Engine 3 always computes under BOTH regimes and returns the comparison. The regime recommendation comes from this comparison. The AI presents both and recommends the lower-tax option.

```json
{
  "regime_comparison": {
    "new_regime": { "taxable_income": 802200, "total_tax": 0, "refund": 30400 },
    "old_regime": { "taxable_income": 750200, "total_tax": 13042, "refund": 17358 },
    "recommended_regime": "new",
    "saving": 13042
  }
}
```

---

## Precision and Rounding

- All amounts are stored and computed as integers (rupees, no paisa).
- Round tax amounts to the nearest rupee (standard practice for ITR filing).
- Never round intermediate values — only round the final liability.

---

## Test Requirements

All tests must have exact expected values computed manually. This engine has zero tolerance for arithmetic errors.

| # | Scenario | Taxable Income | Expected Total Tax | Notes |
|---|----------|---------------|-------------------|-------|
| 1 | New Regime, ₹8.02L | ₹8.02L | ₹0 | Rebate u/s 87A covers full liability |
| 2 | New Regime, ₹12L exactly | ₹12L | ₹0 | At rebate boundary |
| 3 | New Regime, ₹12.1L | ₹12.1L | ₹61,500 + cess | Cliff effect — no rebate above ₹12L |
| 4 | Old Regime, ₹5L | ₹5L | ₹0 | Rebate covers ₹12,500 liability |
| 5 | Old Regime, ₹5.1L | ₹5.1L | ₹2,060 + cess | Above rebate limit |
| 6 | LTCG ₹2L on equity (112A) | Slab + ₹75K LTCG | Slab tax + ₹9,375 + cess | Exemption ₹1.25L |
| 7 | Surcharge case (income ₹60L) | ₹60L | Computed + 10% surcharge | Surcharge bracket 1 |
| 8 | Senior citizen, Old Regime, ₹3L | ₹3L | ₹0 | Enhanced basic exemption ₹3L |

---

## JAB Metrics for This Engine

- **Refund computation accuracy**: `|computed_refund - actual_refund| / actual_refund` → Target: < 0.5% error
- **Zero arithmetic errors**: Any arithmetic error is a P0 bug → Target: 0 errors
- **Both regime computation**: Both regimes always computed → Target: 100%
