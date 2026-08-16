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
}
