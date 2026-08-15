"""Animation capability executor for bounded timeline and keyframe operations."""

from __future__ import annotations

import json
from collections.abc import Mapping

from modules.shared.src.animation.taxonomy_animation_vo import (
    AnimationCurveVO,
    AnimationKeyframeVO,
    AnimationMutationVO,
    AnimationStateVO,
)
from modules.shared.src.common.contract_wave_feature_protocol import IWaveFeatureProtocol

_ALLOWED_PATHS = {"location", "rotation_euler", "scale"}


class AnimationExecutor(IWaveFeatureProtocol):
    """Delegate validated animation behavior to the injected Blender gateway."""

    def __init__(self, code_executor: object) -> None:
        self._code_executor = code_executor

    async def get_state(self, object_name: str, limit: int = 100) -> AnimationStateVO:
        limit = self._bounded_limit(limit)
        code = """
import bpy
obj = bpy.data.objects.get(__OBJECT_NAME__)
if obj is None:
    raise ValueError(f"Object not found: {obj.name}")
action = obj.animation_data.action if obj.animation_data and obj.animation_data.action else None
curves = []
if action:
    for curve in list(action.fcurves)[:__LIMIT__]:
        points = [{"frame": point.co.x, "value": point.co.y, "index": curve.array_index}
                  for point in list(curve.keyframe_points)[:__LIMIT__]]
        curves.append({"data_path": curve.data_path, "array_index": curve.array_index,
                       "keyframes": points})
scene = bpy.context.scene
result = {"object_name": obj.name, "action_name": action.name if action else None,
          "frame_start": int(scene.frame_start), "frame_end": int(scene.frame_end),
          "current_frame": int(scene.frame_current), "curves": curves}
""".replace("__OBJECT_NAME__", json.dumps(str(object_name))).replace("__LIMIT__", str(limit))
        result = await self._execute(code)
        return self._state_from_mapping(result)

    async def insert_keyframe(
        self, object_name: str, frame: int, data_path: str, index: int | None = None
    ) -> AnimationMutationVO:
        path = str(data_path)
        if path not in _ALLOWED_PATHS:
            raise ValueError(f"Unsupported animation data path: {path}")
        frame = self._bounded_frame(frame)
        index_code = "None" if index is None else str(self._bounded_index(index))
        code = """
import bpy
obj = bpy.data.objects.get(__OBJECT_NAME__)
if obj is None:
    raise ValueError(f"Object not found: {obj.name}")
bpy.context.scene.frame_set(__FRAME__)
obj.keyframe_insert(data_path=__DATA_PATH__, index=__INDEX__, frame=__FRAME__)
result = {"object_name": obj.name, "data_path": __DATA_PATH__, "frame": __FRAME__, "changed": True}
""".replace("__OBJECT_NAME__", json.dumps(str(object_name)))
        code = (
            code.replace("__DATA_PATH__", json.dumps(path))
            .replace("__INDEX__", index_code)
            .replace("__FRAME__", str(frame))
        )
        result = await self._execute(code)
        return AnimationMutationVO(
            object_name=str(result["object_name"]),
            data_path=str(result["data_path"]),
            frame=int(result["frame"]),
            changed=bool(result.get("changed", True)),
        )

    async def set_timeline(
        self, frame_start: int, frame_end: int, current_frame: int | None = None
    ) -> AnimationMutationVO:
        start = self._bounded_frame(frame_start)
        end = self._bounded_frame(frame_end)
        if end < start:
            raise ValueError("frame_end must be greater than or equal to frame_start")
        current = end if current_frame is None else self._bounded_frame(current_frame)
        if not start <= current <= end:
            raise ValueError("current_frame must be within the timeline range")
        code = (
            """
import bpy
scene = bpy.context.scene
scene.frame_start = __START__
scene.frame_end = __END__
scene.frame_set(__CURRENT__)
result = {"object_name": "__scene__", "frame_start": scene.frame_start,
          "frame_end": scene.frame_end, "current_frame": scene.frame_current}
""".replace("__START__", str(start))
            .replace("__END__", str(end))
            .replace("__CURRENT__", str(current))
        )
        result = await self._execute(code)
        return AnimationMutationVO(
            object_name="__scene__",
            frame_start=int(result["frame_start"]),
            frame_end=int(result["frame_end"]),
            current_frame=int(result["current_frame"]),
        )

    async def list_keyframes(self, object_name: str, limit: int = 100) -> AnimationStateVO:
        return await self.get_state(object_name, limit)

    async def _execute(self, code: str) -> Mapping[str, object]:
        result = await self._code_executor.execute_blender_code(code)
        if not isinstance(result, Mapping):
            raise RuntimeError("Gateway returned a non-object animation result")
        return result

    @staticmethod
    def _bounded_limit(value: int) -> int:
        limit = int(value)
        if not 1 <= limit <= 1000:
            raise ValueError("limit must be between 1 and 1000")
        return limit

    @staticmethod
    def _bounded_frame(value: int) -> int:
        frame = int(value)
        if not -100000 <= frame <= 100000:
            raise ValueError("frame must be between -100000 and 100000")
        return frame

    @staticmethod
    def _bounded_index(value: int) -> int:
        index = int(value)
        if not 0 <= index <= 3:
            raise ValueError("index must be between 0 and 3")
        return index

    @staticmethod
    def _state_from_mapping(result: Mapping[str, object]) -> AnimationStateVO:
        curves = []
        for raw_curve in result.get("curves", []):
            if not isinstance(raw_curve, Mapping):
                continue
            points = tuple(
                AnimationKeyframeVO(
                    frame=float(point.get("frame", 0.0)),
                    value=float(point.get("value", 0.0)),
                    index=int(point.get("index", raw_curve.get("array_index", 0))),
                )
                for point in raw_curve.get("keyframes", [])
                if isinstance(point, Mapping)
            )
            curves.append(
                AnimationCurveVO(
                    data_path=str(raw_curve.get("data_path", "")),
                    array_index=int(raw_curve.get("array_index", 0)),
                    keyframes=points,
                )
            )
        return AnimationStateVO(
            object_name=str(result.get("object_name", "")),
            action_name=str(result["action_name"]) if result.get("action_name") else None,
            frame_start=int(result.get("frame_start", 1)),
            frame_end=int(result.get("frame_end", 250)),
            current_frame=int(result.get("current_frame", 1)),
            curves=tuple(curves),
        )
