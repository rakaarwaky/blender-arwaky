from __future__ import annotations

import sys
from pathlib import Path

import bpy

sys.path.insert(0, "/home/ubuntu/blender-arwaky")

from blender_mcp_addon.server import BlenderMCPServer


EVIDENCE_BLEND = Path("/home/ubuntu/mpfb_native_rigify_evidence/native_mpfb2_rigify_character.blend")

bpy.ops.wm.open_mainfile(filepath=str(EVIDENCE_BLEND))
server = BlenderMCPServer()
target = next(
    (obj for obj in bpy.data.objects if obj.type == "ARMATURE" and len(obj.data.bones) >= 500),
    None,
)
if target is None:
    raise RuntimeError("Native Rigify target armature was not found")

source = target.copy()
source.data = target.data.copy()
source.name = "Wave4_Source_Armature"
source.data.name = "Wave4_Source_Armature_Data"
bpy.context.scene.collection.objects.link(source)

source.animation_data_create()
source_action = bpy.data.actions.new("Wave4_Source_Action")
source.animation_data.action = source_action
source_bone = source.pose.bones.get("upper_arm_parent.L")
if source_bone is None:
    raise RuntimeError("Source test bone upper_arm_parent.L was not found")
source_bone.rotation_mode = "XYZ"
for frame, angle in ((1, 0.0), (12, 0.35), (24, 0.0)):
    bpy.context.scene.frame_set(frame)
    source_bone.rotation_euler[0] = angle
    source_bone.keyframe_insert(data_path="rotation_euler", frame=frame)

mapping_response = server.execute_command(
    {
        "type": "build_bone_mapping",
        "params": {"source_armature": source.name, "target_armature": target.name, "preset": "exact", "unmapped_policy": "report"},
    }
)
if mapping_response.get("status") != "success":
    raise RuntimeError(f"Bone mapping failed: {mapping_response}")
mapping = mapping_response["result"]
if not any(item.get("source_bone") == "upper_arm_parent.L" for item in mapping.get("mappings", [])):
    raise RuntimeError("Expected upper_arm_parent.L mapping was not produced")

rest_response = server.execute_command(
    {
        "type": "validate_rest_pose",
        "params": {"source_armature": source.name, "target_armature": target.name, "mapping": mapping, "tolerance": 0.25},
    }
)
if rest_response.get("status") != "success" or not rest_response["result"].get("approved"):
    raise RuntimeError(f"Rest pose validation failed: {rest_response}")

root_response = server.execute_command(
    {"type": "set_root_motion", "params": {"armature_name": target.name, "policy": "preserve"}}
)
if root_response.get("status") != "success":
    raise RuntimeError(f"Root motion policy failed: {root_response}")

retarget_response = server.execute_command(
    {
        "type": "retarget_animation",
        "params": {
            "source_armature": source.name,
            "target_armature": target.name,
            "source_action": source_action.name,
            "mapping": mapping,
            "output_action": "Wave4_Retargeted_Action",
            "frame_start": 1,
            "frame_end": 24,
            "scale_policy": "preserve",
            "root_motion": "preserve",
        },
    }
)
if retarget_response.get("status") != "success":
    raise RuntimeError(f"Retarget failed: {retarget_response}")
if retarget_response["result"].get("keyframe_count", 0) < 9:
    raise RuntimeError(f"Retarget produced too few keyframes: {retarget_response}")

bake_response = server.execute_command(
    {
        "type": "bake_retarget_action",
        "params": {"armature_name": target.name, "action_name": "Wave4_Retargeted_Action", "frame_start": 1, "frame_end": 24, "step": 1, "clear_constraints": False},
    }
)
if bake_response.get("status") != "success":
    raise RuntimeError(f"Bake failed: {bake_response}")

validation_response = server.execute_command(
    {
        "type": "validate_animation_result",
        "params": {"armature_name": target.name, "action_name": "Wave4_Retargeted_Action", "limit": 1000},
    }
)
if validation_response.get("status") != "success" or not validation_response["result"].get("approved"):
    raise RuntimeError(f"Retarget validation failed: {validation_response}")

print(
    "WAVE4_NATIVE_RETARGETING_LIVE_OK",
    {
        "blender_version": bpy.app.version_string,
        "source_armature": source.name,
        "target_armature": target.name,
        "target_bone_count": len(target.data.bones),
        "mapping_count": len(mapping.get("mappings", [])),
        "unmapped_source_count": len(mapping.get("unmapped_source", [])),
        "rest_pose": rest_response["result"],
        "retarget": retarget_response["result"],
        "bake": bake_response["result"],
        "validation": validation_response["result"],
    },
)
