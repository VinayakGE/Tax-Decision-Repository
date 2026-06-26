# Jarviz Tax Decision Repository

An evidence-backed, machine-readable repository that encodes Indian income tax laws, filing rules, eligibility criteria, decision trees, validation logic, and real-world filing scenarios into a structured decision system for explainable tax automation.

The AI retrieves. The repository decides.

---

## Architecture

Read [ARCHITECTURE.md](ARCHITECTURE.md) first. It defines the seven core objects and how they relate:

| Object | What it is | Location |
|--------|-----------|----------|
| **Rule** | One atomic, citable piece of tax logic | `/rules/R-XXXX-*.json` |
| **Evidence** | A document or data source (AIS, 26AS, Form 16…) | `/schemas/evidence/` |
| **Decision** | A bounded question the system answers | `/decision_trees/D-XXX-*.json` |
| **Validation** | A consistency or compliance check | `/validation/V-XXX-*.json` |
| **Case** | A complete filing scenario (real or synthetic) | `/cases/C-XXXXXX-*/` |
| **Change** | An immutable record of any modification | `/changes/CH-XXXX.json` |
| **Version** | A snapshot of the rule set at a point in time | Git tag |

---

## Repository Structure

```
/
├── ARCHITECTURE.md          ← Start here. The constitution.
├── CONTRIBUTING.md          ← How to add rules, cases, decisions.
├── CHANGELOG.md             ← Redirect to /changes/CHANGELOG.md
│
├── docs/
│   ├── domain-model.md      ← Entity ontology (Income, ITR forms, etc.)
│   ├── evidence-catalogue.md← All evidence sources and their fields
│   └── decision-catalogue.md← Master list of decisions the system makes
│
├── schemas/
│   ├── rule-schema.json
│   ├── evidence-schema.json
│   ├── decision-schema.json
│   ├── validation-schema.json
│   ├── case-schema.json
│   ├── change-schema.json
│   └── test-schema.json
│
├── rules/
│   ├── R-0001-itr1-ineligible-business-income.json
│   ├── R-0002-itr1-eligible-salary-only.json
│   ├── R-0003-itr2-foreign-assets.json
│   ├── R-0004-itr4-presumptive-eligible.json
│   └── R-0005-new-regime-default.json
│
├── decision_trees/
│   └── DT-001-itr-form-selection.yaml
│
├── validation/
│   ├── V-001-tds-mismatch-form16-26as.json
│   ├── V-002-ais-income-missing.json
│   └── V-003-refund-bank-account-prevalidated.json
│
├── knowledge_graph/
│   └── entities.json        ← Entity relationships
│
├── cases/
│   └── C-000001-salary-gig-itr4/
│       ├── case.json
│       └── explanation.md
│
├── tests/
│   ├── T-0001-*.json
│   ├── T-0003-*.json
│   └── T-0006-*.json
│
├── prompts/
│   ├── P-001-itr-form-selection.md
│   └── P-002-regime-selection.md
│
├── changes/
│   ├── CHANGELOG.md
│   └── CH-0001.json
│
├── data/                    ← Tax data (AY-scoped, empty until needed)
└── explanations/            ← Reusable explanation templates
```

---

## Current Scope

**Assessment Year: AY2025-26 (FY 2024-25)**

| Object Type | Count | Status |
|-------------|-------|--------|
| Rules | 5 | active |
| Decisions | 5 active, 5 draft | in progress |
| Decision Trees | 1 | active |
| Validations | 3 | active |
| Cases | 1 | synthetic |
| Tests | 3 | pending |
| Prompts | 2 | active |
| Schemas | 7 | active |

---

## Design Principles

- **One rule = one file.** Rules are never bundled.
- **Every rule cites legal authority.** No rule is active without an Act and Section.
- **Every rule has tests.** Untested rules stay in `draft`.
- **Evidence before decision.** Every decision traces back to a document.
- **Changes are immutable records.** Nothing is silently edited.
- **AI retrieves, repository decides.** The AI assistant never invents rules.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

MIT License — see [LICENSE](LICENSE).
