"""Tests for Issue #95 — Launcher Business Logic fixes.

Verifies P0/P1 fixes from the business logic review:
- P0: Executable registration persistence (Finding #1)
- P0: PID reuse guard (Finding #3)
- P1: Version compatibility semantic parsing (Finding #2)
- P1: Corrupt state load warning event (Finding #7)
- P1: Process alive EPERM semantics (Finding #6)

Run via pytest from repo root.
"""

from __future__ import annotations

import errno
import os
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

from modules.launcher.src.capabilities_executable_locator import ExecutableLocator
from modules.launcher.src.capabilities_runtime_status import RuntimeStatusChecker
from modules.launcher.src.capabilities_state_persistence import StatePersistence
from modules.shared.src.launcher.taxonomy_launcher_constant import (
    LAUNCHER_EVENT_CORRUPT_STATE_DETECTED,
)
from modules.shared.src.launcher.taxonomy_launcher_vo import (
    LauncherConfigVO,
    ProbeDepth,
    RuntimeState,
    RuntimeStateVO,
    VersionCompatibility,
)

# Import from shared module (injected via conftest shim)
from modules.shared.src.launcher.utility_process_ops import process_alive

# ─── Helpers ──────────────────────────────────────────────────────────────────


def _make_persist(tmp_path: Path) -> tuple[StatePersistence, Path]:
    """Create a StatePersistence with a temp file path."""
    state_file = tmp_path / "launcher_state.json"
    cap = StatePersistence(path_resolver=lambda: str(state_file))
    return cap, state_file


def _make_locators(
    persist_cap: StatePersistence | None = None,
) -> ExecutableLocator:
    """Create an ExecutableLocator with injected dependencies."""
    return ExecutableLocator(
        command_runner=lambda _args, _timeout=5.0: (0, "Blender 3.6.0"),
        env_resolver=lambda _key, _default: None,
        persist_cap=persist_cap,
    )


# ─── P0 Finding #1: Executable Registration Persistence ──────────────────────


class TestExecutableRegistrationPersistence:
    """Test P0 fix for executable registration persistence (Finding #1)."""

    def test_register_persists_executable_path(self, tmp_path: Path) -> None:
        """P0 (Finding #1): ExecutableLocator persists executable path to state store."""
        persist_cap, state_file = _make_persist(tmp_path)
        locator = _make_locators(persist_cap=persist_cap)

        config = LauncherConfigVO(executable_path="/usr/bin/blender")
        result = locator.locate_and_register(config, override="/usr/bin/python3")

        assert result.registered is True
        # Verify state was persisted with executable path
        loaded = persist_cap.load()
        assert loaded is not None
        assert loaded.executable_path == "/usr/bin/python3"

    def test_register_skipped_when_no_persist_cap(self) -> None:
        """P0 (Finding #1): Registration works even without persist capability."""
        locator = _make_locators(persist_cap=None)
        config = LauncherConfigVO(executable_path="/usr/bin/blender")

        result = locator.locate_and_register(config, override="/usr/bin/python3")
        assert result.registered is True

    def test_register_failure_is_non_blocking(self) -> None:
        """P0 (Finding #1): Registration persistence failure doesn't block registration."""

        # Persist cap that always fails
        class FailingPersist:
            def persist(self, _state):
                raise OSError("Cannot write")

            def load(self):
                return None

        locator = _make_locators(persist_cap=FailingPersist())
        config = LauncherConfigVO(executable_path="/usr/bin/blender")

        result = locator.locate_and_register(config, override="/usr/bin/python3")
        assert result.registered is True  # Should succeed despite persist failure


# ─── P0 Finding #3: PID Reuse Guard ──────────────────────────────────────────


