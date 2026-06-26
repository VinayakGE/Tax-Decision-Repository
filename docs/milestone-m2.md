# Milestone M2 — First Externally Grounded Corpus

**Status**: Active  
**Phase**: Phase 4 (Evidence)  
**Written**: 2026-06-26 (after RC-0001, RC-0002)

---

## What M2 Is

M2 is not "20 cases processed."

M2 is the construction of the first validation corpus that is externally grounded — meaning every significant disagreement between the engine and independently established reality has a documented epistemic status.

The cases are not test inputs. They are the first independent body of evidence from which the engine, the methodology, and eventually the doctrine can learn.

---

## The Objective

The objective is not maximum agreement with independent references.

**The objective is: maximize justified agreement while minimizing unjustified disagreement.**

These are different optimization targets. An engine that replicates CPC-accepted returns 100% of the time — including returns where CPC accepted a filing error — is not more correct than an engine that disagrees in documented, legally defensible ways. Chasing agreement without justification produces compliance with practice rather than compliance with statute. For a regulated decision engine, those can diverge.

---

## Success Criteria

M2 is achieved when all five criteria are met simultaneously.

| Criterion | Target | Measure |
|---|---|---|
| **Corpus coverage** | ≥ 10 real cases spanning ≥ 5 distinct income category combinations | See Coverage Matrix below |
| **True matches increasing** | ≥ 1 case per income category where engine = independent reference with no active rule gaps | Match rate per category, not aggregate |
| **Rule gaps decreasing** | No Rule Gap reaches RC-0020 still at Observed or Explained without a closure decision | Every RG has a closure_stage ≥ Explained with an estimated implementation timeline |
| **Defects approaching zero** | Zero known defects remain at Implemented or later stages without Verified status | Defect closure table |
| **Unexplained disagreements approaching zero** | Every disagreement in every real case has a named epistemic status | 100% classification rate across all cases |

**The criterion that matters most is the last one.** A system where every disagreement is classified — even if some are Rule Gaps or Accepted Mismatches — has achieved a kind of epistemic maturity that a high match rate alone cannot demonstrate.

---

## What "Done" Means for M2

A case is "done" not when it has been run through the engine, but when every component of the mismatch has been assigned to a named category.

A case is "diagnosed" when `every_disagreement_has_epistemic_status = true`.

Until then, the case is processed but not diagnosed.

---

## The Two-Dimensional Classification System

Learning Velocity is now two-dimensional. Outcome Classification and Closure State are orthogonal — they must not be collapsed into a single label.

### Dimension 1: Outcome Classification (what kind of disagreement)

| Category | Definition | Engine action |
|---|---|---|
| **True Match** | Engine and independent reference agree | Increase confidence |
| **Accepted Mismatch** | Engine disagrees for documented, legally defensible reasons | Preserve, document, monitor |
| **Rule Gap** | Statutory provision exists and applies, not yet implemented | Implement and revalidate |
| **Defect** | Implementation incorrect | Fix immediately and verify |
| **Evidence Gap** | Case evidence was incomplete; engine computed correctly given what it had | Update case evidence, re-run |
| **Interpretation Gap** | Correct treatment not yet established; may resolve either way | Hold in investigation queue |

### Dimension 2: Closure State (how mature is our understanding)

| State | Definition | Who grants it |
|---|---|---|
| Observed | Mismatch identified | Engineer |
| Explained | Root cause identified and categorized | Engineer |
| Implemented | Code change made (or no change warranted for IG/AM) | Engineer |
| **Verified** | Subsequent independent case confirms corrected behavior | **Reality** |

The asymmetry in the Verified row is structural, not procedural. Engineers can mark Observed, Explained, and Implemented. They cannot self-certify Verified. Verification is granted by an independent reference that was not used to construct the fix. This constraint is constitutive — remove it and the lifecycle collapses to tracking effort rather than tracking evidence.

### The terminal cell

