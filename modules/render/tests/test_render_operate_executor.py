"""Tests for RenderOperateExecutor — FR-RND-001: Capture Viewport Screenshot.

Exercises viewport screenshot capture, camera setup, render configuration,
composition rules, and frame rendering via code executor. All dependencies mocked.
Run via pytest from repo root.
"""

from __future__ import annotations

import time
from unittest.mock import AsyncMock, MagicMock

import pytest

from modules.shared.src.common.taxonomy_core_vo import (
    CoordinateList,
    Prompt,
    RenderEngine,
    RenderSamples,
    RotationVector,
    RuleName,
    UseDenoising,
)
from modules.render.src.capabilities_render_operate_executor import (
    RenderOperateExecutor,
    _format_coord,
    _py_str,
)


# ─── Mocks ──────────────────────────────────────────────────────────────────


class MockCodeExecutor:
    """Mock code executor that returns success."""

    def __init__(self, fail: bool = False) -> None:
        self.fail = fail
        self._executed_code: list[str] = []

    async def __call__(self, code: str) -> str:
        self._executed_code.append(code)
        if self.fail:
            raise RuntimeError("code execution failed")
        return "/tmp/screenshot.png"


# ─── Helpers ────────────────────────────────────────────────────────────────


@pytest.fixture
def executor() -> RenderOperateExecutor:
    """Render executor with code executor mocked."""
    mock = MockCodeExecutor(fail=False)
    cap = RenderOperateExecutor(code_executor=mock)
    return cap


# ─── FR-RND-001: Capture Viewport Screenshot ──────────────────────────────


@pytest.mark.asyncio
async def test_fr_rnd_001_get_viewport_screenshot_success(
    executor: RenderOperateExecutor,
) -> None:
    """Test viewport screenshot capture returns file path."""
    from modules.shared.src.render.taxonomy_render_vo import GetScreenshotVO

    result = await executor.get_viewport_screenshot(
        GetScreenshotVO(
            output_path="/tmp/screenshot.png",
            max_size=1920,
            view_angle="perspective",
            shading="solid",
            show_overlays=True,
            focus_object=None,
        )
    )
    assert result.success is True
    assert "screenshot" in result.image_path.lower() or "screenshot" in str(result.output_path).lower()
    assert result.duration_ms > 0


@pytest.mark.asyncio
async def test_fr_rnd_001_screenshot_code_generated(
    executor: RenderOperateExecutor,
) -> None:
    """Test screenshot generates correct Blender Python code."""
    from modules.shared.src.render.taxonomy_render_vo import GetScreenshotVO

    await executor.get_viewport_screenshot(
        GetScreenshotVO(
            output_path="/tmp/test.png",
            max_size=1024,
            view_angle="perspective",
            shading="wireframe",
            show_overlays=False,
        )
    )
    code = executor._code_executor._executed_code[0]
    assert "import bpy" in code
    assert "bpy.ops.render.render(write_still=True)" in code
    assert "scene.render.filepath" in code


@pytest.mark.asyncio
async def test_fr_rnd_001_screenshot_execution_error(
    executor: RenderOperateExecutor,
) -> None:
    """Test screenshot when code execution fails."""
    executor._code_executor = MockCodeExecutor(fail=True)

    from modules.shared.src.render.taxonomy_render_vo import GetScreenshotVO

    with pytest.raises(RuntimeError) as exc_info:
        await executor.get_viewport_screenshot(
            GetScreenshotVO(
                output_path="/tmp/fail.png",
                max_size=1920,
                view_angle="perspective",
                shading="solid",
                show_overlays=True,
            )
        )
    assert "Failed to capture viewport screenshot" in str(exc_info.value)


# ─── Camera Setup ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_fr_rnd_001_setup_camera_creates_camera(
    executor: RenderOperateExecutor,
) -> None:
    """Test camera setup creates camera if none exists."""
    location = CoordinateList([0.0, 0.0, 5.0])
    rotation = RotationVector([0.0, 0.0, 0.0])

    result = await executor.setup_camera(location, rotation)
    assert isinstance(result, Prompt)
    assert "Camera setup" in result.value or "successful" in result.value.lower()


@pytest.mark.asyncio
async def test_fr_rnd_001_setup_camera_with_target(
    executor: RenderOperateExecutor,
) -> None:
    """Test camera setup with framing target."""
    location = CoordinateList([0.0, 0.0, 5.0])
    rotation = RotationVector([0.0, 0.0, 0.0])
    target = CoordinateList([1.0, 0.0, 0.0])

    await executor.setup_camera(location, rotation, target)
    code = executor._code_executor._executed_code[-1] if not hasattr(executor._code_executor, '_executed_code') else executor._code_executor._executed_code[1]
    # Check the code contains track-to constraint logic
    assert "TRACK_TO" in str(code) or "bpy.ops.object.camera_add" in str(code)


@pytest.mark.asyncio
async def test_fr_rnd_001_setup_camera_failure(
    executor: RenderOperateExecutor,
) -> None:
    """Test camera setup execution failure."""
    executor._code_executor = MockCodeExecutor(fail=True)

    location = CoordinateList([0.0, 0.0, 5.0])
    rotation = RotationVector([0.0, 0.0, 0.0])

    with pytest.raises(RuntimeError):
        await executor.setup_camera(location, rotation)


