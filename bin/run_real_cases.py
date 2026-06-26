#!/usr/bin/env python3
"""
Real-Case Validation Runner — AY2025-26

Runs the engine against anonymized real salary cases and compares output
against human-computed expected values.

This is the first bridge between synthetic confidence (GMs) and real-world
correctness. Cases live in cases/real/RC-*.json.

Usage:
  python bin/run_real_cases.py           # all cases
  python bin/run_real_cases.py RC-0002   # single case by ID

Output: per-field match/mismatch table + entity pressure summary.
"""

import json
import os
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.parsers.manual import ManualParser
from engine.executor import execute
from engine.specs import ALL_SPECS

CASES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cases", "real")
AMOUNT_TOLERANCE = 1  # ±₹1 rounding tolerance

_AMOUNT_FIELDS = {
    "taxable_income_old_regime", "taxable_income_new_regime",
    "total_tax_old_regime", "total_tax_new_regime",
    "refund_amount", "demand_amount",
    "total_interest", "gross_total_income",
}


@dataclass
class FieldResult:
    field: str
    engine_value: Any
    human_value: Any
    matched: bool
    delta: Optional[int] = None


@dataclass
class CaseResult:
    case_id: str
    taxpayer_name: str
    fields: List[FieldResult] = field(default_factory=list)
    entity_pressure: List[str] = field(default_factory=list)
    engine_error: Optional[str] = None

    @property
    def passed(self) -> bool:
        return self.engine_error is None and all(f.matched for f in self.fields)

    @property
    def validated_count(self) -> int:
        return len(self.fields)

    @property
    def matched_count(self) -> int:
        return sum(1 for f in self.fields if f.matched)


def _load_cases(case_id_filter: Optional[str] = None) -> List[dict]:
    cases = []
    for fname in sorted(os.listdir(CASES_DIR)):
        if not fname.endswith(".json") or fname.startswith("_"):
            continue
        if "template" in fname.lower():
            continue
        path = os.path.join(CASES_DIR, fname)
        with open(path) as f:
            case = json.load(f)
        if case_id_filter and case.get("case_id") != case_id_filter:
            continue
        cases.append(case)
    return cases


def _run_engine(case: dict) -> Tuple[dict, Optional[str]]:
    evidence = dict(case.get("evidence", {}))
    taxpayer = case.get("taxpayer", {})
    if "age" in taxpayer:
        evidence.setdefault("taxpayer_age", taxpayer["age"])
    if "age_bracket" in taxpayer:
        evidence.setdefault("age_bracket", taxpayer["age_bracket"])
    evidence.setdefault("case_id", case.get("case_id", "unknown"))
    evidence.setdefault("taxpayer_name", taxpayer.get("name", "Taxpayer"))

    try:
        parser = ManualParser()
        evidence_obj = parser.parse(evidence)
        ctx = execute(ALL_SPECS, evidence_obj.evidence)
        return ctx.snapshot(), None
    except Exception as e:
        return {}, str(e)


def _compare(field_name: str, engine_val: Any, human_val: Any) -> FieldResult:
    if human_val is None:
        return FieldResult(field=field_name, engine_value=engine_val, human_value=None, matched=True)

    if field_name in _AMOUNT_FIELDS and isinstance(engine_val, (int, float)) and isinstance(human_val, (int, float)):
        delta = int(engine_val) - int(human_val)
        matched = abs(delta) <= AMOUNT_TOLERANCE
        return FieldResult(field=field_name, engine_value=engine_val, human_value=human_val,
                           matched=matched, delta=delta if not matched else None)

    matched = engine_val == human_val
    return FieldResult(field=field_name, engine_value=engine_val, human_value=human_val, matched=matched)


def run_case(case: dict) -> CaseResult:
    case_id = case.get("case_id", "unknown")
    taxpayer_name = case.get("taxpayer", {}).get("name", "unknown")

    snapshot, error = _run_engine(case)
    if error:
        return CaseResult(case_id=case_id, taxpayer_name=taxpayer_name, engine_error=error)

    human_expected = {
        k: v for k, v in case.get("human_expected", {}).items()
        if not k.startswith("_")
    }

    field_results = []
    for field_name, human_val in human_expected.items():
        engine_val = snapshot.get(field_name)
        field_results.append(_compare(field_name, engine_val, human_val))

    entity_pressure = case.get("entity_pressure_observed", [])

    return CaseResult(
        case_id=case_id,
        taxpayer_name=taxpayer_name,
        fields=field_results,
        entity_pressure=entity_pressure,
    )


def _fmt_amount(v: Any) -> str:
    if isinstance(v, (int, float)):
        return f"₹{int(v):,}"
    return repr(v)


def print_report(results: List[CaseResult]) -> None:
    WIDTH = 72
    print("\n" + "=" * WIDTH)
    print(" Real-Case Validation Report — AY2025-26")
    print("=" * WIDTH)

    all_pressure = []

    for r in results:
        status = "ERROR" if r.engine_error else ("PASS" if r.passed else "FAIL")
        marker = {"PASS": "✓", "FAIL": "✗", "ERROR": "!"}.get(status, "?")
        print(f"\n  {marker} {r.case_id}  {r.taxpayer_name}  [{status}]")

        if r.engine_error:
            print(f"      Engine error: {r.engine_error}")
            continue

        if not r.fields:
            print("      No human_expected fields declared — run engine output only.")
            snapshot, _ = _run_engine({})  # just show what we can
        else:
            for fr in r.fields:
                if fr.human_value is None:
                    print(f"      {fr.field:<38} engine={_fmt_amount(fr.engine_value)}")
                elif fr.matched:
                    print(f"      {fr.field:<38} {_fmt_amount(fr.engine_value)}  ✓")
                else:
                    delta_str = f"  Δ {fr.delta:+,}" if fr.delta is not None else ""
                    print(f"      {fr.field:<38} engine={_fmt_amount(fr.engine_value)}  human={_fmt_amount(fr.human_value)}{delta_str}  ✗")

        if r.entity_pressure:
            for ep in r.entity_pressure:
                print(f"      ⚠  Entity pressure: {ep}")
            all_pressure.extend(r.entity_pressure)

    print("\n" + "-" * WIDTH)
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    errors = sum(1 for r in results if r.engine_error)
    print(f"  Cases: {total}   Passed: {passed}   Failed: {total - passed - errors}   Errors: {errors}")

    if all_pressure:
        from collections import Counter
        counts = Counter(all_pressure)
        print("\n  Entity pressure recurrences:")
        for ep, n in counts.most_common():
            print(f"    {ep}: {n}×")

    print("=" * WIDTH + "\n")


def main():
    filter_id = sys.argv[1] if len(sys.argv) > 1 else None
    cases = _load_cases(filter_id)

    if not cases:
        target = filter_id or "any"
        print(f"\nNo real cases found in cases/real/ matching '{target}'.")
        print("Use cases/real/RC-0001-template.json as a starting point.\n")
        sys.exit(0)

    results = [run_case(c) for c in cases]
    print_report(results)

    failed = [r for r in results if not r.passed]
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
