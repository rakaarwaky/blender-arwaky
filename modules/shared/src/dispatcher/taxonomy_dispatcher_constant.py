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
        "list_scene_objects": {
            "description": "List scene objects with optional visibility and type filters",
            "parameters": {
                "include_hidden": {
                    "type": "boolean",
                    "required": False,
                    "default": False,
                },
                "object_type": {
                    "type": "string",
                    "required": False,
                    "description": "Optional Blender object type filter",
                },
                "limit": {
                    "type": "integer",
                    "required": False,
                    "default": 100,
                },
            },
        },
        "get_object_hierarchy": {
            "description": "Inspect parent-child hierarchy for one object or the scene roots",
            "parameters": {
                "object_name": {
                    "type": "string",
                    "required": False,
                },
                "include_hidden": {
                    "type": "boolean",
                    "required": False,
                    "default": False,
                },
                "max_depth": {
                    "type": "integer",
                    "required": False,
                    "default": 32,
                },
            },
        },
        "undo": {
            "description": "Undo the most recent Blender edit operation",
            "parameters": {},
        },
        "redo": {
            "description": "Redo the most recently undone Blender edit operation",
            "parameters": {},
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
        "create_material": {
            "description": "Create or reuse a PBR material",
            "parameters": {
                "material_name": {
                    "type": "string",
                    "required": True,
                },
                "base_color": {
                    "type": "array[number]",
                    "required": False,
                    "description": "RGBA color channels in the range 0-1",
                    "default": [0.8, 0.8, 0.8, 1.0],
                },
                "metallic": {
                    "type": "number",
                    "required": False,
                    "default": 0.0,
                },
                "roughness": {
                    "type": "number",
                    "required": False,
                    "default": 0.5,
                },
                "reuse_existing": {
                    "type": "boolean",
                    "required": False,
                    "default": True,
                },
            },
        },
        "set_material_properties": {
            "description": "Update PBR properties of an existing material",
            "parameters": {
                "material_name": {
                    "type": "string",
                    "required": True,
                },
                "base_color": {
                    "type": "array[number]",
                    "required": False,
                },
                "metallic": {
                    "type": "number",
                    "required": False,
                },
                "roughness": {
                    "type": "number",
                    "required": False,
                },
            },
        },
        "set_material_texture": {
            "description": "Assign a local image texture to a material base color",
            "parameters": {
                "material_name": {
                    "type": "string",
                    "required": True,
                },
                "file_path": {
                    "type": "string",
                    "required": True,
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
    "geometry_nodes": {
        "inspect_geometry_node_group": {
            "description": "Inspect a Geometry Nodes group with bounded node, socket, and link metadata",
            "parameters": {
                "node_group_name": {"type": "string", "required": True},
            },
        },
        "create_geometry_node_group": {
            "description": "Create or reuse a Geometry Nodes group and optionally bind it to an object modifier",
            "parameters": {
                "node_group_name": {"type": "string", "required": True},
                "object_name": {"type": "string", "required": False},
            },
        },
        "set_geometry_node_link": {
            "description": "Create a validated link between sockets in a Geometry Nodes group",
            "parameters": {
                "node_group_name": {"type": "string", "required": True},
                "from_node": {"type": "string", "required": True},
                "from_socket": {"type": "string", "required": True},
                "to_node": {"type": "string", "required": True},
                "to_socket": {"type": "string", "required": True},
            },
        },
        "set_geometry_node_modifier": {
            "description": "Bind an existing Geometry Nodes group to an object modifier",
            "parameters": {
                "object_name": {"type": "string", "required": True},
                "node_group_name": {"type": "string", "required": True},
            },
        },
    },
    "animation": {
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
    },
    "mesh": {
        "get_mesh_statistics": {
            "description": "Inspect bounded mesh vertex, edge, polygon, normal, and UV statistics",
            "parameters": {
                "object_name": {"type": "string", "required": True},
            },
        },
        "validate_mesh": {
            "description": "Run bounded mesh validation for loose, degenerate, and non-manifold geometry",
            "parameters": {
                "object_name": {"type": "string", "required": True},
                "limit": {"type": "integer", "required": False, "default": 100},
            },
        },
        "perform_mesh_edit_operation": {
            "description": "Perform one bounded edit-mode-independent mesh cleanup operation",
            "parameters": {
                "object_name": {"type": "string", "required": True},
                "operation": {
                    "type": "string",
                    "required": True,
                    "enum": ["recalculate_normals", "triangulate", "remove_doubles"],
                },
            },
        },
        "ensure_mesh_uv_layer": {
            "description": "Create or reuse a named UV layer on a mesh object",
            "parameters": {
                "object_name": {"type": "string", "required": True},
                "uv_layer_name": {"type": "string", "required": False, "default": "UVMap"},
            },
        },
    },
    "render": {
        "configure_camera": {
            "description": "Configure a Blender camera and optional depth of field",
            "parameters": {
                "camera_ref": {"type": "string", "required": False},
                "focal_length": {"type": "number", "required": False, "default": 50.0},
                "sensor_fit": {
                    "type": "string",
                    "required": False,
                    "enum": ["AUTO", "HORIZONTAL", "VERTICAL"],
                    "default": "AUTO",
                },
                "framing_target": {"type": "string", "required": False},
                "set_active": {"type": "boolean", "required": False, "default": False},
                "depth_of_field_enabled": {"type": "boolean", "required": False, "default": False},
                "focus_distance": {"type": "number", "required": False},
                "focus_object": {"type": "string", "required": False},
                "aperture": {"type": "number", "required": False, "default": 2.8},
                "create_if_missing": {"type": "boolean", "required": False, "default": True},
            },
        },
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
        "set_render_settings": {
            "description": "Configure bounded scene render settings without rendering",
            "parameters": {
                "engine": {
                    "type": "string",
                    "required": False,
                    "description": "Blender render engine identifier",
                },
                "resolution_x": {
                    "type": "integer",
                    "required": False,
                    "default": 1920,
                },
                "resolution_y": {
                    "type": "integer",
                    "required": False,
                    "default": 1080,
                },
                "resolution_percentage": {
                    "type": "integer",
                    "required": False,
                    "default": 100,
                },
                "samples": {
                    "type": "integer",
                    "required": False,
                },
                "use_transparent": {
                    "type": "boolean",
                    "required": False,
                },
            },
        },
    },
    "compositor": {
        "inspect_compositor_nodes": {
            "description": "Inspect a bounded compositor node graph for the active scene",
            "parameters": {
                "limit": {"type": "integer", "required": False, "default": 100},
            },
        },
        "configure_compositor": {
            "description": "Enable or disable compositor nodes for the active scene",
            "parameters": {
                "use_nodes": {"type": "boolean", "required": True},
            },
        },
        "create_compositor_node": {
            "description": "Create one allow-listed compositor node in the active scene",
            "parameters": {
                "node_type": {
                    "type": "string",
                    "required": True,
                    "enum": [
                        "CompositorNodeRGB",
                        "CompositorNodeMixRGB",
                        "CompositorNodeBlur",
                        "CompositorNodeComposite",
                        "CompositorNodeViewer",
                    ],
                },
                "node_name": {"type": "string", "required": False},
            },
        },
        "set_compositor_link": {
            "description": "Create a validated link between compositor node sockets",
            "parameters": {
                "from_node": {"type": "string", "required": True},
                "from_socket": {"type": "string", "required": True},
                "to_node": {"type": "string", "required": True},
                "to_socket": {"type": "string", "required": True},
            },
        },
    },
    "vse": {
        "inspect_sequence_editor": {
            "description": "Inspect bounded VSE strips and channels for the active scene",
            "parameters": {
                "limit": {"type": "integer", "required": False, "default": 100},
            },
        },
        "create_sequence_strip": {
            "description": "Create an allow-listed VSE strip from a validated local media path",
            "parameters": {
                "strip_type": {
                    "type": "string",
                    "required": True,
                    "enum": ["COLOR", "IMAGE", "MOVIE", "SOUND"],
                },
                "strip_name": {"type": "string", "required": True},
                "filepath": {"type": "string", "required": False},
                "channel": {"type": "integer", "required": True},
                "frame_start": {"type": "integer", "required": True},
                "frame_end": {"type": "integer", "required": False},
            },
        },
        "remove_sequence_strip": {
            "description": "Remove one named VSE strip from the active scene",
            "parameters": {
                "strip_name": {"type": "string", "required": True},
            },
            "metadata": {"destructive_flag": True, "risk_level": "high"},
        },
        "render_sequence": {
            "description": "Render a bounded VSE frame range to a validated local output path",
            "parameters": {
                "output_path": {"type": "string", "required": True},
                "frame_start": {"type": "integer", "required": False},
                "frame_end": {"type": "integer", "required": False},
            },
            "metadata": {
                "default_timeout": 300.0,
                "timeout_class": "long_running",
                "background_eligibility_flag": True,
                "long_running_flag": True,
                "risk_level": "high",
            },
        },
    },
    "physics": {
        "get_physics_state": {
            "description": "Inspect bounded rigid body and cloth state for one object",
            "parameters": {
                "object_name": {"type": "string", "required": True},
            },
        },
        "configure_rigid_body": {
            "description": "Configure rigid body simulation settings for one mesh object",
            "parameters": {
                "object_name": {"type": "string", "required": True},
                "enabled": {"type": "boolean", "required": True},
                "body_type": {"type": "string", "required": False, "enum": ["ACTIVE", "PASSIVE"]},
                "mass": {"type": "number", "required": False},
                "kinematic": {"type": "boolean", "required": False},
            },
        },
        "configure_cloth_simulation": {
            "description": "Configure bounded cloth simulation settings for one mesh object",
            "parameters": {
                "object_name": {"type": "string", "required": True},
                "enabled": {"type": "boolean", "required": True},
                "quality": {"type": "integer", "required": False},
                "pin_group": {"type": "string", "required": False},
            },
        },
        "bake_physics_simulation": {
            "description": "Bake a bounded physics cache for the active scene",
            "parameters": {
                "frame_start": {"type": "integer", "required": False},
                "frame_end": {"type": "integer", "required": False},
            },
            "metadata": {
                "default_timeout": 300.0,
                "timeout_class": "long_running",
                "background_eligibility_flag": True,
                "long_running_flag": True,
                "destructive_flag": True,
                "risk_level": "high",
            },
        },
        "clear_physics_bake": {
            "description": "Clear cached physics simulation data for the active scene",
            "parameters": {},
            "metadata": {"destructive_flag": True, "risk_level": "high"},
        },
        "get_simulation_state": {
            "description": "Inspect bounded advanced simulation modifiers for one object",
            "parameters": {
                "object_name": {"type": "string", "required": True},
            },
        },
        "get_simulation_cache_status": {
            "description": "Inspect bounded physics cache range and bake state for the active scene",
            "parameters": {},
        },
        "configure_particle_system": {
            "description": "Configure one bounded particle system on a mesh object",
            "parameters": {
                "object_name": {"type": "string", "required": True},
                "enabled": {"type": "boolean", "required": True},
                "count": {"type": "integer", "required": False},
                "frame_start": {"type": "integer", "required": False},
                "frame_end": {"type": "integer", "required": False},
                "lifetime": {"type": "number", "required": False},
                "physics_type": {
                    "type": "string",
                    "required": False,
                    "enum": ["NEWTON", "KEYED", "BOIDS", "FLUID"],
                },
            },
        },
        "configure_force_field": {
            "description": "Configure a bounded force field on an existing object",
            "parameters": {
                "object_name": {"type": "string", "required": True},
                "enabled": {"type": "boolean", "required": True},
                "field_type": {
                    "type": "string",
                    "required": False,
                    "enum": ["FORCE", "WIND", "VORTEX", "MAGNET", "TURBULENCE"],
                },
                "strength": {"type": "number", "required": False},
                "noise": {"type": "number", "required": False},
            },
        },
        "configure_fluid_domain": {
            "description": "Configure a bounded fluid domain modifier baseline on a mesh object",
            "parameters": {
                "object_name": {"type": "string", "required": True},
                "enabled": {"type": "boolean", "required": True},
                "domain_type": {"type": "string", "required": False, "enum": ["LIQUID", "GAS"]},
                "resolution": {"type": "integer", "required": False},
                "cache_type": {"type": "string", "required": False, "enum": ["REPLAY", "MODULAR", "FINAL"]},
            },
        },
    },
    "rigging": {
        "inspect_armature": {
            "description": "Inspect a bounded armature bone hierarchy and pose summary",
            "parameters": {
                "object_name": {"type": "string", "required": True},
                "limit": {"type": "integer", "required": False, "default": 100},
            },
        },
        "set_pose_bone_transform": {
            "description": "Set a bounded transform on one named pose bone",
            "parameters": {
                "armature_name": {"type": "string", "required": True},
                "bone_name": {"type": "string", "required": True},
                "location": {"type": "array[number]", "required": False},
                "rotation_euler": {"type": "array[number]", "required": False},
                "scale": {"type": "array[number]", "required": False},
            },
        },
        "configure_bone_constraint": {
            "description": "Create, update, or remove one allow-listed bone constraint",
            "parameters": {
                "armature_name": {"type": "string", "required": True},
                "bone_name": {"type": "string", "required": True},
                "constraint_type": {
                    "type": "string",
                    "required": True,
                    "enum": ["COPY_LOCATION", "COPY_ROTATION", "LIMIT_LOCATION", "LIMIT_ROTATION"],
                },
                "enabled": {"type": "boolean", "required": True},
                "constraint_name": {"type": "string", "required": False},
                "target_object": {"type": "string", "required": False},
                "subtarget": {"type": "string", "required": False},
            },
        },
        "configure_shape_key": {
            "description": "Create, update, or remove one bounded mesh shape key",
            "parameters": {
                "object_name": {"type": "string", "required": True},
                "shape_key_name": {"type": "string", "required": True},
                "enabled": {"type": "boolean", "required": True},
                "value": {"type": "number", "required": False},
                "slider_min": {"type": "number", "required": False},
                "slider_max": {"type": "number", "required": False},
            },
        },
        "get_deformation_state": {
            "description": "Inspect bounded deformation modifiers, constraints, and shape keys",
            "parameters": {
                "object_name": {"type": "string", "required": True},
            },
        },
    },
    "asset": {
        "search_assets": {
            "description": "Search configured asset providers",
            "parameters": {
                "query": {"type": "string", "required": False, "default": "curated"},
                "providers": {"type": "array[string]", "required": False},
                "asset_type_filter": {"type": "string", "required": False},
                "limit": {"type": "integer", "required": False},
                "page_token": {"type": "string", "required": False},
            },
        },
        "get_provider_metadata": {
            "description": "Get normalized metadata for a provider asset",
            "parameters": {
                "provider": {"type": "string", "required": True},
                "asset_id": {"type": "string", "required": True},
            },
        },
        "download_asset": {
            "description": "Download a provider asset into the validated local cache",
            "parameters": {
                "provider": {"type": "string", "required": True},
                "asset_id": {"type": "string", "required": True},
                "asset_type": {"type": "string", "required": True},
                "cache_dir": {"type": "string", "required": True},
                "resolution": {"type": "string", "required": False},
                "overwrite_policy": {"type": "string", "required": False, "default": "reuse"},
                "max_size": {"type": "integer", "required": False},
                "background": {"type": "boolean", "required": False, "default": False},
            },
        },
        "extract_asset": {
            "description": "Safely extract a downloaded asset archive",
            "parameters": {
                "artifact_path": {"type": "string", "required": True},
                "destination": {"type": "string", "required": True},
                "max_entries": {"type": "integer", "required": False},
                "max_extracted_size": {"type": "integer", "required": False},
                "allow_symlinks": {"type": "boolean", "required": False, "default": False},
            },
        },
        "import_asset": {
            "description": "Import a locally cached asset into Blender",
            "parameters": {
                "file_path": {"type": "string", "required": True},
                "asset_type": {"type": "string", "required": True},
                "target_collection": {"type": "string", "required": False},
                "scale_normalization": {"type": "boolean", "required": False, "default": False},
                "duplicate_policy": {"type": "string", "required": False, "default": "rename"},
                "format_hint": {"type": "string", "required": False},
            },
        },
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
        "submit_task": {
            "description": "Register a background task through the shared job lifecycle",
            "parameters": {
                "operation_type": {
                    "type": "string",
                    "required": True,
                },
                "correlation_id": {
                    "type": "string",
                    "required": False,
                },
                "metadata": {
                    "type": "any",
                    "required": False,
                },
            },
        },
        "list_tasks": {
            "description": "List current and retained background task snapshots",
            "parameters": {},
        },
        "get_capacity_status": {
            "description": "Return background task capacity and available slots",
            "parameters": {},
        },
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
