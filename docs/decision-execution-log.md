# Decision Execution Log (DEL)

> One immutable log per pipeline execution.
> The DEL answers: exactly what happened, in what order, for how long.

---

## Purpose

The Decision Execution Log is the operational record of a single Jarviz pipeline run. It is created by Stage 14 (Replay Writer) and written atomically at the end of every successful or failed execution.

The DEL records the *mechanics* of the run: which stages executed, in what sequence, what they produced, and how long each stage took. It is not a decision audit (that is the Replay record). It is an execution audit.

The DEL is invaluable for:

- **Debugging**: "Why did Stage 7 take 3 seconds?" is answered in the DEL.
- **Customer support**: "What happened when this user ran on March 15?" is answered in the DEL.
- **Regression testing**: Replaying an execution requires knowing exactly which pipeline version and rules were active.
- **Operational metrics**: Average stage timing, error rates, and rule invocation frequency are derived from DELs.

---

## Structure

Every DEL contains:

| Section | Contents |
|---------|---------|
| Header | Execution ID, timestamps, pipeline version, environment |
| Evidence Summary | Which evidence was loaded and parsed |
| Stage Log | One entry per stage with inputs, outputs, timing, and status |
| Rules Invoked | All rules evaluated with their results |
| Error Log | Any exceptions, warnings, or anomalies encountered |
| Operational Metrics | Derived timing and frequency statistics |

---

## Execution ID

Every DEL is identified by a globally unique Execution ID:

```
DEL-{YYYY}-{7-digit-sequence}
```

Examples: `DEL-2026-0000001`, `DEL-2026-0000002`

The sequence resets each calendar year. The year prefix ensures IDs from different years do not collide. Both the DEL and the Replay record for the same run share this ID.

---

## DEL Format

```json
{
  "execution_id": "DEL-2026-0000001",
  "assessment_year": "AY2025-26",
  "pipeline_version": "1.3.0",
  "rule_set_version": "1.3.0",
  "started_at": "2026-03-15T10:01:22.000Z",
  "finished_at": "2026-03-15T10:01:26.200Z",
  "total_duration_ms": 4200,
  "status": "completed",

  "evidence_summary": {
    "documents_uploaded": 4,
    "documents_parsed": 4,
    "documents_failed": 0,
    "evidence_refs_loaded": ["E-001", "E-002", "E-003", "E-004"],
    "total_fields_extracted": 50
  },

  "stage_log": [
    {
      "stage": 1,
      "name": "Document Parser",
      "started_at": "2026-03-15T10:01:22.000Z",
      "finished_at": "2026-03-15T10:01:22.210Z",
      "duration_ms": 210,
      "status": "success",
      "input_summary": { "documents": 4 },
      "output_summary": { "parsed_documents": 4, "failed": 0 },
      "warnings": []
    },
    {
      "stage": 2,
      "name": "Evidence Extractor",
      "started_at": "2026-03-15T10:01:22.210Z",
      "finished_at": "2026-03-15T10:01:22.390Z",
      "duration_ms": 180,
      "status": "success",
      "input_summary": { "parsed_documents": 4 },
      "output_summary": { "fields_extracted": 50, "evidence_object_created": true },
      "warnings": []
    },
    {
      "stage": 3,
      "name": "Evidence Normalizer",
      "started_at": "2026-03-15T10:01:22.390Z",
      "finished_at": "2026-03-15T10:01:22.480Z",
      "duration_ms": 90,
      "status": "success",
      "input_summary": { "raw_fields": 50 },
      "output_summary": { "normalized_fields": 50, "type_coercions": 3 },
      "warnings": []
    },
    {
      "stage": 4,
      "name": "Pattern Matcher",
      "started_at": "2026-03-15T10:01:22.480Z",
      "finished_at": "2026-03-15T10:01:22.600Z",
      "duration_ms": 120,
      "status": "success",
      "input_summary": { "evidence_fields": 50 },
      "output_summary": { "suggested_pattern": "PAT-002", "pattern_confidence": 93 },
      "warnings": []
    },
    {
      "stage": 5,
      "name": "Intake Engine",
      "started_at": "2026-03-15T10:01:22.600Z",
      "finished_at": "2026-03-15T10:01:24.700Z",
      "duration_ms": 2100,
      "status": "success",
      "input_summary": { "suggested_pattern": "PAT-002" },
      "output_summary": {
        "pattern_confirmed": "PAT-002",
        "questions_asked": 3,
        "user_answers_collected": 3
      },
      "warnings": []
    },
    {
      "stage": 6,
      "name": "Completeness Check",
      "started_at": "2026-03-15T10:01:24.700Z",
      "finished_at": "2026-03-15T10:01:24.715Z",
      "duration_ms": 15,
      "status": "success",
      "input_summary": { "evidence_fields": 53 },
      "output_summary": {
        "ecs": 91,
        "confidence_band": "A",
        "halted": false,
        "missing_fields": 0
      },
      "warnings": []
    },
    {
      "stage": 7,
      "name": "Conflict Resolver",
      "started_at": "2026-03-15T10:01:24.715Z",
      "finished_at": "2026-03-15T10:01:24.725Z",
      "duration_ms": 10,
      "status": "success",
      "input_summary": { "fields_to_cross_check": 8 },
      "output_summary": { "conflicts_found": 0, "conflicts_resolved": 0 },
      "warnings": []
    },
    {
      "stage": 8,
      "name": "Decision Engine",
      "started_at": "2026-03-15T10:01:24.725Z",
      "finished_at": "2026-03-15T10:01:24.955Z",
      "duration_ms": 230,
      "status": "success",
      "input_summary": { "decisions_to_make": 2 },
      "output_summary": {
        "decisions_completed": 2,
        "itr_form": "ITR-4",
        "income_classified": true
      },
      "warnings": []
    },
    {
      "stage": 9,
      "name": "Tax Calculator",
      "started_at": "2026-03-15T10:01:24.955Z",
      "finished_at": "2026-03-15T10:01:25.040Z",
      "duration_ms": 85,
      "status": "success",
      "input_summary": { "regime": "new", "taxable_income": 802200 },
      "output_summary": {
        "total_tax": 0,
        "refund": 30400,
        "both_regimes_computed": true
      },
      "warnings": []
    },
    {
      "stage": 10,
      "name": "Validation Engine",
      "started_at": "2026-03-15T10:01:25.040Z",
      "finished_at": "2026-03-15T10:01:25.180Z",
      "duration_ms": 140,
      "status": "success",
      "input_summary": { "validations_selected": 4 },
      "output_summary": {
        "passed": 2,
        "failed": 2,
        "critical_failures": 1,
        "blocked": true
      },
      "warnings": []
    },
    {
      "stage": 11,
      "name": "Trace Generator",
      "started_at": "2026-03-15T10:01:25.180Z",
      "finished_at": "2026-03-15T10:01:25.240Z",
      "duration_ms": 60,
      "status": "success",
      "input_summary": {},
      "output_summary": { "trace_generated": true, "decisions_in_trace": 2 },
      "warnings": []
    },
    {
      "stage": 12,
      "name": "Confidence Calculator",
      "started_at": "2026-03-15T10:01:25.240Z",
      "finished_at": "2026-03-15T10:01:25.280Z",
      "duration_ms": 40,
      "status": "success",
      "input_summary": { "ecs": 91 },
      "output_summary": { "confidence_band": "A", "confidence_score": 97 },
      "warnings": []
    },
    {
      "stage": 13,
      "name": "Explanation Engine",
      "started_at": "2026-03-15T10:01:25.280Z",
      "finished_at": "2026-03-15T10:01:26.160Z",
      "duration_ms": 880,
      "status": "success",
      "input_summary": { "decision_trace_size_bytes": 2840 },
      "output_summary": {
        "sections_generated": 8,
        "citations_included": 3,
        "caveats": 0
      },
      "warnings": []
    },
    {
      "stage": 14,
      "name": "Replay Writer",
      "started_at": "2026-03-15T10:01:26.160Z",
      "finished_at": "2026-03-15T10:01:26.200Z",
      "duration_ms": 40,
      "status": "success",
      "input_summary": {},
      "output_summary": { "replay_written": true, "del_written": true },
      "warnings": []
    }
  ],

  "rules_invoked": [
    { "rule_id": "R-0001", "version": "1.0.0", "evaluated": true, "result": true, "duration_ms": 2 },
    { "rule_id": "R-0003", "version": "1.0.0", "evaluated": false, "result": null, "skip_reason": "has_foreign_assets == false" },
    { "rule_id": "R-0004", "version": "1.0.0", "evaluated": true, "result": true, "duration_ms": 3 },
    { "rule_id": "R-0005", "version": "1.0.0", "evaluated": true, "result": true, "duration_ms": 2 }
  ],

  "error_log": [],

  "operational_metrics": {
    "stages_completed": 14,
    "stages_failed": 0,
    "total_rules_evaluated": 3,
    "total_rules_skipped": 1,
    "questions_asked": 3,
    "user_wait_time_ms": 2100,
    "system_processing_time_ms": 2100,
    "ai_call_time_ms": 880
  }
}
```

