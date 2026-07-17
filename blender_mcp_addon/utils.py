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


def get_viewport_screenshot(filepath):
    """
    Captures a screenshot of the current viewport.

    Headless: requires active camera, uses EEVEE for speed.
    GUI: uses OpenGL viewport render (no camera needed).

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

        # Set render settings for quick screenshot
        bpy.context.scene.render.image_settings.file_format = "PNG"
        bpy.context.scene.render.filepath = filepath

        # Use EEVEE for fast headless capture (override Cycles if set)
        original_engine = bpy.context.scene.render.engine
        bpy.context.scene.render.engine = "BLENDER_EEVEE"

        bpy.ops.render.render(write_still=True)

        # Restore engine
        bpy.context.scene.render.engine = original_engine
    else:
        # GUI mode: OpenGL render captures viewport as-is
        bpy.ops.render.render(write_still=True)
        render_path = bpy.context.scene.render.frame_path()
        if os.path.exists(render_path):
            shutil.move(render_path, filepath)

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
