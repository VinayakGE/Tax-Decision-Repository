# Engine 5 — Explanation Engine

> Sprint 1, Priority 5.
> Converts the decision trace into language a taxpayer can read and trust.
> This is the only stage where the AI is permitted to generate prose.

---

## Purpose

Produce a human-readable explanation for every decision made, every validation that failed, and the overall tax outcome. The explanation must be honest about uncertainty and traceable to specific rule IDs.

---

## Pipeline Stage

Stage 13 (Explanation Engine). Runs after Confidence Calculator.

---

## The AI Constraint

The AI in this engine operates in **retrieval + narration mode only**. It:

- Receives the structured Decision Trace from Stage 11
- Receives the Confidence Report from Stage 12
- Fills an explanation template using the trace
- Never introduces facts not present in the trace
- Never makes tax assertions beyond what the rules produced

The AI must not be given an open-ended prompt. It must be given a constrained template that forces it to narrate a pre-computed result, not reason about tax law.

---

## Contract

### Input

```json
{
  "decision_trace": {
    "pattern_matched": "PAT-002",
    "pattern_confidence": 88,
    "decisions": [
      {
        "decision_ref": "D-001",
        "outcome": "ITR-4",
        "rules_applied": [
          {
            "rule_id": "R-0001",
            "condition": "business_income > 0",
            "result": true,
            "outcome_text": "ITR-1 eliminated — business income exists"
          },
          {
            "rule_id": "R-0004",
            "condition": "presumptive_44AD AND total_income <= 50L AND no_disqualifiers",
            "result": true,
            "outcome_text": "ITR-4 eligible — presumptive income under Section 44AD"
          }
        ],
        "rules_skipped": [
          { "rule_id": "R-0003", "reason": "No foreign assets declared" }
        ]
      }
    ],
    "tax_computation": {
      "regime": "new",
      "taxable_income": 802200,
      "total_tax": 0,
      "refund": 30400
    },
    "validations": [],
    "confidence": { "band": "A", "score": 97 }
  }
}
```

### Output

```json
{
  "engine": "EXPLANATION",
  "sections": {
    "summary": "string",
    "itr_form_explanation": "string",
    "regime_explanation": "string",
    "income_breakdown": "string",
    "tax_computation": "string",
    "validation_summary": "string",
    "confidence_statement": "string",
    "what_to_do_next": "string"
  },
  "citations": ["R-0001", "R-0004", "R-0005"],
  "caveats": []
}
```

---

## Explanation Templates

### Summary Template

```
We have reviewed your documents and determined the following for AY2025-26:

• ITR Form:    {recommended_form}
• Tax Regime:  {regime} Regime
• Tax Outcome: {outcome_statement}
• Confidence:  {confidence_band} — {confidence_explanation}

{blocking_alert_if_any}
```

### ITR Form Template

```
We recommend ITR-{form} for the following reasons:

{for each rule_applied in itr_decision.rules_applied:}
  • {rule_id}: {outcome_text} (Authority: {legal_citation})

{if rules_skipped:}
The following conditions were checked and did not apply:
{for each rule_skipped:}
  • {rule_id}: {reason}

{if alternatives:}
Alternative: {alternative_form} would be required if {alternative_condition}.
```

### Regime Template

```
We compared your tax under both regimes:

New Regime:
  Gross Income:         ₹{gti}
  Less: Standard Deduction: ₹{std_deduction}
  Less: NPS Employer (80CCD(2)): ₹{nps_employer}
  Taxable Income:       ₹{new_taxable}
  Tax:                  ₹{new_tax}

Old Regime:
  Gross Income:         ₹{gti}
  Less: All deductions: ₹{old_deductions}
  Taxable Income:       ₹{old_taxable}
  Tax:                  ₹{old_tax}

Recommendation: {regime} Regime saves you ₹{saving}.

Note: {regime_caveat_if_any}
(Authority: Section 115BAC — Rule R-0005)
```

### Validation Template

```
{if no_failures:}
All checks passed. No issues found with your documents or return.

{if failures:}
⚠ {count} issue(s) found that must be resolved before filing:

{for each failure ordered by severity:}
  [{severity}] {validation_title}
  What we found: {details}
  What to do:   {remediation}
  Rule: {validation_ref}
```

### Confidence Template

```
Confidence in this analysis: {band} ({score}/100)

{band == A:}
All required documents were provided and verified. The analysis is based on
complete, cross-checked information.

{band == B:}
Most required information was available. The following fields were provided
but not independently verified: {unverified_fields}. We recommend confirming
these before filing.

{band == C:}
Some information was missing. We asked {question_count} questions to fill
the gaps. The fields provided by you (not from documents) are:
{user_answered_fields}. Verify these against your actual documents.

{band == D or E:}
Important information is missing. This analysis should be treated as
preliminary only. Complete your documents and re-run the analysis.
```

---

## Tone and Style Rules

These are enforced constraints, not suggestions:

1. **No tax jargon without definition.** If "LTCG" appears, it must be followed by "(Long-Term Capital Gains)" on first use.
2. **Every claim cites a source.** "We recommend ITR-4 (Rule R-0004, Section 44AD)" — not just "We recommend ITR-4."
3. **Numbers in rupees.** Always show amounts with ₹ symbol and comma formatting (₹30,400 not 30400).
4. **No hedging without reason.** "This may be..." is only acceptable if the confidence band is C or below.
5. **Active voice.** "We found..." not "It was found..."
6. **No unexplained abbreviations.** First use: "Annual Information Statement (AIS)". Subsequent: "AIS".
7. **Uncertainty is explicit.** If a field was user-declared (not from a document), say so.

---

## AI Prompt Template (Sprint 1)

The explanation engine calls the AI with this constrained prompt:

```
You are Jarviz, a tax filing assistant. You must narrate the following
pre-computed tax analysis as a clear, factual explanation for a taxpayer
who is not a tax expert.

STRICT RULES:
- Only describe what is in the DECISION TRACE below. Do not add facts.
- Cite every rule ID and section reference exactly as provided.
- Do not speculate about outcomes not in the trace.
- Format amounts as ₹X,XX,XXX (Indian rupee format with commas).
- If confidence band is C or below, begin the explanation with a caveat.

DECISION TRACE:
{decision_trace_json}

Generate the explanation by filling in the following template:
{template_name}
```

---

## Test Requirements

| # | Scenario | Pass Criteria |
|---|----------|--------------|
| 1 | ITR-4 recommended with two rules fired | Explanation names both rules with R-IDs |
| 2 | New Regime recommended | Shows both regime computations in numbers |
| 3 | Critical validation failure | Explanation leads with blocking alert |
| 4 | Confidence band B | Mentions unverified fields explicitly |
| 5 | Missing income in AIS | Explanation includes V-002 remediation steps |
| 6 | "LTCG" appears in explanation | First use includes "(Long-Term Capital Gains)" |
| 7 | Any rupee amount | Formatted with ₹ and Indian comma format |

---

## JAB Metrics for This Engine

- **Citation completeness**: Decisions explained with at least one cited Rule ID → Target: 100%
- **Jargon compliance**: Technical terms defined on first use → Target: 100%
- **Hallucination rate**: Explanation assertions not traceable to the Decision Trace → Target: 0%
- **Human readability score**: Flesch-Kincaid grade level → Target: Grade 8 or below
