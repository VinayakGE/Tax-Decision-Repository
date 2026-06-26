# Changelog

All notable changes to this repository are documented here.
Format: `[CH-XXXX] YYYY-MM-DD — Type — Summary`

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
