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
        {"actions": [{"name": "Walk", "frame_start": 1, "frame_end": 48, "curve_count": 6, "slot_count": 1}]}
    )

    result = await create_animation_feature(gateway).list_actions("Rig")

    assert result[0].name == "Walk"
    assert result[0].curve_count == 6
    assert '"Rig"' in gateway.codes[0]


@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_animation_import_rejects_unsupported_format_before_gateway(tmp_path) -> None:
    gateway = FakeGateway({})
    source_path = tmp_path / "animation.glb"

    with pytest.raises(ValueError, match="importer must be fbx or bvh"):
        await AnimationExecutor(gateway).import_animation_file(str(source_path))

    assert gateway.codes == []


@pytest.mark.asyncio
async def test_animation_import_returns_created_actions(tmp_path) -> None:
    gateway = FakeGateway(
        {
            "source_path": str(tmp_path / "walk.bvh"),
            "importer": "bvh",
            "imported_objects": ["mocap"],
            "action_names": ["Walk"],
            "warnings": [],
        }
    )

    result = await create_animation_feature(gateway).import_animation_file(str(tmp_path / "walk.bvh"))

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
    gateway = FakeGateway({"assets": [{"name": "T-Pose", "is_pose_asset": True, "frame_start": 1, "frame_end": 1}]})

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
@pytest.mark.asyncio
@pytest.mark.asyncio
@pytest.mark.asyncio
@pytest.mark.asyncio
@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_animation_sets_shape_key_keyframe() -> None:
    gateway = FakeGateway({"mesh_name": "Body", "shape_key_name": "Smile", "value": 0.8, "frame": 12, "changed": True})

    result = await create_animation_feature(gateway).set_shape_key_keyframe("Body", "Smile", 0.8, 12)

    assert result.shape_key_name == "Smile"
    assert result.value == 0.8


@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_animation_rejects_shape_key_value_outside_bounds() -> None:
    gateway = FakeGateway({})

    with pytest.raises(ValueError, match="value must be between"):
        await AnimationExecutor(gateway).set_shape_key_keyframe("Body", "Smile", 1.2, 1)

    assert gateway.codes == []


@pytest.mark.asyncio
@pytest.mark.asyncio
@pytest.mark.asyncio
@pytest.mark.asyncio
@pytest.mark.asyncio
@pytest.mark.asyncio
@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_animation_creates_nla_track() -> None:
    gateway = FakeGateway(
        {
            "armature_name": "Rigify",
            "track_name": "Base",
            "strip_count": 0,
            "is_solo": False,
            "is_muted": False,
            "changed": True,
        }
    )
    result = await create_animation_feature(gateway).create_nla_track("Rigify", "Base")
    assert result.track_name == "Base"
    assert result.changed is True


@pytest.mark.asyncio
async def test_animation_adds_nla_strip() -> None:
    gateway = FakeGateway(
        {
            "armature_name": "Rigify",
            "track_name": "Base",
            "strip_name": "Walk",
            "action_name": "Walk",
            "frame_start": 1.0,
            "frame_end": 25.0,
            "scale": 1.0,
            "repeat": 1.0,
            "blend_in": 2.0,
            "blend_out": 2.0,
            "influence": 1.0,
            "blend_type": "REPLACE",
            "extrapolation": "HOLD",
            "reversed": False,
            "changed": True,
        }
    )
    result = await create_animation_feature(gateway).add_nla_strip(
        "Rigify", "Base", "Walk", "Walk", 1, blend_in=2, blend_out=2
    )
    assert result.action_name == "Walk"
    assert result.blend_in == 2.0


@pytest.mark.asyncio
async def test_animation_updates_nla_strip() -> None:
    gateway = FakeGateway(
        {
            "armature_name": "Rigify",
            "track_name": "Base",
            "strip_name": "Walk",
            "action_name": "Walk",
            "frame_start": 5.0,
            "frame_end": 29.0,
            "scale": 1.0,
            "repeat": 1.0,
            "blend_in": 2.0,
            "blend_out": 2.0,
            "influence": 0.75,
            "blend_type": "ADD",
            "extrapolation": "HOLD",
            "reversed": False,
            "changed": True,
        }
    )
    result = await create_animation_feature(gateway).set_nla_strip(
        "Rigify", "Base", "Walk", frame_start=5, influence=0.75, blend_type="ADD"
    )
    assert result.influence == 0.75
    assert result.blend_type == "ADD"


