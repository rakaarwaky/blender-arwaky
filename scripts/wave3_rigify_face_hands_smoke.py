from __future__ import annotations

import sys
from pathlib import Path

import bpy

sys.path.insert(0, "/home/ubuntu/blender-arwaky")

from blender_mcp_addon.server import BlenderMCPServer


EVIDENCE_BLEND = Path("/home/ubuntu/mpfb_native_rigify_evidence/native_mpfb2_rigify_character.blend")
MESH_NAME = "Native_Render_MPFB2_Character"
SHAPE_KEY_NAME = "$md-$as-$fe-$yn"

bpy.ops.wm.open_mainfile(filepath=str(EVIDENCE_BLEND))
server = BlenderMCPServer()
armature = next(
    (obj for obj in bpy.data.objects if obj.type == "ARMATURE" and len(obj.data.bones) >= 500),
    None,
)
if armature is None:
    raise RuntimeError("Native Rigify control armature was not found in evidence scene")

face_response = server.execute_command(
    {
        "type": "inspect_face_animation_channels",
        "params": {"armature_name": armature.name, "mesh_name": MESH_NAME, "limit": 200},
    }
)
if face_response.get("status") != "success":
    raise RuntimeError(f"Face channel inspection failed: {face_response}")
if not any(item.get("name") == "jaw_master" for item in face_response["result"].get("controls", [])):
    raise RuntimeError("jaw_master was not discovered as a face control")
if SHAPE_KEY_NAME not in face_response["result"].get("shape_keys", []):
    raise RuntimeError("Expected MPFB2 shape key was not discovered")

hand_response = server.execute_command(
    {
        "type": "inspect_hand_animation_controls",
        "params": {"armature_name": armature.name, "side": "left", "limit": 200},
    }
)
if hand_response.get("status") != "success":
    raise RuntimeError(f"Hand control inspection failed: {hand_response}")
if not any(item.get("name") == "hand_ik.L" for item in hand_response["result"].get("controls", [])):
    raise RuntimeError("hand_ik.L was not discovered as a left hand control")

fkik_response = server.execute_command(
    {
        "type": "set_rigify_fk_ik_mode",
        "params": {"armature_name": armature.name, "limb": "arm", "side": "left", "mode": "ik", "frame": 12},
    }
)
if fkik_response.get("status") != "success":
    raise RuntimeError(f"FK/IK mode change failed: {fkik_response}")
if fkik_response["result"].get("value") != 1.0:
    raise RuntimeError(f"Unexpected IK_FK value: {fkik_response}")

face_key_response = server.execute_command(
    {
        "type": "edit_face_control_animation",
        "params": {
            "armature_name": armature.name,
            "bone_name": "jaw_master",
            "frame": 12,
            "rotation_euler": [0.15, 0.0, 0.0],
            "location": [0.0, 0.0, 0.02],
        },
    }
)
if face_key_response.get("status") != "success":
    raise RuntimeError(f"Face control keyframe failed: {face_key_response}")

shape_key_response = server.execute_command(
    {
        "type": "set_shape_key_keyframe",
        "params": {"mesh_name": MESH_NAME, "shape_key_name": SHAPE_KEY_NAME, "value": 0.75, "frame": 12},
    }
)
if shape_key_response.get("status") != "success":
    raise RuntimeError(f"Shape key keyframe failed: {shape_key_response}")

print(
    "WAVE3_RIGIFY_FACE_HANDS_LIVE_OK",
    {
        "blender_version": bpy.app.version_string,
        "armature_name": armature.name,
        "rigify_bone_count": len(armature.data.bones),
        "face_control_count": len(face_response["result"].get("controls", [])),
        "hand_control_count": len(hand_response["result"].get("controls", [])),
        "fk_ik": fkik_response["result"],
        "face_keyframe": face_key_response["result"],
        "shape_key_keyframe": shape_key_response["result"],
    },
)
