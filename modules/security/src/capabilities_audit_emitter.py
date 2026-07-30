"""Capabilities: Audit emitter — FR-SEC-005.

Emits structured security audit events for violations, suspicious activity, and policy overrides.
Implements EmitAuditProtocol.

FR-SEC-004: tokens/credentials/auth tokens must not appear in logs. Audit events are
observability output, so a sensitive value nested in `target_metadata` (or
`redacted_reason`) is redacted at the sink before emission — defense-in-depth that
complements SensitiveRedactor and protects against callers providing raw secrets.
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import Protocol

from modules.shared.src.security.contract_emit_audit_protocol import EmitAuditProtocol
from modules.shared.src.security.taxonomy_security_vo import AuditSeverity, SecurityAuditEventVO
from modules.shared.src.security.utility_security_redactor import redact_sensitive

logger = logging.getLogger(__name__)


class _AuditSink(Protocol):
    """Protocol for delivering audit events to observability (DI boundary)."""

    def deliver(self, event: SecurityAuditEventVO) -> None: ...


class AuditEmitter(EmitAuditProtocol):
    """Emits structured security audit events with fallback on sink failure."""

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(
        self,
        sink: _AuditSink | None = None,
        fallback_buffer: list[SecurityAuditEventVO] | None = None,
    ) -> None:
        self._sink = sink
        self._fallback_buffer: list[SecurityAuditEventVO] = (
            fallback_buffer if fallback_buffer is not None else []
        )

    # ─── Block 2: Public Contract  ────────────────────────
    async def emit_audit(self, event: SecurityAuditEventVO) -> SecurityAuditEventVO:
        """Emit a structured security audit event for violations and policy activity.

        FR-SEC-004: redact sensitive values from `target_metadata` / `redacted_reason`
        before emission so secrets never reach the observability sink, regardless of
        whether the caller pre-redacted. The caller's input event is never mutated.

        FR-SEC-005: when sink delivery fails, creates a fallback record stored in
        _fallback_buffer instead of discarding it.
        """
        raw_meta = redact_sensitive(event.target_metadata) if event.target_metadata else {}
        safe_metadata = raw_meta if isinstance(raw_meta, dict) else {}
        raw_reason = redact_sensitive(event.redacted_reason) if event.redacted_reason else None
        safe_reason = str(raw_reason) if raw_reason is not None else None

        emitted = SecurityAuditEventVO(
            violation_category=event.violation_category,
            operation_type=event.operation_type,
            source_feature=event.source_feature,
            target_metadata=safe_metadata,
            severity=event.severity,
            correlation_id=event.correlation_id,
            redacted_reason=safe_reason,
            event_id=uuid.uuid4().hex[:16],
            timestamp=time.time(),
            policy_mode=event.policy_mode,
        )

        if self._sink:
            try:
                self._sink.deliver(emitted)
            except Exception as exc:
                exc_str = redact_sensitive(str(exc))
                safe_exc = str(exc_str)
                fallback = SecurityAuditEventVO(
                    violation_category=event.violation_category,
                    operation_type=event.operation_type,
                    source_feature=event.source_feature,
                    target_metadata=safe_metadata,
                    severity=AuditSeverity.ERROR,
                    correlation_id=event.correlation_id,
                    redacted_reason=safe_exc,
                    event_id=uuid.uuid4().hex[:16],
                    timestamp=time.time(),
                    policy_mode="fallback",
                )
                self._fallback_buffer.append(fallback)
                logger.warning(
                    "Audit sink delivery failed; fallback record created: %s",
                    safe_exc,
                )
        else:
            self._fallback_buffer.append(emitted)

        return emitted

    # ─── Block 3: Dunder Methods, Factories & Helpers ─────
    def __repr__(self) -> str:
        return "AuditEmitter()"
