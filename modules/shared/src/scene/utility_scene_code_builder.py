"""Scene utility: Blender code builders.

Stateless technical functions that generate Blender Python code.
"""

from __future__ import annotations

from ..common.taxonomy_core_vo import PythonCode
from .taxonomy_scene_constant import (
    CHILD_POLICY_REJECT,
    CLEANUP_MODE_ALL,
    CLEANUP_MODE_MESHES,
    CLEANUP_MODE_OBJECTS,
)
from .taxonomy_scene_vo import SceneCleanupPolicyVO, SceneInspectionVO


def build_inspection_code(request: SceneInspectionVO) -> PythonCode:
    """Build Blender inspection code."""
    include_hidden = bool(request.include_hidden_objects)

    lines = [
        "import bpy",
        "import json",
        "",
        "scene = bpy.context.scene",
        "view_layer = bpy.context.view_layer",
        f"include_hidden = {include_hidden!r}",
        "",
        "objects_by_type = {{}}",
        "visible_count = 0",
        "hidden_count = 0",
        "cameras = []",
        "lights = []",
        "",
        "for obj in scene.objects:",
        "    is_hidden = bool(obj.hide_viewport)",
        "    if is_hidden:",
        "        hidden_count += 1",
        "    else:",
        "        visible_count += 1",
        "",
        "    if not include_hidden and is_hidden:",
        "        continue",
        "",
        "    obj_type = obj.type",
        "    objects_by_type[obj_type] = objects_by_type.get(obj_type, 0) + 1",
        "",
        "    if obj_type == 'CAMERA':",
        "        cameras.append({",
        "            'name': obj.name,",
        "            'type': 'perspective' if obj.data.type == 'PERSP' else 'orthographic'",
        "        })",
        "",
        "    elif obj_type == 'LIGHT':",
        "        lights.append({",
        "            'name': obj.name,",
        "            'light_type': obj.data.type.lower()",
        "        })",
        "",
        "result = {{",
        "    'scene_name': scene.name,",
        "    'total_object_count': len(scene.objects),",
        "    'visible_object_count': visible_count,",
        "    'hidden_object_count': hidden_count,",
        "    'object_type_counts': objects_by_type,",
        "    'cameras': cameras,",
        "    'lights': lights,",
        "    'active_camera_name': bpy.context.scene.camera.name if bpy.context.scene.camera else '',",
        "    'active_object_name': view_layer.objects.active.name if view_layer.objects.active else '',",
        "    'render_engine': scene.render.engine.lower(),",
        "    'resolution_x': scene.render.resolution_x,",
        "    'resolution_y': scene.render.resolution_y,",
        "    'frame_start': scene.frame_start,",
        "    'frame_end': scene.frame_end,",
        "    'unit_system': scene.unit_system.lower(),",
        "    'collections': [{{'name': c.name, 'object_count': len(c.objects)}} for c in scene.collection.children]",
        "}}",
        "print(json.dumps(result))",
    ]

    return PythonCode("\n".join(lines))


def build_cleanup_execution_code(request: SceneCleanupPolicyVO) -> PythonCode:
    """Build Blender cleanup execution code."""
    mode = request.mode or CLEANUP_MODE_ALL
    preserve_list = request.preservation_list or []

    lines = [
        "import bpy",
        "import json",
        "",
        "scene = bpy.context.scene",
        "view_layer = bpy.context.view_layer",
        f"cleanup_mode = '{mode}'",
        f"preserve_list = {preserve_list!r}",
        "",
        "removed_count = 0",
        "preserved_count = 0",
        "skipped_count = 0",
        "removed_refs = []",
        "preserved_refs = []",
        "skipped_refs = []",
        "",
        "def should_preserve(obj):",
        "    obj_type = obj.type",
        "    if obj_type == 'CAMERA':",
        "        return True",
        "    if obj_type == 'LIGHT':",
        "        return True",
        "    if obj.name == bpy.context.scene.camera.name if bpy.context.scene.camera else False:",
        "        return True",
        "    for preserve_name in preserve_list:",
        "        if obj.name.lower().startswith(preserve_name.lower()):",
        "            return True",
        "    return False",
        "",
        "for obj in scene.objects:",
        "    try:",
        "        if should_preserve(obj):",
        "            preserved_count += 1",
        "            preserved_refs.append(obj.name)",
        "        else:",
        "            view_layer.objects.unlink(obj)",
        "            bpy.data.objects.remove(obj)",
        "            removed_count += 1",
        "            removed_refs.append(obj.name)",
        "    except Exception as e:",
        "        skipped_count += 1",
        "        skipped_refs.append(obj.name)",
        "",
        "result = {{",
        "    'removed_count': removed_count,",
        "    'preserved_count': preserved_count,",
        "    'skipped_count': skipped_count,",
        "    'removed_refs': removed_refs,",
        "    'preserved_refs': preserved_refs,",
        "    'skipped_refs': skipped_refs",
        "}}",
        "print(json.dumps(result))",
    ]

    return PythonCode("\n".join(lines))


def build_cleanup_preview_code(request: SceneCleanupPolicyVO) -> PythonCode:
    """Build Blender cleanup preview (dry-run) code."""
    mode = request.mode or CLEANUP_MODE_ALL
    preserve_list = request.preservation_list or []

    lines = [
        "import bpy",
        "import json",
        "",
        "scene = bpy.context.scene",
        f"cleanup_mode = '{mode}'",
        f"preserve_list = {preserve_list!r}",
        "",
        "candidates_count = 0",
        "preserved_count = 0",
        "candidates_refs = []",
        "preserved_refs = []",
        "",
        "def should_preserve(obj):",
        "    obj_type = obj.type",
        "    if obj_type == 'CAMERA':",
        "        return True",
        "    if obj_type == 'LIGHT':",
        "        return True",
        "    if obj.name == bpy.context.scene.camera.name if bpy.context.scene.camera else False:",
        "        return True",
        "    for preserve_name in preserve_list:",
        "        if obj.name.lower().startswith(preserve_name.lower()):",
        "            return True",
        "    return False",
        "",
        "for obj in scene.objects:",
        "    if should_preserve(obj):",
        "        preserved_count += 1",
        "        preserved_refs.append(obj.name)",
        "    else:",
        "        candidates_count += 1",
        "        candidates_refs.append(obj.name)",
        "",
        "result = {{",
        "    'removed_count': candidates_count,",
        "    'preserved_count': preserved_count,",
        "    'skipped_count': 0,",
        "    'removed_refs': candidates_refs,",
        "    'preserved_refs': preserved_refs,",
        "    'skipped_refs': []",
        "}}",
        "print(json.dumps(result))",
    ]

    return PythonCode("\n".join(lines))
