"""TDD suite for FR-SCN-001 (Inspect Scene State).

Exercises SceneInspector over an injected scene-state source. Verifies the
operation is read-only and renders the required overview fields.

RED → GREEN: targets SceneInspectProtocol + SceneInspector.
"""

from __future__ import annotations

from modules.scene.src.capabilities_scene_inspection import SceneInspector
from modules.shared.src.common.taxonomy_core_vo import SuccessFlag
from modules.shared.src.scene.taxonomy_scene_vo import GetSceneInfoVO


def _sample_state() -> dict:
    return {
        "objects": [
            {"name": "Cube", "type": "MESH", "visible": True},
            {"name": "Cam", "type": "CAMERA", "visible": True},
            {"name": "Lamp", "type": "LIGHT", "visible": True},
            {"name": "HiddenSphere", "type": "MESH", "visible": False},
        ],
        "render_settings": {"resolution_x": 1920, "resolution_y": 1080},
        "metadata": {"unit_scale": 1.0},
    }


def test_fr_scn_001_returns_overview_fields():
    cap = SceneInspector(state_source=_sample_state)
    vo = cap.inspect_scene()
    assert isinstance(vo, GetSceneInfoVO)
    assert vo.success == SuccessFlag(True)
    info = vo.scene_info
    # object_count excludes hidden by default
    assert info["object_count"] == 3
    assert info["camera_list"] == ["Cam"]
    assert info["light_list"] == ["Lamp"]
    assert info["render_settings"]["resolution_x"] == 1920
    assert info["metadata"]["unit_scale"] == 1.0


def test_fr_scn_001_include_hidden_toggles_count():
    cap = SceneInspector(state_source=_sample_state)
    vo = cap.inspect_scene(include_hidden=True)
    assert vo.scene_info["object_count"] == 4


def test_fr_scn_001_full_detail_lists_objects():
    cap = SceneInspector(state_source=_sample_state)
    vo = cap.inspect_scene(detail_level="full", include_hidden=True)
    assert len(vo.scene_info["objects"]) == 4


def test_fr_scn_001_failure_marks_unsuccessful():
    cap = SceneInspector(state_source=lambda: (_ for _ in ()).throw(RuntimeError("boom")))
    vo = cap.inspect_scene()
    assert vo.success == SuccessFlag(False)
    assert "boom" in str(vo.message)
