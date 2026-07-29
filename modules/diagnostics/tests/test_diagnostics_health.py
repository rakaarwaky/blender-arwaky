"""Tests for HealthComposer — FR-DIA-001.

Exercises health status derivation, subsystem coverage, probe timeout,
staleness indicators, and composition idempotency via HealthComposer.
Run via pytest from repo root.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch

from modules.diagnostics.src.capabilities_health_composition import HealthComposer


def _make_composer() -> HealthComposer:
    return HealthComposer()


class TestHealthCompositionStatusDerivation:
    """Test overall status derives deterministically from subsystem states."""

    def test_all_healthy_returns_overall_healthy(self) -> None:
        cap = _make_composer()
        result = asyncio.run(
            cap.compose_health(
                launcher_status="healthy",
                gateway_status="healthy",
                config_valid=True,
                job_capacity_available=True,
            )
        )
        assert result.overall_status == "healthy"

    def test_any_unhealthy_returns_overall_unhealthy(self) -> None:
        cap = _make_composer()
        result = asyncio.run(
            cap.compose_health(
                launcher_status="unhealthy",
                gateway_status="healthy",
                config_valid=True,
                job_capacity_available=True,
            )
        )
        assert result.overall_status == "unhealthy"

    def test_any_failed_returns_overall_unhealthy(self) -> None:
        cap = _make_composer()
        result = asyncio.run(
            cap.compose_health(
                launcher_status="healthy",
                gateway_status="failed",
                config_valid=True,
                job_capacity_available=True,
            )
        )
        assert result.overall_status == "unhealthy"

    def test_any_unreachable_returns_overall_unhealthy(self) -> None:
        cap = _make_composer()
        result = asyncio.run(
            cap.compose_health(
                launcher_status="healthy",
                gateway_status="unreachable",
                config_valid=True,
                job_capacity_available=True,
            )
        )
        assert result.overall_status == "unhealthy"

    def test_any_degraded_returns_overall_degraded(self) -> None:
        cap = _make_composer()
        result = asyncio.run(
            cap.compose_health(
                launcher_status="degraded",
                gateway_status="healthy",
                config_valid=True,
                job_capacity_available=True,
            )
        )
        assert result.overall_status == "degraded"

    def test_config_invalid_returns_unhealthy(self) -> None:
        cap = _make_composer()
        result = asyncio.run(
            cap.compose_health(
                launcher_status="healthy",
                gateway_status="healthy",
                config_valid=False,
                job_capacity_available=True,
            )
        )
        assert result.overall_status == "unhealthy"

    def test_job_capacity_exhausted_returns_degraded(self) -> None:
        cap = _make_composer()
        result = asyncio.run(
            cap.compose_health(
                launcher_status="healthy",
                gateway_status="healthy",
                config_valid=True,
                job_capacity_available=False,
            )
        )
        assert result.overall_status == "degraded"

    def test_unknown_statuses_are_degraded(self) -> None:
        cap = _make_composer()
        result = asyncio.run(
            cap.compose_health(
                launcher_status="unknown",
                gateway_status="healthy",
                config_valid=True,
                job_capacity_available=True,
            )
        )
        assert result.overall_status == "degraded"


class TestSubsystemCoverage:
    """Test composed health covers required subsystems."""

    def test_health_contains_launcher(self) -> None:
        cap = _make_composer()
        result = asyncio.run(
            cap.compose_health(launcher_status="healthy", gateway_status="healthy", config_valid=True)
        )
        names = [s.name for s in result.subsystems]
        assert "launcher" in names

    def test_health_contains_gateway(self) -> None:
        cap = _make_composer()
        result = asyncio.run(
            cap.compose_health(launcher_status="healthy", gateway_status="healthy", config_valid=True)
        )
        names = [s.name for s in result.subsystems]
        assert "gateway" in names

    def test_health_contains_config(self) -> None:
        cap = _make_composer()
        result = asyncio.run(
            cap.compose_health(launcher_status="healthy", gateway_status="healthy", config_valid=True)
        )
        names = [s.name for s in result.subsystems]
        assert "config" in names

    def test_health_contains_job_capacity(self) -> None:
        cap = _make_composer()
        result = asyncio.run(
            cap.compose_health(launcher_status="healthy", gateway_status="healthy", config_valid=True)
        )
        names = [s.name for s in result.subsystems]
        assert "job_capacity" in names

    def test_config_status_derives_from_validity(self) -> None:
        cap = _make_composer()
        result = asyncio.run(
            cap.compose_health(launcher_status="healthy", gateway_status="healthy", config_valid=True)
        )
        config_subs = [s for s in result.subsystems if s.name == "config"]
        assert len(config_subs) == 1
        assert config_subs[0].status == "healthy"

    def test_config_invalid_makes_subsystem_unhealthy(self) -> None:
        cap = _make_composer()
        result = asyncio.run(
            cap.compose_health(launcher_status="healthy", gateway_status="healthy", config_valid=False)
        )
        config_subs = [s for s in result.subsystems if s.name == "config"]
        assert len(config_subs) == 1
        assert config_subs[0].status == "unhealthy"

    def test_job_capacity_healthy_when_available(self) -> None:
        cap = _make_composer()
        result = asyncio.run(
            cap.compose_health(
                launcher_status="healthy", gateway_status="healthy", config_valid=True, job_capacity_available=True
            )
        )
        job_subs = [s for s in result.subsystems if s.name == "job_capacity"]
        assert len(job_subs) == 1
        assert job_subs[0].status == "healthy"

    def test_job_capacity_degraded_when_exhausted(self) -> None:
        cap = _make_composer()
        result = asyncio.run(
            cap.compose_health(
                launcher_status="healthy", gateway_status="healthy", config_valid=True, job_capacity_available=False
            )
        )
        job_subs = [s for s in result.subsystems if s.name == "job_capacity"]
        assert len(job_subs) == 1
        assert job_subs[0].status == "degraded"


class TestTimestampAndComposition:
    """Test composition timestamp and read-only/idempotent behavior."""

    def test_composition_has_timestamp(self) -> None:
        cap = _make_composer()
        result = asyncio.run(
            cap.compose_health(launcher_status="healthy", gateway_status="healthy", config_valid=True)
        )
        assert result.composition_timestamp != ""

    def test_timestamp_is_iso_format(self) -> None:
        cap = _make_composer()
        result = asyncio.run(
            cap.compose_health(launcher_status="healthy", gateway_status="healthy", config_valid=True)
        )
        assert "T" in result.composition_timestamp

    def test_composition_is_read_only(self) -> None:
        cap = _make_composer()
        asyncio.run(
            cap.compose_health(launcher_status="healthy", gateway_status="healthy", config_valid=True)
        )
        result2 = asyncio.run(
            cap.compose_health(launcher_status="unhealthy", gateway_status="unhealthy", config_valid=False)
        )
        assert result2.overall_status == "unhealthy"

    def test_multiple_compositions_are_idempotent_same_inputs(self) -> None:
        cap = _make_composer()
        r1 = asyncio.run(
            cap.compose_health(launcher_status="healthy", gateway_status="healthy", config_valid=True)
        )
        r2 = asyncio.run(
            cap.compose_health(launcher_status="healthy", gateway_status="healthy", config_valid=True)
        )
        assert r1.overall_status == r2.overall_status


class TestProbeTimeout:
    """Test probe timeout degrades subsystem instead of stalling."""

    @patch.object(asyncio, "wait_for")
    def test_probe_timeout_makes_subsystem_timeout(self, mock_wait_for: AsyncMock) -> None:
        cap = _make_composer()
        mock_wait_for.side_effect = asyncio.TimeoutError("timeout")
        result = asyncio.run(
            cap.compose_health(launcher_status="healthy", gateway_status="healthy", config_valid=True)
        )
        gw_subs = [s for s in result.subsystems if s.name == "gateway"]
        assert len(gw_subs) == 1
        assert gw_subs[0].status == "timeout"


class TestStalenessIndicators:
    """Test staleness indicators when subsystems report unknown."""

    def test_unknown_launcher_has_staleness(self) -> None:
        cap = _make_composer()
        result = asyncio.run(
            cap.compose_health(launcher_status="unknown", gateway_status="healthy", config_valid=True)
        )
        assert "launcher" in result.staleness_indicators

    def test_unknown_gateway_has_staleness(self) -> None:
        cap = _make_composer()
        result = asyncio.run(
            cap.compose_health(launcher_status="healthy", gateway_status="unknown", config_valid=True)
        )
        assert "gateway" in result.staleness_indicators

    def test_all_healthy_no_staleness(self) -> None:
        cap = _make_composer()
        result = asyncio.run(
            cap.compose_health(launcher_status="healthy", gateway_status="healthy", config_valid=True)
        )
        assert len(result.staleness_indicators) == 0


class TestEdgeCases:
    """Test edge cases from FR-DIA-001."""

    def test_all_unknown_returns_degraded(self) -> None:
        cap = _make_composer()
        result = asyncio.run(
            cap.compose_health(
                launcher_status="unknown",
                gateway_status="unknown",
                config_valid=True,
                job_capacity_available=True,
            )
        )
        assert result.overall_status == "degraded"

    def test_mixed_statuses_derive_correctly(self) -> None:
        cap = _make_composer()
        result = asyncio.run(
            cap.compose_health(
                launcher_status="healthy",
                gateway_status="degraded",
                config_valid=True,
                job_capacity_available=True,
            )
        )
        assert result.overall_status == "degraded"

    def test_first_run_with_no_subsystems_initialized(self) -> None:
        cap = _make_composer()
        result = asyncio.run(
            cap.compose_health(
                launcher_status="unknown",
                gateway_status="unknown",
                config_valid=True,
                job_capacity_available=True,
            )
        )
        assert result.overall_status == "degraded"

    def test_timeout_status_is_unhealthy(self) -> None:
        cap = _make_composer()
        result = asyncio.run(
            cap.compose_health(
                launcher_status="timeout", gateway_status="healthy", config_valid=True
            )
        )
        assert result.overall_status == "unhealthy"
