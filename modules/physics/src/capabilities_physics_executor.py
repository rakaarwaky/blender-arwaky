"""Physics capability executor for bounded rigid body and cloth operations."""

from __future__ import annotations

import json
import math
from collections.abc import Mapping

from modules.shared.src.physics.taxonomy_physics_vo import (
    PhysicsMutationVO,
    PhysicsStateVO,
    SimulationCacheStatusVO,
    SimulationMutationVO,
    SimulationStateVO,
)

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

    async def get_simulation_state(self, object_name: str) -> SimulationStateVO:
        code = """
import bpy
obj = bpy.data.objects.get(__OBJECT_NAME__)
if obj is None:
    raise ValueError(f"Object not found: {__OBJECT_NAME__}")
particles = []
for particle_system in list(obj.particle_systems)[:16]:
    settings = particle_system.settings
    particles.append({"name": particle_system.name, "count": settings.count,
                      "frame_start": settings.frame_start, "frame_end": settings.frame_end,
                      "lifetime": settings.lifetime, "physics_type": settings.physics_type})
effector = obj if obj.field is not None else next((item for item in bpy.data.objects if item.get("arwaky_force_target") == obj.name), None)
field = effector.field if effector is not None else None
fluid_modifier = next((item for item in obj.modifiers if item.type == "FLUID"), None)
domain = fluid_modifier.domain_settings if fluid_modifier else None
result = {"object_name": obj.name,
          "particle_systems": particles,
          "force_field_enabled": field is not None and field.type != "NONE",
          "force_field_type": field.type if field is not None and field.type != "NONE" else None,
          "force_field_strength": field.strength if field is not None and field.type != "NONE" else None,

          "fluid_domain_enabled": domain is not None,
          "fluid_domain_type": domain.domain_type if domain else None,
          "fluid_resolution": domain.resolution_max if domain else None,
          "fluid_cache_type": domain.cache_type if domain else None}
""".replace("__OBJECT_NAME__", json.dumps(str(object_name)))
        result = await self._execute(code)
        particles = tuple(dict(item) for item in result.get("particle_systems", []) if isinstance(item, Mapping))
        return SimulationStateVO(
            object_name=str(result.get("object_name", object_name)),
            particle_system_count=len(particles),
            particle_systems=particles,
            force_field_enabled=bool(result.get("force_field_enabled", False)),
            force_field_type=str(result["force_field_type"]) if result.get("force_field_type") else None,
            force_field_strength=float(result["force_field_strength"])
            if result.get("force_field_strength") is not None
            else None,
            fluid_domain_enabled=bool(result.get("fluid_domain_enabled", False)),
            fluid_domain_type=str(result["fluid_domain_type"]) if result.get("fluid_domain_type") else None,
            fluid_resolution=int(result["fluid_resolution"]) if result.get("fluid_resolution") is not None else None,
            fluid_cache_type=str(result["fluid_cache_type"]) if result.get("fluid_cache_type") else None,
        )

    async def get_simulation_cache_status(self) -> SimulationCacheStatusVO:
        code = """
import bpy
scene = bpy.context.scene
caches = []
for obj in list(bpy.data.objects)[:1000]:
    for modifier in list(obj.modifiers)[:32]:
        if modifier.type not in {"CLOTH", "FLUID"}:
            continue
        point_cache = getattr(modifier, "point_cache", None)
        domain = getattr(modifier, "domain_settings", None)
        caches.append({"object_name": obj.name, "modifier_name": modifier.name,
                       "modifier_type": modifier.type,
                       "is_baked": bool(getattr(point_cache, "is_baked", False)) if point_cache else False,
                       "cache_frame_start": getattr(domain, "cache_frame_start", None) if domain else getattr(point_cache, "frame_start", None),
                       "cache_frame_end": getattr(domain, "cache_frame_end", None) if domain else getattr(point_cache, "frame_end", None)})
result = {"frame_start": scene.frame_start, "frame_end": scene.frame_end,
          "current_frame": scene.frame_current, "cache_states": caches[:100]}
"""
        result = await self._execute(code)
        return SimulationCacheStatusVO(
            frame_start=int(result.get("frame_start", 1)),
            frame_end=int(result.get("frame_end", 250)),
            current_frame=int(result.get("current_frame", 1)),
            cache_states=tuple(dict(item) for item in result.get("cache_states", []) if isinstance(item, Mapping)),
        )

    async def configure_particle_system(
        self,
        object_name: str,
        enabled: bool,
        count: int = 1000,
        frame_start: int = 1,
        frame_end: int = 200,
        lifetime: float = 50.0,
        physics_type: str = "NEWTON",
    ) -> SimulationMutationVO:
        count = self._bounded_count(count)
        frame_start = self._bounded_frame(frame_start)
        frame_end = self._bounded_frame(frame_end)
        if frame_end <= frame_start:
            raise ValueError("frame_end must be greater than frame_start")
        lifetime = self._bounded_lifetime(lifetime)
        physics_type = str(physics_type).upper()
        if physics_type not in {"NEWTON", "KEYED", "BOIDS", "FLUID"}:
            raise ValueError(f"Unsupported particle physics type: {physics_type}")
        code = """
import bpy
obj = bpy.data.objects.get(__OBJECT_NAME__)
if obj is None:
    raise ValueError(f"Object not found: {__OBJECT_NAME__}")
if obj.type != "MESH":
    raise ValueError("Particle systems require a mesh object")
changed = False
if __ENABLED__:
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    if len(obj.particle_systems) == 0:
        bpy.ops.object.particle_system_add()
        changed = True
    particle_system = obj.particle_systems[-1]
    settings = particle_system.settings
    if (settings.count, settings.frame_start, settings.frame_end, settings.lifetime, settings.physics_type) != (__COUNT__, __FRAME_START__, __FRAME_END__, __LIFETIME__, __PHYSICS_TYPE__):
        changed = True
    settings.count = __COUNT__
    settings.frame_start = __FRAME_START__
    settings.frame_end = __FRAME_END__
    settings.lifetime = __LIFETIME__
    settings.physics_type = __PHYSICS_TYPE__
    result = {"object_name": obj.name, "changed": changed, "operation": "configure_particle_system",
              "particle_system_name": particle_system.name, "message": "Particle system configured"}
else:
    if len(obj.particle_systems) > 0:
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.particle_system_remove()
        changed = True
    result = {"object_name": obj.name, "changed": changed, "operation": "configure_particle_system",
              "particle_system_name": None, "message": "Particle system disabled"}
"""
        for token, value in {
            "__OBJECT_NAME__": object_name,
            "__ENABLED__": enabled,
            "__COUNT__": count,
            "__FRAME_START__": frame_start,
            "__FRAME_END__": frame_end,
            "__LIFETIME__": lifetime,
            "__PHYSICS_TYPE__": physics_type,
        }.items():
            code = code.replace(token, json.dumps(value))
        result = await self._execute(code)
        return SimulationMutationVO(
            object_name=str(result.get("object_name")) if result.get("object_name") else None,
            changed=bool(result.get("changed", False)),
            operation=str(result.get("operation", "configure_particle_system")),
            particle_system_name=str(result["particle_system_name"]) if result.get("particle_system_name") else None,
            message=str(result.get("message", "")),
        )

    async def configure_force_field(
        self,
        object_name: str,
        enabled: bool,
        field_type: str = "FORCE",
        strength: float = 1.0,
        noise: float = 0.0,
    ) -> SimulationMutationVO:
        field_type = str(field_type).upper()
        if field_type not in {"FORCE", "WIND", "VORTEX", "MAGNET", "TURBULENCE"}:
            raise ValueError(f"Unsupported force field type: {field_type}")
        strength = self._bounded_strength(strength)
        noise = self._bounded_noise(noise)
        code = """
import bpy
obj = bpy.data.objects.get(__OBJECT_NAME__)
if obj is None:
    raise ValueError(f"Object not found: {__OBJECT_NAME__}")
effector = obj if obj.field is not None else next((item for item in bpy.data.objects if item.get("arwaky_force_target") == obj.name), None)
if __ENABLED__:
    changed = False
    if effector is None or effector.field is None:
        bpy.ops.object.effector_add(type=__FIELD_TYPE__, location=obj.location)
        effector = bpy.context.object
        effector.name = f"{obj.name}_ForceField"
        effector["arwaky_force_target"] = obj.name
        changed = True
    field = effector.field
    previous = (field.type, field.strength, field.noise)
    field.type = __FIELD_TYPE__
    field.strength = __STRENGTH__
    field.noise = __NOISE__
    changed = changed or previous != (field.type, field.strength, field.noise)
    result = {"object_name": obj.name, "changed": changed, "operation": "configure_force_field",
              "force_field_type": field.type, "message": "Force field configured"}
else:
    changed = False
    if effector is not None and effector is not obj and effector.get("arwaky_force_target") == obj.name:
        bpy.data.objects.remove(effector, do_unlink=True)
        changed = True
    elif effector is not None and effector.field is not None and effector.field.type != "NONE":
        effector.field.type = "NONE"
        changed = True
    result = {"object_name": obj.name, "changed": changed, "operation": "configure_force_field",
              "force_field_type": None, "message": "Force field disabled"}
"""
        for token, value in {
            "__OBJECT_NAME__": object_name,
            "__ENABLED__": enabled,
            "__FIELD_TYPE__": field_type,
            "__STRENGTH__": strength,
            "__NOISE__": noise,
        }.items():
            code = code.replace(token, json.dumps(value))
        result = await self._execute(code)
        return SimulationMutationVO(
            object_name=str(result.get("object_name")) if result.get("object_name") else None,
            changed=bool(result.get("changed", False)),
            operation=str(result.get("operation", "configure_force_field")),
            force_field_type=str(result["force_field_type"]) if result.get("force_field_type") else None,
            message=str(result.get("message", "")),
        )

    async def configure_fluid_domain(
        self,
        object_name: str,
        enabled: bool,
        domain_type: str = "LIQUID",
        resolution: int = 64,
        cache_type: str = "REPLAY",
    ) -> SimulationMutationVO:
        domain_type = str(domain_type).upper()
        if domain_type not in {"LIQUID", "GAS"}:
            raise ValueError(f"Unsupported fluid domain type: {domain_type}")
        resolution = int(resolution)
        if not 4 <= resolution <= 512:
            raise ValueError("resolution must be between 4 and 512")
        cache_type = str(cache_type).upper()
        if cache_type not in {"REPLAY", "MODULAR", "FINAL"}:
            raise ValueError(f"Unsupported fluid cache type: {cache_type}")
        code = """
import bpy
obj = bpy.data.objects.get(__OBJECT_NAME__)
if obj is None:
    raise ValueError(f"Object not found: {__OBJECT_NAME__}")
if obj.type != "MESH":
    raise ValueError("Fluid domains require a mesh object")
modifier = next((item for item in obj.modifiers if item.type == "FLUID"), None)
changed = False
if __ENABLED__:
    if modifier is None:
        modifier = obj.modifiers.new(name="Fluid", type="FLUID")
        changed = True
    modifier.fluid_type = "DOMAIN"
    bpy.context.view_layer.update()
    domain = modifier.domain_settings
    if domain is None:
        raise RuntimeError("Blender did not initialize fluid domain settings")
    if domain.domain_type != __DOMAIN_TYPE__ or domain.resolution_max != __RESOLUTION__ or domain.cache_type != __CACHE_TYPE__:
        changed = True
    domain.domain_type = __DOMAIN_TYPE__
    domain.resolution_max = __RESOLUTION__
    domain.cache_type = __CACHE_TYPE__
    result = {"object_name": obj.name, "changed": changed, "operation": "configure_fluid_domain",
              "fluid_domain_type": domain.domain_type, "message": "Fluid domain configured"}
else:
    if modifier is not None:
        obj.modifiers.remove(modifier)
        changed = True
    result = {"object_name": obj.name, "changed": changed, "operation": "configure_fluid_domain",
              "fluid_domain_type": None, "message": "Fluid domain disabled"}
"""
        for token, value in {
            "__OBJECT_NAME__": object_name,
            "__ENABLED__": enabled,
            "__DOMAIN_TYPE__": domain_type,
            "__RESOLUTION__": resolution,
            "__CACHE_TYPE__": cache_type,
        }.items():
            code = code.replace(token, json.dumps(value))
        result = await self._execute(code)
        return SimulationMutationVO(
            object_name=str(result.get("object_name")) if result.get("object_name") else None,
            changed=bool(result.get("changed", False)),
            operation=str(result.get("operation", "configure_fluid_domain")),
            fluid_domain_type=str(result["fluid_domain_type"]) if result.get("fluid_domain_type") else None,
            message=str(result.get("message", "")),
        )

    @staticmethod
    def _bounded_count(value: int) -> int:
        count = int(value)
        if not 1 <= count <= 1_000_000:
            raise ValueError("count must be between 1 and 1000000")
        return count

    @staticmethod
    def _bounded_lifetime(value: float) -> float:
        lifetime = float(value)
        if not math.isfinite(lifetime) or not 0.1 <= lifetime <= 100000.0:
            raise ValueError("lifetime must be between 0.1 and 100000")
        return lifetime

    @staticmethod
    def _bounded_strength(value: float) -> float:
        strength = float(value)
        if not math.isfinite(strength) or not -1.0e6 <= strength <= 1.0e6:
            raise ValueError("strength must be between -1000000 and 1000000")
        return strength

    @staticmethod
    def _bounded_noise(value: float) -> float:
        noise = float(value)
        if not math.isfinite(noise) or not 0.0 <= noise <= 1.0e6:
            raise ValueError("noise must be between 0 and 1000000")
        return noise

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
