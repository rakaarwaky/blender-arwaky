"""Enhanced TDD suite for FR-SCN-001 and FR-SCN-002.

Exercises SceneOperateExecutor over injected code execution. Verifies:
- FR-SCN-001: Scene inspection with detail level, hidden objects filter
- FR-SCN-002: Cleanup with preservation policy, dry-run, child/dependent handling

Unified VO (merged request + response) — no split classes.
"""

from __future__ import annotations

import pytest

from modules.scene.src.capabilities_scene_operate_executor import SceneOperateExecutor
from modules.shared.src.common.taxonomy_core_vo import (
    CleanupMode,
    ObjectCount,
    Prompt,
    SuccessFlag,
)
from modules.shared.src.scene.taxonomy_scene_command_vo import (
    SceneCleanupVO,
    SceneInspectionVO,
)

# ─── Mock Code Executor ──────────────────────────────────────


class MockCodeExecutor:
    """Mock code executor for testing scene operations."""

    def __init__(self, inspection_result: dict | None = None, cleanup_result: dict | None = None) -> None:
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

    async def __call__(self, code: Prompt) -> str:
        """Return mock result based on whether code contains 'print(result)'."""
        import json

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
    executor = SceneOperateExecutor(mock)

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
    executor = SceneOperateExecutor(mock)

    request = SceneInspectionVO(detail_level="detailed")
    result = await executor.get_scene_info(request)

    assert result.success == SuccessFlag(True)
    assert result.detail_level == "detailed"


@pytest.mark.asyncio
async def test_fr_scn_001_handles_empty_scene():
    """Test that inspection handles empty scene gracefully."""
    import json

    class EmptyExecutor:
        async def __call__(self, _code: Prompt) -> str:
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

    executor = SceneOperateExecutor(EmptyExecutor())
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
    executor = SceneOperateExecutor(mock)

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
    executor = SceneOperateExecutor(mock)

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
    executor = SceneOperateExecutor(mock)

    request = SceneCleanupVO(
        mode=CleanupMode("all"),
        dry_run=False,
        confirmation=False,
    )
    result = await executor.cleanup_scene(request)

    assert isinstance(result, SceneCleanupVO)
    assert result.success == SuccessFlag(False)
    assert "Confirmation error" in str(result.message)


@pytest.mark.asyncio
async def test_fr_scn_002_validation_error():
    """Test that invalid cleanup mode returns validation error."""
    mock = MockCodeExecutor()
    executor = SceneOperateExecutor(mock)

    # Invalid mode
    request = SceneCleanupVO(mode=CleanupMode("invalid_mode"))
    result = await executor.cleanup_scene(request)

    assert isinstance(result, SceneCleanupVO)
    assert result.success == SuccessFlag(False)
    assert "Validation error" in str(result.message)


@pytest.mark.asyncio
async def test_fr_scn_002_cleanup_modes():
    """Test different cleanup modes (all, objects, meshes)."""
    mock = MockCodeExecutor()
    executor = SceneOperateExecutor(mock)

    for mode in ["all", "objects", "meshes"]:
        request = SceneCleanupVO(mode=CleanupMode(mode), confirmation=True)
        result = await executor.cleanup_scene(request)
        assert isinstance(result, SceneCleanupVO)
        assert result.success == SuccessFlag(True)


@pytest.mark.asyncio
async def test_fr_scn_002_child_handling_policy():
    """Test that child handling policy is validated."""
    mock = MockCodeExecutor()
    executor = SceneOperateExecutor(mock)

    # Valid policy
    request = SceneCleanupVO(child_handling_policy="detach", confirmation=True)
    result = await executor.cleanup_scene(request)
    assert result.success == SuccessFlag(True)

    # Invalid policy
    request = SceneCleanupVO(child_handling_policy="invalid")
    result = await executor.cleanup_scene(request)
    assert result.success == SuccessFlag(False)


@pytest.mark.asyncio
async def test_fr_scn_002_dependent_handling_policy():
    """Test that dependent handling policy is validated."""
    mock = MockCodeExecutor()
    executor = SceneOperateExecutor(mock)

    # Valid policy
    request = SceneCleanupVO(dependent_handling_policy="reject", confirmation=True)
    result = await executor.cleanup_scene(request)
    assert result.success == SuccessFlag(True)

    # Invalid policy
    request = SceneCleanupVO(dependent_handling_policy="invalid")
    result = await executor.cleanup_scene(request)
    assert result.success == SuccessFlag(False)


