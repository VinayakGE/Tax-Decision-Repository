"""
Wave 3A test suite.
Loads T-0028 through T-0045 and verifies expected outputs.
Each test runs its target rule in isolation against the test's input.
"""

import json
import os
import glob
import pytest

from engine.context import EvidenceContext
from engine.rules.wave3a import (
    r0015_taxable_income_assembly,
    r0016_slab_engine_old_regime,
    r0017_slab_engine_new_regime,
    r0018_regime_comparator,
    r0019_section_87a_rebate,
    r0020_health_education_cess,
    r0021_surcharge,
    r0022_interest_234abc,
    r0023_refund_vs_demand,
)

RULE_FN = {
    "R-0015": r0015_taxable_income_assembly,
    "R-0016": r0016_slab_engine_old_regime,
    "R-0017": r0017_slab_engine_new_regime,
    "R-0018": r0018_regime_comparator,
    "R-0019": r0019_section_87a_rebate,
    "R-0020": r0020_health_education_cess,
    "R-0021": r0021_surcharge,
    "R-0022": r0022_interest_234abc,
    "R-0023": r0023_refund_vs_demand,
}

TESTS_DIR = os.path.join(os.path.dirname(__file__), "tests")


def _load_wave3a_tests():
    ids = list(range(28, 46))
    cases = []
    for tid in ids:
        pattern = os.path.join(TESTS_DIR, f"T-{tid:04d}-*.json")
        matches = glob.glob(pattern)
        for path in matches:
            with open(path) as f:
                cases.append(json.load(f))
    return cases


def _check_keys(expected: dict, actual_ctx: EvidenceContext, test_id: str):
    """Assert each key in expected matches the context value."""
    errors = []
    for key, exp_val in expected.items():
        act_val = actual_ctx.get(key)
        if isinstance(exp_val, dict) and isinstance(act_val, dict):
            for subkey, sub_exp in exp_val.items():
                sub_act = act_val.get(subkey)
                if sub_act != sub_exp:
                    errors.append(
                        f"{test_id}: {key}.{subkey} — expected {sub_exp!r}, got {sub_act!r}"
                    )
        elif isinstance(exp_val, list) and isinstance(act_val, list):
            if len(exp_val) != len(act_val):
                errors.append(
                    f"{test_id}: {key} — expected list length {len(exp_val)}, got {len(act_val)}"
                )
            else:
                for i, (e_item, a_item) in enumerate(zip(exp_val, act_val)):
                    if isinstance(e_item, dict) and isinstance(a_item, dict):
                        for sk, sv in e_item.items():
                            av = a_item.get(sk)
                            if av != sv:
                                errors.append(
                                    f"{test_id}: {key}[{i}].{sk} — expected {sv!r}, got {av!r}"
                                )
                    elif e_item != a_item:
                        errors.append(
                            f"{test_id}: {key}[{i}] — expected {e_item!r}, got {a_item!r}"
                        )
        else:
            if act_val != exp_val:
                errors.append(
                    f"{test_id}: {key} — expected {exp_val!r}, got {act_val!r}"
                )
    return errors


_CASES = _load_wave3a_tests()


@pytest.mark.parametrize("case", _CASES, ids=[c["id"] for c in _CASES])
def test_wave3a_rule(case):
    rule_id = case["target_ref"]
    fn = RULE_FN.get(rule_id)
    assert fn is not None, f"No executor registered for {rule_id}"

    ctx = EvidenceContext(case["input"])
    fn(ctx)

    errors = _check_keys(case["expected_output"], ctx, case["id"])
    assert not errors, "\n".join(errors)
