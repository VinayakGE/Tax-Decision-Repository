"""
Coverage matrix — n-dimensional parameter space for synthetic case generation.
Each dimension is a list of values. The matrix describes the full test space;
actual golden masters cover a subset of it.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Dimension:
    name: str
    values: List[str]
    description: str


@dataclass(frozen=True)
class MatrixCell:
    """One point in the coverage matrix."""
    income_type: str
    age_bracket: str
    income_level: str
    regime: str
    has_special_items: str    # "none", "ltcg", "stcg", "lottery"
    filing_timing: str


# The full coverage space
DIMENSIONS = [
    Dimension(
        name="income_type",
        values=["salary_only", "salary_fd", "salary_ltcg", "salary_business", "salary_hp", "business_only"],
        description="Primary income composition",
    ),
    Dimension(
        name="age_bracket",
        values=["general", "senior", "super_senior"],
        description="Taxpayer age determines old regime slab schedule",
    ),
    Dimension(
        name="income_level",
        values=["below_5L", "5L_to_7L", "7L_to_12L", "above_12L_to_15L", "above_15L_to_50L", "above_50L"],
        description="Income brackets relative to key tax thresholds",
    ),
    Dimension(
        name="regime",
        values=["new_regime", "old_regime", "compare"],
        description="Regime chosen or comparison mode",
    ),
    Dimension(
        name="has_special_items",
        values=["none", "ltcg_112A", "stcg_111A", "lottery_115BB"],
        description="Special-rate income items",
    ),
    Dimension(
        name="filing_timing",
        values=["on_time", "late"],
        description="Filing before or after due date (affects 234A interest)",
    ),
]


# Minimum coverage targets: the cells that MUST have at least one golden master
REQUIRED_COVERAGE = [
    MatrixCell("salary_only",    "general",    "7L_to_12L",       "new_regime", "none",     "on_time"),  # GM-0001
    MatrixCell("salary_only",    "general",    "above_12L_to_15L","new_regime", "none",     "on_time"),  # GM-0002
    MatrixCell("salary_only",    "senior",     "below_5L",        "new_regime", "none",     "on_time"),  # GM-0003
    MatrixCell("business_only",  "general",    "above_12L_to_15L","new_regime", "none",     "on_time"),  # GM-0004
    MatrixCell("salary_only",    "general",    "7L_to_12L",       "old_regime", "none",     "on_time"),  # GM-0005
    # These are targets — golden masters don't exist yet
    MatrixCell("salary_only",    "super_senior","below_5L",       "new_regime", "none",     "on_time"),
    MatrixCell("salary_ltcg",    "general",    "above_12L_to_15L","new_regime", "ltcg_112A","on_time"),
    MatrixCell("salary_only",    "general",    "above_50L",       "new_regime", "none",     "on_time"),
    MatrixCell("salary_only",    "general",    "7L_to_12L",       "new_regime", "none",     "late"),
    MatrixCell("salary_fd",      "general",    "7L_to_12L",       "old_regime", "none",     "on_time"),
    MatrixCell("salary_business","general",    "above_15L_to_50L","new_regime", "none",     "on_time"),
]

# Map GM IDs to matrix cells (for coverage tracking)
GM_COVERAGE_MAP = {
    "GM-0001": MatrixCell("salary_only",   "general", "7L_to_12L",        "new_regime", "none", "on_time"),
    "GM-0002": MatrixCell("salary_only",   "general", "above_12L_to_15L", "new_regime", "none", "on_time"),
    "GM-0003": MatrixCell("salary_only",   "senior",  "below_5L",         "new_regime", "none", "on_time"),
    "GM-0004": MatrixCell("business_only", "general", "above_12L_to_15L", "new_regime", "none", "on_time"),
    "GM-0005": MatrixCell("salary_only",   "general", "7L_to_12L",        "old_regime", "none", "on_time"),
}


def coverage_status() -> dict:
    """Returns which required cells are covered vs pending."""
    covered = set(GM_COVERAGE_MAP.values())
    return {
        "covered": [c for c in REQUIRED_COVERAGE if c in covered],
        "pending": [c for c in REQUIRED_COVERAGE if c not in covered],
    }
