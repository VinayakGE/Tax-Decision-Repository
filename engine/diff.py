"""
Evidence Diff — computes field-level changes between two EvidenceContext snapshots.
Used for revised returns, updated documents, and DEL (Decision Execution Log) explanations.
"""

from dataclasses import dataclass
from typing import Any, List, Optional
from engine.context import EvidenceContext


@dataclass
class FieldChange:
    field: str
    before: Any
    after: Any
    delta: Optional[Any]        # numeric delta if both values are numeric, else None
    source: str                 # description of what changed
    effect: Optional[str]       # populated after re-execution diff


def diff_contexts(
    before: EvidenceContext,
    after: EvidenceContext,
    source: str = "Updated document",
) -> List[FieldChange]:
    """
    Returns a list of FieldChange objects for every key that changed between two snapshots.
    Only leaf-level scalar changes are reported; nested dict changes recurse one level.
    """
    changes = []
    before_snap = before.snapshot()
    after_snap = after.snapshot()

    all_keys = set(before_snap) | set(after_snap)

    for key in sorted(all_keys):
        v_before = before_snap.get(key)
        v_after = after_snap.get(key)
        if v_before == v_after:
            continue

        delta = None
        if isinstance(v_before, (int, float)) and isinstance(v_after, (int, float)):
            delta = v_after - v_before

        changes.append(FieldChange(
            field=key,
            before=v_before,
            after=v_after,
            delta=delta,
            source=source,
            effect=None,
        ))

    return changes


def annotate_effects(
    changes: List[FieldChange],
    before_outputs: EvidenceContext,
    after_outputs: EvidenceContext,
) -> List[FieldChange]:
    """
    After re-running the executor on both snapshots, annotates each FieldChange
    with the downstream effect on key tax outputs.
    """
    output_keys = [
        "total_tax_new_regime", "total_tax_old_regime",
        "refund_amount", "demand_amount", "taxable_income_new_regime",
    ]
    output_changes = diff_contexts(before_outputs, after_outputs, source="re-execution")
    output_delta = {c.field: c.delta for c in output_changes if c.delta is not None}

    for change in changes:
        effects = []
        for ok in output_keys:
            d = output_delta.get(ok)
            if d is not None and d != 0:
                sign = "+" if d > 0 else ""
                effects.append(f"{ok} {sign}{d:,.0f}")
        change.effect = "; ".join(effects) if effects else None

    return changes


def format_diff(changes: List[FieldChange]) -> str:
    """Human-readable diff report for logging or display."""
    if not changes:
        return "No evidence changes detected."
    lines = ["Evidence Diff:"]
    for c in changes:
        delta_str = f"  Δ {c.delta:+,.0f}" if c.delta is not None else ""
        effect_str = f"  → {c.effect}" if c.effect else ""
        lines.append(f"  {c.field}: {c.before!r} → {c.after!r}{delta_str}{effect_str}  [{c.source}]")
    return "\n".join(lines)
