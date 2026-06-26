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

**M2 is achieved when the engine can account for every observed disagreement with independent evidence. Agreement is one valid outcome; documented, legally justified disagreement is another. Unexplained disagreement is not.**

The objective is not maximum agreement with independent references.

**The objective is: maximize justified agreement while minimizing unjustified disagreement.**

These are different optimization targets. An engine that replicates CPC-accepted returns 100% of the time — including returns where CPC accepted a filing error — is not more correct than an engine that disagrees in documented, legally defensible ways. Chasing agreement without justification produces compliance with practice rather than compliance with statute. For a regulated decision engine, those can diverge.

Notice what this objective does not contain: a match-rate threshold. A corpus that deliberately chose more difficult, diverse cases should not fail M2 simply because harder cases produced more Rule Gaps. Harder cases produce more learning per case. The milestone rewards epistemic completeness, not superficial agreement.

---

## Exit Criteria (binary gates — all must be satisfied)

These are pass/fail. The milestone is not complete until all are satisfied simultaneously.

| Gate | Criterion | Why this gate |
|---|---|---|
| **G1: Corpus** | ≥ 20 independently validated real cases, spanning ≥ 5 distinct income category combinations | Minimum empirical basis. Fewer cases cannot reliably expose the rule space. |
| **G2: Defects** | Zero known Defects remain unresolved (Observed, Explained, or Implemented without Verified) | No known implementation errors may remain open. |
| **G3: Classification** | Every disagreement in every real case has a named Outcome Classification | 100% classification rate. No unexplained deltas. |
| **G4: Rule Gaps** | Every Rule Gap is either at Implemented+, or explicitly accepted into the roadmap with a documented timeline | No unknown engineering work. Rule Gaps not yet implemented must be acknowledged, not ignored. |
| **G5: Accepted Mismatches** | Every Accepted Mismatch is documented with its competing statutory interpretations and the legal reasoning for the engine's position | Disagreements must be intentional and traceable. Undocumented Accepted Mismatches are not acceptable. |

No match-rate gate. No minimum True Match percentage. A corpus with 20 cases that exposed 15 Rule Gaps and documented them all has satisfied G3 and G4 and is more valuable than a corpus with 20 cases that avoided difficult territory to maintain a high match rate.

---

## Health Indicators (continuous — not pass/fail)

These describe the maturity and trajectory of the corpus. They do not determine whether M2 has been reached, but they should be tracked with each case.

| Indicator | Desired direction | Notes |
|---|---|---|
| True Match rate | Increasing | Measures rule coverage maturity |
| Accepted Mismatch rate | Stable and documented | High rate may indicate systematic gap between statute and practice |
| Rule Gap count | Decreasing | As rules are implemented |
| Defect count | Approaching zero | With each case cycle |
| Coverage breadth | Increasing | New income heads, new regime/deduction combinations |
| Unexplained delta per case | Approaching zero | Measures diagnostic completeness |

A corpus where True Match rate is increasing, Rule Gap count is decreasing, and every disagreement is classified is a healthy corpus — regardless of the absolute match rate.

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

A decision engine's accountability is *reasoning equivalence*: trace every difference in output to a named difference in reasoning about the source material. Disagreement is no longer opaque — it becomes an object the system can reason about.

M2 is where Jarviz becomes a decision engine rather than a calculator. It doesn't happen when the match rate crosses a threshold. It happens when the system can account for every disagreement with an independent reference, including those where the disagreement is the correct outcome.

### The reasoning comparison artifact

Because reasoning is the accountable unit, every fully-diagnosed case should eventually support two distinct conclusions rather than one:

**Conclusion 1 — Decision:**
> Refund: ₹1,42,500

**Conclusion 2 — Reasoning Comparison:**
> - Salary treatment: equivalent  
> - Standard deduction: equivalent  
> - 80CCD(2): equivalent  
> - Perquisites: *different*  
>   → Status: Accepted Mismatch (IG-001)  
>   → Engine position: Section 17(2) default — perquisites taxable absent exemption evidence  
>   → Filed return: perquisites omitted  
>   → CPC action: accepted filed treatment  
>   → Resolution: await authoritative evidence on exemption status

This is qualitatively richer than a pass/fail comparison. It tells the reader not just that the engine agrees or disagrees, but *where* in the reasoning the divergence occurs and *why* the divergence is either accepted or under investigation.

The reasoning comparison artifact is the mechanism that makes reasoning equivalence concrete rather than aspirational.

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
