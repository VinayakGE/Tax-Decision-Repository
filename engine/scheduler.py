"""
Rule Scheduler — Kahn's topological sort.
Each RuleSpec declares requires (inputs) and produces (outputs).
The scheduler computes a dependency-ordered execution plan.
Rules in the same wave can run in parallel.
"""

from dataclasses import dataclass, field
from typing import Callable, List
from collections import defaultdict, deque


@dataclass
class RuleSpec:
    rule_id: str
    requires: List[str]
    produces: List[str]
    fn: Callable


def build_schedule(specs: List[RuleSpec]) -> List[List[RuleSpec]]:
    """
    Returns rules grouped into execution waves via topological sort.
    Rules within a wave have no inter-dependencies and can run in parallel.
    Raises ValueError on cycles.
    """
    id_to_spec = {s.rule_id: s for s in specs}

    # Map each produced key to the rule that produces it
    produced_by = {}
    for spec in specs:
        for key in spec.produces:
            produced_by[key] = spec.rule_id

    # Build adjacency: rule A must run before rule B if A produces something B requires.
    # Use sets so multiple keys from the same producer only add one edge (and one in_degree unit).
    edges = defaultdict(set)  # edges[a] = set of rule_ids that depend on a

    for spec in specs:
        for req in spec.requires:
            if req in produced_by:
                producer_id = produced_by[req]
                if producer_id != spec.rule_id:
                    edges[producer_id].add(spec.rule_id)

    # Derive in_degree from unique edges (not from key count)
    in_degree = {s.rule_id: 0 for s in specs}
    for producer_id, dependents in edges.items():
        for dep_id in dependents:
            in_degree[dep_id] += 1

    queue = deque(rid for rid, deg in in_degree.items() if deg == 0)
    waves = []

    while queue:
        wave_size = len(queue)
        wave = []
        for _ in range(wave_size):
            rid = queue.popleft()
            wave.append(id_to_spec[rid])
            for dependent in edges[rid]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        waves.append(wave)

    total_scheduled = sum(len(w) for w in waves)
    if total_scheduled != len(specs):
        unscheduled = [rid for rid, deg in in_degree.items() if deg > 0]
        raise ValueError(f"Cycle detected in rule dependencies. Unresolvable: {unscheduled}")

    return waves
