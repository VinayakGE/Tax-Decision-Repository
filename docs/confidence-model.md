# Confidence Model

> The confidence model defines how certain the system is in a decision, given the evidence available.
> Confidence is computed by the repository — not left to the AI to estimate.
> The AI reports the confidence score and acts on it according to the thresholds defined here.

---

## Why Confidence Must Be Defined Here

An AI that guesses confidence is unreliable. If AIS is missing and the AI still says "ITR-4 is recommended," the taxpayer has no idea they're getting a low-confidence answer.

Confidence must be:
- **Computable** — derived from evidence presence and quality, not AI intuition
- **Explainable** — the system must say exactly why confidence is 61%, not just "medium"
- **Actionable** — each confidence band has a defined behavior (proceed / ask / escalate)

---

## Evidence Completeness Score (ECS)

For each decision, there is a defined set of evidence fields. The Evidence Completeness Score measures what fraction of required fields are present and verified.

```
ECS = (present_required_fields / total_required_fields) × 100
```

**Field states:**

| State | Code | Meaning |
|-------|------|---------|
| Present, verified | `PV` | Field is present and confirmed against a primary source |
| Present, unverified | `PU` | Field is present but not cross-checked |
| Missing, optional | `MO` | Field not present but not required for this decision |
| Missing, required | `MR` | Field not present but required for a complete decision |
| Disputed | `DS` | Field is present but values conflict between sources |

Only `PV` fields count as fully present. `PU` counts as 0.5. `MR` counts as 0. `DS` counts as 0 (triggers conflict resolution before confidence can be computed).

---

## Evidence Quality Weight (EQW)

Not all evidence sources are equally authoritative. The quality weight adjusts the raw ECS.

| Evidence Source | Quality Weight |
|-----------------|---------------|
| 26AS (TDS credit) | 1.0 |
| AIS (income data) | 0.95 |
| Form 16 Part A (TRACES) | 0.95 |
| Capital Gains Statement (Broker) | 0.90 |
| Form 16 Part B (Employer) | 0.80 |
| Prefill JSON | 0.75 |
| Form 16A | 0.90 |
| Bank Statement | 0.70 |
| Taxpayer Self-Declaration | 0.50 |

**Confidence Score (CS)** = ECS × EQW (of the primary evidence for this decision)

---

## Confidence Bands and System Behavior

| Band | Score Range | Label | System Behavior |
|------|-------------|-------|-----------------|
| A | 95–100 | High | Proceed. Report score and sources. No user prompt needed. |
| B | 80–94 | Sufficient | Proceed. Flag which fields are unverified. Recommend user verify. |
| C | 60–79 | Partial | Pause. Ask user for missing or unverified fields before deciding. |
| D | 40–59 | Low | Ask user. List every missing required field explicitly. Do not decide. |
| E | 0–39 | Insufficient | Halt. Inform user that a decision cannot be made with current evidence. Provide checklist of what is needed. |

---

## Decision-Specific Confidence Tables

### D-001 — Which ITR form must be filed?

| Required Field | Source | Weight | If Missing |
|----------------|--------|--------|-----------|
| Resident status | Prefill JSON / User | 0.75 | Band drops to C minimum |
| Business income flag | AIS | 0.95 | Band drops to D minimum |
| Capital gains flag | AIS / Broker Statement | 0.90 | Band drops to D minimum |
| Director flag | User declaration | 0.50 | Band drops to C minimum |
| Unlisted shares flag | User declaration | 0.50 | Band drops to C minimum |
| Foreign assets flag | AIS / User | 0.85 | Band drops to D minimum — never assume false |
| Total income | AIS + Prefill | 0.90 | Band drops to D minimum |

**Failure mode to guard against:** Defaulting to ITR-1 because flags are missing. When a disqualifying flag is missing, the system must ask — never assume `false`.

### D-002 — Which tax regime is optimal?

| Required Field | Source | Weight | If Missing |
|----------------|--------|--------|-----------|
| Gross salary | Form 16 / AIS | 0.95 | Band drops to C |
| 80C / 80D deductions | Form 16 Part B / User | 0.80 | Band B — can estimate based on typical patterns |
| HRA exemption | Form 16 Part B | 0.80 | Band B — ask if not present |
| 80CCD(2) employer NPS | Form 16 Part B | 0.80 | Assume 0 if missing (safe default) |

### D-003 — What is the correct TDS credit?

| Required Field | Source | Weight | If Missing |
|----------------|--------|--------|-----------|
| 26AS Part A | 26AS | 1.0 | Band E — cannot compute TDS credit without 26AS |
| Form 16 Part A | Form 16 | 0.95 | Band C — use 26AS only, flag discrepancy risk |

**26AS is never optional for TDS credit. If 26AS is missing, the system halts (Band E).**

---

## Confidence Report Format

Every decision output must include a confidence block:

```json
{
  "decision_id": "D-001",
  "outcome": "ITR-4",
  "confidence": {
    "score": 87,
    "band": "B",
    "label": "Sufficient",
    "evidence_completeness": 92,
    "evidence_quality_weight": 0.95,
    "missing_fields": [],
    "unverified_fields": ["director_flag"],
    "disputed_fields": [],
    "behavior": "Proceed. Recommend user confirm director status.",
    "explanation": "All income fields verified via AIS and Form 16. Director flag was self-declared (not verified against MCA records)."
  }
}
```

---

## What the AI Must Never Do

- Never omit the confidence block from a decision output.
- Never report Band A when any required field is in state `MR` or `DS`.
- Never assume a disqualifying flag is `false` when it is missing — ask.
- Never proceed past Band C without explicit user acknowledgment.
- Never inflate confidence to avoid asking the user a question.

---

*Document Version: 1.0.0*
*Effective: 2026-06-26*
