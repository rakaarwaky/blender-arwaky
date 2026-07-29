"""Diagnostics domain contract: audit emission protocol (ABC based).

Defines the protocol for producing immutable audit records for
security-relevant and operationally significant activity.

FR-DIA-003: Emit Audit Events
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_diagnostics_vo import AuditRecordVO


class AuditEmissionProtocol(ABC):
    """Protocol for emitting immutable audit records."""

    @abstractmethod
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

        FR-DIA-003: Auditable activity includes security violations,
        connection failures, task failures, and destructive actions.
        Audit records are immutable once emitted (frozen dataclass);
        correction = new record with same category + correlation_id + new timestamp.
        Redaction applied before emission — no raw code/tokens/credentials/paths.

        Args:
            category: Event category (security_violation, connection_failure, etc.).
            severity: Severity level (critical, warning, info).
            source_feature: Feature that originated the event.
            operation_type: Type of operation performed.
            target_metadata: Optional redacted target metadata.
            correlation_id: Optional correlation/tracking identifier.

        Returns:
            AuditRecordVO with emission confirmation and emitted metadata.
        """
        ...
