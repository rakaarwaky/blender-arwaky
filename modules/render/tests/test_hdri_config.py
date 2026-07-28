"""Tests for HdriConfigCapability — FR-RND-004: Configure HDRI Lighting.

Exercises strength validation, path security validation, asset acquisition fallback,
and gateway command execution. All dependencies mocked.
Run via pytest from repo root.
"""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from modules.render.src.capabilities_hdri_config import HdriConfigCapability


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


class MockAssetFeature:
    """Mock asset feature for HDRI acquisition."""

    def __init__(self, success: bool = True, file_path: str = "/tmp/mock_hdri.exr") -> None:
        self.success = success
        self.file_path = file_path
        self._downloads: list[dict] = []

    async def download_to_cache(
        self, provider: str, asset_id: str, asset_type: str, cache_dir: str
    ) -> dict:
        self._downloads.append({"provider": provider, "asset_id": asset_id})
        if self.success:
            return {"success": True, "file_path": self.file_path}
        return {"success": False, "message": "download failed"}


class MockGatewayClient:
    """Mock gateway for Blender command transport."""

    def __init__(self) -> None:
        self._commands: list[dict] = []

    async def execute_command(self, command: dict) -> dict:
        self._commands.append(command)
        return {"environment_name": "World", "success": True}


# ─── Helpers ────────────────────────────────────────────────────────────────


def _make_capability(
    gateway_fail: bool = False,
    security_validate: bool = True,
    asset_success: bool = True,
    asset_file: str = "/tmp/mock_hdri.exr",
) -> HdriConfigCapability:
    """Create HDRI capability with configurable mocks."""
    gw = MockGatewayClient()
    if gateway_fail:
        gw.execute_command = AsyncMock(side_effect=RuntimeError("gateway error"))
    sec = MockSecurityValidator(validate=security_validate)
    asset = MockAssetFeature(success=asset_success, file_path=asset_file)
    cap = HdriConfigCapability(
        gateway_client=gw,
        security_validator=sec,
        asset_feature=asset,
        config_getter=None,
    )
    return cap


@pytest.fixture
def hdri_capability() -> HdriConfigCapability:
    """HDRI capability with all dependencies mocked and file existing."""
    gw = MockGatewayClient()
    sec = MockSecurityValidator()
    asset = MockAssetFeature(success=False)  # file exists locally by default
    cap = HdriConfigCapability(
        gateway_client=gw,
        security_validator=sec,
        asset_feature=asset,
        config_getter=None,
    )
    return cap


# ─── FR-RND-004: Configure HDRI Lighting ──────────────────────────────────


@pytest.mark.asyncio
async def test_fr_rnd_004_configure_hdri_success(hdri_capability: HdriConfigCapability) -> None:
    """Test HDRI configuration with valid parameters returns success."""
    with patch.object(os.path, "exists", return_value=True):
        result = await hdri_capability.configure_hdri(
            hdri_file_path="/tmp/test_hdri.exr",
            strength=1.0,
            rotation=0.0,
            background_visible=True,
            overwrite_policy="replace",
        )
    assert result["success"] is True
    assert result["strength"] == 1.0
    assert result["rotation"] == 0.0
    assert "HDRI lighting configured" in result["message"]
    assert hdri_capability.gateway_client._commands[0]["type"] == "hdri_configure"


@pytest.mark.asyncio
async def test_fr_rnd_004_strength_out_of_range_too_low(
    hdri_capability: HdriConfigCapability,
) -> None:
    """Test HDRI strength below valid range (0.0)."""
    result = await hdri_capability.configure_hdri(
        hdri_file_path="/tmp/test.exr",
        strength=-1.0,
    )
    assert result["success"] is False
    assert result["error"] == "invalid_parameter"
    assert "out of range" in result["message"]


@pytest.mark.asyncio
async def test_fr_rnd_004_strength_out_of_range_too_high(
    hdri_capability: HdriConfigCapability,
) -> None:
    """Test HDRI strength above valid range (10.0)."""
    result = await hdri_capability.configure_hdri(
        hdri_file_path="/tmp/test.exr",
        strength=11.0,
    )
    assert result["success"] is False
    assert result["error"] == "invalid_parameter"
    assert "out of range" in result["message"]


