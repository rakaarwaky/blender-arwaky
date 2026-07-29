"""Security feature orchestrator implementing SecurityOperateAggregate.

FR-SEC-001: Validate File Path Access — validate_path() checks path safety and access rules
FR-SEC-002: Safely Extract Archive — extract_archive() delegates to security extraction policy
FR-SEC-003: Validate Untrusted Code — validate_code() inspects code for unsafe patterns
FR-SEC-004: Redact Sensitive Values — redact() removes secrets/tokens/credentials from output
FR-SEC-005: Emit Security Audit Events — emit_audit() records security events for diagnostics

Coordinates security flows via the SecurityOperateAggregate contract.
Orchestration only — no business logic, depends on individual capability protocols.

Structure:
  1. Constants & imports
  2. SecurityOrchestrator — implements aggregate, delegates to 5 individual protocols
"""

import logging

from modules.shared.src.security.contract_emit_audit_protocol import EmitAuditProtocol
from modules.shared.src.security.contract_extract_archive_protocol import ExtractArchiveProtocol
from modules.shared.src.security.contract_redact_sensitive_protocol import RedactSensitiveProtocol
from modules.shared.src.security.contract_security_operate_aggregate import ISecurityOperateAggregate
from modules.shared.src.security.contract_validate_code_protocol import ValidateCodeProtocol
from modules.shared.src.security.contract_validate_path_protocol import ValidatePathProtocol
from modules.shared.src.security.taxonomy_security_vo import (
    ArchiveExtractionVO,
    CodeValidationVO,
    PathValidationVO,
    RedactionVO,
    SecurityAuditEventVO,
)

logger = logging.getLogger(__name__)


class SecurityOrchestrator(ISecurityOperateAggregate):
    """Orchestrates security operations through 5 individual capability protocols."""

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(
        self,
        validate_path_cap: ValidatePathProtocol,
        validate_archive_cap: ExtractArchiveProtocol,
        validate_code_cap: ValidateCodeProtocol,
        redact_cap: RedactSensitiveProtocol,
        emit_audit_cap: EmitAuditProtocol,
    ) -> None:
        self._validate_path = validate_path_cap
        self._validate_archive = validate_archive_cap
        self._validate_code = validate_code_cap
        self._redact = redact_cap
        self._emit_audit = emit_audit_cap

    # ─── Block 2: Aggregate Implementation ───────────────────

    async def _delegate(self, method, request):
        """Delegate to a capability method with correlation_id logging."""
        corr = getattr(request, 'correlation_id', None) or "n/a"
        logger.info("Orchestrating %s corr=%s", method.__name__, corr)
        return await method(request)

    async def validate_path(self, request: PathValidationVO) -> PathValidationVO:
        """Delegate path validation to the capabilities layer."""
        return await self._delegate(self._validate_path.validate_path, request)

    async def validate_extraction(self, request: ArchiveExtractionVO) -> ArchiveExtractionVO:
        """Delegate archive extraction validation to the capabilities layer."""
        return await self._delegate(self._validate_archive.validate_extraction, request)

    async def validate_code(self, request: CodeValidationVO) -> CodeValidationVO:
        """Delegate code validation to the capabilities layer."""
        return await self._delegate(self._validate_code.validate_code, request)

    async def redact(self, request: RedactionVO) -> RedactionVO:
        """Delegate redaction to the capabilities layer."""
        return await self._delegate(self._redact.redact, request)

    async def emit_audit(self, event: SecurityAuditEventVO) -> SecurityAuditEventVO:
        """Delegate audit emission to the capabilities layer."""
        return await self._delegate(self._emit_audit.emit_audit, event)

    # ─── Block 3: Dunder Methods, Factories & Helpers ─────

    @property
    def security_operate_capability(self) -> ISecurityOperateAggregate:
        """Expose self as the security operate aggregate facade for dispatch."""
        return self

    def __repr__(self) -> str:
        return "SecurityOrchestrator()"
