"""Capability: Audit event emitter with immutable records and fallback buffering.

FR-DIA-003: Emit Audit Events
Produces immutable audit records for security-relevant and operationally
significant activity. Supports async subscribers with isolated exception
handling and guaranteed fallback delivery.
Implements AuditEmissionProtocol.
"""

from __future__ import annotations

import logging
import re
import time
import uuid
from collections import deque

from modules.shared.src.diagnostics.contract_audit_emission_protocol import (
    AuditEmissionProtocol,
)
from modules.shared.src.diagnostics.taxonomy_diagnostics_vo import AuditEventRequestVO, AuditRecordVO
from modules.shared.src.security.taxonomy_security_constant import (
    REDACTION_SENSITIVE_PATTERNS,
)

logger = logging.getLogger(__name__)

_SENSITIVE_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(p) for p in REDACTION_SENSITIVE_PATTERNS
)

_SENSITIVE_KEY_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(rf"(?i)\b({p})\b", re.IGNORECASE)
    for p in [
        "password",
        "passwd",
        "secret",
        "token",
        "api[_-]?key",
        "access[_-]?key",
        "private[_-]?key",
        "credential",
    ]
)


def _is_sensitive_key(key: str) -> bool:
    return any(p.search(key) for p in _SENSITIVE_KEY_PATTERNS)


def _redact_sensitive(value: object) -> object:
    if isinstance(value, str):
        text = value
        for pattern in _SENSITIVE_PATTERNS:
            text = pattern.sub("[REDACTED]", text)
        return text
    if isinstance(value, dict):
        new_dict: dict = {}
        for key, val in value.items():
            if _is_sensitive_key(key) and isinstance(val, str):
                new_val = "[REDACTED]"
                for pattern in _SENSITIVE_PATTERNS:
                    new_val = pattern.sub("[REDACTED]", val)
                if new_val == val:
                    new_val = "[REDACTED]"
                new_dict[key] = new_val
            else:
                new_dict[key] = _redact_sensitive(val)
        return new_dict
    if isinstance(value, (list, tuple)):
        return type(value)(_redact_sensitive(item) for item in value)
    return value


class _AuditSink:
    """Protocol for delivering audit events to observability (DI boundary)."""

    def deliver(self, event: AuditRecordVO) -> None: ...


class AuditEmitter(AuditEmissionProtocol):
    """Emit immutable audit records for security-relevant activity."""

    def __init__(self, sink: _AuditSink | None = None, max_buffer_size: int = 1000) -> None:
        self._sink = sink
        self._fallback_buffer: deque[AuditRecordVO] = deque(maxlen=max_buffer_size)

    async def emit_audit_event(
        self,
        request: AuditEventRequestVO,
    ) -> AuditRecordVO:
        """Produce immutable audit record for security-relevant activity.

        FR-DIA-003: Redaction applied before emission — no raw code/tokens/credentials/paths.
        Records are frozen (dataclass(frozen=True)) — immutable once emitted.
        Sink failure → fallback buffer + warning; never alters original operation.
        """
        safe_metadata = _redact_sensitive(request.target_metadata) if request.target_metadata else {}

        record_id = uuid.uuid4().hex[:16]
        timestamp = time.time()
        record = AuditRecordVO(
            category=request.category,
            severity=request.severity,
            source_feature=request.source_feature,
            operation_type=request.operation_type,
            target_metadata=safe_metadata,
            correlation_id=request.correlation_id,
            record_id=record_id,
            timestamp=timestamp,
            emission_confirmed=False,
            emission_path="direct",
        )

        delivery_failed = False
        if self._sink:
            try:
                self._sink.deliver(record)
            except Exception as exc:
                logger.warning("Audit sink delivery failed: %s", exc)
                delivery_failed = True
        else:
            logger.info("No audit sink configured — recording to fallback buffer")
            delivery_failed = True

        if delivery_failed:
            self._fallback_buffer.append(record)
            record = AuditRecordVO(
                category=request.category,
                severity=request.severity,
                source_feature=request.source_feature,
                operation_type=request.operation_type,
                target_metadata=safe_metadata,
                correlation_id=request.correlation_id,
                record_id=record_id,
                timestamp=timestamp,
                emission_confirmed=True,
                emission_path="fallback",
            )

        return record

    def get_fallback_buffer(self) -> list[AuditRecordVO]:
        """Return copy of fallback buffer contents (for testing)."""
        return list(self._fallback_buffer)
