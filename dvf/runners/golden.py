"""
Golden Master runner.
Loads each GM-XXXX case, runs the pipeline, and compares to expected.json.
A golden master fails if any DECISION_FIELDS value differs from the stored expected.
"""

import json
import os
from dataclasses import dataclass
from typing import List, Optional

from engine.parsers.manual import ManualParser
from engine.executor import execute
from engine.specs import WAVE3A_SPECS
from dvf import DECISION_FIELDS

GOLDEN_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "golden")


@dataclass
class GoldenResult:
    case_id: str
    passed: bool
    mismatches: List[str]
    coverage_tags: List[str]


def _load_case(gm_dir: str) -> Optional[dict]:
    input_path = os.path.join(gm_dir, "input.json")
    expected_path = os.path.join(gm_dir, "expected.json")
    metadata_path = os.path.join(gm_dir, "metadata.json")
    trace_path = os.path.join(gm_dir, "decision_trace.json")

    if not os.path.isfile(input_path) or not os.path.isfile(expected_path):
        return None

    with open(input_path) as f:
        case_input = json.load(f)
    with open(expected_path) as f:
        expected = json.load(f)
    metadata = {}
    if os.path.isfile(metadata_path):
        with open(metadata_path) as f:
            metadata = json.load(f)
    trace = {}
    if os.path.isfile(trace_path):
        with open(trace_path) as f:
            trace = json.load(f)

    return {
        "input": case_input,
        "expected": expected,
        "metadata": metadata,
        "stored_trace": trace,
    }


def _run_case(case_data: dict) -> tuple:
    """Run pipeline and return (context_snapshot, execution_trace)."""
    case_input = case_data["input"]
    evidence = dict(case_input.get("evidence", {}))
    taxpayer = case_input.get("taxpayer", {})
    if "age" in taxpayer:
        evidence.setdefault("taxpayer_age", taxpayer["age"])
    if "age_bracket" in taxpayer:
        evidence.setdefault("age_bracket", taxpayer["age_bracket"])
    evidence["case_id"] = case_input.get("case_id", "")
    evidence["taxpayer_name"] = taxpayer.get("name", "Taxpayer")

    parser = ManualParser()
    evidence_obj = parser.parse(evidence)
    ctx = execute(WAVE3A_SPECS, evidence_obj.evidence)
    return ctx.snapshot()


def run_golden(gm_id: str = None) -> List[GoldenResult]:
    """
    Run all golden masters (or a specific one if gm_id is given).
    Returns a list of GoldenResult objects.
    """
    if not os.path.isdir(GOLDEN_DIR):
        return []

    case_dirs = sorted(
        d for d in os.listdir(GOLDEN_DIR)
        if d.startswith("GM-") and (gm_id is None or d == gm_id)
    )

    results = []
    for case_name in case_dirs:
        gm_dir = os.path.join(GOLDEN_DIR, case_name)
        case_data = _load_case(gm_dir)
        if case_data is None:
            continue

        case_id = case_data["input"].get("case_id", case_name)
        expected = case_data["expected"]
        coverage_tags = case_data["metadata"].get("coverage_tags", [])

        try:
            snapshot = _run_case(case_data)
        except Exception as e:
            results.append(GoldenResult(
                case_id=case_id,
                passed=False,
                mismatches=[f"Pipeline error: {e}"],
                coverage_tags=coverage_tags,
            ))
            continue

        mismatches = []
        for field in DECISION_FIELDS:
            expected_val = expected.get(field)
            actual_val = snapshot.get(field)
            if expected_val != actual_val:
                mismatches.append(
                    f"{field}: expected {expected_val!r}, got {actual_val!r}"
                )

        # Structural check: verify execution depth hasn't changed unexpectedly
        stored_trace = case_data.get("stored_trace", {})
        if stored_trace:
            from engine.scheduler import build_schedule
            waves = build_schedule(WAVE3A_SPECS)
            actual_depth = len(waves)
            stored_depth = stored_trace.get("execution_depth", actual_depth)
            if actual_depth != stored_depth:
                mismatches.append(
                    f"execution_depth: expected {stored_depth}, got {actual_depth} — execution plan changed"
                )

        results.append(GoldenResult(
            case_id=case_id,
            passed=len(mismatches) == 0,
            mismatches=mismatches,
            coverage_tags=coverage_tags,
        ))

    return results
