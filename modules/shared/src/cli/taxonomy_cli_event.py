"""CLI events — lifecycle and result event kinds."""

from dataclasses import dataclass, field
from enum import StrEnum, auto


class CliEventKind(StrEnum):
    COMMAND_STARTED = auto()
    COMMAND_SUCCEEDED = auto()
    COMMAND_FAILED = auto()
    CONNECTION_LOST = auto()
    CONNECTION_ESTABLISHED = auto()
    BLENDER_LAUNCHED = auto()
    BLENDER_CLOSED = auto()


@dataclass(frozen=True)
class CliEvent:
    kind: CliEventKind
    command: str | None = None
    detail: str | None = None
    extra: dict[str, str] = field(default_factory=dict)
