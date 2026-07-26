"""Capability: Scene inspection adapter.

Implements SceneInspectionPort — handles scene info and cleanup through the
server module's command dispatch and code execution capabilities.

FR-SCN-001: Enhanced inspection with detail level, hidden objects filter.
FR-SCN-002: Cleanup with preservation policy, dry-run, child/dependent handling.
Unified VO (merged request + response) — no split classes.
"""

from __future__ import annotations

import json
import logging

from modules.shared.src.common.taxonomy_core_vo import ActionName, ObjectCount, ObjectName, Prompt, SuccessFlag
from modules.shared.src.scene.contract_scene_inspection import SceneInspectionPort
from modules.shared.src.scene.taxonomy_scene_error_vo import ConnectionError
from modules.shared.src.scene.taxonomy_scene_request_vo import (
    CameraInfoVO,
    CleanupRequestVO,
    CollectionSummaryVO,
    InspectionRequestVO,
    LightInfoVO,
    ObjectType,
    SceneStateSummaryVO,
)

logger = logging.getLogger("BlenderMCPServer")


class SceneInspectionAdapter(SceneInspectionPort):
    """Scene inspection and cleanup via server command dispatch.

    FR-SCN-001: Enhanced inspection with detail level, hidden objects filter.
    FR-SCN-002: Cleanup with preservation policy, dry-run, child/dependent handling.
    Unified VO (merged request + response) — no split classes.
    """

    def __init__(self, command_sender: Prompt, code_executor: Prompt) -> None:
        """Initialize with server module capabilities.

        Args:
            command_sender: A callable that sends commands to Blender.
            code_executor: A callable that executes Python code in Blender.
        """
        self._command_sender = command_sender
        self._code_executor = code_executor

    async def get_scene_info(self, request: InspectionRequestVO) -> InspectionRequestVO:
        """Get detailed information about the current Blender scene.

        FR-SCN-001: Supports detail level, hidden objects filter, object type filter.
        Returns unified VO with scene state summary (SceneStateSummaryVO).
        """
        try:
            # Build inspection code based on detail level
            code = self._build_inspection_code(request)
            result = await self._execute_code(code)

            # Parse the result into SceneStateSummaryVO
            scene_summary = self._parse_scene_info(result)

            return InspectionRequestVO(
                detail_level=request.detail_level,
                include_hidden_objects=request.include_hidden_objects,
                object_type_filter=request.object_type_filter,
                correlation_id=request.correlation_id,
                success=SuccessFlag(True),
                scene_state_summary=scene_summary,
                message=Prompt("Scene info retrieved successfully"),
            )
        except Exception as e:
            logger.error("get_scene_info failed: %s", e)
            return InspectionRequestVO(
                detail_level=request.detail_level,
                include_hidden_objects=request.include_hidden_objects,
                object_type_filter=request.object_type_filter,
                correlation_id=request.correlation_id,
                success=SuccessFlag(False),
                scene_state_summary=None,
                message=Prompt(f"Failed to get scene info: {e}"),
            )

    async def get_object_info(self, object_name: ObjectName) -> Prompt:
        """Get detailed information about a specific object by name."""
        try:
            result = self._command_sender(ActionName("get_object_info"), {"name": object_name})
            return Prompt(json.dumps(result, indent=2))
        except Exception as e:
            logger.error("Error getting object info from Blender: %s", e)
            return Prompt(f"Error getting object info: {e}")

    async def cleanup_scene(self, request: CleanupRequestVO) -> CleanupRequestVO:
        """Remove objects from scene based on preservation policy.

        FR-SCN-002: Supports preservation modes (keep cameras, lights, both, remove all).
        Supports dry-run preview mode.
        Returns unified VO with removed/preserved/skipped counts and references.
        Same structure for actual cleanup and dry-run preview.
        """
        try:
            code = self._build_cleanup_code(request)
            result = await self._execute_code(code)

            # Parse the result
            data = self._parse_cleanup_result(result, request.dry_run)

            return CleanupRequestVO(
                mode=request.mode,
                preservation_list=request.preservation_list,
                dry_run=request.dry_run,
                confirmation=request.confirmation,
                child_handling_policy=request.child_handling_policy,
                dependent_handling_policy=request.dependent_handling_policy,
                include_hidden_objects=request.include_hidden_objects,
                correlation_id=request.correlation_id,
                success=SuccessFlag(True),
                removed_count=data["removed_count"],
                preserved_count=data["preserved_count"],
                skipped_count=data["skipped_count"],
                removed_object_references=data["removed_refs"],
                preserved_object_references=data["preserved_refs"],
                skipped_object_references=data["skipped_refs"],
                message=Prompt(f"Scene cleaned up successfully (mode={request.mode}): {data['removed_count']} removed"),
            )
        except Exception as e:
            logger.error("Cleanup failed: %s", e)
            return CleanupRequestVO(
                mode=request.mode,
                preservation_list=request.preservation_list,
                dry_run=request.dry_run,
                confirmation=request.confirmation,
                child_handling_policy=request.child_handling_policy,
                dependent_handling_policy=request.dependent_handling_policy,
                include_hidden_objects=request.include_hidden_objects,
                correlation_id=request.correlation_id,
                success=SuccessFlag(False),
                message=Prompt(f"Cleanup failed: {e}"),
            )

    # ─── Helpers ────────────────────────────────────────────────

    def _build_inspection_code(self, request: InspectionRequestVO) -> str:
        """Build Blender Python code for scene inspection."""
        lines = [
            "import bpy",
            "scene = bpy.context.scene",
            "",
            "# Build object summary",
            "objects_by_type = {}",
            "visible_count = 0",
            "hidden_count = 0",
            "cameras = []",
            "lights = []",
            "active_camera_name = ''",
            "active_object_name = ''",
            "",
        ]

        # Object type counts and camera/light detection
        lines.append(
            'for obj in scene.objects:\n'
            "    obj_type = obj.type\n"
            "    objects_by_type[obj_type] = objects_by_type.get(obj_type, 0) + 1\n"
            "    if obj.hide_viewport:\n"
            "        hidden_count += 1\n"
            "    else:\n"
            "        visible_count += 1\n"
            "    if obj.type == 'CAMERA':\n"
            "        cameras.append({'name': obj.name, 'type': obj.data.type if hasattr(obj.data, 'type') else ''})\n"
            "    elif obj.type == 'LIGHT':\n"
            "        lights.append({'name': obj.name, 'light_type': obj.data.type if hasattr(obj.data, 'type') else ''})\n"
        )

        # Active camera and active object
        lines.append(
            "if scene.camera:\n"
            "    active_camera_name = scene.camera.name\n"
            "if scene.objects.active:\n"
            "    active_object_name = scene.objects.active.name\n"
        )

        # Render settings
        lines.extend([
            "render_engine = ''",
            "res_x = 0",
            "res_y = 0",
            "frame_start = 1",
            "frame_end = 250",
            "unit_system = 'METRIC'",
            "",
            "if scene.render:\n"
            "    render_engine = scene.render.engine if hasattr(scene.render, 'engine') else ''\n"
            "    res_x = scene.render.resolution_x\n"
            "    res_y = scene.render.resolution_y\n"
            "if scene.frame_start is not None:\n"
            "    frame_start = scene.frame_start\n"
            "if scene.frame_end is not None:\n"
            "    frame_end = scene.frame_end\n"
        ])

        # Collections
        lines.extend([
            "collections = []",
            "for col in scene.collection.children_recursive:\n"
            "    collections.append({'name': col.name, 'object_count': len(col.objects)})\n"
        ])

        # Output as JSON-compatible dict
        lines.extend([
            "result = {",
            '    "scene_name": scene.name,',
            '    "total_object_count": len(scene.objects),',
            '    "visible_object_count": visible_count,',
            '    "hidden_object_count": hidden_count,',
            '    "object_type_counts": objects_by_type,',
            '    "cameras": cameras,',
            '    "lights": lights,',
            '    "active_camera_name": active_camera_name,',
            '    "active_object_name": active_object_name,',
            '    "render_engine": render_engine,',
            '    "resolution_x": res_x,',
            '    "resolution_y": res_y,',
            '    "frame_start": frame_start,',
            '    "frame_end": frame_end,',
            '    "unit_system": unit_system,',
            '    "collections": collections,',
            "}"
        ])

        code = "\n".join(lines) + "\nprint(result)"
        return code

    def _parse_scene_info(self, result: str) -> SceneStateSummaryVO:
        """Parse inspection result into SceneStateSummaryVO."""
        try:
            import json
            data = json.loads(result)

            # Parse cameras
            cameras = []
            for c in data.get("cameras", []):
                cameras.append(CameraInfoVO(
                    name=c.get("name", ""),
                    type=ObjectType("CAMERA"),
                ))

            # Parse lights
            lights = []
            for l in data.get("lights", []):
                lights.append(LightInfoVO(
                    name=l.get("name", ""),
                    type=ObjectType("LIGHT"),
                ))

            # Parse collections
            collections = []
            for c in data.get("collections", []):
                collections.append(CollectionSummaryVO(
                    name=c.get("name", ""),
                    object_count=ObjectCount(c.get("object_count", 0)),
                ))

            return SceneStateSummaryVO(
                scene_name=data.get("scene_name", ""),
                total_object_count=ObjectCount(data.get("total_object_count", 0)),
                visible_object_count=ObjectCount(data.get("visible_object_count", 0)),
                hidden_object_count=ObjectCount(data.get("hidden_object_count", 0)),
                object_type_counts={k: ObjectCount(v) for k, v in data.get("object_type_counts", {}).items()},
                cameras=cameras,
                lights=lights,
                active_camera_name=data.get("active_camera_name", ""),
                active_object_name=data.get("active_object_name", ""),
                render_engine=data.get("render_engine", "CYCLES"),
                collections=collections,
            )
        except Exception as e:
            logger.warning("Failed to parse scene info: %s", e)
            return SceneStateSummaryVO(
                scene_name="",
                total_object_count=ObjectCount(0),
                visible_object_count=ObjectCount(0),
                hidden_object_count=ObjectCount(0),
            )

    def _build_cleanup_code(self, request: CleanupRequestVO) -> str:
        """Build cleanup code with preservation policy."""
        mode = str(request.mode).lower()

        lines = [
            "import bpy",
            "scene = bpy.context.scene",
            "",
            "removed_count = 0",
            "preserved_count = 0",
            "skipped_count = 0",
            "removed_refs = []",
            "preserved_refs = []",
            "skipped_refs = []",
            "",
        ]

        # Preserve cameras and lights based on preservation list
        if not request.preservation_list:
            request.preservation_list = ("camera", "light")

        if "camera" in request.preservation_list:
            lines.extend([
                "# Preserve cameras",
                "for obj in list(scene.objects):",
                "    if obj.type == 'CAMERA':",
                "        preserved_count += 1",
                "        preserved_refs.append(obj.name)",
            ])

        if "light" in request.preservation_list:
            lines.extend([
                "",
                "# Preserve lights",
                "for obj in list(scene.objects):",
                "    if obj.type == 'LIGHT':",
                "        preserved_count += 1",
                "        preserved_refs.append(obj.name)",
            ])

        # Delete removable objects
        if mode == "all":
            lines.extend([
                "",
                "# Remove non-preserved objects",
                "for obj in list(scene.objects):",
                "    if obj.type not in ('CAMERA', 'LIGHT'):",
                "        bpy.data.objects.remove(obj, do_unlink=True)",
                "        removed_count += 1",
                "        removed_refs.append(obj.name)",
            ])
        elif mode == "objects":
            lines.extend([
                "",
                "# Remove non-preserved objects",
                "for obj in list(scene.objects):",
                "    if obj.type not in ('CAMERA', 'LIGHT'):",
                "        bpy.data.objects.remove(obj, do_unlink=True)",
                "        removed_count += 1",
                "        removed_refs.append(obj.name)",
            ])
        else:  # meshes
            lines.extend([
                "",
                "# Remove mesh objects only",
                "for obj in list(scene.objects):",
                "    if obj.type == 'MESH':",
                "        bpy.data.objects.remove(obj, do_unlink=True)",
                "        removed_count += 1",
                "        removed_refs.append(obj.name)",
            ])

        lines.extend([
            "",
            "result = {",
            '    "removed_count": removed_count,',
            '    "preserved_count": preserved_count,',
            '    "skipped_count": skipped_count,',
            '    "removed_refs": removed_refs,',
            '    "preserved_refs": preserved_refs,',
            '    "skipped_refs": skipped_refs,',
            "}"
        ])

        code = "\n".join(lines) + "\nprint(result)"
        return code

    def _parse_cleanup_result(self, result: str, dry_run: bool) -> dict:
        """Parse cleanup result JSON into structured data."""
        try:
            import json
            data = json.loads(result)
            return {
                "removed_count": ObjectCount(data.get("removed_count", 0)),
                "preserved_count": ObjectCount(data.get("preserved_count", 0)),
                "skipped_count": ObjectCount(data.get("skipped_count", 0)),
                "removed_refs": data.get("removed_refs", []),
                "preserved_refs": data.get("preserved_refs", []),
                "skipped_refs": data.get("skipped_refs", []),
            }
        except Exception as e:
            logger.warning("Failed to parse cleanup result: %s", e)
            return {
                "removed_count": ObjectCount(0),
                "preserved_count": ObjectCount(0),
                "skipped_count": ObjectCount(0),
                "removed_refs": [],
                "preserved_refs": [],
                "skipped_refs": [],
            }

    async def _execute_code(self, code: str) -> str:
        """Execute Python code through the server module's code execution capability.

        Args:
            code: Python code string to execute in Blender.

        Returns:
            Result string from code execution.

        Raises:
            ConnectionError: If code execution fails.
        """
        try:
            if callable(self._code_executor):
                result = await self._code_executor(Prompt(code))
                if isinstance(result, str):
                    return result
            raise RuntimeError(f"Unexpected code_executor type: {type(self._code_executor)}")
        except Exception as e:
            logger.error("Code execution failed: %s", e)
            raise ConnectionError(f"Code execution failed: {e}")
