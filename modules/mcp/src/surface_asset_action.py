"""MCP asset action schemas — parameter definitions for import, export, and asset placement."""

from typing import Any

ASSET_ACTIONS: dict[str, dict[str, Any]] = {
    "import_glb": {
        "description": "Import a GLB/GLTF file into the scene",
        "parameters": {
            "file_path": {"type": "string", "required": True, "description": "Path to the GLB/GLTF file"},
            "object_name": {"type": "string", "required": False, "description": "Custom name for the imported object"},
        },
    },
    "export_model": {
        "description": "Export a model to a file",
        "parameters": {
            "object_name": {"type": "string", "required": True, "description": "Name of the object to export"},
            "file_path": {"type": "string", "required": True, "description": "Output path for the exported file"},
            "export_format": {
                "type": "string",
                "required": False,
                "description": "Export format",
                "enum": ["glb", "fbx", "obj"],
                "default": "glb",
            },
        },
    },
    "place_asset": {
        "description": "Place an asset in the scene at a specific position",
        "parameters": {
            "asset_id": {"type": "string", "required": True, "description": "Asset identifier"},
            "location": {"type": "array[number]", "required": False, "description": "Position [x, y, z]", "default": [0, 0, 0]},
            "rotation": {"type": "array[number]", "required": False, "description": "Rotation [x, y, z] in degrees", "default": [0, 0, 0]},
            "scale": {"type": "array[number]", "required": False, "description": "Scale [x, y, z]", "default": [1, 1, 1]},
        },
    },
}
