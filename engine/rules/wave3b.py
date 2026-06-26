"""
Wave 3B — Tax Adjustment Engine.
Deductions reduce taxable income under Chapter VI-A (old regime).
Each rule is responsible for exactly one deduction section.

Execution order (managed by scheduler):
  R-0024  80C investments      → deduction_80C
  R-0028  Deduction Aggregator → taxable_income_old_regime  (final, used by R-0016)

R-0024 and R-0015 run in parallel (wave 1); R-0028 depends on both.
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

def r0028_deduction_aggregator(ctx: EvidenceContext) -> None:
    """
    Sum all Chapter VI-A deductions and compute final old-regime taxable income.
    New regime taxable income is unaffected — it flows from R-0015 directly.

    Designed to grow: add new deduction keys to breakdown as rules are added.
    """
    pre = ctx.get("taxable_income_old_pre_deductions", 0) or 0

    d80c = ctx.get("deduction_80C", 0) or 0
    # Future deductions plug in here (HRA via exemption, 80D, 80CCD_1B, etc.)

    total = d80c
    taxable_old_final = max(0, pre - total)

    breakdown = {}
    if d80c:
        breakdown["80C"] = d80c

    ctx.update({
        "taxable_income_old_regime": taxable_old_final,
        "total_deductions_old": total,
        "deduction_breakdown": breakdown,
    })
