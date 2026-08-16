"""Native Wave 4 retargeting executor mixin for Blender 5.2."""

from __future__ import annotations

import json
from collections.abc import Mapping

from modules.shared.src.animation.taxonomy_animation_vo import (
    AnimationImportVO,
    AnimationValidationVO,
    BakeRetargetVO,
    BoneMappingStateVO,
    BoneMappingVO,
    RestPoseValidationVO,
    RetargetAnimationVO,
    RootMotionVO,
)
from modules.shared.src.common.contract_wave_feature_protocol import IWaveFeatureProtocol


class AnimationRetargetExecutor(IWaveFeatureProtocol):
    """Execute native Wave 4 retargeting operations through the injected gateway."""

    def __init__(self, code_executor: object) -> None:
        self._code_executor = code_executor

    async def _execute(self, code: str) -> Mapping[str, object]:
        result = await self._code_executor.execute_blender_code(code)
        if not isinstance(result, Mapping):
            raise RuntimeError("Gateway returned a non-object retargeting result")
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

    async def import_motion_capture(self, source_path: str, importer: str | None = None) -> AnimationImportVO:
        path = str(source_path).strip()
        if not path or len(path) > 4096:
            raise ValueError("source_path must be 1-4096 characters")
        suffix = path.rsplit(".", 1)[-1].lower() if "." in path else ""
        selected_importer = str(importer or suffix).lower()
        if selected_importer not in {"fbx", "bvh"}:
            raise ValueError("importer must be fbx or bvh")
        code = """
import bpy
before_objects = set(bpy.data.objects.keys())
before_actions = set(bpy.data.actions.keys())
if __IMPORTER__ == "fbx":
    bpy.ops.import_scene.fbx(filepath=__SOURCE_PATH__)
else:
    bpy.ops.import_anim.bvh(filepath=__SOURCE_PATH__)
result = {"source_path": __SOURCE_PATH__, "importer": __IMPORTER__, "imported_objects": [name for name in bpy.data.objects if name not in before_objects], "action_names": [name for name in bpy.data.actions if name not in before_actions], "warnings": []}
""".replace("__SOURCE_PATH__", json.dumps(path)).replace("__IMPORTER__", json.dumps(selected_importer))
        result = await self._execute(code)
        return AnimationImportVO(
            source_path=str(result.get("source_path", path)),
            importer=str(result.get("importer", selected_importer)),
            imported_objects=tuple(str(value) for value in result.get("imported_objects", [])),
            action_names=tuple(str(value) for value in result.get("action_names", [])),
            warnings=tuple(str(value) for value in result.get("warnings", [])),
        )

    async def build_bone_mapping(
        self,
        source_armature: str,
        target_armature: str,
        preset: str = "exact",
        overrides: Mapping[str, str] | None = None,
        unmapped_policy: str = "report",
    ) -> BoneMappingStateVO:
        source_armature = self._bounded_name(source_armature, "source_armature")
        target_armature = self._bounded_name(target_armature, "target_armature")
        preset = str(preset).lower()
        if preset not in {"exact", "mixamo", "bvh"}:
            raise ValueError("preset must be exact, mixamo, or bvh")
        unmapped_policy = str(unmapped_policy).lower()
        if unmapped_policy not in {"report", "error"}:
            raise ValueError("unmapped_policy must be report or error")
        override_mapping = dict(overrides or {})
        if len(override_mapping) > 1000:
            raise ValueError("overrides must not contain more than 1000 entries")
        code = """
import bpy
source = bpy.data.objects.get(__SOURCE_ARMATURE__)
target = bpy.data.objects.get(__TARGET_ARMATURE__)
if source is None or source.type != "ARMATURE":
    raise ValueError("Source armature not found: " + __SOURCE_ARMATURE__)
if target is None or target.type != "ARMATURE":
    raise ValueError("Target armature not found: " + __TARGET_ARMATURE__)
source_names = {bone.name for bone in source.data.bones}
target_names = {bone.name for bone in target.data.bones}
mapping = {}
for source_name, target_name in __OVERRIDES__.items():
    if source_name in source_names and target_name in target_names:
        mapping[source_name] = target_name
    else:
        raise ValueError("Invalid mapping override: " + str(source_name) + " -> " + str(target_name))
if __PRESET__ == "exact":
    for name in sorted(source_names & target_names):
        mapping.setdefault(name, name)
else:
    aliases = {"Hips": "root", "Spine": "spine", "Spine1": "spine.001", "Spine2": "spine.002", "Neck": "neck", "Head": "head", "LeftShoulder": "shoulder.L", "RightShoulder": "shoulder.R", "LeftArm": "upper_arm.L", "RightArm": "upper_arm.R", "LeftForeArm": "forearm.L", "RightForeArm": "forearm.R", "LeftHand": "hand_ik.L", "RightHand": "hand_ik.R"}
    for source_name, target_name in aliases.items():
        if source_name in source_names and target_name in target_names:
            mapping.setdefault(source_name, target_name)
mappings = [{"source_bone": source_name, "target_bone": target_name, "side": "left" if target_name.endswith(".L") else "right" if target_name.endswith(".R") else None, "confidence": 1.0 if source_name in __OVERRIDES__ else 0.8 if __PRESET__ != "exact" else 1.0} for source_name, target_name in sorted(mapping.items())]
unmapped_source = sorted(source_names - set(mapping))
unmapped_target = sorted(target_names - set(mapping.values()))
if __UNMAPPED_POLICY__ == "error" and unmapped_source:
    raise ValueError("Unmapped source bones: " + ", ".join(unmapped_source[:50]))
result = {"source_armature": source.name, "target_armature": target.name, "preset": __PRESET__, "mappings": mappings, "unmapped_source": unmapped_source, "unmapped_target": unmapped_target}
""".replace("__SOURCE_ARMATURE__", json.dumps(source_armature)).replace(
            "__TARGET_ARMATURE__", json.dumps(target_armature)
        ).replace("__PRESET__", json.dumps(preset)).replace("__OVERRIDES__", json.dumps(override_mapping)).replace(
            "__UNMAPPED_POLICY__", json.dumps(unmapped_policy)
        )
        result = await self._execute(code)
        return self._mapping_from_result(result, source_armature, target_armature, preset)

    async def validate_rest_pose(
        self, source_armature: str, target_armature: str, mapping: Mapping[str, object], tolerance: float = 0.25
    ) -> RestPoseValidationVO:
        source_armature = self._bounded_name(source_armature, "source_armature")
        target_armature = self._bounded_name(target_armature, "target_armature")
        tolerance = float(tolerance)
        if not 0.0 < tolerance <= 10.0:
            raise ValueError("tolerance must be greater than 0 and no greater than 10")
        mapping_payload = self._bounded_mapping_payload(mapping)
        code = """
import bpy
source = bpy.data.objects.get(__SOURCE_ARMATURE__)
target = bpy.data.objects.get(__TARGET_ARMATURE__)
if source is None or source.type != "ARMATURE" or target is None or target.type != "ARMATURE":
    raise ValueError("Both source and target armatures are required")
warnings = []
position_warning_count = 0
ratios = []
for item in __MAPPING__:
    source_bone = source.data.bones.get(item["source_bone"])
    target_bone = target.data.bones.get(item["target_bone"])
    if source_bone is None or target_bone is None:
        warnings.append("Missing mapped bone: " + str(item))
        continue
    source_length = max(float(source_bone.length), 0.000001)
    target_length = max(float(target_bone.length), 0.000001)
    ratios.append(target_length / source_length)
    distance = (source_bone.head_local - target_bone.head_local).length if source == target else 0.0
    if distance > __TOLERANCE__:
        position_warning_count += 1
        warnings.append("Rest-pose head distance exceeds tolerance for " + item["source_bone"])
scale_ratio = sum(ratios) / len(ratios) if ratios else 0.0
approved = bool(__MAPPING__) and position_warning_count == 0
if not ratios:
    warnings.append("No mapped bones were available for rest-pose validation")
result = {"source_armature": source.name, "target_armature": target.name, "approved": approved, "mapped_count": len(__MAPPING__), "position_warning_count": position_warning_count, "scale_ratio": scale_ratio, "warnings": warnings}
""".replace("__SOURCE_ARMATURE__", json.dumps(source_armature)).replace(
            "__TARGET_ARMATURE__", json.dumps(target_armature)
        ).replace("__MAPPING__", json.dumps(mapping_payload)).replace("__TOLERANCE__", str(tolerance))
        result = await self._execute(code)
        return RestPoseValidationVO(
            source_armature=str(result.get("source_armature", source_armature)),
            target_armature=str(result.get("target_armature", target_armature)),
            approved=bool(result.get("approved", False)),
            mapped_count=int(result.get("mapped_count", 0)),
            position_warning_count=int(result.get("position_warning_count", 0)),
            scale_ratio=float(result.get("scale_ratio", 0.0)),
            warnings=tuple(str(value) for value in result.get("warnings", [])),
        )

    async def retarget_animation(
        self,
        source_armature: str,
        target_armature: str,
        source_action: str,
        mapping: Mapping[str, object],
        output_action: str,
        frame_start: int | None = None,
        frame_end: int | None = None,
        scale_policy: str = "preserve",
        root_motion: str = "preserve",
    ) -> RetargetAnimationVO:
        source_armature = self._bounded_name(source_armature, "source_armature")
        target_armature = self._bounded_name(target_armature, "target_armature")
        source_action = self._bounded_name(source_action, "source_action")
        output_action = self._bounded_name(output_action, "output_action")
        scale_policy = str(scale_policy).lower()
        root_motion = str(root_motion).lower()
        if scale_policy not in {"preserve", "normalize"}:
            raise ValueError("scale_policy must be preserve or normalize")
        if root_motion not in {"preserve", "separate", "ignore"}:
            raise ValueError("root_motion must be preserve, separate, or ignore")
        mapping_payload = self._bounded_mapping_payload(mapping)
        start = None if frame_start is None else self._bounded_frame(frame_start)
        end = None if frame_end is None else self._bounded_frame(frame_end)
        if start is not None and end is not None and end < start:
            raise ValueError("frame_end must be greater than or equal to frame_start")
        code = """
import bpy
source = bpy.data.objects.get(__SOURCE_ARMATURE__)
target = bpy.data.objects.get(__TARGET_ARMATURE__)
action = bpy.data.actions.get(__SOURCE_ACTION__)
if source is None or source.type != "ARMATURE" or target is None or target.type != "ARMATURE":
    raise ValueError("Both source and target armatures are required")
if action is None:
    raise ValueError("Source Action not found: " + __SOURCE_ACTION__)
curves = []
if hasattr(action, "fcurves"):
    curves = list(action.fcurves)
else:
    for layer in action.layers:
        for strip in layer.strips:
            for channelbag in getattr(strip, "channelbags", []):
                curves.extend(list(channelbag.fcurves))
frames = sorted({int(point.co.x) for curve in curves for point in curve.keyframe_points})
if not frames:
    frames = [float(action.frame_range[0]), float(action.frame_range[1])]
start = __FRAME_START__ if __FRAME_START__ is not None else int(min(frames))
end = __FRAME_END__ if __FRAME_END__ is not None else int(max(frames))
frames = [frame for frame in frames if start <= frame <= end]
if not frames:
    raise ValueError("Source Action has no keyframes in requested range")
groups = {}
for curve in curves:
    path = str(curve.data_path)
    if not path.startswith('pose.bones["') or '"].' not in path:
        continue
    source_name, property_name = path[12:].split('"].', 1)
    groups.setdefault((source_name, property_name), []).append(curve)
output = bpy.data.actions.get(__OUTPUT_ACTION__)
if output is not None:
    bpy.data.actions.remove(output)
output = bpy.data.actions.new(__OUTPUT_ACTION__)
target.animation_data_create()
target.animation_data.action = output
mapping = {item["source_bone"]: item["target_bone"] for item in __MAPPING__}
root_bones = {"root", "root_master", "hips", "pelvis"}
keyframe_count = 0
for frame in frames:
    bpy.context.scene.frame_set(frame)
    for (source_name, property_name), property_curves in groups.items():
        target_name = mapping.get(source_name)
        if target_name is None or (__ROOT_MOTION__ == "ignore" and target_name.lower() in root_bones):
            continue
        bone = target.pose.bones.get(target_name)
        if bone is None:
            continue
        values = [curve.evaluate(frame) for curve in sorted(property_curves, key=lambda item: item.array_index)]
        target_property = property_name
        if target_property == "rotation_euler" and len(values) >= 3:
            bone.rotation_mode = "XYZ"
        destination = getattr(bone, target_property, None)
        if destination is None:
            continue
        if hasattr(destination, "__getitem__"):
            for index, value in enumerate(values):
                destination[index] = value
        elif values:
            setattr(bone, target_property, values[0])
        bone.keyframe_insert(data_path=target_property, frame=frame)
        keyframe_count += len(values)
result = {"source_armature": source.name, "target_armature": target.name, "source_action": action.name, "output_action": output.name, "frame_start": start, "frame_end": end, "mapped_bone_count": len(mapping), "keyframe_count": keyframe_count, "root_motion": __ROOT_MOTION__, "changed": True}
""".replace("__SOURCE_ARMATURE__", json.dumps(source_armature)).replace(
            "__TARGET_ARMATURE__", json.dumps(target_armature)
        ).replace("__SOURCE_ACTION__", json.dumps(source_action)).replace("__OUTPUT_ACTION__", json.dumps(output_action)).replace(
            "__MAPPING__", json.dumps(mapping_payload)
        ).replace("__FRAME_START__", "None" if start is None else str(start)).replace(
            "__FRAME_END__", "None" if end is None else str(end)
        ).replace("__ROOT_MOTION__", json.dumps(root_motion))
        result = await self._execute(code)
        return RetargetAnimationVO(
            source_armature=str(result.get("source_armature", source_armature)),
            target_armature=str(result.get("target_armature", target_armature)),
            source_action=str(result.get("source_action", source_action)),
            output_action=str(result.get("output_action", output_action)),
            frame_start=int(result.get("frame_start", start or 1)),
            frame_end=int(result.get("frame_end", end or 1)),
            mapped_bone_count=int(result.get("mapped_bone_count", len(mapping_payload))),
            keyframe_count=int(result.get("keyframe_count", 0)),
            root_motion=str(result.get("root_motion", root_motion)),
            changed=bool(result.get("changed", True)),
        )

    async def set_root_motion(self, armature_name: str, policy: str) -> RootMotionVO:
        armature_name = self._bounded_name(armature_name, "armature_name")
        policy = str(policy).lower()
        if policy not in {"preserve", "separate", "ignore"}:
            raise ValueError("policy must be preserve, separate, or ignore")
        code = """
import bpy
obj = bpy.data.objects.get(__ARMATURE_NAME__)
if obj is None or obj.type != "ARMATURE":
    raise ValueError("Armature object not found: " + __ARMATURE_NAME__)
previous = obj.get("arwaky_root_motion_policy")
obj["arwaky_root_motion_policy"] = __POLICY__
result = {"armature_name": obj.name, "policy": obj["arwaky_root_motion_policy"], "changed": previous != obj["arwaky_root_motion_policy"]}
""".replace("__ARMATURE_NAME__", json.dumps(armature_name)).replace("__POLICY__", json.dumps(policy))
        result = await self._execute(code)
        return RootMotionVO(
            armature_name=str(result.get("armature_name", armature_name)),
            policy=str(result.get("policy", policy)),
            changed=bool(result.get("changed", True)),
        )

    async def bake_retarget_action(
        self, armature_name: str, action_name: str, frame_start: int, frame_end: int, step: int = 1, clear_constraints: bool = False
    ) -> BakeRetargetVO:
        armature_name = self._bounded_name(armature_name, "armature_name")
        action_name = self._bounded_name(action_name, "action_name")
        frame_start = self._bounded_frame(frame_start)
        frame_end = self._bounded_frame(frame_end)
        step = int(step)
        if frame_end < frame_start or not 1 <= step <= 100:
            raise ValueError("invalid bake frame range or step")
        code = """
import bpy
obj = bpy.data.objects.get(__ARMATURE_NAME__)
action = bpy.data.actions.get(__ACTION_NAME__)
if obj is None or obj.type != "ARMATURE":
    raise ValueError("Armature object not found: " + __ARMATURE_NAME__)
if action is None:
    raise ValueError("Action not found: " + __ACTION_NAME__)
obj.animation_data_create()
obj.animation_data.action = action
for candidate in list(bpy.context.selected_objects):
    candidate.select_set(False)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj
if obj.mode != "POSE":
    bpy.ops.object.mode_set(mode="POSE")
bpy.ops.pose.select_all(action="SELECT")
bpy.ops.nla.bake(frame_start=__FRAME_START__, frame_end=__FRAME_END__, step=__STEP__, only_selected=True, visual_keying=True, clear_constraints=__CLEAR_CONSTRAINTS__, clear_parents=False, use_current_action=True, clean_curves=False, bake_types={"POSE"}, channel_types={"LOCATION", "ROTATION", "SCALE", "PROPS"})
curve_count = sum(1 for layer in action.layers for strip in layer.strips for channelbag in getattr(strip, "channelbags", []) for _ in channelbag.fcurves) if hasattr(action, "layers") else len(action.fcurves)
keyframe_count = sum(len(curve.keyframe_points) for layer in action.layers for strip in layer.strips for channelbag in getattr(strip, "channelbags", []) for curve in channelbag.fcurves) if hasattr(action, "layers") else sum(len(curve.keyframe_points) for curve in action.fcurves)
result = {"armature_name": obj.name, "action_name": action.name, "frame_start": __FRAME_START__, "frame_end": __FRAME_END__, "step": __STEP__, "keyframe_count": keyframe_count, "cleared_constraints": __CLEAR_CONSTRAINTS__, "changed": True}
""".replace("__ARMATURE_NAME__", json.dumps(armature_name)).replace("__ACTION_NAME__", json.dumps(action_name)).replace(
            "__FRAME_START__", str(frame_start)
        ).replace("__FRAME_END__", str(frame_end)).replace("__STEP__", str(step)).replace(
            "__CLEAR_CONSTRAINTS__", "True" if clear_constraints else "False"
        )
        result = await self._execute(code)
        return BakeRetargetVO(
            armature_name=str(result.get("armature_name", armature_name)),
            action_name=str(result.get("action_name", action_name)),
            frame_start=int(result.get("frame_start", frame_start)),
            frame_end=int(result.get("frame_end", frame_end)),
            step=int(result.get("step", step)),
            keyframe_count=int(result.get("keyframe_count", 0)),
            cleared_constraints=bool(result.get("cleared_constraints", clear_constraints)),
            changed=bool(result.get("changed", True)),
        )

    async def validate_animation_result(self, armature_name: str, action_name: str, limit: int = 1000) -> AnimationValidationVO:
        armature_name = self._bounded_name(armature_name, "armature_name")
        action_name = self._bounded_name(action_name, "action_name")
        limit = self._bounded_limit(limit)
        code = """
import bpy
obj = bpy.data.objects.get(__ARMATURE_NAME__)
action = bpy.data.actions.get(__ACTION_NAME__)
if obj is None or obj.type != "ARMATURE":
    raise ValueError("Armature object not found: " + __ARMATURE_NAME__)
if action is None:
    raise ValueError("Action not found: " + __ACTION_NAME__)
curves = []
if hasattr(action, "fcurves"):
    curves = list(action.fcurves)
else:
    for layer in action.layers:
        for strip in layer.strips:
            for channelbag in getattr(strip, "channelbags", []):
                curves.extend(list(channelbag.fcurves))
curves = curves[:__LIMIT__]
keyframe_count = sum(min(len(curve.keyframe_points), __LIMIT__) for curve in curves)
warnings = []
if not obj.animation_data or obj.animation_data.action != action:
    warnings.append("Action is not linked to the target armature")
if not curves:
    warnings.append("Action contains no curves")
result = {"armature_name": obj.name, "action_name": action.name, "frame_start": int(action.frame_range[0]), "frame_end": int(action.frame_range[1]), "curve_count": len(curves), "keyframe_count": keyframe_count, "approved": not warnings, "warnings": warnings}
""".replace("__ARMATURE_NAME__", json.dumps(armature_name)).replace("__ACTION_NAME__", json.dumps(action_name)).replace(
            "__LIMIT__", str(limit)
        )
        result = await self._execute(code)
        return AnimationValidationVO(
            armature_name=str(result.get("armature_name", armature_name)),
            action_name=str(result.get("action_name", action_name)),
            frame_start=int(result.get("frame_start", 1)),
            frame_end=int(result.get("frame_end", 1)),
            curve_count=int(result.get("curve_count", 0)),
            keyframe_count=int(result.get("keyframe_count", 0)),
            approved=bool(result.get("approved", False)),
            warnings=tuple(str(value) for value in result.get("warnings", [])),
        )

    @staticmethod
    def _bounded_mapping_payload(mapping: Mapping[str, object]) -> list[dict[str, object]]:
        if not isinstance(mapping, Mapping):
            raise ValueError("mapping must be an object")
        raw_items = mapping.get("mappings", [])
        if not isinstance(raw_items, list) or not raw_items or len(raw_items) > 5000:
            raise ValueError("mapping.mappings must contain 1-5000 items")
        payload = []
        for item in raw_items:
            if not isinstance(item, Mapping):
                raise ValueError("each mapping item must be an object")
            source_name = str(item.get("source_bone", "")).strip()
            target_name = str(item.get("target_bone", "")).strip()
            if not source_name or not target_name or len(source_name) > 256 or len(target_name) > 256:
                raise ValueError("mapping bone names must be 1-256 characters")
            payload.append({"source_bone": source_name, "target_bone": target_name})
        return payload

    @staticmethod
    def _mapping_from_result(
        result: Mapping[str, object], source_armature: str, target_armature: str, preset: str
    ) -> BoneMappingStateVO:
        mappings = tuple(
            BoneMappingVO(
                source_bone=str(item.get("source_bone", "")),
                target_bone=str(item.get("target_bone", "")),
                side=str(item["side"]) if item.get("side") else None,
                confidence=float(item.get("confidence", 1.0)),
            )
            for item in result.get("mappings", [])
            if isinstance(item, Mapping)
        )
        return BoneMappingStateVO(
            source_armature=str(result.get("source_armature", source_armature)),
            target_armature=str(result.get("target_armature", target_armature)),
            preset=str(result.get("preset", preset)),
            mappings=mappings,
            unmapped_source=tuple(str(value) for value in result.get("unmapped_source", [])),
            unmapped_target=tuple(str(value) for value in result.get("unmapped_target", [])),
        )


