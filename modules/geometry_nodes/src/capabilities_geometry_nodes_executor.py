"""Geometry Nodes capability executor.

The executor builds bounded Blender commands and delegates transport to the
injected gateway/code executor. It never opens sockets or registers MCP tools.
"""

from __future__ import annotations

import json
from collections.abc import Mapping

from modules.shared.src.geometry_nodes.taxonomy_geometry_nodes_vo import (
    GeometryNodeGroupVO,
    GeometryNodeLinkVO,
    GeometryNodeMutationVO,
    GeometryNodeSocketVO,
)


class GeometryNodesExecutor:
    """Execute contract-level Geometry Nodes operations through one gateway."""

    def __init__(self, code_executor: object) -> None:
        self._code_executor = code_executor

    async def inspect_group(self, group_name: str) -> GeometryNodeGroupVO:
        code = """
import bpy
name = __GROUP_NAME__
group = bpy.data.node_groups.get(name)
if group is None:
    raise ValueError(f"Geometry Nodes group not found: {name}")
links = []
for link in list(group.links)[:256]:
    links.append({"from_node": link.from_node.name, "from_socket": link.from_socket.name,
                  "to_node": link.to_node.name, "to_socket": link.to_socket.name})
sockets = []
interface = getattr(group, "interface", None)
if interface is not None and hasattr(interface, "items_tree"):
    for item in list(interface.items_tree)[:256]:
        if hasattr(item, "socket_type"):
            sockets.append({"name": item.name, "socket_type": item.socket_type,
                            "is_output": bool(getattr(item, "in_out", "INPUT") == "OUTPUT")})
result = {"name": group.name, "node_count": len(group.nodes), "links": links, "sockets": sockets}
""".replace("__GROUP_NAME__", json.dumps(str(group_name)))
        result = await self._execute(code)
        return GeometryNodeGroupVO(
            name=str(result["name"]),
            node_count=int(result["node_count"]),
            links=tuple(GeometryNodeLinkVO(**link) for link in result.get("links", [])),
            sockets=tuple(GeometryNodeSocketVO(**socket) for socket in result.get("sockets", [])),
        )

    async def create_group(self, group_name: str, object_name: str | None = None) -> GeometryNodeMutationVO:
        code = """
import bpy
name = __GROUP_NAME__
group = bpy.data.node_groups.get(name)
created = group is None
if group is None:
    group = bpy.data.node_groups.new(name, "GeometryNodeTree")
    interface = getattr(group, "interface", None)
    if interface is not None:
        interface.new_socket(name="Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
        interface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    input_node = group.nodes.new("NodeGroupInput")
    output_node = group.nodes.new("NodeGroupOutput")
    input_socket = input_node.outputs.get("Geometry")
    output_socket = output_node.inputs.get("Geometry")
    if input_socket is not None and output_socket is not None:
        group.links.new(input_socket, output_socket)
obj_name = __OBJECT_NAME__
modifier_name = None
if obj_name:
    obj = bpy.data.objects.get(obj_name)
    if obj is None:
        raise ValueError(f"Object not found: {obj_name}")
    modifier = next((item for item in obj.modifiers if item.type == "NODES"), None)
    if modifier is None:
        modifier = obj.modifiers.new(name="GeometryNodes", type="NODES")
    modifier.node_group = group
    modifier_name = modifier.name
result = {"group_name": group.name, "changed": created, "object_name": obj_name or None,
          "modifier_name": modifier_name, "message": "Geometry Nodes group ready"}
""".replace("__GROUP_NAME__", json.dumps(str(group_name))).replace("__OBJECT_NAME__", json.dumps(object_name))
        result = await self._execute(code)
        return GeometryNodeMutationVO(**result)

    async def set_link(
        self,
        group_name: str,
        from_node: str,
        from_socket: str,
        to_node: str,
        to_socket: str,
    ) -> GeometryNodeMutationVO:
        code = """
import bpy
group = bpy.data.node_groups.get(__GROUP_NAME__)
if group is None:
    raise ValueError(f"Geometry Nodes group not found: {group_name}")
source = group.nodes.get(__FROM_NODE__)
target = group.nodes.get(__TO_NODE__)
if source is None or target is None:
    raise ValueError("Geometry Nodes source or target node not found")
source_socket = source.outputs.get(__FROM_SOCKET__)
target_socket = target.inputs.get(__TO_SOCKET__)
if source_socket is None or target_socket is None:
    raise ValueError("Geometry Nodes source or target socket not found")
for link in list(group.links):
    if link.from_socket == source_socket and link.to_socket == target_socket:
        result = {"group_name": group.name, "changed": False, "message": "Link already exists"}
        break
else:
    group.links.new(source_socket, target_socket)
    result = {"group_name": group.name, "changed": True, "message": "Link created"}
"""
        for token, value in {
            "__GROUP_NAME__": group_name,
            "__FROM_NODE__": from_node,
            "__FROM_SOCKET__": from_socket,
            "__TO_NODE__": to_node,
            "__TO_SOCKET__": to_socket,
        }.items():
            code = code.replace(token, json.dumps(str(value)))
        result = await self._execute(code)
        return GeometryNodeMutationVO(**result)

    async def bind_modifier(self, object_name: str, group_name: str) -> GeometryNodeMutationVO:
        code = """
import bpy
obj = bpy.data.objects.get(__OBJECT_NAME__)
if obj is None:
    raise ValueError(f"Object not found: {object_name}")
group = bpy.data.node_groups.get(__GROUP_NAME__)
if group is None:
    raise ValueError(f"Geometry Nodes group not found: {group_name}")
modifier = next((item for item in obj.modifiers if item.type == "NODES"), None)
if modifier is None:
    modifier = obj.modifiers.new(name="GeometryNodes", type="NODES")
changed = modifier.node_group != group
modifier.node_group = group
result = {"group_name": group.name, "changed": changed, "object_name": obj.name,
          "modifier_name": modifier.name, "message": "Modifier bound"}
""".replace("__OBJECT_NAME__", json.dumps(str(object_name))).replace("__GROUP_NAME__", json.dumps(str(group_name)))
        result = await self._execute(code)
        return GeometryNodeMutationVO(**result)

    async def _execute(self, code: str) -> Mapping[str, object]:
        result = await self._code_executor.execute_blender_code(code)
        if not isinstance(result, Mapping):
            raise RuntimeError("Gateway returned a non-object Geometry Nodes result")
        return result
