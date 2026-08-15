from __future__ import annotations

import pytest

from modules.physics.src.capabilities_physics_executor import PhysicsExecutor
from modules.physics.src.root_physics_container import create_physics_feature


class FakeGateway:
    def __init__(self, result):
        self.result = result
        self.codes: list[str] = []

    async def execute_blender_code(self, code: str):
        self.codes.append(code)
        return self.result


@pytest.mark.asyncio
async def test_physics_state_returns_rigid_body_and_cloth_models() -> None:
    gateway = FakeGateway(
        {
            "object_name": "Cube",
            "rigid_body_enabled": True,
            "rigid_body_type": "ACTIVE",
            "rigid_body_mass": 2.0,
            "rigid_body_kinematic": False,
            "cloth_enabled": False,
            "cloth_quality": None,
            "cloth_pin_group": None,
        }
    )

    result = await create_physics_feature(gateway).get_state("Cube")

    assert result.rigid_body_enabled is True
    assert result.rigid_body_type == "ACTIVE"
    assert result.rigid_body_mass == 2.0
    assert result.cloth_enabled is False


@pytest.mark.asyncio
async def test_physics_rejects_invalid_rigid_body_type_before_gateway() -> None:
    gateway = FakeGateway({})

    with pytest.raises(ValueError, match="Unsupported rigid body type"):
        await PhysicsExecutor(gateway).configure_rigid_body("Cube", True, "SOFT")

    assert gateway.codes == []


@pytest.mark.asyncio
async def test_physics_rejects_invalid_cloth_quality_before_gateway() -> None:
    gateway = FakeGateway({})

    with pytest.raises(ValueError, match="quality must be between"):
        await PhysicsExecutor(gateway).configure_cloth("Cube", True, 81)

    assert gateway.codes == []


@pytest.mark.asyncio
async def test_physics_bake_returns_cache_mutation_model() -> None:
    gateway = FakeGateway(
        {
            "object_name": None,
            "changed": True,
            "operation": "bake_physics_simulation",
            "frame_start": 1,
            "frame_end": 24,
            "message": "baked",
        }
    )

    result = await create_physics_feature(gateway).bake(1, 24)

    assert result.operation == "bake_physics_simulation"
    assert result.frame_end == 24
