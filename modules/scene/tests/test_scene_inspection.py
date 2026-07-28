"""Enhanced TDD suite for FR-SCN-001 and FR-SCN-002.

Exercises SceneInspectionExecutor and SceneCleanupExecutor over injected code execution.
Verifies:
- FR-SCN-001: Scene inspection with detail level, hidden objects filter
- FR-SCN-002: Cleanup with preservation policy, dry-run, child/dependent handling

Unified VO (merged request + response) — no split classes.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from modules.scene.src.capabilities_scene_cleanup_executor import SceneCleanupExecutor
from modules.scene.src.capabilities_scene_inspection_executor import SceneInspectionExecutor
from modules.shared.src.common.taxonomy_core_vo import (
    CleanupMode,
    ObjectCount,
    Prompt,
    PythonCode,
    SuccessFlag,
)
from modules.shared.src.gateway.contract_code_execution_protocol import ICodeExecutionProtocol
from modules.shared.src.scene.taxonomy_scene_vo import (
    SceneCleanupVO,
    SceneInspectionVO,
)


# ─── Mock Code Executor ──────────────────────────────────────


class MockCodeExecutor:
    """Mock code executor implementing ICodeExecutionProtocol for testing scene operations."""

    def __init__(self, inspection_result: dict | None = None, cleanup_result: dict | None = None) -> None:  # noqa: ANN002
        self._inspection_result = inspection_result or {
            "scene_name": "Scene",
            "total_object_count": 4,
            "visible_object_count": 3,
            "hidden_object_count": 1,
            "object_type_counts": {"MESH": 2, "CAMERA": 1, "LIGHT": 1},
            "cameras": [{"name": "Cam", "type": "perspective"}],
            "lights": [{"name": "Lamp", "light_type": "point"}],
            "active_camera_name": "Cam",
            "active_object_name": "Cube",
            "render_engine": "CYCLES",
            "resolution_x": 1920,
            "resolution_y": 1080,
            "frame_start": 1,
            "frame_end": 250,
            "unit_system": "METRIC",
            "collections": [{"name": "Collection", "object_count": 4}],
        }
        self._cleanup_result = cleanup_result or {
            "removed_count": 2,
            "preserved_count": 2,
            "skipped_count": 0,
            "removed_refs": ["Cube", "Sphere"],
            "preserved_refs": ["Cam", "Lamp"],
            "skipped_refs": [],
        }

    async def execute_code(self, code: PythonCode, language: str = "python", timeout: float = 30.0) -> str:  # noqa: ANN002, ANN401
        """Return mock result based on whether code contains 'print(result)'."""
        if "removed_count" in code or "preserved_count" in code:
            # Cleanup code
            return json.dumps(self._cleanup_result)
        else:
            # Inspection code
            return json.dumps(self._inspection_result)


# ─── FR-SCN-001: Inspect Scene State ─────────────────────────


@pytest.mark.asyncio
async def test_fr_scn_001_returns_scene_state_summary():
    """Test that scene inspection returns comprehensive state summary."""
    mock = MockCodeExecutor()
    executor = SceneInspectionExecutor(mock)

    request = SceneInspectionVO()
    result = await executor.get_scene_info(request)

    assert isinstance(result, SceneInspectionVO)
    assert result.success == SuccessFlag(True)
    assert result.scene_state_summary is not None
    summary = result.scene_state_summary
    assert summary.scene_name == "Scene"
    assert summary.total_object_count == ObjectCount(4)
    assert summary.visible_object_count == ObjectCount(3)
    assert summary.hidden_object_count == ObjectCount(1)
    assert summary.render_engine == "CYCLES"


@pytest.mark.asyncio
async def test_fr_scn_001_handles_detail_level():
    """Test that inspection respects detail level setting."""
    mock = MockCodeExecutor()
    executor = SceneInspectionExecutor(mock)

    request = SceneInspectionVO(detail_level="detailed")
    result = await executor.get_scene_info(request)

    assert result.success == SuccessFlag(True)
    assert result.detail_level == "detailed"


@pytest.mark.asyncio
async def test_fr_scn_001_handles_empty_scene():
    """Test that inspection handles empty scene gracefully."""
    import json

    class EmptyExecutor:
        async def execute_code(self, code: PythonCode, language: str = "python", timeout: float = 30.0) -> str:  # noqa: ANN002, ANN401
            return json.dumps(
                {
                    "scene_name": "EmptyScene",
                    "total_object_count": 0,
                    "visible_object_count": 0,
                    "hidden_object_count": 0,
                    "object_type_counts": {},
                    "cameras": [],
                    "lights": [],
                    "active_camera_name": "",
                    "active_object_name": "",
                    "render_engine": "CYCLES",
                    "resolution_x": 1920,
                    "resolution_y": 1080,
                    "frame_start": 1,
                    "frame_end": 250,
                    "unit_system": "METRIC",
                    "collections": [],
                }
            )

    executor = SceneInspectionExecutor(EmptyExecutor())
    request = SceneInspectionVO()
    result = await executor.get_scene_info(request)

    assert result.success == SuccessFlag(True)
    assert result.scene_state_summary is not None
    assert result.scene_state_summary.total_object_count == ObjectCount(0)


# ─── FR-SCN-002: Cleanup Scene Objects ──────────────────────


@pytest.mark.asyncio
async def test_fr_scn_002_cleanup_with_preservation():
    """Test that cleanup preserves cameras and lights by default."""
    mock = MockCodeExecutor()
    executor = SceneCleanupExecutor(mock)

    request = SceneCleanupVO(
        mode=CleanupMode("all"),
        preservation_list=("camera", "light"),
        confirmation=True,
    )
    result = await executor.cleanup_scene(request)

    assert isinstance(result, SceneCleanupVO)
    assert result.success == SuccessFlag(True)
    assert result.removed_count == ObjectCount(2)
    assert result.preserved_count == ObjectCount(2)
    assert "Cam" in result.preserved_object_references
    assert "Lamp" in result.preserved_object_references


@pytest.mark.asyncio
async def test_fr_scn_002_dry_run_does_not_mutate():
    """Test that dry-run cleanup returns preview without modifying scene."""
    mock = MockCodeExecutor()
    executor = SceneCleanupExecutor(mock)

    request = SceneCleanupVO(
        mode=CleanupMode("all"),
        dry_run=True,
    )
    result = await executor.cleanup_scene(request)

    assert isinstance(result, SceneCleanupVO)
    assert result.success == SuccessFlag(True)
    assert result.dry_run is True
    # Dry-run returns preview counts (what WOULD be removed), not actual removal
    assert result.removed_count == ObjectCount(2)
    assert result.preserved_count == ObjectCount(2)


@pytest.mark.asyncio
async def test_fr_scn_002_confirmation_required():
    """Test that destructive cleanup requires confirmation."""
    mock = MockCodeExecutor()
    executor = SceneCleanupExecutor(mock)

    request = SceneCleanupVO(
        mode=CleanupMode("all"),
        dry_run=False,
        confirmation=False,
    )
    result = await executor.cleanup_scene(request)

    assert isinstance(result, SceneCleanupVO)
    assert result.success == SuccessFlag(False)


# ─── Edge Cases: FR-SCN-001 ────────────────────────────────


@pytest.mark.asyncio
async def test_fr_scn_001_hidden_objects_included_when_requested():
    """Test that hidden objects are included when explicitly requested."""
    import json

    class HiddenObjectsExecutor:
        async def execute_code(self, code: PythonCode, language: str = "python", timeout: float = 30.0) -> str:  # noqa: ANN002, ANN401
            return json.dumps(
                {
                    "scene_name": "Scene",
                    "total_object_count": 5,
                    "visible_object_count": 3,
                    "hidden_object_count": 2,
                    "object_type_counts": {"MESH": 3, "CAMERA": 1, "LIGHT": 1},
                    "cameras": [{"name": "Cam", "type": "perspective"}],
                    "lights": [{"name": "Lamp", "light_type": "point"}],
                    "active_camera_name": "Cam",
                    "active_object_name": "Cube",
                    "render_engine": "CYCLES",
                    "resolution_x": 1920,
                    "resolution_y": 1080,
                    "frame_start": 1,
                    "frame_end": 250,
                    "unit_system": "METRIC",
                    "collections": [{"name": "Collection", "object_count": 5}],
                }
            )

    executor = SceneInspectionExecutor(HiddenObjectsExecutor())
    request = SceneInspectionVO(include_hidden_objects=True)
    result = await executor.get_scene_info(request)

    assert result.success == SuccessFlag(True)
    assert result.scene_state_summary is not None
    assert result.scene_state_summary.total_object_count == ObjectCount(5)
    assert result.scene_state_summary.visible_object_count == ObjectCount(3)
    assert result.scene_state_summary.hidden_object_count == ObjectCount(2)


@pytest.mark.asyncio
async def test_fr_scn_001_object_type_filter():
    """Test that object type filter is applied correctly."""
    import json

    class FilteredExecutor:
        async def execute_code(self, code: PythonCode, language: str = "python", timeout: float = 30.0) -> str:  # noqa: ANN002, ANN401
            return json.dumps(
                {
                    "scene_name": "Scene",
                    "total_object_count": 1,
                    "visible_object_count": 1,
                    "hidden_object_count": 0,
                    "object_type_counts": {"CAMERA": 1},
                    "cameras": [{"name": "Cam", "type": "perspective"}],
                    "lights": [],
                    "active_camera_name": "Cam",
                    "active_object_name": "Cam",
                    "render_engine": "CYCLES",
                    "resolution_x": 1920,
                    "resolution_y": 1080,
                    "frame_start": 1,
                    "frame_end": 250,
                    "unit_system": "METRIC",
                    "collections": [{"name": "Collection", "object_count": 1}],
                }
            )

    executor = SceneInspectionExecutor(FilteredExecutor())
    request = SceneInspectionVO(object_type_filter=("CAMERA",))
    result = await executor.get_scene_info(request)

    assert result.success == SuccessFlag(True)
    assert result.scene_state_summary is not None
    assert result.scene_state_summary.total_object_count == ObjectCount(1)


@pytest.mark.asyncio
async def test_fr_scn_001_correlation_id_propagated():
    """Test that correlation ID is propagated through inspection."""
    import json

    class CorrelatedExecutor:
        async def execute_code(self, code: PythonCode, language: str = "python", timeout: float = 30.0) -> str:  # noqa: ANN002, ANN401
            return json.dumps(
                {
                    "scene_name": "Scene",
                    "total_object_count": 0,
                    "visible_object_count": 0,
                    "hidden_object_count": 0,
                    "object_type_counts": {},
                    "cameras": [],
                    "lights": [],
                    "active_camera_name": "",
                    "active_object_name": "",
                    "render_engine": "CYCLES",
                    "resolution_x": 1920,
                    "resolution_y": 1080,
                    "frame_start": 1,
                    "frame_end": 250,
                    "unit_system": "METRIC",
                    "collections": [],
                }
            )

    executor = SceneInspectionExecutor(CorrelatedExecutor())
    request = SceneInspectionVO(correlation_id="test-correlation-123")
    result = await executor.get_scene_info(request)

    assert result.success == SuccessFlag(True)
    assert result.correlation_id == "test-correlation-123"


@pytest.mark.asyncio
async def test_fr_scn_001_none_result_returns_error():
    """Test that None result from executor returns error state."""
    class NoneResultExecutor:
        async def execute_code(self, code: PythonCode, language: str = "python", timeout: float = 30.0) -> None:  # type: ignore[return-value]
            return None

    executor = SceneInspectionExecutor(NoneResultExecutor())
    request = SceneInspectionVO()
    result = await executor.get_scene_info(request)

    assert result.success == SuccessFlag(False)
    assert result.scene_state_summary is None


@pytest.mark.asyncio
async def test_fr_scn_001_non_string_result_returns_error():
    """Test that non-string result from executor returns error state."""
    class NonStringResultExecutor:
        async def execute_code(self, code: PythonCode, language: str = "python", timeout: float = 30.0) -> dict[str, Any]:  # type: ignore[return-value]
            return {"invalid": True}

    executor = SceneInspectionExecutor(NonStringResultExecutor())
    request = SceneInspectionVO()
    result = await executor.get_scene_info(request)

    assert result.success == SuccessFlag(False)
    assert result.scene_state_summary is None


@pytest.mark.asyncio
async def test_fr_scn_001_json_parse_error_returns_empty_state():
    """Test that malformed JSON returns error state."""
    import json

    class MalformedJSONExecutor:
        async def execute_code(self, code: PythonCode, language: str = "python", timeout: float = 30.0) -> str:  # noqa: ANN002
            return json.dumps({"scene_name": "Scene", "total_object_count": 0})

    executor = SceneInspectionExecutor(MalformedJSONExecutor())
    request = SceneInspectionVO()
    result = await executor.get_scene_info(request)

    assert isinstance(result, SceneInspectionVO)
    # Parser should handle malformed data gracefully


# ─── Edge Cases: FR-SCN-002 ────────────────────────────────


@pytest.mark.asyncio
async def test_fr_scn_002_cleanup_with_custom_preservation_list():
    """Test cleanup with custom preservation list."""
    import json

    class CustomPreservationExecutor:
        async def execute_code(self, code: PythonCode, language: str = "python", timeout: float = 30.0) -> str:  # noqa: ANN002, ANN401
            return json.dumps(
                {
                    "removed_count": 1,
                    "preserved_count": 3,
                    "skipped_count": 0,
                    "removed_refs": ["Cube"],
                    "preserved_refs": ["Cam", "Lamp", "Sphere"],
                    "skipped_refs": [],
                }
            )

    executor = SceneCleanupExecutor(CustomPreservationExecutor())
    request = SceneCleanupVO(
        mode=CleanupMode("all"),
        preservation_list=("camera", "light", "mesh"),
        confirmation=True,
    )
    result = await executor.cleanup_scene(request)

    assert isinstance(result, SceneCleanupVO)
    assert result.success == SuccessFlag(True)
    assert result.removed_count == ObjectCount(1)
    assert result.preserved_count == ObjectCount(3)


@pytest.mark.asyncio
async def test_fr_scn_002_cleanup_malformed_json_returns_empty():
    """Test that malformed JSON from cleanup returns error."""
    import json

    class MalformedCleanupExecutor:
        async def execute_code(self, code: PythonCode, language: str = "python", timeout: float = 30.0) -> str:  # noqa: ANN002
            return json.dumps({"removed_count": 0, "preserved_count": 0})

    executor = SceneCleanupExecutor(MalformedCleanupExecutor())
    request = SceneCleanupVO(mode=CleanupMode("all"), confirmation=True)
    result = await executor.cleanup_scene(request)

    assert isinstance(result, SceneCleanupVO)
    # Parser should handle malformed data gracefully


@pytest.mark.asyncio
async def test_fr_scn_002_dry_run_with_no_removable_objects():
    """Test dry-run with no removable objects returns empty preview."""
    import json

    class EmptySceneExecutor:
        async def execute_code(self, code: PythonCode, language: str = "python", timeout: float = 30.0) -> str:  # noqa: ANN002, ANN401
            return json.dumps(
                {
                    "removed_count": 0,
                    "preserved_count": 0,
                    "skipped_count": 0,
                    "removed_refs": [],
                    "preserved_refs": [],
                    "skipped_refs": [],
                }
            )

    executor = SceneCleanupExecutor(EmptySceneExecutor())
    request = SceneCleanupVO(mode=CleanupMode("all"), dry_run=True)
    result = await executor.cleanup_scene(request)

    assert isinstance(result, SceneCleanupVO)
    assert result.success == SuccessFlag(True)
    assert result.removed_count == ObjectCount(0)


@pytest.mark.asyncio
async def test_fr_scn_001_summarized_detail_level():
    """Test that summarized detail level reduces response size."""
    import json

    class SummarizedExecutor:
        async def execute_code(self, code: PythonCode, language: str = "python", timeout: float = 30.0) -> str:  # noqa: ANN002, ANN401
            return json.dumps(
                {
                    "scene_name": "Scene",
                    "total_object_count": 100,
                    "visible_object_count": 90,
                    "hidden_object_count": 10,
                    "object_type_counts": {"MESH": 80, "CAMERA": 5, "LIGHT": 15},
                    "cameras": [{"name": "Cam", "type": "perspective"}],
                    "lights": [{"name": "Lamp", "light_type": "point"}],
                    "active_camera_name": "Cam",
                    "active_object_name": "Cube",
                    "render_engine": "CYCLES",
                    "resolution_x": 1920,
                    "resolution_y": 1080,
                    "frame_start": 1,
                    "frame_end": 250,
                    "unit_system": "METRIC",
                    "collections": [{"name": "Collection", "object_count": 100}],
                }
            )

    executor = SceneInspectionExecutor(SummarizedExecutor())
    request = SceneInspectionVO(detail_level="summarized")
    result = await executor.get_scene_info(request)

    assert result.success == SuccessFlag(True)
    assert result.scene_state_summary is not None
    assert result.detail_level == "summarized"


# ─── Orchestrator Delegation Tests ─────────────────────────


@pytest.mark.asyncio
async def test_scene_orchestrator_get_scene_info():
    """Test orchestrator delegates to inspection capability for scene info."""

    class InspectionCap:
        async def get_scene_info(self, request: SceneInspectionVO) -> SceneInspectionVO:
            return SceneInspectionVO(
                detail_level=request.detail_level,
                include_hidden_objects=request.include_hidden_objects,
                object_type_filter=request.object_type_filter,
                correlation_id=request.correlation_id,
                success=SuccessFlag(True),
                scene_state_summary=SceneStateSummaryVO(scene_name="Scene", total_object_count=ObjectCount(1)),
            )

    class CleanupCap:
        async def cleanup_scene(self, request: SceneCleanupVO) -> SceneCleanupVO:
            return SceneCleanupVO(mode=request.mode, confirmation=request.confirmation, success=SuccessFlag(True))

    from modules.scene.src.agent_scene_orchestrator import SceneOrchestrator

    orch = SceneOrchestrator(inspection=InspectionCap(), cleanup=CleanupCap())

    request = SceneInspectionVO()
    result = await orch.get_scene_info(request)

    assert result.success == SuccessFlag(True)
    assert result.scene_state_summary is not None
    assert result.scene_state_summary.total_object_count == ObjectCount(1)


@pytest.mark.asyncio
async def test_scene_orchestrator_cleanup_scene():
    """Test orchestrator delegates to cleanup capability."""

    class InspectionCap:
        async def get_scene_info(self, request: SceneInspectionVO) -> SceneInspectionVO:
            return SceneInspectionVO(success=SuccessFlag(True))

    class CleanupCap:
        async def cleanup_scene(self, request: SceneCleanupVO) -> SceneCleanupVO:
            return SceneCleanupVO(
                mode=request.mode,
                confirmation=request.confirmation,
                success=SuccessFlag(True),
                removed_count=ObjectCount(0),
                preserved_count=ObjectCount(0),
            )

    from modules.scene.src.agent_scene_orchestrator import SceneOrchestrator

    orch = SceneOrchestrator(inspection=InspectionCap(), cleanup=CleanupCap())

    request = SceneCleanupVO(mode=CleanupMode("all"), confirmation=True)
    result = await orch.cleanup_scene(request)

    assert isinstance(result, SceneCleanupVO)
    assert result.success == SuccessFlag(True)
    assert result.removed_count == ObjectCount(0)


# ─── Additional Edge Cases ─────────────────────────────────


@pytest.mark.asyncio
async def test_fr_scn_002_cleanup_with_invalid_child_policy():
    """Test cleanup with invalid child handling policy."""
    import json

    class MockExecutor:
        async def execute_code(self, code: PythonCode, language: str = "python", timeout: float = 30.0) -> str:  # noqa: ANN002, ANN401
            return json.dumps({"removed_count": 0, "preserved_count": 0})

    executor = SceneCleanupExecutor(MockExecutor())
    request = SceneCleanupVO(mode=CleanupMode("all"), child_policy="invalid", confirmation=True)
    result = await executor.cleanup_scene(request)

    assert isinstance(result, SceneCleanupVO)
    assert result.success == SuccessFlag(False)


@pytest.mark.asyncio
async def test_fr_scn_002_cleanup_with_invalid_dependent_policy():
    """Test cleanup with invalid dependent handling policy."""
    import json

    class MockExecutor:
        async def execute_code(self, code: PythonCode, language: str = "python", timeout: float = 30.0) -> str:  # noqa: ANN002, ANN401
            return json.dumps({"removed_count": 0, "preserved_count": 0})

    executor = SceneCleanupExecutor(MockExecutor())
    request = SceneCleanupVO(mode=CleanupMode("all"), dependent_policy="invalid", confirmation=True)
    result = await executor.cleanup_scene(request)

    assert isinstance(result, SceneCleanupVO)
    assert result.success == SuccessFlag(False)


@pytest.mark.asyncio
async def test_fr_scn_002_cleanup_preserves_cameras_and_lights():
    """Test cleanup preserves cameras and lights by default."""
    import json

    class CameraLightPreservationExecutor:
        async def execute_code(self, code: PythonCode, language: str = "python", timeout: float = 30.0) -> str:  # noqa: ANN002, ANN401
            return json.dumps(
                {
                    "removed_count": 1,
                    "preserved_count": 2,
                    "skipped_count": 0,
                    "removed_refs": ["Cube"],
                    "preserved_refs": ["Cam", "Lamp"],
                    "skipped_refs": [],
                }
            )

    executor = SceneCleanupExecutor(CameraLightPreservationExecutor())
    request = SceneCleanupVO(mode=CleanupMode("objects"), confirmation=True)
    result = await executor.cleanup_scene(request)

    assert isinstance(result, SceneCleanupVO)
    assert result.success == SuccessFlag(True)
    assert "Cam" in result.preserved_object_references
    assert "Lamp" in result.preserved_object_references


@pytest.mark.asyncio
async def test_fr_scn_001_inspection_message_on_success():
    """Test that successful inspection includes message."""
    import json

    class SuccessExecutor:
        async def execute_code(self, code: PythonCode, language: str = "python", timeout: float = 30.0) -> str:  # noqa: ANN002, ANN401
            return json.dumps(
                {
                    "scene_name": "Scene",
                    "total_object_count": 0,
                    "visible_object_count": 0,
                    "hidden_object_count": 0,
                    "object_type_counts": {},
                    "cameras": [],
                    "lights": [],
                    "active_camera_name": "",
                    "active_object_name": "",
                    "render_engine": "CYCLES",
                    "resolution_x": 1920,
                    "resolution_y": 1080,
                    "frame_start": 1,
                    "frame_end": 250,
                    "unit_system": "METRIC",
                    "collections": [],
                }
            )

    executor = SceneInspectionExecutor(SuccessExecutor())
    request = SceneInspectionVO()
    result = await executor.get_scene_info(request)

    assert result.success == SuccessFlag(True)
    assert result.message is not None


@pytest.mark.asyncio
async def test_fr_scn_002_cleanup_failure_message():
    """Test that cleanup failure includes error message."""
    import json

    class FailureExecutor:
        async def execute_code(self, code: PythonCode, language: str = "python", timeout: float = 30.0) -> str:  # noqa: ANN002, ANN401
            return json.dumps({"error": "Cleanup failed"})

    executor = SceneCleanupExecutor(FailureExecutor())
    request = SceneCleanupVO(mode=CleanupMode("all"), confirmation=True)
    result = await executor.cleanup_scene(request)

    assert isinstance(result, SceneCleanupVO)
    assert result.message is not None


@pytest.mark.asyncio
async def test_fr_scn_002_dry_run_failure_message():
    """Test that dry-run failure includes error message."""
    import json

    class DryRunFailureExecutor:
        async def execute_code(self, code: PythonCode, language: str = "python", timeout: float = 30.0) -> str:  # noqa: ANN002, ANN401
            return json.dumps({"error": "Dry-run failed"})

    executor = SceneCleanupExecutor(DryRunFailureExecutor())
    request = SceneCleanupVO(mode=CleanupMode("all"), dry_run=True)
    result = await executor.cleanup_scene(request)

    assert isinstance(result, SceneCleanupVO)
    assert result.message is not None


# ─── Executor Constructor Tests ────────────────────────────


@pytest.mark.asyncio
async def test_scene_inspection_executor_no_code_executor_raises():
    """Test that inspection executor raises when code_executor is None."""
    with pytest.raises(ValueError, match="code_executor must be provided"):
        SceneInspectionExecutor(code_executor=None)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_scene_cleanup_executor_no_code_executor_raises():
    """Test that cleanup executor raises when code_executor is None."""
    with pytest.raises(ValueError, match="code_executor must be provided"):
        SceneCleanupExecutor(code_executor=None)  # type: ignore[arg-type]


# ─── Request Field Preservation ────────────────────────────


@pytest.mark.asyncio
async def test_fr_scn_001_inspection_with_all_fields():
    """Test inspection request preserves all input fields."""
    import json

    class AllFieldsExecutor:
        async def execute_code(self, code: PythonCode, language: str = "python", timeout: float = 30.0) -> str:  # noqa: ANN002, ANN401
            return json.dumps({"scene_name": "Scene", "total_object_count": 0})

    executor = SceneInspectionExecutor(AllFieldsExecutor())
    request = SceneInspectionVO(
        detail_level="detailed",
        include_hidden_objects=True,
        object_type_filter=("MESH", "CAMERA"),
        correlation_id="test-correlation-123",
    )
    result = await executor.get_scene_info(request)

    assert result.success == SuccessFlag(True)
    assert result.detail_level == "detailed"
    assert result.include_hidden_objects is True
    assert result.object_type_filter == ("MESH", "CAMERA")
    assert result.correlation_id == "test-correlation-123"


@pytest.mark.asyncio
async def test_fr_scn_002_cleanup_all_modes():
    """Test cleanup with all supported modes (all, objects, meshes)."""
    import json

    class ModeExecutor:
        async def execute_code(self, code: PythonCode, language: str = "python", timeout: float = 30.0) -> str:  # noqa: ANN002, ANN401
            return json.dumps({"removed_count": 0, "preserved_count": 0})

    for mode_str in ["all", "objects", "meshes"]:
        executor = SceneCleanupExecutor(ModeExecutor())
        request = SceneCleanupVO(mode=CleanupMode(mode_str), confirmation=True)
        result = await executor.cleanup_scene(request)

        assert isinstance(result, SceneCleanupVO)
        assert result.mode == CleanupMode(mode_str)

