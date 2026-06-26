"""Rule Executor — runs a scheduled list of rule waves against an EvidenceContext."""

from engine.context import EvidenceContext
from engine.scheduler import RuleSpec, build_schedule
from typing import List


def execute(specs: List[RuleSpec], initial_evidence: dict) -> EvidenceContext:
    """
    Topologically sorts specs and executes them in order against a fresh EvidenceContext.
    Returns the populated context after all rules have run.
    """
    ctx = EvidenceContext(initial_evidence)
    waves = build_schedule(specs)
    for wave in waves:
        for spec in wave:
            spec.fn(ctx)
    return ctx
