# Pattern Matching

> Patterns are not rules. They are course-grained profiles that Jarviz matches against before the rule engine runs.
> A matched pattern compresses the decision space, orders the intake questions, and surfaces the most likely validations.
> The rule engine then applies detailed rules within the narrowed space.

---

## Why Patterns Exist

Without patterns, Jarviz must ask every possible question to every taxpayer. With patterns, it asks five targeted questions to confirm the profile, then runs a focused subset of rules.

The difference in user experience:

**Without patterns:**
> "Do you have business income? Do you have capital gains? Do you have foreign assets? Are you a director? Do you hold unlisted shares? Do you have more than one house property? What is your resident status? Did you receive any lottery winnings?..."

**With patterns:**
> Jarviz sees Form 16 in the uploaded documents. Matches PAT-001 (Salaried, Single Employer). Asks: "Did you have any income other than salary and interest this year?" If no → runs D-001 with a narrow rule set. Three questions total.

---

## The Matching Process

### Step 1 — Document Fingerprint

Jarviz identifies which evidence documents have been provided. This is the first signal.

| Documents Present | Suggested Pattern |
|-------------------|-------------------|
| Form 16 only | PAT-001 (Salaried, Single Employer) |
| Form 16 + broker statement | PAT-003 (Salary + Capital Gains) |
| AIS showing business receipts + Form 16 | PAT-002 (Salary + Gig) |
| Multiple Form 16s | PAT-004 (Multiple Employers) |
| No Form 16, AIS shows professional receipts | PAT-008 (Professional Presumptive) |
| NR status flag or foreign remittance in AIS | PAT-005 (NRI) |

### Step 2 — Confirmation Questions

From the suggested pattern, Jarviz asks the minimum `intake_questions` needed to confirm. These are ordered: the most pattern-breaking question comes first.

The first question for any pattern involving ITR-1 or ITR-4 is always:
> "Did you have any income other than [pattern's income heads] this year?"

If yes → the current pattern may be wrong. Re-evaluate.

### Step 3 — Pattern Confirmation or Escalation

**If confirmed:** Run the pattern's `applicable_decisions` in order, applying only `applicable_rules`. High confidence starting point.

**If escalated:** Move to a higher-complexity pattern (specified in `edge_cases.upgrade_to_pattern`) or fall through to the full decision tree with no pattern context.

### Step 4 — Pattern Confidence Score

Pattern matching has its own confidence score, separate from the decision confidence:

| Match State | Pattern Confidence |
|-------------|-------------------|
| Document fingerprint matches + all confirmation questions answered affirmatively | 95% |
| Document fingerprint matches + 1 ambiguous answer | 70% |
| Document fingerprint partial + confirmation answers mixed | 50% |
| No document fingerprint match | 0% — no pattern, run full decision tree |

A pattern confidence below 70% means: do not constrain the rule set to the pattern's `applicable_rules`. Run the full decision tree.

### Step 5 — Rule Engine

The rule engine runs within the narrowed context. Even with a confirmed pattern, the rule engine still evaluates every applicable rule — it just does so with a pre-populated set of field values from the intake questions.

**Patterns never override rules.** If the rule engine reaches a different conclusion than the pattern's `expected_outcome`, the rule engine wins.

---

## Pattern vs Rule — The Distinction

| | Pattern | Rule |
|-|---------|------|
| Purpose | Match and narrow | Decide |
| Legal citation required | No | Yes |
| Needs test cases | Yes (intake scenarios) | Yes (logic verification) |
| AI can use directly | Yes (for matching) | Yes (for decisions) |
| Can be wrong | Yes (upgrades to better pattern) | Must not be wrong |
| Changes frequently | Yes (new evidence patterns) | Only when law changes |

---

## When to Add a New Pattern

Add a new pattern when:
1. You encounter a taxpayer profile that appears repeatedly in the case library
2. The profile has a distinct document signature (different combination of evidence)
3. The profile's intake questions differ meaningfully from existing patterns
4. The profile reaches a predictably different outcome from similar patterns

Do **not** add a new pattern for every income combination. Patterns are for the recurring 80% — edge cases fall through to the full decision tree.

---

## Pattern Upgrade Map

```
PAT-001 (Salaried, Single Employer)
  │
  ├── has capital gains?  ──► PAT-003 (Salary + Capital Gains)
  ├── has gig income?     ──► PAT-002 (Salary + Gig)
  ├── has let-out HP?     ──► PAT-007 (Salary + Let-Out Property)
  ├── multiple Form 16s?  ──► PAT-004 (Multiple Employers)
  └── is NR/RNOR?         ──► PAT-005 (NRI)

PAT-002 (Salary + Gig)
  │
  └── has capital gains?  ──► PAT-003 (with business income flag)

PAT-006 (Pensioner)
  │
  └── has FD interest?    ──► stays PAT-006 (FD interest is core to this pattern)
  └── has capital gains?  ──► PAT-003 (pension treated as salary head)
```

---

*Document Version: 1.0.0*
*Effective: AY2025-26*
