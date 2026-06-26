# Jarviz Processing Pipeline

> This document is the runtime architecture.
> The repositories are knowledge sources. The pipeline is how knowledge becomes a decision.
> Every tax return processed by Jarviz passes through these stages in order, without exception.

---

## The Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│  INPUT: Taxpayer uploads documents                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 1 — Document Parser                                      │
│  Identifies document type and extracts raw structured content   │
│  Knowledge source: Evidence Registry (E-001 to E-007)           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 2 — Evidence Extractor                                   │
│  Pulls specific fields from parsed documents                    │
│  Knowledge source: Evidence Catalogue (docs/evidence-catalogue) │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 3 — Evidence Normalizer                                  │
│  Standardises units, formats, field names across sources        │
│  Knowledge source: Domain Model (docs/domain-model)             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 4 — Pattern Matcher                                      │
│  Matches normalised evidence against pattern registry           │
│  Knowledge source: Pattern Repository (/patterns)               │
│  Output: Matched pattern + pattern confidence score             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 5 — Intake Engine                                        │
│  Asks the minimum questions to fill evidence gaps               │
│  Knowledge source: Pattern intake_questions; Confidence Model   │
│  Output: Completed evidence object; user answers logged         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 6 — Evidence Completeness Check                          │
│  Computes Evidence Completeness Score (ECS) per decision        │
│  Knowledge source: Confidence Model (docs/confidence-model)     │
│  Output: Confidence band per decision; missing field list       │
│  ⚠ If Band E on any required decision → halt, notify user      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 7 — Conflict Resolver                                    │
│  Resolves evidence conflicts before decisions are run           │
│  Knowledge source: Conflict Resolver (docs/conflict-resolver)   │
│  Output: Resolved evidence object; conflict log                 │
│  ⚠ Unresolved conflicts block affected decisions               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 8 — Decision Engine                  [ENGINE 1, 2]       │
│  Runs applicable decisions in order per matched pattern         │
│  Knowledge source: Rule Repository; Decision Catalogue          │
│  Output: Decision outcomes with rule trace; per-rule results    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 9 — Tax Calculator                   [ENGINE 3]          │
│  Pure deterministic computation. No AI. No ambiguity.           │
│  Knowledge source: Tax slabs, surcharge tables (AY-versioned)   │
│  Output: Gross tax, rebate, cess, total liability, refund/due   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 10 — Validation Engine               [ENGINE 4]          │
│  Runs all applicable validations against decisions + evidence   │
│  Knowledge source: Validation Repository (/validation)          │
│  Output: Pass/fail per validation; severity-ranked failure list │
│  ⚠ Critical failures block Final Report                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 11 — Decision Trace Generator                            │
│  Builds the complete audit trail of what happened and why       │
│  Knowledge source: All prior stage outputs                      │
│  Output: Ordered list of rules evaluated, outcomes, citations   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 12 — Confidence Calculator                               │
│  Computes final confidence score across all decisions           │
│  Knowledge source: Confidence Model; conflict log               │
│  Output: Per-decision confidence band; overall session score    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 13 — Explanation Engine              [ENGINE 5]          │
│  Generates human-readable narrative from the decision trace     │
│  Knowledge source: Explanation templates; Prompt Repository     │
│  Output: Taxpayer-facing explanation per decision               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 14 — Decision Replay Writer                              │
│  Persists the complete session to the replay store              │
│  Knowledge source: All prior stage outputs                      │
│  Output: Replay record (schema: schemas/replay-schema.json)     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  OUTPUT: Final Report                                           │
│  ITR form | Regime | Tax/Refund | Validations | Confidence      │
│  Evidence summary | Decision trace | Explanations               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Stage Specifications

### Stage 1 — Document Parser

**Purpose:** Receive uploaded files and identify what each document is.

**Input:** One or more uploaded files (PDF, JSON, Excel, image)

**Process:**
1. Detect file format
2. Match against known document signatures (AIS JSON structure, 26AS layout, Form 16 TRACES format)
3. Extract raw content (structured fields for JSON; OCR-parsed text for PDF)
4. Assign evidence ID (E-001 through E-007) to each document

**Output:**
```json
{
  "parsed_documents": [
    {
      "evidence_ref": "E-004",
      "filename": "Form16_FY2024-25.pdf",
      "parse_status": "success",
      "raw_fields": { ... }
    }
  ]
}
```

**Failure modes:**
- Unrecognised document → flag for manual identification
- Corrupted file → reject with error
- Password-protected PDF → request password or alternative format

---

### Stage 2 — Evidence Extractor

**Purpose:** Pull specific named fields from each parsed document, according to the field definitions in the Evidence Catalogue.

**Input:** Parsed document objects from Stage 1

