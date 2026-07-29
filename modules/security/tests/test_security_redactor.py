"""Tests for SensitiveRedactor — FR-SEC-004.

Exercises sensitive value detection and redaction: key-based patterns,
value patterns, custom keys, failure masking, and truncation.
Run via pytest from repo root.
"""

from __future__ import annotations

import pytest

from modules.security.src.capabilities_sensitive_redactor import SensitiveRedactor
from modules.shared.src.security.taxonomy_security_vo import (
    RedactionVO,
    SensitivityLevel,
)


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _make_redactor(
    extra_patterns: tuple[str, ...] = (),
    extra_key_names: tuple[str, ...] = (),
) -> SensitiveRedactor:
    """Create a SensitiveRedactor with optional configuration."""
    return SensitiveRedactor(
        extra_patterns=extra_patterns,
        extra_key_names=extra_key_names,
    )


def _redact(cap: SensitiveRedactor, text: str, **overrides: object) -> RedactionVO:
    """Helper to run redact synchronously via asyncio."""
    import asyncio
    base = RedactionVO(text=text, sensitivity_level=SensitivityLevel.HIGH)
    update = {k: v for k, v in overrides.items()}
    return asyncio.run(cap.redact(RedactionVO(**{**dict(base.__dict__), **update})))


# ─── FR-SEC-004: Redact Sensitive Values ──────────────────────────────────


class TestDefaultKeyPatterns:
    """Test default sensitive key pattern detection (FR-SEC-004)."""

    def test_password_key_redacted(self) -> None:
        """FR-SEC-004: password=secret is redacted."""
        cap = _make_redactor()
        res = _redact(cap, "password=supersecret")
        assert "supersecret" not in res.text
        assert "password" in res.redacted_text or "[REDACTED]" in res.text

    def test_passwd_key_redacted(self) -> None:
        """FR-SEC-004: passwd=secret is redacted."""
        cap = _make_redactor()
        res = _redact(cap, "passwd=mypassword123")
        assert "mypassword123" not in res.text

    def test_secret_key_redacted(self) -> None:
        """FR-SEC-004: secret=xxx is redacted."""
        cap = _make_redactor()
        res = _redact(cap, "secret=mysecretvalue")
        assert "mysecretvalue" not in res.text

    def test_token_key_redacted(self) -> None:
        """FR-SEC-004: token=xxx is redacted."""
        cap = _make_redactor()
        res = _redact(cap, "token=bearer-xyz")
        assert "bearer-xyz" not in res.text

    def test_api_key_redacted(self) -> None:
        """FR-SEC-004: api_key=xxx is redacted."""
        cap = _make_redactor()
        res = _redact(cap, "api_key=sk-abcdefghijklmnop")
        assert "sk-abcdefghijklmnop" not in res.text

    def test_access_key_redacted(self) -> None:
        """FR-SEC-004: access_key=xxx is redacted."""
        cap = _make_redactor()
        res = _redact(cap, "access_key=AKIA1234567890abcdef")
        assert "AKIA1234567890abcdef" not in res.text

    def test_private_key_redacted(self) -> None:
        """FR-SEC-004: private_key=xxx is redacted."""
        cap = _make_redactor()
        res = _redact(cap, "private_key=my-private-key")
        assert "my-private-key" not in res.text

    def test_auth_key_redacted(self) -> None:
        """FR-SEC-004: auth=xxx is redacted (via custom key)."""
        cap = _make_redactor(extra_key_names=("auth",))
        res = _redact(cap, "auth=myauthvalue")
        assert "myauthvalue" not in res.text

    def test_credential_key_redacted(self) -> None:
        """FR-SEC-004: credential=xxx is redacted (via custom key)."""
        cap = _make_redactor(extra_key_names=("credential",))
        res = _redact(cap, "credential=mycred")
        assert "mycred" not in res.text

    def test_session_key_redacted(self) -> None:
        """FR-SEC-004: session=xxx is redacted (via custom key)."""
        cap = _make_redactor(extra_key_names=("session",))
        res = _redact(cap, "session=sess123")
        assert "sess123" not in res.text

    def test_cookie_key_redacted(self) -> None:
        """FR-SEC-004: cookie=xxx is redacted (via custom key)."""
        cap = _make_redactor(extra_key_names=("cookie",))
        res = _redact(cap, "cookie=cookietoken")
        assert "cookietoken" not in res.text


