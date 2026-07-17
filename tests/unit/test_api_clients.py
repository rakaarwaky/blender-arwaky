"""Unit tests for the infrastructure API clients and their adapters."""
import json
import pytest
from unittest.mock import MagicMock, patch, mock_open

from taxonomy import (
    AssetId,
    AssetType,
    StatusString,
    Prompt,
    ResultUrl,
    ObjectName,
    JobId,
    ProviderError,
    AssetSearchRequestVO,
    AssetDownloadRequestVO,
    StringList,
    Vector3D,
    FilePath,
)
from infrastructure.polyhaven_api_client import PolyhavenApiClient
from infrastructure.polyhaven_asset_adapter import PolyhavenAssetAdapter
from infrastructure.sketchfab_api_client import SketchfabApiClient
from infrastructure.sketchfab_asset_adapter import SketchfabAssetAdapter


@pytest.mark.unit
class TestPolyhavenIntegration:
    """Tests for PolyhavenApiClient and PolyhavenAssetAdapter."""

    @pytest.fixture
    def mock_conn(self):
        return MagicMock()

    @pytest.fixture
    def client(self, mock_conn):
        return PolyhavenApiClient(mock_conn)

    @pytest.fixture
    def adapter(self, mock_conn):
        return PolyhavenAssetAdapter(mock_conn)

    def test_get_polyhaven_categories(self, client, mock_conn):
        # Success formatting sorted
        mock_conn.send_command.return_value = {
            "categories": {"nature": 10, "urban": 25, "indoor": 5}
        }
        res = client.get_polyhaven_categories(AssetType("textures"))
        assert "urban: 25 assets" in str(res)
        assert "nature: 10 assets" in str(res)
        assert "indoor: 5 assets" in str(res)

        # Error path
        mock_conn.send_command.return_value = {"error": "Timeout"}
        assert "Error: Timeout" in str(client.get_polyhaven_categories())

        # Exception path
        mock_conn.send_command.side_effect = Exception("General error")
        assert "General error" in str(client.get_polyhaven_categories())

    def test_search_polyhaven_assets(self, client, mock_conn):
        mock_conn.send_command.return_value = {
            "assets": {
                "brick_wall": {"name": "Brick Wall", "type": 1, "categories": ["brick"], "download_count": 100}
            },
            "total_count": 1,
            "returned_count": 1,
        }
        res = client.search_polyhaven_assets(AssetType("textures"), "brick")
        assert "Brick Wall" in str(res)
        assert "Downloads: 100" in str(res)

        # Error path
        mock_conn.send_command.return_value = {"error": "Fail"}
        assert "Error: Fail" in str(client.search_polyhaven_assets())

        # Exception path
        mock_conn.send_command.side_effect = Exception("API down")
        assert "API down" in str(client.search_polyhaven_assets())

    def test_download_polyhaven_asset(self, client, mock_conn):
        # HDRIs success path
        mock_conn.send_command.return_value = {"success": True, "message": "Imported"}
        res = client.download_polyhaven_asset(AssetId("sun"), AssetType("hdris"))
        assert "world environment" in str(res)

        # Textures success path
        mock_conn.send_command.return_value = {"success": True, "message": "Imported", "material": "wood", "maps": ["diffuse", "normal"]}
        res = client.download_polyhaven_asset(AssetId("wood"), AssetType("textures"))
        assert "Created material 'wood'" in str(res)

        # Models success path
        mock_conn.send_command.return_value = {"success": True, "message": "Imported"}
        res = client.download_polyhaven_asset(AssetId("chair"), AssetType("models"))
        assert "current scene" in str(res)

        # Failed path
        mock_conn.send_command.return_value = {"success": False, "message": "Disk full"}
        res = client.download_polyhaven_asset(AssetId("chair"), AssetType("models"))
        assert "Disk full" in str(res)

        # Exception path
        mock_conn.send_command.side_effect = Exception("Downloader crash")
        res = client.download_polyhaven_asset(AssetId("chair"), AssetType("models"))
        assert "Downloader crash" in str(res)

    def test_set_texture(self, client, mock_conn):
        # Success path with texture nodes
        mock_conn.send_command.return_value = {
            "success": True,
            "material": "mat_1",
            "maps": ["diffuse"],
            "material_info": {
                "node_count": 5,
                "has_nodes": True,
                "texture_nodes": [{"name": "diff_node", "image": "diff.png", "connections": ["Color -> Base Color"]}],
            }
        }
        res = client.set_texture(ObjectName("Cube"), AssetId("tex_1"))
        assert "mat_1" in str(res)
        assert "diff_node" in str(res)
        assert "Color -> Base Color" in str(res)

        # Success path without texture nodes
        mock_conn.send_command.return_value = {
            "success": True,
            "material": "mat_1",
            "maps": [],
            "material_info": {"node_count": 1, "has_nodes": False, "texture_nodes": []}
        }
        res = client.set_texture(ObjectName("Cube"), AssetId("tex_1"))
        assert "No texture nodes found" in str(res)

        # Failure status
        mock_conn.send_command.return_value = {"success": False, "message": "Not mesh"}
        res = client.set_texture(ObjectName("Cube"), AssetId("tex_1"))
        assert "Not mesh" in str(res)

        # Error
        mock_conn.send_command.return_value = {"error": "Invalid obj"}
        res = client.set_texture(ObjectName("Cube"), AssetId("tex_1"))
        assert "Error: Invalid obj" in str(res)

        # Exception
        mock_conn.send_command.side_effect = Exception("Socket reset")
        res = client.set_texture(ObjectName("Cube"), AssetId("tex_1"))
        assert "Socket reset" in str(res)

    def test_get_polyhaven_status(self, client, mock_conn):
        mock_conn.send_command.return_value = {"enabled": True, "message": "Ready. "}
        assert "textures than Sketchfab" in str(client.get_polyhaven_status())

        mock_conn.send_command.side_effect = Exception()
        assert "Error" in str(client.get_polyhaven_status())

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
class TestSketchfabIntegration:
    """Tests for SketchfabApiClient and SketchfabAssetAdapter."""

    @pytest.fixture
    def mock_conn(self):
        return MagicMock()

    @pytest.fixture
    def client(self, mock_conn):
        return SketchfabApiClient(mock_conn)

    @pytest.fixture
    def adapter(self, mock_conn):
        return SketchfabAssetAdapter(mock_conn)

    def test_get_sketchfab_status(self, client, mock_conn):
        mock_conn.send_command.return_value = {"enabled": True, "message": "Sketchfab active. "}
        assert "Sketchfab active" in str(client.get_sketchfab_status())

        mock_conn.send_command.return_value = {"enabled": False, "message": ""}
        assert "not enabled" in str(client.get_sketchfab_status())

        mock_conn.send_command.side_effect = Exception("Conn loss")
        assert "Conn loss" in str(client.get_sketchfab_status())

    def test_search_sketchfab_models(self, client, mock_conn):
        # Valid search with results
        mock_conn.send_command.return_value = {
            "results": [
                {
                    "name": "Knight",
                    "uid": "uid_123",
                    "user": {"username": "arthur"},
                    "license": {"label": "CC-BY"},
                    "faceCount": 5000,
                    "isDownloadable": True,
                },
                None,  # Null item safety check
            ]
        }
        res = client.search_sketchfab_models("knight")
        assert "Knight" in str(res)
        assert "Author: arthur" in str(res)
        assert "License: CC-BY" in str(res)

        # Empty search results
        mock_conn.send_command.return_value = {"results": []}
        assert "No model_domain_entity_model found" in str(client.search_sketchfab_models("knight"))

        # None result safety
        mock_conn.send_command.return_value = None
        assert "no response" in str(client.search_sketchfab_models("knight"))

        # Blender error
        mock_conn.send_command.return_value = {"error": "Rate limit"}
        assert "Error: Rate limit" in str(client.search_sketchfab_models("knight"))

        # Exception
        mock_conn.send_command.side_effect = Exception("Search fails")
        assert "Search fails" in str(client.search_sketchfab_models("knight"))

    def test_get_sketchfab_model_preview(self, client, mock_conn):
        mock_conn.send_command.return_value = {
            "image_data": "aW1hZ2VfYnl0ZXNfaGVyZQ==",
            "model_name": "Chair",
            "author": "john",
        }
        res = client.get_sketchfab_model_preview(AssetId("chair"))
        assert res == b"image_bytes_here"

        # None result
        mock_conn.send_command.return_value = None
        with pytest.raises(ProviderError):
            client.get_sketchfab_model_preview(AssetId("chair"))

        # Error
        mock_conn.send_command.return_value = {"error": "Private model"}
        with pytest.raises(ProviderError):
            client.get_sketchfab_model_preview(AssetId("chair"))

        # Exception
        mock_conn.send_command.side_effect = Exception()
        with pytest.raises(Exception):
            client.get_sketchfab_model_preview(AssetId("chair"))

    def test_download_sketchfab_model(self, client, mock_conn):
        mock_conn.send_command.return_value = {
            "success": True,
            "imported_objects": ["chair_1"],
            "dimensions": [1.0, 1.0, 2.0],
            "world_bounding_box": [0.0, 2.0],
            "normalized": True,
            "scale_applied": 0.5,
        }
        res = client.download_sketchfab_model(AssetId("uid"), 2.0)
        assert "chair_1" in str(res)
        assert "1.000 x 1.000 x 2.000" in str(res)
        assert "scale factor 0.500000" in str(res)

        # Failed download
        mock_conn.send_command.return_value = {"success": False, "message": "Access denied"}
        res = client.download_sketchfab_model(AssetId("uid"), 2.0)
        assert "Access denied" in str(res)

        # None result
        mock_conn.send_command.return_value = None
        res = client.download_sketchfab_model(AssetId("uid"), 2.0)
        assert "no response" in str(res)

        # Error
        mock_conn.send_command.return_value = {"error": "API Key invalid"}
        res = client.download_sketchfab_model(AssetId("uid"), 2.0)
        assert "Error: API Key invalid" in str(res)

        # Exception
        mock_conn.send_command.side_effect = Exception("Network down")
        res = client.download_sketchfab_model(AssetId("uid"), 2.0)
        assert "Network down" in str(res)

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