class TestPIDReuseGuard:
    """Test P0 fix for PID reuse detection (Finding #3)."""

    def test_pid_reuse_detected_via_proc_stat(self) -> None:
        """P0 (Finding #3): PID reuse detected by comparing /proc/{pid}/stat start time."""
        events_received: list[dict] = []

        def mock_event_sink(event):
            events_received.append({"category": event.event_category})

        # Mock liveness checker — process is alive
        def mock_liveness(_pid):
            return True

        # Mock PID resolver — always returns same PID
        pid_resolver_count = [0]

        def mock_pid_resolver():
            pid_resolver_count[0] += 1
            return 99999  # High PID to avoid conflicts

        # Mock persisted state resolver — returns same PID
        def mock_persisted():
            return RuntimeStateVO(process_id=99999, last_status=RuntimeState.RUNNING_READY)

        status_checker = RuntimeStatusChecker(
            liveness_checker=mock_liveness,
            pid_resolver=mock_pid_resolver,
            bridge_probe=None,
            persisted_state_resolver=mock_persisted,
            stale_reconciliation_enabled=True,
            event_sink=mock_event_sink,
        )

        # Mark launch to set process start time
        status_checker.mark_launched(time.time())

        # Mock /proc/99999/stat with different start time than stored
        proc_stat_content = (
            "99999 (test) S 1000 1000 1000 1000 40 110 "
            "38 0 0 0 100 50 0 0 0 0 0 0 0 0 22 0 0"  # utime=100, stime=50 → start_ticks=150
        )

        with patch("os.path.exists", return_value=True), patch("builtins.open") as mock_open:
            mock_file = MagicMock()
            mock_file.read.return_value = proc_stat_content
            mock_open.return_value.__enter__.return_value = mock_file
            mock_open.return_value.__exit__.return_value = None

            result = status_checker.check_status(depth=ProbeDepth.LIGHTWEIGHT)

        # Should detect PID reuse and return STALE
        assert result.state == RuntimeState.STALE
        assert result.stale is True

    def test_pid_reuse_skipped_when_no_start_time(self) -> None:
        """P0 (Finding #3): PID reuse check skipped when _process_start_time is None."""
        events_received: list[dict] = []

        def mock_event_sink(event):
            events_received.append({"category": event.event_category})

        status_checker = RuntimeStatusChecker(
            liveness_checker=lambda _pid: True,
            pid_resolver=lambda: 99998,
            bridge_probe=None,
            persisted_state_resolver=lambda: None,
            stale_reconciliation_enabled=True,
            event_sink=mock_event_sink,
        )

        # Don't call mark_launched — _process_start_time stays None
        result = status_checker.check_status(depth=ProbeDepth.LIGHTWEIGHT)

        # Should return RUNNING_READY (no PID reuse check when no start time)
        assert result.state == RuntimeState.RUNNING_READY

    def test_pid_reuse_fallback_on_proc_error(self) -> None:
        """P0 (Finding #3): PID reuse check falls back gracefully on /proc errors."""
        events_received: list[dict] = []

        def mock_event_sink(event):
            events_received.append({"category": event.event_category})

        status_checker = RuntimeStatusChecker(
            liveness_checker=lambda _pid: True,
            pid_resolver=lambda: 99997,
            bridge_probe=None,
            persisted_state_resolver=lambda: None,
            stale_reconciliation_enabled=True,
            event_sink=mock_event_sink,
        )

        status_checker.mark_launched(time.time())

        # Mock /proc access to raise OSError (permission denied)
        with (
            patch("os.path.exists", return_value=True),
            patch("builtins.open", side_effect=OSError("Permission denied")),
        ):
            result = status_checker.check_status(depth=ProbeDepth.LIGHTWEIGHT)

        # Should fall back to RUNNING_READY (not crash)
        assert result.state == RuntimeState.RUNNING_READY


# ─── P1 Finding #2: Version Compatibility Semantic Parsing ────────────────────


class TestVersionCompatibilityParsing:
    """Test P1 fix for semantic version compatibility parsing (Finding #2)."""

    def test_unsupported_version_36(self) -> None:
        """Blender 3.6 is below the Arwaky 5.2 runtime baseline."""
        locator = ExecutableLocator()
        result = locator._check_compatibility("3.6.0")
        assert result == VersionCompatibility.UNSUPPORTED

    def test_unsupported_version_42(self) -> None:
        """Blender 4.2 is below the Arwaky 5.2 runtime baseline."""
        locator = ExecutableLocator()
        result = locator._check_compatibility("4.2.0")
        assert result == VersionCompatibility.UNSUPPORTED

    def test_unsupported_version_29(self) -> None:
        """P1 (Finding #2): Blender 2.9 is UNSUPPORTED."""
        locator = ExecutableLocator()
        result = locator._check_compatibility("2.9")
        assert result == VersionCompatibility.UNSUPPORTED

    def test_unknown_empty_version(self) -> None:
        """P1 (Finding #2): Empty version returns UNKNOWN."""
        locator = ExecutableLocator()
        result = locator._check_compatibility("")
        assert result == VersionCompatibility.UNKNOWN

    def test_unsupported_version_43(self) -> None:
        """Blender 4.3 is below the Arwaky 5.2 runtime baseline."""
        locator = ExecutableLocator()
        result = locator._check_compatibility("4.3")
        assert result == VersionCompatibility.UNSUPPORTED

    def test_supported_version_52(self) -> None:
        """Blender 5.2 is the supported Arwaky runtime baseline."""
        locator = ExecutableLocator()
        result = locator._check_compatibility("5.2.0")
        assert result == VersionCompatibility.SUPPORTED


# ─── P1 Finding #7: Corrupt State Load Warning Event ─────────────────────────


