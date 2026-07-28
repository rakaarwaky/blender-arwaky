"""Tests for RenderCapability — FR-RND-002: Render Scene Image.

Exercises security path validation, background render submission via job feature,
synchronous render execution, render statistics, and timeout handling.
All dependencies mocked.
Run via pytest from repo root.
"""

from __future__ import annotations

import time
from unittest.mock import AsyncMock, MagicMock

import pytest

from modules.render.src.capabilities_render_operate import RenderCapability


# ─── Mocks ──────────────────────────────────────────────────────────────────


class MockSecurityValidator:
    """Mock security policy validator."""

    def __init__(self, validate: bool = True) -> None:
        self.validate = validate
        self._validated_paths: list[str] = []

    async def validate_path(self, path: str, mode: str) -> None:
        if not self.validate:
            raise PermissionError("path denied")
        self._validated_paths.append(path)


class MockJobScheduler:
    """Mock job feature for background render coordination."""

    def __init__(self, capacity_exhausted: bool = False) -> None:
        self.capacity_exhausted = capacity_exhausted
        self._submitted: list[dict] = []

    async def submit_render(self, **kwargs: object) -> str:
        if self.capacity_exhausted:
            raise RuntimeError("capacity exceeded")
        self._submitted.append(kwargs)
        return f"task-render-{int(time.time())}"


class MockGatewayClient:
    """Mock gateway for Blender command transport."""

    def __init__(self, fail: bool = False) -> None:
        self.fail = fail
        self._commands: list[dict] = []

    async def execute_command(self, command: dict) -> dict:
        self._commands.append(command)
        if self.fail:
            raise RuntimeError("render failed")
        return {"success": True, "file_path": "/tmp/render_output.png"}


# ─── Helpers ────────────────────────────────────────────────────────────────


@pytest.fixture
def render_capability() -> RenderCapability:
    """Render capability with all dependencies mocked."""
    gw = MockGatewayClient(fail=False)
    sec = MockSecurityValidator()
    job = MockJobScheduler(capacity_exhausted=False)
    cap = RenderCapability(
        gateway_client=gw,
        security_validator=sec,
        job_scheduler=job,
        config_getter=None,
    )
    return cap


# ─── FR-RND-002: Render Scene Image — Synchronous ─────────────────────────


@pytest.mark.asyncio
async def test_fr_rnd_002_render_scene_success(
    render_capability: RenderCapability,
) -> None:
    """Test synchronous render returns success with statistics."""
    result = await render_capability.render_scene(
        output_path="/tmp/render_output.png",
        resolution_width=1920,
        resolution_height=1080,
        samples=128,
        use_denoising=True,
    )
    assert result["success"] is True
    assert result["file_path"] == "/tmp/render_output.png"
    assert result["engine"] == "cycles"
    assert result["denoising"] is True
    assert "Render completed" in result["message"]
    assert result["resolution"] == (1920, 1080)


@pytest.mark.asyncio
async def test_fr_rnd_002_security_validation_failure(
    render_capability: RenderCapability,
) -> None:
    """Test output path validation failure via security policy."""
    sec = MockSecurityValidator(validate=False)
    render_capability.security_validator = sec

    result = await render_capability.render_scene(
        output_path="/tmp/render_output.png",
    )
    assert result["success"] is False
    assert result["error"] == "security_violation"
    assert result["file_path"] is None


@pytest.mark.asyncio
async def test_fr_rnd_002_default_output_path(
    render_capability: RenderCapability,
) -> None:
    """Test default output path when none specified."""
    result = await render_capability.render_scene()
    assert result["success"] is True
    assert result["file_path"] == "render_output.png"


@pytest.mark.asyncio
async def test_fr_rnd_002_render_engine_eevee(
    render_capability: RenderCapability,
) -> None:
    """Test render with Eevee engine."""
    from modules.shared.src.common.taxonomy_core_vo import RenderEngine

    result = await render_capability.render_scene(
        output_path="/tmp/eevee.png",
        render_engine=RenderEngine("EEVEE"),
    )
    assert result["success"] is True
    assert result["engine"] == "EEVEE"


@pytest.mark.asyncio
async def test_fr_rnd_002_no_denoising(
    render_capability: RenderCapability,
) -> None:
    """Test render without denoising."""
    result = await render_capability.render_scene(
        output_path="/tmp/no_denoise.png",
        use_denoising=False,
    )
    assert result["success"] is True
    assert result["denoising"] is False