# ─── Edge Cases ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_fr_scn_001_missing_active_camera():
    """Test that inspection handles missing active camera gracefully."""
    import json

    class NoCameraExecutor:
        async def __call__(self, _code: Prompt) -> str:
            data = {
                "scene_name": "Scene",
                "total_object_count": 1,
                "visible_object_count": 1,
                "hidden_object_count": 0,
                "object_type_counts": {"MESH": 1},
                "cameras": [],
                "lights": [],
                "active_camera_name": "",
                "active_object_name": "Cube",
                "render_engine": "CYCLES",
                "resolution_x": 1920,
                "resolution_y": 1080,
                "frame_start": 1,
                "frame_end": 250,
                "unit_system": "METRIC",
                "collections": [],
            }
            return json.dumps(data)

    executor = SceneOperateExecutor(NoCameraExecutor())
    request = SceneInspectionVO()
    result = await executor.get_scene_info(request)

    assert result.success == SuccessFlag(True)
    assert result.scene_state_summary is not None
    assert result.scene_state_summary.active_camera_name == ""


@pytest.mark.asyncio
async def test_fr_scn_002_cleanup_partial_failure():
    """Test that partial failure is reported clearly."""
    import json

    class PartialFailureExecutor:
        async def __call__(self, _code: Prompt) -> str:
            return json.dumps(
                {
                    "removed_count": 1,
                    "preserved_count": 2,
                    "skipped_count": 1,
                    "removed_refs": ["Cube"],
                    "preserved_refs": ["Cam", "Lamp"],
                    "skipped_refs": ["ProtectedSphere"],
                }
            )

    executor = SceneOperateExecutor(PartialFailureExecutor())
    request = SceneCleanupVO(mode=CleanupMode("all"), confirmation=True)
    result = await executor.cleanup_scene(request)

    assert isinstance(result, SceneCleanupVO)
    assert result.success == SuccessFlag(True)
    assert result.removed_count == ObjectCount(1)
    assert result.skipped_count == ObjectCount(1)
    assert "ProtectedSphere" in result.skipped_object_references


# ─── Additional Edge Cases ──────────────────────────────────


@pytest.mark.asyncio
async def test_fr_scn_001_hidden_objects_included_when_requested():
    """Test that inspection includes hidden objects when explicitly requested."""
    import json

    class HiddenObjectsExecutor:
        async def __call__(self, _code: Prompt) -> str:
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
                    "collections": [],
                }
            )

    executor = SceneOperateExecutor(HiddenObjectsExecutor())
    request = SceneInspectionVO(include_hidden_objects=True)
    result = await executor.get_scene_info(request)

    assert result.success == SuccessFlag(True)
    assert result.scene_state_summary is not None
    assert result.scene_state_summary.hidden_object_count == ObjectCount(2)


@pytest.mark.asyncio
async def test_fr_scn_001_object_type_filter():
    """Test that inspection supports object type filter."""
    import json

    class FilteredExecutor:
        async def __call__(self, _code: Prompt) -> str:
            return json.dumps(
                {
                    "scene_name": "Scene",
                    "total_object_count": 2,
                    "visible_object_count": 2,
                    "hidden_object_count": 0,
                    "object_type_counts": {"MESH": 2},
                    "cameras": [],
                    "lights": [],
                    "active_camera_name": "",
                    "active_object_name": "Cube",
                    "render_engine": "CYCLES",
                    "resolution_x": 1920,
                    "resolution_y": 1080,
                    "frame_start": 1,
                    "frame_end": 250,
                    "unit_system": "METRIC",
                    "collections": [],
                }
            )

    executor = SceneOperateExecutor(FilteredExecutor())
    request = SceneInspectionVO(object_type_filter=("MESH",))
    result = await executor.get_scene_info(request)

    assert result.success == SuccessFlag(True)
    assert result.scene_state_summary is not None
    assert "MESH" in result.scene_state_summary.object_type_counts