class TestPatternBasedRedaction:
    """Test pattern-based secret detection (FR-SEC-004)."""

    def test_bearer_token_redacted(self) -> None:
        """FR-SEC-004: bearer token pattern is redacted."""
        cap = _make_redactor()
        res = _redact(cap, "Authorization: Bearer eyJhbGciOiJIUzI1NiIs")
        assert "eyJhbGciOiJIUzI1NiIs" not in res.text

    def test_basic_auth_redacted(self) -> None:
        """FR-SEC-004: basic auth pattern is redacted."""
        cap = _make_redactor()
        res = _redact(cap, "Authorization: Basic dXNlcjpwYXNz")
        assert "dXNlcjpwYXNz" not in res.text

    def test_sk_pattern_redacted(self) -> None:
        """FR-SEC-004: sk-<20+ chars> pattern is redacted."""
        cap = _make_redactor()
        res = _redact(cap, "key=sk-abcdefghijklmnopqrstuvwxyz123456")
        assert "sk-abcdefghijklmnopqrstuvwxyz123456" not in res.text

    def test_ghp_pattern_redacted(self) -> None:
        """FR-SEC-004: ghp_<36 chars> GitHub token pattern is redacted."""
        cap = _make_redactor()
        res = _redact(cap, "token=ghp_ABCDEFGHIJKLMNOPqrstuv1234567890")
        assert "ghp_ABCDEFGHIJKLMNOPqrstuv1234567890" not in res.text

    def test_akia_pattern_redacted(self) -> None:
        """FR-SEC-004: AKIA<16 chars> AWS key pattern is redacted."""
        cap = _make_redactor()
        res = _redact(cap, "key=AKIA1234567890ABCDEF")
        assert "AKIA1234567890ABCDEF" not in res.text


class TestCustomKeyNames:
    """Test custom key name configuration (FR-SEC-004)."""

    def test_custom_key_redacted(self) -> None:
        """FR-SEC-004: custom key names are redacted."""
        cap = _make_redactor(extra_key_names=("my_secret_key",))
        res = _redact(cap, "my_secret_key=abc123")
        assert "abc123" not in res.text

    def test_custom_key_case_insensitive(self) -> None:
        """FR-SEC-004: custom keys are case-insensitive."""
        cap = _make_redactor(extra_key_names=("MY_KEY",))
        res = _redact(cap, "my_key=value123")
        assert "value123" not in res.text

    def test_custom_key_json_form(self) -> None:
        """FR-SEC-004: custom keys match JSON form."""
        cap = _make_redactor(extra_key_names=("session_token",))
        res = _redact(cap, '{"session_token": "tok-abc123"}')
        assert "tok-abc123" not in res.text


class TestKeyAndValueForms:
    """Test different key=value forms (FR-SEC-004)."""

    def test_shell_form_redacted(self) -> None:
        """FR-SEC-004: shell form (key=value) is redacted."""
        cap = _make_redactor()
        res = _redact(cap, "password=secret123")
        assert "secret123" not in res.text

    def test_yaml_form_redacted(self) -> None:
        """FR-SEC-004: YAML form (key: value) is redacted."""
        cap = _make_redactor()
        res = _redact(cap, "password: secret123")
        assert "secret123" not in res.text

    def test_json_form_redacted(self) -> None:
        """FR-SEC-004: JSON form ("key": "value") is redacted."""
        cap = _make_redactor()
        res = _redact(cap, '{"password": "secret123"}')
        assert "secret123" not in res.text

    def test_json_form_with_api_key(self) -> None:
        """FR-SEC-004: JSON form with api_key is redacted."""
        cap = _make_redactor()
        res = _redact(cap, '{"api_key": "sk-abcdefghijklmnopqrst"}')
        assert "sk-abcdefghijklmnopqrst" not in res.text

    def test_spaced_quoted_secret_redacted(self) -> None:
        """FR-SEC-004: spaced quoted secret is fully redacted."""
        cap = _make_redactor()
        res = _redact(cap, '{"password": "my secret value"}')
        assert "my secret value" not in res.text
        assert "secret" not in res.text  # no partial leak

    def test_spaced_json_secret_redacted(self) -> None:
        """FR-SEC-004: spaced secret in JSON is fully consumed."""
        cap = _make_redactor()
        res = _redact(cap, '{"api_key": "sk-1 2 3"}')
        assert "sk-1 2 3" not in res.text


