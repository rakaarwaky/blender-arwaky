# modules/job/src/capabilities_job_checker.py
"""Capability: Job capacity checker (FR-JOB-005).

Evaluates whether a new task can be accepted under capacity policy.
Stateless — receives count and policy, returns decision.
"""
from __future__ import annotations

from modules.shared.src.job.contract_job_capacity_protocol import IJobCapacity
from modules.shared.src.job.taxonomy_job_vo import CapacityDecision, JobPolicy

# ─── Block 1: Class Definition & Constructor ─────────────────────────────────


class JobCapacityChecker(IJobCapacity):
    """Evaluates capacity decisions per FR-JOB-005."""

    def __init__(self) -> None:
        pass

    # ─── Block 2: Domain Protocol Method Implementation ──────────────────────

    def evaluate(self, active_count: int, policy: JobPolicy) -> CapacityDecision:
        """Evaluate whether capacity allows a new task submission.

        - active >= limit → rejected with context
        - active < limit → accepted with available slots
        """
        limit = policy.max_active
        available = max(0, limit - active_count)

        if active_count >= limit:
            return CapacityDecision(
                accepted=False,
                active=active_count,
                limit=limit,
                available=0,
                reason=f"Background capacity exceeded: {active_count}/{limit} active tasks",
            )

        return CapacityDecision(
            accepted=True,
            active=active_count,
            limit=limit,
            available=available,
        )

    # ─── Block 3: Dunder Methods, Factories, and Private Helpers ─────────────

    def __repr__(self) -> str:
        return "<JobCapacityChecker>"
