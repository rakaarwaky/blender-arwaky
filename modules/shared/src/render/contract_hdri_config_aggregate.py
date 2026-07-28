"""Render domain contract: HDRI configuration aggregate (ABC).

Aggregates all HDRI lighting operations into a single facade that the Agent
layer consumes. Surface layer depends on this aggregate.

FR-RND-004: Configure HDRI Lighting
AES Contract layer — pure ABC definitions, no implementation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_render_vo import HdriConfigVO


class HdriConfigAggregate(ABC):
    """Aggregate facade for HDRI lighting configuration operations.

    FR-RND-004: Applies HDRI-based environment lighting using a locally
    available HDRI file acquired through the asset feature. Resolves strength
    (0-10), rotation, overwrite policy, and background visibility. Never
    downloads HDRI itself. The Agent orchestrator implements this interface.
    Surface layers call through this aggregate.
    """

    @abstractmethod
    async def configure_hdri(self, request: HdriConfigVO) -> HdriConfigVO:
        """FR-RND-004: Set up HDRI-based environment lighting.

        HDRI file must be locally available (acquired via asset feature).
        Local file validated through security policy. Strength in valid range
        (0-10). Rotation normalized. Existing environment follows overwrite
        policy. Environment applies to scene world; world created if missing
        (when allowed). Background visibility controls HDRI appearance vs
        lighting-only contribution.

        Args:
            request: HDRI config with hdri_path, strength, rotation,
                     background_visible, and overwrite_policy.

        Returns:
            HdriConfigVO with success, environment_ref, applied_strength,
            and message.
        """
        ...
