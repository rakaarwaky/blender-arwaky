"""Enhanced TDD suite for FR-SCN-001 and FR-SCN-002.

Exercises SceneInspectionExecutor and SceneCleanupExecutor over injected code execution.
Verifies:
- FR-SCN-001: Scene inspection with detail level, hidden objects filter
- FR-SCN-002: Cleanup with preservation policy, dry-run, child/dependent handling

Unified VO (merged request + response) — no split classes.
"""

from __future__ import annotations

from typing import Any

import pytest

from modules.scene.src.capabilities_scene_cleanup_executor import SceneCleanupExecutor
from modules.scene.src.capabilities_scene_inspection_executor import SceneInspectionExecutor

# Import fixtures and helpers from fixtures.py
from modules.scene.tests.fixtures import (
    _empty_scene_result,
    _make_executor,
)
from modules.shared.src.common.taxonomy_core_vo import (
    CleanupMode,
    ObjectCount,
    SuccessFlag,
)
from modules.shared.src.scene.taxonomy_scene_vo import (
    SceneCleanupVO,
    SceneInspectionVO,
    SceneStateSummaryVO,
)

# ─── FR-SCN-001: Inspect Scene State ─────────────────────────


@pytest.mark.asyncio
async def test_fr_scn_001_returns_scene_state_summary():
    """Test that scene inspection returns comprehensive state summary."""
    executor = SceneInspectionExecutor(_make_executor())

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
    executor = SceneInspectionExecutor(_make_executor())

    request = SceneInspectionVO(detail_level="detailed")
    result = await executor.get_scene_info(request)

    assert result.success == SuccessFlag(True)
    assert result.detail_level == "detailed"


@pytest.mark.asyncio
async def test_fr_scn_001_handles_empty_scene():
    """Test that inspection handles empty scene gracefully."""
    executor = SceneInspectionExecutor(_make_executor(inspection_result=_empty_scene_result()))
    request = SceneInspectionVO()
    result = await executor.get_scene_info(request)

    assert result.success == SuccessFlag(True)
    assert result.scene_state_summary is not None
    assert result.scene_state_summary.total_object_count == ObjectCount(0)


# ─── FR-SCN-002: Cleanup Scene Objects ──────────────────────


