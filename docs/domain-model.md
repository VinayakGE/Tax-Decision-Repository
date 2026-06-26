# Domain Model — Entity Ontology

> This document defines every entity the repository reasons about.
> Entities are the inputs and outputs of Rules and Decisions.
> No entity may appear in a Rule or Decision without being defined here first.

---

## 1. Taxpayer

The individual or entity filing the return.

```
Taxpayer
├── Resident Status
│   ├── Resident Ordinarily Resident (ROR)
│   ├── Resident Not Ordinarily Resident (RNOR)
│   └── Non-Resident (NR)
├── Age Category
│   ├── Below 60 (General)
│   ├── Senior Citizen (60–79)
│   └── Super Senior Citizen (80+)
├── Directorship Flag        (Director in a company: Y/N)
├── Unlisted Shares Flag     (Holds unlisted equity shares: Y/N)
├── Foreign Assets Flag      (Foreign assets or signing authority: Y/N)
└── Tax Regime
    ├── Old Regime
    └── New Regime (Default from AY2024-25)
```

---

## 2. Income

All money received by the taxpayer during the Financial Year.

```
Income
├── Salary Income
│   ├── Basic Salary
│   ├── HRA
│   ├── Special Allowances
│   ├── Perquisites
│   └── Exempt Allowances (u/s 10)
│
├── Business Income
│   ├── Regular Business (44A books)
│   ├── Presumptive Business (44AD — Turnover ≤ ₹3 Cr)
│   ├── Presumptive Business (44ADA — Professionals ≤ ₹75 L)
│   └── Speculative Business
│
├── Capital Gains
│   ├── Short-Term Capital Gain (STCG)
│   │   ├── STCG on Listed Equity / MF (15% u/s 111A)
│   │   └── STCG on Other Assets (Slab rate)
│   └── Long-Term Capital Gain (LTCG)
│       ├── LTCG on Listed Equity / MF (12.5% u/s 112A, above ₹1.25 L)
│       └── LTCG on Other Assets (12.5% u/s 112, with indexation removed from AY2025-26)
│
├── House Property Income
│   ├── Self-Occupied Property (SOP)
│   ├── Let-Out Property (LOP)
│   └── Deemed Let-Out Property
│
├── Other Sources
│   ├── Interest Income (Savings / FD / RD)
│   ├── Dividend Income
│   ├── Gifts
│   ├── Lottery / Game Show Winnings
│   └── Casual Income
│
└── Agricultural Income (Exempt, but may trigger AMT for others)
```

---

## 3. Deductions

Amounts that reduce gross total income.

```
Deductions
├── Chapter VI-A (u/s 80)
│   ├── 80C  — LIC, PPF, ELSS, Home Loan Principal (₹1.5 L limit)
│   ├── 80CCD(1) — NPS Employee Contribution
│   ├── 80CCD(1B) — Additional NPS (₹50,000 over 80CCD(1))
│   ├── 80CCD(2) — NPS Employer Contribution (no cap in new regime)
│   ├── 80D  — Medical Insurance Premiums
│   ├── 80E  — Education Loan Interest
│   ├── 80EEB — EV Loan Interest
│   ├── 80G  — Donations
│   ├── 80GG — Rent Paid (no HRA)
│   ├── 80TTA — Savings Interest (up to ₹10,000, old regime)
│   └── 80TTB — Savings + FD Interest for Senior Citizens (up to ₹50,000)
│
├── Standard Deduction
│   ├── Salary: ₹75,000 (New Regime, AY2025-26)
│   └── Salary: ₹50,000 (Old Regime)
│
├── House Property Deductions
│   ├── Standard Deduction 30% of NAV
│   └── Home Loan Interest (u/s 24b)
│
└── Business Deductions
    └── (Per books or presumptive — not enumerated here)
```

---

## 4. Tax

