# Milestone M1 — Engine Ready for Evidence

**Declared**: 2026-06-26  
**Phase**: End of Phase 3 (Execution) / Start of Phase 4 (Evidence)

---

## Criteria — All Met

| Criterion | Status | Evidence |
|-----------|--------|---------|
| Architecture frozen | ✅ | Scheduler, context, executor, parser framework stable. No structural changes in 3+ weeks. |
| Runtime stable | ✅ | 107 tests passing. Pipeline executes in < 300ms across 16 GMs. |
| Validation framework operational | ✅ | DVF: Golden Masters, Differential testing, Mutation testing (6/6 mutations detected), Coverage matrix. |
| Golden Masters in place | ✅ | 16 GMs across new/old regime, HRA, 80C, 80D, 80CCD(1B). |
| Real-case schema frozen | ✅ | Schema v1.0.0 declared in docs/real-case-schema.md. Fields typed, versioned, frozen. |
| Learning Velocity implemented | ✅ | LV categories: match / conservative / rule_gap / defect / unclassified. |
| Real-case runner operational | ✅ | bin/run_real_cases.py — per-field comparison, LV report, entity pressure tracking, CI exit codes. |

---

## What M1 Means

Before M1, the primary question was: *Can we build the engine?*

After M1, the primary question is: *What does reality teach us that synthesis cannot?*

This is the healthy transition. The runtime is no longer the bottleneck. Real-world cases are.

---

## Phase Map

| Phase | Label | Status |
|-------|-------|--------|
| 1 | Vision | Complete |
| 2 | Architecture | Complete |
| 3 | Execution | Complete — M1 declared |
| 4 | Evidence | **Active** |

---

## What Phase 4 Looks Like

**Input**: Anonymized real salary cases (Form 16 + declarations)  
**Process**: Encode → Run engine → Compare against human computation → Classify LV → Fix gaps  
**Output**: Higher RCI, new rules/GMs from real evidence, Entity Pressure Log updates  

**M2 gate** (what ends Phase 4's first sprint):
- 20 real cases processed
- LV match rate ≥ 80%
- Every `defect` case has a corresponding fix + GM

---

## Deductions Covered at M1

Sufficient for a large proportion of salaried taxpayers (AY2025-26):

| Section | Rule | Status |
|---------|------|--------|
| Standard deduction 16(ia) | R-0015 | ✅ |
| HRA 10(13A) | R-0029 to R-0034 | ✅ |
| 80C investments | R-0024 | ✅ |
| 80CCD(1B) NPS | R-0039 | ✅ |
| 80D health insurance | R-0035 to R-0038 | ✅ |

Next deduction (Section 24(b) house property interest) is gated on M2.

---

## Entity Pressure Log at M1

Three pressure points recorded. None justify refactoring today. Review at M2.

| ID | Class | Severity |
|----|-------|----------|
| EP-001 | Multiple employers | HIGH |
| EP-002 | Per-dependent age | MEDIUM |
| EP-003 | TDS–employer join | HIGH |
