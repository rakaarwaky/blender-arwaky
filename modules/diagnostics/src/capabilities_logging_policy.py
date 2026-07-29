"""Capability: Structured logging policy enforcer with ingestion-time redaction.

FR-DIA-004: Structured Logging Policy
All features log through diagnostics policy. Logs are structured.
Redaction applied at ingestion. Backpressure handling via bounded buffer.
Implements LoggingPolicyProtocol.
"""

from __future__ import annotations

import logging
import re
import time
from collections import deque
from datetime import datetime, timezone
from typing import Any

from modules.diagnostics.src.contract_logging_policy_protocol import (
    LoggingPolicyProtocol,
)
from modules.diagnostics.src.taxonomy_diagnostics_vo import LogResultVO
from modules.shared.src.security.taxonomy_security_constant import (
    REDACTION_SENSITIVE_PATTERNS,
)

logger = logging.getLogger(__name__)

# Pre-compiled redaction patterns (AES305 — single source of truth).
_SENSITIVE_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(p) for p in REDACTION_SENSITIVE_PATTERNS
)


def _redact_sensitive(value: object) -> Any:
    """Recursively mask obvious secret shapes in structured fields.

    Strings are pattern-redacted; dict/list/tuple are walked without mutating the
    caller's input object. Non-text scalars pass through untouched.
    """
    if isinstance(value, str):
        text = value
        for pattern in _SENSITIVE_PATTERNS:
            text = pattern.sub("[REDACTED]", text)
        return text
    if isinstance(value, dict):
        return {key: _redact_sensitive(val) for key, val in value.items()}
    if isinstance(value, (list, tuple)):
        return type(value)(_redact_sensitive(item) for item in value)
    return value


class LoggingPolicy(LoggingPolicyProtocol):
    """Enforce structured logging policy with redaction at ingestion.

    All features log through this policy. Private per-feature log formats
    are not permitted. Redaction applied before destination write.
    Bounded buffer drops oldest under backpressure (drop counter exposed).
    """

    def __init__(self, max_buffer_size: int = 10000) -> None:
        self._buffer: deque[dict[str, Any]] = deque(maxlen=max_buffer_size)
        self._drop_counter: int = 0
        self._max_buffer_size = max_buffer_size

    async def log_record(
        self,
        level: str,
        source_feature: str,
        message: str,
        fields: dict[str, Any] | None = None,
        tracking_id: str | None = None,
    ) -> LogResultVO:
        """Write sanitized structured log entry.

        FR-DIA-004: Redaction applied at ingestion. No raw code/tokens/credentials/passwords/paths.
        Backpressure: buffer bounded; oldest dropped when full with counter incremented.
        """
        # Redact message and fields at ingestion
        redacted_message = _redact_sensitive(message) if isinstance(message, str) else message
        redacted_fields = _redact_sensitive(fields) if fields else {}
        redacted_count = self._count_redactions(message, fields)

        entry: dict[str, Any] = {
            "level": level,
            "source_feature": source_feature,
            "message": redacted_message,
            "fields": redacted_fields or {},
            "tracking_id": tracking_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Bounded buffer — drop oldest under backpressure
        if len(self._buffer) >= self._max_buffer_size:
            self._drop_counter += 1
            logger.warning(
                "Log buffer full (%d records), dropping oldest. Drop counter: %d",
                self._max_buffer_size,
                self._drop_counter,
            )

        self._buffer.append(entry)

        # Emit to Python logging (non-blocking — stdlib handles its own buffering)
        log_fn = getattr(logger, level.lower(), logger.info)
        log_fn("%s [%s] %s", source_feature, level, redacted_message)

        return LogResultVO(
            logged=True,
            destination="buffer",
            redacted_count=redacted_count,
            drop_counter=self._drop_counter,
        )

    def _count_redactions(self, message: str, fields: dict | None) -> int:
        """Count how many redaction patterns matched."""
        count = 0
        for pattern in _SENSITIVE_PATTERNS:
            if pattern.search(message):
                count += 1
        if fields:
            for val in fields.values():
                if isinstance(val, str):
                    for pattern in _SENSITIVE_PATTERNS:
                        if pattern.search(val):
                            count += 1
        return count

    def get_buffer_contents(self) -> list[dict[str, Any]]:
        """Return copy of buffer contents (for testing/inspection)."""
        return list(self._buffer)

    def get_drop_counter(self) -> int:
        """Return current drop counter (for backpressure monitoring)."""
        return self._drop_counter

    def __repr__(self) -> str:
        return "LoggingPolicy()"
