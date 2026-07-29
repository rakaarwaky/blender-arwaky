"""Tests for result normalization capability — FR-DSP-006.

FR-DSP-006: Unified Result Envelope
- Normalizes any dispatcher outcome into a unified result envelope
- Never leaks secrets; truncates oversized data; falls back to safe error
- Tracking ID generation and propagation
"""

from __future__ import annotations

from modules.dispatcher.src.capabilities_result_normalization import (
    ResultNormalizationExecutor,
)

# ─── FR-DSP-006: Success Envelope ──────────────────────────────────────────


class TestSuccessEnvelope:
    """Success envelope generation per FR-DSP-006."""

    def test_success_envelope_created(self) -> None:
        """FR-DSP-006: Success outcome creates envelope with status success."""
        executor = ResultNormalizationExecutor()
        raw = {"success": True, "data": {"result": "ok"}}
        result = executor.normalize_result(raw, "track-123")
        assert result.success is True
        assert result.tracking_id == "track-123"

    def test_success_envelope_redacts_secrets(self) -> None:
        """FR-DSP-006: Success envelope redacts secret values."""
        executor = ResultNormalizationExecutor()
        raw = {"success": True, "data": {"password": "secret", "name": "test"}}
        result = executor.normalize_result(raw, "track-123")
        # Secrets are replaced with "***REDACTED***" marker, not removed
        assert result.data is not None
        assert result.data.get("password") == "***REDACTED***"
        assert result.data.get("name") == "test"

    def test_success_envelope_truncates_long_strings(self) -> None:
        """FR-DSP-006: Oversized string data is truncated."""
        executor = ResultNormalizationExecutor()
        raw = {"success": True, "data": {"long_text": "x" * 1500}}
        result = executor.normalize_result(raw, "track-123")
        assert result.data is not None
        # Strings > 1000 chars are truncated with "...[truncated]" suffix
        assert "truncated" in str(result.data.get("long_text", ""))


# ─── FR-DSP-006: Error Envelope ────────────────────────────────────────────


class TestErrorEnvelope:
    """Error envelope generation per FR-DSP-006."""

    def test_error_envelope_created(self) -> None:
        """FR-DSP-006: Error outcome creates envelope with status error."""
        executor = ResultNormalizationExecutor()
        raw = {"success": False, "message": "something failed"}
        result = executor.normalize_result(raw, "track-456")
        assert result.success is False

    def test_error_envelope_safe_fallback(self) -> None:
        """FR-DSP-006: Safe error envelope handles non-dict input."""
        executor = ResultNormalizationExecutor()
        result = executor.normalize_result("not a dict", "track-789")
        assert result.success is False

    def test_error_envelope_handles_none(self) -> None:
        """FR-DSP-006: Safe error envelope handles None input."""
        executor = ResultNormalizationExecutor()
        result = executor.normalize_result(None, "track-none")
        assert result.success is False


# ─── FR-DSP-006: Data Sanitization ──────────────────────────────────────────


class TestDataSanitization:
    """Data sanitization per FR-DSP-006."""

    def test_nested_dict_sanitized(self) -> None:
        """FR-DSP-006: Nested dict secrets are recursively redacted."""
        executor = ResultNormalizationExecutor()
        raw = {
            "success": True,
            "data": {"config": {"api_key": "secret123", "nested": {"token": "abc"}}},
        }
        result = executor.normalize_result(raw, "track-nest")
        assert "api_key" not in str(result.data) or "***REDACTED***" in str(result.data)

    def test_non_serializable_converted(self) -> None:
        """FR-DSP-006: Non-serializable data converted to string."""
        executor = ResultNormalizationExecutor()

        class Unserializable:
            """Object that fails json serialization but succeeds str()."""

            def __repr__(self):
                return "<Unserializable>"

        raw = {"success": True, "data": Unserializable()}
        result = executor.normalize_result(raw, "track-obj")
        # Non-dict data that fails json.dumps gets converted via str()
        assert isinstance(result.data, str)

    def test_sensitive_keys_redacted(self) -> None:
        """FR-DSP-006: Common sensitive keys are redacted."""
        executor = ResultNormalizationExecutor()
        raw = {
            "success": True,
            "data": {"password": "x", "secret": "y", "token": "z", "api_key": "w"},
        }
        result = executor.normalize_result(raw, "track-keys")
        for key in ["password", "secret", "token", "api_key"]:
            assert key not in str(result.data) or "***REDACTED***" in str(result.data)

    def test_long_code_truncated(self) -> None:
        """FR-DSP-006: Long string values are truncated at 1000 chars."""
        executor = ResultNormalizationExecutor()
        raw = {"success": True, "data": {"script": "a" * 1500}}
        result = executor.normalize_result(raw, "track-code")
        assert result.data is not None
        assert "truncated" in str(result.data.get("script", ""))


# ─── FR-DSP-006: Tracking ID Propagation ────────────────────────────────────


class TestTrackingIdPropagation:
    """Tracking ID propagation per FR-DSP-006."""

    def test_tracking_id_preserved(self) -> None:
        """FR-DSP-006: Tracking ID is preserved in envelope."""
        executor = ResultNormalizationExecutor()
        raw = {"success": True, "data": {}}
        result = executor.normalize_result(raw, "exact-id")
        assert result.tracking_id == "exact-id"

    def test_tracking_id_in_error(self) -> None:
        """FR-DSP-006: Tracking ID is preserved in error envelope."""
        executor = ResultNormalizationExecutor()
        raw = {"success": False, "message": "fail"}
        result = executor.normalize_result(raw, "error-id")
        assert result.tracking_id == "error-id"