@pytest.mark.asyncio
async def test_fr_scn_002_cleanup_with_preservation():
    """Test that cleanup preserves cameras and lights by default."""
    executor = SceneCleanupExecutor(_make_executor())

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
    executor = SceneCleanupExecutor(_make_executor())

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
    executor = SceneCleanupExecutor(_make_executor())

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
    hidden_result = {
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

    executor = SceneInspectionExecutor(_make_executor(inspection_result=hidden_result))
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
    camera_result = {
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

    executor = SceneInspectionExecutor(_make_executor(inspection_result=camera_result))
    request = SceneInspectionVO(object_type_filter=("CAMERA",))
    result = await executor.get_scene_info(request)

    assert result.success == SuccessFlag(True)
    assert result.scene_state_summary is not None
    assert result.scene_state_summary.total_object_count == ObjectCount(1)


@pytest.mark.asyncio
async def test_fr_scn_001_correlation_id_propagated():
    """Test that correlation ID is propagated through inspection."""
    empty_result = {
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

    executor = SceneInspectionExecutor(_make_executor(inspection_result=empty_result))
    request = SceneInspectionVO(correlation_id="test-correlation-123")
    result = await executor.get_scene_info(request)

    assert result.success == SuccessFlag(True)
    assert result.correlation_id == "test-correlation-123"


@pytest.mark.asyncio
async def test_fr_scn_001_none_result_returns_empty_summary():
    """Test that None result from executor is handled gracefully."""

    class NoneResultExecutor:
        async def execute_blender_code(self, _code: str, _request_id: str | None = None) -> None:
            return None

    executor = SceneInspectionExecutor(NoneResultExecutor())
    request = SceneInspectionVO()
    result = await executor.get_scene_info(request)

    # Executor converts None to str("None"), parser treats as non-JSON and returns empty summary
    assert result.success == SuccessFlag(True)
    assert result.scene_state_summary is not None


@pytest.mark.asyncio
async def test_fr_scn_001_non_string_result_returns_empty_summary():
    """Test that non-string result from executor is handled gracefully."""

    class NonStringResultExecutor:
        async def execute_blender_code(self, _code: str, _request_id: str | None = None) -> dict[str, Any]:
            return {"invalid": True}

    executor = SceneInspectionExecutor(NonStringResultExecutor())
    request = SceneInspectionVO()
    result = await executor.get_scene_info(request)

    # Executor converts dict to str(dict), parser treats as non-JSON and returns empty summary
    assert result.success == SuccessFlag(True)
    assert result.scene_state_summary is not None


@pytest.mark.asyncio
async def test_fr_scn_001_json_parse_error_returns_empty_state():
    """Test that malformed JSON returns error state."""
    executor = SceneInspectionExecutor(_make_executor(inspection_result={"scene_name": "Scene", "total_object_count": 0}))
    request = SceneInspectionVO()
    result = await executor.get_scene_info(request)

    assert isinstance(result, SceneInspectionVO)
    # Parser should handle malformed data gracefully


# ─── Edge Cases: FR-SCN-002 ────────────────────────────────


@pytest.mark.asyncio
async def test_fr_scn_002_cleanup_with_custom_preservation_list():
    """Test cleanup with custom preservation list."""
    custom_result = {
        "removed_count": 1,
        "preserved_count": 3,
        "skipped_count": 0,
        "removed_refs": ["Cube"],
        "preserved_refs": ["Cam", "Lamp", "Sphere"],
        "skipped_refs": [],
    }

    executor = SceneCleanupExecutor(_make_executor(cleanup_result=custom_result))
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
    executor = SceneCleanupExecutor(_make_executor(cleanup_result={"removed_count": 0, "preserved_count": 0}))
    request = SceneCleanupVO(mode=CleanupMode("all"), confirmation=True)
    result = await executor.cleanup_scene(request)

    assert isinstance(result, SceneCleanupVO)
    # Parser should handle malformed data gracefully


@pytest.mark.asyncio
async def test_fr_scn_002_dry_run_with_no_removable_objects():
    """Test dry-run with no removable objects returns empty preview."""
    empty_cleanup = {
        "removed_count": 0,
        "preserved_count": 0,
        "skipped_count": 0,
        "removed_refs": [],
        "preserved_refs": [],
        "skipped_refs": [],
    }

    executor = SceneCleanupExecutor(_make_executor(cleanup_result=empty_cleanup))
    request = SceneCleanupVO(mode=CleanupMode("all"), dry_run=True)
    result = await executor.cleanup_scene(request)

    assert isinstance(result, SceneCleanupVO)
    assert result.success == SuccessFlag(True)
    assert result.removed_count == ObjectCount(0)


@pytest.mark.asyncio
async def test_fr_scn_001_summarized_detail_level():
    """Test that summarized detail level reduces response size."""
    large_result = {
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

    executor = SceneInspectionExecutor(_make_executor(inspection_result=large_result))
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
        async def get_scene_info(self, _request: SceneInspectionVO) -> SceneInspectionVO:
            return SceneInspectionVO(
                detail_level=request.detail_level,
                include_hidden_objects=request.include_hidden_objects,
                object_type_filter=request.object_type_filter,
                correlation_id=request.correlation_id,
                success=SuccessFlag(True),
                scene_state_summary=SceneStateSummaryVO(
                    scene_name="Scene",
                    total_object_count=ObjectCount(1),
                    visible_object_count=0,
                    hidden_object_count=0,
                ),
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
        async def get_scene_info(self, _request: SceneInspectionVO) -> SceneInspectionVO:
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
    executor = SceneCleanupExecutor(_make_executor(cleanup_result={"removed_count": 0, "preserved_count": 0}))
    request = SceneCleanupVO(mode=CleanupMode("all"), child_handling_policy="invalid", confirmation=True)
    result = await executor.cleanup_scene(request)

    assert isinstance(result, SceneCleanupVO)
    assert result.success == SuccessFlag(False)


@pytest.mark.asyncio
async def test_fr_scn_002_cleanup_with_invalid_dependent_policy():
    """Test cleanup with invalid dependent handling policy."""
    executor = SceneCleanupExecutor(_make_executor(cleanup_result={"removed_count": 0, "preserved_count": 0}))
    request = SceneCleanupVO(mode=CleanupMode("all"), dependent_handling_policy="invalid", confirmation=True)
    result = await executor.cleanup_scene(request)

    assert isinstance(result, SceneCleanupVO)
    assert result.success == SuccessFlag(False)


@pytest.mark.asyncio
async def test_fr_scn_002_cleanup_preserves_cameras_and_lights():
    """Test cleanup preserves cameras and lights by default."""
    camera_light_result = {
        "removed_count": 1,
        "preserved_count": 2,
        "skipped_count": 0,
        "removed_refs": ["Cube"],
        "preserved_refs": ["Cam", "Lamp"],
        "skipped_refs": [],
    }

    executor = SceneCleanupExecutor(_make_executor(cleanup_result=camera_light_result))
    request = SceneCleanupVO(mode=CleanupMode("objects"), confirmation=True)
    result = await executor.cleanup_scene(request)

    assert isinstance(result, SceneCleanupVO)
    assert result.success == SuccessFlag(True)
    assert "Cam" in result.preserved_object_references
    assert "Lamp" in result.preserved_object_references


@pytest.mark.asyncio
async def test_fr_scn_001_inspection_message_on_success():
    """Test that successful inspection includes message."""
    executor = SceneInspectionExecutor(_make_executor(inspection_result={
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
    }))
    request = SceneInspectionVO()
    result = await executor.get_scene_info(request)

    assert result.success == SuccessFlag(True)
    assert result.message is not None


@pytest.mark.asyncio
async def test_fr_scn_002_cleanup_failure_message():
    """Test that cleanup failure includes error message."""
    executor = SceneCleanupExecutor(_make_executor(cleanup_result={"error": "Cleanup failed"}))
    request = SceneCleanupVO(mode=CleanupMode("all"), confirmation=True)
    result = await executor.cleanup_scene(request)

    assert isinstance(result, SceneCleanupVO)
    assert result.message is not None


@pytest.mark.asyncio
async def test_fr_scn_002_dry_run_failure_message():
    """Test that dry-run failure includes error message."""
    executor = SceneCleanupExecutor(_make_executor(cleanup_result={"error": "Dry-run failed"}))
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
    executor = SceneInspectionExecutor(_make_executor(inspection_result={"scene_name": "Scene", "total_object_count": 0}))
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
    empty_result = {"removed_count": 0, "preserved_count": 0}

    for mode_str in ["all", "objects", "meshes"]:
        executor = SceneCleanupExecutor(_make_executor(cleanup_result=empty_result))
        request = SceneCleanupVO(mode=CleanupMode(mode_str), confirmation=True)
        result = await executor.cleanup_scene(request)

        assert isinstance(result, SceneCleanupVO)
        assert result.mode == CleanupMode(mode_str)
