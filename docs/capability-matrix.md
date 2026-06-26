# Jarviz Capability Matrix

> What can Jarviz do right now, and how confident are we in each capability?

This document replaces rule counts and test counts as the primary measure of product maturity. A capability is only marked complete when: (1) rules exist, (2) tests pass, and (3) the capability has been exercised on at least one verified real-world case.

---

## Reading the Matrix

| Symbol | Meaning |
|--------|---------|
| ✅ Complete | Rules active, tests passing, coverage verified on real cases |
| 🟡 In Progress | Rules authored, tests pending, not yet validated on real cases |
| ⏳ Planned | On the roadmap with an assigned wave |
| ❌ Not Started | Not yet scoped or prioritized |

A capability marked 🟡 may be used in the pipeline but its outputs should be treated as high-confidence estimates, not certified results.

---

## Core Capabilities

| Capability | Status | Wave | Rules | Tests | Notes |
|------------|--------|------|-------|-------|-------|
| **ITR Form Selection** | ✅ Complete | Wave 1 | R-0001–R-0004 | T-0001–T-0006 | Covers ITR-1, ITR-2, ITR-4. ITR-3 logic planned. |
| **Tax Regime Selection** | ✅ Complete | Wave 1 | R-0005 | T-0008 | New Regime as default (AY2024-25+). Comparison via R-0018. |
| **Income Classification** | ✅ Complete | Wave 1 | R-0006 | T-0007–T-0010 | 20-entry lookup table. 5 heads of income. |
| **Evidence Integrity** | 🟡 In Progress | Wave 2 | R-0007–R-0014 | T-0011–T-0027 | Source reconciliation, completeness, authenticity, lineage. |
| **Tax Computation** | 🟡 In Progress | Wave 3A | R-0015–R-0023 | T-0028–T-0045 | Slab engine, rebate, cess, surcharge, 234A/B/C, refund/demand. |
| **Tax Adjustments (Deductions)** | ⏳ Planned | Wave 3B | — | — | 80C, 80D, HRA, LTA, Chapter VI-A. Target: ~R-0024–R-0060. |
| **Capital Gains** | ⏳ Planned | Wave 3B/4 | — | — | Equity (111A/112A), property (112), debt, VDA. Date-split computation. |
| **House Property** | ⏳ Planned | Wave 3B | — | — | Let-out vs self-occupied, 24(b) interest, 30% standard deduction. |
| **Presumptive Taxation** | ✅ Complete | Wave 1 | R-0004 | T-0006 | 44AD/44ADA eligible via R-0004. Computation rules planned. |
| **Advance Tax** | 🟡 In Progress | Wave 3A | R-0022 | T-0042–T-0043 | 234A/B/C interest. Installment schedule modeled. |
| **Refund / Demand Position** | 🟡 In Progress | Wave 3A | R-0023 | T-0044–T-0045 | Final net position. TDS credit from 26AS only. |

---

## Evidence and Data Capabilities

| Capability | Status | Wave | Notes |
|------------|--------|------|-------|
| **AIS Parsing** | ⏳ Planned | Engine | Evidence source E-001 defined; parser not yet implemented |
| **26AS Parsing** | ⏳ Planned | Engine | Evidence source E-002 defined; parser not yet implemented |
| **Form 16 Parsing** | ⏳ Planned | Engine | Evidence source E-003 defined; parser not yet implemented |
| **AIS ↔ 26AS Reconciliation** | 🟡 In Progress | Wave 2 | R-0007 authored; T-0011–T-0013 pending |
| **AIS ↔ Prefill Reconciliation** | 🟡 In Progress | Wave 2 | R-0008 authored |
| **26AS ↔ Prefill Reconciliation** | 🟡 In Progress | Wave 2 | R-0009 authored |
| **Duplicate Income Detection** | 🟡 In Progress | Wave 2 | R-0010 authored |
| **Duplicate TDS Detection** | 🟡 In Progress | Wave 2 | R-0011 authored |
| **Missing Evidence Detection** | 🟡 In Progress | Wave 2 | R-0012 authored |
| **Evidence Authenticity Checks** | 🟡 In Progress | Wave 2 | R-0013 authored |
| **Evidence Lineage Generation** | 🟡 In Progress | Wave 2 | R-0014 authored |

---

## Edge Case Capabilities

| Capability | Status | Wave | Notes |
|------------|--------|------|-------|
| **NRI / Foreign Income** | ⏳ Planned | Wave 4 | ITR-2 flag via R-0003. RNOR status, DTAA rules: Wave 4. |
| **ESOP Taxation** | ⏳ Planned | Wave 4 | Perquisite valuation complex; deferred to Wave 4 |
| **Crypto / VDA** | ⏳ Planned | Wave 3B | R-0006 classifies VDA; 115BBH computation rule planned |
| **Revised / Belated Return** | ⏳ Planned | Wave 4 | Different due dates, interest implications |
| **HUF Filing** | ❌ Not Started | — | Separate entity; not in v2.0 scope |
| **Company / LLP Filing** | ❌ Not Started | — | Out of scope — individual filers only |
| **Notice Response Analysis** | ❌ Not Started | — | Post-filing analysis; separate product scope |
| **DTAA Relief (Treaty)** | ❌ Not Started | — | Country-specific; high complexity |
| **Tax Audit (44AB)** | ❌ Not Started | — | Gross receipts > ₹1Cr. Audit requirement flagging only in scope. |

---

## Filing Workflow Capabilities

| Capability | Status | Notes |
|------------|--------|-------|
| **Pattern Matching** | ✅ Complete | 8 patterns covering ~95% of individual filers (PAT-001 through PAT-008) |
| **Regime Comparison** | 🟡 In Progress | R-0018 authored; requires Wave 3A to be exercised on real cases |
| **Validation Checks** | ✅ Complete | V-001 (TDS mismatch), V-002 (AIS income not reported), V-003 (bank not pre-validated) |
| **Decision Explanation** | ⏳ Planned | Engine 5 architecture defined; AI prompt templates P-001, P-002 exist |
| **Decision Replay** | ⏳ Planned | Schema and architecture defined; requires live pipeline |
| **Refund Tracking** | ❌ Not Started | Post-filing; out of current scope |

---

## Benchmark Targets by Milestone

| Milestone | Decision Coverage (M-00) | Capabilities Ready |
|-----------|--------------------------|-------------------|
| v2.0.0 (current dev) | ≥ 85% target | ITR Selection, Classification, Evidence Integrity, Tax Computation |
| v2.5.0 | ≥ 90% | + Deductions (Wave 3B), Capital Gains |
| v3.0.0 | ≥ 95% | + Edge Cases (NRI, VDA, Presumptive computation) |

---

*Last updated: 2026-06-26 (Wave 3A — Tax Computation Engine)*
