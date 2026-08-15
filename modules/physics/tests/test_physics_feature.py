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


@pytest.mark.asyncio
async def test_simulation_state_returns_advanced_modifier_models() -> None:
    gateway = FakeGateway(
        {
            "object_name": "Cube",
            "particle_systems": [
                {
                    "name": "ParticleSettings",
                    "count": 100,
                    "frame_start": 1,
                    "frame_end": 120,
                    "lifetime": 40.0,
                    "physics_type": "NEWTON",
                }
            ],
            "force_field_enabled": True,
            "force_field_type": "WIND",
            "force_field_strength": 10.0,
            "fluid_domain_enabled": True,
            "fluid_domain_type": "LIQUID",
            "fluid_resolution": 32,
            "fluid_cache_type": "REPLAY",
        }
    )

    result = await create_physics_feature(gateway).get_simulation_state("Cube")

    assert result.particle_system_count == 1
    assert result.particle_systems[0]["physics_type"] == "NEWTON"
    assert result.force_field_type == "WIND"
    assert result.fluid_domain_type == "LIQUID"


@pytest.mark.asyncio
async def test_simulation_cache_status_returns_bounded_cache_models() -> None:
    gateway = FakeGateway(
        {
            "frame_start": 1,
            "frame_end": 120,
            "current_frame": 24,
            "cache_states": [{"object_name": "Cube", "modifier_type": "CLOTH", "is_baked": False}],
        }
    )

    result = await create_physics_feature(gateway).get_simulation_cache_status()

    assert result.frame_end == 120
    assert result.current_frame == 24
    assert result.cache_states[0]["modifier_type"] == "CLOTH"


@pytest.mark.asyncio
async def test_particle_system_rejects_unbounded_count_before_gateway() -> None:
    gateway = FakeGateway({})

    with pytest.raises(ValueError, match="count must be between"):
        await PhysicsExecutor(gateway).configure_particle_system("Cube", True, count=1_000_001)

    assert gateway.codes == []


@pytest.mark.asyncio
async def test_force_field_rejects_unknown_type_before_gateway() -> None:
    gateway = FakeGateway({})

    with pytest.raises(ValueError, match="Unsupported force field type"):
        await PhysicsExecutor(gateway).configure_force_field("Cube", True, field_type="UNKNOWN")

    assert gateway.codes == []


@pytest.mark.asyncio
async def test_fluid_domain_rejects_unbounded_resolution_before_gateway() -> None:
    gateway = FakeGateway({})

    with pytest.raises(ValueError, match="resolution must be between"):
        await PhysicsExecutor(gateway).configure_fluid_domain("Cube", True, resolution=513)

    assert gateway.codes == []
