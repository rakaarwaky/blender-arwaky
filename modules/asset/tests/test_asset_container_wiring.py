from __future__ import annotations

from modules.asset.src.root_asset_container import AssetContainer


class ConnectionStub:
    pass


def test_asset_container_wires_download_capability() -> None:
    container = AssetContainer(connection=ConnectionStub())

    orchestrator = container.get_orchestrator()

    assert orchestrator is not None
    assert orchestrator._download is not None
    assert orchestrator._download.config_aggregate is None
