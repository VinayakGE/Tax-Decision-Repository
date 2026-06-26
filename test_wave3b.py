"""
Wave 3B test suite — T-0046 through T-0052 (80C/aggregator) and T-0074 through T-0088 (80D).
Tests the Deduction Engine: R-0024 (80C), R-0035–R-0038 (80D), R-0028 (Deduction Aggregator).
Each test runs the target rule in isolation against fixed inputs.
"""

import json
import os
import glob
import pytest

from engine.context import EvidenceContext
from engine.rules.wave3b import (
    r0024_deduction_80c,
    r0039_deduction_80ccd1b,
    r0035_80d_evidence_completeness,
    r0036_80d_self_cap,
    r0037_80d_parents_cap,
    r0038_80d_total,
    r0028_deduction_aggregator,
)

RULE_FN = {
    "R-0024": r0024_deduction_80c,
    "R-0039": r0039_deduction_80ccd1b,
    "R-0035": r0035_80d_evidence_completeness,
    "R-0036": r0036_80d_self_cap,
    "R-0037": r0037_80d_parents_cap,
    "R-0038": r0038_80d_total,
    "R-0028": r0028_deduction_aggregator,
}

TESTS_DIR = os.path.join(os.path.dirname(__file__), "tests")


def _load_wave3b_tests():
    ids = list(range(46, 53)) + list(range(74, 94))
    cases = []
    for tid in ids:
        pattern = os.path.join(TESTS_DIR, f"T-{tid:04d}-*.json")
        for path in sorted(glob.glob(pattern)):
            with open(path) as f:
                cases.append(json.load(f))
    return cases


def _assert_output(expected: dict, ctx: EvidenceContext, test_id: str):
    errors = []
    for key, exp_val in expected.items():
        act_val = ctx.get(key)
        if isinstance(exp_val, dict) and isinstance(act_val, dict):
            for sk, sv in exp_val.items():
                av = act_val.get(sk)
                if av != sv:
                    errors.append(f"{test_id}: {key}.{sk} — expected {sv!r}, got {av!r}")
        elif act_val != exp_val:
            errors.append(f"{test_id}: {key} — expected {exp_val!r}, got {act_val!r}")
    return errors


@pytest.mark.parametrize("case", _load_wave3b_tests(), ids=[c["id"] for c in _load_wave3b_tests()])
def test_wave3b_rule(case):
    test_id = case["id"]
    rule_ref = case["target_ref"]
    fn = RULE_FN.get(rule_ref)
    assert fn is not None, f"No function registered for {rule_ref}"

    ctx = EvidenceContext(case["input"])
    fn(ctx)

    errors = _assert_output(case["expected_output"], ctx, test_id)
    assert not errors, "\n".join(errors)
