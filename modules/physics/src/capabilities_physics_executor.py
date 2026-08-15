"""Physics capability executor for bounded rigid body and cloth operations."""

from __future__ import annotations

import json
from collections.abc import Mapping

from modules.shared.src.physics.taxonomy_physics_vo import PhysicsMutationVO, PhysicsStateVO

_ALLOWED_BODY_TYPES = {"ACTIVE", "PASSIVE"}


class PhysicsExecutor:
    """Delegate physics operations to the injected Blender gateway."""

    def __init__(self, code_executor: object) -> None:
        self._code_executor = code_executor

    async def get_state(self, object_name: str) -> PhysicsStateVO:
        code = """
import bpy
obj = bpy.data.objects.get(__OBJECT_NAME__)
if obj is None:
    raise ValueError(f"Object not found: {obj.name}")
rigid = obj.rigid_body
cloth = next((item for item in obj.modifiers if item.type == "CLOTH"), None)
settings = cloth.settings if cloth else None
result = {"object_name": obj.name,
          "rigid_body_enabled": rigid is not None,
          "rigid_body_type": rigid.type if rigid else None,
          "rigid_body_mass": rigid.mass if rigid else None,
          "rigid_body_kinematic": rigid.kinematic if rigid else None,
          "cloth_enabled": cloth is not None,
          "cloth_quality": settings.quality if settings else None,
          "cloth_pin_group": settings.vertex_group_mass if settings else None}
""".replace("__OBJECT_NAME__", json.dumps(str(object_name)))
        result = await self._execute(code)
        return PhysicsStateVO(
            object_name=str(result["object_name"]),
            rigid_body_enabled=bool(result.get("rigid_body_enabled", False)),
            rigid_body_type=str(result["rigid_body_type"]) if result.get("rigid_body_type") else None,
            rigid_body_mass=float(result["rigid_body_mass"]) if result.get("rigid_body_mass") is not None else None,
            rigid_body_kinematic=bool(result["rigid_body_kinematic"])
            if result.get("rigid_body_kinematic") is not None
            else None,
            cloth_enabled=bool(result.get("cloth_enabled", False)),
            cloth_quality=int(result["cloth_quality"]) if result.get("cloth_quality") is not None else None,
            cloth_pin_group=str(result["cloth_pin_group"]) if result.get("cloth_pin_group") else None,
        )

    async def configure_rigid_body(
        self,
        object_name: str,
        enabled: bool,
        body_type: str = "ACTIVE",
        mass: float = 1.0,
        kinematic: bool = False,
    ) -> PhysicsMutationVO:
        body_type = str(body_type).upper()
        if body_type not in _ALLOWED_BODY_TYPES:
            raise ValueError(f"Unsupported rigid body type: {body_type}")
        mass = float(mass)
        if not 0.001 <= mass <= 1.0e6:
            raise ValueError("mass must be between 0.001 and 1000000")
        code = """
import bpy
obj = bpy.data.objects.get(__OBJECT_NAME__)
if obj is None:
    raise ValueError(f"Object not found: {obj.name}")
changed = False
if __ENABLED__:
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    if obj.rigid_body is None:
        bpy.ops.rigidbody.object_add()
        changed = True
    rigid = obj.rigid_body
    if rigid.type != __BODY_TYPE__ or rigid.mass != __MASS__ or rigid.kinematic != __KINEMATIC__:
        changed = True
    rigid.type = __BODY_TYPE__
    rigid.mass = __MASS__
    rigid.kinematic = __KINEMATIC__
else:
    if obj.rigid_body is not None:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.rigidbody.object_remove()
        changed = True
result = {"object_name": obj.name, "changed": changed, "operation": "configure_rigid_body",
          "body_type": __BODY_TYPE__ if __ENABLED__ else None,
          "mass": __MASS__ if __ENABLED__ else None,
          "message": "Rigid body configuration updated"}
"""
        for token, value in {
            "__OBJECT_NAME__": object_name,
            "__ENABLED__": enabled,
            "__BODY_TYPE__": body_type,
            "__MASS__": mass,
            "__KINEMATIC__": kinematic,
        }.items():
            code = code.replace(token, json.dumps(value))
        result = await self._execute(code)
        return PhysicsMutationVO(
            object_name=str(result.get("object_name")) if result.get("object_name") else None,
            changed=bool(result.get("changed", False)),
            operation=str(result.get("operation", "configure_rigid_body")),
            body_type=str(result["body_type"]) if result.get("body_type") else None,
            mass=float(result["mass"]) if result.get("mass") is not None else None,
            message=str(result.get("message", "")),
        )

    async def configure_cloth(
        self,
        object_name: str,
        enabled: bool,
        quality: int = 5,
        pin_group: str | None = None,
    ) -> PhysicsMutationVO:
        quality = int(quality)
        if not 1 <= quality <= 80:
            raise ValueError("quality must be between 1 and 80")
        if pin_group is not None and len(str(pin_group)) > 64:
            raise ValueError("pin_group must not exceed 64 characters")
        code = """
import bpy
obj = bpy.data.objects.get(__OBJECT_NAME__)
if obj is None:
    raise ValueError(f"Object not found: {obj.name}")
cloth = next((item for item in obj.modifiers if item.type == "CLOTH"), None)
changed = False
if __ENABLED__:
    if cloth is None:
        cloth = obj.modifiers.new(name="Cloth", type="CLOTH")
        changed = True
    cloth.settings.quality = __QUALITY__
    if __PIN_GROUP__ is not None:
        cloth.settings.vertex_group_mass = __PIN_GROUP__
    result = {"object_name": obj.name, "changed": changed, "operation": "configure_cloth_simulation",
              "quality": cloth.settings.quality, "message": "Cloth configuration updated"}
else:
    if cloth is not None:
        obj.modifiers.remove(cloth)
        changed = True
    result = {"object_name": obj.name, "changed": changed, "operation": "configure_cloth_simulation",
              "quality": None, "message": "Cloth modifier disabled"}
"""
        for token, value in {
            "__OBJECT_NAME__": object_name,
            "__ENABLED__": enabled,
            "__QUALITY__": quality,
            "__PIN_GROUP__": pin_group,
        }.items():
            code = code.replace(token, json.dumps(value))
        result = await self._execute(code)
        return PhysicsMutationVO(
            object_name=str(result.get("object_name")) if result.get("object_name") else None,
            changed=bool(result.get("changed", False)),
            operation=str(result.get("operation", "configure_cloth_simulation")),
            quality=int(result["quality"]) if result.get("quality") is not None else None,
            message=str(result.get("message", "")),
        )

    async def bake(self, frame_start: int | None = None, frame_end: int | None = None) -> PhysicsMutationVO:
        start = None if frame_start is None else self._bounded_frame(frame_start)
        end = None if frame_end is None else self._bounded_frame(frame_end)
        if start is not None and end is not None and end < start:
            raise ValueError("frame_end must be greater than or equal to frame_start")
        code = """
import bpy
scene = bpy.context.scene
previous = (scene.frame_start, scene.frame_end)
try:
    if __FRAME_START__ is not None:
        scene.frame_start = __FRAME_START__
    if __FRAME_END__ is not None:
        scene.frame_end = __FRAME_END__
    bpy.ops.ptcache.bake_all(bake=True)
    result = {"object_name": None, "changed": True, "operation": "bake_physics_simulation",
              "frame_start": scene.frame_start, "frame_end": scene.frame_end,
              "message": "Physics bake completed"}
finally:
    scene.frame_start, scene.frame_end = previous
"""
        code = code.replace("__FRAME_START__", json.dumps(start)).replace("__FRAME_END__", json.dumps(end))
        result = await self._execute(code)
        return PhysicsMutationVO(
            object_name=None,
            changed=bool(result.get("changed", True)),
            operation=str(result.get("operation", "bake_physics_simulation")),
            frame_start=int(result["frame_start"]) if result.get("frame_start") is not None else None,
            frame_end=int(result["frame_end"]) if result.get("frame_end") is not None else None,
            message=str(result.get("message", "")),
        )

    async def clear_bake(self) -> PhysicsMutationVO:
        code = """
import bpy
bpy.ops.ptcache.free_bake_all()
result = {"object_name": None, "changed": True, "operation": "clear_physics_bake",
          "message": "Physics bake cleared"}
"""
        result = await self._execute(code)
        return PhysicsMutationVO(
            object_name=None,
            changed=bool(result.get("changed", True)),
            operation=str(result.get("operation", "clear_physics_bake")),
            message=str(result.get("message", "")),
        )

    async def _execute(self, code: str) -> Mapping[str, object]:
        result = await self._code_executor.execute_blender_code(code)
        if not isinstance(result, Mapping):
            raise RuntimeError("Gateway returned a non-object physics result")
        return result

    @staticmethod
    def _bounded_frame(value: int) -> int:
        frame = int(value)
        if not -100000 <= frame <= 100000:
            raise ValueError("frame must be between -100000 and 100000")
        return frame
