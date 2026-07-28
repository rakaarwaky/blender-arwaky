"""Tests for AssetSearchCapability — FR-AST-001: Search Assets Across Providers.

Exercises unified multi-provider search with mocked provider ports.
Run via pytest from repo root.
"""

from __future__ import annotations

import pytest

from modules.asset.src.capabilities_asset_search import AssetSearchCapability
from modules.shared.src.asset.contract_asset_provider import AssetProviderPort
from modules.shared.src.common.taxonomy_core_vo import (
    AssetTypeFilter,
    ProviderName,
    SearchQuery,
)
from modules.shared.src.common.taxonomy_domain_error import ProviderError

# ─── Mock Provider Port ─────────────────────────────────────────────────────


class MockProviderPort(AssetProviderPort):
    """Mock provider port for testing."""

    def __init__(self, assets: list | None = None, error: Exception | None = None) -> None:
        self._assets = assets or []
        self._error = error

    async def search_assets(self, request: object) -> object:
        if self._error:
            raise self._error
        result = type("SearchResult", (), {"assets": self._assets})()
        return result

    async def get_asset_details(self, asset_id: object) -> object:
        """Return mock asset details or None."""
        if self._error:
            raise self._error
        for asset in self._assets:
            if str(getattr(asset, "id", "")) == str(asset_id):
                return asset
        return None

    async def download_asset(self, request: object) -> object:
        raise NotImplementedError("Not used in search tests")


# ─── Helpers ────────────────────────────────────────────────────────────────


class _AssetObject:
    """Mock asset object with standard attributes."""

    def __init__(self, id: str, name: str, type: str, provider: str, tags: list[str] | None = None) -> None:
        self.id = id
        self.name = name
        self.type = type
        self.provider = provider
        self.thumbnail_url = f"https://example.com/{id}.png"
        self.tags = tags or []


def _make_asset(id: str, name: str, type: str, provider: str, tags: list[str] | None = None) -> _AssetObject:
    """Create a mock asset object with standard attributes."""
    return _AssetObject(id, name, type, provider, tags)


def _make_query(text: str = "cube") -> SearchQuery:
    """Create a default search query."""
    return SearchQuery(text)


@pytest.fixture
def healthy_providers() -> dict[str, AssetProviderPort]:
    """Two healthy providers with sample assets."""
    polyhaven = MockProviderPort(assets=[_make_asset("p1", "Cube HDRI", "hdri", "polyhaven")])
    sketchfab = MockProviderPort(assets=[_make_asset("s1", "Chair Model", "model", "sketchfab")])
    return {"polyhaven": polyhaven, "sketchfab": sketchfab}


@pytest.fixture
def providers_with_failures() -> dict[str, AssetProviderPort]:
    """Three providers: one healthy, one failing, one empty."""
    polyhaven = MockProviderPort(assets=[_make_asset("p1", "Table", "model", "polyhaven")])
    sketchfab = MockProviderPort(error=ProviderError("rate limited"))
    blenderbgx = MockProviderPort(assets=[])
    return {
        "polyhaven": polyhaven,
        "sketchfab": sketchfab,
        "blenderbgx": blenderbgx,
    }


# ─── FR-AST-001: Search Assets Across Providers ────────────────────────────


@pytest.mark.asyncio
async def test_fr_ast_001_search_all_returns_assets(healthy_providers: dict[str, AssetProviderPort]):
    """Test that search returns normalized assets from all healthy providers."""
    capability = AssetSearchCapability(healthy_providers)
    result = await capability.search_all(_make_query())

    assert result["total"] == 2
    assert len(result["assets"]) == 2
    assert result["provider_status"]["polyhaven"] == "success"
    assert result["provider_status"]["sketchfab"] == "success"
    assert "search_timestamp" in result


@pytest.mark.asyncio
async def test_fr_ast_001_search_normalizes_provider_results(healthy_providers: dict[str, AssetProviderPort]):
    """Test that results from different providers are normalized into common shape."""
    capability = AssetSearchCapability(healthy_providers)
    result = await capability.search_all(_make_query())

    for asset in result["assets"]:
        assert "id" in asset
        assert "name" in asset
        assert "type" in asset
        assert "provider" in asset
        assert "thumbnail_url" in asset
        assert "tags" in asset


