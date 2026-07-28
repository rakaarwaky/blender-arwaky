"""Tests for DiagnosticsCapability health composition — FR-DIA-001.

Exercises health status derivation, subsystem coverage, staleness indicators,
and composition idempotency via the unified DiagnosticsCapability class.
Run via pytest from repo root.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

import pytest

from modules.diagnostics.src.capabilities_health_composition import DiagnosticsCapability


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _make_capability() -> DiagnosticsCapability:
    """Create a fresh DiagnosticsCapability instance."""
    return DiagnosticsCapability()


# ─── FR-DIA-001: Compose System Health ──────────────────────────────────────


class TestHealthCompositionStatusDerivation:
    """Test overall status derives deterministically from subsystem states."""

    def test_all_healthy_returns_overall_healthy(self) -> None:
        """FR-DIA-001: healthy when all required subsystems report healthy."""
        cap = _make_capability()
        result = asyncio.run(
            cap.compose_health(
                launcher_status="healthy",
                gateway_status="healthy",
                config_valid=True,
                job_capacity_available=True,
            )
        )
        assert result["overall_status"] == "healthy"

    def test_any_unhealthy_returns_overall_unhealthy(self) -> None:
        """FR-DIA-001: unhealthy when any required subsystem reports unhealthy."""
        cap = _make_capability()
        result = asyncio.run(
            cap.compose_health(
                launcher_status="unhealthy",
                gateway_status="healthy",
                config_valid=True,
                job_capacity_available=True,
            )
        )
        assert result["overall_status"] == "unhealthy"

    def test_any_failed_returns_overall_unhealthy(self) -> None:
        """FR-DIA-001: unhealthy when any required subsystem reports failed."""
        cap = _make_capability()
        result = asyncio.run(
            cap.compose_health(
                launcher_status="healthy",
                gateway_status="failed",
                config_valid=True,
                job_capacity_available=True,
            )
        )
        assert result["overall_status"] == "unhealthy"

    def test_any_unreachable_returns_overall_unhealthy(self) -> None:
        """FR-DIA-001: unhealthy when any required subsystem reports unreachable."""
        cap = _make_capability()
        result = asyncio.run(
            cap.compose_health(
                launcher_status="healthy",
                gateway_status="unreachable",
                config_valid=True,
                job_capacity_available=True,
            )
        )
        assert result["overall_status"] == "unhealthy"

    def test_any_degraded_returns_overall_degraded(self) -> None:
        """FR-DIA-001: degraded when any required subsystem reports degraded."""
        cap = _make_capability()
        result = asyncio.run(
            cap.compose_health(
                launcher_status="degraded",
                gateway_status="healthy",
                config_valid=True,
                job_capacity_available=True,
            )
        )
        assert result["overall_status"] == "degraded"

    def test_config_invalid_returns_unhealthy(self) -> None:
        """FR-DIA-001: invalid config makes overall status unhealthy."""
        cap = _make_capability()
        result = asyncio.run(
            cap.compose_health(
                launcher_status="healthy",
                gateway_status="healthy",
                config_valid=False,
                job_capacity_available=True,
            )
        )
        assert result["overall_status"] == "unhealthy"

    def test_job_capacity_exhausted_returns_degraded(self) -> None:
        """FR-DIA-001: exhausted job capacity makes overall status degraded."""
        cap = _make_capability()
        result = asyncio.run(
            cap.compose_health(
                launcher_status="healthy",
                gateway_status="healthy",
                config_valid=True,
                job_capacity_available=False,
            )
        )
        assert result["overall_status"] == "degraded"

    def test_unknown_statuses_are_degraded(self) -> None:
        """FR-DIA-001: unknown/timeout statuses contribute degraded (not unhealthy)."""
        cap = _make_capability()
        result = asyncio.run(
            cap.compose_health(
                launcher_status="unknown",
                gateway_status="healthy",
                config_valid=True,
                job_capacity_available=True,
            )
        )
        assert result["overall_status"] == "degraded"


class TestSubsystemCoverage:
    """Test composed health covers required subsystems."""

    def test_health_contains_launcher(self) -> None:
        """FR-DIA-001: composed health must include launcher status."""
        cap = _make_capability()
        result = asyncio.run(
            cap.compose_health(launcher_status="healthy", gateway_status="healthy", config_valid=True)
        )
        assert "launcher" in result["subsystems"]

    def test_health_contains_gateway(self) -> None:
        """FR-DIA-001: composed health must include gateway status."""
        cap = _make_capability()
        result = asyncio.run(
            cap.compose_health(launcher_status="healthy", gateway_status="healthy", config_valid=True)
        )
        assert "gateway" in result["subsystems"]

    def test_health_contains_config(self) -> None:
        """FR-DIA-001: composed health must include config validity."""
        cap = _make_capability()
        result = asyncio.run(
            cap.compose_health(launcher_status="healthy", gateway_status="healthy", config_valid=True)
        )
        assert "config" in result["subsystems"]

    def test_health_contains_job_capacity(self) -> None:
        """FR-DIA-001: composed health must include job capacity."""
        cap = _make_capability()
        result = asyncio.run(
            cap.compose_health(launcher_status="healthy", gateway_status="healthy", config_valid=True)
        )
        assert "job_capacity" in result["subsystems"]

    def test_config_status_derives_from_validity(self) -> None:
        """FR-DIA-001: config subsystem status reflects validity."""
        cap = _make_capability()
        result = asyncio.run(
            cap.compose_health(launcher_status="healthy", gateway_status="healthy", config_valid=True)
        )
        assert result["subsystems"]["config"] == "healthy"

    def test_config_invalid_makes_subsystem_unhealthy(self) -> None:
        """FR-DIA-001: invalid config maps to unhealthy subsystem status."""
        cap = _make_capability()
        result = asyncio.run(
            cap.compose_health(launcher_status="healthy", gateway_status="healthy", config_valid=False)
        )
        assert result["subsystems"]["config"] == "unhealthy"

    def test_job_capacity_healthy_when_available(self) -> None:
        """FR-DIA-001: job capacity is healthy when slots available."""
        cap = _make_capability()
        result = asyncio.run(
            cap.compose_health(
                launcher_status="healthy", gateway_status="healthy", config_valid=True, job_capacity_available=True
            )
        )
        assert result["subsystems"]["job_capacity"] == "healthy"

    def test_job_capacity_degraded_when_exhausted(self) -> None:
        """FR-DIA-001: job capacity is degraded when slots exhausted."""
        cap = _make_capability()
        result = asyncio.run(
            cap.compose_health(
                launcher_status="healthy", gateway_status="healthy", config_valid=True, job_capacity_available=False
            )
        )
        assert result["subsystems"]["job_capacity"] == "degraded"


class TestTimestampAndComposition:
    """Test composition timestamp and read-only/idempotent behavior."""

    def test_composition_has_timestamp(self) -> None:
        """FR-DIA-001: composition includes timestamp."""
        cap = _make_capability()
        result = asyncio.run(
            cap.compose_health(launcher_status="healthy", gateway_status="healthy", config_valid=True)
        )
        assert "composition_timestamp" in result

    def test_timestamp_is_iso_format(self) -> None:
        """FR-DIA-001: timestamp is ISO-formatted string."""
        cap = _make_capability()
        result = asyncio.run(
            cap.compose_health(launcher_status="healthy", gateway_status="healthy", config_valid=True)
        )
        assert "T" in result["composition_timestamp"]
        assert "Z" not in result["composition_timestamp"]  # UTC uses +00:00 or no Z

    def test_composition_is_read_only(self) -> None:
        """FR-DIA-001: composition never mutates subsystems."""
        cap = _make_capability()
        # Compose once
        asyncio.run(
            cap.compose_health(launcher_status="healthy", gateway_status="healthy", config_valid=True)
        )
        # Compose again with different inputs — should not affect previous internal state unexpectedly
        result2 = asyncio.run(
            cap.compose_health(launcher_status="unhealthy", gateway_status="unhealthy", config_valid=False)
        )
        assert result2["overall_status"] == "unhealthy"

    def test_multiple_compositions_are_idempotent_same_inputs(self) -> None:
        """FR-DIA-001: repeated composition with same inputs yields consistent status."""
        cap = _make_capability()
        r1 = asyncio.run(
            cap.compose_health(launcher_status="healthy", gateway_status="healthy", config_valid=True)
        )
        r2 = asyncio.run(
            cap.compose_health(launcher_status="healthy", gateway_status="healthy", config_valid=True)
        )
        assert r1["overall_status"] == r2["overall_status"]


class TestEdgeCases:
    """Test edge cases from FR-DIA-001."""

    def test_all_unknown_returns_degraded(self) -> None:
        """FR-DIA-001: all unknown subsystems with valid config → degraded."""
        cap = _make_capability()
        result = asyncio.run(
            cap.compose_health(
                launcher_status="unknown",
                gateway_status="unknown",
                config_valid=True,
                job_capacity_available=True,
            )
        )
        assert result["overall_status"] == "degraded"

    def test_mixed_statuses_derive_correctly(self) -> None:
        """FR-DIA-001: mixed healthy/degraded → degraded (not unhealthy)."""
        cap = _make_capability()
        result = asyncio.run(
            cap.compose_health(
                launcher_status="healthy",
                gateway_status="degraded",
                config_valid=True,
                job_capacity_available=True,
            )
        )
        assert result["overall_status"] == "degraded"

    def test_first_run_with_no_subsystems_initialized(self) -> None:
        """FR-DIA-001: first run with unknown statuses and valid config → degraded."""
        cap = _make_capability()
        result = asyncio.run(
            cap.compose_health(
                launcher_status="unknown",
                gateway_status="unknown",
                config_valid=True,
                job_capacity_available=True,
            )
        )
        assert result["overall_status"] == "degraded"

    def test_stale_subsystem_data_indicated(self) -> None:
        """FR-DIA-001: stale data carries explicit staleness indicator."""
        cap = _make_capability()
        # The capability stores health state internally
        asyncio.run(
            cap.compose_health(launcher_status="healthy", gateway_status="healthy", config_valid=True)
        )
        # Internal state should have timestamp for staleness comparison
        assert "composition_timestamp" in cap._health_state
