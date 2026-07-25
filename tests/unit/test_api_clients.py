"""Unit tests for the infrastructure asset adapters."""
from unittest.mock import MagicMock

import pytest

from modules.render.infrastructure_polyhaven_adapter import PolyhavenAssetAdapter
from modules.render.infrastructure_sketchfab_adapter import SketchfabAssetAdapter
from taxonomy import (
    AssetDownloadRequestVO,
    AssetId,
    AssetSearchRequestVO,
    FilePath,
    ProviderError,
)


@pytest.mark.unit
class TestPolyhavenAssetAdapter:
    """Tests for PolyhavenAssetAdapter."""

    @pytest.fixture
    def mock_conn(self):
        return MagicMock()

    @pytest.fixture
    def adapter(self, mock_conn):
        return PolyhavenAssetAdapter(mock_conn)

    @pytest.mark.asyncio
    async def test_polyhaven_asset_adapter(self, adapter, mock_conn):
        # Search assets
        mock_conn.send_command.return_value = {
            "assets": {
                "wall": {"name": "Wall", "type": "textures", "categories": ["brick"]}
            }
        }
        res = await adapter.search_assets(AssetSearchRequestVO(query="brick", asset_type="textures", categories=["brick"]))
        assert len(res.assets) == 1
        assert res.assets[0].name == "Wall"

        # Search exception
        mock_conn.send_command.side_effect = Exception("API error")
        with pytest.raises(ProviderError):
            await adapter.search_assets(AssetSearchRequestVO(query="brick"))

        # Details success
        mock_conn.send_command.side_effect = None
        mock_conn.send_command.return_value = {"name": "Oak", "type": "textures", "tags": ["wood"]}
        details = await adapter.get_asset_details("oak")
        assert details is not None
        assert details.name == "Oak"

        # Details Blender error or exception
        mock_conn.send_command.return_value = {"error": "Not found"}
        assert await adapter.get_asset_details("oak") is None

        mock_conn.send_command.side_effect = Exception()
        assert await adapter.get_asset_details("oak") is None

        # Download success
        mock_conn.send_command.side_effect = None
        mock_conn.send_command.return_value = {"success": True, "path": "/path/to/asset"}
        download_res = await adapter.download_asset(AssetDownloadRequestVO(asset_id=AssetId("oak"), destination_path=FilePath("/path/to/asset")))
        assert download_res.success is True
        assert download_res.file_path == "/path/to/asset"

        # Download failure
        mock_conn.send_command.return_value = {"success": False, "message": "Failed"}
        with pytest.raises(ProviderError):
            await adapter.download_asset(AssetDownloadRequestVO(asset_id=AssetId("oak"), destination_path=FilePath("/path/to/asset")))

        # Download exception
        mock_conn.send_command.side_effect = Exception("IO failed")
        with pytest.raises(ProviderError):
            await adapter.download_asset(AssetDownloadRequestVO(asset_id=AssetId("oak"), destination_path=FilePath("/path/to/asset")))

    def test_uninitialized_polyhaven_adapter(self):
        adapter = PolyhavenAssetAdapter(None)  # type: ignore
        with pytest.raises(ProviderError):
            adapter._get_conn()


@pytest.mark.unit
class TestSketchfabAssetAdapter:
    """Tests for SketchfabAssetAdapter."""

    @pytest.fixture
    def mock_conn(self):
        return MagicMock()

    @pytest.fixture
    def adapter(self, mock_conn):
        return SketchfabAssetAdapter(mock_conn)

    @pytest.mark.asyncio
    async def test_sketchfab_asset_adapter(self, adapter, mock_conn):
        # Search
        mock_conn.send_command.return_value = {"results": [{"uid": "1", "name": "M1"}]}
        res = await adapter.search_assets(AssetSearchRequestVO(query="table"))
        assert len(res.assets) == 1
        assert res.assets[0].id == "1"

        # Search error
        mock_conn.send_command.side_effect = Exception()
        with pytest.raises(ProviderError):
            await adapter.search_assets(AssetSearchRequestVO(query="table"))

        # Details
        mock_conn.send_command.side_effect = None
        mock_conn.send_command.return_value = {"model_name": "M1"}
        details = await adapter.get_asset_details("1")
        assert details is not None
        assert details.name == "M1"

        mock_conn.send_command.return_value = {"error": "Forbidden"}
        assert await adapter.get_asset_details("1") is None

        mock_conn.send_command.side_effect = Exception()
        assert await adapter.get_asset_details("1") is None

        # Download success
        mock_conn.send_command.side_effect = None
        mock_conn.send_command.return_value = {"success": True, "imported_objects": ["o1"]}
        download_res = await adapter.download_asset(AssetDownloadRequestVO(asset_id=AssetId("1"), destination_path=FilePath("o1")))
        assert download_res.success is True
        assert download_res.file_path == "o1"

        # Download fail
        mock_conn.send_command.return_value = {"success": False, "message": "Failed"}
        with pytest.raises(ProviderError):
            await adapter.download_asset(AssetDownloadRequestVO(asset_id=AssetId("1"), destination_path=FilePath("o1")))

        # Download exception
        mock_conn.send_command.side_effect = Exception()
        with pytest.raises(ProviderError):
            await adapter.download_asset(AssetDownloadRequestVO(asset_id=AssetId("1"), destination_path=FilePath("o1")))
