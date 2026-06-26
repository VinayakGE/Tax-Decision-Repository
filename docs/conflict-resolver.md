# Conflict Resolver

> When two evidence sources report the same fact with different values, which one wins?
> This document formalizes the resolution framework. The AI does not make this judgment at runtime — it follows the rules defined here.

---

## Conflict Types

### Type 1: Amount Mismatch

Two sources agree a fact exists but report different numeric values.

**Example:** AIS shows salary ₹8,40,000. Form 16 shows salary ₹8,38,000.

### Type 2: Presence Mismatch

One source reports income that does not appear in another.

**Example:** AIS shows FD interest ₹18,000. Form 26AS shows TDS on FD but no interest amount.

### Type 3: Classification Mismatch

Two sources report the same transaction but classify it differently.

**Example:** AIS classifies a receipt as "dividend." Taxpayer's records classify it as "return of capital."

### Type 4: Missing Source

A required evidence source is entirely absent.

**Example:** 26AS not downloaded. Form 16 Part A not issued by employer.

---

## Resolution Hierarchy

Conflicts are resolved by strict source priority. The priority order was established in `docs/evidence-catalogue.md` and is reproduced here as an executable rule.

| Fact | Tier 1 (Wins) | Tier 2 (Deferred) | Tier 3 (Reference Only) |
|------|--------------|-------------------|------------------------|
| TDS credit | 26AS | Form 16 Part A | AIS summary |
| Salary income | Form 16 Part A | AIS | Prefill JSON |
| Interest income | AIS | Bank Statement | — |
| Dividend income | AIS | Dividend warrants | — |
| Capital gains | Broker / CAS statement | AIS | — |
| Property TDS | 26AS Part A1 | Form 26QB | — |
| Advance tax / SAT | 26AS Part C | Challan | — |
| Deductions claimed | Form 16 Part B | Taxpayer declaration | — |

---

## Resolution Rules by Conflict Type

### Type 1: Amount Mismatch

**Step 1 — Compute the delta:**

```
delta_pct = |source_A_amount - source_B_amount| / max(source_A_amount, source_B_amount) × 100
```

**Step 2 — Apply threshold:**

| Delta | Action |
|-------|--------|
| < 1% (rounding) | Auto-resolve: use Tier 1 source. Log resolution. |
| 1% – 5% | Flag as warning. Use Tier 1 source. Display both values to user. Recommend verification. |
| > 5% | Halt. Do not auto-resolve. Require user to provide source document and confirm correct value. |

**Step 3 — Log the resolution:**

Every auto-resolved conflict produces a conflict log entry (see schema below).

---

### Type 2: Presence Mismatch

**Rule:** Income that appears in AIS but not in the return is always treated as present until the taxpayer explicitly disputes it via AIS feedback.

**Steps:**
1. Identify the income in AIS.
2. Check if it appears in the return under any head.
3. If missing from return: trigger V-002 (AIS income not reported — critical validation).
4. Resolution path A: Taxpayer includes the income → resolved.
5. Resolution path B: Taxpayer disputes the AIS entry → requires AIS feedback submission on the IT Portal before this flag can be cleared.

**The system never silently ignores AIS income.**

---

### Type 3: Classification Mismatch

**Rule:** Classification disputes cannot be auto-resolved. They require a human judgment about the nature of the transaction.

**Steps:**
1. Flag the transaction with classification details from both sources.
2. Describe the tax consequence of each classification (e.g., "If dividend: taxable at slab rate. If return of capital: reduces cost basis, not currently taxable").
3. Halt and ask the taxpayer to confirm classification with reference to the underlying instrument or contract.
4. Log the taxpayer's declaration and the basis for it.

---

### Type 4: Missing Source

**Handled by the Confidence Model** (see `docs/confidence-model.md`). Missing required source → confidence band drops proportionally → system behavior is defined by the band.

For 26AS specifically: the system halts at Band E. No TDS credit can be computed or claimed without 26AS.

---

## Conflict Log Schema

Every resolved or escalated conflict produces a machine-readable log entry. These are stored alongside the case they arose from.

```json
{
  "conflict_id": "CONF-XXXXXX",
  "case_ref": "C-XXXXXX",
  "detected": "2026-06-26T00:00:00Z",
  "type": "amount_mismatch",
  "fact": "salary_income",
  "source_A": {
    "evidence_ref": "E-001",
    "name": "AIS",
    "value": 840000
  },
  "source_B": {
    "evidence_ref": "E-004",
    "name": "Form 16 Part A",
    "value": 838000
  },
  "delta_pct": 0.24,
  "resolution": "auto",
  "resolved_value": 840000,
  "resolved_source": "E-001",
  "resolution_rule": "delta < 1% — auto-resolved using Tier 1 source (AIS)",
  "user_notified": true,
  "user_confirmed": false,
  "escalated_to_human": false
}
```

---

## What the AI Must Never Do

- Never silently pick one value when sources conflict.
- Never resolve a > 5% amount mismatch automatically.
- Never auto-resolve a classification mismatch.
- Never claim TDS credit using a source other than 26AS without explicit user acknowledgment and flagging.
- Never clear a V-002 flag without confirmed AIS feedback from the taxpayer.
- Always log every conflict resolution — even auto-resolved ones.

---

## Relationship to Confidence Model

Unresolved conflicts (`DS` field state) reduce confidence:
- Any `DS` field blocks Band A.
- More than one `DS` field blocks Band B.
- Three or more `DS` fields trigger Band D (ask user before proceeding).

The confidence score cannot reach Band A if any conflict is unresolved.

---

*Document Version: 1.0.0*
*Effective: 2026-06-26*