@pytest.mark.asyncio
async def test_animation_sets_nla_layer() -> None:
    gateway = FakeGateway(
        {
            "armature_name": "Rigify",
            "track_name": "UpperBody",
            "blend_type": "ADD",
            "influence": 0.5,
            "is_solo": False,
            "is_muted": False,
            "changed": True,
        }
    )
    result = await create_animation_feature(gateway).set_animation_layer("Rigify", "UpperBody", "ADD", 0.5)
    assert result.blend_type == "ADD"
    assert result.influence == 0.5


@pytest.mark.asyncio
async def test_animation_sets_rigify_nla_mask() -> None:
    gateway = FakeGateway(
        {
            "armature_name": "Rigify",
            "track_name": "UpperBody",
            "strip_name": "Gesture",
            "bone_names": ["hand_ik.L", "hand_ik.R"],
            "changed": True,
        }
    )
    result = await create_animation_feature(gateway).set_animation_mask(
        "Rigify", "UpperBody", "Gesture", ["hand_ik.L", "hand_ik.R"]
    )
    assert result.bone_names == ("hand_ik.L", "hand_ik.R")


@pytest.mark.asyncio
async def test_animation_rejects_deform_nla_mask() -> None:
    gateway = FakeGateway({})
    with pytest.raises(ValueError, match="animator controls"):
        await create_animation_feature(gateway).set_animation_mask("Rigify", "Base", "Walk", ["DEF-upper_arm.L"])
    assert gateway.codes == []


@pytest.mark.asyncio
async def test_animation_bakes_nla_assembly() -> None:
    gateway = FakeGateway(
        {
            "armature_name": "Rigify",
            "output_action": "Final",
            "frame_start": 1,
            "frame_end": 24,
            "step": 1,
            "keyframe_count": 288,
            "cleared_constraints": False,
            "cleared_nla": True,
            "changed": True,
        }
    )
    result = await create_animation_feature(gateway).bake_nla_assembly(
        "Rigify", 1, 24, output_action="Final", clear_nla=True
    )
    assert result.output_action == "Final"
    assert result.cleared_nla is True


@pytest.mark.asyncio
async def test_animation_validates_nla_assembly() -> None:
    gateway = FakeGateway(
        {
            "armature_name": "Rigify",
            "track_count": 2,
            "strip_count": 3,
            "frame_start": 1.0,
            "frame_end": 72.0,
            "approved": True,
            "warnings": [],
        }
    )
    result = await create_animation_feature(gateway).validate_nla_assembly("Rigify")
    assert result.approved is True
    assert result.strip_count == 3


@pytest.mark.asyncio
async def test_animation_removes_nla_strip() -> None:
    gateway = FakeGateway(
        {"armature_name": "Rigify", "track_name": "Base", "strip_name": "Walk", "changed": True, "removed": True}
    )
    result = await create_animation_feature(gateway).remove_nla_strip("Rigify", "Base", "Walk")
    assert result.removed is True


@pytest.mark.asyncio
async def test_animation_pose_bone_keyframe_returns_typed_mutation() -> None:
    gateway = FakeGateway(
        {
            "armature_name": "Armature",
            "bone_name": "upper_arm.L",
            "data_path": "rotation_euler",
            "frame": 12,
            "changed": True,
        }
    )

    result = await create_animation_feature(gateway).insert_pose_bone_keyframe(
        "Armature", "upper_arm.L", 12, "rotation_euler", 2
    )

    assert result.object_name == "Armature"
    assert result.frame == 12
    assert "upper_arm.L" in result.data_path


@pytest.mark.asyncio
async def test_animation_pose_bone_keyframe_rejects_unsupported_path() -> None:
    gateway = FakeGateway({})

    with pytest.raises(ValueError, match="Unsupported pose bone animation data path"):
        await AnimationExecutor(gateway).insert_pose_bone_keyframe("Armature", "Bone", 1, "location.x")

    assert gateway.codes == []
