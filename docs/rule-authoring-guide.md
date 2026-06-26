# Rule Authoring Guide

> If you can follow this guide, you can write Rule 500 without asking anyone.
> This document is the single reference for anyone adding a rule to this repository.

---

## Before You Start

Answer these four questions. If you cannot answer all four, do not write the rule yet.

1. **What is the legal authority?** Which Act, which section, which Finance Act, what effective date?
2. **What evidence makes this rule checkable?** Which document (AIS, 26AS, Form 16) contains the data this rule needs?
3. **Which decision does this rule participate in?** Look up the Decision Catalogue (`docs/decision-catalogue.md`) and find the D-XXX this rule belongs to.
4. **What does the outcome look like?** What exact value, flag, or classification does this rule produce?

If any of these answers is "I don't know," resolve that first. A rule with an incomplete authority citation cannot become active.

---

## Step 1: Assign the Rule ID

Open `registry/rule-registry.json`. Find the highest existing Rule ID. The next rule is that number + 1, zero-padded to four digits.

```
Current highest: R-0005
Your rule ID: R-0006
```

Write this down. You will use it everywhere.

---

## Step 2: Choose the File Name

Format: `rules/R-XXXX-short-descriptive-slug.json`

The slug should:
- Be all lowercase with hyphens
- Describe what the rule does, not what it is
- Be ≤ 60 characters

**Good:** `R-0006-itr2-capital-gains-required.json`
**Bad:** `R-0006-rule-about-capital-gains-and-itr-form-two.json`

---

## Step 3: Write the Rule File

Copy this template. Fill in every field. Do not delete any field.

```json
{
  "id": "R-XXXX",
  "title": "Short, specific title (max 120 characters)",
  "description": "Plain-English statement of what the rule says. One or two sentences. A non-tax reader should understand this.",
  "logic": {
    "if": "Condition in plain English or pseudo-code. E.g. 'taxpayer.income.capital_gains > 0'",
    "then": "Outcome when condition is true. E.g. 'itr_form = ITR-2 (minimum)'",
    "else": "Outcome when condition is false. E.g. 'Capital gains disqualifier does not apply.'"
  },
  "authority": {
    "act": "Income Tax Act, 1961",
    "section": "Section XX",
    "proviso": null,
    "notification": null,
    "circular": null,
    "finance_act": "Finance Act YYYY or null",
    "effective_from": "YYYY-MM-DD",
    "url": null
  },
  "effective_date": "YYYY-MM-DD",
  "sunset_date": null,
  "assessment_years": ["AYXXXX-XX"],
  "version": "1.0.0",
  "status": "draft",
  "superseded_by": null,
  "tags": ["tag1", "tag2"],
  "evidence_refs": ["E-XXX"],
  "decision_refs": ["D-XXX"],
  "test_refs": ["T-XXXX"],
  "change_refs": ["CH-XXXX"],
  "notes": "Any edge cases, caveats, or cross-references a reader needs to understand this rule fully."
}
```

**Always start with `"status": "draft"`.** Never set `active` yourself — that happens after review.

---

## Step 4: Write the Logic Correctly

The `logic` block is the most important part. Common mistakes:

**Do not write ambiguous conditions:**

Bad: `"if": "taxpayer has capital gains"`

Good: `"if": "taxpayer.income.capital_gains_stcg > 0 OR taxpayer.income.capital_gains_ltcg > 0"`

**Cover the `else` case explicitly:**

Bad: `"else": null`

Good: `"else": "No capital gains — this rule does not apply. Continue to next rule."`

**Do not bundle two rules:**

Bad: `"if": "business income OR capital gains exist", "then": "ITR-1 invalid"`

This is two separate rules (business income → no ITR-1; capital gains → no ITR-1). Write them separately.

---

## Step 5: Cite the Authority Precisely

Every field in the `authority` block matters:

| Field | What to put | Example |
|-------|-------------|---------|
| `act` | Full formal name | `"Income Tax Act, 1961"` |
| `section` | Exact section number | `"Section 112A"` |
| `proviso` | First, second, etc. proviso | `"First Proviso to Section 112A"` or `null` |
| `notification` | CBDT notification number | `"Notification No. 60/2018"` or `null` |
| `circular` | CBDT circular number | `"Circular No. 4/2020"` or `null` |
| `finance_act` | Year only | `"Finance Act 2023"` or `null` |
| `effective_from` | Date the provision started | `"2018-04-01"` |

If you are unsure of any field, leave it `null` and note it in `notes`. A rule with `null` authority fields cannot be promoted past `draft`.

---

## Step 6: Write the Test Cases First

Do not wait until the rule is done to write tests. Write them now, while the logic is fresh.

### How many tests?

