# Tax Table Repository

This directory contains Finance Act-versioned numeric lookup tables that rules reference for all computation values.

## Design Principle

**No numeric tax value is ever hard-coded into a rule.** Every rate, threshold, slab, rebate, or cess value lives in this directory. When Finance Act 2027 changes a slab, the update happens in one place — not scattered across dozens of rules.

## Reference Syntax

Rules and tests reference table values using the notation:

```
TaxTable:2024.tax_slabs.new_regime
TaxTable:2024.rebates.87A.new_regime
TaxTable:2024.surcharge.brackets
TaxTable:2024.cess.cess.rate
TaxTable:2024.special_rates.rates.ltcg_112A
TaxTable:2024.deductions.chapter_via.80C.limit
```

The prefix `2024` denotes the Finance Act year (Finance Act 2024, applicable for AY2025-26).

## Directory Structure

```
tables/
└── 2024/                           ← Finance Act 2024 (AY2025-26)
    ├── tax_slabs.json              ← New and Old Regime income tax slabs
    ├── rebates.json                ← Section 87A rebate limits
    ├── surcharge.json              ← Surcharge brackets and caps
    ├── cess.json                   ← Health & Education Cess rate
    ├── deductions.json             ← Chapter VI-A and other deduction limits
    └── special_rates.json          ← Capital gains, lottery, VDA special rates
```

## Versioning Policy

Each table file has its own `version` field. When a Finance Act changes a value:

1. Create a new directory `tables/YYYY/` for the new Finance Act year
2. Copy all table files; update only the changed values
3. Update the `finance_act` and `version` fields in affected files
4. Update rules to reference the new year prefix where applicable
5. Record the change in `changes/CH-XXXX.json`

Do **not** edit existing table files after they have been used in a JAB benchmark run. They are the audit trail for why past returns computed as they did.

## Tables in This Directory

| File | Contents | Key values |
|------|----------|------------|
| `tax_slabs.json` | New Regime (6 brackets), Old Regime (general/senior/super_senior) | New: 0%/5%/10%/15%/20%/30%; Old: 0%/5%/20%/30% |
| `rebates.json` | Section 87A rebate limits | New Regime: ₹60,000 if income ≤ ₹12L; Old: ₹12,500 if ≤ ₹5L |
| `surcharge.json` | Surcharge brackets and regime caps | 10%/15%/25%/37%; New Regime cap 25%; LTCG 112A cap 15% |
| `cess.json` | Health & Education Cess | 4% on tax + surcharge |
| `deductions.json` | Chapter VI-A deduction limits (Wave 3B reference) | 80C ₹1.5L, 80CCD(1B) ₹50K, 80D ₹25K–₹1L, etc. |
| `special_rates.json` | Capital gains, lottery, VDA special tax rates | STCG 111A 20%, LTCG 112A 12.5%, Lottery/VDA 30% |

## Finance Act 2024 Rate Changes (Effective 23 July 2024)

All `special_rates.json` entries include both the post- and pre-23-July-2024 rates for AY2025-26.
Transactions on or before 22 July 2024 use the pre-July-23 rates.

| Asset | Pre-23 Jul 2024 | Post-23 Jul 2024 |
|-------|-----------------|------------------|
| STCG on listed equity (111A) | 15% | 20% |
| LTCG on listed equity (112A) | 10%, ₹1L exempt | 12.5%, ₹1.25L exempt |
| LTCG on other assets (112) | 20% with indexation | 12.5% without indexation |
