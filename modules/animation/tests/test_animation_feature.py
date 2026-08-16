from __future__ import annotations

import pytest

from modules.animation.src.capabilities_animation_executor import AnimationExecutor
from modules.animation.src.capabilities_animation_retarget_executor import AnimationRetargetExecutor
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


@pytest.mark.asyncio
async def test_animation_inspects_face_channels() -> None:
    gateway = FakeGateway(
        {
            "armature_name": "Rigify",
            "domain": "face",
            "controls": [
                {"name": "jaw_master", "side": None, "role": "face_control", "is_deform": False, "property_names": []}
            ],
            "shape_keys": ["Basis", "Smile"],
        }
    )

    result = await create_animation_feature(gateway).inspect_face_animation_channels("Rigify", "Body")

    assert result.domain == "face"
    assert result.controls[0].name == "jaw_master"
    assert result.shape_keys == ("Basis", "Smile")


@pytest.mark.asyncio
async def test_animation_inspects_hand_channels_by_side() -> None:
    gateway = FakeGateway(
        {
            "armature_name": "Rigify",
            "domain": "hands",
            "controls": [
                {"name": "hand_ik.L", "side": "left", "role": "hand_control", "is_deform": False}
            ],
            "shape_keys": [],
        }
    )

    result = await create_animation_feature(gateway).inspect_hand_animation_controls("Rigify", "left")

    assert result.domain == "hands"
    assert result.controls[0].side == "left"


@pytest.mark.asyncio
async def test_animation_sets_fk_ik_mode_with_optional_frame() -> None:
    gateway = FakeGateway(
        {
            "armature_name": "Rigify",
            "bone_name": "upper_arm_parent.L",
            "limb": "arm",
            "side": "left",
            "mode": "ik",
            "value": 1.0,
            "frame": 24,
            "changed": True,
        }
    )

    result = await create_animation_feature(gateway).set_rigify_fk_ik_mode("Rigify", "arm", "left", "ik", 24)

    assert result.mode == "ik"
    assert result.value == 1.0
    assert result.frame == 24


@pytest.mark.asyncio
async def test_animation_rejects_invalid_fk_ik_mode_before_gateway() -> None:
    gateway = FakeGateway({})

    with pytest.raises(ValueError, match="mode must be fk or ik"):
        await AnimationExecutor(gateway).set_rigify_fk_ik_mode("Rigify", "arm", "left", "blend")

    assert gateway.codes == []


@pytest.mark.asyncio
async def test_animation_sets_shape_key_keyframe() -> None:
    gateway = FakeGateway(
        {"mesh_name": "Body", "shape_key_name": "Smile", "value": 0.8, "frame": 12, "changed": True}
    )

    result = await create_animation_feature(gateway).set_shape_key_keyframe("Body", "Smile", 0.8, 12)

    assert result.shape_key_name == "Smile"
    assert result.value == 0.8


@pytest.mark.asyncio
async def test_animation_keys_face_control_transform() -> None:
    gateway = FakeGateway(
        {
            "armature_name": "Rigify",
            "bone_name": "jaw_master",
            "frame": 12,
            "location": [0.0, 0.0, 0.1],
            "rotation_euler": [0.2, 0.0, 0.0],
            "changed": True,
        }
    )

    result = await create_animation_feature(gateway).edit_face_control_animation(
        "Rigify", "jaw_master", 12, rotation_euler=[0.2, 0.0, 0.0], location=[0.0, 0.0, 0.1]
    )

    assert result.bone_name == "jaw_master"
    assert result.rotation_euler == (0.2, 0.0, 0.0)


@pytest.mark.asyncio
async def test_animation_rejects_shape_key_value_outside_bounds() -> None:
    gateway = FakeGateway({})

    with pytest.raises(ValueError, match="value must be between"):
        await AnimationExecutor(gateway).set_shape_key_keyframe("Body", "Smile", 1.2, 1)

    assert gateway.codes == []


