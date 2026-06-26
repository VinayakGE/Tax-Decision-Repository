#!/usr/bin/env python3
"""
Real-Case Validation Runner — AY2025-26

Runs the engine against anonymized real salary cases and compares output
against human-computed expected values. Produces a Learning Velocity (LV)
report that tracks how the engine improves case-by-case.

Schema: docs/real-case-schema.md (frozen, version 1.0.0)

Usage:
  python bin/run_real_cases.py           # all cases
  python bin/run_real_cases.py RC-0002   # single case by ID

Output: per-field comparison table + LV breakdown + entity pressure summary.
"""

import json
import os
import sys
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.parsers.manual import ManualParser
from engine.executor import execute
from engine.specs import ALL_SPECS

CASES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cases", "real")
SCHEMA_VERSION = "1.0.0"
AMOUNT_TOLERANCE = 1  # ±₹1 rounding tolerance

_AMOUNT_FIELDS = {
    "taxable_income_old_regime", "taxable_income_new_regime",
    "total_tax_old_regime", "total_tax_new_regime",
    "refund_amount", "demand_amount",
    "total_interest", "gross_total_income",
}

# LV classification labels and display markers
_LV_LABELS = {
    "match":        ("✅", "Match        — engine correct"),
    "conservative": ("🟡", "Conservative — engine over-cautious on evidence"),
    "rule_gap":     ("🟠", "Rule gap     — deduction or rule not yet implemented"),
    "defect":       ("🔴", "Defect       — engine computed incorrectly"),
    "unclassified": ("⬜", "Unclassified — review pending"),
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
    lv_classification: str = "unclassified"
    schema_warnings: List[str] = field(default_factory=list)
    fields: List[FieldResult] = field(default_factory=list)
    entity_pressure: List[str] = field(default_factory=list)
    engine_error: Optional[str] = None

    @property
    def all_fields_match(self) -> bool:
        validated = [f for f in self.fields if f.human_value is not None]
        return bool(validated) and all(f.matched for f in validated)

    @property
    def has_mismatch(self) -> bool:
        return any(not f.matched and f.human_value is not None for f in self.fields)

    @property
    def effective_lv(self) -> str:
        """Auto-classify if human hasn't set one, based on field matches."""
        if self.lv_classification != "unclassified":
            return self.lv_classification
        if self.engine_error:
            return "defect"
        if self.all_fields_match:
            return "match"
        return "unclassified"


def _validate_schema(case: dict) -> List[str]:
    warnings = []
    sv = case.get("schema_version")
    if not sv:
        warnings.append("missing schema_version — expected 1.0.0")
    elif sv != SCHEMA_VERSION:
        warnings.append(f"schema_version {sv!r} != {SCHEMA_VERSION!r}")
    if not case.get("anonymized"):
        warnings.append("anonymized is not true — verify before sharing")
    if not case.get("assessment_year"):
        warnings.append("assessment_year not set")
    return warnings


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


def _compare_field(field_name: str, engine_val: Any, human_val: Any) -> FieldResult:
    if human_val is None:
        return FieldResult(field=field_name, engine_value=engine_val, human_value=None, matched=True)

    if field_name in _AMOUNT_FIELDS and isinstance(engine_val, (int, float)) and isinstance(human_val, (int, float)):
        delta = int(engine_val) - int(human_val)
        matched = abs(delta) <= AMOUNT_TOLERANCE
        return FieldResult(field=field_name, engine_value=engine_val, human_value=human_val,
                           matched=matched, delta=delta if not matched else None)

    return FieldResult(field=field_name, engine_value=engine_val, human_value=human_val,
                       matched=(engine_val == human_val))


def run_case(case: dict) -> CaseResult:
    case_id = case.get("case_id", "unknown")
    taxpayer_name = case.get("taxpayer", {}).get("name", "unknown")
    lv = case.get("lv_classification", "unclassified")
    schema_warnings = _validate_schema(case)

    snapshot, error = _run_engine(case)
    if error:
        return CaseResult(case_id=case_id, taxpayer_name=taxpayer_name,
                          lv_classification=lv, schema_warnings=schema_warnings,
                          engine_error=error)

    human_expected = {
        k: v for k, v in case.get("human_expected", {}).items()
        if not k.startswith("_")
    }

    field_results = [
        _compare_field(fname, snapshot.get(fname), human_val)
        for fname, human_val in human_expected.items()
    ]

    return CaseResult(
        case_id=case_id,
        taxpayer_name=taxpayer_name,
        lv_classification=lv,
        schema_warnings=schema_warnings,
        fields=field_results,
        entity_pressure=case.get("entity_pressure_observed", []),
    )


def _fmt(v: Any) -> str:
    if isinstance(v, (int, float)):
        return f"₹{int(v):,}"
    return repr(v)


def print_report(results: List[CaseResult]) -> None:
    W = 74
    print("\n" + "=" * W)
    print(" Real-Case Validation Report — AY2025-26")
    print("=" * W)

    all_pressure: List[str] = []

    for r in results:
        lv_marker, _ = _LV_LABELS.get(r.effective_lv, ("?", ""))
        status = "ERROR" if r.engine_error else ("PASS" if r.all_fields_match else "FAIL")
        print(f"\n  {lv_marker} {r.case_id}  {r.taxpayer_name}  [{status}]  lv={r.effective_lv}")

        for w in r.schema_warnings:
            print(f"      ⚠  Schema: {w}")

        if r.engine_error:
            print(f"      Engine error: {r.engine_error}")
            continue

        validated = [f for f in r.fields if f.human_value is not None]
        unset = [f for f in r.fields if f.human_value is None]

        for fr in validated:
            if fr.matched:
                print(f"      {fr.field:<40} {_fmt(fr.engine_value)}  ✓")
            else:
                delta_str = f"  Δ {fr.delta:+,}" if fr.delta is not None else ""
                print(f"      {fr.field:<40} engine={_fmt(fr.engine_value)}  human={_fmt(fr.human_value)}{delta_str}  ✗")

        if unset:
            print(f"      (engine-only, {len(unset)} field(s) without human benchmark)")
            for fr in unset:
                print(f"        {fr.field:<38} {_fmt(fr.engine_value)}")

        if not r.fields:
            print("      No human_expected fields declared yet.")

        if r.entity_pressure:
            for ep in r.entity_pressure:
                print(f"      ⚠  Entity pressure: {ep}")
            all_pressure.extend(r.entity_pressure)

    # ── LV Summary ──────────────────────────────────────────────────────────
    print("\n" + "-" * W)
    total = len(results)
    errors = sum(1 for r in results if r.engine_error)

    lv_counts = Counter(r.effective_lv for r in results)
    print(f"\n  Learning Velocity — {total} case(s)")
    for lv_key in ("match", "conservative", "rule_gap", "defect", "unclassified"):
        n = lv_counts.get(lv_key, 0)
        if n or lv_key in ("match", "unclassified"):
            marker, label = _LV_LABELS[lv_key]
            print(f"    {marker}  {n:2d}  {label}")

    match_rate = lv_counts.get("match", 0) / total * 100 if total else 0
    print(f"\n  Match rate: {match_rate:.0f}%  |  Errors: {errors}")

    # ── Entity Pressure ──────────────────────────────────────────────────────
    if all_pressure:
        ep_counts = Counter(all_pressure)
        print("\n  Entity pressure recurrences:")
        for ep, n in ep_counts.most_common():
            print(f"    {ep}: {n}×")

    print("=" * W + "\n")


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

    failed = [r for r in results if r.has_mismatch or r.engine_error]
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
