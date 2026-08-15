from __future__ import annotations

import pytest

from modules.compositor.src.capabilities_compositor_executor import CompositorExecutor
from modules.compositor.src.root_compositor_container import create_compositor_feature


class FakeGateway:
    def __init__(self, result):
        self.result = result
        self.codes: list[str] = []

    async def execute_blender_code(self, code: str):
        self.codes.append(code)
        return self.result


@pytest.mark.asyncio
async def test_compositor_inspection_returns_typed_graph() -> None:
    gateway = FakeGateway(
        {
            "use_nodes": True,
            "nodes": [{"name": "RGB", "node_type": "CompositorNodeRGB", "inputs": [], "outputs": ["Color"]}],
            "links": [],
        }
    )

    result = await create_compositor_feature(gateway).inspect_nodes()

    assert result.use_nodes is True
    assert result.nodes[0].node_type == "CompositorNodeRGB"
    assert "__LIMIT__" not in gateway.codes[0]


@pytest.mark.asyncio
async def test_compositor_rejects_unlisted_node_type_before_gateway() -> None:
    gateway = FakeGateway({})

    with pytest.raises(ValueError, match="Unsupported compositor node type"):
        await CompositorExecutor(gateway).create_node("CompositorNodeCustom")

    assert gateway.codes == []


@pytest.mark.asyncio
async def test_compositor_mutation_returns_typed_result() -> None:
    gateway = FakeGateway({"changed": True, "node_name": "RGB", "use_nodes": True, "message": "created"})

    result = await create_compositor_feature(gateway).create_node("CompositorNodeRGB", "RGB")

    assert result.changed is True
    assert result.node_name == "RGB"
