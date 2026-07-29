"""Capabilities: Audit emitter — FR-SEC-005.

Emits structured security audit events for violations, suspicious activity, and policy overrides.
Implements EmitAuditProtocol.

FR-SEC-004: tokens/credentials/passwords must not appear in logs. Audit events are
observability output, so any sensitive value nested in `target_metadata` (or
`redacted_reason`) is redacted at the sink before emission — defense-in-depth that
complements SensitiveRedactor and protects against callers passing raw secrets.
"""

from __future__ import annotations

import re
import time
import uuid
from typing import Any, Protocol

from modules.shared.src.security.contract_emit_audit_protocol import EmitAuditProtocol
from modules.shared.src.security.taxonomy_security_constant import REDACTION_SENSITIVE_PATTERNS
from modules.shared.src.security.taxonomy_security_vo import AuditSeverity, SecurityAuditEventVO

# Pre-compiled patterns shared from taxonomy constant (AES305 fix).
_SENSITIVE_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(p) for p in REDACTION_SENSITIVE_PATTERNS
)


def _redact_sensitive(value: object) -> Any:
    """Recursively mask obvious secret shapes in nested audit metadata.

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


class _AuditSink(Protocol):
    """Protocol for delivering audit events to observability (DI boundary)."""

    def deliver(self, event: SecurityAuditEventVO) -> None: ...


class AuditEmitter(EmitAuditProtocol):
    """Emits structured security audit events with fallback on sink failure."""

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(self, sink: _AuditSink | None = None) -> None:
        self._sink = sink

    # ─── Block 2: Public Contract  ────────────────────────
    async def emit_audit(self, event: SecurityAuditEventVO) -> SecurityAuditEventVO:
        """Emit a structured security audit event for violations and policy activity.

        FR-SEC-004: redact sensitive values from `target_metadata` / `redacted_reason`
        before emission so secrets never reach the observability sink, regardless of
        whether the caller pre-redacted. The caller's input event is never mutated.
        """
        emitted = SecurityAuditEventVO(
            violation_category=event.violation_category,
            operation_type=event.operation_type,
            source_feature=event.source_feature,
            target_metadata=_redact_sensitive(event.target_metadata),  # FR-SEC-004
            severity=event.severity,
            correlation_id=event.correlation_id,
            redacted_reason=_redact_sensitive(event.redacted_reason) if event.redacted_reason else None,
            event_id=uuid.uuid4().hex[:16],
            timestamp=time.time(),
            policy_mode=event.policy_mode,
        )

        fallback_record: SecurityAuditEventVO | None = None
        if self._sink:
            try:
                self._sink.deliver(emitted)
            except Exception as exc:
                # FR-SEC-005: audit sink unavailable — create local fallback record
                logger.warning("Audit sink delivery failed: %s", exc)
                fallback_record = SecurityAuditEventVO(
                    violation_category=event.violation_category,
                    operation_type=event.operation_type,
                    source_feature=event.source_feature,
                    target_metadata=_redact_sensitive(event.target_metadata),
                    severity=AuditSeverity.ERROR,
                    correlation_id=event.correlation_id,
                    redacted_reason=event.redacted_reason,
                    event_id=uuid.uuid4().hex[:16],
                    timestamp=time.time(),
                    policy_mode="fallback",
                )

        return emitted

    # ─── Block 3: Dunder Methods, Factories & Helpers ─────
    def __repr__(self) -> str:
        return "AuditEmitter()"