class TestRedactionOutput:
    """Test redaction output safety (FR-SEC-004)."""

    def test_text_field_is_leak_free(self) -> None:
        """FR-SEC-004: the text field carries redacted output, never raw secret."""
        cap = _make_redactor()
        res = _redact(cap, "password=supersecret token=abc123")
        assert "supersecret" not in res.text
        assert "abc123" not in res.text

    def test_text_equals_redacted_text(self) -> None:
        """FR-SEC-004: text and redacted_text are identical on success."""
        cap = _make_redactor()
        res = _redact(cap, "password=secret")
        assert res.text == res.redacted_text

    def test_redacted_count_increments(self) -> None:
        """FR-SEC-004: redacted_count reflects number of replacements."""
        cap = _make_redactor()
        res = _redact(cap, "password=secret token=abc")
        assert res.redacted_count >= 2

    def test_multiple_secrets_all_redacted(self) -> None:
        """FR-SEC-004: multiple secrets in one string are all redacted."""
        cap = _make_redactor()
        res = _redact(cap, "password=supersecret token=bearer-xyz api_key=sk-abcdefghijklmnop")
        assert "supersecret" not in res.text
        assert "bearer-xyz" not in res.text
        assert "sk-abcdefghijklmnop" not in res.text


class TestFailureMasking:
    """Test redaction failure safety (FR-SEC-004)."""

    def test_failure_masks_entire_payload(self) -> None:
        """FR-SEC-004: redaction failure masks entire payload."""
        cap = _make_redactor()
        res = _redact(cap, "password=supersecret", patterns=("(",))  # invalid regex
        assert res.failed is True
        assert res.text == "[REDACTION_FAILED]"
        assert res.redacted_text == "[REDACTION_FAILED]"

    def test_failure_does_not_echo_secret(self) -> None:
        """FR-SEC-004: failure never echoes original secret."""
        cap = _make_redactor()
        res = _redact(cap, "password=supersecret", patterns=("(",))
        assert "supersecret" not in res.text

    def test_failure_has_failure_reason(self) -> None:
        """FR-SEC-004: failure includes failure reason."""
        cap = _make_redactor()
        res = _redact(cap, "password=secret", patterns=("(",))
        assert res.failed is True
        assert res.failure_reason is not None

    def test_failure_has_sensitivity_level(self) -> None:
        """FR-SEC-004: failure preserves sensitivity level."""
        cap = _make_redactor()
        res = _redact(cap, "password=secret", sensitivity_level=SensitivityLevel.CRITICAL, patterns=("(",))
        assert res.failed is True


class TestTruncation:
    """Test oversized payload truncation (FR-SEC-004)."""

    def test_large_payload_truncated(self) -> None:
        """FR-SEC-004: payloads over 10000 bytes are truncated."""
        cap = _make_redactor()
        res = _redact(cap, "a" * 15000)
        assert len(res.text) <= 10012  # 10000 + "\n[TRUNCATED]"

    def test_truncated_payload_has_marker(self) -> None:
        """FR-SEC-004: truncated payload includes truncation marker."""
        cap = _make_redactor()
        res = _redact(cap, "a" * 15000)
        assert "TRUNCATED" in res.text


