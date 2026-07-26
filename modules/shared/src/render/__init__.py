"""Render domain — taxonomy types and contracts."""

from .contract_camera_config_protocol import CameraConfigProtocol
from .contract_hdri_config_protocol import HdriConfigProtocol
from .contract_render_operate_protocol import RenderOperateProtocol
from .contract_viewport_capture import ViewportCapturePort
from .taxonomy_render_request_vo import (
    CameraConfigResultVO,
    CameraSetupRequestVO,
    GetScreenshotRequestVO,
    HdriConfigResultVO,
    HdriSetupRequestVO,
    RenderRequestVO,
    RenderResponseVO,
    ScreenshotResponseVO,
)
from .taxonomy_render_vo import (
    CameraConfigVO,
    CameraSetupVO,
    GetScreenshotVO,
    HdriConfigVO,
    HdriSetupVO,
    RenderVO,
)

__all__ = [
    # Protocols
    "CameraConfigProtocol",
    "HdriConfigProtocol",
    "RenderOperateProtocol",
    "ViewportCapturePort",
    # Request/Result VOs (legacy aliases)
    "CameraSetupRequestVO",
    "CameraConfigResultVO",
    "GetScreenshotRequestVO",
    "HdriSetupRequestVO",
    "HdriConfigResultVO",
    "RenderRequestVO",
    "RenderResponseVO",
    "ScreenshotResponseVO",
    # Merged VOs
    "CameraConfigVO",
    "CameraSetupVO",
    "GetScreenshotVO",
    "HdriConfigVO",
    "HdriSetupVO",
    "RenderVO",
]
