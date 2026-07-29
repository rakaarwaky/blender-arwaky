"""End-to-end smoke test for the security feature (FRD FR-SEC-001..005).

Exercises all 5 capabilities through the SecurityContainer aggregate and
verifies FRD business rules hold. Run via pytest from repo root.

Requires the ``mcp`` namespace shim from conftest.py (modules.shared.src is
currently broken without it).

All aggregate methods are ``async def``; with ``asyncio_mode = "auto"`` in
pyproject.toml, async test functions are awaited automatically.
"""

from __future__ import annotations

import os

from modules.security.src import create_security_feature
from modules.shared.src.security.taxonomy_security_event import (
    PolicyOverrideEvent,
    RedactionFailureEvent,
    SecurityAuditEvent,
    SecurityViolationEvent,
)
from modules.shared.src.security.taxonomy_security_vo import (
    AccessMode,
    ArchiveEntryVO,
    ArchiveExtractionOptionsVO,
    ArchiveExtractionVO,
    AuditSeverity,
    CodeValidationVO,
    PathValidationVO,
    RedactionVO,
    SecurityAuditEventVO,
    SecurityPolicyVO,
    SensitivityLevel,
    ViolationCategory,
)

# ─── FR-SEC-001: Validate File Path Access ─────────────────────────────────

async def test_fr_sec_001_allows_path_inside_allowed_dir():
    feat = create_security_feature(SecurityPolicyVO(allowed_directories=("/safe",)))
    res = await feat.validate_path(PathValidationVO(
        target_path="/safe/project/main.blend", access_mode=AccessMode.WRITE))
    assert res.allowed is True
    assert res.canonical_path == os.path.normpath("/safe/project/main.blend")


async def test_fr_sec_001_rejects_traversal():
    feat = create_security_feature(SecurityPolicyVO(allowed_directories=("/safe",)))
    res = await feat.validate_path(PathValidationVO(
        target_path="/safe/../etc/passwd", access_mode=AccessMode.WRITE))
    assert res.allowed is False
    # After normalization, /safe/../etc/passwd -> /etc/passwd (no ".." left).
    # It's rejected by the allowed-dirs check, not the traversal check.
    assert res.denial_reason in ("Path traversal detected", "Path outside allowed directories")


async def test_fr_sec_001_rejects_out_of_bounds():
    feat = create_security_feature(SecurityPolicyVO(allowed_directories=("/safe",)))
    res = await feat.validate_path(PathValidationVO(
        target_path="/etc/passwd", access_mode=AccessMode.READ))
    assert res.allowed is False
    assert res.denial_reason == "Path outside allowed directories"


async def test_fr_sec_001_rejects_empty_path():
    feat = create_security_feature()
    res = await feat.validate_path(PathValidationVO(target_path="", access_mode=AccessMode.READ))
    assert res.allowed is False
    assert res.denial_reason == "Empty path"


async def test_fr_sec_001_resolves_relative_against_base():
    feat = create_security_feature(SecurityPolicyVO(allowed_directories=("/safe",)))
    res = await feat.validate_path(PathValidationVO(
        target_path="main.blend", access_mode=AccessMode.WRITE,
        base_directory="/safe/project"))
    assert res.allowed is True
    assert res.canonical_path.endswith("main.blend")


# ─── FR-SEC-002: Safely Extract Archive ────────────────────────────────────

async def _extract(feat, entries, options=None):
    return await feat.validate_extraction(ArchiveExtractionVO(
        destination_directory="/safe/out", entries=tuple(entries),
        options=options or ArchiveExtractionOptionsVO()))


async def test_fr_sec_002_rejects_absolute_entry():
    feat = create_security_feature()
    res = await _extract(feat, [ArchiveEntryVO(entry_path="/etc/passwd")])
    assert res.allowed is False
    assert res.rejected_entries


async def test_fr_sec_002_rejects_traversal_entry():
    feat = create_security_feature()
    res = await _extract(feat, [ArchiveEntryVO(entry_path="../escape")])
    assert res.allowed is False
    assert any("traversal" in r.reason.lower() for r in res.rejected_entries)


