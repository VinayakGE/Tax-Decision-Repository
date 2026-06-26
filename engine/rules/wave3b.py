"""
Wave 3B — Tax Adjustment Engine.
Deductions reduce taxable income under Chapter VI-A (old regime).
Each rule is responsible for exactly one deduction section.

Execution order (managed by scheduler):
  R-0024  80C investments          → deduction_80C
  R-0039  80CCD(1B) NPS            → deduction_80CCD1B
  R-0035  80D evidence completeness → deduction_80d_evidence_status
  R-0036  80D self / family cap     → deduction_80d_self
  R-0037  80D parents cap           → deduction_80d_parents
  R-0038  80D total                 → deduction_80D
  R-0028  Deduction Aggregator      → taxable_income_old_regime  (final, used by R-0016)
"""

from engine.context import EvidenceContext
from engine import tables


# ---------------------------------------------------------------------------
# R-0024: Section 80C — Investments and Savings
# ---------------------------------------------------------------------------

def r0024_deduction_80c(ctx: EvidenceContext) -> None:
    """
    Compute 80C deduction from eligible investment declarations.
    Available under old regime only. Aggregate cap ₹1.5L across all instruments.
    """
    regime = ctx.get("regime_chosen", "new_regime")

    if regime != "old_regime":
        ctx.set("deduction_80C", 0)
        return

    investments = ctx.get("investments_80C", 0) or 0
    limit = tables.get("2024.deductions.chapter_via.80C.limit")  # 150000

    deduction = min(int(investments), limit)
    ctx.update({
        "deduction_80C": deduction,
        "deduction_80C_investments_declared": int(investments),
        "deduction_80C_cap": limit,
        "deduction_80C_capped": investments > limit,
    })


# ---------------------------------------------------------------------------
# R-0028: Deduction Aggregator — Chapter VI-A (old regime)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# R-0039: Section 80CCD(1B) — Additional NPS Contribution
# ---------------------------------------------------------------------------

def r0039_deduction_80ccd1b(ctx: EvidenceContext) -> None:
    """
    80CCD(1B): employee's own additional NPS contribution beyond the ₹1.5L 80C aggregate.
    Old regime only — Section 115BAC(2) excludes this from the new regime.
    Separate ₹50K ceiling that stacks on top of 80C.
    """
    regime = ctx.get("regime_chosen", "new_regime")

    if regime != "old_regime":
        ctx.set("deduction_80CCD1B", 0)
        return

    contribution = ctx.get("nps_contribution_80ccd1b", 0) or 0
    limit = tables.get("2024.deductions.chapter_via.80CCD_1B.limit")  # 50000

    deduction = min(int(contribution), limit)
    ctx.update({
        "deduction_80CCD1B": deduction,
        "deduction_80CCD1B_declared": int(contribution),
        "deduction_80CCD1B_cap": limit,
        "deduction_80CCD1B_capped": contribution > limit,
    })


# ---------------------------------------------------------------------------
# R-0035: Section 80D — Evidence Completeness
# ---------------------------------------------------------------------------

def r0035_80d_evidence_completeness(ctx: EvidenceContext) -> None:
    """
    Check completeness of 80D health insurance premium evidence.
    Uses age_bracket (taxpayer) and parent_age_bracket to determine applicable limits.
    """
    regime = ctx.get("regime_chosen", "new_regime")

    if regime != "old_regime":
        ctx.set("deduction_80d_evidence_status", {
            "status": "NOT_APPLICABLE",
            "reason": "80D deductions not available under new regime",
            "missing_fields": [],
            "suggested_questions": [],
        })
        return

    self_premium = ctx.get("deduction_80d_self_premium")
    parents_premium = ctx.get("deduction_80d_parents_premium")

    has_self = self_premium is not None and int(self_premium) > 0
    has_parents = parents_premium is not None and int(parents_premium) > 0

    if not has_self and not has_parents:
        ctx.set("deduction_80d_evidence_status", {
            "status": "NOT_APPLICABLE",
            "reason": "No 80D health insurance premium declared",
            "missing_fields": [],
            "suggested_questions": [],
        })
        return

    missing = []
    suggested = []

    if has_self and not ctx.get("age_bracket"):
        missing.append("age_bracket")
        suggested.append("What is the taxpayer's age bracket? (below_60 or senior)")

    if has_parents and not ctx.get("parent_age_bracket"):
        missing.append("parent_age_bracket")
        suggested.append("What is the parents' age bracket? (below_60 or senior)")

    if missing:
        ctx.set("deduction_80d_evidence_status", {
            "status": "INCOMPLETE",
            "missing_fields": missing,
            "suggested_questions": suggested,
        })
    else:
        ctx.set("deduction_80d_evidence_status", {
            "status": "COMPLETE",
            "missing_fields": [],
            "suggested_questions": [],
        })


