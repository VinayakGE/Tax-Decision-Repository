# Evidence Doctrine

*Engineering principles for building trustworthy decision systems through independent evidence.*

---

## Doctrine Origins

The doctrines below were not designed in advance. They were discovered by allowing real cases to contradict the system and updating accordingly. This table records what forced each doctrine into existence — applying the same evidentiary standard to the methodology that the methodology applies to the rules.

| Doctrine | Origin | What forced it |
|---|---|---|
| Doctrine 0 | RC-0001 + D-001 | D-001 could not have been detected by any synthetic test. The entire test suite shared the same wrong assumption. |
| Doctrine 1 | RC-0001 | 107 synthetic tests passed while the standard deduction was wrong for both regimes. |
| Doctrine 2 | RC-0001 | A single CPC-verified return exposed what 107 tests missed. |
| Doctrine 3 | RC-0002 (IG-001) | Perquisites treatment unclear — engine behavior may be correct, or the filing may have omitted them. Implementing a guess would have been wrong. |
| Doctrine 4 | RC-0001 + RC-0002 | Rules implemented before RC-0001 had no independent verification. D-001 revealed that consistency without independence is not correctness. |
| Doctrine 5 | RC-0002 planning | Two salary cases cannot expose business income, house property, or capital gains errors. Corpus selection must be intentional. |
| Evidence Regression | Finance Act cadence | No code change is required for the implementation to become wrong. External authority moves; the engine must follow; synthetic tests cannot detect the drift. |

A doctrine that cannot be traced to an observation has the same status as a rule with no independent case behind it: consistent with the author's reasoning, but not yet verified against reality.

---

## Doctrine 0: No System Can Fully Validate Its Own Foundational Assumptions

A system cannot establish the correctness of assumptions that originate from within itself using only artifacts derived from those assumptions.

