"""CLI value objects — result envelope, process info, registry state, and error structures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import NewType

BlenderPid = NewType("BlenderPid", int)


@dataclass(frozen=True)
class CliErrorVo:
    """CLI error Value Object."""

    category: str
    ref: str
    message: str = "Operation failed"
    detail: str | None = None


@dataclass(frozen=True)
class BlenderProcessVo:
    """Blender process information Value Object (Taxonomy layer)."""

    pid: int
    port: int
    filepath: str = ""
    is_running: bool = True


@dataclass(frozen=True)
class RegistryStateVo:
    """State of active Blender instance Value Object (Taxonomy layer)."""

    active_entity: str | None = None
    port: int = 9876
    pid: int | None = None


@dataclass(frozen=True)
class CliResultVo:
    """CLI result envelope Value Object."""

    success: bool
    message: str | None = None
    error: str | None = None
    category: str | None = None
    ref: str | None = None
    warnings: list[str] | None = None
    data: dict[str, object] | None = None
