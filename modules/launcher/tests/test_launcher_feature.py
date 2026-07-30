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
        readiness_probe=lambda _pid, _to: status_backend.ready,
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
        readiness_probe=lambda _pid, _to: backend.ready,
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
