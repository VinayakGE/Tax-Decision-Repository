# Changelog

All notable changes to this repository are documented here.
Format: `[CH-XXXX] YYYY-MM-DD — Type — Summary`

---

## v2.0.0-dev — AY2025-26 (2026-06-26) [continued]

**Wave 2: Evidence Integrity Engine — R-0007 through R-0014.**

### Added (Wave 2)
- [CH-0007] `docs/evidence-integrity.md` — Wave 2 architecture: four submodules (Source Reconciliation, Evidence Completeness, Evidence Authenticity, Evidence Lineage), reconciliation status values, evidence authority hierarchy, lineage graph node types
- [CH-0007] `rules/R-0007` — AIS ↔ 26AS reconciliation: variance thresholds (< 1% reconciled, 1–5% minor, > 5% major), presence mismatch detection, 26AS authority for TDS credits
- [CH-0007] `rules/R-0008` — AIS ↔ Prefill reconciliation: stale Prefill detection, AIS always supersedes Prefill
- [CH-0007] `rules/R-0009` — 26AS ↔ Prefill reconciliation: TDS credit only claimable if in 26AS; Prefill TDS not in 26AS flagged as unclaimed_credit_risk
- [CH-0007] `rules/R-0010` — Duplicate income detection: same income in Form 16 + AIS resolved by authority hierarchy (not summed)
- [CH-0007] `rules/R-0011` — Duplicate TDS detection: same TDS in 26AS + Form 16 resolved (26AS is the credit; Form 16 is corroborating)
- [CH-0007] `rules/R-0012` — Missing evidence detection: critical_missing (halt), expected_missing (reduce ECS), acceptable_absent
- [CH-0007] `rules/R-0013` — Evidence authenticity: PAN consistency (blocking), TAN format, AY consistency, Form 16 TAN must match 26AS
- [CH-0007] `rules/R-0014` — Evidence lineage generation: computation provenance DAG tracing every output to evidence leaf, rule_applied leaf, or user_declared leaf; blocks Stage 13 if any orphaned nodes
- [CH-0007] Tests T-0011 through T-0027 (17 tests covering all 8 Wave 2 rules)

### Updated (Wave 2)
- [CH-0007] `docs/benchmark-jab.md` — Added M-07 Evidence Integrity Score (≥95% target); renumbered M-07/M-08/M-09 → M-08/M-09/M-10; total metrics: 11
- [CH-0007] `schemas/benchmark-schema.json` — Added M07_evidence_integrity_score with failure breakdown; renamed M07/M08/M09 keys
- [CH-0007] `registry/rule-registry.json` — Added R-0007 through R-0014
- [CH-0007] `registry/index.json` — Rules: 6→14 active, Tests: 7→27 pending

---

## v2.0.0-dev — AY2025-26 (2026-06-26)

**Phase 5: Knowledge Expansion begins. R-0006 — first Wave 1 rule.**

### Added
- [CH-0006] `rules/R-0006-income-classification-authority.json` — Canonical evidence-to-income-head mapping: 20-entry lookup table covering Form 16, 26AS TDS sections (192, 193, 194A, 194C, 194I, 194J, 194IA, 194S, 194B), AIS categories (salary, interest, dividend, rent, business receipts, capital gains, VDA, lottery, agricultural, foreign), with `requires_confirmation` flags for ambiguous cases
- [CH-0006] `tests/T-0007` — Form 16 → Head 1 Salary (positive)
- [CH-0006] `tests/T-0008` — 26AS u/s 194J → Head 3 requires confirmation (positive — confirmation path)
- [CH-0006] `tests/T-0009` — AIS FD interest → Head 5 Other Sources (positive)
- [CH-0006] `tests/T-0010` — Unknown source → unclassified_pending escalation (negative)

### Updated
- [CH-0006] `docs/benchmark-jab.md` — Added M-00 Decision Coverage as north-star KPI (≥85% target for v2.0); total metrics now 10
- [CH-0006] `schemas/benchmark-schema.json` — Added M00_decision_coverage metric with escalation breakdown
- [CH-0006] `schemas/rule-schema.json` — Extended logic object to support optional `lookup_table` array for mapping-type rules
- [CH-0006] `GOVERNANCE.md` — Replaced flat rule priority list with Wave 1-4 structure (Wave 1: decision-critical, Wave 2: reconciliation, Wave 3: computation, Wave 4: edge cases)
- [CH-0006] `registry/rule-registry.json` — Added R-0006 entry
- [CH-0006] `registry/index.json` — Rules: 5→6 active, Tests: 3→7 pending

---

