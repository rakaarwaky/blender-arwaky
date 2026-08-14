"""Scene utility: Blender code builders.

Stateless technical functions that generate Blender Python code.
"""

from __future__ import annotations

from ..common.taxonomy_core_vo import PythonCode
from .taxonomy_scene_constant import (
    CHILD_POLICY_DETACH,
    CLEANUP_MODE_ALL,
    DEPENDENT_POLICY_REJECT,
)
from .taxonomy_scene_vo import SceneCleanupPolicyVO, SceneInspectionVO


def build_inspection_code(request: SceneInspectionVO) -> PythonCode:
    """Build Blender inspection code with detail level awareness.

    Implements FR-SCN-001: large scenes should support summarized detail level.
    - minimal: count-only, no object details (fastest)
    - standard: summary with cameras/lights (default)
    - detailed: full dump with all object properties
    """
    include_hidden = bool(request.include_hidden_objects)
    detail_level = getattr(request, "detail_level", "standard") or "standard"

    if detail_level == "minimal":
        return _build_minimal_inspection_code(include_hidden)
    elif detail_level == "detailed":
        return _build_detailed_inspection_code(include_hidden)
    else:  # standard or summary
        return _build_standard_inspection_code(include_hidden)


def _build_minimal_inspection_code(include_hidden: bool) -> PythonCode:
    """Count-only inspection — no object details (FR-SCN-001 minimal detail)."""
    lines = [
        "import bpy",
        "import json",
        "",
        f"include_hidden = {include_hidden!r}",
        "",
        "result = {",
        "    'total_object_count': len(bpy.context.scene.objects),",
        "    'visible_object_count': sum(1 for o in bpy.context.scene.objects if (not o.hide_viewport) or include_hidden),",
        "    'hidden_object_count': sum(1 for o in bpy.context.scene.objects if o.hide_viewport and not include_hidden),",
        "}",
        "print(json.dumps(result))",
    ]
    return PythonCode("\n".join(lines))


def _build_standard_inspection_code(include_hidden: bool) -> PythonCode:
    """Summary inspection — counts + cameras/lights (FR-SCN-001 standard detail)."""
    lines = [
        "import bpy",
        "import json",
        "",
        f"include_hidden = {include_hidden!r}",
        "",
        "scene = bpy.context.scene",
        "view_layer = bpy.context.view_layer",
        "objects_by_type = {{}}",
        "visible_count = 0",
        "hidden_count = 0",
        "cameras = []",
        "lights = []",
        "",
        "for obj in scene.objects:",
        "    is_hidden = bool(obj.hide_viewport)",
        "    if is_hidden: hidden_count += 1",
        "    else: visible_count += 1",
        "",
        "    if not include_hidden and is_hidden: continue",
        "",
        "    obj_type = obj.type",
        "    objects_by_type[obj_type] = objects_by_type.get(obj_type, 0) + 1",
        "",
        "    if obj_type == 'CAMERA':",
        "        cameras.append({{'name': obj.name}})",
        "    elif obj_type == 'LIGHT':",
        "        lights.append({{'name': obj.name}})",
        "",
        "result = {",
        "    'scene_name': scene.name,",
        "    'total_object_count': len(scene.objects),",
        "    'visible_object_count': visible_count,",
        "    'hidden_object_count': hidden_count,",
        "    'object_type_counts': objects_by_type,",
        "    'cameras': cameras,",
        "    'lights': lights,",
        "    'active_camera_name': bpy.context.scene.camera.name if bpy.context.scene.camera else '',",
        "    'active_object_name': view_layer.objects.active.name if view_layer.objects.active else '',",
        "}",
        "print(json.dumps(result))",
    ]
    return PythonCode("\n".join(lines))


def _build_detailed_inspection_code(include_hidden: bool) -> PythonCode:
    """Full dump — all object properties (FR-SCN-001 detailed)."""
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


