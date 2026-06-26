# Rule Lifecycle Model

> This document defines every stage a rule passes through from authorship to archival.
> No rule reaches `active` without passing through peer review and legal review.
> This is the quality gate that keeps the repository trustworthy at scale.

---

## The Seven Stages

```
draft
  │
  ▼
peer_reviewed
  │
  ▼
legal_reviewed
  │
  ▼
active ──────────────► deprecated ──► archived
  │                         ▲
  └──► superseded ───────────┘
         │
         └──► (new rule is active)
```

---

## Stage Definitions

### 1. `draft`

**What it means:** The rule is being authored. It exists in the repository but is not used in any live decision.

**Requirements to enter:** None. Any contributor can create a draft.

**Requirements to exit:** A draft may move to `peer_reviewed` only when:
- All required fields are populated (id, title, description, logic, authority, effective_date, assessment_years, version, tags, evidence_refs, decision_refs)
- At least one test case exists (`test_refs` is non-empty)
- The file validates against `schemas/rule-schema.json`

**What the AI does with draft rules:** Ignores them entirely. Draft rules are never retrieved.

---

### 2. `peer_reviewed`

**What it means:** A second contributor has verified the rule's logic, completeness, and internal consistency.

**Requirements to enter:** Passed all `draft` exit requirements AND:
- A second contributor (not the author) has reviewed the rule
- Review is documented in the Pull Request or via a `review_ref` in the change entry
- All test cases pass

**What the reviewer checks:**
- Does the rule logic match the authority cited?
- Are edge cases covered by tests?
- Are the evidence_refs correct?
- Is the effective_date accurate?
- Could this rule conflict with an existing active rule?

**What the AI does:** Still ignores — never retrieves `peer_reviewed` rules.

---

### 3. `legal_reviewed`

**What it means:** The rule's legal citation has been verified against the primary source (the Act, Notification, or Circular).

**Requirements to enter:** Passed `peer_reviewed` AND:
- The legal citation (act, section, proviso, finance_act) has been verified against the official text
- If a notification or circular is cited, the document has been located and the rule text matches
- The reviewer confirms the authority is currently in force for the declared assessment_years

**Who performs legal review:** The repository owner, a qualified CA, or a documented trusted source. This is not an automated check.

**What the AI does:** Still ignores — never retrieves `legal_reviewed` rules.

---

### 4. `active`

**What it means:** The rule is production-quality. It is retrieved by the AI, used in decisions, and trusted as ground truth.

**Requirements to enter:** Passed `legal_reviewed` AND:
- All test cases pass
- No known conflicts with other active rules
- A Change entry (CH-XXXX) documents the promotion

**What the AI does:** Retrieves and cites this rule. This is the only stage the AI uses.

**How to maintain:** Any modification to an active rule requires:
1. Creating a new version (increment version field)
2. Creating a CH-XXXX Change entry
3. Re-running all test cases
4. Passing peer review and legal review for the changed fields before the update goes live

---

### 5. `deprecated`

**What it means:** The rule no longer applies — the law it encodes has been removed, the provision has lapsed, or the AY it covered has passed and no updated version was created.

**Requirements to enter:** An active rule may be deprecated when:
- The Finance Act removes or materially changes the provision
- The sunset_date has been reached
- A newer version of the same rule exists and the old AY is closed

**What happens to dependent objects:** The dependency graph is consulted. All objects that referenced this rule are reviewed for impact.

**What the AI does:** Ignores deprecated rules. If the AI is asked about a deprecated provision, it must explicitly state the rule is deprecated and the effective dates.

---

### 6. `superseded`

**What it means:** The rule has been replaced by a newer rule that covers the same provision with updated logic. This is different from deprecated — the underlying law still exists, but the rule encoding it has changed enough to require a new rule ID.

**Requirements to enter:**
- A new rule (R-XXXX) must be `active` before the old rule is superseded
- The `superseded_by` field in the old rule must point to the new rule ID

**What the AI does:** Ignores superseded rules. If asked, it cites the replacement.

---

### 7. `archived`

**What it means:** The rule is retired from the active knowledge base. It is kept for historical audit but removed from the working rule set.

**When to archive:** When a deprecated or superseded rule has been out of active use for more than two Assessment Years, it may be archived. Archiving is a housekeeping action, not a legal one.

**Where archived rules go:** Moved to `rules/archived/AY-XXXX-XX/` — still valid JSON, still in version control, still referenceable from old cases.

---

## Lifecycle Metadata Fields

Every rule carries these lifecycle fields beyond the current `status`:

```json
{
  "status": "active",
  "lifecycle_stage": "active",
  "peer_reviewed_by": "Contributor name or GitHub handle",
  "peer_reviewed_date": "2026-06-26",
  "legal_reviewed_by": "Reviewer name",
  "legal_reviewed_date": "2026-06-26",
  "legal_source_verified": true,
  "deprecated_date": null,
  "archived_date": null,
  "superseded_by": null
}
```

These fields are optional in the current schema but **required before a rule can be marked `active`** as per this document.

---

## Review Checklist (Peer Review)

Copy this into every PR that promotes a rule from `draft` to `peer_reviewed`:

```
Rule ID: R-XXXX
Reviewer:
Date:

[ ] Rule ID follows R-XXXX format and is next in sequence
[ ] Title is ≤ 120 characters and descriptive
[ ] Logic.if and logic.then are unambiguous
[ ] Authority fields are complete (act, section minimum)
[ ] Effective date matches the Finance Act cited
[ ] At least one test case exists and covers the core condition
[ ] At least one test case covers a disqualifying / negative condition
[ ] Evidence refs point to valid E-XXX entries
[ ] Decision refs point to valid D-XXX entries
[ ] No conflict with any existing active rule
[ ] Tags are consistent with existing taxonomy
[ ] File validates against schemas/rule-schema.json
```

## Review Checklist (Legal Review)

```
Rule ID: R-XXXX
Legal Reviewer:
Date:
Source document consulted:

[ ] Act name is correct
[ ] Section number is correct and currently exists in the Act
[ ] Proviso or sub-section cited (if any) exists in the section
[ ] Finance Act reference is correct for the amendment cited
[ ] Effective_from date matches the commencement date of the Finance Act
[ ] Rule text accurately reflects the legal provision (not a paraphrase that changes meaning)
[ ] Assessment years declared are correct for this provision
[ ] Any CBDT notification or circular cited exists and is correctly described
```

---

## Conflict Detection

Before any rule is promoted to `active`, the contributor must confirm no conflict exists with existing active rules by checking:

1. Do any other rules produce a contradictory outcome for the same input conditions?
2. Do any other rules reference the same legal section with different logic?

If a conflict is found, it must be resolved at the rule level before promotion — not left to the AI to resolve at runtime.

---

*Document Version: 1.0.0*
*Effective: 2026-06-26*
