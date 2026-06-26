# Entity Pressure Log

**Purpose**: Record every point where the flat evidence model creates friction. Do not implement entity modeling yet — collect the signal first. If the same pressure points recur across 50–100 rules, the pattern will justify the architectural investment.

**Decision threshold**: Review after the first real-case ingestion batch. If 3+ distinct pressure classes repeat, begin entity model design.

---

## Pressure Log

### EP-001 — Multiple Employers (HRA, Salary Head)

**Rule(s)**: R-0029 (HRA evidence completeness), R-0015 (income assembly)
**Date observed**: Wave 3B / HRA implementation
**What became awkward**:
`basic_salary`, `hra_actual`, and `rent_paid` are flat scalars in the evidence context. In a two-employer scenario (common mid-year job change), each employer has its own gross salary, basic salary, and HRA component. The current model silently takes only the first (or only) employer's values.
**What an entity model would solve**:
`Employer` entity with fields `{tan, gross_salary, basic_salary, hra_actual}`. HRA calculation would iterate over employers, aggregate, and apply the min() over combined components.
**Current workaround**: Out of scope — single employer only for now.
**Recurrence risk**: HIGH — multiple employers affect HRA, TDS reconciliation, standard deduction.

---

### EP-002 — Parent Age vs. Taxpayer Age (80D)

**Rule(s)**: R-0035, R-0037
**Date observed**: Wave 3B / 80D implementation
**What became awkward**:
`age_bracket` (taxpayer) and `parent_age_bracket` are separate flat fields. If multiple parents have different ages (e.g., father 65, mother 58), the current model takes one `parent_age_bracket` for both and applies a single cap. The higher-paying senior cap would be silently mis-applied to the non-senior parent.
**What an entity model would solve**:
`Dependent` entity with `{relationship, age, age_bracket}`. 80D would compute per-person premium and apply the correct cap per person, then sum.
**Current workaround**: Assume single age bracket for all parents. Document this limitation.
**Recurrence risk**: MEDIUM — affects 80D only today, but 80DD and 80DDB have similar per-dependent structure.

---

### EP-003 — TDS Reconciliation Across Multiple Employers

**Rule(s)**: R-0023 (refund/demand)
**Date observed**: Wave 3A / TDS design
**What became awkward**:
`tds_credits_from_26AS` is a list of `{tan, section, amount, employer}` dicts — already partially entity-shaped. But the salary head is a separate list of `{source, gross_salary, employer, tan}` dicts. Matching TDS credits to the correct employer salary entry requires a join on `tan`, which is currently implicit rather than enforced.
**What an entity model would solve**:
`EmployerRecord` entity linking `{tan → gross_salary, tds_amount, form16_reference}`. TDS reconciliation becomes a lookup rather than an implicit assumption.
**Current workaround**: Assume TDS credits match salary entries by convention. No validation rule yet.
**Recurrence risk**: HIGH — any real Form 16 case with multiple employers will surface this.

---

## Summary

| ID | Pressure Class | Recurrences | Severity |
|----|---------------|-------------|----------|
| EP-001 | Multiple employers | 2 (HRA + TDS) | HIGH |
| EP-002 | Per-dependent age | 1 | MEDIUM |
| EP-003 | TDS–employer join | 1 | HIGH |

**Running count**: 3 pressure points across 2 distinct classes (employer multiplicity, dependent multiplicity).

**Next review**: After first real-case batch (B4 milestone).
