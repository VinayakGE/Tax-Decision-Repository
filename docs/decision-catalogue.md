# Decision Catalogue — Phase 4

> This is the master list of every bounded question the repository can answer.
> Each decision has a unique ID, a question, required inputs, and a pointer to its decision tree.
> No question may be answered by the AI without a corresponding Decision entry here.

---

## Decision Index

| ID    | Question                           | Status   | Tree        | Rules |
|-------|------------------------------------|----------|-------------|-------|
| D-001 | Which ITR form must be filed?      | active   | DT-001      | R-0001 to R-0020 |
| D-002 | Which tax regime is optimal?       | active   | DT-002      | R-0021 to R-0040 |
| D-003 | What is the correct TDS credit?    | active   | DT-003      | R-0041 to R-0050 |
| D-004 | What is the refund or tax due?     | active   | DT-004      | R-0051 to R-0060 |
| D-005 | Is the taxpayer eligible for ITR-4?| active   | DT-005      | R-0001, R-0005, R-0006 |
| D-006 | Are there carry-forward losses?    | draft    | DT-006      | TBD |
| D-007 | Is advance tax applicable?         | draft    | DT-007      | TBD |
| D-008 | Is audit required?                 | draft    | DT-008      | TBD |
| D-009 | Are there foreign assets to report?| draft    | DT-009      | TBD |
| D-010 | Which deductions can be claimed?   | draft    | DT-010      | TBD |

---

## D-001 — Which ITR form must be filed?

**Question:** Given the taxpayer's income profile, which ITR form is legally required?

**Inputs Required:**
- Income heads present (E-001 AIS, E-003 Prefill)
- Resident status
- Directorship flag
- Unlisted shares flag
- Foreign assets flag
- Agricultural income > ₹5,000 flag

**Output:** ITR form ID (`ITR-1`, `ITR-2`, `ITR-3`, `ITR-4`)

**Decision Logic (high level):**
1. If business income (non-presumptive) exists → ITR-3
2. If presumptive business (44AD/44ADA) and no disqualifiers → ITR-4
3. If capital gains exist and no business income → ITR-2
4. If salary only + HP (≤1 SOP) + other sources ≤ ₹50L + no disqualifiers → ITR-1
5. Otherwise → ITR-2

**Disqualifiers for ITR-1 and ITR-4:**
- Director in a company
- Holds unlisted equity shares
- Foreign assets or foreign income
- Non-resident or RNOR

**Tree:** `decision_trees/DT-001-itr-form-selection.yaml`

---

## D-002 — Which tax regime is optimal?

**Question:** Should the taxpayer opt for the Old Regime or the New Regime?

**Inputs Required:**
- Gross salary income
- Total Chapter VI-A deductions claimable
- HRA exemption claimable
- Home loan interest (u/s 24b)
- NPS employer contribution (80CCD(2))
- Tax liability under both regimes

**Output:** Recommended regime + breakeven analysis

**Decision Logic (high level):**
1. Compute tax under Old Regime (gross income − all deductions)
2. Compute tax under New Regime (gross income − std deduction − 80CCD(2))
3. Compare and recommend lower
4. Flag: New Regime is default from AY2024-25; taxpayer must actively opt out

**Tree:** `decision_trees/DT-002-regime-selection.yaml`

---

## D-003 — What is the correct TDS credit?

**Question:** What TDS amount should be claimed in the return?

**Inputs Required:**
- 26AS (E-002) — authoritative TDS credit
- Form 16 Part A (E-004) — employer TDS
- Form 16A (E-005) — non-salary TDS
- AIS TDS summary (E-001)

**Output:** Total TDS claimable, broken by deductor

**Decision Logic:**
1. Use 26AS as primary source
2. For each deductor in Form 16 / 16A — verify against 26AS
3. Flag mismatches as V-001 (critical validation)
4. If AIS shows TDS not in 26AS — flag for deductor follow-up

**Tree:** `decision_trees/DT-003-tds-credit-computation.yaml`

---

## D-004 — What is the refund or tax due?

**Question:** After computing income tax and crediting all taxes paid, is there a refund or a balance due?

**Inputs Required:**
- Total taxable income (after D-001, D-002)
- Total tax liability (income tax + surcharge + cess)
- TDS credit (from D-003)
- TCS credit (from 26AS)
- Advance tax paid (from 26AS)
- Self-assessment tax paid

**Output:** Refund amount OR balance due (with interest u/s 234B/234C if applicable)

**Tree:** `decision_trees/DT-004-refund-or-tax-due.yaml`

---

## D-005 — Is the taxpayer eligible for ITR-4?

**Question:** Does the taxpayer qualify to use ITR-4 (Sugam)?

**Inputs Required:**
- Business income type (44AD / 44ADA / 44AE)
- Total income threshold (≤ ₹50L)
- Directorship flag
- Unlisted shares flag
- Foreign assets flag
- Capital gains flag
- Non-resident flag

**Output:** `eligible` | `ineligible` (with reason)

**Tree:** `decision_trees/DT-005-itr4-eligibility.yaml`

---

*Document Version: 1.0.0*
*Effective: AY2025-26*
