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
}
