"""Capabilities: Audit emitter — FR-SEC-005.

Emits structured security audit events for violations, suspicious activity, and policy overrides.
Implements EmitAuditProtocol.
"""

from __future__ import annotations

import contextlib
import time
import uuid
from typing import Protocol

from modules.shared.src.security.contract_emit_audit_protocol import EmitAuditProtocol
from modules.shared.src.security.taxonomy_security_vo import SecurityAuditEventVO


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
        """Emit a structured security audit event for violations and policy activity."""
        emitted = SecurityAuditEventVO(
            violation_category=event.violation_category,
            operation_type=event.operation_type,
            source_feature=event.source_feature,
            target_metadata=event.target_metadata,
            severity=event.severity,
            correlation_id=event.correlation_id,
            redacted_reason=event.redacted_reason,
            event_id=uuid.uuid4().hex[:16],
            timestamp=time.time(),
            policy_mode=event.policy_mode,
        )

        if self._sink:
            with contextlib.suppress(Exception):
                self._sink.deliver(emitted)

        return emitted

    # ─── Block 3: Dunder Methods, Factories & Helpers ─────
    def __repr__(self) -> str:
        return "AuditEmitter()"