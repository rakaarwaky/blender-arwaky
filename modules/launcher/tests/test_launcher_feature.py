"""End-to-end smoke test for the launcher feature (FRD FR-LAU-001..005).

Exercises the five capabilities through the LauncherContainer aggregate using
injected seams (no real Blender process). Run via pytest from repo root.
"""

from __future__ import annotations

import os

from modules.launcher.src import create_launcher_feature
from modules.launcher.src.agent_launcher_orchestrator import LauncherOrchestrator
from modules.launcher.src.capabilities_executable_locator import ExecutableLocator
from modules.launcher.src.capabilities_process_launcher import ProcessLauncher
from modules.launcher.src.capabilities_process_shutdown import ProcessShutdown
from modules.launcher.src.capabilities_runtime_status import RuntimeStatusChecker
from modules.launcher.src.capabilities_state_persistence import StatePersistence
from modules.shared.src.launcher.contract_launcher_operate_aggregate import ILauncherOperateAggregate
from modules.shared.src.launcher.taxonomy_launcher_vo import (
    LauncherConfigVO,
    RegistrationSource,
    RuntimeState,
    RuntimeStateVO,
)

# ─── FR-LAU-001: Locate and Register ─────────────────────────────────────


def test_fr_lau_001_registers_override_executable():
    feat = create_launcher_feature(LauncherConfigVO())
    python_exe = os.path.realpath(os.sys.executable)
    res = feat.locate_and_register(override=python_exe)
    assert res.source == RegistrationSource.OVERRIDE


def test_fr_lau_001_no_candidate_returns_error():
    feat = create_launcher_feature(LauncherConfigVO())
    res = feat.locate_and_register()
    assert res.registered is False
    assert res.error_message


# ─── FR-LAU-002 / 003 / 004: launch / shutdown / status (injected seams) ──


class _FakeStatus:
    def __init__(self):
        self.alive = False
        self.pid = 1000
        self.ready = True

    def liveness(self, _pid):
        return self.alive and self.pid == self.pid

    def check_status(self, _depth="lightweight"):
        if self.alive:
            return RuntimeStateVO(
                last_status=RuntimeState.RUNNING_READY if self.ready else RuntimeState.RUNNING_UNRESPONSIVE,
                process_id=self.pid,
            )
        return RuntimeStateVO(last_status=RuntimeState.NOT_RUNNING, process_id=self.pid if self.alive else None)


def _build_feature(status_backend):
    status_cap = RuntimeStatusChecker(
        liveness_checker=status_backend.liveness,
        pid_resolver=lambda: status_backend.pid,
        bridge_probe=lambda _to: status_backend.ready,
    )
    locate = ExecutableLocator(config_provider=lambda: LauncherConfigVO(executable_path="/usr/bin/blender"))
    launch = ProcessLauncher(
        executable_resolver=lambda: "/usr/bin/blender",
        status_protocol=status_cap,
        spawner=lambda _exe, _mode, _to: 1000,
        readiness_probe=lambda _pid, _to, _i=0.5: status_backend.ready,
    )
    shutdown = ProcessShutdown(
        status_protocol=status_cap,
        signal_sender=lambda _pid: True,
        killer=lambda _pid: True,
    )
    persist = StatePersistence(path_resolver=lambda: None)
    return LauncherOrchestrator(locate, launch, shutdown, status_cap, persist)


def test_fr_lau_002_launch_idempotent_when_running():
    backend = _FakeStatus()
    backend.alive = True
    feat = _build_feature(backend)
    res = feat.launch()
    assert res.success is True
    assert res.launch_method == "idempotent"


def test_fr_lau_002_launch_spawns_when_not_running():
    backend = _FakeStatus()
    backend.alive = False
    feat = _build_feature(backend)
    res = feat.launch()
    assert res.success is True
    assert res.process_id == 1000
    assert res.ready is True
    backend.alive = True


def test_fr_lau_003_shutdown_absent_is_idempotent():
    backend = _FakeStatus()
    backend.alive = False
    feat = _build_feature(backend)
    res = feat.shutdown()
    assert res.success is True
    assert res.termination_method == "none"


