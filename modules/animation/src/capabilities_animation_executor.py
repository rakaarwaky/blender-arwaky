"""Animation capability executor for bounded timeline and keyframe operations."""

from __future__ import annotations

import json
from collections.abc import Mapping

from modules.shared.src.animation.taxonomy_animation_vo import (
    AnimationActionLinkVO,
    AnimationActionVO,
    AnimationCurveVO,
    AnimationImportVO,
    AnimationKeyframeVO,
    AnimationMutationVO,
    AnimationPoseAssetStateVO,
    AnimationPoseAssetVO,
    AnimationPoseBufferVO,
    AnimationStateVO,
    RigifyControlStateVO,
    RigifyControlVO,
    RigifyPoseKeyframeVO,
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

    async def list_actions(self, armature_name: str | None = None, limit: int = 100) -> tuple[AnimationActionVO, ...]:
        limit = self._bounded_limit(limit)
        code = """
import bpy
armature = bpy.data.objects.get(__ARMATURE_NAME__) if __ARMATURE_NAME__ else None
if __ARMATURE_NAME__ and (armature is None or armature.type != "ARMATURE"):
    raise ValueError(f"Armature object not found: {__ARMATURE_NAME__}")
items = []
for action in list(bpy.data.actions)[:__LIMIT__]:
    if armature is not None and armature.animation_data and armature.animation_data.action != action:
        continue
    items.append({"name": action.name, "frame_start": float(action.frame_range[0]),
                  "frame_end": float(action.frame_range[1]), "curve_count": len(action.fcurves),
                  "slot_count": len(action.slots) if hasattr(action, "slots") else 0})
result = {"actions": items}
""".replace("__ARMATURE_NAME__", json.dumps(str(armature_name) if armature_name else ""))
        code = code.replace("__LIMIT__", str(limit))
        result = await self._execute(code)
        return tuple(
            AnimationActionVO(
                name=str(item.get("name", "")),
                frame_start=float(item.get("frame_start", 0.0)),
                frame_end=float(item.get("frame_end", 0.0)),
                curve_count=int(item.get("curve_count", 0)),
                slot_count=int(item.get("slot_count", 0)),
            )
            for item in result.get("actions", [])
            if isinstance(item, Mapping)
        )

    async def inspect_rigify_controls(self, armature_name: str, limit: int = 1000) -> RigifyControlStateVO:
        limit = self._bounded_limit(limit)
        code = """
import bpy
obj = bpy.data.objects.get(__ARMATURE_NAME__)
if obj is None or obj.type != "ARMATURE":
    raise ValueError(f"Rigify armature not found: {__ARMATURE_NAME__}")
controls = []
for bone in list(obj.data.bones)[:__LIMIT__]:
    name = bone.name
    lowered = name.lower()
    if name.startswith("DEF-"):
        role = "deform"
    elif "_ik" in lowered:
        role = "ik"
    elif "_pole" in lowered:
        role = "pole"
    elif name.startswith("MCH-"):
        role = "mechanism"
    elif name.startswith("ORG-"):
        role = "original"
    else:
        role = "control"
    side = "left" if name.endswith(".L") else "right" if name.endswith(".R") else None
    controls.append({"name": name, "role": role, "side": side, "is_deform": bool(bone.use_deform)})
result = {"armature_name": obj.name, "controls": controls, "control_count": len(controls)}
""".replace("__ARMATURE_NAME__", json.dumps(str(armature_name))).replace("__LIMIT__", str(limit))
        result = await self._execute(code)
        controls = tuple(
            RigifyControlVO(
                name=str(item.get("name", "")),
                role=str(item.get("role", "control")),
                side=str(item["side"]) if item.get("side") else None,
                is_deform=bool(item.get("is_deform", False)),
            )
            for item in result.get("controls", [])
            if isinstance(item, Mapping)
        )
        return RigifyControlStateVO(
            armature_name=str(result.get("armature_name", armature_name)),
            controls=controls,
            control_count=int(result.get("control_count", len(controls))),
        )

    async def import_animation_file(self, source_path: str, importer: str | None = None) -> AnimationImportVO:
        path = str(source_path).strip()
        if not path or len(path) > 4096:
            raise ValueError("source_path must be 1-4096 characters")
        suffix = path.rsplit(".", 1)[-1].lower() if "." in path else ""
        selected_importer = str(importer or suffix).lower()
        if selected_importer not in {"fbx", "bvh"}:
            raise ValueError("importer must be fbx or bvh")
        operator = "bpy.ops.import_scene.fbx" if selected_importer == "fbx" else "bpy.ops.import_anim.bvh"
        code = """
import bpy
before_objects = set(bpy.data.objects.keys())
before_actions = set(bpy.data.actions.keys())
__OPERATOR__(filepath=__SOURCE_PATH__)
after_objects = [name for name in bpy.data.objects.keys() if name not in before_objects]
after_actions = [name for name in bpy.data.actions.keys() if name not in before_actions]
result = {"source_path": __SOURCE_PATH__, "importer": __IMPORTER__,
          "imported_objects": after_objects, "action_names": after_actions, "warnings": []}
""".replace("__OPERATOR__", operator).replace("__SOURCE_PATH__", json.dumps(path)).replace(
            "__IMPORTER__", json.dumps(selected_importer)
        )
        result = await self._execute(code)
        return AnimationImportVO(
            source_path=str(result.get("source_path", path)),
            importer=str(result.get("importer", selected_importer)),
            imported_objects=tuple(str(item) for item in result.get("imported_objects", [])),
            action_names=tuple(str(item) for item in result.get("action_names", [])),
            warnings=tuple(str(item) for item in result.get("warnings", [])),
        )

    async def link_action_to_armature(self, armature_name: str, action_name: str) -> AnimationActionLinkVO:
        armature_name = str(armature_name).strip()
        action_name = str(action_name).strip()
        if not armature_name or not action_name:
            raise ValueError("armature_name and action_name are required")
        if len(armature_name) > 256 or len(action_name) > 256:
            raise ValueError("armature_name and action_name must not exceed 256 characters")
        code = """
import bpy
obj = bpy.data.objects.get(__ARMATURE_NAME__)
if obj is None or obj.type != "ARMATURE":
    raise ValueError(f"Armature object not found: {__ARMATURE_NAME__}")
action = bpy.data.actions.get(__ACTION_NAME__)
if action is None:
    raise ValueError(f"Action not found: {__ACTION_NAME__}")
obj.animation_data_create()
previous = obj.animation_data.action.name if obj.animation_data.action else None
changed = previous != action.name
obj.animation_data.action = action
result = {"armature_name": obj.name, "action_name": action.name,
          "previous_action_name": previous, "changed": changed}
""".replace("__ARMATURE_NAME__", json.dumps(armature_name)).replace("__ACTION_NAME__", json.dumps(action_name))
        result = await self._execute(code)
        return AnimationActionLinkVO(
            armature_name=str(result.get("armature_name", armature_name)),
            action_name=str(result.get("action_name", action_name)),
            previous_action_name=str(result["previous_action_name"])
            if result.get("previous_action_name")
            else None,
            changed=bool(result.get("changed", False)),
        )

    async def list_pose_assets(self, limit: int = 100) -> tuple[AnimationPoseAssetVO, ...]:
        limit = self._bounded_limit(limit)
        code = """
import bpy
items = []
for action in list(bpy.data.actions)[:__LIMIT__]:
    if action.asset_data is None:
        continue
    items.append({"name": action.name, "is_pose_asset": True,
                  "frame_start": float(action.frame_range[0]),
                  "frame_end": float(action.frame_range[1]),
                  "catalog_id": getattr(action.asset_data, "catalog_id", None)})
result = {"assets": items}
""".replace("__LIMIT__", str(limit))
        result = await self._execute(code)
        return tuple(
            AnimationPoseAssetVO(
                name=str(item.get("name", "")),
                is_pose_asset=bool(item.get("is_pose_asset", False)),
                frame_start=float(item.get("frame_start", 0.0)),
                frame_end=float(item.get("frame_end", 0.0)),
                catalog_id=str(item["catalog_id"]) if item.get("catalog_id") else None,
            )
            for item in result.get("assets", [])
            if isinstance(item, Mapping)
        )

    async def create_pose_asset(
        self, armature_name: str, pose_name: str, catalog_path: str | None = None
    ) -> AnimationPoseAssetVO:
        armature_name = self._bounded_name(armature_name, "armature_name")
        pose_name = self._bounded_name(pose_name, "pose_name")
        catalog_path = "" if catalog_path is None else str(catalog_path).strip()
        if len(catalog_path) > 1024:
            raise ValueError("catalog_path must not exceed 1024 characters")
        code = """
import bpy
obj = bpy.data.objects.get(__ARMATURE_NAME__)
if obj is None or obj.type != "ARMATURE":
    raise ValueError("Armature object not found: " + __ARMATURE_NAME__)
for candidate in list(bpy.context.selected_objects):
    candidate.select_set(False)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj
if obj.mode != "POSE":
    bpy.ops.object.mode_set(mode="POSE")
bpy.ops.poselib.create_pose_asset(pose_name=__POSE_NAME__, catalog_path=__CATALOG_PATH__)
action = bpy.data.actions.get(__POSE_NAME__)
if action is None:
    action = obj.animation_data.action if obj.animation_data else None
if action is None:
    raise RuntimeError("Pose asset creation did not produce an Action")
result = {"name": action.name, "is_pose_asset": action.asset_data is not None,
          "frame_start": float(action.frame_range[0]), "frame_end": float(action.frame_range[1]),
          "catalog_id": getattr(action.asset_data, "catalog_id", None)}
""".replace("__ARMATURE_NAME__", json.dumps(armature_name)).replace(
            "__POSE_NAME__", json.dumps(pose_name)
        ).replace("__CATALOG_PATH__", json.dumps(catalog_path))
        result = await self._execute(code)
        return AnimationPoseAssetVO(
            name=str(result.get("name", pose_name)),
            is_pose_asset=bool(result.get("is_pose_asset", False)),
            frame_start=float(result.get("frame_start", 0.0)),
            frame_end=float(result.get("frame_end", 0.0)),
            catalog_id=str(result["catalog_id"]) if result.get("catalog_id") else None,
        )

    async def apply_pose_asset(
        self, armature_name: str, asset_name: str, blend_factor: float = 1.0, flipped: bool = False
    ) -> AnimationPoseAssetStateVO:
        return await self._apply_pose_asset(armature_name, asset_name, blend_factor, flipped, False)

    async def blend_pose_asset(
        self, armature_name: str, asset_name: str, blend_factor: float, flipped: bool = False
    ) -> AnimationPoseAssetStateVO:
        return await self._apply_pose_asset(armature_name, asset_name, blend_factor, flipped, True)

    async def _apply_pose_asset(
        self, armature_name: str, asset_name: str, blend_factor: float, flipped: bool, blended: bool
    ) -> AnimationPoseAssetStateVO:
        armature_name = self._bounded_name(armature_name, "armature_name")
        asset_name = self._bounded_name(asset_name, "asset_name")
        factor = float(blend_factor)
        if not 0.0 <= factor <= 1.0:
            raise ValueError("blend_factor must be between 0.0 and 1.0")
        operator = "bpy.ops.poselib.blend_pose_asset" if blended else "bpy.ops.poselib.apply_pose_asset"
        code = """
import bpy
obj = bpy.data.objects.get(__ARMATURE_NAME__)
asset = bpy.data.actions.get(__ASSET_NAME__)
if obj is None or obj.type != "ARMATURE":
    raise ValueError("Armature object not found: " + __ARMATURE_NAME__)
if asset is None or asset.asset_data is None:
    raise ValueError("Pose asset not found: " + __ASSET_NAME__)
for candidate in list(bpy.context.selected_objects):
    candidate.select_set(False)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj
if obj.mode != "POSE":
    bpy.ops.object.mode_set(mode="POSE")
__OPERATOR__(asset_library_type="LOCAL", relative_asset_identifier=asset.name,
             blend_factor=__BLEND_FACTOR__, flipped=__FLIPPED__)
result = {"armature_name": obj.name, "asset_name": asset.name,
          "blend_factor": __BLEND_FACTOR__, "flipped": __FLIPPED__, "changed": True}
""".replace("__ARMATURE_NAME__", json.dumps(armature_name)).replace(
            "__ASSET_NAME__", json.dumps(asset_name)
        ).replace("__OPERATOR__", operator).replace("__BLEND_FACTOR__", str(factor)).replace(
            "__FLIPPED__", "True" if flipped else "False"
        )
        result = await self._execute(code)
        return AnimationPoseAssetStateVO(
            armature_name=str(result.get("armature_name", armature_name)),
            asset_name=str(result.get("asset_name", asset_name)),
            blend_factor=float(result.get("blend_factor", factor)),
            flipped=bool(result.get("flipped", flipped)),
            changed=bool(result.get("changed", True)),
        )

    async def copy_rigify_pose(self, armature_name: str) -> AnimationPoseBufferVO:
        return await self._pose_buffer_operation(armature_name, "bpy.ops.pose.copy", False, False)

    async def paste_rigify_pose(
        self, armature_name: str, flipped: bool = False, selected_mask: bool = False
    ) -> AnimationPoseBufferVO:
        return await self._pose_buffer_operation(armature_name, "bpy.ops.pose.paste", flipped, selected_mask)

    async def _pose_buffer_operation(
        self, armature_name: str, operator: str, flipped: bool, selected_mask: bool
    ) -> AnimationPoseBufferVO:
        armature_name = self._bounded_name(armature_name, "armature_name")
        call = f"{operator}()" if operator.endswith("pose.copy") else (
            f"{operator}(flipped={'True' if flipped else 'False'}, selected_mask={'True' if selected_mask else 'False'})"
        )
        code = """
import bpy
obj = bpy.data.objects.get(__ARMATURE_NAME__)
if obj is None or obj.type != "ARMATURE":
    raise ValueError("Armature object not found: " + __ARMATURE_NAME__)
for candidate in list(bpy.context.selected_objects):
    candidate.select_set(False)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj
if obj.mode != "POSE":
    bpy.ops.object.mode_set(mode="POSE")
__CALL__
result = {"armature_name": obj.name, "flipped": __FLIPPED__,
          "selected_mask": __SELECTED_MASK__, "changed": True}
""".replace("__ARMATURE_NAME__", json.dumps(armature_name)).replace(
            "__CALL__", call
        ).replace("__FLIPPED__", "True" if flipped else "False").replace(
            "__SELECTED_MASK__", "True" if selected_mask else "False"
        )
        result = await self._execute(code)
        return AnimationPoseBufferVO(
            armature_name=str(result.get("armature_name", armature_name)),
            flipped=bool(result.get("flipped", flipped)),
            selected_mask=bool(result.get("selected_mask", selected_mask)),
            changed=bool(result.get("changed", True)),
        )

    async def keyframe_rigify_pose(
        self, armature_name: str, frame: int, bone_names: list[str] | None = None
    ) -> RigifyPoseKeyframeVO:
        armature_name = self._bounded_name(armature_name, "armature_name")
        frame = self._bounded_frame(frame)
        names = tuple(self._bounded_name(name, "bone_name") for name in (bone_names or ()))
        names_code = json.dumps(list(names))
        code = """
import bpy
obj = bpy.data.objects.get(__ARMATURE_NAME__)
if obj is None or obj.type != "ARMATURE":
    raise ValueError("Armature object not found: " + __ARMATURE_NAME__)
bpy.context.scene.frame_set(__FRAME__)
selected = __BONE_NAMES__
if selected:
    missing = [name for name in selected if name not in obj.pose.bones]
    if missing:
        raise ValueError("Rigify pose bones not found: " + ", ".join(missing))
    targets = [obj.pose.bones[name] for name in selected]
else:
    targets = [bone for bone in obj.pose.bones if bone.bone.select]
    selected = [bone.name for bone in targets]
if not targets:
    raise ValueError("At least one Rigify pose bone must be selected or named")
for bone in targets:
    bone.keyframe_insert(data_path="location", frame=__FRAME__)
    bone.keyframe_insert(data_path="scale", frame=__FRAME__)
    rotation_path = "rotation_quaternion" if bone.rotation_mode == "QUATERNION" else "rotation_axis_angle" if bone.rotation_mode == "AXIS_ANGLE" else "rotation_euler"
    bone.keyframe_insert(data_path=rotation_path, frame=__FRAME__)
result = {"armature_name": obj.name, "frame": __FRAME__, "bone_names": selected, "changed": True}
""".replace("__ARMATURE_NAME__", json.dumps(armature_name)).replace(
            "__FRAME__", str(frame)
        ).replace("__BONE_NAMES__", names_code)
        result = await self._execute(code)
        return RigifyPoseKeyframeVO(
            armature_name=str(result.get("armature_name", armature_name)),
            frame=int(result.get("frame", frame)),
            bone_names=tuple(str(name) for name in result.get("bone_names", names)),
            changed=bool(result.get("changed", True)),
        )

    @staticmethod
    def _bounded_name(value: str, label: str) -> str:
        name = str(value).strip()
        if not name or len(name) > 256:
            raise ValueError(f"{label} must be 1-256 characters")
        return name

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