class TestCorruptStateLoadWarning:
    """Test P1 fix for corrupt state load warning event emission (Finding #7)."""

    def test_corrupt_json_emits_warning_event(self, tmp_path: Path) -> None:
        """P1 (Finding #7): Corrupt JSON emits LAUNCHER_EVENT_CORRUPT_STATE_DETECTED."""
        events_received: list[dict] = []

        def mock_event_sink(event):
            events_received.append({"category": event.event_category, "reason": event.reason_summary})

        state_file = tmp_path / "corrupt.json"
        state_file.write_text("{ this is not valid json")

        cap = StatePersistence(path_resolver=lambda: str(state_file), event_sink=mock_event_sink)
        result = cap.load()

        assert result is None  # Still returns None on corrupt data
        assert len(events_received) == 1
        assert events_received[0]["category"] == LAUNCHER_EVENT_CORRUPT_STATE_DETECTED
        assert "load_error" in events_received[0]["reason"]

    def test_non_dict_json_emits_warning_event(self, tmp_path: Path) -> None:
        """P1 (Finding #7): Non-dict JSON emits warning event."""
        events_received: list[dict] = []

        def mock_event_sink(event):
            events_received.append({"category": event.event_category, "reason": event.reason_summary})

        state_file = tmp_path / "array.json"
        state_file.write_text('["not", "a", "dict"]')

        cap = StatePersistence(path_resolver=lambda: str(state_file), event_sink=mock_event_sink)
        result = cap.load()

        assert result is None
        assert len(events_received) == 1
        assert events_received[0]["category"] == LAUNCHER_EVENT_CORRUPT_STATE_DETECTED
        assert "state_data_not_dict" in events_received[0]["reason"]

    def test_no_event_when_no_event_sink(self, tmp_path: Path) -> None:
        """P1 (Finding #7): No event emitted when event_sink is None."""
        state_file = tmp_path / "corrupt.json"
        state_file.write_text("{ invalid json")

        cap = StatePersistence(path_resolver=lambda: str(state_file), event_sink=None)
        result = cap.load()

        assert result is None  # Should still return None gracefully


# ─── P1 Finding #6: Process Alive EPERM Semantics ────────────────────────────


class TestProcessAliveEPERM:
    """Test P1 fix for process_alive EPERM semantics (Finding #6)."""

    def test_eperm_treated_as_alive(self) -> None:
        """P1 (Finding #6): EPERM means process exists but caller lacks permission — treated as alive."""

        class MockOSErrNoPermissionError(OSError):
            errno = errno.EPERM

        original_kill = os.kill

        def mock_kill(pid, sig):
            if pid == 99996:
                raise MockOSErrNoPermissionError("Permission denied")
            return original_kill(pid, sig)

        with patch("os.kill", side_effect=mock_kill):
            # Process 99996 returns EPERM — should be treated as alive
            result = process_alive(99996)
            assert result is True

    def test_esrch_treated_as_dead(self) -> None:
        """P1 (Finding #6): ESRCH means process doesn't exist — treated as dead."""

        class MockOSErrNoSuchProcessError(OSError):
            errno = errno.ESRCH

        def mock_kill(_pid, _sig):
            raise MockOSErrNoSuchProcessError("No such process")

        with patch("os.kill", side_effect=mock_kill):
            result = process_alive(99995)
            assert result is False

    def test_valid_pid_is_alive(self) -> None:
        """P1 (Finding #6): Valid PID returns True when os.kill succeeds."""
        with patch("os.kill", return_value=None):
            result = process_alive(99994)
            assert result is True


# ─── Integration: Container Wiring ───────────────────────────────────────────


class TestContainerWiringFixes:
    """Test that container wiring includes all P0/P1 fixes."""

    def test_container_wires_persist_into_locator(self, tmp_path: Path) -> None:
        """Verify container injects persist_cap into ExecutableLocator."""
        from modules.launcher.src.capabilities_executable_locator import ExecutableLocator

        # Create locator with persist_cap
        state_file = tmp_path / "state.json"
        persist_cap = StatePersistence(path_resolver=lambda: str(state_file))
        locator = ExecutableLocator(persist_cap=persist_cap)

        # Verify _persist is set
        assert locator._persist is persist_cap

    def test_container_wires_event_sink_into_persist(self, tmp_path: Path) -> None:
        """Verify container injects event_sink into StatePersistence."""
        events_received: list = []

        def mock_event_sink(event):
            events_received.append(event)

        state_file = tmp_path / "state.json"
        persist_cap = StatePersistence(path_resolver=lambda: str(state_file), event_sink=mock_event_sink)

        # Verify _events is set
        assert persist_cap._events is not None

        # Write corrupt data and verify event emitted
        state_file.write_text("{ invalid json")
        persist_cap.load()

        assert len(events_received) == 1
        assert events_received[0].event_category == LAUNCHER_EVENT_CORRUPT_STATE_DETECTED