```
Tax
├── Income Tax
│   ├── Old Regime Slabs
│   └── New Regime Slabs (Default)
├── Surcharge
│   ├── >₹50L: 10%
│   ├── >₹1Cr: 15%
│   ├── >₹2Cr: 25%
│   └── >₹5Cr: 37% (capped at 15% for LTCG u/s 112A)
├── Health & Education Cess (4%)
├── Advance Tax
├── TDS (Tax Deducted at Source)
├── TCS (Tax Collected at Source)
└── Self-Assessment Tax
```

---

## 5. ITR Forms

The return form the taxpayer must file.

```
ITR Form
├── ITR-1 (Sahaj)
│   ├── Who: Resident individuals only
│   ├── Income: Salary + House Property (1 SOP) + Other Sources ≤ ₹50L
│   └── Who cannot: Director, unlisted shares, foreign assets, multiple HPs, capital gains
│
├── ITR-2
│   ├── Who: Individuals + HUFs with no business income
│   └── Income: Salary, HP, Capital Gains, Other Sources, Foreign Assets
│
├── ITR-3
│   ├── Who: Individuals + HUFs with business/profession income (non-presumptive)
│   └── Income: All heads + Regular business income
│
├── ITR-4 (Sugam)
│   ├── Who: Individuals, HUFs, Firms (excl. LLP) with presumptive income
│   ├── Income: Salary + Business (44AD/44ADA/44AE) + HP + Other Sources ≤ ₹50L
│   └── Who cannot: Director, unlisted shares, foreign assets, capital gains
│
├── ITR-5 — Firms, LLPs, AOPs, BOIs
├── ITR-6 — Companies
└── ITR-7 — Trusts, Political Parties, Research Associations
```

*Repository scope: ITR-1 through ITR-4 only (individual filers).*

---

## 6. Documents / Evidence Sources

```
Document
├── AIS (Annual Information Statement)
│   ├── Salary
│   ├── Interest (Savings, FD, RD)
│   ├── Dividend
│   ├── Capital Gains (Securities, MF, Property)
│   ├── Foreign Remittance
│   ├── Rent Received
│   └── TDS / TCS Summary
│
├── 26AS (Tax Credit Statement)
│   ├── TDS (Part A)
│   ├── TDS on Property (Part A1)
│   ├── TDS on Rent (Part A2)
│   ├── TCS (Part B)
│   ├── Advance Tax / Self-Assessment Tax (Part C)
│   └── TDS Defaults (Part D)
│
├── Prefill JSON (from IT Portal)
│   ├── Personal Details
│   ├── Bank Accounts
│   ├── AIS Summary
│   └── Previous Year Carry-Forwards
│
├── Form 16
│   ├── Part A — TDS Summary
│   └── Part B — Salary Breakdown + Deductions
│
├── Form 16A — TDS on Non-Salary Income
│
├── Form 26QB — TDS on Property Purchase
│
├── Capital Gains Statement (Broker)
│
├── Bank Statements
│
└── Rent Receipts / Rental Agreement
```

---

## 7. Regime

```
Tax Regime
├── Old Regime
│   ├── All deductions applicable (80C, 80D, HRA, LTA, etc.)
│   └── Higher tax slabs
│
└── New Regime (Default from AY2024-25)
    ├── Standard deduction ₹75,000 applicable (AY2025-26)
    ├── 80CCD(2) — NPS Employer contribution applicable
    ├── Most other deductions NOT applicable
    └── Lower tax slabs
```

---

## 8. Filing Status

```
Filing Status
├── Original Return
├── Revised Return (u/s 139(5))
├── Belated Return (u/s 139(4))
└── Updated Return (u/s 139(8A) — ITR-U)
```

---

## 9. Relationship Map (Summary)

```
Taxpayer ──has──► Income (multiple heads)
Taxpayer ──claims──► Deductions
Taxpayer ──holds──► Documents (Evidence)
Taxpayer ──must file──► ITR Form (decided by rules)
Taxpayer ──chooses──► Tax Regime
Taxpayer ──owes / is owed──► Tax / Refund

Income + Deductions ──► Taxable Income
Taxable Income ──► Tax (per slabs + surcharge + cess)
Tax - TDS - TCS - Advance Tax ──► Refund / Balance Due
```

---

*Document Version: 1.0.0*
*Effective: AY2025-26*
