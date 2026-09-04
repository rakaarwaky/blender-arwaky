"""Tests for SecurityOrchestrator — FR-SEC-003 + FR-SEC-005.

Exercises security orchestration: policy override audit emission, violation
auditing, and aggregate delegation.
Run via pytest from repo root.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

from modules.security.src.agent_security_orchestrator import SecurityOrchestrator
from modules.shared.src.security.taxonomy_security_vo import (
    AuditSeverity,
    CodeValidationVO,
    CodeViolationVO,
    SecurityAuditEventVO,
    ViolationCategory,
)

# ─── Helpers ──────────────────────────────────────────────────────────────────


def _make_orchestrator(
    validate_code_result: CodeValidationVO | None = None,
    emit_audit_sink: AsyncMock | None = None,
) -> tuple[SecurityOrchestrator, AsyncMock]:
    """Create a SecurityOrchestrator with mocked capabilities."""
    mock_validate_code = AsyncMock()
    if validate_code_result is None:
        validate_code_result = CodeValidationVO(code_text="x=1", allowed=True)
    mock_validate_code.validate_code = AsyncMock(return_value=validate_code_result)

    mock_emit_audit = emit_audit_sink or MagicMock()
    mock_emit_audit.emit_audit = AsyncMock()

    mock_validate_path = AsyncMock()
    mock_validate_archive = AsyncMock()
    mock_redact = AsyncMock()

    orchestrator = SecurityOrchestrator(
        validate_path_cap=mock_validate_path,
        validate_archive_cap=mock_validate_archive,
        validate_code_cap=mock_validate_code,
        redact_cap=mock_redact,
        emit_audit_cap=mock_emit_audit,
    )
    return orchestrator, mock_emit_audit


# ─── FR-SEC-005: Policy Override Audit Emission (Finding #8 — P1) ──────────


class TestPolicyOverrideAudit:
    """Test policy override audit event emission (FR-SEC-005 — P1)."""

    def test_disabled_validation_emits_policy_override(self) -> None:
        """FR-SEC-005: when code validation is disabled, orchestrator emits POLICY_OVERRIDE."""
        # CodeValidationVO with validation_disabled_override rule
        override_result = CodeValidationVO(
            code_text="import os",
            allowed=True,
            audit_metadata={"rule": "validation_disabled_override", "severity": "WARNING"},
        )
        orchestrator, mock_emit = _make_orchestrator(validate_code_result=override_result)
        import asyncio

        request = CodeValidationVO(code_text="import os")
        asyncio.run(orchestrator.validate_code(request))
        # Should have emitted POLICY_OVERRIDE event
        assert mock_emit.emit_audit.called
        event = mock_emit.emit_audit.call_args[0][0]
        assert event.violation_category == ViolationCategory.POLICY_OVERRIDE

    def test_policy_override_has_correct_severity(self) -> None:
        """FR-SEC-005: policy override audit has WARNING severity."""
        override_result = CodeValidationVO(
            code_text="import os",
            allowed=True,
            audit_metadata={"rule": "validation_disabled_override"},
        )
        orchestrator, mock_emit = _make_orchestrator(validate_code_result=override_result)
        import asyncio

        asyncio.run(orchestrator.validate_code(CodeValidationVO(code_text="import os")))
        event = mock_emit.emit_audit.call_args[0][0]
        assert event.severity == AuditSeverity.WARNING

    def test_policy_override_has_redacted_reason(self) -> None:
        """FR-SEC-005: policy override audit has redacted reason."""
        override_result = CodeValidationVO(
            code_text="import os",
            allowed=True,
            audit_metadata={"rule": "validation_disabled_override"},
        )
        orchestrator, mock_emit = _make_orchestrator(validate_code_result=override_result)
        import asyncio

        asyncio.run(orchestrator.validate_code(CodeValidationVO(code_text="import os")))
        event = mock_emit.emit_audit.call_args[0][0]
        assert "Code validation disabled by policy" in (event.redacted_reason or "")

    def test_policy_override_not_emitted_when_violations(self) -> None:
        """FR-SEC-005: no policy override when violations exist (CODE_VIOLATION takes precedence)."""
        violation_result = CodeValidationVO(
            code_text="import os",
            allowed=False,
            violations=(CodeViolationVO(category="blocked_module_import", description="Blocked import"),),
            audit_metadata={"rule": "validation_disabled_override"},
        )
        orchestrator, mock_emit = _make_orchestrator(validate_code_result=violation_result)
        import asyncio

        asyncio.run(orchestrator.validate_code(CodeValidationVO(code_text="import os")))
        # Should have emitted CODE_VIOLATION (not POLICY_OVERRIDE) due to if-not-allowed-or-violations
        event = mock_emit.emit_audit.call_args[0][0]
        assert event.violation_category == ViolationCategory.CODE_VIOLATION

    def test_no_audit_when_allowed_without_override(self) -> None:
        """FR-SEC-005: no audit event when code is allowed without override rule."""
        normal_result = CodeValidationVO(
            code_text="x=1",
            allowed=True,
            audit_metadata={"violation_count": 0},
        )
        orchestrator, mock_emit = _make_orchestrator(validate_code_result=normal_result)
        import asyncio

        asyncio.run(orchestrator.validate_code(CodeValidationVO(code_text="x=1")))
        # Should not emit any audit event (allowed=True, no violations, no override rule)
        assert not mock_emit.emit_audit.called

    def test_violations_emits_code_violation(self) -> None:
        """FR-SEC-005: code violations emit CODE_VIOLATION audit event."""
        violation_result = CodeValidationVO(
            code_text="import os",
            allowed=False,
            violations=(CodeViolationVO(category="blocked_module_import", description="Blocked import"),),
        )
        orchestrator, mock_emit = _make_orchestrator(validate_code_result=violation_result)
        import asyncio

        asyncio.run(orchestrator.validate_code(CodeValidationVO(code_text="import os")))
        event = mock_emit.emit_audit.call_args[0][0]
        assert event.violation_category == ViolationCategory.CODE_VIOLATION


class TestOrchestratorDelegation:
    """Test orchestrator delegation to capabilities."""

    def test_validate_path_delegates(self) -> None:
        """FR-SEC-005: validate_path delegates to path capability."""
        mock_validate_path = AsyncMock()
        mock_emit_audit = AsyncMock()
        mock_validate_archive = AsyncMock()
        mock_redact = AsyncMock()
        orchestrator = SecurityOrchestrator(
            validate_path_cap=mock_validate_path,
            validate_archive_cap=mock_validate_archive,
            validate_code_cap=AsyncMock(),
            redact_cap=mock_redact,
            emit_audit_cap=mock_emit_audit,
        )
        import asyncio

        from modules.shared.src.security.taxonomy_security_vo import AccessMode, PathValidationVO

        asyncio.run(orchestrator.validate_path(PathValidationVO(target_path="/safe/file", access_mode=AccessMode.READ)))
        assert mock_validate_path.validate_path.called

    def test_redact_delegates(self) -> None:
        """FR-SEC-005: redact delegates to redact capability."""
        mock_redact = AsyncMock()
        mock_emit_audit = AsyncMock()
        orchestrator = SecurityOrchestrator(
            validate_path_cap=AsyncMock(),
            validate_archive_cap=AsyncMock(),
            validate_code_cap=AsyncMock(),
            redact_cap=mock_redact,
            emit_audit_cap=mock_emit_audit,
        )
        import asyncio

        from modules.shared.src.security.taxonomy_security_vo import RedactionVO

        asyncio.run(orchestrator.redact(RedactionVO(text="test")))
        assert mock_redact.redact.called

    def test_emit_audit_delegates(self) -> None:
        """FR-SEC-005: emit_audit delegates to audit capability."""
        mock_emit_audit = AsyncMock()
        orchestrator = SecurityOrchestrator(
            validate_path_cap=AsyncMock(),
            validate_archive_cap=AsyncMock(),
            validate_code_cap=AsyncMock(),
            redact_cap=AsyncMock(),
            emit_audit_cap=mock_emit_audit,
        )
        import asyncio

        event = SecurityAuditEventVO(violation_category=ViolationCategory.PATH_TRAVERSAL)
        asyncio.run(orchestrator.emit_audit(event))
        assert mock_emit_audit.emit_audit.called


class TestRepresentation:
    """Test class representation."""

    def test_orchestrator_repr(self) -> None:
        """SecurityOrchestrator has a repr."""
        orchestrator = SecurityOrchestrator.__new__(SecurityOrchestrator)
        assert "SecurityOrchestrator" in repr(orchestrator)
