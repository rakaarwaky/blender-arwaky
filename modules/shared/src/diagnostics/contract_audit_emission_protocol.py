"""Diagnostics domain contract: audit emission protocol."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_diagnostics_vo import AuditEventRequestVO, AuditRecordVO


class AuditEmissionProtocol(ABC):
    """Contract protocol for audit log emission.

    FR-DIA-003: Audit log emission with security classification,
    tamper evidence, structured context, and delivery guarantees.
    """

    @abstractmethod
    async def emit_audit_event(
        self,
        request: AuditEventRequestVO,
    ) -> AuditRecordVO:
        """Emit an audit event for security-relevant operations."""
        ...