@pytest.mark.asyncio
async def test_fr_rnd_004_strength_at_boundary_zero(hdri_capability: HdriConfigCapability) -> None:
    """Test HDRI strength at lower boundary (0.0) — valid."""
    with patch.object(os.path, "exists", return_value=True):
        result = await hdri_capability.configure_hdri(
            hdri_file_path="/tmp/test.exr",
            strength=0.0,
        )
    assert result["success"] is True


@pytest.mark.asyncio
async def test_fr_rnd_004_strength_at_boundary_ten(hdri_capability: HdriConfigCapability) -> None:
    """Test HDRI strength at upper boundary (10.0) — valid."""
    with patch.object(os.path, "exists", return_value=True):
        result = await hdri_capability.configure_hdri(
            hdri_file_path="/tmp/test.exr",
            strength=10.0,
        )
    assert result["success"] is True


@pytest.mark.asyncio
async def test_fr_rnd_004_rotation_normalized(hdri_capability: HdriConfigCapability) -> None:
    """Test HDRI rotation normalized to [0, 360)."""
    with patch.object(os.path, "exists", return_value=True):
        result = await hdri_capability.configure_hdri(
            hdri_file_path="/tmp/test.exr",
            strength=1.0,
            rotation=360.0,
        )
    assert result["success"] is True
    assert result["rotation"] == 0.0


@pytest.mark.asyncio
async def test_fr_rnd_004_rotation_normalized_negative(hdri_capability: HdriConfigCapability) -> None:
    """Test negative rotation normalized."""
    with patch.object(os.path, "exists", return_value=True):
        result = await hdri_capability.configure_hdri(
            hdri_file_path="/tmp/test.exr",
            strength=1.0,
            rotation=-90.0,
        )
    assert result["success"] is True
    assert result["rotation"] == 270.0


@pytest.mark.asyncio
async def test_fr_rnd_004_security_validation_failure(
    hdri_capability: HdriConfigCapability,
) -> None:
    """Test HDRI path validation failure via security policy."""
    sec = MockSecurityValidator(validate=False)
    hdri_capability.security_validator = sec

    with patch.object(os.path, "exists", return_value=True):
        result = await hdri_capability.configure_hdri(
            hdri_file_path="/tmp/test.exr",
            strength=1.0,
        )
    assert result["success"] is False
    assert result["error"] == "security_violation"


@pytest.mark.asyncio
async def test_fr_rnd_004_hdri_file_not_found_asset_fallback(
    hdri_capability: HdriConfigCapability,
) -> None:
    """Test HDRI file not found locally — asset feature fallback."""
    asset = MockAssetFeature(success=False)
    hdri_capability.asset_feature = asset

    with patch("os.path.exists", return_value=False):
        result = await hdri_capability.configure_hdri(
            hdri_file_path="/tmp/nonexistent.exr",
            strength=1.0,
        )
    assert result["success"] is False
    assert result["error"] == "asset_not_found"


@pytest.mark.asyncio
async def test_fr_rnd_004_hdri_file_not_found_asset_acquisition_success(
    hdri_capability: HdriConfigCapability,
) -> None:
    """Test HDRI file not found — asset feature successfully acquires it."""
    asset = MockAssetFeature(success=True, file_path="/tmp/acquired.exr")
    gw = MockGatewayClient()
    sec = MockSecurityValidator()
    cap = HdriConfigCapability(
        gateway_client=gw,
        security_validator=sec,
        asset_feature=asset,
    )

    with patch("os.path.exists", side_effect=lambda p: p == "/tmp/acquired.exr"):
        result = await cap.configure_hdri(
            hdri_file_path="/tmp/nonexistent.exr",
            strength=1.0,
        )
    assert result["success"] is True
    assert asset._downloads[0]["provider"] == "polyhaven"


