"""Job domain error taxonomy (AES taxonomy layer).

Domain errors for the job feature. Centralized here so capabilities, the agent
orchestrator, and consumers share one vocabulary instead of raising bare
`KeyError` / `RuntimeError` / `OverflowError`.

FR-JOB error categories: task not found, capacity, state, validation,
concurrency. `ConcurrencyConflictError` is provided for the
"lost atomic race → already terminal" outcome described in FR-JOB-001/003.
"""

from __future__ import annotations

from modules.shared.src.common.taxonomy_core_vo import ErrorString


class JobNotFoundError(Exception):
    """Task identifier not found, including records purged after retention."""


class JobStateError(Exception):
    """Invalid or out-of-order state transition / cancellation of terminal task."""


class JobCapacityError(Exception):
    """Background capacity exceeded at submission time (FR-JOB-005)."""


class JobValidationError(Exception):
    """Malformed metadata, out-of-range progress, or missing required detail."""


class JobConcurrencyConflictError(Exception):
    """Competing transition lost an atomic race; reported as already terminal."""
