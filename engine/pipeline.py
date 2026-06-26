"""
Jarviz Pipeline — end-to-end: case file → executor → explanation → HTML report.

Usage:
    python -m engine.pipeline engine/cases/synthetic_001.json
    python -m engine.pipeline engine/cases/synthetic_001.json --output output/report.html
"""

import json
import os
import sys
import argparse

from engine.parsers.manual import ManualParser
from engine.executor import execute
from engine.specs import ALL_SPECS
from engine.explanation import explain
from engine.report import render_html


def run(case_path: str, output_path: str = None) -> dict:
    """
    Run the full pipeline for a case file.
    Returns a result dict with context snapshot, explanation, and output_path.
    """
    with open(case_path) as f:
        case = json.load(f)

    # Merge case-level evidence with taxpayer metadata
    evidence = dict(case.get("evidence", {}))
    taxpayer = case.get("taxpayer", {})
    if "age" in taxpayer and "taxpayer_age" not in evidence:
        evidence["taxpayer_age"] = taxpayer["age"]
    if "age_bracket" in taxpayer and "age_bracket" not in evidence:
        evidence["age_bracket"] = taxpayer["age_bracket"]
    evidence["case_id"] = case.get("case_id", "")
    evidence["taxpayer_name"] = taxpayer.get("name", "Taxpayer")

    # Parse evidence (passthrough — already structured)
    parser = ManualParser()
    evidence_obj = parser.parse(evidence)

    # Execute rules
    ctx = execute(ALL_SPECS, evidence_obj.evidence)

    # Generate explanation
    explanation = explain(ctx)

    # Generate HTML report
    html = render_html(explanation, ctx.snapshot())

    # Write report
    if output_path is None:
        case_stem = os.path.splitext(os.path.basename(case_path))[0]
        output_dir = os.path.join(os.path.dirname(case_path), "..", "..", "output")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{case_stem}-report.html")

    with open(output_path, "w") as f:
        f.write(html)

    return {
        "case_id": case.get("case_id"),
        "output_path": os.path.abspath(output_path),
        "regime_recommendation": explanation["regime_recommendation"],
        "summary": explanation["summary"],
        "context": ctx.snapshot(),
    }


def _print_result(result: dict) -> None:
    print(f"\n{'─' * 60}")
    print(f"  Case:        {result['case_id']}")
    print(f"  Regime:      {result['regime_recommendation'].replace('_', ' ').title()}")
    print(f"  Summary:     {result['summary']}")
    print(f"  Report:      {result['output_path']}")
    print(f"{'─' * 60}\n")


def main():
    parser = argparse.ArgumentParser(description="Jarviz Tax Decision Pipeline")
    parser.add_argument("case", help="Path to case JSON file")
    parser.add_argument("--output", help="Output HTML path (optional)")
    args = parser.parse_args()

    result = run(args.case, args.output)
    _print_result(result)


if __name__ == "__main__":
    main()
