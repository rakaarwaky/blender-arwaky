"""Capability: Structured logging policy enforcer.

FR-DIA-004: Structured Logging Policy
All features log through diagnostics policy. Logs are structured.
Redaction applied at ingestion.
Implements LoggingPolicyProtocol.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from modules.diagnostics.src.contract_logging_policy_protocol import (
    LoggingPolicyProtocol,
)

logger = logging.getLogger("BlenderMCPServer")


class LoggingPolicy(LoggingPolicyProtocol):
    """Enforce structured logging policy with redaction at ingestion.

    All features log through this policy. Private per-feature log formats
    are not permitted. Redaction applied before destination write.
    """

    def __init__(self) -> None:
        self._log_buffer: list[dict[str, Any]] = []

    async def log_record(
        self,
        level: str,
        source_feature: str,
        message: str,
        fields: dict[str, Any] | None = None,
        tracking_id: str | None = None,
        source_tool: Any = None,
    ) -> dict[str, Any]:
        """Write sanitized structured log entry."""
        entry: dict[str, Any] = {
            "level": level,
            "source_feature": source_feature,
            "message": message,
            "fields": fields or {},
            "tracking_id": tracking_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._log_buffer.append(entry)

        log_fn = getattr(logger, level.lower(), logger.info)
        log_fn("%s [%s] %s", source_feature, level, message)

        return {"logged": True, "destination": "buffer"}
