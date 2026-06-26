# Jarviz Tax Decision Repository — Architecture

> This document is the constitution of the repository.
> Every rule, decision tree, test case, and change entry must conform to the definitions and relationships described here.
> No content may be added without a corresponding definition in this document.

---

## 1. Purpose

This repository encodes Indian income tax law into machine-readable, evidence-backed, explainable decision logic. It is designed to power an AI tax assistant (Jarviz) that retrieves knowledge from this repository rather than hallucinating rules.

The AI retrieves. The repository decides.

---

## 2. Core Object Model

There are seven first-class objects in this repository. Each has a strict definition, a canonical file location, and a schema it must conform to.

```
Evidence
   └── feeds ──► Decision
                    └── applies ──► Rule(s)
                                      └── produces ──► Explanation
                                      └── validated by ──► Validation
                                      └── proven by ──► Case
                                      └── tracked by ──► Change
```

### 2.1 Rule

A **Rule** is a single, atomic, citable piece of tax logic.

| Property       | Description |
|----------------|-------------|
| ID             | Unique identifier. Format: `R-XXXX` (zero-padded, sequential) |
| Title          | Short human-readable label |
| Description    | Plain-English statement of what the rule says |
| Logic          | Formal condition → outcome expression |
| Authority      | Legal source: Act, Section, Notification, Circular, Proviso |
| Effective Date | Date from which this rule is in force |
| Sunset Date    | Date this rule ceases to apply (null if still active) |
| Assessment Year| AY to which this rule applies, e.g. `AY2025-26` |
| Version        | Semver string, e.g. `1.0.0` |
| Status         | `draft` | `active` | `deprecated` | `superseded` |
| Tags           | Free-form classification labels |
| Evidence Refs  | List of evidence types this rule consumes |
| Decision Refs  | List of decisions this rule participates in |
| Test Refs      | IDs of test cases that verify this rule |
| Change Refs    | IDs of change entries that modified this rule |

**One rule = one file.** Location: `rules/R-XXXX-slug.json`

### 2.2 Evidence

**Evidence** is a document or data source from which facts are extracted to feed decisions.

| Property     | Description |
|--------------|-------------|
| ID           | Format: `E-XXX` |
| Name         | Common name, e.g. `AIS`, `Form 16`, `26AS` |
| Description  | What this document contains |
| Source       | Who issues it (e.g. Income Tax Department, Employer) |
| Format       | `PDF` | `JSON` | `XML` | `Portal` |
| Fields       | List of data fields this evidence contains |
| Reliable For | Which facts this evidence is authoritative for |
| Issued By    | Issuing authority |
| Frequency    | `Annual` | `Per-Transaction` | `On-Request` |

**One evidence source = one schema entry.** Location: `schemas/evidence/E-XXX-slug.json`

### 2.3 Decision

A **Decision** is a named, bounded question that the system must answer for a taxpayer.

| Property      | Description |
|---------------|-------------|
| ID            | Format: `D-XXX` |
| Title         | Question the decision answers, e.g. "Which ITR form applies?" |
| Description   | Scope and context |
| Inputs        | Evidence types and entity fields required |
| Outputs       | What the decision produces (a value, a set, a flag) |
| Rules Applied | Ordered list of Rule IDs consulted |
| Tree Ref      | Corresponding decision tree file |
| Validations   | Validation checks run after the decision |

**One decision = one file.** Location: `decision_trees/D-XXX-slug.json`

### 2.4 Validation

A **Validation** is a check that verifies consistency, completeness, or correctness of data or decisions.

| Property  | Description |
|-----------|-------------|
| ID        | Format: `V-XXX` |
| Title     | Short label |
| Type      | `consistency` | `completeness` | `compliance` | `cross-check` |
| Severity  | `critical` | `high` | `medium` | `low` |
| Condition | What is being checked |
| Failure   | What the failure means |
| Remediation | Suggested action on failure |
| Rule Refs | Rules that this validation enforces |

Location: `validation/V-XXX-slug.json`

### 2.5 Case

A **Case** is a complete, real or synthetic tax filing scenario used as ground truth.

| Property    | Description |
|-------------|-------------|
| ID          | Format: `C-XXXXXX` (six digits) |
| Title       | Short description of the scenario |
| AY          | Assessment Year |
| Profile     | Taxpayer profile summary |
| Inputs      | Evidence provided in this case |
| Decisions   | Decisions made and their outcomes |
| Rules Used  | Which rules were applied |
| Validations | Which validations ran and their results |
| Final Output| ITR form, regime, refund/payable |
| Explanation | Human-readable walkthrough |
| Source      | `real` | `synthetic` |
| Verified    | Boolean — has this been cross-checked |

Location: `cases/C-XXXXXX-slug/` (directory, one file per component)

### 2.6 Change

A **Change** is an immutable record of a modification to any object in the repository.

| Property    | Description |
|-------------|-------------|
| ID          | Format: `CH-XXXX` |
| Date        | ISO 8601 date |
| Author      | Who made the change |
| Type        | `add` | `modify` | `deprecate` | `supersede` | `fix` |
| Object Type | What kind of object changed |
| Object ID   | Which specific object changed |
| Summary     | What changed and why |
| Authority   | If triggered by law change: legal source |
| Prior Version | Previous version string |
| New Version   | New version string |

Location: `changes/CH-XXXX.json`

### 2.7 Version

A **Version** is a snapshot of the repository's rule set at a point in time, tied to an Assessment Year or a legal amendment.

