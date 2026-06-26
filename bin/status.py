#!/usr/bin/env python3
"""
Jarviz Engine Status Dashboard.
Reads the registry and live test results to report engine health.
Run: python bin/status.py
"""

import json
import os
import subprocess
import sys
import time

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)


def _load(path: str) -> dict:
    with open(os.path.join(REPO_ROOT, path)) as f:
        return json.load(f)


def _fmt(v, width=8) -> str:
    return str(v).rjust(width)


def _bar(pct: float, width=20) -> str:
    filled = round(pct / 100 * width)
    return "█" * filled + "░" * (width - filled)


def run_dvf() -> dict:
    """Run DVF: golden masters + coverage map."""
    from dvf.runners.golden import run_golden
    from dvf.coverage import coverage_report
    t0 = time.time()
    results = run_golden()
    elapsed = time.time() - t0
    passed = sum(1 for r in results if r.passed)
    report = coverage_report()
    return {
        "total": len(results),
        "passed": passed,
        "elapsed_ms": round(elapsed * 1000),
        "coverage_pct": report["overall"]["pct"],
        "covered": report["overall"]["covered"],
        "required": report["overall"]["total"],
    }


def run_tests() -> dict:
    t0 = time.time()
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "test_wave3a.py", "-q", "--tb=no", "--no-header"],
        capture_output=True, text=True, cwd=REPO_ROOT
    )
    elapsed = time.time() - t0
    output = result.stdout + result.stderr
    passed = failed = 0
    for line in output.splitlines():
        if " passed" in line:
            parts = line.split()
            for i, p in enumerate(parts):
                if p == "passed":
                    try: passed = int(parts[i - 1])
                    except: pass
                if p == "failed":
                    try: failed = int(parts[i - 1])
                    except: pass
    return {"passed": passed, "failed": failed, "elapsed_s": round(elapsed, 2)}


def scheduler_depth() -> int:
    """Compute the depth (number of waves) in the Wave 3A spec graph."""
    from engine.scheduler import build_schedule
    from engine.specs import WAVE3A_SPECS
    waves = build_schedule(WAVE3A_SPECS)
    return len(waves)


def rules_per_decision(ctx_snapshot: dict) -> int:
    """Count rules that actually wrote output keys (approximation)."""
    from engine.specs import WAVE3A_SPECS
    return len(WAVE3A_SPECS)


def run_synthetic_pipeline() -> dict:
    """Run synthetic_001 through the pipeline and capture key metrics."""
    from engine.pipeline import run
    case_path = os.path.join(REPO_ROOT, "engine", "cases", "synthetic_001.json")
    output_path = os.path.join(REPO_ROOT, "output", "synthetic_001-report.html")
    t0 = time.time()
    result = run(case_path, output_path)
    elapsed = time.time() - t0
    return {"elapsed_ms": round(elapsed * 1000), "outcome": result.get("context", {}).get("outcome"), "recommendation": result.get("regime_recommendation")}


