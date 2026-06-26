# Replays

This directory stores Decision Replay and Decision Execution Log (DEL) records. Every pipeline execution writes one file here.

## File Naming

```
replays/DEL-{YYYY}-{7-digit-sequence}.json
```

Example: `replays/DEL-2026-0000001.json`

Each file contains both the DEL (execution mechanics) and the Replay (decision and outcome) for a single run. Both share the same execution ID.

## Schema

All files conform to `schemas/replay-schema.json`.

## Immutability

Replay records are never edited after creation. If a correction is needed, append to the `corrections` array. Do not modify existing fields.

## Post-Filing Outcomes

After a taxpayer files their return, update the `post_filing_outcome` block in the replay record. This data feeds JAB Metric M-09 (Human Override Rate) and the rule feedback loop.

## See Also

- `docs/decision-replay.md` — Replay system design and feedback loop
- `docs/decision-execution-log.md` — DEL structure and operational metrics
- `docs/benchmark-jab.md` — How replay data feeds JAB M-09