async def test_fr_sec_002_rejects_symlink_by_default():
    feat = create_security_feature()
    res = await _extract(feat, [ArchiveEntryVO(entry_path="link", is_symbolic_link=True)])
    assert res.allowed is False
    assert any("Symbolic link" in r.reason for r in res.rejected_entries)


async def test_fr_sec_002_enforces_entry_count():
    feat = create_security_feature()
    entries = [ArchiveEntryVO(entry_path=f"f{i}") for i in range(10)]
    res = await _extract(feat, entries, ArchiveExtractionOptionsVO(max_entry_count=2))
    assert res.allowed is False
    assert len(res.rejected_entries) >= 8


async def test_fr_sec_002_enforces_total_size():
    feat = create_security_feature()
    entries = [ArchiveEntryVO(entry_path="big", uncompressed_size=200)]
    res = await _extract(feat, entries, ArchiveExtractionOptionsVO(max_total_size=100))
    assert res.allowed is False
    # Total-size breach is reported via warnings (FR-SEC-002 output shape).
    assert any("size" in w.lower() for w in res.warnings)


async def test_fr_sec_002_allows_clean_entries():
    feat = create_security_feature()
    res = await _extract(feat, [ArchiveEntryVO(entry_path="a.txt"), ArchiveEntryVO(entry_path="sub/b.txt")])
    assert res.allowed is True
    assert res.safe_destination == os.path.normpath("/safe/out")


# ─── FR-SEC-003: Validate Untrusted Code ──────────────────────────────────

async def test_fr_sec_003_blocks_dangerous_import():
    feat = create_security_feature()
    res = await feat.validate_code(CodeValidationVO(
        code_text="import os\nos.system('rm -rf /')", strict_mode=True))
    assert res.allowed is False
    assert any("blocked_module_import" in v.category for v in res.violations)


async def test_fr_sec_003_blocks_eval_call():
    feat = create_security_feature()
    res = await feat.validate_code(CodeValidationVO(code_text="eval('1+1')", strict_mode=True))
    assert res.allowed is False
    assert any("blocked_function_call" in v.category for v in res.violations)


async def test_fr_sec_003_rejects_oversized():
    feat = create_security_feature()
    res = await feat.validate_code(CodeValidationVO(code_text="x=1", max_code_size=2, strict_mode=True))
    assert res.allowed is False
    assert any("size_limit" in v.category for v in res.violations)


async def test_fr_sec_003_strict_rejects_syntax_error():
    feat = create_security_feature()
    res = await feat.validate_code(CodeValidationVO(code_text="def (:", strict_mode=True))
    assert res.allowed is False
    assert any("syntax_error" in v.category for v in res.violations)


async def test_fr_sec_003_disabled_override_warns():
    feat = create_security_feature(SecurityPolicyVO(code_validation_enabled=False))
    res = await feat.validate_code(CodeValidationVO(
        code_text="import os\nos.system('x')", strict_mode=True))
    assert res.allowed is True
    assert res.audit_metadata.get("rule") == "validation_disabled_override"


async def test_fr_sec_003_allows_safe_code():
    feat = create_security_feature()
    res = await feat.validate_code(CodeValidationVO(
        code_text="x = 1 + 2\nprint(x)", strict_mode=True))
    assert res.allowed is True


# ─── FR-SEC-004: Redact Sensitive Values ──────────────────────────────────

async def test_fr_sec_004_redacts_password_pattern():
    feat = create_security_feature()
    res = await feat.redact(RedactionVO(
        text="password=supersecret", sensitivity_level=SensitivityLevel.HIGH))
    assert "supersecret" not in res.redacted_text
    assert res.redacted_count >= 1


async def test_fr_sec_004_redacts_api_key_by_name():
    feat = create_security_feature()
    res = await feat.redact(RedactionVO(
        text="api_key=abc123xyz", sensitivity_level=SensitivityLevel.HIGH,
        key_names=("api_key",)))
    assert "abc123xyz" not in res.redacted_text


