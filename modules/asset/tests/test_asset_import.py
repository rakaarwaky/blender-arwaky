"""Tests for AssetImportCapability — FR-AST-004: Import Asset into Blender.

Exercises import validation, gateway transport, format support, and
object reference handoff boundary.
Run via pytest from repo root.
"""

from __future__ import annotations

import os
import pathlib
from unittest.mock import AsyncMock, MagicMock

import pytest

from modules.asset.src.capabilities_asset_import import AssetImportCapability
from modules.shared.src.common.taxonomy_core_vo import AssetType, FilePath


# ─── Mock Gateway Client ───────────────────────────────────────────────────


class MockGatewayClient:
    """Mock gateway feature for Blender command transport."""

    def __init__(self, execute_result: dict | None = None) -> None:
        self._execute_result = execute_result or {
            "object_names": ["Cube", "Plane"],
            "asset_name": "test_asset",
            "license_summary": "CC0",
        }
        self._calls: list[dict] = []

    async def execute_command(self, command: dict) -> dict:
        self._calls.append(command)
        return self._execute_result


# ─── Helpers ────────────────────────────────────────────────────────────────


def _create_test_file(tmp_path: pathlib.Path, name: str = "test.glb", content: bytes = b"fake glb") -> str:
    """Create a test file."""
    path = tmp_path / name
    path.write_bytes(content)
    return str(path)


# ─── Fixtures ───────────────────────────────────────────────────────────────


@pytest.fixture
def gateway_with_success() -> MockGatewayClient:
    """Gateway client that returns success."""
    return MockGatewayClient(execute_result={
        "object_names": ["ImportedModel"],
        "asset_name": "test_asset",
        "license_summary": "CC-BY 4.0",
    })


@pytest.fixture
def gateway_with_failure() -> MockGatewayClient:
    """Gateway client that raises on execute."""
    gw = MockGatewayClient()
    async def fail(command: dict) -> dict:
        raise Exception("Blender import failed")
    gw.execute_command = fail
    return gw


# ─── FR-AST-004: Import Asset into Blender ─────────────────────────────────


def test_fr_ast_004_import_success(gateway_with_success: MockGatewayClient, tmp_path: pathlib.Path):
    """Test that successful import returns object references."""
    cap = AssetImportCapability(gateway_client=gateway_with_success)
    file_path = _create_test_file(tmp_path, "model.glb")

    result = cap.import_asset(
        file_path=FilePath(file_path),
        asset_type=AssetType("model"),
    )

    assert result["success"] is True
    assert len(result["object_names"]) == 1
    assert result["object_names"][0] == "ImportedModel"
    assert result["asset_name"] == "test_asset"


def test_fr_ast_004_import_missing_file():
    """Test that import fails when local file is missing with download guidance."""
    cap = AssetImportCapability()

    result = cap.import_asset(
        file_path=FilePath("/nonexistent/file.glb"),
        asset_type=AssetType("model"),
    )

    assert result["success"] is False
    assert result.get("error") == "missing_local_file"
    assert "download operation" in result["message"].lower()


def test_fr_ast_004_import_empty_file(tmp_path: pathlib.Path):
    """Test that import fails when file is empty."""
    cap = AssetImportCapability()
    empty_file = _create_test_file(tmp_path, "empty.glb", content=b"")

    result = cap.import_asset(
        file_path=FilePath(empty_file),
        asset_type=AssetType("model"),
    )

    assert result["success"] is False
    assert result.get("error") == "empty_file"


def test_fr_ast_004_unsupported_format(tmp_path: pathlib.Path):
    """Test that unsupported format returns validation error."""
    cap = AssetImportCapability()
    file_path = _create_test_file(tmp_path, "weird.xyz", b"data")

    result = cap.import_asset(
        file_path=FilePath(file_path),
        asset_type=AssetType("model"),
    )

    # .xyz is not a supported format for model import
    assert result["success"] is False
    assert result.get("error") == "unsupported_format"


def test_fr_ast_004_blender_import_failure(gateway_with_failure: MockGatewayClient, tmp_path: pathlib.Path):
    """Test that Blender-side import failure is distinguished from download failure."""
    cap = AssetImportCapability(gateway_client=gateway_with_failure)
    file_path = _create_test_file(tmp_path, "model.glb")

    result = cap.import_asset(
        file_path=FilePath(file_path),
        asset_type=AssetType("model"),
    )

    assert result["success"] is False
    assert result.get("error") is not None
    # Should NOT contain download-related error
    assert "download" not in result.get("message", "").lower() or "blender" in result.get("message", "").lower()


