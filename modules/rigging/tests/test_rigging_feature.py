from __future__ import annotations

import pytest

from modules.rigging.src.capabilities_rigging_executor import RiggingExecutor
from modules.rigging.src.root_rigging_container import create_rigging_feature


class FakeGateway:
    def __init__(self, result):
        self.result = result
        self.codes: list[str] = []

    async def execute_blender_code(self, code: str):
        self.codes.append(code)
        return self.result


@pytest.mark.asyncio
async def test_inspect_armature_returns_typed_hierarchy() -> None:
    gateway = FakeGateway(
        {
            "object_name": "Rig",
            "bone_count": 2,
            "bones": [{"name": "Root", "parent": None}, {"name": "Child", "parent": "Root"}],
        }
    )

    result = await create_rigging_feature(gateway).inspect_armature("Rig")

    assert result.bone_count == 2
    assert result.bones[1]["parent"] == "Root"


@pytest.mark.asyncio
async def test_pose_transform_requires_three_finite_values() -> None:
    gateway = FakeGateway({})

    with pytest.raises(ValueError, match="exactly 3 numbers"):
        await RiggingExecutor(gateway).set_pose_bone_transform("Rig", "Bone", location=[0.0, 0.0])

    assert gateway.codes == []


@pytest.mark.asyncio
async def test_pose_transform_requires_at_least_one_vector() -> None:
    gateway = FakeGateway({})

    with pytest.raises(ValueError, match="at least one pose transform"):
        await RiggingExecutor(gateway).set_pose_bone_transform("Rig", "Bone")

    assert gateway.codes == []


@pytest.mark.asyncio
async def test_constraint_rejects_unlisted_type_before_gateway() -> None:
    gateway = FakeGateway({})

    with pytest.raises(ValueError, match="Unsupported bone constraint type"):
        await RiggingExecutor(gateway).configure_bone_constraint("Rig", "Bone", "IK", True)

    assert gateway.codes == []


@pytest.mark.asyncio
async def test_shape_key_rejects_value_outside_slider_limits() -> None:
    gateway = FakeGateway({})

    with pytest.raises(ValueError, match="within slider limits"):
        await RiggingExecutor(gateway).configure_shape_key(
            "Mesh", "Smile", True, value=2.0, slider_min=0.0, slider_max=1.0
        )

    assert gateway.codes == []


@pytest.mark.asyncio
async def test_deformation_state_returns_modifier_constraints_and_shape_keys() -> None:
    gateway = FakeGateway(
        {
            "object_name": "Mesh",
            "armature_modifiers": [{"name": "Armature", "object_name": "Rig"}],
            "constraints": [{"name": "CopyRotation", "type": "COPY_ROTATION"}],
            "shape_keys": [{"name": "Basis", "value": 0.0}, {"name": "Smile", "value": 0.5}],
        }
    )

    result = await create_rigging_feature(gateway).get_deformation_state("Mesh")

    assert result.armature_modifiers[0]["object_name"] == "Rig"
    assert result.constraints[0]["type"] == "COPY_ROTATION"
    assert result.shape_keys[1]["name"] == "Smile"