This is not a formal mathematical statement (Gödel's incompleteness theorem operates in a different domain). It is an epistemic constraint on engineering practice, closer in spirit to Popper's falsificationism: a theory cannot be confirmed from within its own framework, only potentially falsified from outside it.

Applied to decision systems: you cannot *establish* correctness by running tests derived from the same interpretation that produced the implementation. You can only accumulate external evidence that the system has not yet been falsified.

Every software project has this constraint. Most never acknowledge it. The consequence of acknowledging it is the methodology described in this document.

---

## Three Kinds of Truth

A trustworthy decision system must answer three distinct questions, each requiring a different kind of evidence:

| Layer | Question | Evidence source |
|---|---|---|
| **Logical Truth** | Does the implementation correctly follow its own rules? | Unit tests |
| **Behavioral Truth** | Does the implementation continue behaving the same way over time? | Golden masters, regression tests |
| **Empirical Truth** | Does the implementation agree with independently established reality? | CPC 143(1) intimations, CA computations, official assessments |

These layers are not redundant — they answer different questions. Unit tests do not become obsolete when real cases exist. Real cases do not replace golden masters. But they are not independent: **Empirical Truth can retroactively invalidate Behavioral Truth baselines**.

When an empirical observation reveals that the implementation has been wrong since before the behavioral baselines were generated, those baselines must be recomputed from the corrected state — not patched. Patching a golden master to the correct value while leaving the implementation wrong would restore consistency without establishing correctness.

**Defect D-001** demonstrates this cascade. The empirical finding (CPC-accepted return requiring ₹75,000 standard deduction) revealed that the implementation was wrong. Correcting the implementation then required regenerating 15 golden masters, because all 15 had been generated from the incorrect baseline. The empirical correction propagated backward through the behavioral layer and reset it.

The dependency ordering is:

```
Correct Logical Truth → stable Behavioral baselines
Empirical Truth exposes Logical errors → Behavioral baselines must be recomputed, not patched
```

---

## The Core Problem: Circularity of Validation

Traditional decision-system engineering assumes this model:

```
Law → Implementation → Testing → Confidence
```

This breaks in a specific, non-obvious way.

The synthetic test corpus and the implementation share the same author: a human's interpretation of the source material. When both are derived from the same mental model, they can agree perfectly while both being wrong in the same direction. Testing then reports zero defects — not because the system is correct, but because the error is consistent across both the implementation and the tests.

This is the **circularity problem**. Internal consistency is not the same as correctness.

**Defect D-001** is the canonical example. The old-regime standard deduction was implemented as ₹50,000. The synthetic test suite expected ₹50,000. Both were wrong (Finance No. 2 Act 2024 raised it to ₹75,000). Both agreed. Zero defects reported — until one real CPC-accepted return exposed the mismatch.

No synthetic test can break this circularity, because every synthetic test is downstream of the same misunderstanding. Only a reference from outside the closed system can.

The empirical validation layer exists for this reason. It is not redundant with testing. It operates at a different epistemic level.

```
Law
 ↓
Implementation
 ↓
Testing         ← verifies internal consistency
 ↓
Independent Evidence  ← verifies correct grounding in reality
 ↓
Correction
```

---

## The Five Doctrines

These follow from Doctrine 0. Each one is an engineering decision about how to operate within the constraint that no closed system can fully validate itself.

**Doctrine 1** — *Synthetic evidence establishes consistency, not confidence.*

A system that passes 1,000 synthetic tests is consistent. It is not verified. The tests and the implementation share the same source of error. This is not a criticism of synthetic tests — they are necessary for the Logical Truth layer. It is a statement about what they cannot establish.

**Doctrine 2** — *Independent evidence establishes confidence.*

An independent source is one whose computation is not derived from the same mental model as the implementation. CPC 143(1) intimations, CA-reviewed computations, and official assessments qualify. A human manually applying the same interpretation of the statute does not fully qualify — the circularity is only partially broken.

**Doctrine 3** — *Interpretation uncertainty must never be silently encoded as deterministic logic.*

When the correct treatment of an observation is not yet known, the observation becomes an Interpretation Gap. Implementing a guess as a rule converts uncertainty into false confidence and may cause the system to learn the wrong behavior. An Interpretation Gap may close with no code change — if evidence later confirms that the engine behavior was already correct.

**Doctrine 4** — *Every implemented rule should eventually trace back to independent evidence.*

A rule with no independent case behind it has unknown accuracy. It has been verified consistent (tests pass) but not verified correct (no independent reference confirms it produces the right answer). Consistency is not correctness.

**Doctrine 5** — *The validation corpus defines the boundary of verified knowledge. Expand it deliberately, not randomly.*

The cases you have run determine what reality has had the opportunity to teach the system. A corpus of 20 salary-only cases cannot expose errors in capital gains rules, presumptive income rules, or house property rules. Corpus selection is an experimental design problem. Cases should be chosen to maximize the probability of uncovering errors in regions of the rule space that have not yet been independently verified.

---

## Evidence Classification

### Rule Gap (RG)

A statutory provision that exists and applies but is not implemented in the engine.

- Status: Observed → Explained → Implemented → Verified
- Resolution: always involves a code change
- Example: RG-005, Section 80CCD(2) employer NPS — identified in RC-0002, confirmed by CPC intimation (₹70,000 impact)

### Knowledge Gap (KG)

An Interpretation Gap that resolves into a confirmed implementable rule when sufficient evidence arrives.

- Status: (promoted from IG) → Implemented → Verified
- Resolution: code change after evidence confirms correct interpretation

### Interpretation Gap (IG)

An observation that cannot yet be classified as a rule gap or evidence gap because the correct treatment is not yet established.

```
Observation
     ↓
Interpretation Gap
     │
     ├── Evidence supports implementation
     │         ↓
     │    Knowledge Gap → rule implemented
     │
     └── Evidence supports current engine behavior
               ↓
          Close with NO code change
```

The second exit path is important. An IG may close without any code change, because the observation turns out to reflect a filing error or incomplete evidence rather than an engine error. The system was already correct; the observation was incomplete.

- Example: IG-001, perquisites treatment — Form 24Q reports ₹6,541; CPC accepted return without them; no evidence yet that they were Rule 3 exempt vs. simply omitted by the taxpayer. Engine behavior (include perquisites at full value under Section 17(2) default) is the more defensible statutory position.

### Evidence Gap (EG)

Evidence that was expected to be present in the case but was not recorded, causing the engine to compute with an incomplete picture. Distinct from a rule gap — the rule may be correct, but the input was incomplete.

- Resolution: update the case file; re-run validation
- Example: prior year 244A refund interest (₹1,743) missing from RC-0002 initial evidence, later found in prefill data

### Domain Model Gap (DMG)

A structural limitation in how the evidence schema represents a concept, distinct from an unimplemented rule.

- Example: VDA income was initially represented in `head_5_other_sources` with `amount: null`, but VDA flows to `head_4_capital_gains` in ITR-2. The model needed extension, not just a new rule.

---

## Evidence Weight

Evidence Weight has two independent dimensions: **Strength** and **Breadth**. They should not be collapsed into a single scalar, because they represent different failure modes.

### Strength (per observation)

How much epistemic weight does each observation carry?

| Provenance | Tier | Weight |
|---|---|---|
| CPC 143(1) intimation | Government-accepted | 3 |
| CA-reviewed computation | Expert-independent | 2 |
| Taxpayer self-computation | Author-dependent | 1 |
| Synthetic case | Engine-derived | 0.5 |

**Strength score** for a rule = sum of weights across all observations that exercise it.

### Breadth (across the corpus)

How many distinct income categories, regime choices, and edge conditions has the rule been tested against independently?

Breadth is not just a count — it measures coverage across orthogonal dimensions:

- Regime (new vs. old)
- Income head (salary, capital gains, house property, business, other sources)
- Age bracket (general, senior, super-senior)
- Complexity tier (simple salary, multiple employers, VDA, foreign assets, surcharge)

**Breadth failure**: 10 high-strength observations all from salary-only cases leaves all other income categories with zero independent verification of the same rule.

### Prioritization

- Maximize **breadth** until minimum category coverage is achieved
- Maximize **strength** within each covered category
- A rule with strength ≥ 6 and breadth across ≥ 3 categories is provisionally well-evidenced

---

## Corpus Design

The validation corpus is not a collection of whatever cases are available. It is a designed experiment.

**Corpus selection criterion**: prefer cases that exercise rule combinations not yet independently verified, rather than cases that accumulate evidence for already-verified rules.

**Minimum coverage target (M2)**:

| Category | Target cases | Notes |
|---|---|---|
| Salary only, new regime | 2 | Baseline |
| Salary only, old regime | 2 | Regime comparison |
| Multiple employers | 1 | Aggregation logic |
| HRA + salary | 2 | Section 10(13A) |
| Capital gains | 2 | Short-term + long-term |
| Presumptive income (44AD/44ADA) | 2 | Business head |
| House property | 2 | Rental income |
| VDA income | 1 | Section 115BBH |
| High-income surcharge | 1 | >₹50L |
| 80C + 80D deductions | 2 | Chapter VI-A depth |
| Foreign assets | 1 | Schedule FA |

Completing this matrix with CPC-verified cases provides strong independent confidence across the rule space. Cases that overlap categories (e.g., salary + capital gains + 80C) are particularly valuable because they expose interaction effects between rules.

---

## Evidence Closure Lifecycle

Each rule gap, knowledge gap, and interpretation gap carries a `closure_stage` that is updated as evidence accumulates.

```
Observed → Explained → Implemented → Verified
```

| Stage | Definition |
|---|---|
| Observed | Mismatch identified between engine output and independent reference |
| Explained | Root cause identified; categorized as RG / KG / IG / EG / DMG |
| Implemented | Code change made (or, for IGs, determination that no change is warranted) |
| Verified | A subsequent independent case confirms the corrected behavior |

The `Verified` stage requires a *new* case — the case that exposed the gap cannot itself verify the fix.

### Living document pattern

Each real case's `_investigation_log` carries the observation and explanation. The implementation is traceable via git commit. Verification is traceable via the subsequent case that exercises the same rule after the fix.

```json
{
  "id": "RG-005",
  "description": "Section 80CCD(2) employer NPS not implemented",
  "closure_stage": "Explained",
  "observed_in": "RC-0002",
  "observed_date": "2026-06-26",
  "impact": "₹70,000 GTI under-reduction under new regime",
  "implemented_commit": null,
  "verified_in": null
}
```

---

## Relationship to Testing

This doctrine does not diminish the role of the synthetic test suite. The three layers are complementary and each answers a different question:

| Layer | What it establishes | What it cannot detect | Independence from implementation |
|---|---|---|---|
| Unit tests | Rule logic follows its own axioms | Axioms encoded in rules are wrong | None — shares same source interpretation |
| Golden master tests | Engine output is stable across changes | Baseline output was wrong at generation time | Partial — shares assumptions at generation time |
| Independent case validation | Engine output matches independently established reality | — | Complete — no shared assumptions |

The layers are ordered by independence from the implementation. This ordering determines what each layer can establish: unit tests establish Logical Truth, golden masters establish Behavioral Truth, independent cases establish Empirical Truth.

All three layers are necessary. The presence of layers 1 and 2 without layer 3 leaves the system in a state where it can know it is consistent but cannot know it is correct. That distinction is not philosophical — it is the difference between a system that has never been shown to be wrong and a system that has been shown to be right.

For regulated decision engines specifically, "has not been shown to be wrong" is not sufficient. A government authority (CPC, tax tribunal, appellate body) will measure the system against independently established computation, not against internal consistency. The empirical layer is therefore not optional for this class of system — it is the only layer that answers the question a regulated outcome actually poses.

---

## Knowledge Drift and Evidence Regression

### Three kinds of drift

Software systems are subject to familiar drift types. A regulated decision engine adds a third:

| Drift type | Trigger | Detection mechanism |
|---|---|---|
| **Code drift** | Developer changes code | Unit tests, CI, golden masters |
| **Dependency drift** | Library or platform changes | Integration tests, dependency alerts |
| **Knowledge drift** | External authority changes meaning or interpretation | Independent case validation, regulatory watch |

Code drift and dependency drift are well understood. Knowledge drift is characteristic of knowledge systems — systems whose correctness depends not just on their internal logic but on alignment with an external authority that evolves independently.

### Evidence regression: the observable form of knowledge drift

When knowledge drift reaches the implementation — when the external authority has moved and the implementation has not — the system is in an **evidence regression**. Its tests all pass. Its behavior is internally consistent. But it is producing wrong answers, because the reference reality it was built against no longer matches the reference reality that governs.

Conventional software has two maintenance triggers:

1. **Code regression** — a code change causes behavior to change unexpectedly
2. **Requirement change** — new requirements mean code must change

A regulated decision engine has a third:

3. **Evidence regression** — reference reality changes, making the implementation wrong even though nothing in the repository changed

For a tax engine, evidence regression triggers include:
- Finance Act published each year (slab rates, deduction limits, new sections)
- CBDT circulars and notifications (interpretation of existing provisions)
- CPC processing behavior changes (what the government actually computes)
- New forms or schedules (structural changes to how income is reported)

The critical property of evidence regression: **all synthetic tests will continue to pass**. The tests don't know the statute changed. Only an independent case from the new period — or a deliberate re-validation pass against the updated reference — can expose the drift.

This changes the maintenance calendar. The system now runs on two independent clocks:

```
Engineering clock   → code changes, refactors, dependency updates
Regulatory clock    → Finance Act, CBDT circulars, CPC behavior
```

The regulatory clock does not respect sprint cycles. It fires in February when the Union Budget is presented, again when the Finance Act receives assent, and at irregular intervals when CBDT issues clarifications. Each event is a potential evidence regression that must be absorbed into the implementation and re-verified against real cases from the new period.

A system without the empirical layer has no mechanism to detect evidence regression. A system with it has a natural detection mechanism: the first independent case from the new period that exercises the affected rule will expose the drift.

The practical consequence is that **every Finance Act change should be followed by targeted corpus expansion** — at least one real case exercising the changed rules in the new period, verified against CPC computation, to close the evidence regression loop.
