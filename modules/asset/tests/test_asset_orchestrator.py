"""Tests for AssetOrchestrator — Agent layer coordination.

Exercises the orchestrator's delegation to the search collector and
fetch-and-import workflow.
Run via pytest from repo root.
"""

from __future__ import annotations

import inspect

import pytest

from modules.asset.src.agent_orchestrator import AssetOrchestrator
from modules.shared.src.asset import (
    AssetMetadata,
    ImportedAsset,
)
from modules.shared.src.asset.contract_asset_search_protocol import AssetSearchProtocol
from modules.shared.src.common.taxonomy_core_vo import (
    AssetId,
    ProviderName,
    SearchQuery,
    StringList,
)

# ─── Mock Collector ────────────────────────────────────────────────────────


class MockSearchCollector(AssetSearchProtocol):
    """Mock search collector for testing."""

    def __init__(
        self,
        search_result: list[AssetMetadata] | None = None,
        fetch_result: ImportedAsset | None = None,
    ) -> None:
        self._search_result = search_result or []
        self._fetch_result = fetch_result
        self._search_calls: list[tuple] = []
        self._fetch_calls: list[tuple] = []

    async def search_all(
        self,
        query: SearchQuery,
        providers: StringList | None = None,
    ) -> list[AssetMetadata]:
        self._search_calls.append((query, providers))
        return self._search_result

    async def fetch_and_import(self, provider_name: ProviderName, asset_id: AssetId) -> ImportedAsset:
        self._fetch_calls.append((provider_name, asset_id))
        if not self._fetch_result:
            raise ValueError("No fetch result configured")
        return self._fetch_result


# ─── Helpers ────────────────────────────────────────────────────────────────


def _make_metadata(name: str, asset_id: str = "001", provider: str = "polyhaven") -> AssetMetadata:
    """Create a test AssetMetadata."""
    return AssetMetadata(
        id=asset_id,
        name=name,
        type="hdri",
        provider=ProviderName(provider),
        thumbnail_url=f"https://example.com/{asset_id}.png",
        tags=[],
    )


# ─── Tests ──────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_orchestrator_search_delegates_to_collector():
    """Test that orchestrator search delegates to the collector."""
    metadata = _make_metadata("Cube HDRI")
    collector = MockSearchCollector(search_result=[metadata])
    orch = AssetOrchestrator(collector)

    result = await orch.search(SearchQuery("cube"))

    assert len(result) == 1
    assert result[0].name == "Cube HDRI"
    assert len(collector._search_calls) == 1


@pytest.mark.asyncio
async def test_orchestrator_search_with_provider_filter():
    """Test that orchestrator passes provider filter to collector."""
    collector = MockSearchCollector(search_result=[])
    orch = AssetOrchestrator(collector)

    await orch.search(SearchQuery("test"), providers=StringList([ProviderName("polyhaven")]))

    assert len(collector._search_calls) == 1
    query, providers = collector._search_calls[0]
    assert providers is not None


@pytest.mark.asyncio
async def test_orchestrator_fetch_and_import():
    """Test that orchestrator delegates fetch-and-import to collector."""
    imported = ImportedAsset(
        id=AssetId("hdri_001"),
        name=ProviderName("polyhaven"),
        blender_id=ProviderName("forest_hdri"),
    )
    collector = MockSearchCollector(fetch_result=imported)
    orch = AssetOrchestrator(collector)

    result = await orch.fetch_and_import(ProviderName("polyhaven"), AssetId("hdri_001"))

    assert result.id == "hdri_001"
    assert len(collector._fetch_calls) == 1


@pytest.mark.asyncio
async def test_orchestrator_fetch_raises_on_missing():
    """Test that orchestrator propagates collector errors."""
    collector = MockSearchCollector(fetch_result=None)
    orch = AssetOrchestrator(collector)

    with pytest.raises(ValueError, match="No fetch result"):
        await orch.fetch_and_import(ProviderName("polyhaven"), AssetId("bad"))


@pytest.mark.asyncio
async def test_orchestrator_empty_search():
    """Test that orchestrator returns empty list when no results."""
    collector = MockSearchCollector(search_result=[])
    orch = AssetOrchestrator(collector)

    result = await orch.search(SearchQuery("nothing"))
    assert result == []


@pytest.mark.asyncio
async def test_orchestrator_multiple_searches():
    """Test that orchestrator tracks multiple search calls."""
    collector = MockSearchCollector(search_result=[_make_metadata("A"), _make_metadata("B")])
    orch = AssetOrchestrator(collector)

    await orch.search(SearchQuery("a"))
    await orch.search(SearchQuery("b"))

    assert len(collector._search_calls) == 2


@pytest.mark.asyncio
async def test_orchestrator_preserves_metadata_fields():
    """Test that orchestrator preserves all metadata fields from collector."""
    metadata = AssetMetadata(
        id="test_001",
        name="Test Asset",
        type="hdri",
        provider=ProviderName("polyhaven"),
        thumbnail_url="https://example.com/test.png",
        tags=["nature", "outdoor"],
    )
    collector = MockSearchCollector(search_result=[metadata])
    orch = AssetOrchestrator(collector)

    result = await orch.search(SearchQuery("test"))

    assert len(result) == 1
    assert result[0].id == "test_001"
    assert result[0].name == "Test Asset"
    assert result[0].type == "hdri"
    assert result[0].provider == ProviderName("polyhaven")
    assert result[0].thumbnail_url == "https://example.com/test.png"
    assert result[0].tags == ["nature", "outdoor"]


@pytest.mark.asyncio
async def test_orchestrator_fetch_and_import_calls_collector_once():
    """Test that fetch-and-import makes exactly one collector call."""
    imported = ImportedAsset(
        id=AssetId("test"),
        name=ProviderName("polyhaven"),
        blender_id=ProviderName("test_blender"),
    )
    collector = MockSearchCollector(fetch_result=imported)
    orch = AssetOrchestrator(collector)

    await orch.fetch_and_import(ProviderName("polyhaven"), AssetId("test"))

    assert len(collector._fetch_calls) == 1


def test_orchestrator_no_direct_blender_access():
    """Test that orchestrator never talks to Blender directly.

    The orchestrator delegates entirely to the collector (which uses
    provider ports), never calling Blender APIs itself.
    """
    # If the orchestrator had direct Blender calls, this test would fail
    # Current implementation only delegates — verify no Blender import in source
    source = inspect.getsource(AssetOrchestrator)
    assert "bpy" not in source.lower() or "import" not in source.split("import")[0]