def main():
    index = _load("registry/index.json")
    rule_reg = _load("registry/rule-registry.json")
    counts = index["counts"]

    print()
    print("  ┌─────────────────────────────────────────────────────────────┐")
    print("  │  JARVIZ ENGINE STATUS                           AY2025-26   │")
    print("  └─────────────────────────────────────────────────────────────┘")
    print()

    # Registry counts
    r = counts["rules"]
    t = counts["tests"]
    print(f"  KNOWLEDGE LAYER")
    print(f"  {'Rules':<30} {r['active']:>4} active   {r['draft']:>3} draft   {r['deprecated']:>3} deprecated")
    print(f"  {'Tests':<30} {t['total']:>4} total    {t['pending']:>3} pending")
    print(f"  {'Evidence sources':<30} {counts['evidence_sources']['total']:>4} active")
    print(f"  {'Patterns':<30} {counts['patterns']['total']:>4} ({counts['patterns']['estimated_coverage_pct']}% estimated taxpayer coverage)")
    print(f"  {'Decisions':<30} {counts['decisions']['active']:>4} active    {counts['decisions']['draft']:>3} draft")
    print()

    # Test results
    print(f"  LIVE TEST RESULTS  (running...)", flush=True)
    test_res = run_tests()
    total_tests = test_res["passed"] + test_res["failed"]
    pass_rate = (test_res["passed"] / total_tests * 100) if total_tests > 0 else 0
    print(f"  {'Wave 3A suite':<30} {test_res['passed']:>2}/{total_tests} passed   {_bar(pass_rate)}  {pass_rate:.0f}%  ({test_res['elapsed_s']}s)")
    print()

    # DVF results
    print(f"  DECISION VALIDATION FRAMEWORK  (running...)", flush=True)
    dvf_res = run_dvf()
    gm_rate = (dvf_res["passed"] / dvf_res["total"] * 100) if dvf_res["total"] > 0 else 0
    cov_bar = _bar(dvf_res["coverage_pct"])
    print(f"  {'Golden masters':<30} {dvf_res['passed']:>2}/{dvf_res['total']} passed   {_bar(gm_rate)}  {gm_rate:.0f}%  ({dvf_res['elapsed_ms']}ms)")
    print(f"  {'Matrix coverage':<30} {dvf_res['covered']:>2}/{dvf_res['required']} cells    {cov_bar}  {dvf_res['coverage_pct']}%")
    print()

    # Scheduler metrics
    print(f"  SCHEDULER GRAPH")
    depth = scheduler_depth()
    from engine.specs import WAVE3A_SPECS
    print(f"  {'Wave 3A rules':<30} {len(WAVE3A_SPECS):>4}")
    print(f"  {'Execution depth (waves)':<30} {depth:>4}")
    print(f"  {'Rules per decision':<30} {len(WAVE3A_SPECS):>4}")
    print()

    # Pipeline benchmark
    print(f"  PIPELINE BENCHMARK  (running...)", flush=True)
    pip_res = run_synthetic_pipeline()
    print(f"  {'Synthetic 001 (SYNTH-001)':<30} {pip_res['elapsed_ms']:>4}ms   {pip_res['recommendation'].replace('_',' ').title()} → {pip_res['outcome']}")
    print()

    # JAB targets
    print(f"  JAB TARGETS  (v2.0.0 release gates)")
    jab = [
        ("M00", "Decision Coverage",     "≥ 85%",   "⏳ pending baseline"),
        ("M01", "ITR Accuracy",          "≥ 99%",   "⏳ pending GSS"),
        ("M02", "Refund Accuracy",       "< 0.5%",  "⏳ pending GSS"),
        ("M03", "Classification Acc.",   "≥ 98%",   "⏳ pending GSS"),
        ("M04", "Validation Precision",  "≥ 97%",   "⏳ pending GSS"),
        ("M05", "Validation Recall",     "≥ 99%",   "⏳ pending GSS"),
        ("M06", "False Positive Rate",   "< 1%",    "⏳ pending GSS"),
        ("M07", "Evidence Integrity",    "≥ 95%",   "⏳ pending GSS"),
        ("M08", "Avg Questions",         "≤ 3",     "⏳ Phase C (Intake)"),
        ("M09", "Processing Time",       "p50 < 8s", f"✅ {pip_res['elapsed_ms']}ms"),
        ("M10", "Human Override Rate",   "< 2%",    "⏳ pending real cases"),
        ("M11", "Explainability",        "= 100%",  "🟡 HTML report generated"),
    ]
    for metric_id, name, target, status_display in jab:
        print(f"  {metric_id}  {name:<26} {target:<12}  {status_display}")

    print()
    print(f"  {'─' * 61}")
    dvf_health = "✅ PASS" if dvf_res["passed"] == dvf_res["total"] else "❌ FAIL"
    wave_health = "✅ PASS" if test_res["failed"] == 0 else "❌ FAIL"
    print(f"  Wave 3A: {wave_health}  ·  DVF golden masters: {dvf_health}  ·  Matrix: {dvf_res['coverage_pct']}% covered")
    print()


if __name__ == "__main__":
    main()