**Process:**
For each document, extract only the fields defined in `docs/evidence-catalogue.md` for that evidence type. No interpretation at this stage — extraction only.

**Output:**
```json
{
  "extracted_evidence": {
    "E-004": {
      "gross_salary": 840000,
      "employer_tds": 28600,
      "employer_tan": "BNGE12345A",
      "standard_deduction": 75000,
      "net_salary": 765000
    }
  }
}
```

---

### Stage 3 — Evidence Normalizer

**Purpose:** Standardize all extracted values to canonical field names, units, and types from the Domain Model.

**Input:** Extracted evidence from Stage 2

**Process:**
- Map evidence field names to canonical entity fields (e.g. Form 16's "Gross Salary" → `taxpayer.income.salary`)
- Convert all amounts to rupees (integer, no decimal)
- Normalize dates to ISO 8601
- Resolve boolean flags (Yes/No strings → true/false)
- Merge fields from multiple sources into a single evidence object

**Output:** A single `EvidenceObject` conforming to the Domain Model entity schema, with source annotations on every field.

---

### Stage 4 — Pattern Matcher

**Purpose:** Match the normalised evidence fingerprint against the Pattern Repository to identify the most likely taxpayer profile.

**Input:** Normalised EvidenceObject from Stage 3

**Process:**
1. Build document fingerprint: set of evidence_refs present
2. Iterate pattern registry in prevalence order (PAT-001 first)
3. Score each pattern against fingerprint and available field values
4. Select best-matching pattern; compute pattern confidence score
5. If pattern confidence < 70%: no pattern selected, proceed without narrowing

**Output:**
```json
{
  "matched_pattern": "PAT-002",
  "pattern_confidence": 88,
  "pattern_title": "Salary + Gig / Freelance Income",
  "alternative_patterns": ["PAT-001"],
  "fallback_to_full_tree": false
}
```

---

### Stage 5 — Intake Engine

**Purpose:** Ask the minimum questions from the matched pattern's `intake_questions` to resolve missing required fields before decisions are evaluated.

**Input:** Matched pattern + normalised EvidenceObject

**Process:**
1. Identify which required fields are still `null` or `MR` (missing required)
2. Filter pattern's `intake_questions` to only those that populate missing fields
3. Apply `conditional_on` logic — skip questions made irrelevant by prior answers
4. Present questions to user; record answers
5. Merge answers back into EvidenceObject

**Design constraint:** Never ask more than 7 questions per session before reaching Stage 6. If more than 7 fields are missing, run Stage 6 first and halt on Band E decisions rather than continuing to ask.

---

### Stage 6 — Evidence Completeness Check

**Purpose:** Compute the Evidence Completeness Score for each decision that needs to be made, and assign a confidence band.

**Input:** Completed EvidenceObject from Stage 5

**Process:** Per decision in the pattern's `applicable_decisions`, apply the Confidence Model formula:
```
ECS = (present_required_fields / total_required_fields) × 100
CS  = ECS × evidence_quality_weight
```

**Output:** Confidence band (A–E) per decision. Band E on a required decision halts the pipeline for that decision.

---

### Stage 7 — Conflict Resolver

**Purpose:** Detect and resolve conflicts between evidence sources before decisions are evaluated.

**Input:** EvidenceObject with multi-source fields

**Process:** For each field that has values from more than one source, apply the Conflict Resolver rules from `docs/conflict-resolver.md`.

**Output:** Conflict-resolved EvidenceObject + conflict log.

---

### Stage 8 — Decision Engine

**Purpose:** Evaluate all applicable decisions in order, applying rules from the Rule Repository.

**Engines used:** Engine 1 (ITR Selection), Engine 2 (Income Classification)

**Input:** Conflict-resolved EvidenceObject + applicable decision list

**Process:**
1. For each decision in order, traverse its decision tree
2. At each node, evaluate the condition against the EvidenceObject
3. Follow the branch; log which rule produced the outcome
4. Continue until a leaf node (outcome) is reached

**Output:** Decision outcomes with full rule trace.

---

### Stage 9 — Tax Calculator

**Purpose:** Deterministic computation of tax liability, rebate, surcharge, cess, TDS credit, and refund or balance due.

**Engine used:** Engine 3

**Input:** Income classification (from Stage 8) + resolved TDS credit

**Process:** Pure arithmetic. No AI. No ambiguity. All slab rates, surcharge rates, and rebate limits are versioned by AY in `/data/AY-XXXX-XX/tax-tables.json`.

**Output:**
```json
{
  "taxable_income": 802200,
  "gross_tax": 30220,
  "rebate_87A": 30220,
  "tax_after_rebate": 0,
  "surcharge": 0,
  "cess": 0,
  "total_tax_liability": 0,
  "tds_credit": 30400,
  "advance_tax_paid": 0,
  "refund": 30400,
  "tax_due": 0
}
```

---

### Stage 10 — Validation Engine

**Purpose:** Run all applicable validations and produce a severity-ranked list of issues.

**Engine used:** Engine 4

**Input:** All prior stage outputs (decisions, tax computation, conflict log)

**Process:**
1. Identify applicable validations from the pattern's `common_validations` + any triggered by decision outcomes
2. Evaluate each validation condition against the evidence and decisions
3. Rank failures by severity (critical → high → medium → low)
4. Critical failures block the Final Report; others are advisory

**Output:** Validation results with pass/fail per validation and a prioritised remediation list.

---

### Stage 11 — Decision Trace Generator

**Purpose:** Build the complete, citable audit trail that shows exactly how every decision was reached.

**Input:** All prior stage outputs

**Process:** Assemble the trace in order:
- Pattern matched + confidence
- Evidence fields used
- Rules evaluated (with condition text, outcome, rule ID, legal citation)
- Rules skipped (with reason)
- Conflicts detected and resolved
- Validations run

**Output:** Decision Trace object (basis for both the Explanation Engine and the Decision Replay record).

---

### Stage 12 — Confidence Calculator

**Purpose:** Compute the final, overall confidence score for the complete session.

**Input:** Per-decision confidence bands + conflict log + validation results

**Process:**
- Start with the lowest confidence band across all decisions
- Downgrade further for each unresolved conflict
- Downgrade further for each critical validation failure
- Never report Band A if any validation failed at medium or above

**Output:** Final confidence band + score + plain-English explanation of confidence drivers.

---

### Stage 13 — Explanation Engine

**Purpose:** Convert the Decision Trace into taxpayer-readable language.

**Engine used:** Engine 5

**Input:** Decision Trace from Stage 11 + final confidence from Stage 12

**Process:**
Use explanation templates from `/explanations/` and prompt templates from `/prompts/` to generate:
- One paragraph per decision (why this outcome was reached)
- One sentence per rule applied (what the rule says, in plain English)
- One section for validations (what was checked, what needs attention)

**Constraint:** Every generated sentence must be traceable back to a specific Rule ID or Decision ID. No unreferenced assertions.

---

### Stage 14 — Decision Replay Writer

**Purpose:** Persist the complete session record for future analysis, benchmark, and rule improvement.

**Input:** All stage outputs

**Process:** Serialize to a Replay record (schema: `schemas/replay-schema.json`). Write to `replays/AY2025-26/`. The replay is immutable once written.

---

## Pipeline Invariants

These must hold for every processed return, without exception:

1. **Immutable order.** Stages execute in sequence 1–14. No stage may be skipped.
2. **No AI in Stages 1–12.** Document parsing, evidence extraction, pattern matching, decisions, tax computation, and validation are deterministic. The AI is only permitted in Stage 13 (Explanation) and then only with a constrained prompt.
3. **Every decision cites a rule.** No outcome leaves Stage 8 without a Rule ID.
4. **Every conflict is logged.** No evidence conflict is silently resolved.
5. **Critical validation blocks output.** A critical failure from Stage 10 must be resolved before Stage 14 output is delivered to the taxpayer.
6. **Replay is always written.** Even if the pipeline halts mid-way, the partial replay record is written. Incomplete sessions are recoverable.

---

## Repository → Pipeline Mapping

| Stage | Repository / Knowledge Source |
|-------|-------------------------------|
| 1. Document Parser | `registry/evidence-registry.json` |
| 2. Evidence Extractor | `docs/evidence-catalogue.md` |
| 3. Evidence Normalizer | `docs/domain-model.md` |
| 4. Pattern Matcher | `/patterns/`, `registry/pattern-registry.json` |
| 5. Intake Engine | `patterns/*.json` → `intake_questions` |
| 6. Completeness Check | `docs/confidence-model.md` |
| 7. Conflict Resolver | `docs/conflict-resolver.md` |
| 8. Decision Engine | `/rules/`, `/decision_trees/`, `registry/rule-registry.json` |
| 9. Tax Calculator | `/data/AY-XXXX-XX/tax-tables.json` (Sprint 1 deliverable) |
| 10. Validation Engine | `/validation/`, `registry/validation-registry.json` |
| 11. Trace Generator | Aggregates all prior outputs |
| 12. Confidence Calculator | `docs/confidence-model.md` |
| 13. Explanation Engine | `/explanations/`, `/prompts/` |
| 14. Replay Writer | `schemas/replay-schema.json`, `/replays/` |

---

*Document Version: 1.0.0*
*Effective: 2026-06-26*
