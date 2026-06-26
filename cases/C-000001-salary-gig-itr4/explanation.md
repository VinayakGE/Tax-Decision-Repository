# Case C-000001 — Salary + Gig Income → ITR-4

## Taxpayer Profile
Resident individual, below 60. Works a salaried job and does freelance work.

## Step 1: Determine ITR Form (Decision D-001)

**Income heads present:**
- Salary income: ₹8,40,000 (gross)
- Freelance receipts: ₹3,20,000 (treated as business income under Section 44AD)
- FD Interest: ₹18,000

**Applying rules:**
- R-0001: Business income exists → ITR-1 eliminated
- R-0004: Business income is presumptive (44AD, turnover ₹3.2L << ₹3 Cr limit) → ITR-4 eligible
- No capital gains, not a director, no unlisted shares, no foreign assets, total income < ₹50L → ITR-4 confirmed

**Outcome: ITR-4**

---

## Step 2: Determine Tax Regime (Decision D-002)

**New Regime (default under R-0005):**

| Component | Amount |
|-----------|--------|
| Gross Salary | ₹8,40,000 |
| Less: Standard Deduction | ₹75,000 |
| Net Salary | ₹7,65,000 |
| Presumptive Business Income (44AD @ 6% on ₹3.2L digital) | ₹19,200 |
| FD Interest | ₹18,000 |
| **Gross Total Income** | **₹8,02,200** |
| Less: Deductions (New Regime — only 80CCD(2) applicable, not availed) | ₹0 |
| **Taxable Income** | **₹8,02,200** |

**New Regime Tax (AY2025-26 slabs):**
- Up to ₹3,00,000: Nil
- ₹3,00,001 – ₹7,00,000: 5% on ₹4,00,000 = ₹20,000
- ₹7,00,001 – ₹8,02,200: 10% on ₹1,02,200 = ₹10,220
- **Tax before rebate: ₹30,220**
- Rebate u/s 87A: Taxable income ≤ ₹12,00,000 → Rebate up to ₹60,000 — Full rebate applies
- **Tax after rebate: ₹0**
- Cess: ₹0
- **Total Tax Liability: ₹0**

**Old Regime (for comparison):**
- Deductions: 80C ₹40,000 + 80D ₹12,000 = ₹52,000
- Taxable Income: ₹8,02,200 − ₹52,000 = ₹7,50,200
- Old Regime Tax: ₹12,540 + cess ₹501.60 = ~₹13,042
- Rebate u/s 87A: ₹12,500 (income < ₹5L — not applicable here)
- **Old Regime Tax: ~₹13,042**

**Recommendation: New Regime** — results in ₹0 tax vs ₹13,042 in Old Regime.

---

## Step 3: TDS Credit (Decision D-003)

| Source | Form 16 / 16A | 26AS | Match? |
|--------|---------------|------|--------|
| Employer (BNGE12345A) | ₹28,600 | ₹28,600 | ✓ Pass (V-001) |
| Bank FD TDS | ₹1,800 | ₹1,800 | ✓ Pass |
| **Total** | **₹30,400** | **₹30,400** | |

---

## Step 4: Refund Computation (Decision D-004)

| Item | Amount |
|------|--------|
| Tax Liability | ₹0 |
| TDS Deducted | ₹30,400 |
| **Refund Due** | **₹30,400** |

---

## Validations Run

| Check | Result | Notes |
|-------|--------|-------|
| V-001 TDS Mismatch | PASS | Form 16 matches 26AS exactly |
| V-002 AIS Income Coverage | PASS | All AIS entries included |
| V-003 Bank Pre-Validation | PASS | Account pre-validated on portal |

---

## Filing Summary

- **ITR Form:** ITR-4
- **Tax Regime:** New (Section 115BAC)
- **Tax Payable:** ₹0
- **Refund:** ₹30,400
