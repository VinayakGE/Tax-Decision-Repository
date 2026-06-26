# Jarviz Repository Governance Charter

> Effective from v1.3.0. Applies to all contributors, all changes, all time.

---

## The Seven Principles

**1. Evidence before inference.**
Every fact used in a decision must trace to a loaded document or a recorded user answer. Jarviz never assumes. If the evidence is absent, the confidence band drops and the taxpayer is asked.

**2. Deterministic computation before AI explanation.**
Stages 1 through 12 of the pipeline contain no AI. Tax law is deterministic; computation is arithmetic. The AI is permitted exactly once — Stage 13 — to narrate a pre-computed result. It does not reason. It does not invent. It translates.

**3. Every rule has legal authority.**
A rule without a primary legal citation does not exist. `authority.section` and `authority.act` are required fields. A rule that cites secondary material (a news article, a CA blog, a circular summary) without the primary source is rejected at peer review.

**4. Every decision is traceable.**
Every output Jarviz produces — ITR form, tax regime, refund amount, validation failure — must be reproducible from the Decision Execution Log alone. "The AI decided" is not an explanation. The rule IDs that produced the outcome are the explanation.

**5. Every rule is tested.**
No rule is merged to `active` status without at least one positive test, one negative test, and one boundary test. Rules that touch thresholds (income ceilings, turnover limits, rate cutoffs) require a boundary test at exactly the threshold value. Zero exceptions.

**6. Every change is versioned.**
No rule, validation, decision tree, or schema changes without a corresponding `CH-XXXX` change record and a `CHANGELOG.md` entry. The version registry records a quality snapshot at every tagged release. The history of the repository is the history of every rule change, traceable to the Finance Act that caused it.

**7. Architecture changes require measurable justification.**
The architecture is frozen at v1.3.0. A proposed architectural change must cite: (a) a specific benchmark failure (JAB metric and measured value), or (b) a specific user pain point with evidence from real cases. "This would be cleaner" is not justification. The cost of architectural complexity is paid by every contributor who follows.

---

## Release Quality Profile

Every tagged release must record this profile in `registry/version-registry.json`:

| Field | Description |
|-------|-------------|
| `active_rules` | Count of rules with `status: active` |
| `deprecated_rules` | Count of rules with `status: deprecated` |
| `active_cases` | Count of cases in `cases/` |
| `total_tests` | Count of test files in `tests/` |
| `jab_score` | Overall JAB M-01 ITR accuracy, or `null` if GSS < 100 cases |
| `finance_act_version` | Most recent Finance Act encoded in rules |
| `gss_case_count` | Gold Standard Set size at time of release |

Example progression:

| Release | Rules | Cases | Tests | JAB M-01 | Finance Act |
|---------|-------|-------|-------|----------|-------------|
| v1.3.0  | 5     | 1     | 3     | null     | 2024        |
| v2.0.0  | 500   | 500   | 2,000 | 96.8%    | 2026        |

A release where `jab_score` regresses from the prior release is blocked unless the regression is explained and accepted.

---

## Phase 5 Priorities (v2.0 target)

Work in this order. Do not start the next epic until the current one has passed JAB.

| Epic | Target | Acceptance Criterion |
|------|--------|---------------------|
| E-1: Rule Repository | R-0006 → R-0500 | 100% rule test coverage; all rules `active` |
| E-2: Case Repository | 500 anonymized real cases | Each case has filed outcome or CA sign-off |
| E-3: Rule Tests | 2,000+ tests | No rule without positive + negative + boundary test |
| E-4: Engine Implementation | All 5 engines running end-to-end | JAB M-01 ≥ 99%, M-02 < 0.5%, M-05 ≥ 99% |

**The milestone that matters:**
> Jarviz processed its first 100 real taxpayer returns end-to-end with ≥ 99% correct ITR selection, deterministic calculations, complete decision traces, and no unexplained validation failures.

That milestone — not rule count — is what demonstrates the architecture works in practice.

---

## Rule Authoring Priority for Epic 1

Encode rules in this sequence, highest-frequency topics first:

1. Salary (Head 1 — deductions, exemptions, perquisites)
2. TDS (credit computation, 26AS matching)
3. ITR eligibility (extensions of R-0001 through R-0004)
4. Presumptive taxation (44AD, 44ADA, 44AE — thresholds, disqualifiers)
5. Interest income (Head 5 — savings, FD, 80TTA, 80TTB)
6. House property (SOP vs LOP, interest deduction, loss set-off)
7. Capital gains (all asset classes, holding periods, AY2025-26 rate splits)
8. Deductions (80C family, 80D, 80E, 80G, 80CCD)
9. Foreign assets and DTAA
10. Audit and edge cases (44AB, 234B/234C, revised returns)

---

*This charter does not expire. It is updated only by a Change record approved by the repository maintainer.*
