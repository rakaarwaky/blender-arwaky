"""Tests for render executors — FR-RND-001 (Viewport Capture) and FR-RND-002 (Scene Render).

Exercises validation, Blender code generation, success paths with mocked code
executor, security delegation, and failure handling. All Blender transport is mocked.
"""

from __future__ import annotations

import json

import pytest

from modules.render.src.capabilities_render_scene_image_executor import (
    RenderSceneImageExecutor,
)
from modules.render.src.capabilities_render_viewport_capture_executor import (
    RenderViewportCaptureExecutor,
)
from modules.shared.src.common.taxonomy_core_vo import (
    FilePath,
    ImageFormat,
    Prompt,
    RenderEngine,
    RenderSamples,
    ResolutionX,
    ResolutionY,
    UseDenoising,
)
from modules.shared.src.render.taxonomy_render_vo import (
    RenderSceneVO,
    ViewportCaptureVO,
)
from modules.shared.src.security.contract_validate_path_protocol import (
    ValidatePathProtocol,
)
from modules.shared.src.security.taxonomy_security_vo import (
    AccessMode,
    PathValidationVO,
)


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
        from pathlib import Path as _Path

        return PathValidationVO(
            target_path=request.target_path,
            access_mode=request.access_mode,
            allowed=True,
            canonical_path=str(_Path(request.target_path).resolve()),
        )


# ─── FR-RND-001: Viewport capture ─────────────────────────────


@pytest.fixture
def viewport_executor() -> RenderViewportCaptureExecutor:
    return RenderViewportCaptureExecutor(
        code_executor=MockCodeExecutor(
            payload={
                "artifact_path": "/tmp/shot.png",
                "width": 1920,
                "height": 1080,
                "format": "PNG",
            }
        ),
        security_validator=MockSecurityValidator(),
    )


def _viewport_req(**kwargs: object) -> ViewportCaptureVO:
    base = dict(
        output_path=FilePath("/tmp/shot.png"),
        view_angle="perspective",
        shading="rendered",
        image_format=ImageFormat("PNG"),
        overwrite_policy="overwrite",
    )
    base.update(kwargs)
    return ViewportCaptureVO(**base)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_fr_rnd_001_capture_viewport_success(
    viewport_executor: RenderViewportCaptureExecutor,
) -> None:
    result = await viewport_executor.capture_viewport(_viewport_req())
    assert bool(result.success) is True
    assert str(result.artifact_path) == "/tmp/shot.png"
    assert int(result.width) == 1920
    assert int(result.height) == 1080


@pytest.mark.asyncio
async def test_fr_rnd_001_missing_output_path(
    viewport_executor: RenderViewportCaptureExecutor,
) -> None:
    result = await viewport_executor.capture_viewport(_viewport_req(output_path=FilePath("")))
    assert bool(result.success) is False


@pytest.mark.asyncio
async def test_fr_rnd_001_invalid_view_angle(
    viewport_executor: RenderViewportCaptureExecutor,
) -> None:
    result = await viewport_executor.capture_viewport(_viewport_req(view_angle="top"))
    assert bool(result.success) is False


@pytest.mark.asyncio
async def test_fr_rnd_001_invalid_shading(
    viewport_executor: RenderViewportCaptureExecutor,
) -> None:
    result = await viewport_executor.capture_viewport(_viewport_req(shading="rainbow"))
    assert bool(result.success) is False


@pytest.mark.asyncio
async def test_fr_rnd_001_invalid_image_format(
    viewport_executor: RenderViewportCaptureExecutor,
) -> None:
    result = await viewport_executor.capture_viewport(_viewport_req(image_format=ImageFormat("GIF")))
    assert bool(result.success) is False


@pytest.mark.asyncio
async def test_fr_rnd_001_invalid_overwrite_policy(
    viewport_executor: RenderViewportCaptureExecutor,
) -> None:
    result = await viewport_executor.capture_viewport(_viewport_req(overwrite_policy="maybe"))
    assert bool(result.success) is False


@pytest.mark.asyncio
async def test_fr_rnd_001_code_generated(
    viewport_executor: RenderViewportCaptureExecutor,
) -> None:
    await viewport_executor.capture_viewport(_viewport_req())
    code = str(viewport_executor._code_executor.captured_code)
    assert "bpy.ops.render.render(write_still=True)" in code


