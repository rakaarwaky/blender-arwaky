"""Diagnostics domain contract: audit emission protocol (ABC based).

Defines the protocol for producing immutable audit records for
security-relevant and operationally significant activity.

FR-DIA-003: Emit Audit Events
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_diagnostics_vo import AuditEventRequestVO, AuditRecordVO


class AuditEmissionProtocol(ABC):
    """Protocol for emitting immutable audit records."""

    @abstractmethod
    async def emit_audit_event(
        self,
        request: AuditEventRequestVO,
    ) -> AuditRecordVO:
        """Produce immutable audit record for security-relevant activity.

        FR-DIA-003: Auditable activity includes security violations,
        connection failures, task failures, and destructive actions.
        Audit records are immutable once emitted (frozen dataclass);
        correction = new record with same category + correlation_id + new timestamp.
        Redaction applied before emission — no raw code/tokens/credentials/paths.
        """
        ...
