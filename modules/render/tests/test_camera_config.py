"""Tests for RenderCameraConfigExecutor — FR-RND-003: Configure Camera.

Exercises lens/sensor-fit validation, Blender code generation, success path with a mocked code
executor, and execution failure handling. All Blender transport is mocked via a duck-typed
ICodeExecutionProtocol (execute_python).
"""

from __future__ import annotations

import json

import pytest

from modules.render.src.capabilities_render_camera_config_executor import (
    RenderCameraConfigExecutor,
)
from modules.shared.src.common.taxonomy_core_vo import Prompt
from modules.shared.src.render.taxonomy_render_constant import (
    MAX_FOCAL_LENGTH,
    MIN_FOCAL_LENGTH,
)
from modules.shared.src.render.taxonomy_render_vo import CameraConfigVO, FocalLength


class MockCodeExecutor:
    """Duck-typed ICodeExecutionProtocol returning a fixed JSON payload."""

    def __init__(self, payload: dict | None = None, fail: bool = False) -> None:
        self.payload = payload
        self.fail = fail
        self.captured_code: str | None = None

    async def execute_python(self, code: str) -> Prompt:
        self.captured_code = code
        if self.fail:
            raise RuntimeError("code execution failed")
        return Prompt(json.dumps(self.payload) if self.payload is not None else "")


@pytest.fixture
def executor() -> RenderCameraConfigExecutor:
    return RenderCameraConfigExecutor(
        code_executor=MockCodeExecutor(
            payload={
                "camera_reference": "Camera",
                "final_focal_length": 50.0,
                "active_status": True,
                "depth_of_field_applied": False,
            }
        ),
    )


@pytest.mark.asyncio
async def test_fr_rnd_003_configure_camera_success(
    executor: RenderCameraConfigExecutor,
) -> None:
    result = await executor.configure_camera(CameraConfigVO(focal_length=FocalLength(50.0)))
    assert bool(result.success) is True
    assert str(result.resolved_camera_ref) == "Camera"
    assert float(result.final_focal_length) == 50.0
    assert bool(result.active_status) is True


@pytest.mark.asyncio
async def test_fr_rnd_003_lens_too_small(
    executor: RenderCameraConfigExecutor,
) -> None:
    result = await executor.configure_camera(CameraConfigVO(focal_length=FocalLength(5.0)))
    assert bool(result.success) is False


@pytest.mark.asyncio
async def test_fr_rnd_003_lens_too_large(
    executor: RenderCameraConfigExecutor,
) -> None:
    result = await executor.configure_camera(CameraConfigVO(focal_length=FocalLength(400.0)))
    assert bool(result.success) is False


@pytest.mark.asyncio
async def test_fr_rnd_003_lens_boundary_min(
    executor: RenderCameraConfigExecutor,
) -> None:
    result = await executor.configure_camera(
        CameraConfigVO(focal_length=FocalLength(MIN_FOCAL_LENGTH))
    )
    assert bool(result.success) is True


@pytest.mark.asyncio
async def test_fr_rnd_003_lens_boundary_max(
    executor: RenderCameraConfigExecutor,
) -> None:
    result = await executor.configure_camera(
        CameraConfigVO(focal_length=FocalLength(MAX_FOCAL_LENGTH))
    )
    assert bool(result.success) is True


@pytest.mark.asyncio
async def test_fr_rnd_003_invalid_sensor_fit(
    executor: RenderCameraConfigExecutor,
) -> None:
    result = await executor.configure_camera(
        CameraConfigVO(focal_length=FocalLength(50.0), sensor_fit="DIAGONAL")
    )
    assert bool(result.success) is False


@pytest.mark.asyncio
async def test_fr_rnd_003_code_generated(
    executor: RenderCameraConfigExecutor,
) -> None:
    await executor.configure_camera(CameraConfigVO(focal_length=FocalLength(50.0)))
    code = str(executor._code_executor.captured_code)
    assert "import bpy" in code
    assert "camera.data.lens" in code


@pytest.mark.asyncio
async def test_fr_rnd_003_execution_failure() -> None:
    bad = RenderCameraConfigExecutor(code_executor=MockCodeExecutor(fail=True))
    result = await bad.configure_camera(CameraConfigVO(focal_length=FocalLength(50.0)))
    assert bool(result.success) is False


@pytest.mark.asyncio
async def test_fr_rnd_003_missing_camera_reference() -> None:
    """FR-RND-003: Camera not resolved returns error with camera_setup category."""
    bad = RenderCameraConfigExecutor(
        code_executor=MockCodeExecutor(payload={"camera_reference": ""})
    )
    result = await bad.configure_camera(CameraConfigVO(focal_length=FocalLength(50.0)))
    assert bool(result.success) is False
    assert "camera_setup" in str(result.message).lower()


@pytest.mark.asyncio
async def test_fr_rnd_003_default_sensor_fit(executor: RenderCameraConfigExecutor) -> None:
    """FR-RND-003: Valid sensor_fit values pass validation."""
    # sensor_fit uses AUTO/HORIZONTAL/VERTICAL — AUTO is a common default
    result = await executor.configure_camera(
        CameraConfigVO(focal_length=FocalLength(50.0), sensor_fit="AUTO")
    )
    assert bool(result.success) is True
