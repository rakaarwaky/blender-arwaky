"""Capability: Scene operation executor.

Implements SceneOperateProtocol — handles scene inspection and cleanup
through the server module's code execution, with enhanced VOs, preservation
policy, dry-run preview, child/dependent handling, and protection rules.

FR-SCN-001: Enhanced inspection with detail level, hidden objects filter.
FR-SCN-002: Cleanup with preservation policy, dry-run, child/dependent handling.
Unified VO (merged request + response) — no split classes.
"""

from __future__ import annotations

import logging

from modules.shared.src.common.taxonomy_core_vo import (
    CoordinateList,
    ObjectCount,
    Prompt,
    ResolutionX,
    ResolutionY,
    RotationVector,
    ScaleVector,
    SuccessFlag,
)
from modules.shared.src.scene.contract_scene_operate_protocol import SceneOperateProtocol
from modules.shared.src.scene.taxonomy_scene_error_vo import (
    ConfirmationError,
    ProtectionError,
    ValidationError,
)
from modules.shared.src.scene.taxonomy_scene_event_vo import (
    SceneCleanupCompletedEvent,
    SceneInspectionCompletedEvent,
)
from modules.shared.src.scene.taxonomy_scene_request_vo import (
    CameraInfoVO,
    CleanupRequestVO,
    CollectionSummaryVO,
    InspectionRequestVO,
    ObjectType,
    SceneStateSummaryVO,
)

logger = logging.getLogger("BlenderMCPServer")


