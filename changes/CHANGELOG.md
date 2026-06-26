# Changelog

All notable changes to this repository are documented here.
Format: `[CH-XXXX] YYYY-MM-DD — Type — Summary`

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