async def test_fr_sec_004_key_and_pattern_detection():
    feat = create_security_feature()
    res = await feat.redact(RedactionVO(
        text="token=bearer-xyz and password=hunter2",
        sensitivity_level=SensitivityLevel.CRITICAL))
    assert "bearer-xyz" not in res.redacted_text
    assert "hunter2" not in res.redacted_text


async def test_fr_sec_004_returned_text_is_leak_free():
    # FR-SEC-004: the primary `text` field of the returned VO must never carry
    # the raw secret — consumers reading `.text` (not just `.redacted_text`)
    # must stay leak-free.
    feat = create_security_feature()
    res = await feat.redact(RedactionVO(
        text="password=supersecret token=abc123xyz",
        sensitivity_level=SensitivityLevel.HIGH))
    assert "supersecret" not in res.text
    assert "abc123xyz" not in res.text
    assert res.text == res.redacted_text
    assert res.failed is False


async def test_fr_sec_004_redacts_json_quoted_secrets():
    # FR-SEC-004 edge cases: "secret inside text blob" / "nested structure".
    # JSON-formatted secrets were previously leaked because the key-based
    # pattern only matched the unquoted shell `key=value` form.
    feat = create_security_feature()
    text = 'config = {"password": "hunter2", "api_key": "sk-abcdefghijklmnopqrstuvwx"}'
    res = await feat.redact(RedactionVO(text=text, sensitivity_level=SensitivityLevel.HIGH))
    assert "hunter2" not in res.text
    assert "sk-abcdefghijklmnopqrstuvwx" not in res.text
    assert res.redacted_count >= 2


async def test_fr_sec_004_redacts_json_quoted_custom_key():
    # Custom key_names must also match JSON/`"key": "value"` forms.
    feat = create_security_feature()
    text = 'payload = {"session_token": "tok-9f8e7d6c5b4a"}'
    res = await feat.redact(RedactionVO(
        text=text, sensitivity_level=SensitivityLevel.HIGH, key_names=("session_token",)))
    assert "tok-9f8e7d6c5b4a" not in res.text


async def test_fr_sec_004_redacts_spaced_json_quoted_secret():
    # FR-SEC-004 edge case (cycle-43 known limitation): a quoted secret containing
    # an internal space — `"password": "my secret"` — was only partially redacted
    # (`secret"` leaked) because the value matcher stopped at whitespace. The value
    # half now honors a matched closing quote, consuming the whole quoted value.
    feat = create_security_feature()
    text = 'config = {"password": "my secret", "api_key": "sk-1 2 3"}'
    res = await feat.redact(RedactionVO(text=text, sensitivity_level=SensitivityLevel.HIGH))
    assert "my secret" not in res.text
    assert "secret" not in res.text          # no partial `"secret"` leak
    assert "sk-1 2 3" not in res.text
    assert res.redacted_count >= 2


async def test_fr_sec_004_failure_masks_payload():
    # FR-SEC-004: redaction failure must mask the entire payload, never echo
    # the original secret back in `text`.
    feat = create_security_feature()
    res = await feat.redact(RedactionVO(
        text="password=supersecret",
        sensitivity_level=SensitivityLevel.HIGH,
        patterns=("(",)))  # invalid regex -> forces the except path
    assert res.failed is True
    assert res.text == "[REDACTION_FAILED]"
    assert res.redacted_text == "[REDACTION_FAILED]"
    assert "supersecret" not in res.text


# ─── FR-SEC-005: Emit Security Audit Events ───────────────────────────────

async def test_fr_sec_005_emits_event_with_id_and_timestamp():
    feat = create_security_feature()
    event = SecurityAuditEventVO(
        violation_category=ViolationCategory.PATH_TRAVERSAL,
        operation_type="validate_path", source_feature="asset",
        severity=AuditSeverity.WARNING, redacted_reason="traversal blocked")
    out = await feat.emit_audit(event)
    assert out.event_id
    assert out.timestamp > 0
    assert out.violation_category == ViolationCategory.PATH_TRAVERSAL


