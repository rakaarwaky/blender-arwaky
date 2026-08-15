"""Mesh value objects shared across the dispatcher and mesh feature layers."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class MeshStatisticsVO:
    object_name: str
    vertex_count: int
    edge_count: int
    polygon_count: int
    uv_layer_count: int
    has_custom_normals: bool


@dataclass(frozen=True)
class MeshValidationFindingVO:
    category: str
    count: int
    examples: tuple[int, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class MeshValidationVO:
    object_name: str
    valid: bool
    findings: tuple[MeshValidationFindingVO, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class MeshMutationVO:
    object_name: str
    operation: str
    changed: bool
    uv_layer_name: str | None = None
    message: str = ""