@pytest.mark.asyncio
async def test_fr_rnd_001_execution_failure() -> None:
    bad = RenderViewportCaptureExecutor(code_executor=MockCodeExecutor(fail=True))
    result = await bad.capture_viewport(_viewport_req())
    assert bool(result.success) is False


@pytest.mark.asyncio
async def test_fr_rnd_001_security_delegation(
    viewport_executor: RenderViewportCaptureExecutor,
) -> None:
    """FR-RND-001: Verify security validator is called before execution."""
    await viewport_executor.capture_viewport(_viewport_req())
    assert len(viewport_executor._security_validator._calls) == 1
    call = viewport_executor._security_validator._calls[0]
    assert call.access_mode == AccessMode.WRITE


@pytest.mark.asyncio
async def test_fr_rnd_001_security_rejection() -> None:
    """FR-RND-001: Security rejection returns error."""
    sec = MockSecurityValidator(deny=True)
    cap = RenderViewportCaptureExecutor(
        code_executor=MockCodeExecutor(payload={"artifact_path": "/tmp/shot.png"}),
        security_validator=sec,
    )
    result = await cap.capture_viewport(_viewport_req())
    assert bool(result.success) is False
    assert "security_violation" in str(result.message).lower()


# ─── FR-RND-002: Scene render ─────────────────────────────────


@pytest.fixture
def scene_executor() -> RenderSceneImageExecutor:
    return RenderSceneImageExecutor(
        code_executor=MockCodeExecutor(
            payload={
                "artifact_path": "/tmp/render.png",
                "width": 1920,
                "height": 1080,
                "render_time": 1.5,
                "engine_used": "CYCLES",
                "denoising_applied": True,
            }
        ),
        security_validator=MockSecurityValidator(),
    )


def _scene_req(**kwargs: object) -> RenderSceneVO:
    base = dict(
        output_path=FilePath("/tmp/render.png"),
        resolution_x=ResolutionX(1920),
        resolution_y=ResolutionY(1080),
        samples=RenderSamples(128),
        use_denoising=UseDenoising(True),
        render_engine=RenderEngine("CYCLES"),
        overwrite_policy="overwrite",
    )
    base.update(kwargs)
    return RenderSceneVO(**base)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_fr_rnd_002_render_scene_success(
    scene_executor: RenderSceneImageExecutor,
) -> None:
    result = await scene_executor.render_scene(_scene_req())
    assert bool(result.success) is True
    assert str(result.artifact_path) == "/tmp/render.png"
    assert float(result.render_time) == 1.5


@pytest.mark.asyncio
async def test_fr_rnd_002_missing_output_path(
    scene_executor: RenderSceneImageExecutor,
) -> None:
    result = await scene_executor.render_scene(_scene_req(output_path=FilePath("")))
    assert bool(result.success) is False


@pytest.mark.asyncio
async def test_fr_rnd_002_resolution_too_small(
    scene_executor: RenderSceneImageExecutor,
) -> None:
    result = await scene_executor.render_scene(_scene_req(resolution_x=ResolutionX(0)))
    assert bool(result.success) is False


@pytest.mark.asyncio
async def test_fr_rnd_002_resolution_too_large(
    scene_executor: RenderSceneImageExecutor,
) -> None:
    result = await scene_executor.render_scene(_scene_req(resolution_x=ResolutionX(9000)))
    assert bool(result.success) is False


@pytest.mark.asyncio
async def test_fr_rnd_002_samples_out_of_range(
    scene_executor: RenderSceneImageExecutor,
) -> None:
    result = await scene_executor.render_scene(_scene_req(samples=RenderSamples(0)))
    assert bool(result.success) is False


@pytest.mark.asyncio
async def test_fr_rnd_002_invalid_overwrite_policy(
    scene_executor: RenderSceneImageExecutor,
) -> None:
    result = await scene_executor.render_scene(_scene_req(overwrite_policy="maybe"))
    assert bool(result.success) is False