## v1.3.1 — AY2025-26 (2026-06-26)

**Governance Charter — the last document before Phase 5.**

### Added
- [CH-0005] `GOVERNANCE.md` — Repository Governance Charter: seven permanent principles, release quality profile format, Phase 5 epic priorities, rule authoring sequence for Epic 1

### Updated
- [CH-0005] `registry/version-registry.json` — Added quality profile blocks to all four version entries (active_rules, deprecated_rules, active_cases, total_tests, jab_score, finance_act_version, gss_case_count)

---

## v1.3.0 — AY2025-26 (2026-06-26)

**Processing Pipeline, five Sprint 1 engines, JAB, Decision Replay, DEL, and tax tables. Architecture feature-frozen.**

### Added
- [CH-0004] `docs/pipeline.md` — 14-stage Jarviz Processing Pipeline with stage contracts, invariants, and Repository→Pipeline mapping
- [CH-0004] `docs/engines/engine-1-itr-selection.md` — ITR Selection Engine: contract, algorithm, missing field handling, 12 test cases, JAB metrics
- [CH-0004] `docs/engines/engine-2-income-classification.md` — Income Classification Engine: 5 heads of income, AY2025-26 Finance Act 2024 rate split (23 Jul 2024), ambiguous cases
- [CH-0004] `docs/engines/engine-3-tax-computation.md` — Tax Computation Engine: 14-step deterministic algorithm, both-regime comparison, precision rules, 8 test cases
- [CH-0004] `docs/engines/engine-4-validation.md` — Validation Engine: 6 Sprint 1 validations (V-001 through V-006), selection logic, severity blocking, 8 test cases
- [CH-0004] `docs/engines/engine-5-explanation.md` — Explanation Engine: AI in retrieval+narration mode only, constrained templates, 7 tone rules, 7 test cases
- [CH-0004] `docs/benchmark-jab.md` — Jarviz Accuracy Benchmark: 9 metrics with formulas, GSS requirements, JAB report format, release gate rules
- [CH-0004] `docs/decision-replay.md` — Decision Replay system: schema, post-filing outcome fields, corrections block, feedback loop to rule authoring, query patterns
- [CH-0004] `docs/decision-execution-log.md` — Decision Execution Log (DEL): per-execution operational record, stage log, rules invoked, operational metrics
- [CH-0004] `schemas/benchmark-schema.json` — JSON Schema for JAB report objects
- [CH-0004] `schemas/replay-schema.json` — JSON Schema for combined DEL + Replay records
- [CH-0004] `data/AY2025-26/tax-tables.json` — AY2025-26 tax computation data: New/Old Regime slabs, rebate 87A limits, special rates (111A/112A/112/lottery/crypto), surcharge brackets, cess 4%, presumptive rates, advance tax schedule, TDS reference rates
- [CH-0004] `benchmarks/README.md` — GSS structure, benchmark run instructions, release gate summary
- [CH-0004] `replays/README.md` — Replay directory structure, immutability policy, post-filing update instructions

### Architecture Decision
The architecture is declared **feature-frozen** as of v1.3.0. All future contributions must add at least one of: a deterministic rule, a real-world case, an automated test, a measurable engine improvement, or a user-facing workflow change. No further architectural abstractions will be accepted.

---

## v1.2.0 — AY2025-26 (2026-06-26)

**Pattern Repository — 8 filing patterns covering ~95% of individual filers.**

### Added
- [CH-0003] `schemas/pattern-schema.json` — JSON Schema for pattern objects
- [CH-0003] `docs/pattern-matching.md` — Pattern matching process: document fingerprint → confirmation questions → pattern confirmation or escalation → rule engine
- [CH-0003] `patterns/PAT-001` — Salaried, Single Employer (~45% of filers) → ITR-1
- [CH-0003] `patterns/PAT-002` — Salary + Gig / Freelance 44AD (~12%) → ITR-4
- [CH-0003] `patterns/PAT-003` — Salary + Capital Gains (~10%) → ITR-2
- [CH-0003] `patterns/PAT-004` — Multiple Employers / Job Change (~8%) → ITR-1
- [CH-0003] `patterns/PAT-005` — NRI with Indian Income (~3%) → ITR-2
- [CH-0003] `patterns/PAT-006` — Pensioner + FD Interest (~7%) → ITR-1
- [CH-0003] `patterns/PAT-007` — Salary + Let-Out House Property (~4%) → ITR-1
- [CH-0003] `patterns/PAT-008` — Professional Presumptive 44ADA (~3%) → ITR-4
- [CH-0003] `patterns/README.md` — Pattern index and usage guide
- [CH-0003] `registry/pattern-registry.json` — Pattern registry ordered by prevalence

