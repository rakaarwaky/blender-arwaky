"""Native Blender 5.2 NLA animation assembly capability."""

from __future__ import annotations

import json
from collections.abc import Mapping

from modules.shared.src.animation.taxonomy_animation_vo import (
    NlaBakeVO,
    NlaLayerVO,
    NlaMaskVO,
    NlaMutationVO,
    NlaStripVO,
    NlaTrackVO,
    NlaValidationVO,
)
from modules.shared.src.common.contract_wave_feature_protocol import IWaveFeatureProtocol


class AnimationNlaExecutor(IWaveFeatureProtocol):
    """Execute bounded native NLA track, strip, layer, mask, bake, and validation actions."""

    def __init__(self, code_executor: object) -> None:
        self._code_executor = code_executor

    async def _execute(self, code: str) -> Mapping[str, object]:
        result = await self._code_executor.execute_blender_code(code)
        if not isinstance(result, Mapping):
            raise RuntimeError("Gateway returned a non-object NLA result")
        return result

    @staticmethod
    def _bounded_name(value: str, label: str) -> str:
        name = str(value).strip()
        if not name or len(name) > 256:
            raise ValueError(f"{label} must be 1-256 characters")
        return name

    @staticmethod
    def _bounded_frame(value: int) -> int:
        frame = int(value)
        if not -100000 <= frame <= 100000:
            raise ValueError("frame must be between -100000 and 100000")
        return frame

    @staticmethod
    def _bounded_limit(value: int) -> int:
        limit = int(value)
        if not 1 <= limit <= 1000:
            raise ValueError("limit must be between 1 and 1000")
        return limit

    @staticmethod
    def _bounded_float(value: float, label: str, minimum: float, maximum: float) -> float:
        number = float(value)
        if not minimum <= number <= maximum:
            raise ValueError(f"{label} must be between {minimum} and {maximum}")
        return number

    @staticmethod
    def _strip_from_result(result: Mapping[str, object], fallback: Mapping[str, object]) -> NlaStripVO:
        return NlaStripVO(
            armature_name=str(result.get("armature_name", fallback.get("armature_name", ""))),
            track_name=str(result.get("track_name", fallback.get("track_name", ""))),
            strip_name=str(result.get("strip_name", fallback.get("strip_name", ""))),
            action_name=str(result.get("action_name", fallback.get("action_name", ""))),
            frame_start=float(result.get("frame_start", 0.0)),
            frame_end=float(result.get("frame_end", 0.0)),
            scale=float(result.get("scale", 1.0)),
            repeat=float(result.get("repeat", 1.0)),
            blend_in=float(result.get("blend_in", 0.0)),
            blend_out=float(result.get("blend_out", 0.0)),
            influence=float(result.get("influence", 1.0)),
            blend_type=str(result.get("blend_type", "REPLACE")),
            extrapolation=str(result.get("extrapolation", "HOLD")),
            reversed=bool(result.get("reversed", False)),
            changed=bool(result.get("changed", True)),
        )

    async def create_nla_track(
        self, armature_name: str, track_name: str, is_solo: bool = False, is_muted: bool = False
    ) -> NlaTrackVO:
        armature_name = self._bounded_name(armature_name, "armature_name")
        track_name = self._bounded_name(track_name, "track_name")
        code = (
            """
import bpy
obj = bpy.data.objects.get(__ARMATURE_NAME__)
if obj is None or obj.type != "ARMATURE":
    raise ValueError("Armature object not found: " + __ARMATURE_NAME__)
obj.animation_data_create()
track = next((item for item in obj.animation_data.nla_tracks if item.name == __TRACK_NAME__), None)
changed = track is None
if track is None:
    track = obj.animation_data.nla_tracks.new()
    track.name = __TRACK_NAME__
track.is_solo = __IS_SOLO__
track.mute = __IS_MUTED__
result = {"armature_name": obj.name, "track_name": track.name, "strip_count": len(track.strips), "is_solo": bool(track.is_solo), "is_muted": bool(track.mute), "changed": changed}
""".replace("__ARMATURE_NAME__", json.dumps(armature_name))
            .replace("__TRACK_NAME__", json.dumps(track_name))
            .replace("__IS_SOLO__", str(bool(is_solo)))
            .replace("__IS_MUTED__", str(bool(is_muted)))
        )
        result = await self._execute(code)
        return NlaTrackVO(
            armature_name=str(result.get("armature_name", armature_name)),
            track_name=str(result.get("track_name", track_name)),
            strip_count=int(result.get("strip_count", 0)),
            is_solo=bool(result.get("is_solo", is_solo)),
            is_muted=bool(result.get("is_muted", is_muted)),
            changed=bool(result.get("changed", True)),
        )

    async def add_nla_strip(
        self,
        armature_name: str,
        track_name: str,
        action_name: str,
        strip_name: str,
        frame_start: float,
        scale: float = 1.0,
        repeat: float = 1.0,
        blend_in: float = 0.0,
        blend_out: float = 0.0,
        influence: float = 1.0,
        blend_type: str = "REPLACE",
        extrapolation: str = "HOLD",
        reverse: bool = False,
    ) -> NlaStripVO:
        armature_name = self._bounded_name(armature_name, "armature_name")
        track_name = self._bounded_name(track_name, "track_name")
        action_name = self._bounded_name(action_name, "action_name")
        strip_name = self._bounded_name(strip_name, "strip_name")
        frame_start = int(self._bounded_float(frame_start, "frame_start", -100000.0, 100000.0))
        scale = self._bounded_float(scale, "scale", 0.001, 1000.0)
        repeat = self._bounded_float(repeat, "repeat", 0.001, 1000.0)
        blend_in = self._bounded_float(blend_in, "blend_in", 0.0, 100000.0)
        blend_out = self._bounded_float(blend_out, "blend_out", 0.0, 100000.0)
        influence = self._bounded_float(influence, "influence", 0.0, 1.0)
        if blend_type not in {"REPLACE", "ADD", "SUBTRACT", "MULTIPLY"}:
            raise ValueError("unsupported NLA blend_type")
        if extrapolation not in {"NOTHING", "HOLD", "HOLD_FORWARD"}:
            raise ValueError("unsupported NLA extrapolation")
        code = (
            """
import bpy
obj = bpy.data.objects.get(__ARMATURE_NAME__)
if obj is None or obj.type != "ARMATURE":
    raise ValueError("Armature object not found: " + __ARMATURE_NAME__)
obj.animation_data_create()
track = next((item for item in obj.animation_data.nla_tracks if item.name == __TRACK_NAME__), None)
if track is None:
    raise ValueError("NLA track not found: " + __TRACK_NAME__)
action = bpy.data.actions.get(__ACTION_NAME__)
if action is None:
    raise ValueError("Action not found: " + __ACTION_NAME__)
if any(item.name == __STRIP_NAME__ for item in track.strips):
    raise ValueError("NLA strip already exists: " + __STRIP_NAME__)
strip = track.strips.new(__STRIP_NAME__, __FRAME_START__, action)
strip.scale = __SCALE__
strip.repeat = __REPEAT__
strip.blend_in = __BLEND_IN__
strip.blend_out = __BLEND_OUT__
strip.influence = __INFLUENCE__
strip.blend_type = __BLEND_TYPE__
strip.extrapolation = __EXTRAPOLATION__
strip.use_reverse = __REVERSED__
result = {"armature_name": obj.name, "track_name": track.name, "strip_name": strip.name, "action_name": strip.action.name, "frame_start": float(strip.frame_start), "frame_end": float(strip.frame_end), "scale": float(strip.scale), "repeat": float(strip.repeat), "blend_in": float(strip.blend_in), "blend_out": float(strip.blend_out), "influence": float(strip.influence), "blend_type": strip.blend_type, "extrapolation": strip.extrapolation, "reversed": bool(strip.use_reverse), "changed": True}
""".replace("__ARMATURE_NAME__", json.dumps(armature_name))
            .replace("__TRACK_NAME__", json.dumps(track_name))
            .replace("__ACTION_NAME__", json.dumps(action_name))
            .replace("__STRIP_NAME__", json.dumps(strip_name))
            .replace("__FRAME_START__", str(frame_start))
            .replace("__SCALE__", str(scale))
            .replace("__REPEAT__", str(repeat))
            .replace("__BLEND_IN__", str(blend_in))
            .replace("__BLEND_OUT__", str(blend_out))
            .replace("__INFLUENCE__", str(influence))
            .replace("__BLEND_TYPE__", json.dumps(blend_type))
            .replace("__EXTRAPOLATION__", json.dumps(extrapolation))
            .replace("__REVERSED__", str(bool(reverse)))
        )
        result = await self._execute(code)
        return self._strip_from_result(
            result,
            {
                "armature_name": armature_name,
                "track_name": track_name,
                "strip_name": strip_name,
                "action_name": action_name,
            },
        )

    async def set_nla_strip(
        self,
        armature_name: str,
        track_name: str,
        strip_name: str,
        frame_start: float | None = None,
        scale: float | None = None,
        repeat: float | None = None,
        blend_in: float | None = None,
        blend_out: float | None = None,
        influence: float | None = None,
        blend_type: str | None = None,
        extrapolation: str | None = None,
        reverse: bool | None = None,
    ) -> NlaStripVO:
        armature_name = self._bounded_name(armature_name, "armature_name")
        track_name = self._bounded_name(track_name, "track_name")
        strip_name = self._bounded_name(strip_name, "strip_name")
        if all(
            value is None
            for value in (
                frame_start,
                scale,
                repeat,
                blend_in,
                blend_out,
                influence,
                blend_type,
                extrapolation,
                reverse,
            )
        ):
            raise ValueError("at least one NLA strip property must be provided")
        assignments = []
        for property_name, value in (
            ("frame_start", frame_start),
            ("scale", scale),
            ("repeat", repeat),
            ("blend_in", blend_in),
            ("blend_out", blend_out),
            ("influence", influence),
        ):
            if value is not None:
                minimum, maximum = (
                    (0.001, 1000.0)
                    if property_name in {"scale", "repeat"}
                    else (0.0, 1.0)
                    if property_name == "influence"
                    else (0.0, 100000.0)
                )
                if property_name == "frame_start":
                    minimum, maximum = -100000.0, 100000.0
                number = self._bounded_float(value, property_name, minimum, maximum)
                assignments.append(f"strip.{property_name} = {number}")
        if blend_type is not None:
            if blend_type not in {"REPLACE", "ADD", "SUBTRACT", "MULTIPLY"}:
                raise ValueError("unsupported NLA blend_type")
            assignments.append(f"strip.blend_type = {json.dumps(blend_type)}")
        if extrapolation is not None:
            if extrapolation not in {"NOTHING", "HOLD", "HOLD_FORWARD"}:
                raise ValueError("unsupported NLA extrapolation")
            assignments.append(f"strip.extrapolation = {json.dumps(extrapolation)}")
        if reverse is not None:
            assignments.append(f"strip.use_reverse = {bool(reverse)}")
        code = (
            """
import bpy
obj = bpy.data.objects.get(__ARMATURE_NAME__)
if obj is None or obj.type != "ARMATURE":
    raise ValueError("Armature object not found: " + __ARMATURE_NAME__)
obj.animation_data_create()
track = next((item for item in obj.animation_data.nla_tracks if item.name == __TRACK_NAME__), None)
if track is None:
    raise ValueError("NLA track not found: " + __TRACK_NAME__)
strip = next((item for item in track.strips if item.name == __STRIP_NAME__), None)
if strip is None:
    raise ValueError("NLA strip not found: " + __STRIP_NAME__)
__ASSIGNMENTS__
if strip.influence < 0.0 or strip.influence > 1.0:
    raise ValueError("influence must be between 0 and 1")
result = {"armature_name": obj.name, "track_name": track.name, "strip_name": strip.name, "action_name": strip.action.name if strip.action else "", "frame_start": float(strip.frame_start), "frame_end": float(strip.frame_end), "scale": float(strip.scale), "repeat": float(strip.repeat), "blend_in": float(strip.blend_in), "blend_out": float(strip.blend_out), "influence": float(strip.influence), "blend_type": strip.blend_type, "extrapolation": strip.extrapolation, "reversed": bool(strip.use_reverse), "changed": True}
""".replace("__ARMATURE_NAME__", json.dumps(armature_name))
            .replace("__TRACK_NAME__", json.dumps(track_name))
            .replace("__STRIP_NAME__", json.dumps(strip_name))
            .replace("__ASSIGNMENTS__", "\n".join(assignments))
        )
        result = await self._execute(code)
        return self._strip_from_result(
            result, {"armature_name": armature_name, "track_name": track_name, "strip_name": strip_name}
        )

    async def set_animation_layer(
        self,
        armature_name: str,
        track_name: str,
        blend_type: str | None = None,
        influence: float | None = None,
        is_solo: bool | None = None,
        is_muted: bool | None = None,
    ) -> NlaLayerVO:
        armature_name = self._bounded_name(armature_name, "armature_name")
        track_name = self._bounded_name(track_name, "track_name")
        if all(value is None for value in (blend_type, influence, is_solo, is_muted)):
            raise ValueError("at least one NLA layer property must be provided")
        if blend_type is not None and blend_type not in {"REPLACE", "ADD", "SUBTRACT", "MULTIPLY"}:
            raise ValueError("unsupported NLA blend_type")
        if influence is not None:
            influence = self._bounded_float(influence, "influence", 0.0, 1.0)
        assignments = []
        if is_solo is not None:
            assignments.append(f"track.is_solo = {bool(is_solo)}")
        if is_muted is not None:
            assignments.append(f"track.mute = {bool(is_muted)}")
        if blend_type is not None:
            assignments.append(f"strip.blend_type = {json.dumps(blend_type)}")
        if influence is not None:
            assignments.append(f"strip.influence = {influence}")
        code = (
            """
import bpy
obj = bpy.data.objects.get(__ARMATURE_NAME__)
if obj is None or obj.type != "ARMATURE":
    raise ValueError("Armature object not found: " + __ARMATURE_NAME__)
obj.animation_data_create()
track = next((item for item in obj.animation_data.nla_tracks if item.name == __TRACK_NAME__), None)
if track is None:
    raise ValueError("NLA track not found: " + __TRACK_NAME__)
for strip in track.strips:
    __ASSIGNMENTS__
result = {"armature_name": obj.name, "track_name": track.name, "blend_type": __BLEND_TYPE__, "influence": __INFLUENCE__, "is_solo": __IS_SOLO__, "is_muted": __IS_MUTED__, "changed": True}
""".replace("__ARMATURE_NAME__", json.dumps(armature_name))
            .replace("__TRACK_NAME__", json.dumps(track_name))
            .replace("__ASSIGNMENTS__", "\n    ".join(assignments))
            .replace("__BLEND_TYPE__", json.dumps(blend_type) if blend_type is not None else "None")
            .replace("__INFLUENCE__", str(influence) if influence is not None else "None")
            .replace("__IS_SOLO__", str(is_solo) if is_solo is not None else "None")
            .replace("__IS_MUTED__", str(is_muted) if is_muted is not None else "None")
        )
        result = await self._execute(code)
        return NlaLayerVO(
            armature_name=str(result.get("armature_name", armature_name)),
            track_name=str(result.get("track_name", track_name)),
            blend_type=str(result["blend_type"]) if result.get("blend_type") else None,
            influence=float(result["influence"]) if result.get("influence") is not None else None,
            is_solo=bool(result["is_solo"]) if result.get("is_solo") is not None else None,
            is_muted=bool(result["is_muted"]) if result.get("is_muted") is not None else None,
            changed=bool(result.get("changed", True)),
        )

    async def set_animation_mask(
        self, armature_name: str, track_name: str, strip_name: str, bone_names: list[str]
    ) -> NlaMaskVO:
        armature_name = self._bounded_name(armature_name, "armature_name")
        track_name = self._bounded_name(track_name, "track_name")
        strip_name = self._bounded_name(strip_name, "strip_name")
        if not isinstance(bone_names, list) or len(bone_names) > 1000:
            raise ValueError("bone_names must be a list of no more than 1000 items")
        normalized = [self._bounded_name(name, "bone_name") for name in bone_names]
        if any(name.startswith(("DEF-", "MCH-", "ORG-")) for name in normalized):
            raise ValueError("animation masks may only contain Rigify animator controls")
        code = (
            """
import bpy, json
obj = bpy.data.objects.get(__ARMATURE_NAME__)
if obj is None or obj.type != "ARMATURE":
    raise ValueError("Armature object not found: " + __ARMATURE_NAME__)
obj.animation_data_create()
track = next((item for item in obj.animation_data.nla_tracks if item.name == __TRACK_NAME__), None)
if track is None:
    raise ValueError("NLA track not found: " + __TRACK_NAME__)
strip = next((item for item in track.strips if item.name == __STRIP_NAME__), None)
if strip is None:
    raise ValueError("NLA strip not found: " + __STRIP_NAME__)
for name in __BONE_NAMES__:
    if obj.pose.bones.get(name) is None:
        raise ValueError("Pose bone not found: " + name)
metadata = json.loads(obj.get("arwaky_nla_masks", "{}"))
metadata[__MASK_KEY__] = __BONE_NAMES__
obj["arwaky_nla_masks"] = json.dumps(metadata, separators=(",", ":"))
result = {"armature_name": obj.name, "track_name": track.name, "strip_name": strip.name, "bone_names": __BONE_NAMES__, "changed": True}
""".replace("__ARMATURE_NAME__", json.dumps(armature_name))
            .replace("__TRACK_NAME__", json.dumps(track_name))
            .replace("__STRIP_NAME__", json.dumps(strip_name))
            .replace("__BONE_NAMES__", json.dumps(normalized))
            .replace("__MASK_KEY__", json.dumps(f"{track_name}:{strip_name}"))
        )
        result = await self._execute(code)
        return NlaMaskVO(
            armature_name=str(result.get("armature_name", armature_name)),
            track_name=str(result.get("track_name", track_name)),
            strip_name=str(result.get("strip_name", strip_name)),
            bone_names=tuple(str(name) for name in result.get("bone_names", normalized)),
            changed=bool(result.get("changed", True)),
        )

    async def remove_nla_strip(self, armature_name: str, track_name: str, strip_name: str) -> NlaMutationVO:
        armature_name = self._bounded_name(armature_name, "armature_name")
        track_name = self._bounded_name(track_name, "track_name")
        strip_name = self._bounded_name(strip_name, "strip_name")
        code = (
            """
import bpy
obj = bpy.data.objects.get(__ARMATURE_NAME__)
if obj is None or obj.type != "ARMATURE":
    raise ValueError("Armature object not found: " + __ARMATURE_NAME__)
obj.animation_data_create()
track = next((item for item in obj.animation_data.nla_tracks if item.name == __TRACK_NAME__), None)
if track is None:
    raise ValueError("NLA track not found: " + __TRACK_NAME__)
strip = next((item for item in track.strips if item.name == __STRIP_NAME__), None)
if strip is None:
    raise ValueError("NLA strip not found: " + __STRIP_NAME__)
track.strips.remove(strip)
result = {"armature_name": obj.name, "track_name": track.name, "strip_name": __STRIP_NAME__, "changed": True, "removed": True}
""".replace("__ARMATURE_NAME__", json.dumps(armature_name))
            .replace("__TRACK_NAME__", json.dumps(track_name))
            .replace("__STRIP_NAME__", json.dumps(strip_name))
        )
        result = await self._execute(code)
        return NlaMutationVO(
            armature_name=str(result.get("armature_name", armature_name)),
            track_name=str(result.get("track_name", track_name)),
            strip_name=str(result.get("strip_name", strip_name)),
            changed=bool(result.get("changed", True)),
            removed=bool(result.get("removed", True)),
        )

    async def bake_nla_assembly(
        self,
        armature_name: str,
        frame_start: int,
        frame_end: int,
        step: int = 1,
        output_action: str = "Wave5_Baked_Action",
        clear_constraints: bool = False,
        clear_nla: bool = False,
    ) -> NlaBakeVO:
        armature_name = self._bounded_name(armature_name, "armature_name")
        frame_start = self._bounded_frame(frame_start)
        frame_end = self._bounded_frame(frame_end)
        output_action = self._bounded_name(output_action, "output_action")
        step = int(step)
        if frame_end < frame_start or not 1 <= step <= 100:
            raise ValueError("invalid NLA bake frame range or step")
        code = (
            """
import bpy
obj = bpy.data.objects.get(__ARMATURE_NAME__)
if obj is None or obj.type != "ARMATURE":
    raise ValueError("Armature object not found: " + __ARMATURE_NAME__)
obj.animation_data_create()
for candidate in list(bpy.context.selected_objects):
    candidate.select_set(False)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj
if obj.mode != "POSE":
    bpy.ops.object.mode_set(mode="POSE")
bpy.ops.pose.select_all(action="SELECT")
obj.animation_data.action = None
before_actions = set(bpy.data.actions.keys())
bpy.ops.nla.bake(frame_start=__FRAME_START__, frame_end=__FRAME_END__, step=__STEP__, only_selected=True, visual_keying=True, clear_constraints=__CLEAR_CONSTRAINTS__, clear_parents=False, use_current_action=False, clean_curves=False, bake_types={"POSE"}, channel_types={"LOCATION", "ROTATION", "SCALE", "PROPS"})
created = [action for action in bpy.data.actions if action.name not in before_actions]
baked = obj.animation_data.action or (created[-1] if created else None)
if baked is None:
    raise RuntimeError("NLA bake did not create an Action")
baked.name = __OUTPUT_ACTION__
obj.animation_data.action = baked
if __CLEAR_NLA__:
    for track in list(obj.animation_data.nla_tracks):
        obj.animation_data.nla_tracks.remove(track)
curves = list(baked.fcurves) if hasattr(baked, "fcurves") else [curve for layer in baked.layers for strip in layer.strips for bag in getattr(strip, "channelbags", []) for curve in bag.fcurves]
result = {"armature_name": obj.name, "output_action": baked.name, "frame_start": __FRAME_START__, "frame_end": __FRAME_END__, "step": __STEP__, "keyframe_count": sum(len(curve.keyframe_points) for curve in curves), "cleared_constraints": __CLEAR_CONSTRAINTS__, "cleared_nla": __CLEAR_NLA__, "changed": True}
""".replace("__ARMATURE_NAME__", json.dumps(armature_name))
            .replace("__FRAME_START__", str(frame_start))
            .replace("__FRAME_END__", str(frame_end))
            .replace("__STEP__", str(step))
            .replace("__OUTPUT_ACTION__", json.dumps(output_action))
            .replace("__CLEAR_CONSTRAINTS__", str(bool(clear_constraints)))
            .replace("__CLEAR_NLA__", str(bool(clear_nla)))
        )
        result = await self._execute(code)
        return NlaBakeVO(
            armature_name=str(result.get("armature_name", armature_name)),
            output_action=str(result.get("output_action", output_action)),
            frame_start=int(result.get("frame_start", frame_start)),
            frame_end=int(result.get("frame_end", frame_end)),
            step=int(result.get("step", step)),
            keyframe_count=int(result.get("keyframe_count", 0)),
            cleared_constraints=bool(result.get("cleared_constraints", clear_constraints)),
            cleared_nla=bool(result.get("cleared_nla", clear_nla)),
            changed=bool(result.get("changed", True)),
        )

    async def validate_nla_assembly(self, armature_name: str, limit: int = 100) -> NlaValidationVO:
        armature_name = self._bounded_name(armature_name, "armature_name")
        limit = self._bounded_limit(limit)
        code = """
import bpy
obj = bpy.data.objects.get(__ARMATURE_NAME__)
if obj is None or obj.type != "ARMATURE":
    raise ValueError("Armature object not found: " + __ARMATURE_NAME__)
obj.animation_data_create()
tracks = list(obj.animation_data.nla_tracks)[:__LIMIT__]
strips = []
warnings = []
for track in tracks:
    for strip in list(track.strips)[:max(1, __LIMIT__ - len(strips))]:
        strips.append(strip)
        if strip.action is None:
            warnings.append("NLA strip has no Action: " + track.name + "/" + strip.name)
        if not 0.0 <= float(strip.influence) <= 1.0:
            warnings.append("NLA strip influence is out of bounds: " + track.name + "/" + strip.name)
        if strip.frame_end < strip.frame_start:
            warnings.append("NLA strip frame range is invalid: " + track.name + "/" + strip.name)
frame_values = [value for strip in strips for value in (float(strip.frame_start), float(strip.frame_end))]
result = {"armature_name": obj.name, "track_count": len(tracks), "strip_count": len(strips), "frame_start": min(frame_values) if frame_values else None, "frame_end": max(frame_values) if frame_values else None, "approved": bool(strips) and not warnings, "warnings": warnings}
""".replace("__ARMATURE_NAME__", json.dumps(armature_name)).replace("__LIMIT__", str(limit))
        result = await self._execute(code)
        return NlaValidationVO(
            armature_name=str(result.get("armature_name", armature_name)),
            track_count=int(result.get("track_count", 0)),
            strip_count=int(result.get("strip_count", 0)),
            frame_start=float(result["frame_start"]) if result.get("frame_start") is not None else None,
            frame_end=float(result["frame_end"]) if result.get("frame_end") is not None else None,
            approved=bool(result.get("approved", False)),
            warnings=tuple(str(value) for value in result.get("warnings", [])),
        )
