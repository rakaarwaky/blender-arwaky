"""End-to-end smoke test for the launcher feature (FRD FR-LAU-001..005).

Exercises the five capabilities through the LauncherContainer aggregate using
injected seams (no real Blender process). Run via pytest from repo root.
"""

from __future__ import annotations

import os
import tempfile

import pytest

from modules.launcher.src import create_launcher_feature
from modules.shared.src.launcher.taxonomy_launcher_vo import (
    LauncherConfigVO,
    RegistrationSource,
    RuntimeState,
    RuntimeStateVO,
)
from modules.shared.src.launcher.contract_launcher_operate_aggregate import LauncherOperateAggregate
from modules.launcher.src.agent_launcher_orchestrator import LauncherOrchestrator
from modules.launcher.src.capabilities_executable_locator import ExecutableLocator
from modules.launcher.src.capabilities_process_launcher import ProcessLauncher
from modules.launcher.src.capabilities_process_shutdown import ProcessShutdown
from modules.launcher.src.capabilities_runtime_status import RuntimeStatusChecker
from modules.launcher.src.capabilities_state_persistence import StatePersistence


# ─── FR-LAU-001: Locate and Register ─────────────────────────────────────

def test_fr_lau_001_registers_override_executable():
    feat = create_launcher_feature(LauncherConfigVO())
    python_exe = os.path.realpath(os.sys.executable)
    res = feat.locate_and_register(LauncherConfigVO(), override=python_exe)
    assert res.source == RegistrationSource.OVERRIDE


def test_fr_lau_001_no_candidate_returns_error():
    feat = create_launcher_feature(LauncherConfigVO())
    res = feat.locate_and_register(LauncherConfigVO())
    assert res.registered is False
    assert res.error


# ─── FR-LAU-002 / 003 / 004: launch / shutdown / status (injected seams) ──

class _FakeStatus:
    def __init__(self):
        self.alive = False
        self.pid = 1000
        self.ready = True

    def liveness(self, pid):
        return self.alive and pid == self.pid

    def check_status(self, depth="lightweight"):
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
        bridge_probe=lambda to: status_backend.ready,
    )
    locate = ExecutableLocator(config_provider=lambda: LauncherConfigVO(executable_path="/usr/bin/blender"))
    launch = ProcessLauncher(
        executable_resolver=lambda: "/usr/bin/blender",
        status_protocol=status_cap,
        spawner=lambda exe, mode, to: 1000,
        readiness_probe=lambda pid, to: status_backend.ready,
    )
    shutdown = ProcessShutdown(
        status_protocol=status_cap,
        signal_sender=lambda pid: True,
        killer=lambda pid: True,
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
    feat = _build_feature(backend)
    feat.status._resolve_persisted = lambda: RuntimeStateVO(process_id=1000)
    st = feat.check_status()
    assert st.stale is True
    assert st.state == RuntimeState.STALE


# ─── FR-LAU-005: Persist State (corruption-safe) ─────────────────────────

def test_fr_lau_005_persist_and_load_roundtrip(tmp_path):
    state_file = tmp_path / "launcher_state.json"
    cap = StatePersistence(path_resolver=lambda: str(state_file))
    res = cap.persist(RuntimeStateVO(
        executable_path="/usr/bin/blender", process_id=42, last_status=RuntimeState.RUNNING_READY))
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


def test_aggregate_is_implemented():
    feat = create_launcher_feature(LauncherConfigVO())
    assert isinstance(feat, LauncherOperateAggregate)
