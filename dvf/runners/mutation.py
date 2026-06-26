"""
Mutation runner — verifies that golden masters are sensitive to rule/table changes.
For each mutation: apply it, run affected GMs, assert the output changes.
If NO golden master detects the mutation, the suite has a blind spot.

Borrowed from compiler testing: if a test doesn't catch a deliberate wrong value,
it isn't protecting that rule.
"""

import copy
import json
import os
from dataclasses import dataclass
from typing import Any, Callable, List

from engine import tables
from dvf.runners.golden import run_golden, GOLDEN_DIR


@dataclass
class MutationSpec:
    name: str
    description: str
    table_file: str           # relative path, e.g. "tables/2024/rebates.json"
    key_path: List[str]       # e.g. ["87A", "new_regime", "income_limit"]
    mutated_value: Any
    should_affect: List[str]  # GM IDs expected to detect this mutation


@dataclass
class MutationResult:
    mutation_name: str
    cases_affected: List[str]    # GMs that detected the mutation (output changed)
    cases_missed: List[str]      # GMs that should have detected but didn't
    effective: bool              # True if at least one case_affected in should_affect


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MUTATIONS = [
    MutationSpec(
        name="87A_NR_limit_reduced",
        description="Reduce New Regime 87A income limit from ₹12L to ₹9L — GM-0001 (total income ₹10.22L) loses the rebate; GM-0002 already above limit so unaffected",
        table_file="tables/2024/rebates.json",
        key_path=["87A", "new_regime", "income_limit"],
        mutated_value=900000,
        should_affect=["GM-0001"],
    ),
    MutationSpec(
        name="87A_NR_max_rebate_halved",
        description="Halve New Regime max rebate from ₹60K to ₹30K — GM-0001 slab_tax is ₹44.7K < ₹60K so rebate was limited by slab_tax anyway. GM-0003 affected (rebate was ₹6250 < ₹60K).",
        table_file="tables/2024/rebates.json",
        key_path=["87A", "new_regime", "max_rebate"],
        mutated_value=30000,
        should_affect=["GM-0001"],
    ),
    MutationSpec(
        name="cess_rate_increased",
        description="Increase cess from 4% to 5% — affects all cases with non-zero tax",
        table_file="tables/2024/cess.json",
        key_path=["cess", "rate"],
        mutated_value=0.05,
        should_affect=["GM-0002", "GM-0004"],
    ),
    MutationSpec(
        name="new_regime_std_deduction_reduced",
        description="Reduce New Regime standard deduction from ₹75K to ₹50K — affects all salary cases",
        table_file="tables/2024/tax_slabs.json",
        key_path=["new_regime", "standard_deduction"],
        mutated_value=50000,
        should_affect=["GM-0001", "GM-0002", "GM-0003"],
    ),
]


def _get_nested(d: dict, key_path: list) -> Any:
    for k in key_path:
        d = d[k]
    return d


def _set_nested(d: dict, key_path: list, value: Any) -> None:
    for k in key_path[:-1]:
        d = d[k]
    d[key_path[-1]] = value


def run_mutation(mut: MutationSpec) -> MutationResult:
    table_path = os.path.join(REPO_ROOT, mut.table_file)

    # Read original raw bytes so restore is byte-perfect
    with open(table_path, "rb") as f:
        original_bytes = f.read()
    original = json.loads(original_bytes)

    # Apply mutation
    mutated = copy.deepcopy(original)
    _set_nested(mutated, mut.key_path, mut.mutated_value)

    try:
        with open(table_path, "w") as f:
            json.dump(mutated, f, indent=2)
        tables._load.cache_clear()

        results = run_golden()
        affected = [r.case_id for r in results if not r.passed]

    finally:
        # Restore original bytes exactly — no re-serialization artifacts
        with open(table_path, "wb") as f:
            f.write(original_bytes)
        tables._load.cache_clear()

    cases_affected = [gm for gm in mut.should_affect if gm in affected]
    cases_missed = [gm for gm in mut.should_affect if gm not in affected]

    return MutationResult(
        mutation_name=mut.name,
        cases_affected=cases_affected,
        cases_missed=cases_missed,
        effective=len(cases_affected) > 0,
    )


def run_all_mutations() -> List[MutationResult]:
    return [run_mutation(m) for m in MUTATIONS]
