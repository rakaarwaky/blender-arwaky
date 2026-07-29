# modules/job/src/capabilities_job_evaluator.py
"""Capability: Job cancellation evaluator (FR-JOB-003).

Evaluates cancellation eligibility. Signals executor via utility.
Does NOT mutate state — Agent applies transition via repository.
"""
from __future__ import annotations

import logging

from modules.shared.src.common.taxonomy_core_vo import JobState
from modules.shared.src.job.contract_job_cancellation_protocol import IJobCancellation
from modules.shared.src.job.taxonomy_job_constant import (
    CANCELLATION_ACCEPTED,
    CANCELLATION_ALREADY_TERMINAL,
    CANCELLATION_UNSUPPORTED,
    JOB_STATE_PENDING,
    JOB_STATE_RUNNING,
    TERMINAL_JOB_STATES,
)
from modules.shared.src.job.taxonomy_job_vo import (
    CancellationResult,
    CancelTaskCommand,
)
from modules.shared.src.job.utility_job_sanitizer import sanitize_cancellation_reason
from modules.shared.src.job.utility_job_signaler import signal_executor

logger = logging.getLogger("BlenderMCPServer")


# ─── Block 1: Class Definition & Constructor ─────────────────────────────────


class JobCancellationEvaluator(IJobCancellation):
    """Evaluates cancellation eligibility per FR-JOB-003."""

    # ─── Block 2: Domain Protocol Method Implementation ──────────────────────

    def evaluate(
        self,
        command: CancelTaskCommand,
        current_state: JobState,
    ) -> CancellationResult:
        """Evaluate cancellation request against current task state.

        - Terminal → ALREADY_TERMINAL
        - Pending → ACCEPTED (no signaling)
        - Running → signal executor via utility, then ACCEPTED or UNSUPPORTED
        """
        if current_state in TERMINAL_JOB_STATES:
            return CancellationResult(
                job_id=command.job_id,
                accepted=False,
                outcome=CANCELLATION_ALREADY_TERMINAL,
                message=f"Task already in terminal state {current_state}",
            )

        if current_state == JOB_STATE_PENDING:
            return CancellationResult(
                job_id=command.job_id,
                accepted=True,
                outcome=CANCELLATION_ACCEPTED,
                message="Cancellation accepted for pending task",
            )

        if current_state == JOB_STATE_RUNNING:
            return self._evaluate_running(command)

        return CancellationResult(
            job_id=command.job_id,
            accepted=False,
            outcome=CANCELLATION_UNSUPPORTED,
            message=f"Cancellation not supported for state {current_state}",
        )

    # ─── Block 3: Dunder Methods, Factories, and Private Helpers ─────────────

    def __repr__(self) -> str:
        return "<JobCancellationEvaluator>"

    def _evaluate_running(self, command: CancelTaskCommand) -> CancellationResult:
        reason = sanitize_cancellation_reason(command.reason)
        reason_str = str(reason) if reason else None

        signaled = signal_executor(str(command.job_id), reason_str)

        if not signaled:
            return CancellationResult(
                job_id=command.job_id,
                accepted=False,
                outcome=CANCELLATION_UNSUPPORTED,
                message="Executor could not be signaled",
            )

        return CancellationResult(
            job_id=command.job_id,
            accepted=True,
            outcome=CANCELLATION_ACCEPTED,
            message="Cancellation signal sent to executor",
        )
