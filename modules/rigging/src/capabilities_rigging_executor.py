"""Rigging and deformation capability executor with explicit Blender bounds."""

from __future__ import annotations

import json
import math
from collections.abc import Mapping

from modules.shared.src.rigging.taxonomy_rigging_vo import (
    ArmatureStateVO,
    DeformationStateVO,
    RiggingMutationVO,
)

_ALLOWED_CONSTRAINT_TYPES = {"COPY_LOCATION", "COPY_ROTATION", "LIMIT_LOCATION", "LIMIT_ROTATION"}


class RiggingExecutor:
    """Delegate rigging operations to the injected Blender gateway."""

    def __init__(self, code_executor: object) -> None:
        self._code_executor = code_executor

    async def inspect_armature(self, object_name: str, limit: int = 100) -> ArmatureStateVO:
        limit = self._bounded_limit(limit)
        code = """
import bpy
obj = bpy.data.objects.get(__OBJECT_NAME__)
if obj is None:
    raise ValueError(f"Armature object not found: {__OBJECT_NAME__}")
if obj.type != "ARMATURE":
    raise ValueError("inspect_armature requires an armature object")
bones = []
for bone in list(obj.data.bones)[:__LIMIT__]:
    pose_bone = obj.pose.bones.get(bone.name)
    bones.append({"name": bone.name, "parent": bone.parent.name if bone.parent else None,
                  "children": [child.name for child in list(bone.children)[:64]],
                  "use_deform": bone.use_deform,
                  "head": list(bone.head_local), "tail": list(bone.tail_local),
                  "pose_location": list(pose_bone.location) if pose_bone else [0.0, 0.0, 0.0],
                  "pose_rotation": list(pose_bone.rotation_euler) if pose_bone else [0.0, 0.0, 0.0],
                  "pose_scale": list(pose_bone.scale) if pose_bone else [1.0, 1.0, 1.0]})
result = {"object_name": obj.name, "bone_count": len(obj.data.bones), "bones": bones}
""".replace("__OBJECT_NAME__", json.dumps(str(object_name))).replace("__LIMIT__", str(limit))
        result = await self._execute(code)
        bones = tuple(dict(item) for item in result.get("bones", []) if isinstance(item, Mapping))
        return ArmatureStateVO(
            object_name=str(result.get("object_name", object_name)),
            bone_count=int(result.get("bone_count", len(bones))),
            bones=bones,
        )

    async def set_pose_bone_transform(
        self,
        armature_name: str,
        bone_name: str,
        location: list[float] | None = None,
        rotation_euler: list[float] | None = None,
        scale: list[float] | None = None,
    ) -> RiggingMutationVO:
        location = self._bounded_vector(location, "location", -100000.0, 100000.0)
        rotation_euler = self._bounded_vector(rotation_euler, "rotation_euler", -math.tau * 1000.0, math.tau * 1000.0)
        scale = self._bounded_vector(scale, "scale", -1000.0, 1000.0)
        if location is None and rotation_euler is None and scale is None:
            raise ValueError("at least one pose transform vector is required")
        code = """
import bpy
obj = bpy.data.objects.get(__ARMATURE_NAME__)
if obj is None:
    raise ValueError(f"Armature object not found: {__ARMATURE_NAME__}")
if obj.type != "ARMATURE":
    raise ValueError("set_pose_bone_transform requires an armature object")
pose_bone = obj.pose.bones.get(__BONE_NAME__)
if pose_bone is None:
    raise ValueError(f"Pose bone not found: {__BONE_NAME__}")
changed = False
if __LOCATION__ is not None:
    changed = changed or list(pose_bone.location) != __LOCATION__
    pose_bone.location = __LOCATION__
if __ROTATION__ is not None:
    pose_bone.rotation_mode = "XYZ"
    changed = changed or list(pose_bone.rotation_euler) != __ROTATION__
    pose_bone.rotation_euler = __ROTATION__
if __SCALE__ is not None:
    changed = changed or list(pose_bone.scale) != __SCALE__
    pose_bone.scale = __SCALE__
result = {"object_name": obj.name, "changed": changed, "operation": "set_pose_bone_transform",
          "bone_name": pose_bone.name, "message": "Pose bone transform updated"}
"""
        for token, value in {
            "__ARMATURE_NAME__": armature_name,
            "__BONE_NAME__": bone_name,
            "__LOCATION__": location,
            "__ROTATION__": rotation_euler,
            "__SCALE__": scale,
        }.items():
            code = code.replace(token, json.dumps(value))
        result = await self._execute(code)
        return RiggingMutationVO(
            object_name=str(result.get("object_name")) if result.get("object_name") else None,
            changed=bool(result.get("changed", False)),
            operation=str(result.get("operation", "set_pose_bone_transform")),
            bone_name=str(result.get("bone_name")) if result.get("bone_name") else None,
            message=str(result.get("message", "")),
        )

    async def configure_bone_constraint(
        self,
        armature_name: str,
        bone_name: str,
        constraint_type: str,
        enabled: bool,
        constraint_name: str | None = None,
        target_object: str | None = None,
        subtarget: str | None = None,
    ) -> RiggingMutationVO:
        constraint_type = str(constraint_type).upper()
        if constraint_type not in _ALLOWED_CONSTRAINT_TYPES:
            raise ValueError(f"Unsupported bone constraint type: {constraint_type}")
        name = str(constraint_name or f"Arwaky_{constraint_type}").strip()
        if not name or len(name) > 128:
            raise ValueError("constraint_name must be 1-128 characters")
        if subtarget is not None and len(str(subtarget)) > 128:
            raise ValueError("subtarget must not exceed 128 characters")
        code = """
import bpy
obj = bpy.data.objects.get(__ARMATURE_NAME__)
if obj is None:
    raise ValueError(f"Armature object not found: {__ARMATURE_NAME__}")
if obj.type != "ARMATURE":
    raise ValueError("configure_bone_constraint requires an armature object")
pose_bone = obj.pose.bones.get(__BONE_NAME__)
if pose_bone is None:
    raise ValueError(f"Pose bone not found: {__BONE_NAME__}")
constraint = pose_bone.constraints.get(__CONSTRAINT_NAME__)
if __ENABLED__:
    if constraint is not None and constraint.type != __CONSTRAINT_TYPE__:
        pose_bone.constraints.remove(constraint)
        constraint = None
    if constraint is None:
        constraint = pose_bone.constraints.new(type=__CONSTRAINT_TYPE__)
        constraint.name = __CONSTRAINT_NAME__
    target = bpy.data.objects.get(__TARGET_OBJECT__) if __TARGET_OBJECT__ else None
    if __TARGET_OBJECT__ and target is None:
        raise ValueError(f"Constraint target object not found: {__TARGET_OBJECT__}")
    if target is not None:
        constraint.target = target
    if __SUBTARGET__ is not None and hasattr(constraint, "subtarget"):
        constraint.subtarget = __SUBTARGET__
    result = {"object_name": obj.name, "changed": True, "operation": "configure_bone_constraint",
              "bone_name": pose_bone.name, "constraint_name": constraint.name,
              "message": "Bone constraint configured"}
else:
    if constraint is not None:
        pose_bone.constraints.remove(constraint)
        changed = True
    else:
        changed = False
    result = {"object_name": obj.name, "changed": changed, "operation": "configure_bone_constraint",
              "bone_name": pose_bone.name, "constraint_name": __CONSTRAINT_NAME__,
              "message": "Bone constraint disabled"}
"""
        for token, value in {
            "__ARMATURE_NAME__": armature_name,
            "__BONE_NAME__": bone_name,
            "__CONSTRAINT_TYPE__": constraint_type,
            "__ENABLED__": enabled,
            "__CONSTRAINT_NAME__": name,
            "__TARGET_OBJECT__": target_object,
            "__SUBTARGET__": subtarget,
        }.items():
            code = code.replace(token, json.dumps(value))
        result = await self._execute(code)
        return RiggingMutationVO(
            object_name=str(result.get("object_name")) if result.get("object_name") else None,
            changed=bool(result.get("changed", False)),
            operation=str(result.get("operation", "configure_bone_constraint")),
            bone_name=str(result.get("bone_name")) if result.get("bone_name") else None,
            constraint_name=str(result.get("constraint_name")) if result.get("constraint_name") else None,
            message=str(result.get("message", "")),
        )

    async def configure_shape_key(
        self,
        object_name: str,
        shape_key_name: str,
        enabled: bool,
        value: float = 0.0,
        slider_min: float = 0.0,
        slider_max: float = 1.0,
    ) -> RiggingMutationVO:
        name = str(shape_key_name).strip()
        if not name or len(name) > 128:
            raise ValueError("shape_key_name must be 1-128 characters")
        value = self._bounded_scalar(value, "value", -10.0, 10.0)
        slider_min = self._bounded_scalar(slider_min, "slider_min", -10.0, 10.0)
        slider_max = self._bounded_scalar(slider_max, "slider_max", -10.0, 10.0)
        if slider_min > slider_max:
            raise ValueError("slider_min must be less than or equal to slider_max")
        if not slider_min <= value <= slider_max:
            raise ValueError("value must be within slider limits")
        code = """
import bpy
obj = bpy.data.objects.get(__OBJECT_NAME__)
if obj is None:
    raise ValueError(f"Object not found: {__OBJECT_NAME__}")
if obj.type != "MESH":
    raise ValueError("configure_shape_key requires a mesh object")
key = obj.data.shape_keys.key_blocks.get(__SHAPE_KEY_NAME__) if obj.data.shape_keys else None
if __ENABLED__:
    if key is None:
        key = obj.shape_key_add(name=__SHAPE_KEY_NAME__)
    key.value = __VALUE__
    key.slider_min = __SLIDER_MIN__
    key.slider_max = __SLIDER_MAX__
    result = {"object_name": obj.name, "changed": True, "operation": "configure_shape_key",
              "shape_key_name": key.name, "message": "Shape key configured"}
else:
    if key is None:
        raise ValueError(f"Shape key not found: {__SHAPE_KEY_NAME__}")
    if key.name == "Basis":
        raise ValueError("Basis shape key cannot be removed")
    obj.shape_key_remove(key)
    result = {"object_name": obj.name, "changed": True, "operation": "configure_shape_key",
              "shape_key_name": __SHAPE_KEY_NAME__, "message": "Shape key removed"}
"""
        for token, value_to_replace in {
            "__OBJECT_NAME__": object_name,
            "__SHAPE_KEY_NAME__": name,
            "__ENABLED__": enabled,
            "__VALUE__": value,
            "__SLIDER_MIN__": slider_min,
            "__SLIDER_MAX__": slider_max,
        }.items():
            code = code.replace(token, json.dumps(value_to_replace))
        result = await self._execute(code)
        return RiggingMutationVO(
            object_name=str(result.get("object_name")) if result.get("object_name") else None,
            changed=bool(result.get("changed", False)),
            operation=str(result.get("operation", "configure_shape_key")),
            shape_key_name=str(result.get("shape_key_name")) if result.get("shape_key_name") else None,
            message=str(result.get("message", "")),
        )

    async def get_deformation_state(self, object_name: str) -> DeformationStateVO:
        code = """
import bpy
obj = bpy.data.objects.get(__OBJECT_NAME__)
if obj is None:
    raise ValueError(f"Object not found: {__OBJECT_NAME__}")
if obj.type != "MESH":
    raise ValueError("get_deformation_state requires a mesh object")
armature_modifiers = []
constraints = []
for modifier in list(obj.modifiers)[:64]:
    if modifier.type == "ARMATURE":
        armature_modifiers.append({"name": modifier.name, "object_name": modifier.object.name if modifier.object else None})
        armature = modifier.object
        if armature and armature.type == "ARMATURE":
            for pose_bone in list(armature.pose.bones)[:1000]:
                for constraint in list(pose_bone.constraints)[:32]:
                    constraints.append({"bone_name": pose_bone.name, "name": constraint.name, "type": constraint.type,
                                        "target_object": constraint.target.name if constraint.target else None,
                                        "subtarget": getattr(constraint, "subtarget", "")})
for constraint in list(obj.constraints)[:64]:
    constraints.append({"bone_name": None, "name": constraint.name, "type": constraint.type,
                        "target_object": constraint.target.name if constraint.target else None,
                        "subtarget": getattr(constraint, "subtarget", "")})
shape_keys = []
if obj.data.shape_keys:
    for key in list(obj.data.shape_keys.key_blocks)[:128]:
        shape_keys.append({"name": key.name, "value": key.value, "slider_min": key.slider_min, "slider_max": key.slider_max})
result = {"object_name": obj.name, "armature_modifiers": armature_modifiers,
          "constraints": constraints[:128], "shape_keys": shape_keys}
""".replace("__OBJECT_NAME__", json.dumps(str(object_name)))
        result = await self._execute(code)
        return DeformationStateVO(
            object_name=str(result.get("object_name", object_name)),
            armature_modifiers=tuple(
                dict(item) for item in result.get("armature_modifiers", []) if isinstance(item, Mapping)
            ),
            constraints=tuple(dict(item) for item in result.get("constraints", []) if isinstance(item, Mapping)),
            shape_keys=tuple(dict(item) for item in result.get("shape_keys", []) if isinstance(item, Mapping)),
        )

    async def _execute(self, code: str) -> Mapping[str, object]:
        result = await self._code_executor.execute_blender_code(code)
        if not isinstance(result, Mapping):
            raise RuntimeError("Gateway returned a non-object rigging result")
        return result

    @staticmethod
    def _bounded_limit(value: int) -> int:
        limit = int(value)
        if not 1 <= limit <= 1000:
            raise ValueError("limit must be between 1 and 1000")
        return limit

    @staticmethod
    def _bounded_scalar(value: float, name: str, lower: float, upper: float) -> float:
        scalar = float(value)
        if not math.isfinite(scalar) or not lower <= scalar <= upper:
            raise ValueError(f"{name} must be between {lower} and {upper}")
        return scalar

    @classmethod
    def _bounded_vector(cls, value: list[float] | None, name: str, lower: float, upper: float) -> list[float] | None:
        if value is None:
            return None
        if len(value) != 3:
            raise ValueError(f"{name} must contain exactly 3 numbers")
        return [cls._bounded_scalar(item, name, lower, upper) for item in value]