@pytest.mark.asyncio
async def test_fr_rnd_004_background_visible_false(
    hdri_capability: HdriConfigCapability,
) -> None:
    """Test HDRI background visibility set to False (lighting only)."""
    with patch.object(os.path, "exists", return_value=True):
        result = await hdri_capability.configure_hdri(
            hdri_file_path="/tmp/test.exr",
            strength=1.0,
            background_visible=False,
        )
    assert result["success"] is True
    cmd = hdri_capability.gateway_client._commands[0]
    assert cmd["background_visible"] is False


@pytest.mark.asyncio
async def test_fr_rnd_004_overwrite_policy_reject(
    hdri_capability: HdriConfigCapability,
) -> None:
    """Test overwrite policy set to reject."""
    with patch.object(os.path, "exists", return_value=True):
        result = await hdri_capability.configure_hdri(
            hdri_file_path="/tmp/test.exr",
            strength=1.0,
            overwrite_policy="reject",
        )
    assert result["success"] is True
    cmd = hdri_capability.gateway_client._commands[0]
    assert cmd["overwrite_policy"] == "reject"


@pytest.mark.asyncio
async def test_fr_rnd_004_gateway_execution_error(
    hdri_capability: HdriConfigCapability,
) -> None:
    """Test gateway execution failure."""
    gw = MagicMock()
    gw.execute_command = AsyncMock(side_effect=RuntimeError("gateway error"))
    hdri_capability.gateway_client = gw

    with patch.object(os.path, "exists", return_value=True):
        result = await hdri_capability.configure_hdri(
            hdri_file_path="/tmp/test.exr",
            strength=1.0,
        )
    assert result["success"] is False
    assert "gateway error" in result["message"]


@pytest.mark.asyncio
async def test_fr_rnd_004_default_strength_is_one(
    hdri_capability: HdriConfigCapability,
) -> None:
    """Test default strength of 1.0."""
    with patch.object(os.path, "exists", return_value=True):
        await hdri_capability.configure_hdri(hdri_file_path="/tmp/test.exr")
    assert hdri_capability.gateway_client._commands[0]["strength"] == 1.0


@pytest.mark.asyncio
async def test_fr_rnd_004_default_rotation_is_zero(
    hdri_capability: HdriConfigCapability,
) -> None:
    """Test default rotation of 0.0."""
    with patch.object(os.path, "exists", return_value=True):
        await hdri_capability.configure_hdri(hdri_file_path="/tmp/test.exr")
    assert hdri_capability.gateway_client._commands[0]["rotation"] == 0.0


@pytest.mark.asyncio
async def test_fr_rnd_004_no_gateway_no_security_validator(
    hdri_capability: HdriConfigCapability,
) -> None:
    """Test with no gateway client — gateway must be available."""
    hdri_capability.gateway_client = None

    result = await hdri_capability.configure_hdri(
        hdri_file_path="/tmp/test.exr",
        strength=1.0,
    )
    assert result["success"] is False


# ─── Edge Cases ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_hdri_strength_float_precision(hdri_capability: HdriConfigCapability) -> None:
    """Test strength with float precision."""
    with patch.object(os.path, "exists", return_value=True):
        result = await hdri_capability.configure_hdri(
            hdri_file_path="/tmp/test.exr",
            strength=0.75,
        )
    assert result["success"] is True
    assert result["strength"] == 0.75


@pytest.mark.asyncio
async def test_hdri_rotation_large_value_normalized(hdri_capability: HdriConfigCapability) -> None:
    """Test rotation > 360 normalized."""
    with patch.object(os.path, "exists", return_value=True):
        result = await hdri_capability.configure_hdri(
            hdri_file_path="/tmp/test.exr",
            strength=1.0,
            rotation=720.0,
        )
    assert result["success"] is True
    assert result["rotation"] == 0.0


@pytest.mark.asyncio
async def test_hdri_no_dependencies_at_all(hdri_capability: HdriConfigCapability) -> None:
    """Test with all dependencies set to None."""
    hdri_capability.gateway_client = None
    hdri_capability.security_validator = None
    hdri_capability.asset_feature = None

    result = await hdri_capability.configure_hdri(
        hdri_file_path="/tmp/test.exr",
        strength=1.0,
    )
    assert result["success"] is False  # No gateway to execute
