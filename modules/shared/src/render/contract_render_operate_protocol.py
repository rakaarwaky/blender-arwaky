"""Render domain contract: scene render protocol (ABC based).

Defines the protocol for rendering the scene to an image artifact.

FR-RND-002: Render Scene Image
AES Contract layer — pure ABC definitions, no implementation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import (
    FilePath,
    ObjectId,
    RenderEngine,
    RenderSamples,
    UseDenoising,
)


class RenderOperateProtocol(ABC):
    """Protocol for rendering scene images.

    FR-RND-002: Renders scene to image artifact at validated output location.
    Validates paths through security policy, submits long renders through job feature.
    Returns render statistics and artifact reference.
    """

    @abstractmethod
    async def render_scene(
        self,
        output_path: FilePath | None = None,
        resolution_width: int = 1920,
        resolution_height: int = 1080,
        samples: RenderSamples | None = None,
        use_denoising: UseDenoising = False,
        render_engine: RenderEngine | None = None,
        camera_id: ObjectId | None = None,
        background: bool = False,
        timeout_seconds: float | None = None,
        overwrite_policy: str = "overwrite",
    ) -> dict[str, Any]:
        """Render scene to image artifact.

        FR-RND-002: Output validated through security policy. Resolution and
        samples within configured bounds. Long-running renders submitted through
        job feature with task reference. Render statistics include duration,
        resolution, sample count, engine used, and denoising status.

        Args:
            output_path: Optional output file path.
            resolution_width: Render width in pixels.
            resolution_height: Render height in pixels.
            samples: Render sample count.
            use_denoising: Enable denoising.
            render_engine: Preferred render engine.
            camera_id: Optional camera reference.
            background: Submit as background job.
            timeout_seconds: Optional timeout limit.
            overwrite_policy: overwrite/reject/unique for existing files.

        Returns:
            Dict with success, file_path, render_time, resolution, engine,
            denoising_status, and message; or task_ref when background.
        """
        ...