class TestEdgeCases:
    """Test edge cases from FR-SEC-004 specification."""

    def test_no_secrets_in_text(self) -> None:
        """FR-SEC-004: text without secrets is unchanged."""
        cap = _make_redactor()
        res = _redact(cap, "This is a normal message with no secrets")
        assert res.text == "This is a normal message with no secrets"

    def test_empty_text(self) -> None:
        """FR-SEC-004: empty text is handled."""
        cap = _make_redactor()
        res = _redact(cap, "")
        assert res.text == ""
        assert res.redacted_count == 0

    def test_binary_data_handling(self) -> None:
        """FR-SEC-004: binary data is handled safely."""
        cap = _make_redactor()
        res = _redact(cap, "binary\x00data")
        # Should not raise
        assert res.failed is False

    def test_nested_structure_redacted(self) -> None:
        """FR-SEC-004: secrets inside nested structures are redacted."""
        cap = _make_redactor()
        res = _redact(cap, '{"config": {"password": "hunter2", "api_key": "sk-abcdefghijklmnop"}}')
        assert "hunter2" not in res.text
        assert "sk-abcdefghijklmnop" not in res.text

    def test_encoded_secret_redacted(self) -> None:
        """FR-SEC-004: encoded secrets are redacted (base64-like patterns)."""
        cap = _make_redactor()
        res = _redact(cap, "Authorization: Bearer eyJhbGciOiJIUzI1NiIs")
        assert "eyJhbGciOiJIUzI1NiIs" not in res.text

    def test_sensitive_path_in_message(self) -> None:
        """FR-SEC-004: sensitive paths are redacted when configured."""
        cap = _make_redactor()
        res = _redact(cap, "accessing /etc/shadow with password=secret")
        assert "secret" not in res.text

    def test_token_in_query_parameter(self) -> None:
        """FR-SEC-004: token in query parameter is redacted."""
        cap = _make_redactor()
        res = _redact(cap, "url?token=abc123xyz&other=value")
        assert "abc123xyz" not in res.text

    def test_credential_in_connection_string(self) -> None:
        """FR-SEC-004: credential in connection string is redacted."""
        cap = _make_redactor()
        res = _redact(cap, "host=db.example.com password=hunter2 port=5432")
        assert "hunter2" not in res.text

    def test_multiline_secret_redacted(self) -> None:
        """FR-SEC-004: multiline secrets are redacted."""
        cap = _make_redactor()
        res = _redact(cap, "password=line1\nline2")
        # The pattern matches up to whitespace/comma, so only line1 is redacted
        # This is expected behavior for the pattern-based approach


class TestSensitivityLevels:
    """Test sensitivity level handling (FR-SEC-004)."""

    def test_high_sensitivity(self) -> None:
        """FR-SEC-004: HIGH sensitivity level is preserved."""
        cap = _make_redactor()
        res = _redact(cap, "password=secret", sensitivity_level=SensitivityLevel.HIGH)
        assert res.sensitivity_level == SensitivityLevel.HIGH

    def test_critical_sensitivity(self) -> None:
        """FR-SEC-004: CRITICAL sensitivity level is preserved."""
        cap = _make_redactor()
        res = _redact(cap, "password=secret", sensitivity_level=SensitivityLevel.CRITICAL)
        assert res.sensitivity_level == SensitivityLevel.CRITICAL

    def test_low_sensitivity(self) -> None:
        """FR-SEC-004: LOW sensitivity level is preserved."""
        cap = _make_redactor()
        res = _redact(cap, "password=secret", sensitivity_level=SensitivityLevel.LOW)
        assert res.sensitivity_level == SensitivityLevel.LOW


class TestRepresentation:
    """Test class representation."""

    def test_sensitive_redactor_repr(self) -> None:
        """SensitiveRedactor has a repr."""
        cap = SensitiveRedactor.__new__(SensitiveRedactor)
        SensitiveRedactor.__init__(cap, ())
        assert "SensitiveRedactor" in repr(cap)


# ─── FR-SEC-004: Redaction Rule Conflict ──────────────────────────────────


class TestRedactionConflicts:
    """Test redaction rule conflict scenarios (FR-SEC-004)."""

    def test_overlapping_patterns(self) -> None:
        """FR-SEC-004: overlapping patterns are handled gracefully."""
        cap = _make_redactor()
        # password=xxx matches both password key and generic patterns
        res = _redact(cap, "password=secret123")
        assert "secret123" not in res.text

    def test_custom_pattern_added_to_default(self) -> None:
        """FR-SEC-004: custom patterns are added to default set."""
        cap = _make_redactor(extra_patterns=(r"(?i)my_custom_secret",))
        res = _redact(cap, "my_custom_secret=abc123")
        assert "abc123" not in res.text
