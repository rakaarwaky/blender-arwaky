from __future__ import annotations

import pytest

from modules.geometry_nodes.src.capabilities_geometry_nodes_executor import GeometryNodesExecutor
from modules.geometry_nodes.src.root_geometry_nodes_container import create_geometry_nodes_feature


class FakeGateway:
    def __init__(self, result):
        self.result = result
        self.codes: list[str] = []

    async def execute_blender_code(self, code: str):
        self.codes.append(code)
        return self.result


@pytest.mark.asyncio
async def test_geometry_nodes_inspection_returns_typed_group() -> None:
    gateway = FakeGateway(
        {
            "name": "Geometry",
            "node_count": 2,
            "links": [
                {
                    "from_node": "Group Input",
                    "from_socket": "Geometry",
                    "to_node": "Group Output",
                    "to_socket": "Geometry",
                }
            ],
            "sockets": [{"name": "Geometry", "socket_type": "NodeSocketGeometry", "is_output": True}],
        }
    )

    result = await create_geometry_nodes_feature(gateway).inspect_group("Geometry")

    assert result.name == "Geometry"
    assert result.node_count == 2
    assert result.links[0].from_node == "Group Input"
    assert '"Geometry"' in gateway.codes[0]


@pytest.mark.asyncio
async def test_geometry_nodes_group_mutation_delegates_through_gateway() -> None:
    gateway = FakeGateway(
        {
            "group_name": "Geometry",
            "changed": True,
            "object_name": "Cube",
            "modifier_name": "GeometryNodes",
            "message": "ready",
        }
    )

    result = await create_geometry_nodes_feature(gateway).create_group("Geometry", "Cube")

    assert result.group_name == "Geometry"
    assert result.changed is True
    assert len(gateway.codes) == 1


@pytest.mark.asyncio
async def test_geometry_nodes_gateway_result_must_be_an_object() -> None:
    gateway = FakeGateway(["invalid"])

    with pytest.raises(RuntimeError, match="non-object"):
        await GeometryNodesExecutor(gateway).inspect_group("Geometry")
