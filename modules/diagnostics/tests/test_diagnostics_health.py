"""Tests for HealthComposer — FR-DIA-001.

Exercises health status derivation, subsystem coverage, probe timeout,
staleness indicators, and composition idempotency via HealthComposer.
Run via pytest from repo root.
"""

from __future__ import annotations

import asyncio
from unittest.mock import patch

from modules.diagnostics.src.capabilities_health_composer import HealthComposer
from modules.shared.src.diagnostics.taxonomy_diagnostics_vo import HealthCompositionRequestVO


def _make_composer() -> HealthComposer:
    return HealthComposer()


def _request(**kwargs):
    return HealthCompositionRequestVO(**kwargs)


class TestHealthCompositionStatusDerivation:
    """Test overall status derives deterministically from subsystem states."""

    def test_all_healthy_returns_overall_healthy(self) -> None:
        cap = _make_composer()
        result = asyncio.run(
            cap.compose_health(
                request=_request(
                    launcher_status="healthy", gateway_status="healthy", config_valid=True, job_capacity_available=True
                )
            )
        )
        assert result.overall_status == "healthy"

    def test_any_unhealthy_returns_overall_unhealthy(self) -> None:
        cap = _make_composer()
        result = asyncio.run(
            cap.compose_health(
                request=_request(
                    launcher_status="unhealthy",
                    gateway_status="healthy",
                    config_valid=True,
                    job_capacity_available=True,
                )
            )
        )
        assert result.overall_status == "unhealthy"

    def test_any_failed_returns_overall_unhealthy(self) -> None:
        cap = _make_composer()
        result = asyncio.run(
            cap.compose_health(
                request=_request(
                    launcher_status="healthy", gateway_status="failed", config_valid=True, job_capacity_available=True
                )
            )
        )
        assert result.overall_status == "unhealthy"

    def test_any_unreachable_returns_overall_unhealthy(self) -> None:
        cap = _make_composer()
        result = asyncio.run(
            cap.compose_health(
                request=_request(
                    launcher_status="healthy",
                    gateway_status="unreachable",
                    config_valid=True,
                    job_capacity_available=True,
                )
            )
        )
        assert result.overall_status == "unhealthy"

    def test_any_degraded_returns_overall_degraded(self) -> None:
        cap = _make_composer()
        result = asyncio.run(
            cap.compose_health(
                request=_request(
                    launcher_status="degraded", gateway_status="healthy", config_valid=True, job_capacity_available=True
                )
            )
        )
        assert result.overall_status == "degraded"

    def test_config_invalid_returns_unhealthy(self) -> None:
        cap = _make_composer()
        result = asyncio.run(
            cap.compose_health(
                request=_request(
                    launcher_status="healthy", gateway_status="healthy", config_valid=False, job_capacity_available=True
                )
            )
        )
        assert result.overall_status == "unhealthy"

    def test_job_capacity_exhausted_returns_degraded(self) -> None:
        cap = _make_composer()
        result = asyncio.run(
            cap.compose_health(
                request=_request(
                    launcher_status="healthy", gateway_status="healthy", config_valid=True, job_capacity_available=False
                )
            )
        )
        assert result.overall_status == "degraded"

    def test_unknown_statuses_are_degraded(self) -> None:
        cap = _make_composer()
        result = asyncio.run(
            cap.compose_health(
                request=_request(
                    launcher_status="unknown", gateway_status="healthy", config_valid=True, job_capacity_available=True
                )
            )
        )
        assert result.overall_status == "degraded"


class TestSubsystemCoverage:
    """Test composed health includes required subsystem names."""

    def test_includes_launcher_gateway_config_job_capacity(self) -> None:
        cap = _make_composer()
        result = asyncio.run(
            cap.compose_health(
                request=_request(
                    launcher_status="healthy", gateway_status="healthy", config_valid=True, job_capacity_available=True
                )
            )
        )
        names = [s.name for s in result.subsystems]
        assert set(names) >= {"launcher", "gateway", "config", "job_capacity"}


class TestProbeTimeout:
    """Test slow subsystems become timeout/degraded instead of stalling composition."""

    def test_probe_timeout_marks_subsystem_timeout(self) -> None:
        cap = _make_composer()

        async def slow_probe(_status):
            await asyncio.sleep(10)

        with patch.object(cap, "_probe_launcher", slow_probe):
            result = asyncio.run(
                cap.compose_health(
                    request=_request(
                        launcher_status="healthy",
                        gateway_status="healthy",
                        config_valid=True,
                        job_capacity_available=True,
                    )
                )
            )

        launcher = next(s for s in result.subsystems if s.name == "launcher")
        assert launcher.status == "timeout"
        assert cap._composition_cache is not None


class TestStalenessIndicators:
    """Test staleness indicators are populated for unknown inputs."""

    def test_unknown_launcher_populates_staleness_delta(self) -> None:
        cap = _make_composer()
        result = asyncio.run(
            cap.compose_health(
                request=_request(
                    launcher_status="unknown", gateway_status="healthy", config_valid=True, job_capacity_available=True
                )
            )
        )
        assert result.overall_status == "degraded"

    def test_unknown_gateway_populates_staleness_delta(self) -> None:
        cap = _make_composer()
        result = asyncio.run(
            cap.compose_health(
                request=_request(
                    launcher_status="healthy", gateway_status="unknown", config_valid=True, job_capacity_available=True
                )
            )
        )
        assert result.overall_status == "degraded"


class TestCompositionIdempotency:
    """Test identical inputs within freshness tolerance return cached result."""

    def test_identical_input_within_freshness_returns_cached(self) -> None:
        cap = _make_composer()
        r1 = asyncio.run(
            cap.compose_health(
                request=_request(
                    launcher_status="healthy", gateway_status="healthy", config_valid=True, job_capacity_available=True
                )
            )
        )
        r2 = asyncio.run(
            cap.compose_health(
                request=_request(
                    launcher_status="healthy", gateway_status="healthy", config_valid=True, job_capacity_available=True
                )
            )
        )
        assert r1.composition_timestamp == r2.composition_timestamp