@pytest.mark.asyncio
async def test_animation_builds_explicit_bone_mapping() -> None:
    gateway = FakeGateway(
        {
            "source_armature": "Source",
            "target_armature": "Rigify",
            "preset": "exact",
            "mappings": [{"source_bone": "upper_arm.L", "target_bone": "upper_arm.L", "side": "left", "confidence": 1.0}],
            "unmapped_source": ["unused"],
            "unmapped_target": ["jaw_master"],
        }
    )
    result = await create_animation_feature(gateway).build_bone_mapping("Source", "Rigify")
    assert result.mappings[0].source_bone == "upper_arm.L"
    assert result.unmapped_source == ("unused",)


@pytest.mark.asyncio
async def test_animation_validates_rest_pose_result() -> None:
    gateway = FakeGateway(
        {"source_armature": "Source", "target_armature": "Rigify", "approved": True, "mapped_count": 1, "position_warning_count": 0, "scale_ratio": 1.0, "warnings": []}
    )
    mapping = {"mappings": [{"source_bone": "upper_arm.L", "target_bone": "upper_arm.L"}]}
    result = await create_animation_feature(gateway).validate_rest_pose("Source", "Rigify", mapping)
    assert result.approved is True
    assert result.scale_ratio == 1.0


@pytest.mark.asyncio
async def test_animation_retargets_action_result() -> None:
    gateway = FakeGateway(
        {"source_armature": "Source", "target_armature": "Rigify", "source_action": "Walk", "output_action": "Walk_Rigify", "frame_start": 1, "frame_end": 24, "mapped_bone_count": 1, "keyframe_count": 72, "root_motion": "preserve", "changed": True}
    )
    mapping = {"mappings": [{"source_bone": "upper_arm.L", "target_bone": "upper_arm.L"}]}
    result = await create_animation_feature(gateway).retarget_animation("Source", "Rigify", "Walk", mapping, "Walk_Rigify", 1, 24)
    assert result.output_action == "Walk_Rigify"
    assert result.keyframe_count == 72


@pytest.mark.asyncio
async def test_animation_rejects_invalid_root_motion_policy() -> None:
    gateway = FakeGateway({})
    with pytest.raises(ValueError, match="root_motion must be"):
        await AnimationRetargetExecutor(gateway).retarget_animation(
            "Source", "Rigify", "Walk", {"mappings": [{"source_bone": "a", "target_bone": "b"}]}, "Out", root_motion="move"
        )
    assert gateway.codes == []


@pytest.mark.asyncio
async def test_animation_sets_root_motion_metadata() -> None:
    gateway = FakeGateway({"armature_name": "Rigify", "policy": "separate", "changed": True})
    result = await create_animation_feature(gateway).set_root_motion("Rigify", "separate")
    assert result.policy == "separate"
    assert result.changed is True


@pytest.mark.asyncio
async def test_animation_bakes_retarget_action() -> None:
    gateway = FakeGateway(
        {"armature_name": "Rigify", "action_name": "Walk_Rigify", "frame_start": 1, "frame_end": 24, "step": 1, "keyframe_count": 144, "cleared_constraints": False, "changed": True}
    )
    result = await create_animation_feature(gateway).bake_retarget_action("Rigify", "Walk_Rigify", 1, 24)
    assert result.action_name == "Walk_Rigify"
    assert result.keyframe_count == 144


@pytest.mark.asyncio
async def test_animation_validates_retarget_result() -> None:
    gateway = FakeGateway(
        {"armature_name": "Rigify", "action_name": "Walk_Rigify", "frame_start": 1, "frame_end": 24, "curve_count": 3, "keyframe_count": 72, "approved": True, "warnings": []}
    )
    result = await create_animation_feature(gateway).validate_animation_result("Rigify", "Walk_Rigify")
    assert result.approved is True
    assert result.curve_count == 3


@pytest.mark.asyncio
async def test_animation_creates_nla_track() -> None:
    gateway = FakeGateway({"armature_name": "Rigify", "track_name": "Base", "strip_count": 0, "is_solo": False, "is_muted": False, "changed": True})
    result = await create_animation_feature(gateway).create_nla_track("Rigify", "Base")
    assert result.track_name == "Base"
    assert result.changed is True


