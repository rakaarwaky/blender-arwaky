"""CLI events — lifecycle and result event kinds."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum, auto

from .taxonomy_cli_vo import CliResultVo


class CliEventKind(StrEnum):
    """CLI event kind enumeration."""

    COMMAND_STARTED = auto()
    COMMAND_SUCCEEDED = auto()
    COMMAND_FAILED = auto()
    CONNECTION_LOST = auto()
    CONNECTION_ESTABLISHED = auto()
    BLENDER_LAUNCHED = auto()
    BLENDER_CLOSED = auto()


@dataclass(frozen=True)
class CliEvent:
    """CLI event structure."""

    kind: CliEventKind
    command: str | None = None
    detail: str | None = None
    result: CliResultVo | None = None
