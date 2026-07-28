# modules/shared/src/job/utility_job_signaler.py
"""Job executor signaling utility — stateless standalone function.

Technical mechanics for dispatching cancellation signals to the
execution layer. Does not make business decisions.
"""
from __future__ import annotations

import logging

logger = logging.getLogger("BlenderMCPServer")


def signal_executor(job_id: str, reason: str | None) -> bool:
    """Dispatch a cancellation signal to the execution layer.

    Technical mechanics only. Returns True if signal was dispatched.
    In production, this would interact with the actual executor
    (thread event, process signal, callback registry, etc.).
    """
    logger.info(
        "Cancellation signal dispatched: job=%s reason=%s",
        job_id,
        reason or "none",
    )
    return True