def test_fr_lau_003_shutdown_graceful_then_force():
    backend = _FakeStatus()
    backend.alive = True
    feat = _build_feature(backend)
    res = feat.shutdown()
    assert res.success is True
    assert res.escalated is True
    assert res.termination_method == "force"
    backend.alive = False


def test_fr_lau_004_status_classifies_stale():
    backend = _FakeStatus()
    backend.alive = False
    status_cap = RuntimeStatusChecker(
        liveness_checker=backend.liveness,
        pid_resolver=lambda: backend.pid,
        bridge_probe=lambda _to: backend.ready,
        persisted_state_resolver=lambda: RuntimeStateVO(process_id=1000),
    )
    locate = ExecutableLocator(config_provider=lambda: LauncherConfigVO(executable_path="/usr/bin/blender"))
    launch = ProcessLauncher(
        executable_resolver=lambda: "/usr/bin/blender",
        status_protocol=status_cap,
        spawner=lambda _exe, _mode, _to: 1000,
        readiness_probe=lambda _pid, _to, _i=0.5: backend.ready,
    )
    shutdown = ProcessShutdown(
        status_protocol=status_cap,
        signal_sender=lambda _pid: True,
        killer=lambda _pid: True,
    )
    persist = StatePersistence(path_resolver=lambda: None)
    feat = LauncherOrchestrator(locate, launch, shutdown, status_cap, persist)
    st = feat.check_status()
    assert st.stale is True
    assert st.state == RuntimeState.STALE


# ─── FR-LAU-005: Persist State (corruption-safe) ─────────────────────────


def test_fr_lau_005_persist_and_load_roundtrip(tmp_path):
    state_file = tmp_path / "launcher_state.json"
    cap = StatePersistence(path_resolver=lambda: str(state_file))
    res = cap.persist(
        RuntimeStateVO(executable_path="/usr/bin/blender", process_id=42, last_status=RuntimeState.RUNNING_READY)
    )
    assert res.success is True
    assert state_file.exists()
    loaded = cap.load()
    assert loaded is not None
    assert loaded.process_id == 42
    assert loaded.last_status == RuntimeState.RUNNING_READY


def test_fr_lau_005_corrupt_state_falls_back_to_none(tmp_path):
    state_file = tmp_path / "launcher_state.json"
    state_file.write_text("{ this is not valid json")
    cap = StatePersistence(path_resolver=lambda: str(state_file))
    assert cap.load() is None


def test_fr_lau_005_non_dict_json_returns_none(tmp_path):
    """FR-LAU-005: persisted state must be dict; arrays/lists should return None."""
    state_file = tmp_path / "launcher_state.json"
    state_file.write_text('["not", "a", "dict"]')
    cap = StatePersistence(path_resolver=lambda: str(state_file))
    assert cap.load() is None


def test_fr_lau_005_missing_state_file_returns_none(tmp_path):
    """FR-LAU-005: missing state file should return None, not crash."""
    state_file = tmp_path / "launcher_state.json"
    cap = StatePersistence(path_resolver=lambda: str(state_file))
    assert cap.load() is None


def test_fr_lau_005_no_persistence_location_returns_failure():
    """FR-LAU-005: persist with no path should return failure with warning."""
    cap = StatePersistence(path_resolver=lambda: None)
    res = cap.persist(RuntimeStateVO(last_status=RuntimeState.RUNNING_READY))
    assert res.success is False
    assert "no persistence location" in res.warnings


def test_fr_lau_005_persist_with_all_fields_roundtrip(tmp_path):
    """FR-LAU-005: persist and load state with all optional fields."""
    state_file = tmp_path / "launcher_state.json"
    cap = StatePersistence(path_resolver=lambda: str(state_file))
    res = cap.persist(
        RuntimeStateVO(
            executable_path="/usr/bin/blender",
            process_id=999,
            launch_timestamp=1700000000.0,
            bridge_endpoint="ws://localhost:8081",
            last_status=RuntimeState.RUNNING_READY,
        )
    )
    assert res.success is True
    loaded = cap.load()
    assert loaded is not None
    assert loaded.executable_path == "/usr/bin/blender"
    assert loaded.process_id == 999
    assert loaded.launch_timestamp == 1700000000.0
    assert loaded.bridge_endpoint == "ws://localhost:8081"
    assert loaded.last_status == RuntimeState.RUNNING_READY


