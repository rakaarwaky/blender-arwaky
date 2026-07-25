"""Blender object type constants."""

from __future__ import annotations

from typing import Final

from .constant_core_types import ObjectType


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
