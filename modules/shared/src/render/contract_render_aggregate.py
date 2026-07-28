"""Aggregate contract for the render feature.

Aggregates all protocol contracts into a single unified interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .contract_camera_config_protocol import CameraConfigProtocol
from .contract_hdri_config_protocol import HdriConfigProtocol
from .contract_render_operate_protocol import RenderOperateProtocol
from .contract_viewport_capture import ViewportCapturePort
from .taxonomy_render_vo import CameraConfigVO, GetScreenshotVO, HdriConfigVO, RenderVO

__all__ = [
    "CameraConfigProtocol",
    "HdriConfigProtocol",
    "RenderOperateProtocol",
    "ViewportCapturePort",
]


class ICameraConfigAggregate(ABC):
    """Aggregate facade for camera configuration operations.

    FR-RND-003: Configures camera optical properties including lens, framing,
    active designation, and depth of field. Returns resolved camera reference
    and final settings. The Agent orchestrator implements this interface.
    Surface layers call through this aggregate.
    """

    @abstractmethod
    async def configure_camera(self, request: CameraConfigVO) -> CameraConfigVO:
        """FR-RND-003: Configure camera optical and selection behavior.

        Creates camera if none exists (when policy allows). Resolves multiple
        cameras deterministically. Lens within valid range. Depth of field
        settings include enablement, focus distance/object, aperture. Framing
        target adjusts camera orientation preserving lens settings. Positional
        transform belongs to object feature, not here.

        Args:
            request: Camera config with camera_id, lens, framing_target,
                     set_active, depth_of_field, and create_if_missing.

        Returns:
            CameraConfigVO with success, camera_name, final_settings,
            and message.
        """
        ...


class IHdriConfigAggregate(ABC):
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


class IRenderOperateAggregate(ABC):
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


class IViewportCaptureAggregate(ABC):
    """Aggregate facade for viewport screenshot capture operations.

    FR-RND-001: Captures the current viewport as an image artifact at a
    validated output location. Returns file reference with capture metadata.
    The Agent orchestrator implements this interface.
    Surface layers call through this aggregate.
    """

    @abstractmethod
    async def capture_viewport(self, request: GetScreenshotVO) -> GetScreenshotVO:
        """FR-RND-001: Capture current viewport as image artifact.

        Output location validated through security policy. View angle must be
        perspective/orthographic/active_camera. Shading mode must be
        wireframe/solid/material_preview/rendered. Max size enforced while
        preserving aspect ratio. Result returns file reference with metadata.

        Args:
            request: Screenshot capture request with max_size, view_angle,
                     shading_mode, overlay_visibility, and focus_object.

        Returns:
            GetScreenshotVO with success, image_path, dimensions, format,
            duration_ms, and message.
        """
        ...
