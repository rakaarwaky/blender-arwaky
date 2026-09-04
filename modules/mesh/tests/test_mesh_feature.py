from __future__ import annotations

import pytest

from modules.mesh.src.capabilities_mesh_executor import MeshExecutor
from modules.mesh.src.root_mesh_container import create_mesh_feature


class FakeGateway:
    def __init__(self, result):
        self.result = result
        self.codes: list[str] = []

    async def execute_blender_code(self, code: str):
        self.codes.append(code)
        return self.result


@pytest.mark.asyncio
async def test_mesh_statistics_returns_typed_summary() -> None:
    gateway = FakeGateway(
        {
            "object_name": "Cube",
            "vertex_count": 8,
            "edge_count": 12,
            "polygon_count": 6,
            "uv_layer_count": 1,
            "has_custom_normals": False,
        }
    )

    result = await create_mesh_feature(gateway).get_statistics("Cube")

    assert result.object_name == "Cube"
    assert result.vertex_count == 8
    assert result.uv_layer_count == 1
    assert '"Cube"' in gateway.codes[0]


@pytest.mark.asyncio
async def test_mesh_rejects_unknown_edit_operation_before_gateway() -> None:
    gateway = FakeGateway({})

    with pytest.raises(ValueError, match="Unsupported mesh operation"):
        await MeshExecutor(gateway).edit("Cube", "bevel_everything")

    assert gateway.codes == []


@pytest.mark.asyncio
async def test_mesh_validation_converts_findings() -> None:
    gateway = FakeGateway(
        {
            "object_name": "Cube",
            "valid": False,
            "findings": [{"category": "loose_vertices", "count": 2, "examples": [3, 5]}],
        }
    )

    result = await create_mesh_feature(gateway).validate("Cube")

    assert result.valid is False
    assert result.findings[0].category == "loose_vertices"
    assert result.findings[0].examples == (3, 5)


@pytest.mark.asyncio
async def test_mesh_uv_layer_returns_typed_mutation() -> None:
    gateway = FakeGateway(
        {
            "object_name": "Cube",
            "operation": "ensure_mesh_uv_layer",
            "changed": True,
            "uv_layer_name": "UVMap",
            "message": "ready",
        }
    )

    result = await create_mesh_feature(gateway).ensure_uv_layer("Cube", "UVMap")

    assert result.changed is True
    assert result.uv_layer_name == "UVMap"
