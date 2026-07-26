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
        async def __call__(self, code: Prompt) -> str:
            return json.dumps({
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
            })

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
    assert result.dry_run == True
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
        async def __call__(self, code: Prompt) -> str:
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
        async def __call__(self, code: Prompt) -> str:
            return json.dumps({
                "removed_count": 1,
                "preserved_count": 2,
                "skipped_count": 1,
                "removed_refs": ["Cube"],
                "preserved_refs": ["Cam", "Lamp"],
                "skipped_refs": ["ProtectedSphere"],
            })

    executor = SceneOperateExecutor(PartialFailureExecutor())
    request = SceneCleanupVO(mode=CleanupMode("all"), confirmation=True)
    result = await executor.cleanup_scene(request)

    assert isinstance(result, SceneCleanupVO)
    assert result.success == SuccessFlag(True)
    assert result.removed_count == ObjectCount(1)
    assert result.skipped_count == ObjectCount(1)
    assert "ProtectedSphere" in result.skipped_object_references
