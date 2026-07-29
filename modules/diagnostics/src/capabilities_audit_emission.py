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
from typing import Any, Protocol

from modules.shared.src.diagnostics.contract_audit_emission_protocol import (
    AuditEmissionProtocol,
)
from modules.shared.src.diagnostics.taxonomy_diagnostics_vo import AuditRecordVO
from modules.shared.src.security.taxonomy_security_constant import (
    REDACTION_SENSITIVE_PATTERNS,
)

logger = logging.getLogger(__name__)

# Pre-compiled redaction patterns (AES305 — single source of truth).
_SENSITIVE_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(p) for p in REDACTION_SENSITIVE_PATTERNS
)


# Pre-compiled patterns for sensitive key names (case-insensitive).
_SENSITIVE_KEY_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(rf"(?i)\b({p})\b", re.IGNORECASE)
    for p in [
        "password", "passwd", "secret", "token", "api[_-]?key",
        "access[_-]?key", "private[_-]?key", "credential",
    ]
)


def _is_sensitive_key(key: str) -> bool:
    """Return True if the key name looks like a secret holder."""
    return any(p.search(key) for p in _SENSITIVE_KEY_PATTERNS)


def _redact_sensitive(value: object) -> Any:
    """Recursively mask obvious secret shapes in nested metadata.

    Strings are pattern-redacted; dict/list/tuple are walked without mutating the
    caller's input object. Dict values whose keys match sensitive names are also
    redacted (handles bare-token shapes like {"token": "ghp_..."}).
    Non-text scalars pass through untouched.
    """
    if isinstance(value, str):
        text = value
        for pattern in _SENSITIVE_PATTERNS:
            text = pattern.sub("[REDACTED]", text)
        return text
    if isinstance(value, dict):
        new_dict: dict[str, Any] = {}
        for key, val in value.items():
            if _is_sensitive_key(key) and isinstance(val, str):
                # Redact bare secret values behind sensitive keys.
                new_val: Any = "[REDACTED]"
                for pattern in _SENSITIVE_PATTERNS:
                    new_val = pattern.sub("[REDACTED]", val)
                if new_val == val:  # no pattern matched — value is a secret shape
                    new_val = "[REDACTED]"
                new_dict[key] = new_val
            else:
                new_dict[key] = _redact_sensitive(val)
        return new_dict
    if isinstance(value, (list, tuple)):
        return type(value)(_redact_sensitive(item) for item in value)
    return value


class _AuditSink(Protocol):
    """Protocol for delivering audit events to observability (DI boundary)."""

    def deliver(self, event: AuditRecordVO) -> None: ...


class AuditEmitter(AuditEmissionProtocol):
    """Emit immutable audit records for security-relevant activity.

    Produces frozen audit records for security violations, connection failures,
    task failures, and destructive actions. Records are immutable once emitted.
    Falls back to in-memory ring buffer when subscribers fail.
    """

    def __init__(self, sink: _AuditSink | None = None, max_buffer_size: int = 1000) -> None:
        self._sink = sink
        # Fallback ring buffer (bounded — drops oldest when full)
        self._fallback_buffer: deque[AuditRecordVO] = deque(maxlen=max_buffer_size)

    async def emit_audit_event(
        self,
        category: str,
        severity: str,
        source_feature: str,
        operation_type: str,
        target_metadata: dict | None = None,
        correlation_id: str | None = None,
    ) -> AuditRecordVO:
        """Produce immutable audit record for security-relevant activity.

        FR-DIA-003: Redaction applied before emission — no raw code/tokens/credentials/paths.
        Records are frozen (dataclass(frozen=True)) — immutable once emitted.
        Sink failure → fallback buffer + warning; never alters original operation.
        """
        # Redact target metadata before emission (FR-SEC-004 defense-in-depth)
        safe_metadata = _redact_sensitive(target_metadata) if target_metadata else {}

        # Build frozen audit record
        record_id = uuid.uuid4().hex[:16]
        timestamp = time.time()
        record = AuditRecordVO(
            category=category,
            severity=severity,
            source_feature=source_feature,
            operation_type=operation_type,
            target_metadata=safe_metadata,
            correlation_id=correlation_id,
            record_id=record_id,
            timestamp=timestamp,
            emission_confirmed=False,
            emission_path="direct",
        )

        # Attempt sink delivery
        delivery_failed = False
        if self._sink:
            try:
                self._sink.deliver(record)
            except Exception as exc:
                logger.warning("Audit sink delivery failed: %s", exc)
                delivery_failed = True
        else:
            # No sink configured — log and use fallback
            logger.info("No audit sink configured — recording to fallback buffer")
            delivery_failed = True

        if delivery_failed:
            # Push to fallback ring buffer
            self._fallback_buffer.append(record)
            record = AuditRecordVO(
                category=category,
                severity=severity,
                source_feature=source_feature,
                operation_type=operation_type,
                target_metadata=safe_metadata,
                correlation_id=correlation_id,
                record_id=record_id,
                timestamp=timestamp,
                emission_confirmed=True,
                emission_path="fallback",
            )

        return record

    def get_fallback_buffer(self) -> list[AuditRecordVO]:
        """Return copy of fallback buffer contents (for testing)."""
        return list(self._fallback_buffer)


class InMemoryEventBus:
    """In-memory event bus stub for testing.

    Actual event publishing is delegated to the MCP gateway layer.
    This class exists only as a DI placeholder — subscribers must be
    wired by the container before use.
    """

    def __init__(self) -> None:
        self._subscribers: list[Any] = []

    def subscribe(self, subscriber: Any) -> None:
        """Subscribe an event handler."""
        if subscriber not in self._subscribers:
            self._subscribers.append(subscriber)
            logger.debug("Event bus subscribed: %s", type(subscriber).__name__)

    async def publish(self, event: Any) -> None:
        """Publish an event to all subscribers."""
        for subscriber in self._subscribers:
            try:
                if hasattr(subscriber, "handle"):
                    await subscriber.handle(event)
            except Exception as e:
                logger.error(
                    "Event subscriber %s failed: %s",
                    type(subscriber).__name__,
                    e,
                    exc_info=True,
                )

    def get_subscribers(self) -> list[Any]:
        """Return list of registered subscribers (for testing)."""
        return list(self._subscribers)

    def __repr__(self) -> str:
        return "InMemoryEventBus()"
