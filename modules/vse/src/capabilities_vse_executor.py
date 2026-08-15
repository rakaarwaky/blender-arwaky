"""VSE capability executor with bounded strip and render operations."""

from __future__ import annotations

import json
from collections.abc import Mapping

from modules.shared.src.vse.taxonomy_vse_vo import SequenceMutationVO, SequenceStateVO, SequenceStripVO

_ALLOWED_STRIP_TYPES = {"COLOR", "IMAGE", "MOVIE", "SOUND"}


class VseExecutor:
    """Delegate VSE operations to the injected Blender gateway."""

    def __init__(self, code_executor: object) -> None:
        self._code_executor = code_executor

    async def inspect(self, limit: int = 100) -> SequenceStateVO:
        limit = self._bounded_limit(limit)
        code = """
import bpy
scene = bpy.context.scene
editor = scene.sequence_editor
strips = []
if editor:
    collection = getattr(editor, "strips", None) or getattr(editor, "sequences", None)
    if collection:
        for strip in list(collection)[:__LIMIT__]:
            strips.append({"name": strip.name, "strip_type": strip.type, "channel": strip.channel,
                           "frame_start": strip.frame_final_start, "frame_final": strip.frame_final_end,
                           "filepath": getattr(strip, "filepath", None)})
result = {"sequence_present": editor is not None, "strips": strips}
""".replace("__LIMIT__", str(limit))
        result = await self._execute(code)
        return SequenceStateVO(
            sequence_present=bool(result.get("sequence_present", False)),
            strips=tuple(
                SequenceStripVO(
                    name=str(strip.get("name", "")),
                    strip_type=str(strip.get("strip_type", "")),
                    channel=int(strip.get("channel", 0)),
                    frame_start=int(strip.get("frame_start", 0)),
                    frame_final=int(strip.get("frame_final", 0)),
                    filepath=str(strip["filepath"]) if strip.get("filepath") else None,
                )
                for strip in result.get("strips", [])
                if isinstance(strip, Mapping)
            ),
        )

    async def create_strip(
        self,
        strip_type: str,
        strip_name: str,
        filepath: str | None,
        channel: int,
        frame_start: int,
        frame_end: int | None = None,
    ) -> SequenceMutationVO:
        strip_type = str(strip_type).upper()
        if strip_type not in _ALLOWED_STRIP_TYPES:
            raise ValueError(f"Unsupported sequence strip type: {strip_type}")
        name = str(strip_name).strip()
        if not name or len(name) > 128:
            raise ValueError("strip_name must be 1-128 characters")
        channel = self._bounded_channel(channel)
        start = self._bounded_frame(frame_start)
        end = start + 1 if frame_end is None else self._bounded_frame(frame_end)
        if end <= start:
            raise ValueError("frame_end must be greater than frame_start")
        if strip_type != "COLOR" and not filepath:
            raise ValueError("filepath is required for media strips")
        code = """
import bpy
from pathlib import Path
scene = bpy.context.scene
editor = scene.sequence_editor_create()
strips = getattr(editor, "strips", None) or getattr(editor, "sequences", None)
if strips is None:
    raise RuntimeError("Blender sequence editor collection is unavailable")
strip_type = __STRIP_TYPE__
name = __STRIP_NAME__
filepath = __FILEPATH__
if strip_type == "COLOR":
    strip = strips.new_effect(name=name, type="COLOR", channel=__CHANNEL__, frame_start=__FRAME__, frame_end=__END__)
elif strip_type == "IMAGE":
    if not Path(filepath).is_file():
        raise FileNotFoundError(filepath)
    strip = strips.new_image(name=name, filepath=filepath, channel=__CHANNEL__, frame_start=__FRAME__)
    strip.frame_final_end = __END__
elif strip_type == "MOVIE":
    if not Path(filepath).is_file():
        raise FileNotFoundError(filepath)
    strip = strips.new_movie(name=name, filepath=filepath, channel=__CHANNEL__, frame_start=__FRAME__)
else:
    if not Path(filepath).is_file():
        raise FileNotFoundError(filepath)
    strip = strips.new_sound(name=name, filepath=filepath, channel=__CHANNEL__, frame_start=__FRAME__)
result = {"changed": True, "strip_name": strip.name, "strip_type": strip.type,
          "message": "Sequence strip created"}
"""
        for token, value in {
            "__STRIP_TYPE__": strip_type,
            "__STRIP_NAME__": name,
            "__FILEPATH__": filepath,
            "__CHANNEL__": channel,
            "__FRAME__": start,
            "__END__": end,
        }.items():
            code = code.replace(token, json.dumps(value))
        result = await self._execute(code)
        return SequenceMutationVO(
            changed=bool(result.get("changed", True)),
            strip_name=str(result.get("strip_name")) if result.get("strip_name") else name,
            strip_type=str(result.get("strip_type")) if result.get("strip_type") else strip_type,
            message=str(result.get("message", "")),
        )

    async def remove_strip(self, strip_name: str) -> SequenceMutationVO:
        name = str(strip_name).strip()
        if not name:
            raise ValueError("strip_name is required")
        code = """
import bpy
scene = bpy.context.scene
editor = scene.sequence_editor
if editor is None:
    raise ValueError("Sequence editor is not initialized")
strips = getattr(editor, "strips", None) or getattr(editor, "sequences", None)
strip = strips.get(__STRIP_NAME__) if strips else None
if strip is None:
    raise ValueError(f"Sequence strip not found: {__strip_name}")
strips.remove(strip)
result = {"changed": True, "strip_name": __STRIP_NAME__, "message": "Sequence strip removed"}
""".replace("__STRIP_NAME__", json.dumps(name))
        result = await self._execute(code)
        return SequenceMutationVO(
            changed=bool(result.get("changed", True)),
            strip_name=str(result.get("strip_name", name)),
            message=str(result.get("message", "")),
        )

    async def render(
        self, output_path: str, frame_start: int | None = None, frame_end: int | None = None
    ) -> SequenceMutationVO:
        start = None if frame_start is None else self._bounded_frame(frame_start)
        end = None if frame_end is None else self._bounded_frame(frame_end)
        if start is not None and end is not None and end < start:
            raise ValueError("frame_end must be greater than or equal to frame_start")
        code = """
import bpy
from pathlib import Path
scene = bpy.context.scene
path = Path(__OUTPUT_PATH__).expanduser().resolve()
if path.exists() and path.is_dir():
    raise ValueError("output_path must be a file path")
path.parent.mkdir(parents=True, exist_ok=True)
previous = (scene.frame_start, scene.frame_end, scene.render.filepath)
try:
    if __FRAME_START__ is not None:
        scene.frame_start = __FRAME_START__
    if __FRAME_END__ is not None:
        scene.frame_end = __FRAME_END__
    scene.render.filepath = str(path)
    bpy.ops.render.render(animation=True, write_still=True)
    result = {"changed": True, "output_path": str(path), "frame_start": scene.frame_start,
              "frame_end": scene.frame_end, "message": "Sequence render completed"}
finally:
    scene.frame_start, scene.frame_end, scene.render.filepath = previous
"""
        for token, value in {
            "__OUTPUT_PATH__": output_path,
            "__FRAME_START__": start,
            "__FRAME_END__": end,
        }.items():
            code = code.replace(token, json.dumps(value))
        result = await self._execute(code)
        return SequenceMutationVO(
            changed=bool(result.get("changed", True)),
            output_path=str(result.get("output_path")) if result.get("output_path") else None,
            frame_start=int(result["frame_start"]) if result.get("frame_start") is not None else None,
            frame_end=int(result["frame_end"]) if result.get("frame_end") is not None else None,
            message=str(result.get("message", "")),
        )

    async def _execute(self, code: str) -> Mapping[str, object]:
        result = await self._code_executor.execute_blender_code(code)
        if not isinstance(result, Mapping):
            raise RuntimeError("Gateway returned a non-object VSE result")
        return result

    @staticmethod
    def _bounded_limit(value: int) -> int:
        limit = int(value)
        if not 1 <= limit <= 1000:
            raise ValueError("limit must be between 1 and 1000")
        return limit

    @staticmethod
    def _bounded_channel(value: int) -> int:
        channel = int(value)
        if not 1 <= channel <= 128:
            raise ValueError("channel must be between 1 and 128")
        return channel

    @staticmethod
    def _bounded_frame(value: int) -> int:
        frame = int(value)
        if not -100000 <= frame <= 100000:
            raise ValueError("frame must be between -100000 and 100000")
        return frame
