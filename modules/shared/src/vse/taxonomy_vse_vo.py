"""VSE value objects shared across AES layers."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SequenceStripVO:
    name: str
    strip_type: str
    channel: int
    frame_start: int
    frame_final: int
    filepath: str | None = None


@dataclass(frozen=True)
class SequenceStateVO:
    sequence_present: bool
    strips: tuple[SequenceStripVO, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class SequenceMutationVO:
    changed: bool
    strip_name: str | None = None
    strip_type: str | None = None
    output_path: str | None = None
    frame_start: int | None = None
    frame_end: int | None = None
    message: str = ""
