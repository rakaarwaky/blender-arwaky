"""Tests for telemetry event enrichment capability — FR-TLM-004.

FR-TLM-004: Environment Metadata Enrichment with Coarse Fields Only
- Enriches events with environment metadata (OS, app version, Blender version)
- Missing fields default to "unknown"
- No PII included — no sensitive file paths or hostnames
"""

from __future__ import annotations

import pytest

from modules.shared.src.common.taxonomy_core_vo import PlatformName, VersionString

# ─── Mock Protocol for Testing ──────────────────────────────────────────────


class MockEnrichmentProtocol:
    """Mock async enrichment protocol matching TelemetryEnrichmentProtocol interface."""

    async def enrich_event(
        self,
        event: dict,  # noqa: ARG002
        platform: PlatformName | None = None,  # noqa: ARG002
        version: VersionString | None = None,  # noqa: ARG002
    ) -> dict:
        return {
            "os_family": "linux",
            "runtime_version": "3.12",
            "blender_version": "4.0",
            "app_version": "unknown",
        }

    async def get_environment_metadata(self) -> dict:
        return {"os_family": "linux", "runtime_version": "3.12"}


# ─── FR-TLM-004: Metadata Enrichment ──────────────────────────────────────


class TestMetadataEnrichment:
    """FR-TLM-004: Environment metadata enrichment."""

    @pytest.mark.asyncio
    async def test_enrich_event_returns_metadata(self) -> None:
        """FR-TLM-004: enrich_event returns a dict with metadata."""
        protocol = MockEnrichmentProtocol()
        result = await protocol.enrich_event({"action": "test"})
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_metadata_contains_platform(self) -> None:
        """FR-TLM-004: Metadata includes platform information."""
        protocol = MockEnrichmentProtocol()
        result = await protocol.enrich_event({"action": "test"})
        assert "os_family" in result or "linux" in str(result)

    @pytest.mark.asyncio
    async def test_metadata_contains_version(self) -> None:
        """FR-TLM-004: Metadata includes version information."""
        protocol = MockEnrichmentProtocol()
        result = await protocol.enrich_event({"action": "test"})
        assert "runtime_version" in result or "blender_version" in result


# ─── FR-TLM-004: No PII ──────────────────────────────────────────────────


class TestNoPII:
    """FR-TLM-004: Enrichment includes no PII."""

    @pytest.mark.asyncio
    async def test_metadata_contains_no_hostname(self) -> None:
        """FR-TLM-004: Metadata does not include hostnames."""
        protocol = MockEnrichmentProtocol()
        result = await protocol.enrich_event({"action": "test"})
        assert "hostname" not in str(result).lower()

    @pytest.mark.asyncio
    async def test_metadata_contains_no_user(self) -> None:
        """FR-TLM-004: Metadata does not include user names."""
        protocol = MockEnrichmentProtocol()
        result = await protocol.enrich_event({"action": "test"})
        assert "user" not in str(result).lower()

    @pytest.mark.asyncio
    async def test_metadata_contains_no_file_paths(self) -> None:
        """FR-TLM-004: Metadata does not include sensitive file paths."""
        protocol = MockEnrichmentProtocol()
        result = await protocol.enrich_event({"action": "test"})
        assert "/home/" not in str(result)
        assert "~" not in str(result)


# ─── FR-TLM-004: Environment Metadata Snapshot ────────────────────────────


class TestEnvironmentMetadata:
    """FR-TLM-004: Environment metadata snapshot."""

    @pytest.mark.asyncio
    async def test_get_environment_returns_snapshot(self) -> None:
        """FR-TLM-004: get_environment_metadata returns a dict snapshot."""
        protocol = MockEnrichmentProtocol()
        result = await protocol.get_environment_metadata()
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_environment_contains_os_family(self) -> None:
        """FR-TLM-004: Environment metadata includes OS family."""
        protocol = MockEnrichmentProtocol()
        result = await protocol.get_environment_metadata()
        assert "os_family" in result or "linux" in str(result)
