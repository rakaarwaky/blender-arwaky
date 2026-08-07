"""Unit tests for MaintenanceExecutor reconnect retry / exhaustion (FR-GWY-002).

The production `attempt_reconnect` must be able to transition the connection
to a FAILED terminal state when reconnect attempts are exhausted — previously
the FAILED branch was unreachable dead code (the method always reported
CONNECTED). These tests exercise the reconnect hook directly with fakes so no
real Blender socket is opened.
"""

from __future__ import annotations

from dataclasses import dataclass

from modules.gateway.src.capabilities_connection_maintenance import MaintenanceExecutor
from modules.shared.src.gateway.taxonomy_gateway_vo import ConnectionState


@dataclass
class _FakeOutcome:
    state: ConnectionState
    error: str | None = None


def test_reconnect_success_transitions_to_connected():
    executor = MaintenanceExecutor(reconnect_fn=lambda: _FakeOutcome(ConnectionState.CONNECTED))
    status = executor.attempt_reconnect()
    assert status.state == ConnectionState.CONNECTED
    assert status.reconnect_attempts == 1
    assert status.last_failure_reason is None


def test_reconnect_failure_transitions_to_failed():
    executor = MaintenanceExecutor(
        reconnect_fn=lambda: _FakeOutcome(ConnectionState.FAILED, "connection refused")
    )
    status = executor.attempt_reconnect()
    assert status.state == ConnectionState.FAILED
    assert status.reconnect_attempts == 1
    assert "connection refused" in (status.last_failure_reason or "")


def test_reconnect_exhaustion_stays_failed():
    executor = MaintenanceExecutor(
        max_retries=2,
        reconnect_fn=lambda: _FakeOutcome(ConnectionState.FAILED, "connection refused"),
    )
    first = executor.attempt_reconnect()
    assert first.state == ConnectionState.FAILED
    second = executor.attempt_reconnect()
    assert second.state == ConnectionState.FAILED
    assert second.reconnect_attempts == 2


def test_reconnect_can_recover_to_connected_after_failures():
    states = iter([ConnectionState.FAILED, ConnectionState.FAILED, ConnectionState.CONNECTED])
    executor = MaintenanceExecutor(
        max_retries=3,
        reconnect_fn=lambda: _FakeOutcome(next(states)),
    )
    assert executor.attempt_reconnect().state == ConnectionState.FAILED
    assert executor.attempt_reconnect().state == ConnectionState.FAILED
    recovered = executor.attempt_reconnect()
    assert recovered.state == ConnectionState.CONNECTED
    assert recovered.reconnect_attempts == 3


def test_reconnect_raised_exception_treated_as_failure():
    def boom() -> _FakeOutcome:
        raise OSError("connection reset by peer")

    executor = MaintenanceExecutor(reconnect_fn=boom)
    status = executor.attempt_reconnect()
    assert status.state == ConnectionState.FAILED
    assert "connection reset" in (status.last_failure_reason or "")


def test_reconnect_none_outcome_treated_as_failure():
    executor = MaintenanceExecutor(reconnect_fn=lambda: None)
    status = executor.attempt_reconnect()
    assert status.state == ConnectionState.FAILED


def test_reconnect_without_hook_transitions_to_failed():
    executor = MaintenanceExecutor()
    status = executor.attempt_reconnect()
    assert status.state == ConnectionState.FAILED
    assert "No reconnect function configured" in (status.last_failure_reason or "")


def test_reconnect_counter_resets_after_exhaustion():
    executor = MaintenanceExecutor(
        max_retries=2,
        reconnect_fn=lambda: _FakeOutcome(ConnectionState.FAILED, "down"),
    )
    assert executor.attempt_reconnect().reconnect_attempts == 1
    assert executor.attempt_reconnect().reconnect_attempts == 2  # session exhausted
    # A later connection drop starts a fresh session at 1, not 3.
    assert executor.attempt_reconnect().reconnect_attempts == 1


def test_reconnect_counter_resets_after_recovery():
    states = iter(
        [
            ConnectionState.FAILED,
            ConnectionState.CONNECTED,
            ConnectionState.CONNECTED,
        ]
    )
    executor = MaintenanceExecutor(
        max_retries=3,
        reconnect_fn=lambda: _FakeOutcome(next(states)),
    )
    assert executor.attempt_reconnect().reconnect_attempts == 1  # FAILED
    assert executor.attempt_reconnect().reconnect_attempts == 2  # recovered
    # After recovery, state is CONNECTED — early return resets counter.
    assert executor.attempt_reconnect().reconnect_attempts == 0