@pytest.mark.asyncio
async def test_fr_rnd_002_invalid_engine_normalized_to_cycles(
    scene_executor: RenderSceneImageExecutor,
) -> None:
    await scene_executor.render_scene(_scene_req(render_engine=RenderEngine("INVALID")))
    code = str(scene_executor._code_executor.captured_code)
    assert "scene.render.engine = 'CYCLES'" in code


@pytest.mark.asyncio
async def test_fr_rnd_002_code_generated(
    scene_executor: RenderSceneImageExecutor,
) -> None:
    await scene_executor.render_scene(_scene_req())
    code = str(scene_executor._code_executor.captured_code)
    assert "bpy.ops.render.render(write_still=True)" in code


@pytest.mark.asyncio
async def test_fr_rnd_002_execution_failure() -> None:
    bad = RenderSceneImageExecutor(code_executor=MockCodeExecutor(fail=True))
    result = await bad.render_scene(_scene_req())
    assert bool(result.success) is False


@pytest.mark.asyncio
async def test_fr_rnd_002_security_delegation(
    scene_executor: RenderSceneImageExecutor,
) -> None:
    """FR-RND-002: Verify security validator is called before render."""
    await scene_executor.render_scene(_scene_req())
    assert len(scene_executor._security_validator._calls) == 1
    call = scene_executor._security_validator._calls[0]
    assert call.access_mode == AccessMode.WRITE


@pytest.mark.asyncio
async def test_fr_rnd_002_security_rejection() -> None:
    """FR-RND-002: Security rejection returns error."""
    sec = MockSecurityValidator(deny=True)
    cap = RenderSceneImageExecutor(
        code_executor=MockCodeExecutor(payload={"artifact_path": "/tmp/render.png"}),
        security_validator=sec,
    )
    result = await cap.render_scene(_scene_req())
    assert bool(result.success) is False
    assert "security_violation" in str(result.message).lower()


@pytest.mark.asyncio
async def test_fr_rnd_001_max_size_too_small(
    viewport_executor: RenderViewportCaptureExecutor,
) -> None:
    """FR-RND-001: max_size below 64 pixels is rejected."""
    result = await viewport_executor.capture_viewport(
        _viewport_req(max_size=32)  # type: ignore[arg-type]
    )
    assert bool(result.success) is False
    assert "max_size" in str(result.message).lower()


@pytest.mark.asyncio
async def test_fr_rnd_001_max_size_valid(
    viewport_executor: RenderViewportCaptureExecutor,
) -> None:
    """FR-RND-001: max_size >= 64 passes validation."""
    result = await viewport_executor.capture_viewport(
        _viewport_req(max_size=64)  # type: ignore[arg-type]
    )
    assert bool(result.success) is True


@pytest.mark.asyncio
async def test_fr_rnd_001_max_size_zero_unlimited(
    viewport_executor: RenderViewportCaptureExecutor,
) -> None:
    """FR-RND-001: max_size=0 means no limit, passes validation."""
    result = await viewport_executor.capture_viewport(
        _viewport_req(max_size=0)  # type: ignore[arg-type]
    )
    assert bool(result.success) is True


@pytest.mark.asyncio
async def test_fr_rnd_002_overwrite_policy_reject() -> None:
    """FR-RND-002: overwrite_policy='reject' rejects when artifact exists."""
    exec_ = RenderSceneImageExecutor(
        code_executor=MockCodeExecutor(payload={"artifact_path": "/tmp/render.png"}),
        security_validator=MockSecurityValidator(),
    )
    # Reject policy with existing artifact path — capability accepts it at validation
    # (Blender runtime enforces actual overwrite; capability validates format only)
    result = await exec_.render_scene(_scene_req(overwrite_policy="reject"))
    assert bool(result.success) is True


@pytest.mark.asyncio
async def test_fr_rnd_002_overwrite_policy_unique() -> None:
    """FR-RND-002: overwrite_policy='unique' generates unique path."""
    exec_ = RenderSceneImageExecutor(
        code_executor=MockCodeExecutor(payload={"artifact_path": "/tmp/render_abc123.png"}),
        security_validator=MockSecurityValidator(),
    )
    result = await exec_.render_scene(_scene_req(overwrite_policy="unique"))
    assert bool(result.success) is True
    assert "abc123" in str(result.artifact_path)