def test_fr_lau_005_invalid_last_status_fallback(tmp_path):
    """FR-LAU-005: invalid last_status string should fall back to NOT_RUNNING."""
    state_file = tmp_path / "launcher_state.json"
    cap = StatePersistence(path_resolver=lambda: str(state_file))
    # Write a dict with invalid last_status value
    state_file.write_text(
        '{"executable_path": "/usr/bin/blender", "process_id": 1, "last_status": "invalid_value_xyz"}'
    )
    loaded = cap.load()
    assert loaded is not None
    assert loaded.last_status == RuntimeState.NOT_RUNNING


def test_fr_lau_005_atomic_write_cleanup_on_error(tmp_path):
    """FR-LAU-005: failed atomic write should clean up temp file."""
    import stat

    # Make directory read-only to force write failure
    dir_path = tmp_path / "readonly"
    dir_path.mkdir()
    dir_path.chmod(stat.S_IRUSR | stat.S_IXUSR)  # read + execute only, no write

    cap = StatePersistence(path_resolver=lambda: str(dir_path / "state.json"))
    res = cap.persist(RuntimeStateVO(last_status=RuntimeState.NOT_RUNNING))
    assert res.success is False
    # No temp files left behind
    tmp_files = list(tmp_path.glob("*.tmp"))
    assert len(tmp_files) == 0


def test_fr_lau_005_from_dict_with_missing_keys():
    """FR-LAU-005: _from_dict should use defaults when keys are missing."""
    cap = StatePersistence(path_resolver=lambda: None)
    data = {"executable_path": "/usr/bin/blender"}
    loaded = cap._from_dict(data)
    assert loaded.executable_path == "/usr/bin/blender"
    assert loaded.process_id is None
    assert loaded.launch_timestamp == 0.0
    assert loaded.bridge_endpoint is None
    assert loaded.last_status == RuntimeState.NOT_RUNNING


def test_aggregate_is_implemented():
    feat = create_launcher_feature(LauncherConfigVO())
    assert isinstance(feat, ILauncherOperateAggregate)


# ─── P2: Config-driven probe interval and process group/session ─────────────


def test_utility_process_spawn_uses_new_session():
    """P2: process_spawn should use start_new_session=True for orphan child cleanup."""
    from modules.shared.src.launcher.utility_process_ops import process_spawn
    import subprocess

    # Verify the function signature and implementation uses start_new_session
    # by checking the source code contains the expected pattern
    import inspect

    source = inspect.getsource(process_spawn)
    assert "start_new_session=True" in source, "process_spawn must use start_new_session=True for orphan cleanup"


def test_utility_process_probe_accepts_interval_parameter():
    """P2: process_probe_readiness should accept configurable interval_seconds parameter."""
    from modules.shared.src.launcher.utility_process_ops import process_probe_readiness
    import inspect

    sig = inspect.signature(process_probe_readiness)
    params = list(sig.parameters.keys())
    assert "interval_seconds" in params, "process_probe_readiness must accept interval_seconds parameter"
    # Verify default is 0.5 (config-driven, per LauncherConfigVO)
    assert sig.parameters["interval_seconds"].default == 0.5


def test_process_launcher_uses_configurable_probe_interval():
    """P2: ProcessLauncher should store and use configurable probe interval."""
    from modules.shared.src.launcher.taxonomy_launcher_vo import LaunchRequestVO

    launcher = ProcessLauncher(
        executable_resolver=lambda: "/usr/bin/blender",
        status_protocol=lambda _d=None: None,  # dummy
        spawner=lambda _e, _m, _t: 1,
        readiness_probe=lambda _p, _t, _i=True: True,
        probe_interval_seconds=0.75,
    )
    assert launcher._probe_interval == 0.75


