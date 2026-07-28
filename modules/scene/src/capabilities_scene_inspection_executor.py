"""Capability: Scene inspection executor.

FR-SCN-001: Inspect scene state.

Capabilities layer:
- implements protocol ABC
- 3-block structure
- delegates technical parsing/building to utility
"""

from __future__ import annotations

import logging

from modules.shared.src.gateway.contract_code_execution_protocol import (
    ICodeExecutionProtocol,
)
from modules.shared.src.common.taxonomy_core_vo import Prompt, PythonCode, SuccessFlag
from modules.shared.src.scene.contract_scene_protocol import ISceneInspectionProtocol
from modules.shared.src.scene.taxonomy_scene_error import SceneErrorCategory
from modules.shared.src.scene.taxonomy_scene_event import SceneInspectionCompletedEvent
from modules.shared.src.scene.taxonomy_scene_vo import SceneInspectionVO
from modules.shared.src.scene.utility_scene_code_builder import build_inspection_code
from modules.shared.src.scene.utility_scene_result_parser import parse_scene_state_summary

logger = logging.getLogger("BlenderMCPServer")


class SceneInspectionExecutor(ISceneInspectionProtocol):
    """Capability for FR-SCN-001: scene inspection."""

    # ─── Block 1: definition + constructor ─────────────────────
    def __init__(self, code_executor: ICodeExecutionProtocol) -> None:
        if code_executor is None:
            raise ValueError("code_executor must be provided")
        self._code_executor = code_executor

    # ─── Block 2: protocol methods only ───────────────────────
    async def get_scene_info(self, request: SceneInspectionVO) -> SceneInspectionVO:
        """Retrieve scene state summary."""
        try:
            code = build_inspection_code(request)
            raw = await self._execute_code(code)

            if not isinstance(raw, str):
                return SceneInspectionVO(
                    detail_level=request.detail_level,
                    include_hidden_objects=request.include_hidden_objects,
                    object_type_filter=request.object_type_filter,
                    correlation_id=request.correlation_id,
                    success=SuccessFlag(False),
                    scene_state_summary=None,
                    message=Prompt("Inspection failed: non-string result from executor"),
                )

            summary = parse_scene_state_summary(raw)

            event = SceneInspectionCompletedEvent(
                correlation_id=request.correlation_id,
                success=SuccessFlag(True),
                detail_level=request.detail_level,
                total_object_count=summary.total_object_count,
                message=Prompt("Scene inspection completed"),
            )
            logger.info(event.message)

            return SceneInspectionVO(
                detail_level=request.detail_level,
                include_hidden_objects=request.include_hidden_objects,
                object_type_filter=request.object_type_filter,
                correlation_id=request.correlation_id,
                success=SuccessFlag(True),
                scene_state_summary=summary,
                message=event.message,
            )

        except Exception as e:
            logger.error("Scene inspection failed: %s", e)
            return SceneInspectionVO(
                detail_level=request.detail_level,
                include_hidden_objects=request.include_hidden_objects,
                object_type_filter=request.object_type_filter,
                correlation_id=request.correlation_id,
                success=SuccessFlag(False),
                scene_state_summary=None,
                message=Prompt(f"Inspection failed: {e}"),
            )

    # ─── Block 3: dunders / factories / helpers ───────────────
    async def _execute_code(self, code: PythonCode) -> str:
        """Execute code via injected code executor."""
        if self._code_executor is None:
            raise ValueError("code_executor must be provided")

        return await self._code_executor.execute_code(code, timeout=30.0)

    def __repr__(self) -> str:
        return "SceneInspectionExecutor()"
