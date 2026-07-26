"""Scene inspection capability — read-only scene overview.

FR-SCN-001: Inspect Scene State
- Returns object count, camera list, light list, render settings summary, metadata
- Strictly read-only; never mutates scene state

AES Capabilities layer — concrete implementation of SceneInspectProtocol.
"""

from __future__ import annotations

import logging
from collections.abc import Callable

from modules.shared.src.common.taxonomy_core_vo import Prompt, SuccessFlag
from modules.shared.src.scene.contract_scene_inspect_protocol import SceneInspectProtocol
from modules.shared.src.scene.taxonomy_scene_vo import SceneInspectionVO

logger = logging.getLogger("BlenderMCPServer")


class SceneInspector(SceneInspectProtocol):
    """Concrete read-only scene inspector.

    FR-SCN-001: The scene-state source is injected (a real deployment reads it
    from Blender via the server module). The capability only projects the state
    into a SceneInspectionVO; it performs no mutations.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(self, state_source: Callable[[], dict] | None = None) -> None:
        self._state_source = state_source or (lambda: {})

    # ─── Block 2: Protocol Method Implementation ─────────────

    def inspect_scene(
        self,
        detail_level: str = "standard",
        include_hidden: bool = False,
    ) -> SceneInspectionVO:
        """Return a structured, read-only scene overview.

        FR-SCN-001: Projects the injected scene state into a SceneInspectionVO.
        `include_hidden` controls whether hidden objects are counted.
        """
        try:
            raw = self._state_source()
            summary = self._summarize(raw, detail_level, include_hidden)
            return SceneInspectionVO(success=SuccessFlag(True), scene_info=summary)
        except Exception as e:
            logger.error("Scene inspection failed: %s", e)
            return SceneInspectionVO(
                success=SuccessFlag(False),
                message=Prompt(f"inspection failed: {e}"),
            )

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    def _summarize(self, raw: dict, detail_level: str, include_hidden: bool) -> dict:
        objects = raw.get("objects", [])
        visible = [o for o in objects if o.get("visible", True)]
        included = objects if include_hidden else visible
        cameras = [o["name"] for o in objects if o.get("type") == "CAMERA"]
        lights = [o["name"] for o in objects if o.get("type") == "LIGHT"]
        summary = {
            "object_count": len(included),
            "camera_list": cameras,
            "light_list": lights,
            "render_settings": raw.get("render_settings", {}),
            "metadata": raw.get("metadata", {}),
        }
        if detail_level == "full":
            summary["objects"] = [
                {"name": o.get("name"), "type": o.get("type")} for o in included
            ]
        return summary

    def __repr__(self) -> str:
        return "SceneInspector()"
