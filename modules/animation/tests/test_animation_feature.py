from __future__ import annotations

import pytest

from modules.animation.src.capabilities_animation_executor import AnimationExecutor
from modules.animation.src.root_animation_container import create_animation_feature


class FakeGateway:
    def __init__(self, result):
        self.result = result
        self.codes: list[str] = []

    async def execute_blender_code(self, code: str):
        self.codes.append(code)
        return self.result


@pytest.mark.asyncio
async def test_animation_state_returns_curves_and_keyframes() -> None:
    gateway = FakeGateway(
        {
            "object_name": "Cube",
            "action_name": "CubeAction",
            "frame_start": 1,
            "frame_end": 120,
            "current_frame": 24,
            "curves": [
                {
                    "data_path": "location",
                    "array_index": 0,
                    "keyframes": [{"frame": 1, "value": 0, "index": 0}],
                }
            ],
        }
    )

    result = await create_animation_feature(gateway).get_state("Cube")

    assert result.action_name == "CubeAction"
    assert result.curves[0].keyframes[0].frame == 1
    assert '"Cube"' in gateway.codes[0]


@pytest.mark.asyncio
async def test_animation_rejects_unsupported_path_before_gateway() -> None:
    gateway = FakeGateway({})

    with pytest.raises(ValueError, match="Unsupported animation data path"):
        await AnimationExecutor(gateway).insert_keyframe("Cube", 1, "location.x")

    assert gateway.codes == []


@pytest.mark.asyncio
async def test_animation_timeline_rejects_out_of_range_current_frame() -> None:
    gateway = FakeGateway({})

    with pytest.raises(ValueError, match="within the timeline range"):
        await AnimationExecutor(gateway).set_timeline(1, 10, 20)


@pytest.mark.asyncio
async def test_animation_keyframe_returns_typed_mutation() -> None:
    gateway = FakeGateway({"object_name": "Cube", "data_path": "scale", "frame": 12, "changed": True})

    result = await create_animation_feature(gateway).insert_keyframe("Cube", 12, "scale")

    assert result.object_name == "Cube"
    assert result.data_path == "scale"
    assert result.frame == 12


@pytest.mark.asyncio
async def test_animation_lists_actions_with_typed_result() -> None:
    gateway = FakeGateway(
        {
            "actions": [
                {"name": "Walk", "frame_start": 1, "frame_end": 48, "curve_count": 6, "slot_count": 1}
            ]
        }
    )

    result = await create_animation_feature(gateway).list_actions("Rig")

    assert result[0].name == "Walk"
    assert result[0].curve_count == 6
    assert '"Rig"' in gateway.codes[0]


@pytest.mark.asyncio
async def test_animation_inspects_rigify_controls() -> None:
    gateway = FakeGateway(
        {
            "armature_name": "Rigify",
            "control_count": 2,
            "controls": [
                {"name": "upper_arm_ik.L", "role": "ik", "side": "left", "is_deform": False},
                {"name": "DEF-upper_arm.L", "role": "deform", "side": "left", "is_deform": True},
            ],
        }
    )

    result = await create_animation_feature(gateway).inspect_rigify_controls("Rigify")

    assert result.control_count == 2
    assert result.controls[0].role == "ik"
    assert result.controls[1].is_deform is True


@pytest.mark.asyncio
async def test_animation_import_rejects_unsupported_format_before_gateway() -> None:
    gateway = FakeGateway({})

    with pytest.raises(ValueError, match="importer must be fbx or bvh"):
        await AnimationExecutor(gateway).import_animation_file("/tmp/animation.glb")

    assert gateway.codes == []


@pytest.mark.asyncio
async def test_animation_import_returns_created_actions() -> None:
    gateway = FakeGateway(
        {
            "source_path": "/tmp/walk.bvh",
            "importer": "bvh",
            "imported_objects": ["mocap"],
            "action_names": ["Walk"],
            "warnings": [],
        }
    )

    result = await create_animation_feature(gateway).import_animation_file("/tmp/walk.bvh")

    assert result.importer == "bvh"
    assert result.action_names == ("Walk",)


@pytest.mark.asyncio
async def test_animation_links_action_to_armature() -> None:
    gateway = FakeGateway(
        {
            "armature_name": "Rigify",
            "action_name": "Walk",
            "previous_action_name": "Idle",
            "changed": True,
        }
    )

    result = await create_animation_feature(gateway).link_action_to_armature("Rigify", "Walk")

    assert result.action_name == "Walk"
    assert result.previous_action_name == "Idle"
    assert result.changed is True


@pytest.mark.asyncio
async def test_animation_lists_pose_assets_with_typed_result() -> None:
    gateway = FakeGateway(
        {"assets": [{"name": "T-Pose", "is_pose_asset": True, "frame_start": 1, "frame_end": 1}]}
    )

    result = await create_animation_feature(gateway).list_pose_assets()

    assert result[0].name == "T-Pose"
    assert result[0].is_pose_asset is True


@pytest.mark.asyncio
async def test_animation_applies_flipped_pose_asset() -> None:
    gateway = FakeGateway(
        {
            "armature_name": "Rigify",
            "asset_name": "T-Pose",
            "blend_factor": 1.0,
            "flipped": True,
            "changed": True,
        }
    )

    result = await create_animation_feature(gateway).apply_pose_asset("Rigify", "T-Pose", flipped=True)

    assert result.flipped is True
    assert result.asset_name == "T-Pose"


@pytest.mark.asyncio
async def test_animation_rejects_pose_blend_outside_bounds() -> None:
    gateway = FakeGateway({})

    with pytest.raises(ValueError, match="blend_factor"):
        await AnimationExecutor(gateway).apply_pose_asset("Rigify", "T-Pose", blend_factor=1.1)

    assert gateway.codes == []


@pytest.mark.asyncio
async def test_animation_pastes_mirrored_pose_buffer() -> None:
    gateway = FakeGateway(
        {"armature_name": "Rigify", "flipped": True, "selected_mask": True, "changed": True}
    )

    result = await create_animation_feature(gateway).paste_rigify_pose("Rigify", True, True)

    assert result.flipped is True
    assert result.selected_mask is True


@pytest.mark.asyncio
async def test_animation_keyframes_named_rigify_controls() -> None:
    gateway = FakeGateway(
        {"armature_name": "Rigify", "frame": 24, "bone_names": ["upper_arm_ik.L"], "changed": True}
    )

    result = await create_animation_feature(gateway).keyframe_rigify_pose(
        "Rigify", 24, ["upper_arm_ik.L"]
    )

    assert result.frame == 24
    assert result.bone_names == ("upper_arm_ik.L",)
    assert '"upper_arm_ik.L"' in gateway.codes[0]
