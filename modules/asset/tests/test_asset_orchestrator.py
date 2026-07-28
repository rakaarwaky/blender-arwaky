from __future__ import annotations

from typing import Any

import pytest

from modules.asset.src.agent_asset_orchestrator import AssetOrchestrator
from modules.shared.src.asset.contract_asset_search_protocol import AssetSearchProtocol
from modules.shared.src.common.taxonomy_core_vo import (
    ProviderName,
    SearchQuery,
)


class MockSearchCollector(AssetSearchProtocol):
    def __init__(self) -> None:
        self._search_calls: list[tuple] = []

    async def search_all(
        self,
        query: SearchQuery,
        providers: list[ProviderName] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        self._search_calls.append((query, providers))
        return {
            "assets": [
                {"id": "001", "name": "Cube HDRI", "type": "hdri", "provider": "polyhaven", "thumbnail_url": None, "tags": []},
            ],
            "provider_status": {"polyhaven": "success"},
            "total": 1,
            "warnings": [],
        }


def test_orchestrator_implements_aggregate():
    from modules.shared.src.asset.contract_asset_aggregate import IAssetAggregate
    assert isinstance(AssetOrchestrator.__mro__[1], type) and issubclass(AssetOrchestrator, IAssetAggregate)


@pytest.mark.asyncio
async def test_orchestrator_search_delegates():
    collector = MockSearchCollector()
    orch = AssetOrchestrator(search_capability=collector)
    result = await orch.search(SearchQuery("cube"))
    assert len(result) == 1
    assert result[0].name == "Cube HDRI"
    assert len(collector._search_calls) == 1


@pytest.mark.asyncio
async def test_orchestrator_search_empty():
    class EmptyCollector(AssetSearchProtocol):
        async def search_all(self, query: SearchQuery, providers: list[ProviderName] | None = None, **kwargs: Any) -> dict[str, Any]:
            return {"assets": [], "provider_status": {}, "total": 0, "warnings": []}

    orch = AssetOrchestrator(search_capability=EmptyCollector())
    result = await orch.search(SearchQuery("nothing"))
    assert result == []


@pytest.mark.asyncio
async def test_orchestrator_no_direct_blender_access():
    import inspect
    source = inspect.getsource(AssetOrchestrator)
    assert "bpy" not in source.lower()