@pytest.mark.asyncio
async def test_fr_scn_001_correlation_id_propagated():
    """Test that correlation ID is preserved through inspection."""
    import json

    class CorrelatedExecutor:
        async def __call__(self, _code: Prompt) -> str:
            return json.dumps({"scene_name": "Scene", "total_object_count": 0})

    executor = SceneOperateExecutor(CorrelatedExecutor())
    request = SceneInspectionVO(correlation_id="corr-123")
    result = await executor.get_scene_info(request)

    assert result.success == SuccessFlag(True)
    assert result.correlation_id == "corr-123"


@pytest.mark.asyncio
async def test_fr_scn_001_none_result_returns_error():
    """Test that None inspection result returns error (executor rejects non-string)."""

    class NoneResultExecutor:
        async def __call__(self, _code: Prompt) -> str | None:
            return None  # type: ignore[return-value]

    executor = SceneOperateExecutor(NoneResultExecutor())
    request = SceneInspectionVO()
    result = await executor.get_scene_info(request)

    assert result.success == SuccessFlag(False)
    assert result.scene_state_summary is None
    assert "failed" in str(result.message).lower()


@pytest.mark.asyncio
async def test_fr_scn_001_non_string_result_returns_error():
    """Test that non-string inspection result returns error (executor rejects non-string)."""

    class NonStringResultExecutor:
        async def __call__(self, _code: Prompt) -> dict:  # type: ignore[return-value]
            return {"scene_name": "Scene"}

    executor = SceneOperateExecutor(NonStringResultExecutor())
    request = SceneInspectionVO()
    result = await executor.get_scene_info(request)

    assert result.success == SuccessFlag(False)
    assert result.scene_state_summary is None
    assert "failed" in str(result.message).lower()


@pytest.mark.asyncio
async def test_fr_scn_001_json_parse_error_returns_empty_state():
    """Test that malformed JSON result returns empty state summary."""

    class MalformedJSONExecutor:
        async def __call__(self, _code: Prompt) -> str:  # type: ignore[return-value]
            return "not valid json {"

    executor = SceneOperateExecutor(MalformedJSONExecutor())
    request = SceneInspectionVO()
    result = await executor.get_scene_info(request)

    assert result.success == SuccessFlag(True)
    assert result.scene_state_summary is not None
    assert result.scene_state_summary.total_object_count == ObjectCount(0)


@pytest.mark.asyncio
async def test_fr_scn_002_cleanup_with_custom_preservation_list():
    """Test cleanup with explicit preservation list of object names."""
    import json

    class CustomPreservationExecutor:
        async def __call__(self, _code: Prompt) -> str:
            return json.dumps(
                {
                    "removed_count": 1,
                    "preserved_count": 3,
                    "skipped_count": 0,
                    "removed_refs": ["Cube"],
                    "preserved_refs": ["Cam", "Lamp", "ProtectedObj"],
                    "skipped_refs": [],
                }
            )

    executor = SceneOperateExecutor(CustomPreservationExecutor())
    request = SceneCleanupVO(
        mode=CleanupMode("all"),
        preservation_list=("camera", "light", "ProtectedObj"),
        confirmation=True,
    )
    result = await executor.cleanup_scene(request)

    assert isinstance(result, SceneCleanupVO)
    assert result.success == SuccessFlag(True)
    assert "ProtectedObj" in result.preserved_object_references


@pytest.mark.asyncio
async def test_fr_scn_002_cleanup_malformed_json_returns_empty():
    """Test that malformed JSON in cleanup result returns safe empty counts."""
    import json

    class MalformedCleanupExecutor:
        async def __call__(self, _code: Prompt) -> str:
            return "not valid json {"

    executor = SceneOperateExecutor(MalformedCleanupExecutor())
    request = SceneCleanupVO(mode=CleanupMode("all"), confirmation=True)
    result = await executor.cleanup_scene(request)

    assert isinstance(result, SceneCleanupVO)
    assert result.success == SuccessFlag(True)
    assert result.removed_count == ObjectCount(0)
    assert result.preserved_count == ObjectCount(0)
    assert result.skipped_count == ObjectCount(0)