def test_fr_ast_004_target_collection(gateway_with_success: MockGatewayClient, tmp_path: pathlib.Path):
    """Test that target collection is passed through import command."""
    cap = AssetImportCapability(gateway_client=gateway_with_success)
    file_path = _create_test_file(tmp_path, "model.glb")

    result = cap.import_asset(
        file_path=FilePath(file_path),
        asset_type=AssetType("model"),
        target_collection="MyCollection",
    )

    assert result["success"] is True
    assert len(gateway_with_success._calls) == 1
    assert gateway_with_success._calls[0].get("target_collection") == "MyCollection"


def test_fr_ast_004_scale_normalization(gateway_with_success: MockGatewayClient, tmp_path: pathlib.Path):
    """Test that scale normalization policy is applied."""
    cap = AssetImportCapability(gateway_client=gateway_with_success)
    file_path = _create_test_file(tmp_path, "model.glb")

    result = cap.import_asset(
        file_path=FilePath(file_path),
        asset_type=AssetType("model"),
        scale_normalization=True,
    )

    assert result["success"] is True
    assert gateway_with_success._calls[0].get("scale_normalization") is True


def test_fr_ast_004_duplicate_policy(gateway_with_success: MockGatewayClient, tmp_path: pathlib.Path):
    """Test that duplicate handling policy is passed through."""
    cap = AssetImportCapability(gateway_client=gateway_with_success)
    file_path = _create_test_file(tmp_path, "model.glb")

    result = cap.import_asset(
        file_path=FilePath(file_path),
        asset_type=AssetType("model"),
        duplicate_policy="reject",
    )

    assert result["success"] is True
    assert gateway_with_success._calls[0].get("duplicate_policy") == "reject"


def test_fr_ast_004_format_hint(gateway_with_success: MockGatewayClient, tmp_path: pathlib.Path):
    """Test that format hint overrides default format detection."""
    cap = AssetImportCapability(gateway_client=gateway_with_success)
    file_path = _create_test_file(tmp_path, "model.custom", b"data")

    result = cap.import_asset(
        file_path=FilePath(file_path),
        asset_type=AssetType("model"),
        format_hint="glTF",
    )

    # With format hint, unsupported extension is accepted
    assert result["success"] is True


def test_fr_ast_004_license_preserved(gateway_with_success: MockGatewayClient, tmp_path: pathlib.Path):
    """Test that license and attribution metadata are preserved."""
    cap = AssetImportCapability(gateway_client=gateway_with_success)
    file_path = _create_test_file(tmp_path, "model.glb")

    result = cap.import_asset(
        file_path=FilePath(file_path),
        asset_type=AssetType("model"),
    )

    assert result["success"] is True
    assert result.get("license_summary") == "CC-BY 4.0"


def test_fr_ast_004_import_handoff_boundary():
    """Test that import capability ends at object reference handoff.

    FR-AST-004: After import, object manipulation is responsibility of
    object feature. Import should return object names, not manipulate them.
    """
    cap = AssetImportCapability()

    # Even without gateway, result structure should not include manipulation keys
    result = cap.import_asset(
        file_path=FilePath("/nonexistent.glb"),
        asset_type=AssetType("model"),
    )

    # Should have object_names (handoff), not manipulation results
    assert "object_names" in result
    assert "position" not in result  # no manipulation
    assert "material" not in result  # no manipulation


def test_fr_ast_004_supported_formats():
    """Test that supported formats are correctly identified."""
    cap = AssetImportCapability()

    # Model formats
    for ext in [".glb", ".gltf", ".fbx", ".obj"]:
        assert cap._is_supported_format(f"/tmp/model{ext}", AssetType("model"), None) is True

    # Texture formats
    for ext in [".png", ".jpg", ".exr"]:
        assert cap._is_supported_format(f"/tmp/texture{ext}", AssetType("texture"), None) is True

    # HDRI formats
    for ext in [".hdr", ".exr"]:
        assert cap._is_supported_format(f"/tmp/hdr{ext}", AssetType("hdri"), None) is True


def test_fr_ast_004_import_command_structure(gateway_with_success: MockGatewayClient, tmp_path: pathlib.Path):
    """Test that the import command built for gateway has correct structure."""
    cap = AssetImportCapability(gateway_client=gateway_with_success)
    file_path = _create_test_file(tmp_path, "model.glb")

    result = cap.import_asset(
        file_path=FilePath(file_path),
        asset_type=AssetType("model"),
        duplicate_policy="replace",
    )

    command = gateway_with_success._calls[0]
    assert command["type"] == "import"
    assert command["asset_type"] == "model"
    assert command["duplicate_policy"] == "replace"
