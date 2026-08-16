import sys

import bpy

sys.path.insert(0, "/home/ubuntu/blender-arwaky")

from blender_mcp_addon.server import BlenderMCPServer


bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.preferences.addon_enable(module="rigify")

try:
    from bl_ext.user_default.mpfb.services.humanservice import HumanService
except ImportError as error:
    raise RuntimeError("MPFB2 HumanService is unavailable") from error

objects_before = set(bpy.data.objects)
character = HumanService.create_human()
if character is None:
    active = bpy.context.view_layer.objects.active
    character = active if active not in objects_before else None
if character is None:
    raise RuntimeError("MPFB2 did not create a character object")

new_meshes = [obj for obj in bpy.data.objects if obj not in objects_before and obj.type == "MESH"]
if character.type != "MESH":
    character = new_meshes[0] if new_meshes else None
if character is None or character.type != "MESH":
    raise RuntimeError("MPFB2 character did not produce a mesh object")
character.name = "Wave8_MPFB2_Character"

server = BlenderMCPServer()
params = {
    "character_object_name": character.name,
    "armature_name": "Wave8_Rigify_Metarig",
    "preset": "human",
    "bind_character": True,
    "replace_existing": False,
}
first_response = server.execute_command({"type": "create_rigify_metarig", "params": params})
if first_response.get("status") != "success":
    raise RuntimeError(f"First metarig workflow failed: {first_response}")
first = first_response["result"]

second_response = server.execute_command({"type": "create_rigify_metarig", "params": params})
if second_response.get("status") != "success":
    raise RuntimeError(f"Idempotent metarig workflow failed: {second_response}")
second = second_response["result"]

armature = bpy.data.objects.get("Wave8_Rigify_Metarig")
modifier = character.modifiers.get("Wave8_Rigify_Metarig_Armature")
if armature is None or armature.type != "ARMATURE":
    raise RuntimeError("Automatic workflow did not create a Rigify armature")
if len(armature.data.bones) == 0:
    raise RuntimeError("Automatic Rigify metarig contains no bones")
if modifier is None or modifier.object != armature:
    raise RuntimeError("Automatic workflow did not bind the MPFB2 character")
if first["created"] is not True or second["created"] is not False:
    raise RuntimeError(f"Metarig workflow is not idempotent: first={first}, second={second}")
if second["bound"] is not True or second["modifier_name"] != modifier.name:
    raise RuntimeError(f"Automatic binding result is invalid: {second}")
if len(second.get("fit", {}).get("scale", ())) != 3:
    raise RuntimeError(f"Global metarig fitting result is missing: {second}")
if second.get("arm_fit", {}).get("max_lateral_x", 0.0) <= 0.0:
    raise RuntimeError(f"Arm landmark fitting result is missing: {second}")

print(
    "WAVE8_MPFB2_RIGIFY_METARIG_LIVE_OK",
    {
        "blender_version": bpy.app.version_string,
        "character_name": character.name,
        "armature_name": armature.name,
        "bone_count": len(armature.data.bones),
        "modifier_name": modifier.name,
        "first_created": first["created"],
        "second_created": second["created"],
        "second_bound": second["bound"],
        "global_fit_scale": second["fit"]["scale"],
        "arm_fit": second["arm_fit"],
    },
)
