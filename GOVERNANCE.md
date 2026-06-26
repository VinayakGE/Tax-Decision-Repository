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

Rules are encoded in four waves, ordered by decision impact — not by section frequency. A perfect HRA calculation is useless if the engine filed the wrong form.

### Wave 1 — Decision-Critical Rules (R-0006 to ~R-0050)

These answer: **"Can I file this return correctly?"** No computation rule runs until Wave 1 is complete.

- Income classification authority (R-0006 — done)
- Salary vs business vs professional income distinction
- Full ITR eligibility matrix (extensions of R-0001 through R-0004)
- New vs Old regime eligibility and opt-out rules
- Presumptive taxation eligibility: 44AD, 44ADA, 44AE (thresholds, disqualifiers, opt-out lock-in)
- Residential status determination (ROR, RNOR, NR)
- Director status impact on ITR eligibility
- Unlisted equity holder impact on ITR eligibility
- Foreign assets / foreign income — ITR-2 mandatory
- Capital gains existence — ITR form upgrade triggers
- Agricultural income threshold — partial integration rules

### Wave 2 — Reconciliation Rules (~R-0051 to R-0150)

These answer: **"Is this return internally consistent?"** No filing recommendation is complete without reconciliation.

- AIS ↔ 26AS reconciliation (income amounts, TDS credits)
- AIS ↔ Prefill JSON reconciliation
- 26AS ↔ Form 16 TDS reconciliation (extension of V-001)
- Duplicate income detection across evidence sources
- Missing TDS credit rules
- Missing interest income detection (extension of V-002)
- PAN mismatch in evidence documents
- Bank account pre-validation for refunds (extension of V-003)
- Advance tax default detection (extension of V-005)

### Wave 3 — Computation Rules (~R-0151 to R-0400)

These answer: **"How much tax?"** Only reached after Wave 1 and Wave 2 are stable.

- Salary deductions: standard deduction, exempt allowances, HRA, LTA, perquisites
- House property: SOP vs LOP, NAV computation, 30% standard deduction, 24(b) interest
- 80C family deductions (80C, 80CCC, 80CCD)
- 80D health insurance deduction
- 80CCD additional NPS deduction
- 80G donations
- 80TTA / 80TTB interest deductions
- Special rate computations: 111A, 112A, 112, 115BB, 115BBH
- Rebate u/s 87A (both regimes)
- Surcharge computation and marginal relief
- Cess computation
- Section 234B / 234C interest

### Wave 4 — Edge Cases (~R-0401+)

These handle the long tail of complex situations.

- ESOP: perquisite on allotment, capital gain on sale
- Crypto and VDA: 115BBH, 194S TDS
- Share buyback
- RSUs and stock options for MNC employees
- DTAA claims (relief u/s 90 / 90A / 91)
- Section 89 relief for salary arrears
- Clubbing of minor's income
- Loss set-off and carry forward rules
- Search and reassessment scenarios
- Revised return rules

---

*This charter does not expire. It is updated only by a Change record approved by the repository maintainer.*