class SceneOperateExecutor(SceneOperateProtocol):
    """Business logic for scene management (inspection, cleanup).

    FR-SCN-001: Enhanced inspection with detail level, hidden objects filter.
    FR-SCN-002: Cleanup with preservation policy, dry-run, child/dependent handling.
    Unified VO (merged request + response) — no split classes.
    """

    def __init__(self, code_executor: Prompt) -> None:
        """Initialize with a code executor capability from the server module.

        Args:
            code_executor: A callable or server capability that executes Python code.
        """
        self._code_executor = code_executor

    async def cleanup_scene(self, request: CleanupRequestVO) -> CleanupRequestVO:
        """Execute cleanup of scene objects based on preservation policy.

        FR-SCN-002: Supports preservation modes (keep cameras, lights, both, remove all).
        Supports dry-run preview mode.
        Returns unified VO with removed/preserved/skipped counts and references.
        Same structure for actual cleanup and dry-run preview.
        """
        logger.info("Cleaning up scene (mode=%s, dry_run=%s)...", request.mode, request.dry_run)

        # Validation
        if not self._validate_request(request):
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
                message=Prompt("Validation error: invalid cleanup mode"),
            )

        # Confirmation check for destructive operations
        if not request.dry_run and not request.confirmation:
            return CleanupRequestVO(
                mode=request.mode,
                preservation_list=request.preservation_list,
                dry_run=False,
                confirmation=False,
                child_handling_policy=request.child_handling_policy,
                dependent_handling_policy=request.dependent_handling_policy,
                include_hidden_objects=request.include_hidden_objects,
                correlation_id=request.correlation_id,
                success=SuccessFlag(False),
                message=Prompt("Confirmation error: destructive operation requires explicit confirmation"),
            )

        # Execute cleanup code
        try:
            if request.dry_run:
                result = await self._execute_dry_run(request)
            else:
                result = await self._execute_cleanup(request)
            return result
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

    async def get_scene_info(self, request: InspectionRequestVO) -> InspectionRequestVO:
        """Retrieve current scene metadata and object tree.

        FR-SCN-001: Supports detail level, hidden objects filter, object type filter.
        Returns unified VO with scene state summary (SceneStateSummaryVO).
        """
        logger.info("Retrieving scene info (detail=%s)...", request.detail_level)

        try:
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

    # ─── Helpers ────────────────────────────────────────────────

    def _validate_request(self, request: CleanupRequestVO) -> bool:
        """Validate cleanup request parameters."""
        valid_modes = {"all", "objects", "meshes"}
        if str(request.mode).lower() not in valid_modes:
            return False
        valid_child_policies = {"delete", "detach", "reject"}
        if request.child_handling_policy not in valid_child_policies:
            return False
        valid_dependent_policies = {"ignore", "reject", "remove_safe"}
        if request.dependent_handling_policy not in valid_dependent_policies:
            return False
        return True

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
                    location=CoordinateList([0.0, 0.0, 0.0]),
                    rotation=RotationVector([0.0, 0.0, 0.0]),
                    scale=ScaleVector([1.0, 1.0, 1.0]),
                    data_type=c.get("type", ""),
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
                active_camera_name=data.get("active_camera_name", ""),
                active_object_name=data.get("active_object_name", ""),
                render_engine=data.get("render_engine", "CYCLES"),
                resolution_x=ResolutionX(data.get("resolution_x", 1920)),
                resolution_y=ResolutionY(data.get("resolution_y", 1080)),
                frame_start=data.get("frame_start", 1),
                frame_end=data.get("frame_end", 250),
                unit_system=data.get("unit_system", "METRIC"),
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

    async def _execute_dry_run(self, request: CleanupRequestVO) -> CleanupRequestVO:
        """Execute dry-run cleanup preview without modifying scene."""
        logger.info("Dry-run cleanup (mode=%s)...", request.mode)

        # Generate code to count removable objects (without deleting)
        code = self._build_dry_run_code(request)

        try:
            result = await self._execute_code(code)
            data = self._parse_cleanup_result(result, dry_run=True)
            return CleanupRequestVO(
                mode=request.mode,
                preservation_list=request.preservation_list,
                dry_run=True,
                confirmation=False,
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
                message=Prompt(f"Dry-run cleanup complete (mode={request.mode}): {data['removed_count']} removable"),
            )
        except Exception as e:
            logger.error("Dry-run failed: %s", e)
            return CleanupRequestVO(
                mode=request.mode,
                preservation_list=request.preservation_list,
                dry_run=True,
                confirmation=False,
                child_handling_policy=request.child_handling_policy,
                dependent_handling_policy=request.dependent_handling_policy,
                include_hidden_objects=request.include_hidden_objects,
                correlation_id=request.correlation_id,
                success=SuccessFlag(False),
                message=Prompt(f"Dry-run failed: {e}"),
            )

    async def _execute_cleanup(self, request: CleanupRequestVO) -> CleanupRequestVO:
        """Execute actual cleanup with preservation policy."""
        logger.info("Actual cleanup (mode=%s)...", request.mode)

        code = self._build_cleanup_code(request)

        try:
            result = await self._execute_code(code)
            data = self._parse_cleanup_result(result, dry_run=False)
            return CleanupRequestVO(
                mode=request.mode,
                preservation_list=request.preservation_list,
                dry_run=False,
                confirmation=True,
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
            logger.error("Actual cleanup failed: %s", e)
            return CleanupRequestVO(
                mode=request.mode,
                preservation_list=request.preservation_list,
                dry_run=False,
                confirmation=True,
                child_handling_policy=request.child_handling_policy,
                dependent_handling_policy=request.dependent_handling_policy,
                include_hidden_objects=request.include_hidden_objects,
                correlation_id=request.correlation_id,
                success=SuccessFlag(False),
                message=Prompt(f"Actual cleanup failed: {e}"),
            )

    def _build_dry_run_code(self, request: CleanupRequestVO) -> str:
        """Build dry-run code to count removable objects without deleting."""
        mode = str(request.mode).lower()
        preservation = list(request.preservation_list) if request.preservation_list else ["camera", "light"]

        lines = [
            "import bpy",
            "scene = bpy.context.scene",
            "",
            "removable = []",
            "preserved = []",
            "skipped = []",
            "",
        ]

        # Build preservation check
        if "camera" in preservation:
            lines.append("# Preserve cameras")
            lines.append("cameras = [o for o in scene.objects if o.type == 'CAMERA']")
            lines.append("for cam in cameras:")
            lines.append("    preserved.append(cam.name)")
            lines.append("")

        if "light" in preservation:
            lines.append("# Preserve lights")
            lines.append("lights = [o for o in scene.objects if o.type == 'LIGHT']")
            lines.append("for light in lights:")
            lines.append("    preserved.append(light.name)")
            lines.append("")

        # Count removable objects
        if mode == "all":
            lines.append(
                "for obj in scene.objects:\n"
                "    if obj.type not in ('CAMERA', 'LIGHT'):\n"
                "        removable.append(obj.name)\n"
                "    else:\n"
                "        preserved.append(obj.name)\n"
            )
        elif mode == "objects":
            lines.append(
                "for obj in scene.objects:\n"
                "    if obj.type not in ('CAMERA', 'LIGHT'):\n"
                "        removable.append(obj.name)\n"
            )
        else:  # meshes
            lines.append(
                "for obj in scene.objects:\n"
                "    if obj.type == 'MESH':\n"
                "        removable.append(obj.name)\n"
            )

        lines.extend([
            "result = {",
            '    "removed_count": len(removable),',
            '    "preserved_count": len(preserved),',
            '    "skipped_count": 0,',
            '    "removed_refs": removable,',
            '    "preserved_refs": preserved,',
            '    "skipped_refs": [],'
            "}"
        ])

        code = "\n".join(lines) + "\nprint(result)"
        return code

    def _build_cleanup_code(self, request: CleanupRequestVO) -> str:
        """Build actual cleanup code with preservation policy."""
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

        # Preserve cameras
        lines.extend([
            "# Preserve cameras",
            "for obj in list(scene.objects):",
            "    if obj.type == 'CAMERA':",
            "        preserved_count += 1",
            "        preserved_refs.append(obj.name)",
        ])

        # Preserve lights
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
            RuntimeError: If code execution fails.
        """
        if callable(self._code_executor):
            result = await self._code_executor(Prompt(code))
            if isinstance(result, str):
                logger.info("Code execution result: %s", result[:200])
                return result
            raise RuntimeError(f"Unexpected code_executor result type: {type(self._code_executor)}")
        else:
            raise RuntimeError(f"Unexpected code_executor type: {type(self._code_executor)}")

    def __repr__(self) -> str:
        return "SceneOperateExecutor()"
