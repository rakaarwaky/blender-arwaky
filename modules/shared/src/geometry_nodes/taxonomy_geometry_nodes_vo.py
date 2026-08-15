"""Geometry Nodes value objects shared by consumers and feature implementations."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class GeometryNodeSocketVO:
    name: str
    socket_type: str
    is_output: bool


@dataclass(frozen=True)
class GeometryNodeLinkVO:
    from_node: str
    from_socket: str
    to_node: str
    to_socket: str


@dataclass(frozen=True)
class GeometryNodeGroupVO:
    name: str
    node_count: int
    links: tuple[GeometryNodeLinkVO, ...] = field(default_factory=tuple)
    sockets: tuple[GeometryNodeSocketVO, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class GeometryNodeMutationVO:
    group_name: str
    changed: bool
    object_name: str | None = None
    modifier_name: str | None = None
    message: str = ""