### Updated
- [CH-0003] `registry/index.json` — Added pattern count (8 active, ~95% estimated coverage)

---

## v1.1.0 — AY2025-26 (2026-06-26)

**Scalability architecture — five missing modules.**

### Added
- [CH-0002] `registry/` — Repository Index (operating system): rule-registry, decision-registry, evidence-registry, validation-registry, case-registry, section-registry, version-registry, index.json
- [CH-0002] `dependency_graph/SEC-002-section-44AD.json` — Full 7-layer impact map for Section 44AD with update procedure
- [CH-0002] `dependency_graph/SEC-004-section-115BAC.json` — Full 7-layer impact map for Section 115BAC with update procedure
- [CH-0002] `schemas/dependency-schema.json` — JSON Schema for dependency graph files
- [CH-0002] `schemas/registry-index-schema.json` — Base schema for registry files
- [CH-0002] `docs/rule-lifecycle.md` — 7-stage rule lifecycle with review checklists (draft → peer_reviewed → legal_reviewed → active → deprecated → superseded → archived)
- [CH-0002] `docs/confidence-model.md` — Evidence Completeness Score, Evidence Quality Weights, Confidence Bands A–E, per-decision confidence tables, required output format
- [CH-0002] `docs/conflict-resolver.md` — 4 conflict types, resolution hierarchy table, delta-threshold rules, conflict log schema
- [CH-0002] `docs/rule-authoring-guide.md` — 11-step guide enabling any contributor to write Rule N+1 without asking the original author

### Updated
- [CH-0002] `ARCHITECTURE.md` — Added sections 10–15 covering Registry, Dependency Graph, Lifecycle, Confidence Model, Conflict Resolver, Rule Authoring Guide
- [CH-0002] `README.md` — Updated structure, object counts, design principles

---

## v1.0.0 — AY2025-26 (2026-06-26)

**Initial knowledge architecture release.**

### Added
- [CH-0001] `ARCHITECTURE.md` — Repository constitution defining all 7 core object types and their relationships
- [CH-0001] `docs/domain-model.md` — Full entity ontology: Taxpayer, Income, Deductions, Tax, ITR Forms, Documents, Regime, Filing Status
- [CH-0001] `docs/evidence-catalogue.md` — Evidence sources E-001 through E-007 with field-level definitions
- [CH-0001] `docs/decision-catalogue.md` — Decision catalogue D-001 through D-010 (5 active, 5 draft)
- [CH-0001] `schemas/rule-schema.json` — JSON Schema for Rule objects
- [CH-0001] `schemas/evidence-schema.json` — JSON Schema for Evidence objects
- [CH-0001] `schemas/decision-schema.json` — JSON Schema for Decision objects
- [CH-0001] `schemas/validation-schema.json` — JSON Schema for Validation objects
- [CH-0001] `schemas/case-schema.json` — JSON Schema for Case objects
- [CH-0001] `schemas/change-schema.json` — JSON Schema for Change objects
- [CH-0001] `schemas/test-schema.json` — JSON Schema for Test objects
- [CH-0001] `rules/R-0001` — ITR-1 ineligible when business income exists
- [CH-0001] `rules/R-0002` — ITR-1 eligible for salary-only taxpayers
- [CH-0001] `rules/R-0003` — ITR-2 required for foreign assets/income
- [CH-0001] `rules/R-0004` — ITR-4 eligible for presumptive income (44AD/44ADA)
- [CH-0001] `rules/R-0005` — New Regime is default from AY2024-25
- [CH-0001] `decision_trees/DT-001` — ITR Form Selection decision tree (YAML)
- [CH-0001] `validation/V-001` — TDS mismatch Form 16 vs 26AS (critical)
- [CH-0001] `validation/V-002` — AIS income not reported (critical)
- [CH-0001] `validation/V-003` — Refund bank account not pre-validated (high)
- [CH-0001] `cases/C-000001` — Salary + Gig Income → ITR-4, New Regime (synthetic)
- [CH-0001] `tests/T-0001` — R-0001: business income disqualifies ITR-1
- [CH-0001] `tests/T-0003` — R-0002: salary-only → ITR-1 eligible
- [CH-0001] `tests/T-0006` — R-0004: salary + presumptive → ITR-4
- [CH-0001] `prompts/P-001` — AI prompt template for ITR form selection
- [CH-0001] `prompts/P-002` — AI prompt template for regime selection
- [CH-0001] `CONTRIBUTING.md` — Contribution guidelines
