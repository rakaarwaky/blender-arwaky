"""Blender object type constants."""

from __future__ import annotations

from typing import Final

from ..common.taxonomy_core_vo import ObjectType

# ============================================================
# OBJECT TYPE CONSTANTS
# ============================================================

OBJECT_TYPE_MESH: Final[ObjectType] = ObjectType("MESH")
OBJECT_TYPE_CAMERA: Final[ObjectType] = ObjectType("CAMERA")
OBJECT_TYPE_LIGHT: Final[ObjectType] = ObjectType("LIGHT")
OBJECT_TYPE_EMPTY: Final[ObjectType] = ObjectType("EMPTY")
OBJECT_TYPE_ARMATURE: Final[ObjectType] = ObjectType("ARMATURE")
OBJECT_TYPE_CURVE: Final[ObjectType] = ObjectType("CURVE")
OBJECT_TYPE_SURFACE: Final[ObjectType] = ObjectType("SURFACE")
OBJECT_TYPE_META: Final[ObjectType] = ObjectType("META")
OBJECT_TYPE_FONT: Final[ObjectType] = ObjectType("FONT")
OBJECT_TYPE_LATTICE: Final[ObjectType] = ObjectType("LATTICE")
OBJECT_TYPE_GPENCIL: Final[ObjectType] = ObjectType("GPENCIL")
OBJECT_TYPE_VOLUME: Final[ObjectType] = ObjectType("VOLUME")
OBJECT_TYPE_POINTCLOUD: Final[ObjectType] = ObjectType("POINTCLOUD")

ALLOWED_OBJECT_TYPES: Final[list[ObjectType]] = [
    OBJECT_TYPE_MESH,
    OBJECT_TYPE_CAMERA,
    OBJECT_TYPE_LIGHT,
    OBJECT_TYPE_EMPTY,
    OBJECT_TYPE_ARMATURE,
    OBJECT_TYPE_CURVE,
    OBJECT_TYPE_SURFACE,
    OBJECT_TYPE_META,
    OBJECT_TYPE_FONT,
    OBJECT_TYPE_LATTICE,
    OBJECT_TYPE_GPENCIL,
    OBJECT_TYPE_VOLUME,
    OBJECT_TYPE_POINTCLOUD,
]

# ============================================================
# PRIMITIVE / MODIFIER CATALOG CONSTANTS
# ============================================================

# Supported primitive type mapping to Blender operator strings.
# Includes mesh primitives and non-mesh types (camera, light, empty).
PRIMITIVE_OPS_MAP: Final[dict[str, str]] = {
    "cube": "bpy.ops.mesh.primitive_cube_add",
    "sphere": "bpy.ops.mesh.primitive_uv_sphere_add",
    "cylinder": "bpy.ops.mesh.primitive_cylinder_add",
    "cone": "bpy.ops.mesh.primitive_cone_add",
    "torus": "bpy.ops.mesh.primitive_torus_add",
    "grid": "bpy.ops.mesh.primitive_grid_add",
    "monkey": "bpy.ops.mesh.primitive_monkey_add",
    "plane": "bpy.ops.mesh.primitive_plane_add",
    "circle": "bpy.ops.mesh.primitive_circle_add",
    "octahedron": "bpy.ops.mesh.primitive_octahedron_add",
    "irregular_monkey": "bpy.ops.mesh.primitive_irregular_grid_grid_add",
}

# Non-mesh primitive operators (camera, light, empty)
NON_MESH_PRIMITIVES: Final[dict[str, str]] = {
    "camera": "bpy.ops.object.camera_add",
    "light": "bpy.ops.object.light_add",
    "empty": "bpy.ops.object.empty_add",
}
