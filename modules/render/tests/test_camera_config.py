"""Tests for RenderCameraConfigExecutor — FR-RND-003: Configure Camera.

Exercises lens/sensor-fit validation, security delegation (optional), Blender code generation,
success path with a mocked code executor, and execution failure handling.
All Blender transport is mocked via a duck-typed ICodeExecutionProtocol (execute_python).
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
from modules.shared.src.security.contract_validate_path_protocol import (
    ValidatePathProtocol,
)
from modules.shared.src.security.taxonomy_security_vo import PathValidationVO


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


class MockSecurityValidator(ValidatePathProtocol):
    """Mock security path validator that always allows."""

    def __init__(self, deny: bool = False) -> None:
        self.deny = deny
        self._calls: list[PathValidationVO] = []

    async def validate_path(self, request: PathValidationVO) -> PathValidationVO:
        self._calls.append(request)
        if self.deny:
            return PathValidationVO(
                target_path=request.target_path,
                access_mode=request.access_mode,
                allowed=False,
                denial_reason="Path denied by security policy",
            )
        return PathValidationVO(
            target_path=request.target_path,
            access_mode=request.access_mode,
            allowed=True,
        )


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
        security_validator=MockSecurityValidator(),
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
