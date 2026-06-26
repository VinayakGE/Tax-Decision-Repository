# Pattern Repository

Patterns are coarse-grained taxpayer profiles. They are not rules — they do not cite legal authority and cannot override the rule engine. They exist to compress the decision space and minimize the questions Jarviz must ask before reaching a confident decision.

## Pattern Index

| ID | Title | Prevalence | ITR Form | Complexity |
|----|-------|-----------|----------|-----------|
| PAT-001 | Salaried, Single Employer | Very Common (~45%) | ITR-1 | Simple |
| PAT-002 | Salary + Gig / Freelance (44AD) | Common (~12%) | ITR-4 | Moderate |
| PAT-003 | Salary + Capital Gains | Common (~10%) | ITR-2 | Moderate |
| PAT-004 | Multiple Employers (Job Change) | Common (~8%) | ITR-1 | Moderate |
| PAT-005 | NRI — Indian Source Income | Moderate (~3%) | ITR-2 | Complex |
| PAT-006 | Pensioner + FD Interest | Common (~7%) | ITR-1 | Simple |
| PAT-007 | Salary + Let-Out Property | Moderate (~4%) | ITR-1 | Moderate |
| PAT-008 | Professional Presumptive (44ADA) | Moderate (~3%) | ITR-4 | Moderate |

**Combined coverage: ~95% of individual filer profiles.**

## How Pattern Matching Works

See `docs/pattern-matching.md` for the full matching process.

Short version:
1. Identify documents present → suggests a pattern
2. Ask confirmation questions (≤ 5 questions per pattern)
3. Confirm or escalate to a higher-complexity pattern
4. Run the pattern's decisions and rules in the specified order
5. Rule engine verdict always overrides pattern expectation

## What a Pattern Is Not

- Not a legal rule. No legal citation.
- Not a test case. Patterns have no pass/fail.
- Not a decision tree. Patterns feed into the decision tree — they don't replace it.
- Not exhaustive. Edge cases within a pattern still go through the full rule engine.

## Adding a New Pattern

Add a pattern only when:
- A recurring taxpayer profile appears in the case library at least three times
- The profile's intake questions differ from all existing patterns
- The profile reaches a reliably different outcome than similar patterns

Assign the next `PAT-XXX` ID. Validate against `schemas/pattern-schema.json`. Add to `registry/pattern-registry.json`.
