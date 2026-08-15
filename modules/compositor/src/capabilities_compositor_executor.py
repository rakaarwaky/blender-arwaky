"""Compositor capability executor with explicit node and socket bounds."""

from __future__ import annotations

import json
from collections.abc import Mapping

from modules.shared.src.common.contract_wave_feature_protocol import IWaveFeatureProtocol
from modules.shared.src.compositor.taxonomy_compositor_vo import (
    CompositorGraphVO,
    CompositorLinkVO,
    CompositorMutationVO,
    CompositorNodeVO,
)

_ALLOWED_NODE_TYPES = {
    "CompositorNodeRGB",
    "CompositorNodeMixRGB",
    "CompositorNodeBlur",
    "CompositorNodeComposite",
    "CompositorNodeViewer",
}


class CompositorExecutor(IWaveFeatureProtocol):
    """Delegate compositor graph operations to the injected gateway."""

    def __init__(self, code_executor: object) -> None:
        self._code_executor = code_executor

    async def inspect_nodes(self, limit: int = 100) -> CompositorGraphVO:
        limit = self._bounded_limit(limit)
        code = """
import bpy
scene = bpy.context.scene
node_tree = scene.node_tree if scene.use_nodes and scene.node_tree else None
nodes = []
links = []
if node_tree:
    for node in list(node_tree.nodes)[:__LIMIT__]:
        nodes.append({"name": node.name, "node_type": node.bl_idname,
                      "inputs": [socket.name for socket in list(node.inputs)[:128]],
                      "outputs": [socket.name for socket in list(node.outputs)[:128]]})
    for link in list(node_tree.links)[:__LIMIT__]:
        links.append({"from_node": link.from_node.name, "from_socket": link.from_socket.name,
                      "to_node": link.to_node.name, "to_socket": link.to_socket.name})
result = {"use_nodes": bool(scene.use_nodes), "nodes": nodes, "links": links}
""".replace("__LIMIT__", str(limit))
        result = await self._execute(code)
        return CompositorGraphVO(
            use_nodes=bool(result.get("use_nodes", False)),
            nodes=tuple(
                CompositorNodeVO(
                    name=str(node.get("name", "")),
                    node_type=str(node.get("node_type", "")),
                    inputs=tuple(str(value) for value in node.get("inputs", [])),
                    outputs=tuple(str(value) for value in node.get("outputs", [])),
                )
                for node in result.get("nodes", [])
                if isinstance(node, Mapping)
            ),
            links=tuple(
                CompositorLinkVO(
                    from_node=str(link.get("from_node", "")),
                    from_socket=str(link.get("from_socket", "")),
                    to_node=str(link.get("to_node", "")),
                    to_socket=str(link.get("to_socket", "")),
                )
                for link in result.get("links", [])
                if isinstance(link, Mapping)
            ),
        )

    async def configure(self, use_nodes: bool) -> CompositorMutationVO:
        code = """
import bpy
scene = bpy.context.scene
changed = scene.use_nodes != __USE_NODES__
scene.use_nodes = __USE_NODES__
result = {"changed": changed, "use_nodes": scene.use_nodes, "message": "Compositor configuration updated"}
""".replace("__USE_NODES__", "True" if use_nodes else "False")
        result = await self._execute(code)
        return CompositorMutationVO(
            changed=bool(result.get("changed", False)),
            use_nodes=bool(result.get("use_nodes", use_nodes)),
            message=str(result.get("message", "")),
        )

    async def create_node(self, node_type: str, node_name: str | None = None) -> CompositorMutationVO:
        node_type = str(node_type)
        if node_type not in _ALLOWED_NODE_TYPES:
            raise ValueError(f"Unsupported compositor node type: {node_type}")
        code = """
import bpy
scene = bpy.context.scene
scene.use_nodes = True
node = scene.node_tree.nodes.new(__NODE_TYPE__)
if __NODE_NAME__:
    node.name = __NODE_NAME__
result = {"changed": True, "node_name": node.name, "use_nodes": scene.use_nodes,
          "message": "Compositor node created"}
""".replace("__NODE_TYPE__", json.dumps(node_type)).replace("__NODE_NAME__", json.dumps(node_name))
        result = await self._execute(code)
        return CompositorMutationVO(
            changed=bool(result.get("changed", True)),
            node_name=str(result.get("node_name")) if result.get("node_name") else None,
            use_nodes=bool(result.get("use_nodes", True)),
            message=str(result.get("message", "")),
        )

    async def set_link(self, from_node: str, from_socket: str, to_node: str, to_socket: str) -> CompositorMutationVO:
        code = """
import bpy
scene = bpy.context.scene
if not scene.use_nodes or scene.node_tree is None:
    raise ValueError("Compositor nodes are disabled")
source = scene.node_tree.nodes.get(__FROM_NODE__)
target = scene.node_tree.nodes.get(__TO_NODE__)
if source is None or target is None:
    raise ValueError("Compositor source or target node not found")
source_socket = source.outputs.get(__FROM_SOCKET__)
target_socket = target.inputs.get(__TO_SOCKET__)
if source_socket is None or target_socket is None:
    raise ValueError("Compositor source or target socket not found")
for link in scene.node_tree.links:
    if link.from_socket == source_socket and link.to_socket == target_socket:
        result = {"changed": False, "message": "Link already exists"}
        break
else:
    scene.node_tree.links.new(source_socket, target_socket)
    result = {"changed": True, "message": "Link created"}
"""
        for token, value in {
            "__FROM_NODE__": from_node,
            "__FROM_SOCKET__": from_socket,
            "__TO_NODE__": to_node,
            "__TO_SOCKET__": to_socket,
        }.items():
            code = code.replace(token, json.dumps(str(value)))
        result = await self._execute(code)
        return CompositorMutationVO(changed=bool(result.get("changed", False)), message=str(result.get("message", "")))

    async def _execute(self, code: str) -> Mapping[str, object]:
        result = await self._code_executor.execute_blender_code(code)
        if not isinstance(result, Mapping):
            raise RuntimeError("Gateway returned a non-object compositor result")
        return result

    @staticmethod
    def _bounded_limit(value: int) -> int:
        limit = int(value)
        if not 1 <= limit <= 1000:
            raise ValueError("limit must be between 1 and 1000")
        return limit
