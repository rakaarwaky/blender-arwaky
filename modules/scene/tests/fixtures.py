"""Test fixtures for scene module.

Provides reusable mock executors and helper functions for testing
SceneInspectionExecutor and SceneCleanupExecutor.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

# ─── Default Mock Results ──────────────────────────────────────

DEFAULT_INSPECTION_RESULT: dict[str, Any] = {
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

DEFAULT_CLEANUP_RESULT: dict[str, Any] = {
    "removed_count": 2,
    "preserved_count": 2,
    "skipped_count": 0,
    "removed_refs": ["Cube", "Sphere"],
    "preserved_refs": ["Cam", "Lamp"],
    "skipped_refs": [],
}


# ─── Mock Code Executor ──────────────────────────────────────


class MockCodeExecutor:
    """Mock code executor implementing ICodeExecutionProtocol for testing scene operations."""

    def __init__(self, inspection_result: dict | None = None, cleanup_result: dict | None = None) -> None:
        self._inspection_result = inspection_result or DEFAULT_INSPECTION_RESULT
        self._cleanup_result = cleanup_result or DEFAULT_CLEANUP_RESULT

    async def execute_blender_code(self, _code: str, _request_id: str | None = None) -> str:
        """Return mock result based on whether code contains 'print(result)'."""
        if "removed_count" in _code or "preserved_count" in _code:
            # Cleanup code
            return json.dumps(self._cleanup_result)
        else:
            # Inspection code
            return json.dumps(self._inspection_result)


# ─── Fixture Helpers ─────────────────────────────────────────


def _make_executor(
    inspection_result: dict | None = None,
    cleanup_result: dict | None = None,
) -> MockCodeExecutor:
    """Create a mock executor with specified results."""
    return MockCodeExecutor(
        inspection_result=inspection_result,
        cleanup_result=cleanup_result,
    )


def _empty_scene_result() -> dict[str, Any]:
    """Return empty scene inspection result."""
    return {
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


def _make_json_executor(
    result: dict[str, Any],
    is_cleanup: bool = False,
) -> MockCodeExecutor:
    """Create a mock executor that returns a single JSON result for both inspection and cleanup."""
    return MockCodeExecutor(
        inspection_result=result,
        cleanup_result=result if not is_cleanup else result,
    )


# ─── Pytest Fixtures ─────────────────────────────────────────


@pytest.fixture
def mock_code_executor() -> MockCodeExecutor:
    """Provide a default mock code executor for scene tests."""
    return MockCodeExecutor()


@pytest.fixture
def empty_scene_executor() -> MockCodeExecutor:
    """Provide a mock executor returning empty scene results."""
    return _make_executor(inspection_result=_empty_scene_result())


@pytest.fixture
def inspection_executor(mock_code_executor: MockCodeExecutor):
    """Provide a SceneInspectionExecutor with mock code executor."""
    from modules.scene.src.capabilities_scene_inspection_executor import SceneInspectionExecutor

    return SceneInspectionExecutor(mock_code_executor, event_emitter=None)


@pytest.fixture
def cleanup_executor(mock_code_executor: MockCodeExecutor):
    """Provide a SceneCleanupExecutor with mock code executor."""
    from modules.scene.src.capabilities_scene_cleanup_executor import SceneCleanupExecutor

    return SceneCleanupExecutor(mock_code_executor)
