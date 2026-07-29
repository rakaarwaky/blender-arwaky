"""Render taxonomy errors."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from typing import NewType

from ..common.taxonomy_core_vo import Prompt

# Branded tuple type for render error detail chains
RenderErrorDetails = NewType("RenderErrorDetails", tuple[Prompt, ...])


class RenderErrorCategory(str, Enum):
    """Stable render error categories."""

    RENDER_OUTPUT = "render_output"
    CAMERA_SETUP = "camera_setup"
    SECURITY_VIOLATION = "security_violation"
    CAPACITY = "capacity"
    TIMEOUT = "timeout"
    VALIDATION = "validation"
    ASSET_NOT_FOUND = "asset_not_found"
    ENVIRONMENT_STATE = "environment_state"
    SCENE_STATE = "scene_state"
    EXECUTION = "execution"


@dataclass(frozen=True)
class RenderError:
    """Immutable render domain error."""

    category: RenderErrorCategory
    message: Prompt
    retryable: bool = False
    details: RenderErrorDetails = ()

    def to_prompt(self) -> Prompt:
        """Render error as prompt/message."""
        return Prompt(f"[{self.category.value}] {self.message}")
