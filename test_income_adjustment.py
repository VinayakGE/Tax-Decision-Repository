"""
Income Adjustment Engine test suite — T-0053 through T-0072.
Tests the Income Adjustment Engine: R-0029 through R-0034 (HRA exemption).
Each test runs the target rule in isolation against fixed inputs.
"""

import json
import os
import glob
import pytest

from engine.context import EvidenceContext
from engine.rules.income_adjustment import (
    r0029_hra_evidence_completeness,
    r0030_hra_candidate_1,
    r0031_hra_candidate_2,
    r0032_hra_candidate_3,
    r0033_hra_final_exemption,
    r0034_income_adjustment_aggregator,
)

RULE_FN = {
    "R-0029": r0029_hra_evidence_completeness,
    "R-0030": r0030_hra_candidate_1,
    "R-0031": r0031_hra_candidate_2,
    "R-0032": r0032_hra_candidate_3,
    "R-0033": r0033_hra_final_exemption,
    "R-0034": r0034_income_adjustment_aggregator,
}

TESTS_DIR = os.path.join(os.path.dirname(__file__), "tests")


def _load_income_adjustment_tests():
    ids = list(range(53, 74))
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


@pytest.mark.parametrize(
    "case",
    _load_income_adjustment_tests(),
    ids=[c["id"] for c in _load_income_adjustment_tests()],
)
def test_income_adjustment_rule(case):
    test_id = case["id"]
    rule_ref = case["target_ref"]
    fn = RULE_FN.get(rule_ref)
    assert fn is not None, f"No function registered for {rule_ref}"

    ctx = EvidenceContext(case["input"])
    fn(ctx)

    errors = _assert_output(case["expected_output"], ctx, test_id)
    assert not errors, "\n".join(errors)
