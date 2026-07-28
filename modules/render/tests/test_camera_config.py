"""Tests for CameraConfigCapability — FR-RND-003: Configure Camera.

Exercises lens validation, gateway command execution, missing camera creation policy,
and depth of field configuration. All dependencies mocked.
Run via pytest from repo root.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from modules.render.src.capabilities_camera_config import CameraConfigCapability


# ─── Mocks ──────────────────────────────────────────────────────────────────


class MockGatewayClient:
    """Mock gateway for Blender command transport."""

    def __init__(self) -> None:
        self._commands: list[dict] = []

    async def execute_command(self, command: dict) -> dict:
        self._commands.append(command)
        return {"camera_id": "Camera.001", "is_active": True, "current_lens": 50.0, "dof_enabled": False}


# ─── Helpers ────────────────────────────────────────────────────────────────


@pytest.fixture
def camera_capability() -> CameraConfigCapability:
    """Camera capability with gateway mocked."""
    gw = MockGatewayClient()
    cap = CameraConfigCapability(
        gateway_client=gw,
        security_validator=None,
        config_getter=None,
    )
    return cap


# ─── FR-RND-003: Configure Camera ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_fr_rnd_003_configure_camera_success(camera_capability: CameraConfigCapability) -> None:
    """Test camera configuration with valid parameters returns success."""
    result = await camera_capability.configure_camera(
        lens=50.0,
        set_active=True,
    )
    assert result["success"] is True
    assert result["lens"] == 50.0
    assert result["active_status"] is True
    assert "configured successfully" in result["message"]


@pytest.mark.asyncio
async def test_fr_rnd_003_lens_out_of_range_too_small(camera_capability: CameraConfigCapability) -> None:
    """Test lens below valid range (10mm)."""
    result = await camera_capability.configure_camera(lens=5.0)
    assert result["success"] is False
    assert result["error"] == "invalid_parameter"
    assert "out of range" in result["message"]


@pytest.mark.asyncio
async def test_fr_rnd_003_lens_out_of_range_too_large(camera_capability: CameraConfigCapability) -> None:
    """Test lens above valid range (300mm)."""
    result = await camera_capability.configure_camera(lens=400.0)
    assert result["success"] is False
    assert result["error"] == "invalid_parameter"
    assert "out of range" in result["message"]


@pytest.mark.asyncio
async def test_fr_rnd_003_lens_at_boundary_min(camera_capability: CameraConfigCapability) -> None:
    """Test lens at lower boundary (10mm) — valid."""
    result = await camera_capability.configure_camera(lens=10.0)
    assert result["success"] is True


@pytest.mark.asyncio
async def test_fr_rnd_003_lens_at_boundary_max(camera_capability: CameraConfigCapability) -> None:
    """Test lens at upper boundary (300mm) — valid."""
    result = await camera_capability.configure_camera(lens=300.0)
    assert result["success"] is True


@pytest.mark.asyncio
async def test_fr_rnd_003_no_lens_provided(camera_capability: CameraConfigCapability) -> None:
    """Test camera configuration without specifying lens."""
    result = await camera_capability.configure_camera()
    assert result["success"] is True


@pytest.mark.asyncio
async def test_fr_rnd_003_depth_of_field_applied(
    camera_capability: CameraConfigCapability,
) -> None:
    """Test depth of field settings applied."""
    result = await camera_capability.configure_camera(
        lens=50.0,
        depth_of_field={"enable": True, "focus_distance": 2.0, "aperture": 1.8},
    )
    assert result["success"] is True
    cmd = camera_capability.gateway_client._commands[0]
    assert "depth_of_field" in cmd
    assert cmd["depth_of_field"]["enable"] is True


@pytest.mark.asyncio
async def test_fr_rnd_003_set_active_true(camera_capability: CameraConfigCapability) -> None:
    """Test camera designated as active."""
    await camera_capability.configure_camera(lens=50.0, set_active=True)
    cmd = camera_capability.gateway_client._commands[0]
    assert cmd["set_active"] is True


@pytest.mark.asyncio
async def test_fr_rnd_003_set_active_false(camera_capability: CameraConfigCapability) -> None:
    """Test camera not designated as active."""
    await camera_capability.configure_camera(lens=50.0, set_active=False)
    cmd = camera_capability.gateway_client._commands[0]
    assert cmd["set_active"] is False


@pytest.mark.asyncio
async def test_fr_rnd_003_framing_target(camera_capability: CameraConfigCapability) -> None:
    """Test framing target specified."""
    await camera_capability.configure_camera(lens=50.0, framing_target="TargetObj")
    cmd = camera_capability.gateway_client._commands[0]
    assert cmd["framing_target"] == "TargetObj"


@pytest.mark.asyncio
async def test_fr_rnd_003_create_if_missing_true(camera_capability: CameraConfigCapability) -> None:
    """Test create_if_missing policy enabled."""
    await camera_capability.configure_camera(lens=50.0, create_if_missing=True)
    cmd = camera_capability.gateway_client._commands[0]
    assert cmd["create_if_missing"] is True


@pytest.mark.asyncio
async def test_fr_rnd_003_create_if_missing_false(camera_capability: CameraConfigCapability) -> None:
    """Test create_if_missing policy disabled."""
    await camera_capability.configure_camera(lens=50.0, create_if_missing=False)
    cmd = camera_capability.gateway_client._commands[0]
    assert cmd["create_if_missing"] is False


@pytest.mark.asyncio
async def test_fr_rnd_003_gateway_failure(camera_capability: CameraConfigCapability) -> None:
    """Test gateway execution failure."""
    gw = MagicMock()
    gw.execute_command = AsyncMock(side_effect=RuntimeError("gateway error"))
    camera_capability.gateway_client = gw

    result = await camera_capability.configure_camera(lens=50.0)
    assert result["success"] is False
    assert "gateway error" in result["message"]


@pytest.mark.asyncio
async def test_fr_rnd_003_no_gateway(camera_capability: CameraConfigCapability) -> None:
    """Test with no gateway client."""
    camera_capability.gateway_client = None

    result = await camera_capability.configure_camera(lens=50.0)
    assert result["success"] is False


# ─── Edge Cases ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_camera_lens_zero(camera_capability: CameraConfigCapability) -> None:
    """Test lens at 0mm — out of range."""
    result = await camera_capability.configure_camera(lens=0.0)
    assert result["success"] is False


@pytest.mark.asyncio
async def test_camera_negative_lens(camera_capability: CameraConfigCapability) -> None:
    """Test negative lens value."""
    result = await camera_capability.configure_camera(lens=-50.0)
    assert result["success"] is False


@pytest.mark.asyncio
async def test_camera_id_specified(camera_capability: CameraConfigCapability) -> None:
    """Test with explicit camera ID."""
    await camera_capability.configure_camera(
        camera_id="Camera.002", lens=85.0, set_active=True
    )
    cmd = camera_capability.gateway_client._commands[0]
    assert cmd["camera_id"] == "Camera.002"


@pytest.mark.asyncio
async def test_camera_command_type(camera_capability: CameraConfigCapability) -> None:
    """Test command type is camera_configure."""
    await camera_capability.configure_camera(lens=50.0)
    cmd = camera_capability.gateway_client._commands[0]
    assert cmd["type"] == "camera_configure"
