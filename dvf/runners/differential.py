"""
Differential runner — compare two engine configurations against the same evidence.
Surfaces any output that changed between version A and version B of the specs.
Typical use: compare current branch vs main branch rule set.
"""

from dataclasses import dataclass
from typing import List, Dict, Any

from engine.parsers.manual import ManualParser
from engine.executor import execute
from dvf import DECISION_FIELDS


@dataclass
class DiffResult:
    case_id: str
    changed_fields: Dict[str, dict]  # {field: {"a": v, "b": v}}
    has_diff: bool


def run_diff(evidence_dict: dict, specs_a, specs_b, case_id: str = "diff") -> DiffResult:
    """
    Run the same evidence through two spec sets. Return field-level differences.
    """
    parser = ManualParser()
    ev = parser.parse(evidence_dict)

    ctx_a = execute(specs_a, dict(ev.evidence))
    ctx_b = execute(specs_b, dict(ev.evidence))

    snap_a = ctx_a.snapshot()
    snap_b = ctx_b.snapshot()

    all_keys = set(DECISION_FIELDS) | set(snap_a.keys()) | set(snap_b.keys())
    changed = {}
    for key in sorted(all_keys):
        va = snap_a.get(key)
        vb = snap_b.get(key)
        if va != vb:
            changed[key] = {"a": va, "b": vb}

    return DiffResult(case_id=case_id, changed_fields=changed, has_diff=bool(changed))


def run_golden_diff(specs_a, specs_b) -> List[DiffResult]:
    """
    Run differential against all golden master cases.
    """
    import json, os
    from dvf.runners.golden import GOLDEN_DIR

    results = []
    case_dirs = sorted(d for d in os.listdir(GOLDEN_DIR) if d.startswith("GM-"))
    for case_name in case_dirs:
        gm_dir = os.path.join(GOLDEN_DIR, case_name)
        input_path = os.path.join(gm_dir, "input.json")
        if not os.path.isfile(input_path):
            continue
        with open(input_path) as f:
            case = json.load(f)
        evidence = dict(case.get("evidence", {}))
        taxpayer = case.get("taxpayer", {})
        if "age" in taxpayer:
            evidence.setdefault("taxpayer_age", taxpayer["age"])
        if "age_bracket" in taxpayer:
            evidence.setdefault("age_bracket", taxpayer["age_bracket"])

        result = run_diff(evidence, specs_a, specs_b, case_id=case.get("case_id", case_name))
        results.append(result)

    return results
