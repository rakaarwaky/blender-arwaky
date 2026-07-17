import logging
import os
import shutil

import bpy  # type: ignore
import mathutils  # type: ignore

logger = logging.getLogger(__name__)


def _get_aabb(obj):
    """Calculate axis-aligned bounding box for an object in world space."""
    matrix = obj.matrix_world
    if obj.type == "MESH":
        coords = [matrix @ mathutils.Vector(v.co) for v in obj.data.vertices]
    else:
        coords = [matrix @ mathutils.Vector(v) for v in obj.bound_box]

    if not coords:
        return (0, 0, 0, 0, 0, 0)

    min_x = min(c[0] for c in coords)
    max_x = max(c[0] for c in coords)
    min_y = min(c[1] for c in coords)
    max_y = max(c[1] for c in coords)
    min_z = min(c[2] for c in coords)
    max_z = max(c[2] for c in coords)

    return (min_x, max_x, min_y, max_y, min_z, max_z)


def get_viewport_screenshot(
    filepath,
    view_angle="PERSPECTIVE",
    shading_mode="MATERIAL",
    show_overlays=True,
    focus_object=None,
):
    """
    Captures a screenshot of the current viewport with AI agent optimizations.

    Args:
        filepath: Output path for the screenshot
        view_angle: PERSPECTIVE, TOP, FRONT, or SIDE
        shading_mode: WIREFRAME, SOLID, MATERIAL, or RENDERED
        show_overlays: Whether to show viewport overlays (grid, axes, etc.)
        focus_object: Object name to frame in viewport before capture

    Returns dict with filepath, width, height for response metadata.
    """
    is_headless = bpy.app.background

    if is_headless:
        camera = bpy.context.scene.camera
        if not camera:
            raise RuntimeError(
                "No active camera in scene. "
                "Set an active camera before taking headless screenshots."
            )

        # Save and apply viewport settings for AI optimization
        space_data = None
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                space_data = area.spaces.active
                break

        if space_data:
            original_shading = space_data.shading.type
            original_overlays = space_data.overlay.show_overlays

            # Apply shading mode
            if shading_mode in ("WIREFRAME", "SOLID", "MATERIAL", "RENDERED"):
                space_data.shading.type = shading_mode

            # Apply overlay setting
            space_data.overlay.show_overlays = show_overlays

        # Focus on specific object if requested
        if focus_object:
            obj = bpy.data.objects.get(focus_object)
            if obj:
                bpy.context.view_layer.objects.active = obj
                obj.select_set(True)
                bpy.ops.view3d.view_selected(use_all_regions=False)

        # Set render settings for quick screenshot
        bpy.context.scene.render.image_settings.file_format = "PNG"
        bpy.context.scene.render.filepath = filepath

        # Use EEVEE for fast headless capture (override Cycles if set)
        original_engine = bpy.context.scene.render.engine
        bpy.context.scene.render.engine = "BLENDER_EEVEE"

        bpy.ops.render.render(write_still=True)

        # Restore engine
        bpy.context.scene.render.engine = original_engine

        # Restore viewport settings
        if space_data:
            space_data.shading.type = original_shading
            space_data.overlay.show_overlays = original_overlays
    else:
        # GUI mode: apply viewport overrides temporarily
        space_data = None
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                space_data = area.spaces.active
                break

        if space_data:
            original_shading = space_data.shading.type
            original_overlays = space_data.overlay.show_overlays

            # Apply shading mode
            if shading_mode in ("WIREFRAME", "SOLID", "MATERIAL", "RENDERED"):
                space_data.shading.type = shading_mode

            # Apply overlay setting
            space_data.overlay.show_overlays = show_overlays

        # Focus on specific object if requested
        if focus_object:
            obj = bpy.data.objects.get(focus_object)
            if obj:
                bpy.context.view_layer.objects.active = obj
                obj.select_set(True)
                bpy.ops.view3d.view_selected(use_all_regions=False)

        # Apply view angle
        view_map = {
            "TOP": "TOP",
            "FRONT": "FRONT",
            "SIDE": "SIDE",
        }
        if view_angle in view_map:
            bpy.ops.view3d.viewnumpad(type=view_map[view_angle])

        # Take screenshot
        bpy.ops.render.render(write_still=True)
        render_path = bpy.context.scene.render.frame_path()
        if os.path.exists(render_path):
            shutil.move(render_path, filepath)

        # Restore viewport settings
        if space_data:
            space_data.shading.type = original_shading
            space_data.overlay.show_overlays = original_overlays

    # Return actual render dimensions
    scene = bpy.context.scene
    return {
        "filepath": filepath,
        "width": scene.render.resolution_x,
        "height": scene.render.resolution_y,
    }


def clean_imported_glb(filepath, mesh_name=None):
    """Imports a GLB, finds the mesh, and renames it. Returns the mesh object."""
    existing_objects = set(bpy.data.objects.keys())
    bpy.ops.import_scene.gltf(filepath=filepath)
    bpy.context.view_layer.update()

    new_objects = [bpy.data.objects[name] for name in set(bpy.data.objects.keys()) - existing_objects]
    if not new_objects:
        return None

    # Find the main mesh
    mesh_obj = next((o for o in new_objects if o.type == "MESH"), None)
    if not mesh_obj:
        # Check children of empty nodes (common in GLTF imports)
        for o in new_objects:
            if o.type == "EMPTY" and o.children:
                mesh_obj = next((c for c in o.children if c.type == "MESH"), None)
                if mesh_obj:
                    mesh_obj.parent = None
                    bpy.data.objects.remove(o)
                    break

    if mesh_obj and mesh_name:
        mesh_obj.name = mesh_name
        if mesh_obj.data:
            mesh_obj.data.name = mesh_name

    return mesh_obj
