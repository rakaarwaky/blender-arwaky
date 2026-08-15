"""Dispatcher taxonomy — Action schema constants.

All action schemas consolidated from surface_*_action.py files.
Taxonomy layer: pure constants only — no functions, loops, classes, or I/O.
"""

from __future__ import annotations

DISPATCHER_ACTION_SCHEMAS: dict[str, dict[str, dict[str, object]]] = {
    "gateway": {
        "execute_blender_code": {
            "description": "Execute validated Blender Python code",
            "parameters": {
                "code": {
                    "type": "string",
                    "required": True,
                    "description": "Blender Python source code",
                },
            },
        },
    },
    "scene": {
        "get_scene_info": {
            "description": "Full scene metadata — object count, frame range, resolution, render engine",
            "parameters": {},
        },
        "cleanup_scene": {
            "description": "Remove objects from scene by mode",
            "parameters": {
                "mode": {
                    "type": "string",
                    "required": True,
                    "description": "Cleanup scope",
                    "enum": ["all", "objects", "meshes"],
                },
            },
        },
    },
    "object": {
        "get_object_info": {
            "description": "Get details of a specific object — location, rotation, scale, modifiers, materials",
            "parameters": {
                "object_name": {
                    "type": "string",
                    "required": True,
                    "description": "Name of the target object",
                },
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
                "location": {
                    "type": "array[number]",
                    "required": False,
                    "description": "Position [x, y, z]",
                    "default": [0, 0, 0],
                },
                "scale": {
                    "type": "array[number]",
                    "required": False,
                    "description": "Scale [x, y, z]",
                    "default": [1, 1, 1],
                },
                "name": {
                    "type": "string",
                    "required": False,
                    "description": "Custom object name",
                },
            },
        },
        "set_object_transform": {
            "description": "Update object transform — location, rotation, or scale",
            "parameters": {
                "object_name": {
                    "type": "string",
                    "required": True,
                    "description": "Name of the target object",
                },
                "location": {
                    "type": "array[number]",
                    "required": False,
                    "description": "Position [x, y, z]",
                },
                "rotation": {
                    "type": "array[number]",
                    "required": False,
                    "description": "Rotation [x, y, z] in degrees",
                },
                "scale": {
                    "type": "array[number]",
                    "required": False,
                    "description": "Scale [x, y, z]",
                },
            },
        },
        "delete_object": {
            "description": "Remove an object from the scene",
            "parameters": {
                "object_name": {
                    "type": "string",
                    "required": True,
                    "description": "Name of the object to delete",
                },
            },
        },
        "set_material": {
            "description": "Assign a material to an object",
            "parameters": {
                "object_name": {
                    "type": "string",
                    "required": True,
                    "description": "Name of the target object",
                },
                "material_name": {
                    "type": "string",
                    "required": True,
                    "description": "Name of the material to assign",
                },
            },
        },
        "apply_modifier": {
            "description": "Apply a modifier on an object",
            "parameters": {
                "object_name": {
                    "type": "string",
                    "required": True,
                    "description": "Name of the target object",
                },
                "modifier_name": {
                    "type": "string",
                    "required": True,
                    "description": "Name of the modifier to apply",
                },
            },
        },
    },
    "render": {
        "setup_environment": {
            "description": "Configure HDRI lighting using a local file resolved by the Asset feature",
            "parameters": {
                "hdri_id": {
                    "type": "string",
                    "required": True,
                    "description": "Absolute or project-local path to an already cached .hdr or .exr asset",
                },
                "strength": {
                    "type": "number",
                    "required": False,
                    "description": "Environment light strength in the inclusive range 0-10",
                    "default": 1.0,
                },
            },
        },
        "get_viewport_screenshot": {
            "description": "Capture AI-optimized viewport screenshot",
            "parameters": {
                "filepath": {
                    "type": "string",
                    "required": False,
                    "description": "Output path for screenshot",
                },
                "max_size": {
                    "type": "integer",
                    "required": False,
                    "description": "Maximum dimension in pixels",
                    "default": 800,
                },
                "view_angle": {
                    "type": "string",
                    "required": False,
                    "description": "Camera view angle",
                    "enum": ["PERSPECTIVE", "TOP", "FRONT", "SIDE"],
                    "default": "PERSPECTIVE",
                },
                "shading_mode": {
                    "type": "string",
                    "required": False,
                    "description": "Viewport shading mode",
                    "enum": ["WIREFRAME", "SOLID", "MATERIAL", "RENDERED"],
                    "default": "MATERIAL",
                },
                "show_overlays": {
                    "type": "boolean",
                    "required": False,
                    "description": "Show viewport overlays",
                    "default": True,
                },
                "focus_object": {
                    "type": "string",
                    "required": False,
                    "description": "Object name to frame in viewport",
                },
            },
        },
        "render": {
            "description": "Execute a full frame render",
            "parameters": {
                "output_path": {
                    "type": "string",
                    "required": True,
                    "description": "Output path for rendered image",
                },
                "resolution_x": {
                    "type": "integer",
                    "required": False,
                    "description": "Render width in pixels",
                    "default": 1920,
                },
                "resolution_y": {
                    "type": "integer",
                    "required": False,
                    "description": "Render height in pixels",
                    "default": 1080,
                },
            },
        },
    },
    "asset": {
        "import_glb": {
            "description": "Import a GLB/GLTF file into the scene",
            "parameters": {
                "file_path": {
                    "type": "string",
                    "required": True,
                    "description": "Path to the GLB/GLTF file",
                },
                "object_name": {
                    "type": "string",
                    "required": False,
                    "description": "Custom name for the imported object",
                },
            },
        },
        "export_model": {
            "description": "Export a model to a file",
            "parameters": {
                "object_name": {
                    "type": "string",
                    "required": True,
                    "description": "Name of the object to export",
                },
                "file_path": {
                    "type": "string",
                    "required": True,
                    "description": "Output path for the exported file",
                },
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
                "asset_id": {
                    "type": "string",
                    "required": True,
                    "description": "Asset identifier",
                },
                "location": {
                    "type": "array[number]",
                    "required": False,
                    "description": "Position [x, y, z]",
                    "default": [0, 0, 0],
                },
                "rotation": {
                    "type": "array[number]",
                    "required": False,
                    "description": "Rotation [x, y, z] in degrees",
                    "default": [0, 0, 0],
                },
                "scale": {
                    "type": "array[number]",
                    "required": False,
                    "description": "Scale [x, y, z]",
                    "default": [1, 1, 1],
                },
            },
        },
    },
    "launcher": {
        "launch_blender": {
            "description": "Start Blender with integration component active",
            "parameters": {
                "filepath": {
                    "type": "string",
                    "required": False,
                    "description": "Optional .blend file to open",
                },
                "mode": {
                    "type": "string",
                    "required": False,
                    "description": "Blender launch mode",
                    "enum": ["interface", "headless"],
                    "default": "headless",
                },
                "port": {
                    "type": "integer",
                    "required": False,
                    "description": "TCP port for addon communication",
                    "default": 9876,
                },
            },
        },
        "shutdown_blender": {
            "description": "Gracefully shut down Blender with force termination fallback",
            "parameters": {
                "force": {
                    "type": "boolean",
                    "required": False,
                    "description": "Skip graceful shutdown and force terminate",
                    "default": False,
                },
            },
        },
        "get_runtime_status": {
            "description": "Verify true Blender process liveness and readiness",
            "parameters": {},
        },
        "register_executable": {
            "description": "Locate and register the Blender executable path",
            "parameters": {
                "path": {
                    "type": "string",
                    "required": False,
                    "description": "Explicit path to Blender executable",
                },
            },
        },
    },
    "job": {
        "get_task_status": {
            "description": "Query the progress and status of a background task",
            "parameters": {
                "task_id": {
                    "type": "string",
                    "required": True,
                    "description": "Task identifier returned from a previous submit action",
                },
            },
        },
        "cancel_task": {
            "description": "Cancel a running background task",
            "parameters": {
                "task_id": {
                    "type": "string",
                    "required": True,
                    "description": "Task identifier of the task to cancel",
                },
            },
        },
    },
    "config": {
        "get_config": {
            "description": "Retrieve BlenderArwaky configuration settings",
            "parameters": {
                "key": {
                    "type": "string",
                    "required": False,
                    "description": "Specific config key to retrieve. Omit for all settings.",
                },
            },
        },
        "set_config": {
            "description": "Update a configuration setting",
            "parameters": {
                "key": {
                    "type": "string",
                    "required": True,
                    "description": "Config key to update",
                },
                "value": {
                    "type": "any",
                    "required": True,
                    "description": "New value for the config key",
                },
            },
        },
    },
}
