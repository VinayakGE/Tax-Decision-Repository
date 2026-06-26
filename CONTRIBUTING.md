# Contributing to the Jarviz Tax Decision Repository

Read ARCHITECTURE.md before contributing anything. Every object type, naming convention, and lifecycle rule is defined there.

---

## Core Principles

1. **One rule = one file.** Never bundle two rules into one JSON file.
2. **Every rule must cite legal authority.** `act` and `section` are mandatory. A rule without citation cannot be marked `active`.
3. **Every rule must have at least one test case** before its status can be set to `active`.
4. **Every modification creates a Change entry.** Add a `CH-XXXX.json` file in `/changes/` and update `CHANGELOG.md`.
5. **Evidence first, decision second, rule third.** Before writing a rule, verify the evidence source that makes it checkable.

---

## Adding a New Rule

1. Assign the next sequential `R-XXXX` ID (check the highest existing ID in `/rules/`).
2. Create the file: `rules/R-XXXX-short-slug.json`
3. Validate against `schemas/rule-schema.json`.
4. Create at least one test: `tests/T-XXXX-rule-rXXXX-description.json`
5. Add the rule ID to the relevant Decision in `/docs/decision-catalogue.md`.
6. Create a `CH-XXXX.json` change entry.
7. Update `CHANGELOG.md`.
8. Set `status: "draft"` until tests pass. Only then set `status: "active"`.

## Adding a New Decision

1. Assign the next `D-XXX` ID.
2. Document it in `docs/decision-catalogue.md`.
3. Create `decision_trees/DT-XXX-slug.yaml` for the tree.
4. Create `decision_trees/D-XXX-slug.json` as the Decision object.
5. Link all Rules it uses.

## Adding a New Case

1. Assign the next `C-XXXXXX` ID (six digits).
2. Create directory: `cases/C-XXXXXX-slug/`
3. Create `case.json` (validate against `schemas/case-schema.json`)
4. Create `explanation.md` with the step-by-step walkthrough
5. Set `verified: false` until cross-checked against actual return.

## Updating an Existing Rule

1. Increment the version:
   - Logic change within same authority → `MINOR`
   - Authority changed or rule superseded → `MAJOR`
   - Typo/clarification only → `PATCH`
2. If the rule is superseded: set `status: "superseded"`, add `superseded_by: "R-XXXX"` pointing to the new rule.
3. Create a `CH-XXXX.json` entry documenting what changed and why.

## Filing Year Scope

- All new rules must declare which `assessment_years` they apply to.
- Do not modify existing AY rules — create new versioned rules instead.
- Current target: **AY2025-26**

## What Not to Do

- Do not write a rule without a legal citation.
- Do not merge rules — one file per rule, always.
- Do not set `status: "active"` without a test case.
- Do not add tax data to `/data` without AY-scoping it (e.g. `data/AY2025-26/`).
- Do not edit AI prompt templates without updating their version.

---

## Schema Validation

All JSON files must validate against their respective schema in `/schemas/`.

Quick check (requires `ajv-cli`):
```bash
npx ajv validate -s schemas/rule-schema.json -d rules/R-XXXX-slug.json
```

---

## Commit Message Format

```
[R-XXXX] Add rule: <short title>
[D-XXX] Add decision: <short title>
[V-XXX] Add validation: <short title>
[C-XXXXXX] Add case: <short title>
[CH-XXXX] Change: <object-id> — <what changed>
[SCHEMA] Update: <schema name>
[DOCS] Update: <document name>
```
