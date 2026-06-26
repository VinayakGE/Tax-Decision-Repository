"""
Coverage map — shows which required matrix cells are covered by golden masters,
which are pending, and per-dimension coverage percentages.
"""

from collections import defaultdict
from dvf.generator.matrix import DIMENSIONS, REQUIRED_COVERAGE, GM_COVERAGE_MAP, coverage_status


def coverage_report() -> dict:
    """
    Returns a structured coverage report:
    - overall: {covered, total, pct}
    - by_dimension: {dim_name: {value: {covered, total}}}
    - covered_cells: list of MatrixCell
    - pending_cells: list of MatrixCell
    - gm_ids: mapping gm_id -> MatrixCell
    """
    status = coverage_status()
    covered_cells = status["covered"]
    pending_cells = status["pending"]

    total = len(REQUIRED_COVERAGE)
    n_covered = len(covered_cells)

    # Per-dimension breakdown
    by_dim: dict = {}
    for dim in DIMENSIONS:
        counts: dict = {v: {"covered": 0, "total": 0} for v in dim.values}
        for cell in REQUIRED_COVERAGE:
            val = getattr(cell, dim.name)
            counts[val]["total"] += 1
        for cell in covered_cells:
            val = getattr(cell, dim.name)
            counts[val]["covered"] += 1
        by_dim[dim.name] = counts

    return {
        "overall": {
            "covered": n_covered,
            "total": total,
            "pct": round(100 * n_covered / total) if total else 0,
        },
        "by_dimension": by_dim,
        "covered_cells": covered_cells,
        "pending_cells": pending_cells,
        "gm_ids": GM_COVERAGE_MAP,
    }


def print_coverage() -> None:
    """Print a human-readable coverage table to stdout."""
    report = coverage_report()
    ov = report["overall"]
    print(f"\nDecision Validation Coverage: {ov['covered']}/{ov['total']} required cells ({ov['pct']}%)")
    print()

    for dim_name, counts in report["by_dimension"].items():
        total_vals = sum(c["total"] for c in counts.values())
        if total_vals == 0:
            continue
        covered_vals = sum(c["covered"] for c in counts.values())
        print(f"  {dim_name}: {covered_vals}/{total_vals}")
        for val, c in counts.items():
            if c["total"] == 0:
                continue
            mark = "✓" if c["covered"] == c["total"] else ("~" if c["covered"] > 0 else "·")
            print(f"    {mark} {val}: {c['covered']}/{c['total']}")
    print()

    print("  Covered GMs:")
    for gm_id, cell in report["gm_ids"].items():
        print(f"    {gm_id}  {cell.income_type}/{cell.age_bracket}/{cell.income_level}")
    print()

    if report["pending_cells"]:
        print("  Pending cells (no GM yet):")
        for cell in report["pending_cells"]:
            print(f"    · {cell.income_type}/{cell.age_bracket}/{cell.income_level}/{cell.regime}/{cell.has_special_items}/{cell.filing_timing}")
    print()


if __name__ == "__main__":
    print_coverage()
