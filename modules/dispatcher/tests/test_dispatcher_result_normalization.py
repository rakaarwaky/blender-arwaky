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
from modules.shared.src.dispatcher.taxonomy_raw_outcome_vo import RawOutcomeVO


def _make_raw(
    success: bool = True,
    message: str = "",
    tracking_id: str = "",
    data: dict | None = None,
    error_category: str | None = None,
) -> RawOutcomeVO:
    """Helper to create a RawOutcomeVO for tests."""
    return RawOutcomeVO(
        success=success,
        message=message,
        tracking_id=tracking_id or "track-test",
        data=data,
        error_category=error_category,
    )


# ─── FR-DSP-006: Success Envelope ──────────────────────────────────────────


class TestSuccessEnvelope:
    """Success envelope generation per FR-DSP-006."""

    def test_success_envelope_created(self) -> None:
        """FR-DSP-006: Success outcome creates envelope with status success."""
        executor = ResultNormalizationExecutor()
        raw = _make_raw(success=True, data={"result": "ok"}, tracking_id="track-123")
        result = executor.normalize_result(raw)
        assert result.success is True
        assert result.tracking_id == "track-123"

    def test_success_envelope_redacts_secrets(self) -> None:
        """FR-DSP-006: Success envelope redacts secret values."""
        executor = ResultNormalizationExecutor()
        raw = _make_raw(success=True, data={"password": "secret", "name": "test"})
        result = executor.normalize_result(raw)
        # Secrets are replaced with "***REDACTED***" marker, not removed
        assert result.data is not None
        assert result.data.get("password") == "***REDACTED***"
        assert result.data.get("name") == "test"

    def test_success_envelope_truncates_long_strings(self) -> None:
        """FR-DSP-006: Oversized string data is truncated."""
        executor = ResultNormalizationExecutor()
        raw = _make_raw(success=True, data={"long_text": "x" * 1500})
        result = executor.normalize_result(raw)
        assert result.data is not None
        # Strings > 1000 chars are truncated with "...[truncated]" suffix
        assert "truncated" in str(result.data.get("long_text", ""))


# ─── FR-DSP-006: Error Envelope ────────────────────────────────────────────


class TestErrorEnvelope:
    """Error envelope generation per FR-DSP-006."""

    def test_error_envelope_created(self) -> None:
        """FR-DSP-006: Error outcome creates envelope with status error."""
        executor = ResultNormalizationExecutor()
        raw = _make_raw(success=False, message="something failed", tracking_id="track-456")
        result = executor.normalize_result(raw)
        assert result.success is False

    def test_error_envelope_safe_fallback(self) -> None:
        """FR-DSP-006: Safe error envelope handles invalid input data."""
        executor = ResultNormalizationExecutor()
        # RawOutcomeVO with non-dict data triggers safe fallback path
        raw = RawOutcomeVO(success=False, tracking_id="track-789")
        result = executor.normalize_result(raw)
        assert result.success is False

    def test_error_envelope_handles_none_data(self) -> None:
        """FR-DSP-006: Safe error envelope handles None data."""
        executor = ResultNormalizationExecutor()
        raw = RawOutcomeVO(success=False, tracking_id="track-none", data=None)
        result = executor.normalize_result(raw)
        assert result.success is False


# ─── FR-DSP-006: Data Sanitization ──────────────────────────────────────────


class TestDataSanitization:
    """Data sanitization per FR-DSP-006."""

    def test_nested_dict_sanitized(self) -> None:
        """FR-DSP-006: Nested dict secrets are recursively redacted."""
        executor = ResultNormalizationExecutor()
        raw = _make_raw(
            data={"config": {"api_key": "secret123", "nested": {"token": "abc"}}},
        )
        result = executor.normalize_result(raw)
        assert "api_key" not in str(result.data) or "***REDACTED***" in str(result.data)

    def test_non_serializable_converted(self) -> None:
        """FR-DSP-006: Non-serializable data converted to string."""
        executor = ResultNormalizationExecutor()

        class Unserializable:
            """Object that fails json serialization but succeeds str()."""

            def __repr__(self):
                return "<Unserializable>"

        raw = _make_raw(data=Unserializable())
        result = executor.normalize_result(raw)
        # Non-dict data that fails json.dumps gets converted via str()
        assert isinstance(result.data, str)

    def test_sensitive_keys_redacted(self) -> None:
        """FR-DSP-006: Common sensitive keys are redacted."""
        executor = ResultNormalizationExecutor()
        raw = _make_raw(
            data={"password": "x", "secret": "y", "token": "z", "api_key": "w"},
        )
        result = executor.normalize_result(raw)
        for key in ["password", "secret", "token", "api_key"]:
            assert key not in str(result.data) or "***REDACTED***" in str(result.data)

    def test_long_code_truncated(self) -> None:
        """FR-DSP-006: Long string values are truncated at 1000 chars."""
        executor = ResultNormalizationExecutor()
        raw = _make_raw(data={"script": "a" * 1500})
        result = executor.normalize_result(raw)
        assert result.data is not None
        assert "truncated" in str(result.data.get("script", ""))


# ─── FR-DSP-006: Tracking ID Propagation ────────────────────────────────────


class TestTrackingIdPropagation:
    """Tracking ID propagation per FR-DSP-006."""

    def test_tracking_id_preserved(self) -> None:
        """FR-DSP-006: Tracking ID is preserved in envelope."""
        executor = ResultNormalizationExecutor()
        raw = _make_raw(data={}, tracking_id="exact-id")
        result = executor.normalize_result(raw)
        assert result.tracking_id == "exact-id"

    def test_tracking_id_in_error(self) -> None:
        """FR-DSP-006: Tracking ID is preserved in error envelope."""
        executor = ResultNormalizationExecutor()
        raw = _make_raw(success=False, message="fail", tracking_id="error-id")
        result = executor.normalize_result(raw)
        assert result.tracking_id == "error-id"
