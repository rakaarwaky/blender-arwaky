"""Render domain contract: scene render operate aggregate (ABC).

Aggregates all scene render operations into a single facade that the Agent
layer consumes. Surface layer depends on this aggregate.

FR-RND-002: Render Scene Image
AES Contract layer — pure ABC definitions, no implementation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_render_vo import RenderVO


class RenderOperateAggregate(ABC):
    """Aggregate facade for scene render operations.

    FR-RND-002: Renders the scene to an image artifact at a validated output
    location. Long-running renders are submitted through the job feature.
    The Agent orchestrator implements this interface.
    Surface layers call through this aggregate.
    """

    @abstractmethod
    async def render_scene(self, request: RenderVO) -> RenderVO:
        """FR-RND-002: Render scene to image artifact.

        Output validated through security policy. Resolution and samples
        within configured bounds. Long-running renders submitted through
        job feature with task reference. Returns render statistics including
        duration, resolution, sample count, engine used, and denoising status.

        Args:
            request: Render request with output_path, resolution, samples,
                     use_denoising, render_engine, and camera_id.

        Returns:
            RenderVO with success, image_path, render_time, resolution,
            engine, denoising_status, and message; or task_ref when background.
        """
        ...
