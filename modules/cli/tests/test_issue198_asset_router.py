from __future__ import annotations

from modules.cli.src.capabilities_cli_action_router import CliActionRouter
from modules.shared.src.asset.taxonomy_asset_data_vo import AssetMetadata


class FakeAssetAggregate:
    async def search(self, query, providers=None):
        return [AssetMetadata(id="asset-1", name=str(query), type="model", provider="Polyhaven")]

    async def get_provider_metadata(self, provider, asset_id):
        return {"provider_metadata": {"provider": str(provider), "asset_id": str(asset_id)}}


def test_asset_search_is_routed_to_local_aggregate() -> None:
    router = CliActionRouter(object())
    router._asset = FakeAssetAggregate()

    result = router.execute_action("search_assets", {"query": "chair", "providers": ["Polyhaven"]})

    assert result["total"] == 1  # nosec B101
    assert result["assets"][0]["id"] == "asset-1"  # nosec B101
    assert result["assets"][0]["provider"] == "Polyhaven"  # nosec B101


def test_asset_metadata_is_routed_to_local_aggregate() -> None:
    router = CliActionRouter(object())
    router._asset = FakeAssetAggregate()

    result = router.execute_action("get_provider_metadata", {"provider": "Polyhaven", "asset_id": "chair"})

    assert result["provider_metadata"]["asset_id"] == "chair"  # nosec B101
