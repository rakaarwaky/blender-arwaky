"""Scene operation value objects — unified input/output per operation.

Each VO merges request (input) and response (output) into a single frozen dataclass.
Caller sets input fields; callee sets output fields.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..common.taxonomy_core_vo import (
    CleanupMode,
    ObjectCount,
    Prompt,
    SuccessFlag,
)


@dataclass(frozen=True)
class CleanupSceneVO:
    """Scene cleanup — input and output in one VO.

    Input: mode.
    Output: success, objects_removed, message.
    """
    # Input
    mode: CleanupMode = field(default=CleanupMode("all"))
    # Output
    success: SuccessFlag = field(default=SuccessFlag(False))
    objects_removed: ObjectCount = 0
    message: Prompt = field(default_factory=lambda: Prompt(""))


@dataclass(frozen=True)
class GetSceneInfoVO:
    """Scene info retrieval — input and output in one VO.

    Input: (none).
    Output: success, scene_info, message.
    """
    # Input: (no fields — pure query)
    # Output
    success: SuccessFlag = field(default=SuccessFlag(False))
    scene_info: dict | None = None
    message: Prompt = field(default_factory=lambda: Prompt(""))


@dataclass(frozen=True)
class SetupEnvironmentVO:
    """Environment setup — input and output in one VO.

    Input: hdri_id, strength.
    Output: success, hdri_path, message.
    """
    # Input
    hdri_id: str = ""
    strength: float = 1.0
    # Output
    success: SuccessFlag = field(default=SuccessFlag(False))
    hdri_path: str | None = None
    message: Prompt = field(default_factory=lambda: Prompt(""))