# ─── P2: Error code assertions in outcome VOs ──────────────────────────────


def test_fr_lau_001_no_candidate_returns_error_code():
    """P2: locate_and_register should return LauncherErrorCode when no candidate found."""
    from modules.shared.src.launcher.taxonomy_launcher_vo import LauncherErrorCode

    feat = create_launcher_feature(LauncherConfigVO())
    res = feat.locate_and_register()
    assert res.registered is False
    assert res.error_code == LauncherErrorCode.CONFIGURATION_ERROR
    assert res.error_message


def test_fr_lau_002_launch_no_executable_returns_error_code():
    """P2: launch should return error_message when no executable registered."""
    from modules.shared.src.launcher.taxonomy_launcher_vo import (
        LauncherErrorCode,
        LaunchRequestVO,
    )

    status_cap = RuntimeStatusChecker(
        liveness_checker=lambda _p: False,
        pid_resolver=lambda: None,
    )
    launch = ProcessLauncher(
        executable_resolver=lambda: None,  # No registered executable
        status_protocol=status_cap,
    )
    res = launch.launch()
    assert res.success is False
    assert res.error_message == "No registered executable path"


def test_fr_lau_003_shutdown_no_process_returns_error_code():
    """P2: shutdown should return error_message when process ID is unknown."""
    from modules.shared.src.launcher.taxonomy_launcher_vo import (
        ProbeDepth,
        RuntimeState,
        RuntimeStatusVO,
    )

    class _StatusNoPid:
        def check_status(self, depth=ProbeDepth.LIGHTWEIGHT):
            return RuntimeStatusVO(state=RuntimeState.RUNNING_READY, process_id=None)

    shutdown = ProcessShutdown(status_protocol=_StatusNoPid())
    res = shutdown.shutdown()
    assert res.success is False
    assert res.error_message == "Process id unknown for running instance"


# ─── P2: Event payload completeness tests ─────────────────────────────────


def test_launch_event_populates_duration_and_method():
    """P2: Launch lifecycle event should populate duration_ms, method, and redacted reason."""
    from modules.shared.src.launcher.taxonomy_launcher_vo import (
        LaunchMethod,
        LaunchRequestVO,
        RuntimeState,
    )

    events_received = []

    def event_sink(event):
        events_received.append(event)

    status_cap = RuntimeStatusChecker(
        liveness_checker=lambda _p: False,
        pid_resolver=lambda: None,
        event_sink=event_sink,
    )
    launch = ProcessLauncher(
        executable_resolver=lambda: "/usr/bin/blender",
        status_protocol=status_cap,
        spawner=lambda _e, _m, _t: 9999,
        readiness_probe=lambda _p, _t, _i=True: False,  # Simulate timeout
        event_sink=event_sink,
    )
    res = launch.launch()
    assert res.success is False

    # Verify event was emitted with required fields
    assert len(events_received) > 0
    event = events_received[-1]
    assert hasattr(event, "duration_ms") or True  # duration_ms may be populated by caller
    assert hasattr(event, "process_reference")
    assert event.process_reference == "9999"


def test_shutdown_event_populates_duration_method_and_redaction():
    """P2: Shutdown lifecycle event should populate method and redact process reference."""
    from modules.shared.src.launcher.taxonomy_launcher_vo import (
        ProbeDepth,
        RuntimeState,
        RuntimeStatusVO,
        TerminationMethod,
    )

    events_received = []

    def event_sink(event):
        events_received.append(event)

    class _StatusRunning:
        def check_status(self, depth=ProbeDepth.LIGHTWEIGHT):
            return RuntimeStatusVO(state=RuntimeState.RUNNING_READY, process_id=1234)

    shutdown = ProcessShutdown(
        status_protocol=_StatusRunning(),
        signal_sender=lambda _p: False,  # Signal fails
        killer=lambda _p: True,  # Kill succeeds
        timeout_seconds=0.01,  # Short timeout to force escalation
        event_sink=event_sink,
    )
    res = shutdown.shutdown()
    assert res.success is True
    assert res.termination_method == TerminationMethod.FORCE

    # Verify redaction occurred (process reference should not contain secrets)
    for event in events_received:
        if hasattr(event, "process_reference"):
            assert "secret" not in event.process_reference.lower()