| Property   | Description |
|------------|-------------|
| Tag        | Git tag, e.g. `v1.0.0-AY2025-26` |
| AY         | Assessment year covered |
| Date       | Release date |
| Summary    | What changed from prior version |
| Rule Count | Number of active rules |
| Change Refs| CH-IDs included in this version |

Versions are tracked via git tags and documented in `changes/CHANGELOG.md`.

---

## 3. Object Relationships

```
┌─────────────┐
│  Evidence   │  (E-XXX)
│  AIS, 26AS  │
│  Form 16    │
└──────┬──────┘
       │ feeds facts into
       ▼
┌─────────────┐       applies       ┌──────────────┐
│  Decision   │ ──────────────────► │    Rule      │
│  (D-XXX)    │                     │   (R-XXXX)   │
│  Which ITR? │◄── resolves ───────┘              │
│  Which      │                     ├─ cites ──────► Legal Authority
│  Regime?    │                     ├─ validated ──► Validation (V-XXX)
└──────┬──────┘                     ├─ proven ─────► Case (C-XXXXXX)
       │ produces                   └─ tracked ────► Change (CH-XXXX)
       ▼
┌─────────────┐
│ Explanation │
│ (narrative) │
└─────────────┘
```

### Dependency Rules

1. A Rule may not exist without citing a legal authority.
2. A Rule may not be marked `active` without at least one test case.
3. A Decision may not be marked `active` unless all its Rules are `active`.
4. A Validation must reference at least one Rule.
5. A Case must reference at least one Decision and one Rule.
6. Every modification to any object must produce a Change entry.

---

## 4. File Naming Conventions

| Object     | Pattern                        | Example |
|------------|--------------------------------|---------|
| Rule       | `R-XXXX-slug.json`             | `R-0001-itr1-ineligible-business-income.json` |
| Evidence   | `E-XXX-slug.json`              | `E-001-ais.json` |
| Decision   | `D-XXX-slug.json`              | `D-001-choose-itr-form.json` |
| Decision Tree | `DT-XXX-slug.yaml`          | `DT-001-itr-form-selection.yaml` |
| Validation | `V-XXX-slug.json`              | `V-001-tds-mismatch.json` |
| Case       | `C-XXXXXX-slug/`               | `C-000001-salary-gig-itr4/` |
| Change     | `CH-XXXX.json`                 | `CH-0001.json` |
| Schema     | `<object-type>-schema.json`    | `rule-schema.json` |
| Prompt     | `P-XXX-slug.md`                | `P-001-itr-form-selection.md` |

---

## 5. Versioning Policy

- All objects carry a `version` field in semver format (`MAJOR.MINOR.PATCH`).
- **PATCH**: Typo fix, clarification, no logic change.
- **MINOR**: Logic change within same legal authority (e.g. threshold updated).
- **MAJOR**: Legal authority changed, rule deprecated, or rule superseded.
- Every version increment must produce a Change entry.
- Repository-level versions are git tags in the form `vMAJOR.MINOR.PATCH-AYXXXX-XX`.

---

## 6. Legal Authority Citation Format

All rules must cite authority using this structure:

```json
{
  "act": "Income Tax Act, 1961",
  "section": "Section 44AD",
  "proviso": null,
  "notification": null,
  "circular": null,
  "finance_act": "Finance Act 2023",
  "effective_from": "2023-04-01",
  "url": null
}
```

At least `act` and `section` must be non-null for a rule to be `active`.

---

## 7. Assessment Year Scope

Every object that encodes a time-sensitive rule must declare which Assessment Year(s) it applies to. Use the format `AY2025-26`. If a rule applies across multiple years, list all applicable years.

Current repository target: **AY2025-26** (FY 2024-25).

---

## 8. Status Lifecycle

```
draft ──► active ──► deprecated
            │
            └──► superseded ──► (new rule is active)
```

- `draft`: Being authored. Not used in decisions.
- `active`: Validated, tested, and in production use.
- `deprecated`: No longer applies (law changed, provision removed).
- `superseded`: Replaced by another rule (with forward pointer to new rule ID).

---

## 9. Directory Purpose Map

| Directory        | Contains |
|------------------|----------|
| `/docs`          | Human-readable architecture docs, domain model, guides |
| `/data`          | Raw or processed tax data (AY-scoped subdirectories) |
| `/rules`         | One JSON file per rule |
| `/decision_trees`| Decision object files and YAML tree definitions |
| `/validation`    | Validation check files |
| `/knowledge_graph`| Entity definitions, ontology, relationship maps |
| `/cases`         | One directory per case |
| `/explanations`  | Reusable explanation templates |
| `/changes`       | One JSON file per change, plus CHANGELOG.md |
| `/tests`         | Test suites, one file per rule or decision |
| `/schemas`       | JSON Schema files for all object types |
| `/prompts`       | AI prompt templates that retrieve from this repository |

---

## 10. What the AI Layer Must Never Do

The AI (Jarviz) must:

- **Retrieve** rules from this repository, never invent them.
- **Cite** the rule ID and legal authority in every answer.
- **Report** uncertainty when evidence is missing, not assume defaults.
- **Escalate** to a human when validations fail or rules conflict.

The AI must never:

- Assert a tax position without a corresponding Rule ID.
- Skip the Evidence step and infer facts.
- Override a Validation failure without flagging it.
- Treat a deprecated or draft rule as active.

---

*Document Version: 1.0.0*
*Effective: 2026-06-26*
*Author: Vinayak Gautham*