The cell (Accepted Mismatch, Verified) is the first in the lifecycle where Verified is the terminal state rather than a precondition for further work. IG-001 (perquisite treatment) is the first case where the engine has arrived at this cell. It should remain there unless authoritative evidence arrives that resolves the interpretation.

---

## The New Asymptote

Most software converges toward: **100% tests passing**  
Most prediction systems converge toward: **maximum accuracy**  
Jarviz converges toward: **100% of disagreements classified**

This asymptote is:
- **Reachable** — every disagreement can eventually be named
- **Honest** — it does not require eliminating disagreements that represent defensible positions
- **Externally grounded** — the Verified state requires independent evidence, so the asymptote can't be reached by simply declaring everything classified

The endpoint is not a system where everything agrees. It is a system where every disagreement can be immediately answered: *implementation defect, missing rule, interpretation difference, evidence quality issue, or accepted mismatch.* If no disagreement remains unexplained, the system has reached epistemic maturity.

---

## Calculator vs Decision Engine

A calculator's accountability is output equivalence: produce the same number.

A decision engine's accountability is reasoning equivalence: trace every difference in output to a named difference in reasoning about the source material.

M2 is where Jarviz becomes a decision engine rather than a calculator. It doesn't happen when the match rate crosses a threshold. It happens when the system can account for every disagreement with an independent reference, including those where the disagreement is the correct outcome.

---

## Corpus Design

Corpus selection is experimental design, not data collection (see `docs/evidence-doctrine.md`, Doctrine 5).

Every real case should either increase confidence (exercises well-covered rules, matches) or increase coverage (exercises income heads or regime combinations not yet independently verified). Cases that do neither are lower priority.

### Minimum coverage matrix for M2

| Income category | Regime | Target cases | Current coverage | CPC-verified |
|---|---|---|---|---|
| Salary only | New regime | 2 | 2 (RC-0001, RC-0002) | 1 (RC-0002) |
| Salary only | Old regime | 2 | 0 | 0 |
| Multiple employers | Either | 1 | 0 | 0 |
| HRA + salary | Old regime | 1 | 0 | 0 |
| House property (rental) | Old regime | 2 | 0 | 0 |
| Capital gains | Either | 1 | 0 | 0 |
| Presumptive business (44AD/44ADA) | Either | 1 | 0 | 0 |
| VDA income | New regime | 1 | 0 | 0 |
| 80C + 80D deductions | Old regime | 2 | 0 | 0 |
| High-income surcharge (>₹50L) | Either | 1 | 0 | 0 |

### Next case recommendation

**RC-0003**: Old regime taxpayer with house property income and Section 24(b) interest deduction. Rationale: simultaneously tests old regime deduction aggregator (first independent real-world verification), house property (new income head), and Section 24(b) (new deduction type). Whatever the outcome — match, rule gap, or new interpretation gap — the corpus becomes substantially more informative.

---

## Accumulated Institutional Knowledge

As Accepted Mismatches accumulate across cases, they constitute something beyond the individual cases. If, at RC-0020, there are multiple cases where the engine disagrees with CPC-accepted returns in the "engine more defensible" direction, and those disagreements are documented, that is an empirical finding about the systematic gap between statute compliance and accepted practice in Indian income tax administration.

This institutional knowledge cannot be produced by a calculator. It requires a system that maintains both the correct answer and the reasoning for why it differs from the accepted answer.

---

## Current State (as of RC-0002)

| Metric | Value |
|---|---|
| Real cases processed | 2 |
| Cases fully diagnosed | 2 |
| Unexplained disagreements | 0 |
| True matches | 0 |
| Accepted mismatches | 1 (IG-001, perquisites) |
| Rule gaps at Verified | 0 |
| Rule gaps at Implemented | 1 (RG-005, 80CCD(2)) |
| Rule gaps at Explained | 4 (RG-001, 002, 003, 004) |
| Defects found | 4 (D-001, D-002, D-003, D-004) |
| Defects at Verified | 4 |
| Corpus coverage (income heads) | 1 of 10 categories with real-case coverage |