| Rule complexity | Minimum tests |
|-----------------|--------------|
| Simple flag check | 2 — one positive (condition true), one negative (condition false) |
| Threshold condition | 3 — below threshold, at threshold, above threshold |
| Multi-condition AND | 1 per combination that matters (usually 3–4) |
| Multi-condition OR | One test per branch |

### Test ID assignment

Open `tests/`. Find the highest T-XXXX. Assign the next sequential IDs.

### Test file format

`tests/T-XXXX-rule-rXXXX-scenario-slug.json`

Fill in the `input` with concrete values, not labels. `expected_output` must be deterministic — one right answer.

```json
{
  "id": "T-XXXX",
  "title": "One-line description of what scenario this tests",
  "target_type": "rule",
  "target_ref": "R-XXXX",
  "input": {
    "taxpayer.income.capital_gains_stcg": 50000,
    "taxpayer.income.capital_gains_ltcg": 0
  },
  "expected_output": {
    "itr1_valid": false,
    "minimum_itr_form": "ITR-2",
    "applicable_rule": "R-XXXX"
  },
  "actual_output": null,
  "status": "pending",
  "last_run": null,
  "assessment_year": "AY2025-26",
  "notes": ""
}
```

---

## Step 7: Link the Rule to the Decision

Open `docs/decision-catalogue.md`. Find the D-XXX this rule participates in. Add your rule ID to its `Rules Applied` list.

Also open `registry/decision-registry.json` and add your rule ID to the `rule_refs` array for that decision.

---

## Step 8: Update the Registries

**rule-registry.json:** Add a new entry for your rule following the existing format.

**index.json:** Increment `counts.rules.total` and `counts.rules.draft`.

If your rule cites a new legal section not already in `section-registry.json`, add a new entry there too and create its dependency graph file in `dependency_graph/SEC-XXX-*.json`.

---

## Step 9: Create a Change Entry

Every new rule gets a Change entry:

File: `changes/CH-XXXX.json`

```json
{
  "id": "CH-XXXX",
  "date": "YYYY-MM-DD",
  "author": "Your name",
  "type": "add",
  "object_type": "rule",
  "object_id": "R-XXXX",
  "summary": "Added rule R-XXXX: [title]. Reason: [why this rule was needed].",
  "authority": "Finance Act YYYY — Section XX",
  "prior_version": null,
  "new_version": "1.0.0",
  "git_commit": null,
  "notes": ""
}
```

Update `changes/CHANGELOG.md` with a one-line entry.

---

## Step 10: Commit

Use this commit message format:

```
[R-XXXX] Add rule: <title (≤ 60 chars)>
```

Commit all files together:
- `rules/R-XXXX-*.json`
- `tests/T-XXXX-*.json` (all new test files)
- `changes/CH-XXXX.json`
- `changes/CHANGELOG.md`
- `registry/rule-registry.json`
- `registry/index.json`
- `docs/decision-catalogue.md` (if rule_refs updated)
- `registry/decision-registry.json` (if rule_refs updated)
- `registry/section-registry.json` (if new section cited)
- `dependency_graph/SEC-XXX-*.json` (if new section added)

---

## Step 11: Request Review

Open a Pull Request. Include in the PR description:

```
Rule: R-XXXX
Title: [title]
Decision: [D-XXX]
Section: [Act, Section]
Tests: [T-XXXX list]

Peer Review Checklist: (copy from docs/rule-lifecycle.md)
```

The rule will not be promoted to `active` until peer review and legal review are complete.

---

## Common Mistakes

| Mistake | Consequence | Correct Approach |
|---------|-------------|-----------------|
| Setting `status: active` before review | Rule is retrieved by AI with unverified logic | Always start with `draft` |
| Bundling two conditions into one rule | Cannot test them independently | One atomic condition per file |
| Missing `else` in logic | Ambiguous — what happens when condition is false? | Always write the `else` |
| Vague condition like "has income" | Not machine-checkable | Use specific field names and operators |
| Not writing tests | Rule can never be promoted | Write tests before the rule is done |
| Not updating registry | Rule is undiscoverable | Registry is mandatory, same commit |
| Not creating a Change entry | No audit trail | CH-XXXX required for every new rule |

---

## Tags Taxonomy

Use only tags from this list. If you need a new tag, add it here first.

**By ITR form:** `itr1`, `itr2`, `itr3`, `itr4`

**By income head:** `salary`, `business-income`, `presumptive`, `capital-gains`, `house-property`, `other-sources`, `agricultural`

**By topic:** `eligibility`, `disqualifier`, `regime`, `tds`, `refund`, `deduction`, `audit`, `advance-tax`, `foreign-assets`, `carry-forward`

**By section:** `44ad`, `44ada`, `44ae`, `80c`, `80d`, `87a`, `115bac`, `112a`, `139`, `schedule-fa`

---

*Document Version: 1.0.0*
*Effective: 2026-06-26*
