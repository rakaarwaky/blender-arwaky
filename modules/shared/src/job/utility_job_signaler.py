# modules/shared/src/job/utility_job_signaler.py
"""Job executor signaling utility — stateless standalone function.

Technical mechanics: dispatches a cancellation signal to the
execution layer. In the current in-memory architecture, this
logs the signal and confirms dispatch. When a real executor
integration exists, this function body changes — signature stays.
"""
from __future__ import annotations

import logging

logger = logging.getLogger("BlenderMCPServer")


def signal_executor(job_id: str, reason: str | None) -> bool:
    """Dispatch cancellation signal to execution layer.

    Concrete behavior:
      1. Log the signal dispatch (observable via diagnostics).
      2. Return True confirming signal was dispatched.

    Returns False only if dispatch mechanically fails.
    Does NOT make business decisions (accept/reject is caller's job).
    """
    try:
        logger.info(
            "Cancellation signal dispatched: job_id=%s reason=%s",
            job_id,
            reason if reason else "unspecified",
        )
        return True
    except Exception:
        logger.exception("Failed to dispatch cancellation signal for job_id=%s", job_id)
        return False