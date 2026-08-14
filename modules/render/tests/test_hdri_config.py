"""Tests for RenderHdriConfigExecutor — FR-RND-004: Configure HDRI Lighting.

Exercises strength/path/overwrite validation, security delegation (optional), rotation normalization,
Blender code generation, success path with mocked code executor, and execution failure.
"""

from __future__ import annotations

import json

import pytest

from modules.render.src.capabilities_render_hdri_config_executor import (
    RenderHdriConfigExecutor,
)
from modules.shared.src.common.taxonomy_core_vo import (
    FilePath,
    LightStrength,
    Prompt,
)
from modules.shared.src.render.taxonomy_render_constant import (
    MAX_HDRI_STRENGTH,
    MIN_HDRI_STRENGTH,
)
from modules.shared.src.render.taxonomy_render_vo import HdriConfigVO, RotationDegrees
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
def executor() -> RenderHdriConfigExecutor:
    return RenderHdriConfigExecutor(
        code_executor=MockCodeExecutor(
            payload={
                "environment_ref": "World",
                "applied_strength": 1.0,
                "applied_rotation": 0.0,
            }
        ),
        security_validator=MockSecurityValidator(),
    )


def _req(**kwargs: object) -> HdriConfigVO:
    base = dict(
        hdri_path=FilePath("/tmp/test.exr"),
        strength=LightStrength(1.0),
        rotation=RotationDegrees(0.0),
        overwrite_policy="overwrite",
    )
    base.update(kwargs)
    return HdriConfigVO(**base)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_fr_rnd_004_configure_hdri_success(
    executor: RenderHdriConfigExecutor,
) -> None:
    result = await executor.configure_hdri(_req())
    assert bool(result.success) is True
    assert str(result.environment_ref) == "World"
    assert float(result.applied_strength) == 1.0


@pytest.mark.asyncio
async def test_fr_rnd_004_strength_too_low(
    executor: RenderHdriConfigExecutor,
) -> None:
    result = await executor.configure_hdri(_req(strength=LightStrength(-1.0)))
    assert bool(result.success) is False


@pytest.mark.asyncio
async def test_fr_rnd_004_strength_too_high(
    executor: RenderHdriConfigExecutor,
) -> None:
    result = await executor.configure_hdri(_req(strength=LightStrength(11.0)))
    assert bool(result.success) is False


@pytest.mark.asyncio
async def test_fr_rnd_004_strength_boundary_min(
    executor: RenderHdriConfigExecutor,
) -> None:
    result = await executor.configure_hdri(_req(strength=LightStrength(MIN_HDRI_STRENGTH)))
    assert bool(result.success) is True


@pytest.mark.asyncio
async def test_fr_rnd_004_strength_boundary_max(
    executor: RenderHdriConfigExecutor,
) -> None:
    result = await executor.configure_hdri(_req(strength=LightStrength(MAX_HDRI_STRENGTH)))
    assert bool(result.success) is True


@pytest.mark.asyncio
async def test_fr_rnd_004_missing_path(
    executor: RenderHdriConfigExecutor,
) -> None:
    result = await executor.configure_hdri(_req(hdri_path=FilePath("")))
    assert bool(result.success) is False


@pytest.mark.asyncio
async def test_fr_rnd_004_invalid_overwrite_policy(
    executor: RenderHdriConfigExecutor,
) -> None:
    result = await executor.configure_hdri(_req(overwrite_policy="banana"))
    assert bool(result.success) is False


@pytest.mark.asyncio
async def test_fr_rnd_004_rotation_normalized_360(
    executor: RenderHdriConfigExecutor,
) -> None:
    await executor.configure_hdri(_req(rotation=RotationDegrees(360.0)))
    code = str(executor._code_executor.captured_code)
    assert "rotation = 0.0" in code


@pytest.mark.asyncio
async def test_fr_rnd_004_rotation_normalized_negative(
    executor: RenderHdriConfigExecutor,
) -> None:
    await executor.configure_hdri(_req(rotation=RotationDegrees(-90.0)))
    code = str(executor._code_executor.captured_code)
    assert "rotation = 270.0" in code


@pytest.mark.asyncio
async def test_fr_rnd_004_code_generated(
    executor: RenderHdriConfigExecutor,
) -> None:
    await executor.configure_hdri(_req())
    code = str(executor._code_executor.captured_code)
    assert "world.use_nodes = True" in code


@pytest.mark.asyncio
async def test_fr_rnd_004_execution_failure() -> None:
    bad = RenderHdriConfigExecutor(code_executor=MockCodeExecutor(fail=True))
    result = await bad.configure_hdri(_req())
    assert bool(result.success) is False


@pytest.mark.asyncio
async def test_fr_rnd_004_security_delegation(
    executor: RenderHdriConfigExecutor,
) -> None:
    """FR-RND-004: Verify security validator is called before HDRI config."""
    await executor.configure_hdri(_req())
    assert len(executor._security_validator._calls) == 1


@pytest.mark.asyncio
async def test_fr_rnd_004_security_rejection() -> None:
    """FR-RND-004: Security rejection returns error."""
    sec = MockSecurityValidator(deny=True)
    cap = RenderHdriConfigExecutor(
        code_executor=MockCodeExecutor(payload={"environment_ref": "World"}),
        security_validator=sec,
    )
    result = await cap.configure_hdri(_req())
    assert bool(result.success) is False
    assert "security_violation" in str(result.message).lower()


@pytest.mark.asyncio
async def test_fr_rnd_004_missing_world_environment() -> None:
    """FR-RND-004: HDRI config with no world resolved returns environment_state error."""
    bad = RenderHdriConfigExecutor(code_executor=MockCodeExecutor(payload={"environment_ref": ""}))
    result = await bad.configure_hdri(_req())
    assert bool(result.success) is False
    assert "environment_state" in str(result.message).lower()


@pytest.mark.asyncio
async def test_fr_rnd_004_world_created_if_missing() -> None:
    """FR-RND-004: World created if missing + policy allows (success path)."""
    good = RenderHdriConfigExecutor(code_executor=MockCodeExecutor(payload={"environment_ref": "World.HDRI"}))
    result = await good.configure_hdri(_req())
    assert bool(result.success) is True
    assert str(result.environment_ref) == "World.HDRI"
