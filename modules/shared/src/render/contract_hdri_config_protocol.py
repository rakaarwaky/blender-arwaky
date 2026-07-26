"""Render domain contract: HDRI configuration protocol (ABC based).

Defines the protocol for configuring HDRI environment lighting.

FR-RND-004: Configure HDRI Lighting
AES Contract layer — pure ABC definitions, no implementation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import (
    FilePath,
)


class HdriConfigProtocol(ABC):
    """Protocol for configuring HDRI environment lighting.

    FR-RND-004: Applies HDRI-based environment lighting using locally available
    HDRI file acquired through asset feature. Resolves strength (0-10), rotation,
    overwrite policy, and background visibility. Never downloads HDRI itself.
    """

    @abstractmethod
    async def configure_hdri(
        self,
        hdri_file_path: FilePath,
        strength: float = 1.0,
        rotation: float = 0.0,
        background_visible: bool = True,
        overwrite_policy: str = "replace",
    ) -> dict[str, Any]:
        """Set up HDRI-based environment lighting.

        FR-RND-004: HDRI file must be locally available (acquired via asset feature).
        Local file validated through security policy. Strength in valid range (0-10).
        Rotation normalized. Existing environment follows overwrite policy.
        Environment applies to scene world; world created if missing (when allowed).
        Background visibility controls HDRI appearance vs lighting-only contribution.

        Args:
            hdri_file_path: Path to local HDRI file (from asset feature).
            strength: Environment strength (0.0-10.0 range).
            rotation: HDRI rotation in degrees.
            background_visible: Whether HDRI appears as visible background.
            overwrite_policy: replace/update/reject for existing environment.

        Returns:
            Dict with success, environment_reference, strength, rotation,
            and message.
        """
        ...