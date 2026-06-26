# Registry

The registry is the operating system of this repository. Every object that exists must have an entry here. If an object has no registry entry, it does not officially exist — it cannot be referenced by rules, decisions, or cases.

## Files

| File | Contains |
|------|----------|
| `rule-registry.json` | All Rule IDs, titles, status, AY, version |
| `decision-registry.json` | All Decision IDs and their bound questions |
| `evidence-registry.json` | All Evidence source IDs |
| `validation-registry.json` | All Validation IDs, severity, status |
| `case-registry.json` | All Case IDs, AY, source, verified flag |
| `section-registry.json` | All legal sections cited across rules |
| `version-registry.json` | All repository version snapshots |
| `index.json` | Master cross-reference table — object counts and health |

## How to maintain

Every time you add an object, update its registry file **in the same commit**. The CI check (when wired) will reject commits that add a rule file without a corresponding registry entry.

## Lookup patterns

- Find all rules that cite Section 44AD → `section-registry.json` → `rule_refs`
- Find all active rules for AY2025-26 → `rule-registry.json`, filter `status: active` and `assessment_years contains AY2025-26`
- Find which case uses Decision D-001 → `case-registry.json` → `decision_refs`
- Count total objects in repository → `index.json` → `counts`
