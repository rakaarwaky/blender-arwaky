"""Compositor value objects shared across AES layers."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CompositorNodeVO:
    name: str
    node_type: str
    inputs: tuple[str, ...] = field(default_factory=tuple)
    outputs: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class CompositorLinkVO:
    from_node: str
    from_socket: str
    to_node: str
    to_socket: str


@dataclass(frozen=True)
class CompositorGraphVO:
    use_nodes: bool
    nodes: tuple[CompositorNodeVO, ...] = field(default_factory=tuple)
    links: tuple[CompositorLinkVO, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class CompositorMutationVO:
    changed: bool
    node_name: str | None = None
    use_nodes: bool | None = None
    message: str = ""
