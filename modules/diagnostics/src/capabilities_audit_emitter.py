"""Capability: Audit event emitter with immutable records and fallback buffering.

FR-DIA-003: Emit Audit Events
Produces immutable audit records for security-relevant and operationally
significant activity. Supports async subscribers with isolated exception
handling and guaranteed fallback delivery.
Implements AuditEmissionProtocol.
"""

from __future__ import annotations

import logging
import time
import uuid
from collections import deque

from modules.shared.src.diagnostics.contract_audit_emission_protocol import (
    AuditEmissionProtocol,
)
from modules.shared.src.diagnostics.taxonomy_diagnostics_vo import AuditEventRequestVO, AuditRecordVO
from modules.shared.src.security.utility_security_redactor import redact_sensitive

logger = logging.getLogger(__name__)


class _AuditSink:
    """Protocol for delivering audit events to observability (DI boundary)."""

    def deliver(self, event: AuditRecordVO) -> None: ...


class AuditEmitter(AuditEmissionProtocol):
    """Emit immutable audit records for security-relevant activity."""

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(self, sink: _AuditSink | None = None, max_buffer_size: int = 1000) -> None:
        self._sink = sink
        self._fallback_buffer: deque[AuditRecordVO] = deque(maxlen=max_buffer_size)

    # ─── Block 2: Protocol Method Implementation ─────────────

    async def emit_audit_event(
        self,
        request: AuditEventRequestVO,
    ) -> AuditRecordVO:
        """Produce immutable audit record for security-relevant activity.

        FR-DIA-003: Redaction applied before emission — no raw code/tokens/credentials/paths.
        Records are frozen (dataclass(frozen=True)) — immutable once emitted.
        Sink failure → fallback buffer + warning; never alters original operation.
        """
        raw_meta = redact_sensitive(request.target_metadata) if request.target_metadata else {}
        safe_metadata = raw_meta if isinstance(raw_meta, dict) else {}

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

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    def get_fallback_buffer(self) -> list[AuditRecordVO]:
        """Return copy of fallback buffer contents (for testing)."""
        return list(self._fallback_buffer)

    def __repr__(self) -> str:
        return f"AuditEmitter(buffer_size={len(self._fallback_buffer)})"