async def test_fr_sec_005_fallback_when_sink_unavailable():
    # Default container has no sink; emit must still return a valid event.
    feat = create_security_feature()
    out = await feat.emit_audit(SecurityAuditEventVO(
        violation_category=ViolationCategory.CODE_VIOLATION,
        operation_type="validate_code", source_feature="gateway"))
    assert out.event_id


async def test_fr_sec_005_redacts_secret_in_target_metadata():
    # FR-SEC-004: secrets must not appear in audit/observability output.
    feat = create_security_feature()
    secret = "sk-abcdefghijklmnopqrstuvwxyz"
    event = SecurityAuditEventVO(
        violation_category=ViolationCategory.UNAUTHORIZED_ACCESS,
        operation_type="connect", source_feature="gateway",
        target_metadata={"endpoint": "wss://host", "auth": f"token={secret}"},
    )
    out = await feat.emit_audit(event)
    assert out.event_id
    # emitted metadata is masked; caller input is left untouched
    assert secret not in str(out.target_metadata)
    assert "[REDACTED]" in str(out.target_metadata)
    assert event.target_metadata["auth"] == f"token={secret}"
    # nested dict + list values are walked
    deep = SecurityAuditEventVO(
        violation_category=ViolationCategory.PATH_TRAVERSAL,
        target_metadata={"nested": {"pw": "password=hunter2"}, "list": ["api_key=abc123xyz"]},
    )
    deep_out = await feat.emit_audit(deep)
    assert "hunter2" not in str(deep_out.target_metadata)
    assert "abc123xyz" not in str(deep_out.target_metadata)


async def test_fr_sec_005_redacts_secret_in_json_metadata():
    # FR-SEC-004: a JSON body nested as an audit-metadata string must be
    # redacted at the emit boundary (quoted-key pattern now matches JSON).
    feat = create_security_feature()
    event = SecurityAuditEventVO(
        violation_category=ViolationCategory.UNAUTHORIZED_ACCESS,
        operation_type="connect", source_feature="gateway",
        target_metadata={"config": '{"password": "hunter2"}'},
    )
    out = await feat.emit_audit(event)
    assert out.event_id
    assert "hunter2" not in str(out.target_metadata)
    assert "[REDACTED]" in str(out.target_metadata)
    # caller input left untouched
    assert event.target_metadata["config"] == '{"password": "hunter2"}'


async def test_fr_sec_005_redacts_spaced_secret_in_json_metadata():
    # FR-SEC-004: a JSON body nested as an audit-metadata string with a spaced
    # quoted secret (`"password": "my secret"`) must be fully redacted at the emit
    # boundary — closes the same cycle-43 partial-redaction leak at the audit sink.
    feat = create_security_feature()
    event = SecurityAuditEventVO(
        violation_category=ViolationCategory.UNAUTHORIZED_ACCESS,
        operation_type="connect", source_feature="gateway",
        target_metadata={"config": '{"password": "my secret"}'},
    )
    out = await feat.emit_audit(event)
    assert out.event_id
    assert "my secret" not in str(out.target_metadata)
    assert "secret" not in str(out.target_metadata)
    assert "[REDACTED]" in str(out.target_metadata)
    # caller input left untouched
    assert event.target_metadata["config"] == '{"password": "my secret"}'


async def test_fr_sec_005_redacts_secret_in_redacted_reason():
    feat = create_security_feature()
    out = await feat.emit_audit(SecurityAuditEventVO(
        violation_category=ViolationCategory.CODE_VIOLATION,
        operation_type="validate_code", source_feature="gateway",
        redacted_reason="blocked literal api_key=supersecretvalue",
    ))
    assert "supersecretvalue" not in (out.redacted_reason or "")


# ─── Layered value objects / events are importable ────────────────────────

def test_taxonomy_events_present():
    assert SecurityViolationEvent.event_category == "security_violation"
    assert SecurityAuditEvent.event_category == "security_audit"
    assert RedactionFailureEvent.event_category == "redaction_failure"
    assert PolicyOverrideEvent.event_category == "policy_override"
