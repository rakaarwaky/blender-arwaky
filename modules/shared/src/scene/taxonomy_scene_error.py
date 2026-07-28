"""Scene taxonomy errors."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ..common.taxonomy_core_vo import Prompt


class SceneErrorCategory(str, Enum):
    """Stable scene error categories."""

    CONNECTION = "connection"
    TIMEOUT = "timeout"
    SCENE_STATE = "scene_state"
    PROTECTION = "protection"
    VALIDATION = "validation"
    CONFIRMATION = "confirmation"
    DELEGATED_DELETION = "delegated_deletion"


@dataclass(frozen=True)
class SceneError:
    """Immutable scene domain error."""

    category: SceneErrorCategory
    message: Prompt
    retryable: bool = False
    details: tuple[Prompt, ...] = ()

    def to_prompt(self) -> Prompt:
        """Render error as prompt/message."""
        return Prompt(f"[{self.category.value}] {self.message}")
