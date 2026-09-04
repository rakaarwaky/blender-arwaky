"""Mesh capability executor for bounded topology and UV operations."""

from __future__ import annotations

import json
from collections.abc import Mapping

from modules.shared.src.common.contract_wave_feature_protocol import IWaveFeatureProtocol
from modules.shared.src.mesh.taxonomy_mesh_vo import (
    MeshMutationVO,
    MeshStatisticsVO,
    MeshValidationFindingVO,
    MeshValidationVO,
)

_ALLOWED_OPERATIONS = {"recalculate_normals", "triangulate", "remove_doubles"}


class MeshExecutor(IWaveFeatureProtocol):
    """Delegate validated mesh behavior to the injected Blender gateway."""

    def __init__(self, code_executor: object) -> None:
        self._code_executor = code_executor

    async def get_statistics(self, object_name: str) -> MeshStatisticsVO:
        code = """
import bpy
obj = bpy.data.objects.get(__OBJECT_NAME__)
if obj is None:
    raise ValueError(f"Object not found: {obj_name}")
if obj.type != "MESH":
    raise ValueError(f"Object is not a mesh: {obj.name}")
mesh = obj.data
result = {"object_name": obj.name, "vertex_count": len(mesh.vertices),
          "edge_count": len(mesh.edges), "polygon_count": len(mesh.polygons),
          "uv_layer_count": len(mesh.uv_layers),
          "has_custom_normals": bool(getattr(mesh, "has_custom_normals", False))}
""".replace("__OBJECT_NAME__", json.dumps(str(object_name)))
        result = await self._execute(code)
        return MeshStatisticsVO(
            object_name=str(result["object_name"]),
            vertex_count=int(result["vertex_count"]),
            edge_count=int(result["edge_count"]),
            polygon_count=int(result["polygon_count"]),
            uv_layer_count=int(result["uv_layer_count"]),
            has_custom_normals=bool(result["has_custom_normals"]),
        )

    async def validate(self, object_name: str, limit: int = 100) -> MeshValidationVO:
        limit = self._bounded_limit(limit)
        code = """
import bpy
obj = bpy.data.objects.get(__OBJECT_NAME__)
if obj is None:
    raise ValueError(f"Object not found: {obj_name}")
if obj.type != "MESH":
    raise ValueError(f"Object is not a mesh: {obj.name}")
mesh = obj.data
loose = [vertex.index for vertex in mesh.vertices if not vertex.link_edges][:__LIMIT__]
degenerate = [polygon.index for polygon in mesh.polygons if len(polygon.vertices) < 3 or polygon.area <= 1.0e-12][:__LIMIT__]
non_manifold = [edge.index for edge in mesh.edges if not edge.is_manifold][:__LIMIT__]
findings = []
for category, values in (("loose_vertices", loose), ("degenerate_polygons", degenerate), ("non_manifold_edges", non_manifold)):
    if values:
        findings.append({"category": category, "count": len(values), "examples": values})
result = {"object_name": obj.name, "valid": not findings, "findings": findings}
""".replace("__OBJECT_NAME__", json.dumps(str(object_name))).replace("__LIMIT__", str(limit))
        result = await self._execute(code)
        findings = tuple(
            MeshValidationFindingVO(
                category=str(item.get("category", "")),
                count=int(item.get("count", 0)),
                examples=tuple(int(value) for value in item.get("examples", [])),
            )
            for item in result.get("findings", [])
            if isinstance(item, Mapping)
        )
        return MeshValidationVO(object_name=str(result["object_name"]), valid=bool(result["valid"]), findings=findings)

    async def edit(self, object_name: str, operation: str) -> MeshMutationVO:
        operation = str(operation)
        if operation not in _ALLOWED_OPERATIONS:
            raise ValueError(f"Unsupported mesh operation: {operation}")
        code = """
import bmesh
import bpy
obj = bpy.data.objects.get(__OBJECT_NAME__)
if obj is None:
    raise ValueError(f"Object not found: {obj_name}")
if obj.type != "MESH":
    raise ValueError(f"Object is not a mesh: {obj.name}")
mesh = obj.data
bm = bmesh.new()
bm.from_mesh(mesh)
changed = False
if __OPERATION__ == "recalculate_normals":
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    changed = True
elif __OPERATION__ == "triangulate":
    result_faces = bmesh.ops.triangulate(bm, faces=list(bm.faces))
    changed = bool(result_faces.get("faces"))
elif __OPERATION__ == "remove_doubles":
    result_verts = bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1.0e-6)
    changed = bool(result_verts.get("targetmap"))
bm.to_mesh(mesh)
bm.free()
mesh.update()
result = {"object_name": obj.name, "operation": __OPERATION__, "changed": changed,
          "message": "Mesh operation completed"}
""".replace("__OBJECT_NAME__", json.dumps(str(object_name))).replace("__OPERATION__", json.dumps(operation))
        result = await self._execute(code)
        return MeshMutationVO(
            object_name=str(result["object_name"]),
            operation=str(result["operation"]),
            changed=bool(result.get("changed", False)),
            message=str(result.get("message", "")),
        )

    async def ensure_uv_layer(self, object_name: str, uv_layer_name: str = "UVMap") -> MeshMutationVO:
        name = str(uv_layer_name).strip() or "UVMap"
        if len(name) > 64:
            raise ValueError("uv_layer_name must not exceed 64 characters")
        code = """
import bpy
obj = bpy.data.objects.get(__OBJECT_NAME__)
if obj is None:
    raise ValueError(f"Object not found: {obj_name}")
if obj.type != "MESH":
    raise ValueError(f"Object is not a mesh: {obj.name}")
layer = obj.data.uv_layers.get(__UV_NAME__)
created = layer is None
if layer is None:
    layer = obj.data.uv_layers.new(name=__UV_NAME__)
result = {"object_name": obj.name, "operation": "ensure_mesh_uv_layer", "changed": created,
          "uv_layer_name": layer.name, "message": "UV layer ready"}
""".replace("__OBJECT_NAME__", json.dumps(str(object_name))).replace("__UV_NAME__", json.dumps(name))
        result = await self._execute(code)
        return MeshMutationVO(
            object_name=str(result["object_name"]),
            operation=str(result["operation"]),
            changed=bool(result.get("changed", False)),
            uv_layer_name=str(result.get("uv_layer_name", name)),
            message=str(result.get("message", "")),
        )

    async def _execute(self, code: str) -> Mapping[str, object]:
        result = await self._code_executor.execute_blender_code(code)
        if not isinstance(result, Mapping):
            raise RuntimeError("Gateway returned a non-object mesh result")
        return result

    @staticmethod
    def _bounded_limit(value: int) -> int:
        limit = int(value)
        if not 1 <= limit <= 1000:
            raise ValueError("limit must be between 1 and 1000")
        return limit