# ---------------------------------------------------------------------------
# R-0036: Section 80D — Self / Family Cap
# ---------------------------------------------------------------------------

def r0036_80d_self_cap(ctx: EvidenceContext) -> None:
    """
    Apply the self/family health insurance cap.
    below_60 → ₹25K; senior/super_senior → ₹50K.
    """
    status_obj = ctx.get("deduction_80d_evidence_status") or {}
    if status_obj.get("status") != "COMPLETE":
        ctx.set("deduction_80d_self", 0)
        return

    self_premium = ctx.get("deduction_80d_self_premium") or 0
    age_bracket = ctx.get("age_bracket", "general")

    if age_bracket in ("senior", "super_senior"):
        limit = tables.get("2024.deductions.chapter_via.80D.self_senior.limit")
    else:
        limit = tables.get("2024.deductions.chapter_via.80D.self_below_60.limit")

    ctx.set("deduction_80d_self", min(int(self_premium), limit))


# ---------------------------------------------------------------------------
# R-0037: Section 80D — Parents Cap
# ---------------------------------------------------------------------------

def r0037_80d_parents_cap(ctx: EvidenceContext) -> None:
    """
    Apply the parents' health insurance cap.
    below_60 → ₹25K; senior → ₹50K.
    """
    status_obj = ctx.get("deduction_80d_evidence_status") or {}
    if status_obj.get("status") != "COMPLETE":
        ctx.set("deduction_80d_parents", 0)
        return

    parents_premium = ctx.get("deduction_80d_parents_premium") or 0
    parent_age_bracket = ctx.get("parent_age_bracket", "below_60")

    if parent_age_bracket == "senior":
        limit = tables.get("2024.deductions.chapter_via.80D.parents_senior.limit")
    else:
        limit = tables.get("2024.deductions.chapter_via.80D.parents_below_60.limit")

    ctx.set("deduction_80d_parents", min(int(parents_premium), limit))


# ---------------------------------------------------------------------------
# R-0038: Section 80D — Total (aggregate cap)
# ---------------------------------------------------------------------------

def r0038_80d_total(ctx: EvidenceContext) -> None:
    """
    Sum self + parents deductions and apply aggregate cap (₹1L).
    """
    status_obj = ctx.get("deduction_80d_evidence_status") or {}
    if status_obj.get("status") != "COMPLETE":
        ctx.set("deduction_80D", 0)
        return

    d_self = ctx.get("deduction_80d_self", 0) or 0
    d_parents = ctx.get("deduction_80d_parents", 0) or 0
    max_total = tables.get("2024.deductions.chapter_via.80D.max_total")

    ctx.set("deduction_80D", min(d_self + d_parents, max_total))


# ---------------------------------------------------------------------------
# R-0028: Deduction Aggregator — Chapter VI-A (old regime)
# ---------------------------------------------------------------------------

def r0028_deduction_aggregator(ctx: EvidenceContext) -> None:
    """
    Sum all Chapter VI-A deductions and compute final old-regime taxable income.
    New regime taxable income is unaffected — it flows from R-0015 directly.

    Designed to grow: add new deduction keys to breakdown as rules are added.
    """
    pre = ctx.get("taxable_income_old_pre_deductions", 0) or 0

    d80c = ctx.get("deduction_80C", 0) or 0
    d80ccd1b = ctx.get("deduction_80CCD1B", 0) or 0
    d80d = ctx.get("deduction_80D", 0) or 0

    total = d80c + d80ccd1b + d80d
    taxable_old_final = max(0, pre - total)

    breakdown = {}
    if d80c:
        breakdown["80C"] = d80c
    if d80ccd1b:
        breakdown["80CCD1B"] = d80ccd1b
    if d80d:
        breakdown["80D"] = d80d

    ctx.update({
        "taxable_income_old_regime": taxable_old_final,
        "total_deductions_old": total,
        "deduction_breakdown": breakdown,
    })
