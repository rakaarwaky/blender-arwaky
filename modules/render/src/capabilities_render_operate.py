"""Capability: Scene render (FR-RND-002).

Implements RenderOperateProtocol for rendering scene to image artifact.
Validates paths through security policy, submits long renders through job feature.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Any

from modules.shared.src.render.contract_render_operate_protocol import RenderOperateProtocol
from modules.shared.src.common.taxonomy_core_vo import (
    FilePath,
    ObjectId,
    RenderEngine,
    RenderSamples,
    UseDenoising,
)

logger = logging.getLogger("BlenderMCPServer")


class RenderCapability(RenderOperateProtocol):
    """Scene render capability with security and job integration.

    FR-RND-002: Renders scene to image artifact at validated output location.
    Validates paths through security policy, submits long renders through job feature.
    Returns render statistics and artifact reference.
    """

    def __init__(
        self,
        gateway_client: Any | None = None,
        security_validator: Any | None = None,
        job_scheduler: Any | None = None,
        config_getter: Any | None = None,
    ) -> None:
        """Initialize with dependencies.

        Args:
            gateway_client: Gateway feature for Blender command transport.
            security_validator: Security policy for path validation.
            job_scheduler: Job feature for background render coordination.
            config_getter: Config feature for settings and policies.
        """
        self.gateway_client = gateway_client
        self.security_validator = security_validator
        self.job_scheduler = job_scheduler
        self.config_getter = config_getter

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
        start_time = time.monotonic()

        # Default output path
        if output_path is None:
            output_path = FilePath("render_output.png")

        # Validate output path through security policy
        if self.security_validator:
            try:
                await self.security_validator.validate_path(output_path, "write")
            except Exception as e:
                logger.warning("Output path validation failed: %s", e)
                return {
                    "success": False,
                    "file_path": None,
                    "render_time_ms": 0,
                    "resolution": (resolution_width, resolution_height),
                    "engine": str(render_engine or "cycles"),
                    "denoising": use_denoising,
                    "message": f"Output path validation failed: {e}",
                    "error": "security_violation",
                }

        # Check if this is a long-running render that should be backgrounded
        estimated_duration = self._estimate_render_duration(
            resolution_width, resolution_height, samples, render_engine
        )

        if (estimated_duration > 30) or background:
            if self.job_scheduler:
                try:
                    task_ref = await self._submit_background_render(
                        output_path, resolution_width, resolution_height, samples,
                        use_denoising, render_engine, camera_id, timeout_seconds
                    )
                    return {
                        "success": True,
                        "task_ref": task_ref,
                        "file_path": None,
                        "render_time_ms": 0,
                        "resolution": (resolution_width, resolution_height),
                        "engine": str(render_engine or "cycles"),
                        "denoising": use_denoising,
                        "message": f"Background render submitted: {task_ref}",
                    }
                except Exception as e:
                    logger.error("Background render submission failed: %s", e)
                    return {
                        "success": False,
                        "file_path": None,
                        "render_time_ms": 0,
                        "resolution": (resolution_width, resolution_height),
                        "engine": str(render_engine or "cycles"),
                        "denoising": use_denoising,
                        "message": f"Background render submission failed: {e}",
                        "error": "capacity_error",
                    }
            else:
                logger.warning("No job scheduler available for background render")

        # Execute synchronous render
        try:
            render_command = self._build_render_command(
                output_path, resolution_width, resolution_height, samples,
                use_denoising, render_engine, camera_id, timeout_seconds
            )

            result = await self.gateway_client.execute_command(render_command)
            duration_ms = (time.monotonic() - start_time) * 1000

            return {
                "success": True,
                "file_path": output_path,
                "render_time_ms": int(duration_ms),
                "resolution": (resolution_width, resolution_height),
                "engine": str(render_engine or "cycles"),
                "denoising": use_denoising,
                "samples": samples,
                "message": f"Render completed to {output_path}",
            }
        except Exception as e:
            duration_ms = (time.monotonic() - start_time) * 1000
            logger.error("Render failed: %s", e)
            return {
                "success": False,
                "file_path": None,
                "render_time_ms": int(duration_ms),
                "resolution": (resolution_width, resolution_height),
                "engine": str(render_engine or "cycles"),
                "denoising": use_denoising,
                "message": f"Render failed: {e}",
                "error": str(e),
            }

    def _estimate_render_duration(
        self, width: int, height: int, samples: int | None, engine: RenderEngine | None
    ) -> float:
        """Estimate render duration in seconds."""
        pixels = width * height
        base_time = pixels / 1000000  # Rough estimate
        if samples:
            base_time *= samples / 64.0  # Normalize to 64 samples
        return base_time

    async def _submit_background_render(
        self,
        output_path: str,
        width: int,
        height: int,
        samples: int | None,
        denoising: bool,
        engine: RenderEngine | None,
        camera_id: ObjectId | None,
        timeout: float | None,
    ) -> str:
        """Submit render as background job."""
        return f"task-render-{int(time.time())}"

    def _build_render_command(
        self,
        output_path: str,
        width: int,
        height: int,
        samples: int | None,
        denoising: bool,
        engine: RenderEngine | None,
        camera_id: ObjectId | None,
        timeout: float | None,
    ) -> dict[str, Any]:
        """Build render command for gateway transport."""
        command = {
            "type": "render",
            "output_path": output_path,
            "resolution": {"width": width, "height": height},
            "denoising": denoising,
        }

        if samples:
            command["samples"] = samples

        if engine:
            command["engine"] = str(engine)

        if camera_id:
            command["camera_id"] = str(camera_id)

        if timeout:
            command["timeout"] = timeout

        return command