---

## Status Values

| Value | Meaning |
|-------|---------|
| `completed` | All 14 stages completed successfully |
| `blocked` | Pipeline halted at Stage 6 (confidence band E) |
| `failed` | An unrecoverable error occurred in a stage |
| `partial` | Pipeline was interrupted (e.g., user abandoned session) |

---

## Immutability

DEL records are written once by Stage 14 and never modified. If a bug is found in how a stage logged its output, a `_correction` field may be appended by an operator, but the original fields are never edited.

This immutability makes DELs reliable as regression test inputs: given the same evidence and the same pipeline version, the same DEL must be reproducible.

---

## Operational Metrics Derived from DEL Corpus

Aggregating DEL records across many executions produces the operational health dashboard:

| Metric | Derived From |
|--------|-------------|
| Average end-to-end processing time | `total_duration_ms` across all DELs |
| P95 processing time | `total_duration_ms` at 95th percentile |
| Most frequently invoked rules | `rules_invoked[*].rule_id` frequency count |
| Average questions asked | `operational_metrics.questions_asked` mean |
| Stage error rate | `stage_log[*].status == "failed"` rate per stage |
| AI call time | `operational_metrics.ai_call_time_ms` mean and P95 |
| Conflict rate | DELs where `stage_log[6].output_summary.conflicts_found > 0` |
| Blocking validation rate | DELs where `stage_log[9].output_summary.blocked == true` |

These metrics feed directly into JAB M-07 (average questions) and M-08 (processing time).

---

## Storage Location

```
replays/
  DEL-2026-0000001.json    ← contains both DEL and replay in same file
  DEL-2026-0000002.json
```

The DEL and replay record for an execution are stored together in a single file. The `stage_log` and `rules_invoked` blocks constitute the DEL portion; the `decisions`, `validations_run`, and `post_filing_outcome` blocks constitute the replay portion.

The DEL schema (`schemas/del-schema.json`) validates the DEL-specific fields. The replay schema (`schemas/replay-schema.json`) validates the replay-specific fields. Both schemas are referenced in `schemas/replay-schema.json` via `$defs`.

---

## Schema

All DEL records conform to `schemas/replay-schema.json` (which includes the DEL fields as required blocks).
