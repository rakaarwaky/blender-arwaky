"""Render operation request and response value objects.

Re-exports merged VOs from taxonomy_render_vo.py for backward compatibility.
Legacy Request/Response names point to the unified VO classes.
"""

from .taxonomy_render_vo import (
    CameraConfigVO,
    CameraSetupVO,
    GetScreenshotVO,
    HdriConfigVO,
    HdriSetupVO,
    RenderVO,
)

# Legacy aliases — prefer the merged VO names above
GetScreenshotRequestVO = GetScreenshotVO
ScreenshotResponseVO = GetScreenshotVO
RenderRequestVO = RenderVO
RenderResponseVO = RenderVO
CameraSetupRequestVO = CameraSetupVO
HdriSetupRequestVO = HdriSetupVO
CameraConfigResultVO = CameraConfigVO
HdriConfigResultVO = HdriConfigVO

__all__ = [
    # Unified VO names
    "CameraConfigVO",
    "CameraSetupVO",
    "GetScreenshotVO",
    "HdriConfigVO",
    "HdriSetupVO",
    "RenderVO",
    # Legacy aliases
    "CameraConfigResultVO",
    "CameraSetupRequestVO",
    "GetScreenshotRequestVO",
    "HdriConfigResultVO",
    "HdriSetupRequestVO",
    "RenderRequestVO",
    "RenderResponseVO",
    "ScreenshotResponseVO",
]