@pytest.mark.asyncio
async def test_animation_adds_nla_strip() -> None:
    gateway = FakeGateway({"armature_name": "Rigify", "track_name": "Base", "strip_name": "Walk", "action_name": "Walk", "frame_start": 1.0, "frame_end": 25.0, "scale": 1.0, "repeat": 1.0, "blend_in": 2.0, "blend_out": 2.0, "influence": 1.0, "blend_type": "REPLACE", "extrapolation": "HOLD", "reversed": False, "changed": True})
    result = await create_animation_feature(gateway).add_nla_strip("Rigify", "Base", "Walk", "Walk", 1, blend_in=2, blend_out=2)
    assert result.action_name == "Walk"
    assert result.blend_in == 2.0


@pytest.mark.asyncio
async def test_animation_updates_nla_strip() -> None:
    gateway = FakeGateway({"armature_name": "Rigify", "track_name": "Base", "strip_name": "Walk", "action_name": "Walk", "frame_start": 5.0, "frame_end": 29.0, "scale": 1.0, "repeat": 1.0, "blend_in": 2.0, "blend_out": 2.0, "influence": 0.75, "blend_type": "ADD", "extrapolation": "HOLD", "reversed": False, "changed": True})
    result = await create_animation_feature(gateway).set_nla_strip("Rigify", "Base", "Walk", frame_start=5, influence=0.75, blend_type="ADD")
    assert result.influence == 0.75
    assert result.blend_type == "ADD"


@pytest.mark.asyncio
async def test_animation_sets_nla_layer() -> None:
    gateway = FakeGateway({"armature_name": "Rigify", "track_name": "UpperBody", "blend_type": "ADD", "influence": 0.5, "is_solo": False, "is_muted": False, "changed": True})
    result = await create_animation_feature(gateway).set_animation_layer("Rigify", "UpperBody", "ADD", 0.5)
    assert result.blend_type == "ADD"
    assert result.influence == 0.5


@pytest.mark.asyncio
async def test_animation_sets_rigify_nla_mask() -> None:
    gateway = FakeGateway({"armature_name": "Rigify", "track_name": "UpperBody", "strip_name": "Gesture", "bone_names": ["hand_ik.L", "hand_ik.R"], "changed": True})
    result = await create_animation_feature(gateway).set_animation_mask("Rigify", "UpperBody", "Gesture", ["hand_ik.L", "hand_ik.R"])
    assert result.bone_names == ("hand_ik.L", "hand_ik.R")


@pytest.mark.asyncio
async def test_animation_rejects_deform_nla_mask() -> None:
    gateway = FakeGateway({})
    with pytest.raises(ValueError, match="animator controls"):
        await create_animation_feature(gateway).set_animation_mask("Rigify", "Base", "Walk", ["DEF-upper_arm.L"])
    assert gateway.codes == []


@pytest.mark.asyncio
async def test_animation_bakes_nla_assembly() -> None:
    gateway = FakeGateway({"armature_name": "Rigify", "output_action": "Final", "frame_start": 1, "frame_end": 24, "step": 1, "keyframe_count": 288, "cleared_constraints": False, "cleared_nla": True, "changed": True})
    result = await create_animation_feature(gateway).bake_nla_assembly("Rigify", 1, 24, output_action="Final", clear_nla=True)
    assert result.output_action == "Final"
    assert result.cleared_nla is True


@pytest.mark.asyncio
async def test_animation_validates_nla_assembly() -> None:
    gateway = FakeGateway({"armature_name": "Rigify", "track_count": 2, "strip_count": 3, "frame_start": 1.0, "frame_end": 72.0, "approved": True, "warnings": []})
    result = await create_animation_feature(gateway).validate_nla_assembly("Rigify")
    assert result.approved is True
    assert result.strip_count == 3


@pytest.mark.asyncio
async def test_animation_removes_nla_strip() -> None:
    gateway = FakeGateway({"armature_name": "Rigify", "track_name": "Base", "strip_name": "Walk", "changed": True, "removed": True})
    result = await create_animation_feature(gateway).remove_nla_strip("Rigify", "Base", "Walk")
    assert result.removed is True