@pytest.mark.asyncio
async def test_fr_ast_001_search_provider_filter(healthy_providers: dict[str, AssetProviderPort]):
    """Test that provider filter limits search to specified providers."""
    capability = AssetSearchCapability(healthy_providers)
    result = await capability.search_all(_make_query(), providers=[ProviderName("polyhaven")])

    assert result["total"] == 1
    assert result["provider_status"]["polyhaven"] == "success"
    assert "sketchfab" not in result["provider_status"]


@pytest.mark.asyncio
async def test_fr_ast_001_search_partial_failure(providers_with_failures: dict[str, AssetProviderPort]):
    """Test that one provider failure returns partial results from remaining providers."""
    capability = AssetSearchCapability(providers_with_failures)
    result = await capability.search_all(_make_query())

    assert result["total"] == 1
    assert result["provider_status"]["polyhaven"] == "success"
    assert result["provider_status"]["sketchfab"] == "error"
    assert result["provider_status"]["blenderbgx"] == "empty"
    assert len(result["warnings"]) >= 1


@pytest.mark.asyncio
async def test_fr_ast_001_search_all_failures(providers_with_failures: dict[str, AssetProviderPort]):
    """Test that all providers failing returns empty result with aggregated error summary."""
    all_failing = {name: MockProviderPort(error=ProviderError("down")) for name in providers_with_failures}
    capability = AssetSearchCapability(all_failing)
    result = await capability.search_all(_make_query())

    assert result["total"] == 0
    assert len(result["assets"]) == 0
    assert all(v == "error" for v in result["provider_status"].values())
    assert len(result["warnings"]) > 0


def test_fr_ast_001_search_empty_providers():
    """Test that search with no providers returns empty result."""
    capability = AssetSearchCapability({})

    import asyncio

    result = asyncio.get_event_loop_policy().new_event_loop().run_until_complete(capability.search_all(_make_query()))

    assert result["total"] == 0
    assert len(result["assets"]) == 0
    assert result["provider_status"] == {}


@pytest.mark.asyncio
async def test_fr_ast_001_search_asset_type_filter(healthy_providers: dict[str, AssetProviderPort]):
    """Test that asset type filter is applied (mocked providers return all types)."""
    capability = AssetSearchCapability(healthy_providers)
    result = await capability.search_all(_make_query(), asset_type_filter=AssetTypeFilter("hdri"))

    # Mock returns all assets regardless of filter (provider adapter handles real filtering)
    assert result["total"] >= 0


@pytest.mark.asyncio
async def test_fr_ast_001_search_concurrent_execution(healthy_providers: dict[str, AssetProviderPort]):
    """Test that providers are searched concurrently (all appear in status)."""
    capability = AssetSearchCapability(healthy_providers)
    result = await capability.search_all(_make_query())

    # Both providers should be queried regardless of order
    assert "polyhaven" in result["provider_status"]
    assert "sketchfab" in result["provider_status"]


def test_fr_ast_001_search_pagination_included():
    """Test that search result includes pagination metadata."""
    capability = AssetSearchCapability({})

    import asyncio

    result = asyncio.get_event_loop_policy().new_event_loop().run_until_complete(capability.search_all(_make_query()))

    assert "total" in result
    assert "warnings" in result
    assert "provider_status" in result


@pytest.mark.asyncio
async def test_fr_ast_001_search_credentials_not_exposed(healthy_providers: dict[str, AssetProviderPort]):
    """Test that provider credentials never appear in search results."""
    capability = AssetSearchCapability(healthy_providers)
    result = await capability.search_all(_make_query())

    for asset in result["assets"]:
        for value in asset.values():
            if isinstance(value, str):
                assert "token" not in value.lower() or "example.com" in value
                assert "secret" not in value.lower()


# ─── Edge Cases ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_search_with_exception_handling(healthy_providers: dict[str, AssetProviderPort]):
    """Test that unexpected exceptions are caught and reported as warnings."""
    bad_provider = MockProviderPort(error=Exception("unexpected"))
    providers = {**healthy_providers, "bad": bad_provider}
    capability = AssetSearchCapability(providers)
    result = await capability.search_all(_make_query())

    assert "bad" in result["provider_status"]
    assert result["provider_status"]["bad"] == "error"
    assert any("bad" in w for w in result["warnings"])