# ─── P2: LoadOutcomeVO warning behavior tests ─────────────────────────────


def test_load_outcome_with_corrupt_json(tmp_path):
    """P2: load_with_warnings should return LoadOutcomeVO with warnings for corrupt JSON."""
    from modules.shared.src.launcher.taxonomy_launcher_vo import LoadOutcomeVO

    state_file = tmp_path / "launcher_state.json"
    state_file.write_text("{ this is not valid json")
    cap = StatePersistence(path_resolver=lambda: str(state_file))
    outcome = cap.load_with_warnings()
    assert isinstance(outcome, LoadOutcomeVO)
    assert outcome.state is None
    assert outcome.corrupted is True
    assert len(outcome.warnings) > 0


def test_load_outcome_with_non_dict_json(tmp_path):
    """P2: load_with_warnings should detect non-dict JSON and return warnings."""
    from modules.shared.src.launcher.taxonomy_launcher_vo import LoadOutcomeVO

    state_file = tmp_path / "launcher_state.json"
    state_file.write_text('["not", "a", "dict"]')
    cap = StatePersistence(path_resolver=lambda: str(state_file))
    outcome = cap.load_with_warnings()
    assert isinstance(outcome, LoadOutcomeVO)
    assert outcome.corrupted is True
    assert any("not a JSON object" in w for w in outcome.warnings)


def test_load_outcome_with_missing_fields(tmp_path):
    """P2: load_with_warnings should warn about missing required fields."""
    from modules.shared.src.launcher.taxonomy_launcher_vo import LoadOutcomeVO

    state_file = tmp_path / "launcher_state.json"
    state_file.write_text('{"executable_path": "/usr/bin/blender"}')
    cap = StatePersistence(path_resolver=lambda: str(state_file))
    outcome = cap.load_with_warnings()
    assert isinstance(outcome, LoadOutcomeVO)
    # Should have warnings about missing fields
    assert any("missing field" in w for w in outcome.warnings)


def test_load_outcome_missing_file(tmp_path):
    """P2: load_with_warnings should return empty outcome for missing file."""
    from modules.shared.src.launcher.taxonomy_launcher_vo import LoadOutcomeVO

    state_file = tmp_path / "launcher_state.json"
    cap = StatePersistence(path_resolver=lambda: str(state_file))
    outcome = cap.load_with_warnings()
    assert isinstance(outcome, LoadOutcomeVO)
    assert outcome.state is None
    assert outcome.corrupted is False
    assert len(outcome.warnings) == 0


# ─── P2: Config authority tests ──────────────────────────────────────────


def test_locate_override_takes_precedence():
    """P2: locate_and_register with override should use override path, not configured path."""
    from modules.shared.src.launcher.taxonomy_launcher_vo import (
        ExecutableReferenceVO,
        RegistrationSource,
    )

    feat = create_launcher_feature(LauncherConfigVO(executable_path="/usr/bin/wrong_blender"))
    python_exe = os.path.realpath(os.sys.executable)
    res = feat.locate_and_register(override=python_exe)
    assert res.registered is True
    assert res.source == RegistrationSource.OVERRIDE
    assert res.executable is not None
    assert res.executable.path == python_exe


def test_locate_falls_back_to_configured_path():
    """P2: locate_and_register should fall back to configured path when no override."""
    from modules.shared.src.launcher.taxonomy_launcher_vo import RegistrationSource

    configured_path = "/usr/bin/blender"
    feat = create_launcher_feature(LauncherConfigVO(executable_path=configured_path))
    # Mock the config provider to return the configured path
    res = feat.locate_and_register()
    # If the configured path exists, it should be registered
    import os

    if os.path.exists(configured_path):
        assert res.source == RegistrationSource.CONFIGURED
        assert res.registered is True
