"""Diagnostics domain contract: audit emission protocol (ABC based).

Defines the protocol for producing immutable audit records for
security-relevant and operationally significant activity.

FR-DIA-003: Emit Audit Events
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AuditEmissionProtocol(ABC):
    """Protocol for emitting immutable audit records."""

    @abstractmethod
    async def emit_audit_event(
        self,
        category: str,
        severity: str,
        source_feature: str,
        operation_type: str,
        correlation_id: str | None = None,
    ) -> dict[str, Any]:
        """Produce immutable audit record for security-relevant activity.

        FR-DIA-003: Auditable activity includes security violations,
        connection failures, task failures, and destructive actions.
        Audit records are immutable once emitted; content passes redaction.

        Args:
            category: Event category (security_violation, connection_failure, etc.).
            severity: Severity level (critical, warning, info).
            source_feature: Feature that originated the event.
            operation_type: Type of operation performed.
            correlation_id: Optional correlation/tracking identifier.

        Returns:
            Dict with audit record confirmation and emitted metadata.
        """
        pass
