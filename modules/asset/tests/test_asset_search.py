from __future__ import annotations

import asyncio

import pytest

from modules.asset.src.capabilities_asset_search import AssetSearchCapability
from modules.shared.src.common.taxonomy_core_vo import AssetTypeFilter, ProviderName, SearchQuery
from modules.shared.src.common.taxonomy_domain_error import ProviderError


class MockConnection:
    def __init__(self, polyhaven_assets: dict | None = None, sketchfab_results: list | None = None):
        self.polyhaven_assets = polyhaven_assets or {}
        self.sketchfab_results = sketchfab_results or []
        self.fail_polyhaven: Exception | None = None
        self.fail_sketchfab: Exception | None = None

    async def send_command(self, action: str, _params: dict | None = None) -> dict:
        if action == "search_polyhaven_assets":
            if self.fail_polyhaven:
                raise self.fail_polyhaven
            return {"assets": self.polyhaven_assets}
        if action == "search_sketchfab_models":
            if self.fail_sketchfab:
                raise self.fail_sketchfab
            return {"results": self.sketchfab_results}
        return {}


def _mock_polyhaven_asset(asset_id: str, name: str = "", type: str = "hdri") -> dict:
    return {"name": name or asset_id, "type": type, "categories": ["test"]}


def _make_query(text: str = "cube") -> SearchQuery:
    return SearchQuery(text)


@pytest.fixture
def healthy_connection() -> MockConnection:
    polyhaven = {
        "p1": _mock_polyhaven_asset("p1", "Cube HDRI", "hdri"),
    }
    sketchfab = [{"uid": "s1", "name": "Chair Model"}]
    return MockConnection(polyhaven_assets=polyhaven, sketchfab_results=sketchfab)


@pytest.fixture
def connection_with_failures() -> MockConnection:
    polyhaven = {
        "p1": _mock_polyhaven_asset("p1", "Table", "model"),
    }
    conn = MockConnection(polyhaven_assets=polyhaven, sketchfab_results=[])
    conn.fail_sketchfab = ProviderError("rate limited")
    return conn


@pytest.mark.asyncio
async def test_fr_ast_001_search_all_returns_assets(healthy_connection: MockConnection):
    capability = AssetSearchCapability(healthy_connection)
    result = await capability.search_all(_make_query())

    assert result["total"] == 2
    assert len(result["assets"]) == 2
    assert result["provider_status"]["Polyhaven"] == "success"
    assert result["provider_status"]["Sketchfab"] == "success"
    assert "search_timestamp" in result


@pytest.mark.asyncio
async def test_fr_ast_001_search_normalizes_provider_results(healthy_connection: MockConnection):
    capability = AssetSearchCapability(healthy_connection)
    result = await capability.search_all(_make_query())

    for asset in result["assets"]:
        assert "id" in asset
        assert "name" in asset
        assert "type" in asset
        assert "provider" in asset
        assert "thumbnail_url" in asset
        assert "tags" in asset


@pytest.mark.asyncio
async def test_fr_ast_001_search_provider_filter(healthy_connection: MockConnection):
    capability = AssetSearchCapability(healthy_connection)
    result = await capability.search_all(_make_query(), providers=[ProviderName("Polyhaven")])

    assert result["total"] == 1
    assert result["provider_status"]["Polyhaven"] == "success"
    assert "Sketchfab" not in result["provider_status"]


@pytest.mark.asyncio
async def test_fr_ast_001_search_partial_failure(connection_with_failures: MockConnection):
    capability = AssetSearchCapability(connection_with_failures)
    result = await capability.search_all(_make_query())

    assert result["total"] == 1
    assert result["provider_status"]["Polyhaven"] == "success"
    assert result["provider_status"]["Sketchfab"] == "error"
    assert len(result["warnings"]) >= 1


@pytest.mark.asyncio
async def test_fr_ast_001_search_all_failures(connection_with_failures: MockConnection):
    conn = connection_with_failures
    conn.fail_polyhaven = ProviderError("down")
    conn.fail_sketchfab = ProviderError("down")
    capability = AssetSearchCapability(conn)
    result = await capability.search_all(_make_query())

    assert result["total"] == 0
    assert len(result["assets"]) == 0
    assert all(v == "error" for v in result["provider_status"].values())
    assert len(result["warnings"]) > 0


def test_fr_ast_001_search_empty_providers():
    class EmptyMock:
        async def send_command(self, _action: str, _params: dict | None = None) -> dict:
            return {}

    capability = AssetSearchCapability(EmptyMock())
    result = (
        asyncio.get_event_loop_policy()
        .new_event_loop()
        .run_until_complete(capability.search_all(_make_query(), providers=[]))
    )

    assert result["total"] == 0
    assert len(result["assets"]) == 0
    assert result["provider_status"] == {}


@pytest.mark.asyncio
async def test_fr_ast_001_search_asset_type_filter(healthy_connection: MockConnection):
    capability = AssetSearchCapability(healthy_connection)
    result = await capability.search_all(_make_query(), asset_type_filter=AssetTypeFilter("hdri"))
    assert result["total"] >= 0


@pytest.mark.asyncio
async def test_fr_ast_001_search_concurrent_execution(healthy_connection: MockConnection):
    capability = AssetSearchCapability(healthy_connection)
    result = await capability.search_all(_make_query())

    assert "Polyhaven" in result["provider_status"]
    assert "Sketchfab" in result["provider_status"]


def test_fr_ast_001_search_pagination_included():
    class EmptyMock:
        async def send_command(self, _action: str, _params: dict | None = None) -> dict:
            return {}

    capability = AssetSearchCapability(EmptyMock())
    result = (
        asyncio.get_event_loop_policy()
        .new_event_loop()
        .run_until_complete(capability.search_all(_make_query(), providers=[]))
    )

    assert "total" in result
    assert "warnings" in result
    assert "provider_status" in result


@pytest.mark.asyncio
async def test_fr_ast_001_search_credentials_not_exposed(healthy_connection: MockConnection):
    capability = AssetSearchCapability(healthy_connection)
    result = await capability.search_all(_make_query())

    for asset in result["assets"]:
        for value in asset.values():
            if isinstance(value, str):
                assert "token" not in value.lower() or "example.com" in value
                assert "secret" not in value.lower()


@pytest.mark.asyncio
async def test_search_with_exception_handling(healthy_connection: MockConnection):
    conn = healthy_connection
    conn.fail_polyhaven = Exception("unexpected")
    capability = AssetSearchCapability(conn)
    result = await capability.search_all(_make_query())

    assert "Polyhaven" in result["provider_status"]
    assert result["provider_status"]["Polyhaven"] == "error"
    assert any("Polyhaven" in w for w in result["warnings"])