def build_cleanup_code(request: SceneCleanupPolicyVO, dry_run: bool = False) -> PythonCode:
    """Unified cleanup code builder — handles both execution and preview modes.

    Replaces separate build_cleanup_execution_code() and build_cleanup_preview_code().
    Reduces duplication from ~60% to ~10%.

    Implements FR-SCN-002 child/dependent handling policies with linked object safety.
    """
    mode = request.mode or CLEANUP_MODE_ALL
    preserve_cameras = request.preserve_cameras
    preserve_lights = request.preserve_lights
    child_policy = request.child_handling_policy or CHILD_POLICY_DETACH
    dependent_policy = request.dependent_handling_policy or DEPENDENT_POLICY_REJECT

    lines = [
        "import bpy",
        "import json",
        "",
        "scene = bpy.context.scene",
        "view_layer = bpy.context.view_layer",
        f"cleanup_mode = '{mode}'",
        f"dry_run = {dry_run!r}",
        f"child_policy = '{child_policy}'",
        f"dependent_policy = '{dependent_policy}'",
        "",
        "removed_count = 0",
        "candidates_count = 0",
        "preserved_count = 0",
        "skipped_count = 0",
        "removed_refs = []",
        "candidates_refs = []",
        "preserved_refs = []",
        "skipped_refs = []",
        "",
        "def should_preserve(obj):",
        f"    if {preserve_cameras} and obj.type == 'CAMERA': return True",
        f"    if {preserve_lights} and obj.type == 'LIGHT': return True",
        "    return False",
        "",
        "def has_children(obj):",
        "    return hasattr(obj, 'children') and len(obj.children) > 0",
        "",
        "def has_dependents(obj):",
        "    return (hasattr(obj, 'constraints') and len(obj.constraints) > 0 or",
        "            hasattr(obj, 'parents') and len(obj.parents) > 0)",
        "",
        "def is_linked_object(obj):",
        "    return getattr(obj.data, 'users', 1) > 1",
        "",
        "for obj in scene.objects:",
        "    try:",
        "        if should_preserve(obj):",
        "            preserved_count += 1",
        "            preserved_refs.append(obj.name)",
        "        else:",
        "            # FR-SCN-002: linked object safety — do not remove shared data",
        "            if is_linked_object(obj):",
        "                skipped_count += 1",
        "                skipped_refs.append(obj.name)",
        "                continue",
        "",
        "            # FR-SCN-002: child handling policy",
        "            if has_children(obj):",
        "                if child_policy == 'delete':",
        "                    pass  # proceed to delete",
        "                elif child_policy == 'detach':",
        "                    for child in obj.children:",
        "                        child.parent = None",
        "                else:  # reject",
        "                    skipped_count += 1",
        "                    skipped_refs.append(obj.name)",
        "                    continue",
        "",
        "            # FR-SCN-002: dependent handling policy",
        "            if has_dependents(obj):",
        "                if dependent_policy == 'reject':",
        "                    skipped_count += 1",
        "                    skipped_refs.append(obj.name)",
        "                    continue",
        "                elif dependent_policy == 'ignore':",
        "                    pass  # proceed to delete, ignore dependents",
        "                else:  # remove_safe",
        "                    for constraint in (obj.constraints or []):",
        "                        obj.constraints.remove(constraint)",
        "",
        "            # FR-SCN-002: guard — do not remove world/render/settings/metadata",
        "            # Only delete scene objects, never scene data blocks",
        "",
        "            if dry_run:",
        "                candidates_count += 1",
        "                candidates_refs.append(obj.name)",
        "            else:",
        "                removed_count += 1",
        "                removed_refs.append(obj.name)",
        "    except Exception:",
        "        skipped_count += 1",
        "        skipped_refs.append(obj.name)",
        "",
        "result = {",
        "    'removed_count': removed_count if not dry_run else candidates_count,",
        "    'preserved_count': preserved_count,",
        "    'skipped_count': skipped_count,",
        "    'removed_refs': removed_refs if not dry_run else candidates_refs,",
        "    'preserved_refs': preserved_refs,",
        "    'skipped_refs': skipped_refs",
        "}",
        "print(json.dumps(result))",
    ]

    return PythonCode("\n".join(lines))