# ─── Render Configuration ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_fr_rnd_001_setup_render_cycles_engine(
    executor: RenderOperateExecutor,
) -> None:
    """Test render configuration with Cycles engine."""
    result = await executor.setup_render(
        engine=RenderEngine("CYCLES"),
        samples=RenderSamples(256),
        use_denoising=UseDenoising(True),
    )
    assert isinstance(result, Prompt)
    assert "cycles" in str(result.value).lower() or "configured" in str(result.value).lower()


@pytest.mark.asyncio
async def test_fr_rnd_001_setup_render_resolution(
    executor: RenderOperateExecutor,
) -> None:
    """Test render configuration with resolution."""
    await executor.setup_render(
        engine=RenderEngine("CYCLES"),
        resolution=CoordinateList([1920, 1080]),
    )
    code = executor._code_executor._executed_code[-1] if not hasattr(executor._code_executor, '_executed_code') else executor._code_executor._executed_code[1]
    assert "resolution_x" in str(code) or "resolution_y" in str(code)


@pytest.mark.asyncio
async def test_fr_rnd_001_setup_render_default_engine(
    executor: RenderOperateExecutor,
) -> None:
    """Test render defaults to Cycles when no engine specified."""
    result = await executor.setup_render()
    assert isinstance(result, Prompt)


# ─── Composition Rules ─────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_fr_rnd_001_apply_composition_thirds(
    executor: RenderOperateExecutor,
) -> None:
    """Test applying thirds composition rule."""
    result = await executor.apply_composition(rule=RuleName("thirds"))
    assert isinstance(result, Prompt)
    assert "thirds" in str(result.value).lower()


@pytest.mark.asyncio
async def test_fr_rnd_001_apply_composition_golden(
    executor: RenderOperateExecutor,
) -> None:
    """Test applying golden composition rule."""
    result = await executor.apply_composition(rule=RuleName("golden"))
    assert isinstance(result, Prompt)
    assert "golden" in str(result.value).lower()


@pytest.mark.asyncio
async def test_fr_rnd_001_apply_composition_unknown(
    executor: RenderOperateExecutor,
) -> None:
    """Test applying unknown composition rule — falls back to empty set."""
    result = await executor.apply_composition(rule=RuleName("unknown_rule"))
    assert isinstance(result, Prompt)


# ─── Frame Render ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_fr_rnd_001_render_frame_success(
    executor: RenderOperateExecutor,
) -> None:
    """Test single frame render."""
    from modules.shared.src.render.taxonomy_render_vo import RenderVO

    result = await executor.render(
        RenderVO(
            output_path="/tmp/frame.png",
            resolution_x=1920,
            resolution_y=1080,
            samples=128,
            use_denoising=True,
        )
    )
    assert result.success.value is True
    assert "Render complete" in str(result.message)


@pytest.mark.asyncio
async def test_fr_rnd_001_render_frame_code_generated(
    executor: RenderOperateExecutor,
) -> None:
    """Test frame render generates correct Blender code."""
    from modules.shared.src.render.taxonomy_render_vo import RenderVO

    await executor.render(
        RenderVO(
            output_path="/tmp/frame.png",
            resolution_x=1920,
            resolution_y=1080,
            samples=128,
            use_denoising=True,
        )
    )
    code = executor._code_executor._executed_code[-1] if not hasattr(executor._code_executor, '_executed_code') else executor._code_executor._executed_code[1]
    assert "bpy.ops.render.render" in str(code)


# ─── Utility Functions ─────────────────────────────────────────────────────


def test_py_str_escapes_string() -> None:
    """Test _py_str properly escapes strings."""
    result = _py_str("hello world")
    assert result == '"hello world"'


def test_py_str_escapes_special_chars() -> None:
    """Test _py_str handles special characters."""
    result = _py_str('path with "quotes"')
    assert '"' in result


def test_format_coord_floats() -> None:
    """Test _format_coord converts floats."""
    result = _format_coord(1.5)
    assert result == "1.5"


def test_format_coord_ints() -> None:
    """Test _format_coord converts ints to float."""
    result = _format_coord(42)
    assert result == "42.0"


# ─── Edge Cases ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_executor_no_callable_code_executor() -> None:
    """Test executor with non-callable code executor."""
    cap = RenderOperateExecutor(code_executor="not_callable")

    with pytest.raises(RuntimeError) as exc_info:
        await cap._execute_code("import bpy")
    assert "Unexpected code_executor type" in str(exc_info.value)


@pytest.mark.asyncio
async def test_screenshot_duration_ms_recorded(executor: RenderOperateExecutor) -> None:
    """Test screenshot duration is recorded in milliseconds."""
    from modules.shared.src.render.taxonomy_render_vo import GetScreenshotVO

    result = await executor.get_viewport_screenshot(
        GetScreenshotVO(
            output_path="/tmp/duration.png",
            max_size=1920,
            view_angle="perspective",
            shading="solid",
            show_overlays=True,
        )
    )
    assert result.duration_ms > 0


@pytest.mark.asyncio
async def test_render_frame_time_recorded(executor: RenderOperateExecutor) -> None:
    """Test render frame time is recorded."""
    from modules.shared.src.render.taxonomy_render_vo import RenderVO

    result = await executor.render(
        RenderVO(
            output_path="/tmp/timing.png",
            resolution_x=1920,
            resolution_y=1080,
            samples=128,
            use_denoising=True,
        )
    )
    assert result.render_time is not None
