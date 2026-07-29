"""Shared action schemas — Object domain (used by CLI + MCP surfaces via dispatcher)."""

from typing import Any

OBJECT_ACTIONS: dict[str, dict[str, Any]] = {
    "get_object_info": {
        "description": "Get details of a specific object — location, rotation, scale, modifiers, materials",
        "parameters": {
            "object_name": {"type": "string", "required": True, "description": "Name of the target object"},
        },
    },
    "create_primitive": {
        "description": "Create a new primitive mesh object",
        "parameters": {
            "primitive_type": {
                "type": "string",
                "required": True,
                "description": "Primitive shape",
                "enum": ["SPHERE", "CUBE", "CYLINDER", "PLANE", "CONE", "TORUS"],
            },
            "location": {"type": "array[number]", "required": False, "description": "Position [x, y, z]", "default": [0, 0, 0]},
            "scale": {"type": "array[number]", "required": False, "description": "Scale [x, y, z]", "default": [1, 1, 1]},
            "name": {"type": "string", "required": False, "description": "Custom object name"},
        },
    },
    "set_object_transform": {
        "description": "Update object transform — location, rotation, or scale",
        "parameters": {
            "object_name": {"type": "string", "required": True, "description": "Name of the target object"},
            "location": {"type": "array[number]", "required": False, "description": "Position [x, y, z]"},
            "rotation": {"type": "array[number]", "required": False, "description": "Rotation [x, y, z] in degrees"},
            "scale": {"type": "array[number]", "required": False, "description": "Scale [x, y, z]"},
        },
    },
    "delete_object": {
        "description": "Remove an object from the scene",
        "parameters": {
            "object_name": {"type": "string", "required": True, "description": "Name of the object to delete"},
        },
    },
    "set_material": {
        "description": "Assign a material to an object",
        "parameters": {
            "object_name": {"type": "string", "required": True, "description": "Name of the target object"},
            "material_name": {"type": "string", "required": True, "description": "Name of the material to assign"},
        },
    },
    "apply_modifier": {
        "description": "Apply a modifier on an object",
        "parameters": {
            "object_name": {"type": "string", "required": True, "description": "Name of the target object"},
            "modifier_name": {"type": "string", "required": True, "description": "Name of the modifier to apply"},
        },
    },
}
