# Benchmarks

This directory contains the Jarviz Accuracy Benchmark (JAB) infrastructure.

## Structure

```
benchmarks/
  gss/          Gold Standard Set — cases with verified ground truth
  reports/      JAB reports, one per release (JAB-v1.3.0.json, etc.)
  README.md     This file
```

## Running the Benchmark

1. Place GSS cases in `benchmarks/gss/` using the case schema with a `ground_truth` block.
2. Run the pipeline against each GSS case.
3. Compare pipeline output against `ground_truth` for each of the 9 JAB metrics.
4. Write results to `benchmarks/reports/JAB-vX.Y.Z.json` conforming to `schemas/benchmark-schema.json`.

## Adding Cases to the GSS

See `docs/benchmark-jab.md` → "Authoring New GSS Cases" for the full procedure.

Minimum: one CA sign-off per case before adding to the GSS.

## Release Gate

A release is APPROVED only when all blocking JAB metrics pass. See `docs/benchmark-jab.md` for the full release gate rules.
