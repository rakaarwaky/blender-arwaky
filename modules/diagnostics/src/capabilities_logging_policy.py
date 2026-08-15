"""Capability: Structured logging policy enforcer with ingestion-time redaction.

FR-DIA-004: Structured Logging Policy
All features log through diagnostics policy. Logs are structured.
Redaction applied at ingestion. Backpressure handling via bounded buffer.
Implements LoggingPolicyProtocol.
"""

from __future__ import annotations

import logging
from collections import deque
from datetime import datetime, timezone

from modules.shared.src.diagnostics.contract_logging_policy_protocol import (
    LoggingPolicyProtocol,
)
from modules.shared.src.diagnostics.taxonomy_diagnostics_vo import LogRecordRequestVO, LogResultVO
from modules.shared.src.security.taxonomy_security_constant import (
    REDACTION_SENSITIVE_PATTERNS,
)
from modules.shared.src.security.utility_security_redactor import redact_sensitive

logger = logging.getLogger(__name__)


class LoggingPolicy(LoggingPolicyProtocol):
    """Enforce structured logging policy with redaction at ingestion."""

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(self, max_buffer_size: int = 10000) -> None:
        self._buffer: deque[dict[str, object]] = deque(maxlen=max_buffer_size)
        self._drop_counter: int = 0
        self._max_buffer_size = max_buffer_size
        self._min_level: str = "info"

    # ─── Block 2: Protocol Method Implementation ─────────────

    async def log_record(
        self,
        request: LogRecordRequestVO,
    ) -> LogResultVO:
        """Write sanitized structured log entry.

        FR-DIA-004: Redaction applied at ingestion. No raw code/tokens/credentials/auth tokens/paths.
        Backpressure: buffer bounded; oldest dropped when full with counter incremented.
        """
        raw_msg = redact_sensitive(request.message) if isinstance(request.message, str) else request.message
        redacted_message = raw_msg if isinstance(raw_msg, str) else str(raw_msg)
        raw_fields = redact_sensitive(request.fields) if request.fields else {}
        redacted_fields = raw_fields if isinstance(raw_fields, dict) else {}
        redacted_count = self._count_redactions(request.message, request.fields)

        entry: dict[str, object] = {
            "level": request.level,
            "source_feature": request.source_feature,
            "message": redacted_message,
            "fields": redacted_fields or {},
            "tracking_id": request.tracking_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if len(self._buffer) >= self._max_buffer_size:
            self._drop_counter += 1
            logger.warning(
                "Log buffer full (%d records), dropping oldest. Drop counter: %d",
                self._max_buffer_size,
                self._drop_counter,
            )

        self._buffer.append(entry)

        log_fn = getattr(logger, request.level.lower(), logger.info)
        log_fn("%s [%s] %s", request.source_feature, request.level, redacted_message)

        return LogResultVO(
            logged=True,
            destination="buffer",
            redacted_count=redacted_count,
            drop_counter=self._drop_counter,
        )

    async def set_min_level(self, level: str) -> None:
        """Set minimum logging severity level threshold."""
        self._min_level = level.lower()

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    def _count_redactions(self, message: str, fields: dict | None) -> int:
        count = 0
        for pattern_str in REDACTION_SENSITIVE_PATTERNS:
            import re

            pattern = re.compile(pattern_str)
            if pattern.search(message):
                count += 1
        if fields:
            for val in fields.values():
                if isinstance(val, str):
                    for pattern_str in REDACTION_SENSITIVE_PATTERNS:
                        import re

                        pattern = re.compile(pattern_str)
                        if pattern.search(val):
                            count += 1
        return count

    def get_buffer_contents(self) -> list[dict[str, object]]:
        """Return copy of buffer contents (for testing/inspection)."""
        return list(self._buffer)

    def get_drop_counter(self) -> int:
        """Return current drop counter (for backpressure monitoring)."""
        return self._drop_counter

    def __repr__(self) -> str:
        return f"LoggingPolicy(min_level={self._min_level!r})"
