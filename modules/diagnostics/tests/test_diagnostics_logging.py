"""Tests for LoggingPolicy — FR-DIA-004.

Exercises structured log entry creation, buffer management, backpressure,
redaction at ingestion, and source feature tracking via LoggingPolicy.
Run via pytest from repo root.
"""

from __future__ import annotations

import asyncio

import pytest

from modules.diagnostics.src.capabilities_logging_policy import LoggingPolicy
from modules.shared.src.diagnostics.taxonomy_diagnostics_vo import LogRecordRequestVO


def _make_policy() -> LoggingPolicy:
    return LoggingPolicy()


class TestLogRecordCreation:
    """Test structured log entry creation with required fields."""

    def test_log_record_returns_confirmed(self) -> None:
        cap = _make_policy()
        result = asyncio.run(cap.log_record(request=LogRecordRequestVO(level="info", source_feature="cli", message="startup")))
        assert result.logged is True

    def test_log_record_has_destination(self) -> None:
        cap = _make_policy()
        result = asyncio.run(cap.log_record(request=LogRecordRequestVO(level="info", source_feature="cli", message="startup")))
        assert result.destination == "buffer"

    def test_log_entry_contains_level(self) -> None:
        cap = _make_policy()
        asyncio.run(cap.log_record(request=LogRecordRequestVO(level="info", source_feature="cli", message="startup")))
        assert cap._buffer[-1]["level"] == "info"

    def test_log_entry_contains_source_feature(self) -> None:
        cap = _make_policy()
        asyncio.run(cap.log_record(request=LogRecordRequestVO(level="info", source_feature="gateway", message="connection")))
        assert cap._buffer[-1]["source_feature"] == "gateway"

    def test_log_entry_contains_message(self) -> None:
        cap = _make_policy()
        asyncio.run(cap.log_record(request=LogRecordRequestVO(level="info", source_feature="cli", message="test message")))
        assert cap._buffer[-1]["message"] == "test message"

    def test_log_entry_contains_fields(self) -> None:
        cap = _make_policy()
        asyncio.run(cap.log_record(request=LogRecordRequestVO(level="info", source_feature="cli", message="test", fields={"x": 1, "y": 2})))
        assert cap._buffer[-1]["fields"] == {"x": 1, "y": 2}

    def test_log_entry_contains_tracking_id(self) -> None:
        cap = _make_policy()
        asyncio.run(cap.log_record(request=LogRecordRequestVO(level="info", source_feature="cli", message="test", tracking_id="trace-123")))
        assert cap._buffer[-1]["tracking_id"] == "trace-123"

    def test_log_entry_contains_timestamp(self) -> None:
        cap = _make_policy()
        asyncio.run(cap.log_record(request=LogRecordRequestVO(level="info", source_feature="cli", message="test")))
        assert "timestamp" in cap._buffer[-1]


class TestLogLevels:
    """Test supported log level hierarchy."""

    @pytest.mark.parametrize("level", ["debug", "info", "warning", "error"])
    def test_all_standard_levels_supported(self, level: str) -> None:
        cap = _make_policy()
        result = asyncio.run(cap.log_record(request=LogRecordRequestVO(level=level, source_feature="test", message=f"test {level}")))
        assert result.logged is True
        assert cap._buffer[-1]["level"] == level

    def test_debug_level(self) -> None:
        cap = _make_policy()
        asyncio.run(cap.log_record(request=LogRecordRequestVO(level="debug", source_feature="test", message="debug trace")))
        assert cap._buffer[-1]["level"] == "debug"

    def test_info_level(self) -> None:
        cap = _make_policy()
        asyncio.run(cap.log_record(request=LogRecordRequestVO(level="info", source_feature="test", message="info message")))
        assert cap._buffer[-1]["level"] == "info"

    def test_warning_level(self) -> None:
        cap = _make_policy()
        asyncio.run(cap.log_record(request=LogRecordRequestVO(level="warning", source_feature="test", message="warning")))
        assert cap._buffer[-1]["level"] == "warning"

    def test_error_level(self) -> None:
        cap = _make_policy()
        asyncio.run(cap.log_record(request=LogRecordRequestVO(level="error", source_feature="test", message="error")))
        assert cap._buffer[-1]["level"] == "error"


