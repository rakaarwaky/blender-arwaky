"""Security domain contract: emit audit protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.
FR-SEC-005: Emit Security Audit Events.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_security_vo import SecurityAuditEventVO


class EmitAuditProtocol(ABC):
    """Protocol interface for emitting structured security audit events."""

    @abstractmethod
    async def emit_audit(self, event: SecurityAuditEventVO) -> SecurityAuditEventVO:
        """Emit a structured security audit event for violations and policy activity."""
        ...