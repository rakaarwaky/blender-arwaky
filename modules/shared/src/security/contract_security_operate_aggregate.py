"""Security domain contract: security operate aggregate (ABC).

Agent implements this aggregate. Surface layers depend on it.
Facade for all 5 security operations: path, archive, code, redaction, audit.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_security_vo import (
    ArchiveExtractionVO,
    CodeValidationVO,
    PathValidationVO,
    RedactionVO,
    SecurityAuditEventVO,
)


class ISecurityOperateAggregate(ABC):
    """Aggregate facade for all security operations.

    The Agent orchestrator implements this interface.
    Surface layers call through this aggregate.
    """

    @abstractmethod
    async def validate_path(self, request: PathValidationVO) -> PathValidationVO:
        """FR-SEC-001: Validate filesystem path access."""
        ...

    @abstractmethod
    async def validate_extraction(self, request: ArchiveExtractionVO) -> ArchiveExtractionVO:
        """FR-SEC-002: Validate archive extraction safety."""
        ...

    @abstractmethod
    async def validate_code(self, request: CodeValidationVO) -> CodeValidationVO:
        """FR-SEC-003: Validate untrusted code before execution."""
        ...

    @abstractmethod
    async def redact(self, request: RedactionVO) -> RedactionVO:
        """FR-SEC-004: Detect and redact sensitive values."""
        ...

    @abstractmethod
    async def emit_audit(self, event: SecurityAuditEventVO) -> SecurityAuditEventVO:
        """FR-SEC-005: Emit structured security audit event."""
        ...