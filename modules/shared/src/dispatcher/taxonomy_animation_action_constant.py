from __future__ import annotations

ANIMATION_ACTION_SCHEMAS: dict[str, dict[str, dict[str, object]]] = {
    "get_animation_state": {
        "description": "Inspect an object's bounded animation action, frame range, and F-curves",
        "parameters": {
            "object_name": {"type": "string", "required": True},
            "limit": {"type": "integer", "required": False, "default": 100},
        },
    },
    "insert_object_keyframe": {
        "description": "Insert a bounded keyframe for an object's location, rotation, or scale",
        "parameters": {
            "object_name": {"type": "string", "required": True},
            "frame": {"type": "integer", "required": True},
            "data_path": {
                "type": "string",
                "required": True,
                "enum": ["location", "rotation_euler", "scale"],
            },
            "index": {"type": "integer", "required": False},
        },
    },
    "set_timeline_range": {
        "description": "Set the scene timeline frame range with bounded integer values",
        "parameters": {
            "frame_start": {"type": "integer", "required": True},
            "frame_end": {"type": "integer", "required": True},
            "current_frame": {"type": "integer", "required": False},
        },
    },
    "list_object_keyframes": {
        "description": "List an object's bounded F-curve keyframe points",
        "parameters": {
            "object_name": {"type": "string", "required": True},
            "limit": {"type": "integer", "required": False, "default": 100},
        },
    },
    "list_animation_actions": {
        "description": "List native Blender Actions, optionally filtered to an armature's active Action",
        "parameters": {
            "armature_name": {"type": "string", "required": False},
            "limit": {"type": "integer", "required": False, "default": 100},
        },
    },
    "inspect_rigify_controls": {
        "description": "Inspect generated Rigify control, deform, IK, pole, and mechanism bones",
        "parameters": {
            "armature_name": {"type": "string", "required": True},
            "limit": {"type": "integer", "required": False, "default": 1000},
        },
    },
    "import_animation_file": {
        "description": "Import native FBX or BVH animation data and report imported objects and Actions",
        "parameters": {
            "source_path": {"type": "string", "required": True},
            "importer": {"type": "string", "required": False, "enum": ["fbx", "bvh"]},
        },
    },
    "link_action_to_armature": {
        "description": "Assign one existing native Blender Action to an armature",
        "parameters": {
            "armature_name": {"type": "string", "required": True},
            "action_name": {"type": "string", "required": True},
        },
    },
    "list_pose_assets": {
        "description": "List native Blender pose assets available in the current file",
        "parameters": {"limit": {"type": "integer", "required": False, "default": 100}},
    },
    "create_pose_asset": {
        "description": "Create a native pose asset from the active Rigify armature pose",
        "parameters": {
            "armature_name": {"type": "string", "required": True},
            "pose_name": {"type": "string", "required": True},
            "catalog_path": {"type": "string", "required": False},
        },
    },
    "apply_pose_asset": {
        "description": "Apply or mirror a native pose asset to a Rigify armature",
        "parameters": {
            "armature_name": {"type": "string", "required": True},
            "asset_name": {"type": "string", "required": True},
            "blend_factor": {"type": "number", "required": False, "default": 1.0},
            "flipped": {"type": "boolean", "required": False, "default": False},
        },
    },
    "blend_pose_asset": {
        "description": "Blend a native pose asset into a Rigify armature",
        "parameters": {
            "armature_name": {"type": "string", "required": True},
            "asset_name": {"type": "string", "required": True},
            "blend_factor": {"type": "number", "required": True},
            "flipped": {"type": "boolean", "required": False, "default": False},
        },
    },
    "copy_rigify_pose": {
        "description": "Copy the selected Rigify pose to Blender's session pose buffer",
        "parameters": {"armature_name": {"type": "string", "required": True}},
    },
    "paste_rigify_pose": {
        "description": "Paste the session pose buffer to a Rigify armature, optionally mirrored",
        "parameters": {
            "armature_name": {"type": "string", "required": True},
            "flipped": {"type": "boolean", "required": False, "default": False},
            "selected_mask": {"type": "boolean", "required": False, "default": False},
        },
    },
    "keyframe_rigify_pose": {
        "description": "Insert native keyframes for selected or named Rigify pose controls",
        "parameters": {
            "armature_name": {"type": "string", "required": True},
            "frame": {"type": "integer", "required": True},
            "bone_names": {"type": "array", "required": False},
        },
    },
    "inspect_face_animation_channels": {
        "description": "Inspect bounded native Rigify facial control bones and animated shape keys",
        "parameters": {
            "armature_name": {"type": "string", "required": True},
            "mesh_name": {"type": "string", "required": False},
            "limit": {"type": "integer", "required": False, "default": 200},
        },
    },
    "inspect_hand_animation_controls": {
        "description": "Inspect bounded Rigify hand and finger control bones by side",
        "parameters": {
            "armature_name": {"type": "string", "required": True},
            "side": {"type": "string", "required": False, "enum": ["left", "right", "both"]},
            "limit": {"type": "integer", "required": False, "default": 200},
        },
    },
    "set_rigify_fk_ik_mode": {
        "description": "Set and optionally key the native Rigify FK/IK switch on an explicit limb parent",
        "parameters": {
            "armature_name": {"type": "string", "required": True},
            "limb": {"type": "string", "required": True, "enum": ["arm", "leg"]},
            "side": {"type": "string", "required": True, "enum": ["left", "right"]},
            "mode": {"type": "string", "required": True, "enum": ["fk", "ik"]},
            "frame": {"type": "integer", "required": False},
        },
    },
    "set_shape_key_keyframe": {
        "description": "Set and keyframe one mesh shape key value at a bounded frame",
        "parameters": {
            "mesh_name": {"type": "string", "required": True},
            "shape_key_name": {"type": "string", "required": True},
            "value": {"type": "number", "required": True},
            "frame": {"type": "integer", "required": True},
        },
    },
    "edit_face_control_animation": {
        "description": "Keyframe an allowlisted Rigify facial control transform without touching deform bones",
        "parameters": {
            "armature_name": {"type": "string", "required": True},
            "bone_name": {"type": "string", "required": True},
            "frame": {"type": "integer", "required": True},
            "rotation_euler": {"type": "array", "required": False},
            "location": {"type": "array", "required": False},
        },
    },
    "import_motion_capture": {
        "description": "Import native BVH or FBX motion-capture data and report source Actions",
        "parameters": {
            "source_path": {"type": "string", "required": True},
            "importer": {"type": "string", "required": False, "enum": ["bvh", "fbx"]},
        },
    },
    "build_bone_mapping": {
        "description": "Build an explicit source-to-target bone mapping for native Rigify retargeting",
        "parameters": {
            "source_armature": {"type": "string", "required": True},
            "target_armature": {"type": "string", "required": True},
            "preset": {"type": "string", "required": False, "default": "exact"},
            "overrides": {"type": "object", "required": False},
            "unmapped_policy": {"type": "string", "required": False, "enum": ["report", "error"]},
        },
    },
    "validate_rest_pose": {
        "description": "Validate source and target armature rest-pose compatibility for an approved mapping",
        "parameters": {
            "source_armature": {"type": "string", "required": True},
            "target_armature": {"type": "string", "required": True},
            "mapping": {"type": "object", "required": True},
            "tolerance": {"type": "number", "required": False, "default": 0.25},
        },
    },
    "retarget_animation": {
        "description": "Retarget a native source Action to Rigify controls using explicit mapping and frame range",
        "parameters": {
            "source_armature": {"type": "string", "required": True},
            "target_armature": {"type": "string", "required": True},
            "source_action": {"type": "string", "required": True},
            "mapping": {"type": "object", "required": True},
            "frame_start": {"type": "integer", "required": False},
            "frame_end": {"type": "integer", "required": False},
            "output_action": {"type": "string", "required": True},
            "scale_policy": {"type": "string", "required": False, "enum": ["preserve", "normalize"]},
            "root_motion": {"type": "string", "required": False, "enum": ["preserve", "separate", "ignore"]},
        },
    },
    "set_root_motion": {
        "description": "Set the native Arwaky root-motion policy metadata for a target armature",
        "parameters": {
            "armature_name": {"type": "string", "required": True},
            "policy": {"type": "string", "required": True, "enum": ["preserve", "separate", "ignore"]},
        },
    },
    "bake_retarget_action": {
        "description": "Bake or normalize a retargeted target Action over a bounded frame range",
        "parameters": {
            "armature_name": {"type": "string", "required": True},
            "action_name": {"type": "string", "required": True},
            "frame_start": {"type": "integer", "required": True},
            "frame_end": {"type": "integer", "required": True},
            "step": {"type": "integer", "required": False, "default": 1},
            "clear_constraints": {"type": "boolean", "required": False, "default": False},
        },
    },
    "validate_animation_result": {
        "description": "Validate target Action ownership, mapped channels, frame range, and key count",
        "parameters": {
            "armature_name": {"type": "string", "required": True},
            "action_name": {"type": "string", "required": True},
            "limit": {"type": "integer", "required": False, "default": 1000},
        },
    },
    "create_nla_track": {
        "description": "Create or reuse a named native NLA track on an armature",
        "parameters": {
            "armature_name": {"type": "string", "required": True},
            "track_name": {"type": "string", "required": True},
            "is_solo": {"type": "boolean", "required": False, "default": False},
            "is_muted": {"type": "boolean", "required": False, "default": False},
        },
    },
    "add_nla_strip": {
        "description": "Add an existing Action to a native NLA track with bounded timing and blend settings",
        "parameters": {
            "armature_name": {"type": "string", "required": True},
            "track_name": {"type": "string", "required": True},
            "action_name": {"type": "string", "required": True},
            "strip_name": {"type": "string", "required": True},
            "frame_start": {"type": "number", "required": True},
            "scale": {"type": "number", "required": False, "default": 1.0},
            "repeat": {"type": "number", "required": False, "default": 1.0},
            "blend_in": {"type": "number", "required": False, "default": 0.0},
            "blend_out": {"type": "number", "required": False, "default": 0.0},
            "influence": {"type": "number", "required": False, "default": 1.0},
            "blend_type": {"type": "string", "required": False, "enum": ["REPLACE", "ADD", "SUBTRACT", "MULTIPLY"]},
            "extrapolation": {"type": "string", "required": False, "enum": ["NOTHING", "HOLD", "HOLD_FORWARD"]},
            "reversed": {"type": "boolean", "required": False, "default": False},
        },
    },
    "set_nla_strip": {
        "description": "Update bounded timing, influence, blend, and extrapolation settings on a native NLA strip",
        "parameters": {
            "armature_name": {"type": "string", "required": True},
            "track_name": {"type": "string", "required": True},
            "strip_name": {"type": "string", "required": True},
            "frame_start": {"type": "number", "required": False},
            "scale": {"type": "number", "required": False},
            "repeat": {"type": "number", "required": False},
            "blend_in": {"type": "number", "required": False},
            "blend_out": {"type": "number", "required": False},
            "influence": {"type": "number", "required": False},
            "blend_type": {"type": "string", "required": False, "enum": ["REPLACE", "ADD", "SUBTRACT", "MULTIPLY"]},
            "extrapolation": {"type": "string", "required": False, "enum": ["NOTHING", "HOLD", "HOLD_FORWARD"]},
            "reversed": {"type": "boolean", "required": False},
        },
    },
    "set_animation_layer": {
        "description": "Set NLA track mute, solo, and strip blend policy for a native animation layer",
        "parameters": {
            "armature_name": {"type": "string", "required": True},
            "track_name": {"type": "string", "required": True},
            "blend_type": {"type": "string", "required": False, "enum": ["REPLACE", "ADD", "SUBTRACT", "MULTIPLY"]},
            "influence": {"type": "number", "required": False},
            "is_solo": {"type": "boolean", "required": False},
            "is_muted": {"type": "boolean", "required": False},
        },
    },
    "set_animation_mask": {
        "description": "Set an explicit Rigify control-bone mask on a native NLA strip",
        "parameters": {
            "armature_name": {"type": "string", "required": True},
            "track_name": {"type": "string", "required": True},
            "strip_name": {"type": "string", "required": True},
            "bone_names": {"type": "array", "required": True},
        },
    },
    "remove_nla_strip": {
        "description": "Remove one named native NLA strip from an armature track",
        "parameters": {
            "armature_name": {"type": "string", "required": True},
            "track_name": {"type": "string", "required": True},
            "strip_name": {"type": "string", "required": True},
        },
    },
    "bake_nla_assembly": {
        "description": "Bake the evaluated native NLA assembly into one editable Action",
        "parameters": {
            "armature_name": {"type": "string", "required": True},
            "frame_start": {"type": "integer", "required": True},
            "frame_end": {"type": "integer", "required": True},
            "step": {"type": "integer", "required": False, "default": 1},
            "output_action": {"type": "string", "required": True},
            "clear_constraints": {"type": "boolean", "required": False, "default": False},
            "clear_nla": {"type": "boolean", "required": False, "default": False},
        },
    },
    "validate_nla_assembly": {
        "description": "Validate native NLA tracks, strips, Action linkage, frame ranges, and blend settings",
        "parameters": {
            "armature_name": {"type": "string", "required": True},
            "limit": {"type": "integer", "required": False, "default": 100},
        },
    },
}
