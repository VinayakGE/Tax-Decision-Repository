#!/usr/bin/env python3
"""
Jarviz Instrument Panel — AY2025-26
Four sections: Repository Health, Decision Quality, Product Readiness, Business Validation.
Schema is frozen. Only values change going forward.
Run: python bin/status.py
"""

import json
import os
import subprocess
import sys
import time

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

# ── Manually-updated targets (schema frozen; update values as work progresses) ──

RULES_TARGET        = 200
GM_TARGET           = 500
REAL_CASES_TARGET   = 100
CA_FIRMS_TARGET     = 20
PAYING_USERS_TARGET = 50
PARSERS_TOTAL       = 6
PARSERS_DONE        = 2   # manual + AIS (Form16 is scaffolded)

# Business validation — updated manually as milestones are reached
BUSINESS = {
    "ca_firms_interviewed":       0,
    "real_taxpayers_processed":   0,
    "paying_users":               0,
    "customer_satisfaction":     "—",
    "bug_escape_rate":           "—",
}

# Product readiness — updated manually each wave
PRODUCT = {
    "wave_3a":         "Complete",
    "wave_3b":         "Not Started",
    "parser_framework":"Ready",
    "real_parser":     "Not Started",
    "real_cases":      0,
    "closed_beta":     "Not Started",
    "public_mvp":      "Target: 4–5 months",
}


# ── Live metrics ───────────────────────────────────────────────────────────────

def _load(path: str) -> dict:
    with open(os.path.join(REPO_ROOT, path)) as f:
        return json.load(f)


def _row(label: str, value: str, width: int = 32) -> str:
    return f"  {label:<{width}} {value}"


def _pct(n: int, d: int) -> float:
    return round(100 * n / d, 1) if d else 0.0


def run_all_tests() -> dict:
    t0 = time.time()
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "test_wave3a.py", "test_dvf.py",
         "-q", "--tb=no", "--no-header"],
        capture_output=True, text=True, cwd=REPO_ROOT
    )
    elapsed = time.time() - t0
    output = result.stdout + result.stderr
    passed = failed = 0
    for line in output.splitlines():
        parts = line.split()
        for i, p in enumerate(parts):
            if p == "passed":
                try: passed = int(parts[i - 1])
                except: pass
            if p == "failed":
                try: failed = int(parts[i - 1])
                except: pass
    return {"passed": passed, "failed": failed, "elapsed_s": round(elapsed, 2)}


def run_pipeline() -> dict:
    from engine.pipeline import run
    case_path = os.path.join(REPO_ROOT, "engine", "cases", "synthetic_001.json")
    output_path = os.path.join(REPO_ROOT, "output", "synthetic_001-report.html")
    t0 = time.time()
    try:
        run(case_path, output_path)
        elapsed_ms = round((time.time() - t0) * 1000)
        return {"ok": True, "elapsed_ms": elapsed_ms}
    except Exception as e:
        return {"ok": False, "elapsed_ms": 0, "error": str(e)}


def run_golden() -> dict:
    from dvf.runners.golden import run_golden as _rg
    from dvf.coverage import coverage_report
    t0 = time.time()
    results = _rg()
    elapsed_ms = round((time.time() - t0) * 1000)
    passed = sum(1 for r in results if r.passed)
    report = coverage_report()
    return {
        "total": len(results),
        "passed": passed,
        "elapsed_ms": elapsed_ms,
        "decision_coverage_pct": report["overall"]["pct"],
        "covered_cells": report["overall"]["covered"],
        "required_cells": report["overall"]["total"],
    }


def scheduler_info() -> dict:
    from engine.scheduler import build_schedule
    from engine.specs import WAVE3A_SPECS
    waves = build_schedule(WAVE3A_SPECS)
    return {"depth": len(waves), "rules": len(WAVE3A_SPECS)}


def compute_rci(active_rules: int, tests_passed: int, tests_total: int,
                gm_passed: int, real_cases: int) -> dict:
    """Repository Confidence Index — 5 equal-weight components, each 0–100."""
    knowledge   = _pct(active_rules, RULES_TARGET)
    rule_tests  = _pct(tests_passed, tests_total) if tests_total else 0.0
    gm_cov      = _pct(gm_passed, GM_TARGET)
    mutation    = 100.0   # 4/4 mutations detected; update if new blind spots found
    real_val    = _pct(real_cases, REAL_CASES_TARGET)
    score       = round((knowledge + rule_tests + gm_cov + mutation + real_val) / 5, 1)
    return {
        "score": score,
        "knowledge": knowledge,
        "rule_tests": rule_tests,
        "gm_cov": gm_cov,
        "mutation": mutation,
        "real_val": real_val,
    }


# ── Rendering ──────────────────────────────────────────────────────────────────

def _section(title: str) -> None:
    print(f"\n  {title}")
    print(f"  {'─' * 55}")


