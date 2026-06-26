# Engine 2 — Income Classification Engine

> Sprint 1, Priority 2.
> Classifies all income into the five heads under the Income Tax Act before the Tax Calculator can run.

---

## Purpose

Given raw evidence from AIS, 26AS, Form 16, and user answers, classify every rupee of income into the correct head and sub-head. The Tax Calculator (Engine 3) cannot run until all income is classified.

---

## Pipeline Stage

Stage 8 (Decision Engine), runs after Engine 1.

---

## The Five Heads of Income

```
Head 1: Salaries
Head 2: Income from House Property
Head 3: Profits and Gains of Business or Profession
Head 4: Capital Gains
Head 5: Income from Other Sources
```

Every income item must be assigned to exactly one head. Misclassification changes the tax rate and form used.

---

## Contract

### Input

```json
{
  "raw_income": {
    "ais": {
      "salary_entries": [],
      "business_entries": [],
      "interest_entries": [],
      "dividend_entries": [],
      "capital_gain_entries": [],
      "rent_entries": []
    },
    "form16": {
      "gross_salary": 840000,
      "standard_deduction": 75000,
      "exempt_allowances": {},
      "employer_tds": 28600
    },
    "capital_gains_statement": {
      "equity_stcg": 0,
      "equity_ltcg": 0,
      "mf_stcg": 0,
      "mf_ltcg": 0,
      "property_stcg": 0,
      "property_ltcg": 0
    },
    "user_answers": {}
  }
}
```

### Output

```json
{
  "engine": "INCOME-CLASSIFICATION",
  "classified_income": {
    "head_1_salary": {
      "gross_salary": 840000,
      "standard_deduction": 75000,
      "exempt_allowances": 0,
      "net_taxable_salary": 765000,
      "source_ref": "E-004",
      "rule_trace": []
    },
    "head_2_house_property": {
      "self_occupied": { "net_annual_value": 0, "interest_24b": 0, "net_income": 0 },
      "let_out": null
    },
    "head_3_business": {
      "presumptive_44AD": {
        "turnover": 320000,
        "presumptive_rate": "6%",
        "net_income": 19200,
        "source_ref": "E-001"
      },
      "regular": null
    },
    "head_4_capital_gains": {
      "stcg_111A": 0,
      "stcg_other": 0,
      "ltcg_112A": 0,
      "ltcg_other": 0,
      "total": 0
    },
    "head_5_other_sources": {
      "savings_interest": 0,
      "fd_interest": 18000,
      "dividend": 0,
      "other": 0,
      "total": 18000,
      "source_ref": "E-001"
    }
  },
  "gross_total_income": 802200,
  "classification_confidence": 94,
  "unclassified_entries": [],
  "conflicts": []
}
```

---

## Classification Rules

### Head 1 — Salaries

Sources: Form 16 (primary), AIS salary entries (secondary), 26AS TDS on salary.

| Item | Treatment |
|------|-----------|
| Basic salary, DA, HRA, allowances | Taxable under Head 1 |
| Standard deduction | Deduct ₹75,000 (New Regime) or ₹50,000 (Old Regime) |
| HRA exemption | Only in Old Regime — compute min(actual HRA, 50%/40% of basic, rent paid − 10% basic) |
| Exempt allowances (LTA, uniform, etc.) | Deduct from gross; only Old Regime |
| Perquisites | Add to taxable salary |
| Pension | Treated as salary |

### Head 2 — House Property

Sources: User answers (rent received, municipal tax, home loan interest), AIS rent entries.

| Item | Treatment |
|------|-----------|
| Self-Occupied (SOP) | NAV = 0; u/s 24b interest deductible up to ₹2L (Old Regime only) |
| Let-Out (LOP) | GAV = higher of actual rent or fair market rent; deduct municipal tax → NAV; 30% std deduction; full interest u/s 24b |
| Loss from HP | Set off against salary up to ₹2L; balance carry forward 8 years |
| New Regime | Interest on SOP loan: NOT deductible. Interest on LOP: NOT deductible. |

### Head 3 — Business / Profession

Sources: AIS business entries, user answers.

| Item | Treatment |
|------|-----------|
| Turnover ≤ ₹3 Cr, mostly digital | 6% of turnover = income (44AD) |
| Turnover ≤ ₹3 Cr, cash > 5% | 8% of turnover = income (44AD) |
| Specified professional receipts ≤ ₹75L | 50% of receipts = income (44ADA) |
| Non-presumptive | Actual profit from books; full expense deduction |

### Head 4 — Capital Gains

Sources: Broker statement / CAS (primary), AIS (secondary — DO NOT use AIS as primary for CG).

| Asset | Holding | Section | Rate |
|-------|---------|---------|------|
| Listed equity / equity MF | < 12 months | 111A | 20% (from 23 Jul 2024) |
| Listed equity / equity MF | ≥ 12 months | 112A | 12.5% above ₹1.25L |
| Property / non-equity assets | < 24 months | Normal | Slab rate |
| Property / non-equity assets | ≥ 24 months | 112 | 12.5% (no indexation from AY2025-26) |

⚠ **AY2025-26 specific:** Finance Act 2024 changed capital gains rates effective 23 July 2024. Transactions before and after this date in the same AY may carry different rates. The classifier must split by transaction date.

### Head 5 — Other Sources (Residual)

Sources: AIS interest entries, AIS dividend entries, user answers.

| Item | Treatment |
|------|-----------|
| Savings bank interest | Taxable; 80TTA deduction up to ₹10,000 (Old Regime) |
| FD / RD interest | Fully taxable; 80TTB for seniors up to ₹50,000 (Old Regime) |
| Dividend from Indian companies | Taxable at slab rate |
| Gifts > ₹50,000 from non-relatives | Taxable |
| Lottery / game show | 30% flat rate u/s 115BB |

---

## Ambiguous Cases

| Ambiguity | Resolution Rule |
|-----------|----------------|
| Freelance income — business or profession? | Ask user for profession type. If specified profession → 44ADA. Else → 44AD. |
| Crypto gains | Taxable at 30% u/s 115BBH (no deduction except cost). Not covered by 44AD/44ADA. Use Head 5. |
| Bonus / ESOP | ESOPs: taxable as perquisite on allotment; capital gain on sale. Classify separately. |
| Interest from employer loans | Taxable as perquisite under Head 1. |
| NRE account interest | Exempt u/s 10(4). Zero in all heads. Do not include. |

---

## Test Requirements

| # | Scenario | Expected |
|---|----------|----------|
| 1 | Salary ₹8.4L, FD interest ₹18K, presumptive business ₹19.2K | H1: ₹7.65L, H3: ₹19.2K, H5: ₹18K |
| 2 | LTCG on equity ₹2L (> ₹1.25L threshold) | H4 LTCG 112A: ₹75K taxable |
| 3 | STCG on equity ₹50K | H4 STCG 111A: ₹50K @ 20% |
| 4 | Let-out property, rent ₹6L, home loan interest ₹4L | H2 LOP net loss: −₹1.8L (after 30% std) |
| 5 | Transaction on 22 Jul 2024 (old rate) and 24 Jul 2024 (new rate) | Split STCG by date; different rates applied |

---

## JAB Metrics for This Engine

- **Classification accuracy**: Correct head assignment / total income items → Target: ≥ 98%
- **Missed income rate**: Income in AIS not classified → Target: 0%
- **AY2025-26 CG date-split accuracy**: Correct pre/post 23-Jul-2024 classification → Target: 100%
