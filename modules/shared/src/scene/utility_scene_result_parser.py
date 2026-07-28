"""Scene utility: result parsers.

Stateless parsers for Blender execution output.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from ..common.taxonomy_core_vo import (
    ObjectCount,
    ObjectName,
    ObjectType,
    Prompt,
    RenderEngine,
    ResolutionX,
    ResolutionY,
    SceneId,
)
from .taxonomy_scene_vo import (
    CameraInfoVO,
    CollectionSummaryVO,
    LightInfoVO,
    SceneCleanupMetricsVO,
    SceneStateSummaryVO,
)

logger = logging.getLogger("BlenderMCPServer")


def parse_scene_state_summary(raw: Prompt | None) -> SceneStateSummaryVO:
    """Parse raw execution output into SceneStateSummaryVO."""
    if raw is None:
        logger.warning("Scene inspection result is None; returning empty state")
        return SceneStateSummaryVO()

    text = str(raw)

    try:
        data = json.loads(text)
    except Exception as exc:
        logger.warning("Failed to parse scene inspection result: %s", exc)
        return SceneStateSummaryVO()

    if not isinstance(data, dict):
        logger.warning("Scene inspection result is not a JSON object")
        return SceneStateSummaryVO()

    cameras_raw = data.get("cameras", [])
    if not isinstance(cameras_raw, list):
        cameras_raw = []

    lights_raw = data.get("lights", [])
    if not isinstance(lights_raw, list):
        lights_raw = []

    collections_raw = data.get("collections", [])
    if not isinstance(collections_raw, list):
        collections_raw = []

    object_type_counts_raw = data.get("object_type_counts", {})
    if not isinstance(object_type_counts_raw, dict):
        object_type_counts_raw = {}

    cameras = tuple(
        CameraInfoVO(
            name=ObjectName(str(item.get("name", ""))),
            type=ObjectType("CAMERA"),
            data_type=str(item.get("type", "")),
        )
        for item in cameras_raw
        if isinstance(item, dict)
    )

    lights = tuple(
        LightInfoVO(
            name=ObjectName(str(item.get("name", ""))),
            type=ObjectType("LIGHT"),
            light_type=str(item.get("light_type", "")),
        )
        for item in lights_raw
        if isinstance(item, dict)
    )

    collections = tuple(
        CollectionSummaryVO(
            name=ObjectName(str(item.get("name", ""))),
            object_count=ObjectCount(int(item.get("object_count", 0))),
        )
        for item in collections_raw
        if isinstance(item, dict)
    )

    object_type_counts = {
        ObjectType(str(key)): ObjectCount(int(value))
        for key, value in object_type_counts_raw.items()
    }

    scene_name = str(data.get("scene_name", ""))

    return SceneStateSummaryVO(
        scene_name=scene_name,
        scene_identifier=SceneId(scene_name),
        total_object_count=ObjectCount(int(data.get("total_object_count", 0))),
        visible_object_count=ObjectCount(int(data.get("visible_object_count", 0))),
        hidden_object_count=ObjectCount(int(data.get("hidden_object_count", 0))),
        object_type_counts=object_type_counts,
        cameras=cameras,
        lights=lights,
        active_camera_name=ObjectName(str(data.get("active_camera_name", ""))),
        active_object_name=ObjectName(str(data.get("active_object_name", ""))),
        render_engine=RenderEngine(str(data.get("render_engine", "CYCLES"))),
        resolution_x=ResolutionX(int(data.get("resolution_x", 1920))),
        resolution_y=ResolutionY(int(data.get("resolution_y", 1080))),
        frame_start=int(data.get("frame_start", 1)),
        frame_end=int(data.get("frame_end", 250)),
        unit_system=str(data.get("unit_system", "METRIC")),
        collection_count=ObjectCount(len(collections)),
        collections=collections,
    )


def parse_cleanup_metrics(raw: Prompt | None) -> SceneCleanupMetricsVO:
    """Parse raw execution output into cleanup metrics."""
    if raw is None:
        logger.warning("Cleanup result is None; returning empty metrics")
        return SceneCleanupMetricsVO()

    text = str(raw)

    try:
        data = json.loads(text)
    except Exception as exc:
        logger.warning("Failed to parse cleanup result: %s", exc)
        return SceneCleanupMetricsVO()

    if not isinstance(data, dict):
        logger.warning("Cleanup result is not a JSON object")
        return SceneCleanupMetricsVO()

    def _as_object_name_tuple(key: str) -> tuple[ObjectName, ...]:
        values = data.get(key, [])
        if not isinstance(values, list):
            return ()
        return tuple(ObjectName(str(item)) for item in values)

    return SceneCleanupMetricsVO(
        removed_count=ObjectCount(int(data.get("removed_count", 0))),
        preserved_count=ObjectCount(int(data.get("preserved_count", 0))),
        skipped_count=ObjectCount(int(data.get("skipped_count", 0))),
        removed_object_references=_as_object_name_tuple("removed_refs"),
        preserved_object_references=_as_object_name_tuple("preserved_refs"),
        skipped_object_references=_as_object_name_tuple("skipped_refs"),
    )