@pytest.mark.asyncio
async def test_fr_rnd_002_gateway_failure(
    render_capability: RenderCapability,
) -> None:
    """Test gateway execution failure during render."""
    gw = MockGatewayClient(fail=True)
    render_capability.gateway_client = gw

    result = await render_capability.render_scene(
        output_path="/tmp/fail.png",
    )
    assert result["success"] is False
    assert "Render failed" in result["message"]


# ─── Background Render Submission ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_fr_rnd_002_background_render_submitted(
    render_capability: RenderCapability,
) -> None:
    """Test long-running render submitted as background job."""
    job = MockJobScheduler(capacity_exhausted=False)
    gw = MockGatewayClient(fail=False)
    sec = MockSecurityValidator()
    cap = RenderCapability(
        gateway_client=gw,
        security_validator=sec,
        job_scheduler=job,
    )

    # High resolution triggers background render (>30s estimate)
    result = await cap.render_scene(
        output_path="/tmp/big.png",
        resolution_width=8192,
        resolution_height=4320,
        samples=4096,
        background=True,
    )
    assert result["success"] is True
    assert "task_ref" in result
    assert result["file_path"] is None  # Background doesn't return file path directly
    assert "Background render submitted" in result["message"]


@pytest.mark.asyncio
async def test_fr_rnd_002_no_job_scheduler_background(
    render_capability: RenderCapability,
) -> None:
    """Test background render when no job scheduler available — falls back to sync."""
    render_capability.job_scheduler = None

    result = await render_capability.render_scene(
        output_path="/tmp/sync.png",
        resolution_width=8192,
        resolution_height=4320,
        background=True,
    )
    assert result["success"] is True  # Falls back to sync render
    assert "file_path" in result


@pytest.mark.asyncio
async def test_fr_rnd_002_job_capacity_exhausted(
    render_capability: RenderCapability,
) -> None:
    """Test background render when job capacity is exhausted."""
    job = MockJobScheduler(capacity_exhausted=True)
    gw = MockGatewayClient(fail=False)
    sec = MockSecurityValidator()
    cap = RenderCapability(
        gateway_client=gw,
        security_validator=sec,
        job_scheduler=job,
    )

    result = await cap.render_scene(
        output_path="/tmp/overflow.png",
        resolution_width=8192,
        resolution_height=4320,
        background=True,
    )
    assert result["success"] is False
    assert result["error"] == "capacity_error"


# ─── Render Statistics ─────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_fr_rnd_002_render_time_recorded(
    render_capability: RenderCapability,
) -> None:
    """Test render time is recorded in result."""
    result = await render_capability.render_scene(output_path="/tmp/stats.png")
    assert "render_time_ms" in result
    assert result["render_time_ms"] > 0


@pytest.mark.asyncio
async def test_fr_rnd_002_resolution_recorded(
    render_capability: RenderCapability,
) -> None:
    """Test resolution is recorded in result."""
    result = await render_capability.render_scene(
        output_path="/tmp/res.png",
        resolution_width=3840,
        resolution_height=2160,
    )
    assert result["resolution"] == (3840, 2160)


# ─── Edge Cases ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_render_no_security_validator(
    render_capability: RenderCapability,
) -> None:
    """Test render without security validator — path validation skipped."""
    render_capability.security_validator = None

    result = await render_capability.render_scene(output_path="/tmp/no_sec.png")
    assert result["success"] is True


@pytest.mark.asyncio
async def test_render_custom_samples(
    render_capability: RenderCapability,
) -> None:
    """Test render with custom sample count."""
    result = await render_capability.render_scene(
        output_path="/tmp/custom.png",
        samples=2048,
    )
    assert result["success"] is True
    assert result["samples"] == 2048


@pytest.mark.asyncio
async def test_render_overwrite_policy(
    render_capability: RenderCapability,
) -> None:
    """Test render with overwrite policy."""
    result = await render_capability.render_scene(
        output_path="/tmp/overwrite.png",
        overwrite_policy="overwrite",
    )
    assert result["success"] is True


@pytest.mark.asyncio
async def test_render_estimate_duration_high_resolution(
    render_capability: RenderCapability,
) -> None:
    """Test estimated render duration for high resolution."""
    duration = render_capability._estimate_render_duration(8192, 4320, 4096, None)
    assert duration > 30  # Should trigger background


@pytest.mark.asyncio
async def test_render_estimate_duration_low_resolution(
    render_capability: RenderCapability,
) -> None:
    """Test estimated render duration for low resolution."""
    duration = render_capability._estimate_render_duration(640, 480, 64, None)
    assert duration < 30  # Should stay synchronous
