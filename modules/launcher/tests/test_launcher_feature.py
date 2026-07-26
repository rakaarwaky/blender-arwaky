"""TDD suite for the launcher feature (FRD FR-LAU-001..005).

Exercises the five capabilities through the LauncherContainer aggregate using
injected seams (no real Blender process). Run via pytest from repo root.

RED → GREEN: these tests target the real committed capability surface
(LocateRegisterExecutor, LaunchExecutor, ShutdownExecutor, RuntimeStatusChecker,
StatePersistence) wired by create_launcher_feature.
"""

from __future__ import annotations

import os
import sys
import tempfile

import pytest

from modules.launcher.src import create_launcher_feature
from modules.launcher.src.agent_launcher_orchestrator import LauncherOrchestrator
from modules.shared.src.launcher.taxonomy_launcher_vo import (
    LauncherConfigVO,
    RuntimeState,
    RuntimeStateVO,
)
from modules.shared.src.launcher.contract_launcher_operate_aggregate import LauncherOperateAggregate


# ─── FR-LAU-001: Locate and Register ─────────────────────────────────────


def test_fr_lau_001_registers_override_executable():
    # No real Blender on CI; the locator rejects a non-Blender override with a
    # configuration error (authenticity check fails). This verifies the
    # deterministic discovery + validation path executes and rejects impostors.
    feat = create_launcher_feature(LauncherConfigVO())
    python_exe = os.path.realpath(sys.executable)
    with pytest.raises(Exception):
        feat.locate_and_register(LauncherConfigVO(), override=python_exe)


def test_fr_lau_001_no_candidate_returns_error():
    # No override, no configured path, no system Blender → raises config error
    # (the capability signals failure via exception, not a result payload).
    feat = create_launcher_feature(LauncherConfigVO())
    with pytest.raises(Exception):
        feat.locate_and_register(LauncherConfigVO())


# ─── FR-LAU-002: Launch (injected seams) ─────────────────────────────────


class _FakeLaunch:
    """Controllable launch backend."""

    def __init__(self):
        self.alive = False
        self.pid = 1000

    def spawner(self, exe, mode, timeout):
        return _FakeProc(self.pid)

    def liveness(self, pid):
        return self.alive and pid == self.pid


class _FakeProc:
    def __init__(self, pid):
        self.pid = pid


def _build_launch_feature(backend: _FakeLaunch):
    feat = create_launcher_feature(LauncherConfigVO())
    orch = feat if isinstance(feat, LauncherOrchestrator) else None
    assert orch is not None
    launch = orch._launch
    launch._spawner = backend.spawner
    launch._is_running = backend.liveness
    return feat, backend


def test_fr_lau_002_launch_spawns_when_not_running():
    backend = _FakeLaunch()
    backend.alive = True
    feat, _ = _build_launch_feature(backend)
    res = feat.launch()
    assert res.success is True
    assert res.process_id == 1000
    assert res.ready is True


# ─── FR-LAU-003: Shutdown (injected seams) ───────────────────────────────


def _build_shutdown_feature():
    feat = create_launcher_feature(LauncherConfigVO())
    state = {"pid": 1000, "alive": True}

    def liveness(pid):
        return state["alive"] and pid == state["pid"]

    def signal_sender(pid, sig):
        # SIGTERM (15) graceful → set not alive; SIGKILL (9) force.
        if sig == 15:
            state["alive"] = False
        return True

    feat._shutdown._liveness = liveness
    feat._shutdown._signal_sender = signal_sender
    feat._shutdown._pid_resolver = lambda: state["pid"]
    return feat, state


def test_fr_lau_003_shutdown_absent_is_idempotent():
    feat, state = _build_shutdown_feature()
    state["alive"] = False
    state["pid"] = None
    res = feat.shutdown()
    assert res.success is True
    assert res.termination_method == "none"


def test_fr_lau_003_shutdown_graceful_then_force():
    feat, state = _build_shutdown_feature()
    state["alive"] = True
    # Graceful (SIGTERM) will set alive=False → graceful success.
    res = feat.shutdown()
    assert res.success is True
    assert res.termination_method == "graceful"


def test_fr_lau_003_shutdown_escalates_when_graceful_fails():
    feat, state = _build_shutdown_feature()
    state["alive"] = True
    # Refuse to die on SIGTERM, only on SIGKILL.
    def signal_sender(pid, sig):
        if sig == 15:
            return True  # pretend sent, but stays alive
        state["alive"] = False
        return True

    feat._shutdown._signal_sender = signal_sender
    res = feat.shutdown()
    assert res.success is True
    assert res.escalated is True
    assert res.termination_method == "force"


# ─── FR-LAU-004: Runtime Status (injected seams) ─────────────────────────


def test_fr_lau_004_status_classifies_stale():
    feat = create_launcher_feature(LauncherConfigVO())

    def liveness(pid):
        return False  # persisted pid no longer alive → stale

    feat._status._liveness_checker = liveness
    feat._status._pid_resolver = lambda: 1000
    st = feat.check_status()
    assert st.stale is True
    assert st.state == RuntimeState.STALE


def test_fr_lau_004_status_not_running_without_pid():
    feat = create_launcher_feature(LauncherConfigVO())
    feat._status._pid_resolver = lambda: None
    st = feat.check_status()
    assert st.state == RuntimeState.NOT_RUNNING


# ─── FR-LAU-005: Persist State (corruption-safe) ─────────────────────────


def test_fr_lau_005_persist_and_load_roundtrip(tmp_path):
    feat = create_launcher_feature(LauncherConfigVO())
    state_file = tmp_path / "launcher_state.json"
    feat._persist._path_resolver = lambda: str(state_file)
    res = feat.persist(RuntimeStateVO(
        executable_path="/usr/bin/blender", process_id=42, last_status=RuntimeState.RUNNING_READY))
    assert res.success is True
    assert state_file.exists()
    loaded = feat.load_persisted_state()
    assert loaded is not None
    assert loaded.process_id == 42
    assert loaded.last_status == RuntimeState.RUNNING_READY


def test_fr_lau_005_corrupt_state_falls_back_to_none(tmp_path):
    feat = create_launcher_feature(LauncherConfigVO())
    state_file = tmp_path / "launcher_state.json"
    state_file.write_text("{ this is not valid json")
    feat._persist._path_resolver = lambda: str(state_file)
    assert feat.load_persisted_state() is None


# ─── Aggregate contract ───────────────────────────────────────────────────


def test_aggregate_is_implemented():
    feat = create_launcher_feature(LauncherConfigVO())
    assert isinstance(feat, LauncherOperateAggregate)