@pytest.mark.asyncio
async def test_fr_scn_002_dry_run_with_no_removable_objects():
    """Test dry-run when scene has no removable objects."""
    import json

    class EmptySceneExecutor:
        async def __call__(self, _code: Prompt) -> str:
            return json.dumps(
                {
                    "removed_count": 0,
                    "preserved_count": 2,
                    "skipped_count": 0,
                    "removed_refs": [],
                    "preserved_refs": ["Cam", "Lamp"],
                    "skipped_refs": [],
                }
            )

    executor = SceneOperateExecutor(EmptySceneExecutor())
    request = SceneCleanupVO(mode=CleanupMode("all"), dry_run=True)
    result = await executor.cleanup_scene(request)

    assert isinstance(result, SceneCleanupVO)
    assert result.success == SuccessFlag(True)
    assert result.dry_run is True
    assert result.removed_count == ObjectCount(0)


@pytest.mark.asyncio
async def test_fr_scn_001_summarized_detail_level():
    """Test inspection with summarized detail level for large scenes."""
    import json

    class SummarizedExecutor:
        async def __call__(self, _code: Prompt) -> str:
            return json.dumps(
                {
                    "scene_name": "LargeScene",
                    "total_object_count": 10000,
                    "visible_object_count": 8000,
                    "hidden_object_count": 2000,
                    "object_type_counts": {"MESH": 7000, "CAMERA": 500, "LIGHT": 500},
                    "cameras": [{"name": "Cam", "type": "perspective"}],
                    "lights": [{"name": "Lamp", "light_type": "point"}],
                    "active_camera_name": "Cam",
                    "active_object_name": "ActiveMesh",
                    "render_engine": "CYCLES",
                    "resolution_x": 1920,
                    "resolution_y": 1080,
                    "frame_start": 1,
                    "frame_end": 250,
                    "unit_system": "METRIC",
                    "collections": [{"name": "Collection", "object_count": 10000}],
                }
            )

    executor = SceneOperateExecutor(SummarizedExecutor())
    request = SceneInspectionVO(detail_level="summary")
    result = await executor.get_scene_info(request)

    assert result.success == SuccessFlag(True)
    assert result.scene_state_summary is not None
    assert result.scene_state_summary.total_object_count == ObjectCount(10000)


@pytest.mark.asyncio
async def test_fr_scn_002_cleanup_with_invalid_child_policy():
    """Test that cleanup rejects invalid child handling policy."""
    mock = MockCodeExecutor()
    executor = SceneOperateExecutor(mock)

    request = SceneCleanupVO(
        mode=CleanupMode("all"),
        child_handling_policy="invalid",
        confirmation=True,
    )
    result = await executor.cleanup_scene(request)

    assert isinstance(result, SceneCleanupVO)
    assert result.success == SuccessFlag(False)
    assert "Validation error" in str(result.message)


@pytest.mark.asyncio
async def test_fr_scn_002_cleanup_with_invalid_dependent_policy():
    """Test that cleanup rejects invalid dependent handling policy."""
    mock = MockCodeExecutor()
    executor = SceneOperateExecutor(mock)

    request = SceneCleanupVO(
        mode=CleanupMode("all"),
        dependent_handling_policy="invalid",
        confirmation=True,
    )
    result = await executor.cleanup_scene(request)

    assert isinstance(result, SceneCleanupVO)
    assert result.success == SuccessFlag(False)
    assert "Validation error" in str(result.message)


@pytest.mark.asyncio
async def test_scene_orchestrator_get_scene_info():
    """Test orchestrator delegates to inspection capability for scene info."""
    import json

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

    orch = SceneOrchestrator(inspection=InspectionCap(), cleanup=CleanupCap())

    request = SceneInspectionVO()
    result = await orch.get_scene_info(request)

    assert result.success == SuccessFlag(True)
    assert result.scene_state_summary is not None
    assert result.scene_state_summary.total_object_count == ObjectCount(1)


@pytest.mark.asyncio
async def test_scene_orchestrator_cleanup_scene():
    """Test orchestrator delegates to cleanup capability."""
    import json

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

    orch = SceneOrchestrator(inspection=InspectionCap(), cleanup=CleanupCap())

    request = SceneCleanupVO(mode=CleanupMode("all"), confirmation=True)
    result = await orch.cleanup_scene(request)

    assert isinstance(result, SceneCleanupVO)
    assert result.success == SuccessFlag(True)
    assert result.removed_count == ObjectCount(0)