def main():
    index  = _load("registry/index.json")
    counts = index["counts"]
    r      = counts["rules"]

    print()
    print("  ┌─────────────────────────────────────────────────────────────┐")
    print("  │  JARVIZ INSTRUMENT PANEL                        AY2025-26   │")
    print("  └─────────────────────────────────────────────────────────────┘")

    # Live collections — run once, used across sections
    print("\n  Collecting live metrics...", end="", flush=True)
    test_res  = run_all_tests()
    pip_res   = run_pipeline()
    gm_res    = run_golden()
    sched     = scheduler_info()
    print(" done.")

    tests_total  = test_res["passed"] + test_res["failed"]
    pipeline_ok  = pip_res["ok"]

    # ── 1. Repository Health ─────────────────────────────────────────────────
    _section("1. REPOSITORY HEALTH")
    print(_row("Active rules",    f"{r['active']} / {RULES_TARGET}"))
    print(_row("Tests",           f"{test_res['passed']} / {tests_total} passing   ({test_res['elapsed_s']}s)"))
    print(_row("Golden masters",  f"{gm_res['passed']} / {GM_TARGET}"))
    print(_row("Pipeline",        "PASS" if pipeline_ok else f"FAIL — {pip_res.get('error','')}"))
    print(_row("Scheduler depth", f"{sched['depth']} waves"))
    print(_row("Avg runtime",     f"{gm_res['elapsed_ms']} ms  (4 GMs)"))

    # ── 2. Decision Quality ──────────────────────────────────────────────────
    _section("2. DECISION QUALITY")
    knowledge_pct = _pct(r['active'], RULES_TARGET)
    print(_row("Decision coverage",  f"{gm_res['decision_coverage_pct']}%  ({gm_res['covered_cells']}/{gm_res['required_cells']} required cells)"))
    print(_row("Knowledge coverage", f"{knowledge_pct}%  ({r['active']}/{RULES_TARGET} rules)"))
    print(_row("Parser coverage",    f"{PARSERS_DONE} / {PARSERS_TOTAL}"))
    print(_row("Evidence integrity", "Pending  (JAB M-07)"))
    print(_row("Decision accuracy",  "Pending  (JAB — needs GSS)"))

    # ── 3. Product Readiness ─────────────────────────────────────────────────
    _section("3. PRODUCT READINESS")
    print(_row("Wave 3A",          PRODUCT["wave_3a"]))
    print(_row("Wave 3B",          PRODUCT["wave_3b"]))
    print(_row("Parser framework", PRODUCT["parser_framework"]))
    print(_row("Real parser",      PRODUCT["real_parser"]))
    print(_row("Real cases",       f"{PRODUCT['real_cases']} / {REAL_CASES_TARGET}"))
    print(_row("Closed beta",      PRODUCT["closed_beta"]))
    print(_row("Public MVP",       PRODUCT["public_mvp"]))

    # ── 4. Business Validation ───────────────────────────────────────────────
    _section("4. BUSINESS VALIDATION")
    print(_row("CA firms interviewed",      f"{BUSINESS['ca_firms_interviewed']} / {CA_FIRMS_TARGET}"))
    print(_row("Real taxpayers processed",  f"{BUSINESS['real_taxpayers_processed']} / {REAL_CASES_TARGET}"))
    print(_row("Paying users",              f"{BUSINESS['paying_users']} / {PAYING_USERS_TARGET}"))
    print(_row("Customer satisfaction",     BUSINESS["customer_satisfaction"]))
    print(_row("Bug escape rate",           BUSINESS["bug_escape_rate"]))

    # ── RCI ──────────────────────────────────────────────────────────────────
    rci = compute_rci(
        active_rules  = r["active"],
        tests_passed  = test_res["passed"],
        tests_total   = tests_total,
        gm_passed     = gm_res["passed"],
        real_cases    = BUSINESS["real_taxpayers_processed"],
    )
    _section("REPOSITORY CONFIDENCE INDEX")
    print(_row("Knowledge coverage",   f"{rci['knowledge']:>5.1f} / 100   ({r['active']}/{RULES_TARGET} rules)"))
    print(_row("Rule test coverage",   f"{rci['rule_tests']:>5.1f} / 100   ({test_res['passed']}/{tests_total} tests passing)"))
    print(_row("Golden master coverage",f"{rci['gm_cov']:>5.1f} / 100   ({gm_res['passed']}/{GM_TARGET} masters)"))
    print(_row("Mutation detection",   f"{rci['mutation']:>5.1f} / 100   (4/4 mutations caught)"))
    print(_row("Real case validation", f"{rci['real_val']:>5.1f} / 100   ({BUSINESS['real_taxpayers_processed']}/{REAL_CASES_TARGET} cases)"))
    print()
    print(f"  {'RCI':<32} {rci['score']:>5.1f} / 100")

    print()
    print(f"  {'═' * 55}")
    health = "✅ HEALTHY" if (pipeline_ok and test_res["failed"] == 0 and gm_res["passed"] == gm_res["total"]) else "⚠️  DEGRADED"
    print(f"  {health}   RCI {rci['score']}   Tests {test_res['passed']}/{tests_total}   GMs {gm_res['passed']}/{gm_res['total']}")
    print()


if __name__ == "__main__":
    main()