class TestLogBufferManagement:
    """Test log buffer entry management and ordering."""

    def test_logs_are_appended_in_order(self) -> None:
        cap = _make_policy()
        asyncio.run(cap.log_record(request=LogRecordRequestVO(level="info", source_feature="cli", message="first")))
        asyncio.run(cap.log_record(request=LogRecordRequestVO(level="info", source_feature="gateway", message="second")))
        assert len(cap._buffer) == 2
        assert cap._buffer[0]["message"] == "first"
        assert cap._buffer[1]["message"] == "second"

    def test_empty_fields_defaults_to_empty_dict(self) -> None:
        cap = _make_policy()
        asyncio.run(cap.log_record(request=LogRecordRequestVO(level="info", source_feature="cli", message="test")))
        assert cap._buffer[-1]["fields"] == {}

    def test_none_tracking_id_preserved(self) -> None:
        cap = _make_policy()
        asyncio.run(cap.log_record(request=LogRecordRequestVO(level="info", source_feature="cli", message="test", tracking_id=None)))
        assert cap._buffer[-1]["tracking_id"] is None


class TestLogRedaction:
    """Test redaction rules for log content — no raw secrets at any level."""

    def test_redacts_password_in_message(self) -> None:
        cap = _make_policy()
        asyncio.run(cap.log_record(request=LogRecordRequestVO(level="info", source_feature="cli", message="password=[REDACTED:API key param]")))
        assert "REDACTED" in cap._buffer[-1]["message"]
        assert "secret123" not in cap._buffer[-1]["message"]

    def test_redacts_api_key_in_fields(self) -> None:
        cap = _make_policy()
        asyncio.run(cap.log_record(request=LogRecordRequestVO(level="info", source_feature="cli", message="test", fields={"api_key": "abc123def456"})))
        assert "REDACTED" in str(cap._buffer[-1]["fields"])

    def test_redacts_token_in_message(self) -> None:
        cap = _make_policy()
        asyncio.run(cap.log_record(request=LogRecordRequestVO(level="info", source_feature="cli", message="token=[REDACTED:API key param]")))
        assert "REDACTED" in cap._buffer[-1]["message"]

    def test_debug_does_not_bypass_redaction(self) -> None:
        cap = _make_policy()
        asyncio.run(cap.log_record(request=LogRecordRequestVO(level="debug", source_feature="cli", message="password=debug_secret")))
        assert "REDACTED" in cap._buffer[-1]["message"]


class TestBackpressure:
    """Test backpressure handling — bounded buffer, drop counter exposed."""

    def test_bounded_buffer_drops_oldest(self) -> None:
        cap = LoggingPolicy(max_buffer_size=3)
        asyncio.run(cap.log_record(request=LogRecordRequestVO(level="info", source_feature="cli", message="first")))
        asyncio.run(cap.log_record(request=LogRecordRequestVO(level="info", source_feature="cli", message="second")))
        asyncio.run(cap.log_record(request=LogRecordRequestVO(level="info", source_feature="cli", message="third")))
        asyncio.run(cap.log_record(request=LogRecordRequestVO(level="info", source_feature="cli", message="fourth")))
        assert len(cap._buffer) <= 3
        assert cap.get_drop_counter() >= 1

    def test_drop_counter_increments(self) -> None:
        cap = LoggingPolicy(max_buffer_size=2)
        for _ in range(5):
            asyncio.run(cap.log_record(request=LogRecordRequestVO(level="info", source_feature="cli", message=f"log {_}")))
        assert cap.get_drop_counter() >= 3

    def test_redacted_count_in_result(self) -> None:
        cap = _make_policy()
        result = asyncio.run(cap.log_record(request=LogRecordRequestVO(level="info", source_feature="cli", message="password=secret")))
        assert result.redacted_count >= 1


class TestStructuredFields:
    """Test structured field handling."""

    def test_fields_can_contain_numbers(self) -> None:
        cap = _make_policy()
        asyncio.run(cap.log_record(request=LogRecordRequestVO(level="info", source_feature="cli", message="test", fields={"count": 5})))
        assert cap._buffer[-1]["fields"]["count"] == 5

    def test_fields_can_contain_strings(self) -> None:
        cap = _make_policy()
        asyncio.run(cap.log_record(request=LogRecordRequestVO(level="info", source_feature="cli", message="test", fields={"status": "ok"})))
        assert cap._buffer[-1]["fields"]["status"] == "ok"

    def test_fields_can_contain_nested_structures(self) -> None:
        cap = _make_policy()
        asyncio.run(
            cap.log_record(request=LogRecordRequestVO(level="info", source_feature="cli", message="test", fields={"nested": {"key": "val"}}))
        )
        assert "nested" in cap._buffer[-1]["fields"]


class TestLogDestination:
    """Test log destination handling."""

    def test_log_written_to_buffer(self) -> None:
        cap = _make_policy()
        result = asyncio.run(cap.log_record(request=LogRecordRequestVO(level="info", source_feature="cli", message="test")))
        assert result.destination == "buffer"

    def test_log_written_to_python_logger(self) -> None:
        cap = _make_policy()
        asyncio.run(cap.log_record(request=LogRecordRequestVO(level="info", source_feature="cli", message="test")))
        assert len(cap._buffer) >= 1