@pytest.mark.asyncio
async def test_scene_operate_executor_no_code_executor_raises():
    """Test that executor raises when code_executor is None."""
    with pytest.raises(ValueError, match="code_executor must be provided"):
        SceneOperateExecutor(code_executor=None)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_fr_scn_001_inspection_with_all_fields():
    """Test inspection request preserves all input fields."""
    import json

    class AllFieldsExecutor:
        async def __call__(self, _code: Prompt) -> str:
            return json.dumps({"scene_name": "Scene", "total_object_count": 0})

    executor = SceneOperateExecutor(AllFieldsExecutor())
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

    for mode_str in ["all", "objects", "meshes"]:
        class ModeExecutor:
            async def __call__(self, _code: Prompt) -> str:
                return json.dumps({"removed_count": 1, "preserved_count": 1})

        executor = SceneOperateExecutor(ModeExecutor())
        request = SceneCleanupVO(mode=CleanupMode(mode_str), confirmation=True)
        result = await executor.cleanup_scene(request)

        assert isinstance(result, SceneCleanupVO)
        assert result.success == SuccessFlag(True)


@pytest.mark.asyncio
async def test_fr_scn_002_cleanup_preserves_cameras_and_lights():
    """Test that cleanup preserves cameras and lights by default."""
    import json

    class CameraLightPreservationExecutor:
        async def __call__(self, _code: Prompt) -> str:
            return json.dumps(
                {
                    "removed_count": 2,
                    "preserved_count": 2,
                    "skipped_count": 0,
                    "removed_refs": ["Cube", "Sphere"],
                    "preserved_refs": ["Cam", "Lamp"],
                    "skipped_refs": [],
                }
            )

    executor = SceneOperateExecutor(CameraLightPreservationExecutor())
    request = SceneCleanupVO(mode=CleanupMode("all"), confirmation=True)
    result = await executor.cleanup_scene(request)

    assert isinstance(result, SceneCleanupVO)
    assert result.success == SuccessFlag(True)
    assert "Cam" in result.preserved_object_references
    assert "Lamp" in result.preserved_object_references
    assert "Cube" in result.removed_object_references
    assert "Sphere" in result.removed_object_references


@pytest.mark.asyncio
async def test_fr_scn_001_inspection_message_on_success():
    """Test that successful inspection returns proper message."""
    import json

    class SuccessExecutor:
        async def __call__(self, _code: Prompt) -> str:
            return json.dumps({"scene_name": "Scene", "total_object_count": 0})

    executor = SceneOperateExecutor(SuccessExecutor())
    request = SceneInspectionVO()
    result = await executor.get_scene_info(request)

    assert result.success == SuccessFlag(True)
    assert "retrieved successfully" in str(result.message).lower()


@pytest.mark.asyncio
async def test_fr_scn_002_cleanup_failure_message():
    """Test that cleanup failure returns error message."""
    import json

    class FailureExecutor:
        async def __call__(self, _code: Prompt) -> str:
            raise RuntimeError("Blender execution failed")

    executor = SceneOperateExecutor(FailureExecutor())
    request = SceneCleanupVO(mode=CleanupMode("all"), confirmation=True)
    result = await executor.cleanup_scene(request)

    assert isinstance(result, SceneCleanupVO)
    assert result.success == SuccessFlag(False)
    assert "failed" in str(result.message).lower()


@pytest.mark.asyncio
async def test_fr_scn_002_dry_run_failure_message():
    """Test that dry-run failure returns error message."""
    import json

    class DryRunFailureExecutor:
        async def __call__(self, _code: Prompt) -> str:
            raise RuntimeError("Dry run failed")

    executor = SceneOperateExecutor(DryRunFailureExecutor())
    request = SceneCleanupVO(mode=CleanupMode("all"), dry_run=True)
    result = await executor.cleanup_scene(request)

    assert isinstance(result, SceneCleanupVO)
    assert result.success == SuccessFlag(False)
    assert "failed" in str(result.message).lower()
