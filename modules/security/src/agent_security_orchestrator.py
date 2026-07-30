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
  3. Helpers moved to Block 3
"""

from modules.shared.src.security.contract_emit_audit_protocol import EmitAuditProtocol
from modules.shared.src.security.contract_extract_archive_protocol import ExtractArchiveProtocol
from modules.shared.src.security.contract_redact_sensitive_protocol import RedactSensitiveProtocol
from modules.shared.src.security.contract_security_operate_aggregate import ISecurityOperateAggregate
from modules.shared.src.security.contract_validate_code_protocol import ValidateCodeProtocol
from modules.shared.src.security.contract_validate_path_protocol import ValidatePathProtocol
from modules.shared.src.security.taxonomy_security_constant import SECURITY_SOURCE_FEATURE
from modules.shared.src.security.taxonomy_security_vo import (
    ArchiveExtractionVO,
    AuditSeverity,
    CodeValidationVO,
    PathValidationVO,
    RedactionVO,
    SecurityAuditEventVO,
    ViolationCategory,
)


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

    async def validate_path(self, request: PathValidationVO) -> PathValidationVO:
        """Delegate path validation to the capabilities layer and emit audit on denial."""
        result = await self._validate_path.validate_path(request)

        if not result.allowed:
            await self._emit_audit.emit_audit(
                SecurityAuditEventVO(
                    violation_category=ViolationCategory.PATH_TRAVERSAL,
                    operation_type="validate_path",
                    source_feature=SECURITY_SOURCE_FEATURE,
                    target_metadata=result.audit_metadata,
                    severity=AuditSeverity.WARNING,
                    redacted_reason=result.denial_reason or "Path validation denied",
                )
            )

        return result

    async def validate_extraction(self, request: ArchiveExtractionVO) -> ArchiveExtractionVO:
        """Delegate archive extraction validation and emit audit on denial/rejection."""
        result = await self._validate_archive.validate_extraction(request)

        if not result.allowed or result.rejected_entries:
            await self._emit_audit.emit_audit(
                SecurityAuditEventVO(
                    violation_category=ViolationCategory.UNSAFE_ARCHIVE_ENTRY,
                    operation_type="validate_extraction",
                    source_feature=SECURITY_SOURCE_FEATURE,
                    target_metadata=result.audit_metadata,
                    severity=AuditSeverity.WARNING,
                    redacted_reason="Archive extraction denied or entries rejected",
                )
            )

        return result

    async def validate_code(self, request: CodeValidationVO) -> CodeValidationVO:
        """Delegate code validation and emit audit on denial/violations/override."""
        result = await self._validate_code.validate_code(request)

        if not result.allowed or result.violations:
            await self._emit_audit.emit_audit(
                SecurityAuditEventVO(
                    violation_category=ViolationCategory.CODE_VIOLATION,
                    operation_type="validate_code",
                    source_feature=SECURITY_SOURCE_FEATURE,
                    target_metadata=result.audit_metadata,
                    severity=AuditSeverity.WARNING,
                    redacted_reason="Code validation denied",
                )
            )
        elif result.audit_metadata.get("rule") == "validation_disabled_override":
            # FR-SEC-005: policy override must produce audit event
            await self._emit_audit.emit_audit(
                SecurityAuditEventVO(
                    violation_category=ViolationCategory.POLICY_OVERRIDE,
                    operation_type="validate_code",
                    source_feature=SECURITY_SOURCE_FEATURE,
                    target_metadata=result.audit_metadata,
                    severity=AuditSeverity.WARNING,
                    redacted_reason="Code validation disabled by policy",
                )
            )

        return result

    async def redact(self, request: RedactionVO) -> RedactionVO:
        """Delegate redaction and emit audit on failure."""
        result = await self._redact.redact(request)

        if result.failed:
            await self._emit_audit.emit_audit(
                SecurityAuditEventVO(
                    violation_category=ViolationCategory.REDACTION_FAILURE,
                    operation_type="redact",
                    source_feature=SECURITY_SOURCE_FEATURE,
                    target_metadata={},
                    severity=AuditSeverity.ERROR,
                    redacted_reason=result.failure_reason or "Redaction failed",
                )
            )

        return result

    async def emit_audit(self, event: SecurityAuditEventVO) -> SecurityAuditEventVO:
        """Delegate audit emission to the capabilities layer."""
        return await self._emit_audit.emit_audit(event)

    # ─── Block 3: Dunder Methods, Factories & Helpers ─────

    @property
    def security_operate_capability(self) -> ISecurityOperateAggregate:
        """Expose self as the security operate aggregate facade for dispatch."""
        return self

    def __repr__(self) -> str:
        return "SecurityOrchestrator()"
