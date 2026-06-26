"""
Golden Master generator.
Run: python dvf/generate.py
Reads each dvf/golden/GM-XXXX/input.json, runs the pipeline, and writes:
  - expected.json   (decision fields — the regression target)
  - decision_trace.json  (execution plan + rule outputs — structural regression)
  - metadata.json   (generation timestamp, description, coverage tags)
"""

import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.parsers.manual import ManualParser
from engine.executor import execute
from engine.specs import WAVE3A_SPECS
from engine.scheduler import build_schedule
from dvf import DECISION_FIELDS

GOLDEN_DIR = os.path.join(os.path.dirname(__file__), "golden")

# Coverage tags describe what each case exercises
CASE_COVERAGE = {
    "GM-0001": ["salary", "fd_interest", "87a_rebate_applies", "new_regime", "refund"],
    "GM-0002": ["salary", "87a_cliff", "no_rebate", "new_regime", "refund"],
    "GM-0003": ["salary", "senior_citizen", "87a_rebate_both_regimes", "zero_tax", "refund"],
    "GM-0004": ["business_income", "no_advance_tax", "234b", "234c", "demand", "new_regime"],
}


def _extract_decision_fields(ctx_snapshot: dict) -> dict:
    return {k: ctx_snapshot.get(k) for k in DECISION_FIELDS}


def _build_trace(waves, ctx_snapshot: dict) -> dict:
    """Capture execution plan and key outputs per rule."""
    schedule = [{"wave": i + 1, "rules": [s.rule_id for s in wave]} for i, wave in enumerate(waves)]
    execution_order = [s.rule_id for wave in waves for s in wave]

    rule_outputs = {}
    for wave in waves:
        for spec in wave:
            produced = {k: ctx_snapshot.get(k) for k in spec.produces if k in ctx_snapshot}
            rule_outputs[spec.rule_id] = produced

    return {
        "schedule": schedule,
        "execution_order": execution_order,
        "execution_depth": len(waves),
        "rules_executed": len(execution_order),
        "rule_outputs": rule_outputs,
    }


def generate_one(gm_dir: str) -> dict:
    input_path = os.path.join(gm_dir, "input.json")
    with open(input_path) as f:
        case = json.load(f)

    case_id = case.get("case_id", os.path.basename(gm_dir))
    evidence = dict(case.get("evidence", {}))
    taxpayer = case.get("taxpayer", {})
    if "age" in taxpayer:
        evidence.setdefault("taxpayer_age", taxpayer["age"])
    if "age_bracket" in taxpayer:
        evidence.setdefault("age_bracket", taxpayer["age_bracket"])
    evidence["case_id"] = case_id
    evidence["taxpayer_name"] = taxpayer.get("name", "Taxpayer")

    parser = ManualParser()
    evidence_obj = parser.parse(evidence)

    waves = build_schedule(WAVE3A_SPECS)
    ctx = execute(WAVE3A_SPECS, evidence_obj.evidence)
    snapshot = ctx.snapshot()

    expected = _extract_decision_fields(snapshot)
    trace = _build_trace(waves, snapshot)
    metadata = {
        "case_id": case_id,
        "description": case.get("description", ""),
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "engine_version": "1.0.0",
        "coverage_tags": CASE_COVERAGE.get(case_id, []),
        "source": "synthetic",
        "verified_by": "dvf/generate.py",
    }

    # Write files
    def _write(name, data):
        with open(os.path.join(gm_dir, name), "w") as f:
            json.dump(data, f, indent=2)

    _write("expected.json", expected)
    _write("decision_trace.json", trace)
    _write("metadata.json", metadata)

    return {"case_id": case_id, "outcome": expected.get("outcome"), "regime": expected.get("regime_recommendation")}


def main():
    if not os.path.isdir(GOLDEN_DIR):
        print(f"Golden dir not found: {GOLDEN_DIR}")
        sys.exit(1)

    cases = sorted(d for d in os.listdir(GOLDEN_DIR) if d.startswith("GM-"))
    print(f"\nGenerating {len(cases)} golden masters...\n")

    for case_name in cases:
        gm_dir = os.path.join(GOLDEN_DIR, case_name)
        if not os.path.isfile(os.path.join(gm_dir, "input.json")):
            continue
        result = generate_one(gm_dir)
        print(f"  {result['case_id']}  regime={result['regime']}  outcome={result['outcome']}")

    print(f"\nDone. Files written to dvf/golden/.\n")


if __name__ == "__main__":
    main()
