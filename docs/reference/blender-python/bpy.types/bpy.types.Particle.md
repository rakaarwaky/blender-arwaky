# bpy.types.Particle

# Particle(bpy_struct)

 

base class — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct)

   class bpy.types.Particle(bpy_struct) 

Particle in a particle system

   alive_state 

(default `'DEAD'`)

  Type: 

Literal[‘DEAD’, ‘UNBORN’, ‘ALIVE’, ‘DYING’]

      angular_velocity 

(array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

  Type: 

[`mathutils.Vector`](mathutils.html#mathutils.Vector)

      birth_time 

(in [-inf, inf], default 0.0)

  Type: 

float

      die_time 

(in [-inf, inf], default 0.0)

  Type: 

float

      hair_keys 

(default None, readonly)

  Type: 

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.html#bpy.types.bpy_prop_collection)[[`ParticleHairKey`](bpy.types.ParticleHairKey.html#bpy.types.ParticleHairKey)]

      is_exist 

(default True, readonly)

  Type: 

bool

      is_visible 

(default True, readonly)

  Type: 

bool

      lifetime 

(in [-inf, inf], default 0.0)

  Type: 

float

      location 

(array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

  Type: 

[`mathutils.Vector`](mathutils.html#mathutils.Vector)

      particle_keys 

(default None, readonly)

  Type: 

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.html#bpy.types.bpy_prop_collection)[[`ParticleKey`](bpy.types.ParticleKey.html#bpy.types.ParticleKey)]

      prev_angular_velocity 

(array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

  Type: 

[`mathutils.Vector`](mathutils.html#mathutils.Vector)

      prev_location 

(array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

  Type: 

[`mathutils.Vector`](mathutils.html#mathutils.Vector)

      prev_rotation 

(array of 4 items, in [-inf, inf], default (0.0, 0.0, 0.0, 0.0))

  Type: 

[`mathutils.Quaternion`](mathutils.html#mathutils.Quaternion)

      prev_velocity 

(array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

  Type: 

[`mathutils.Vector`](mathutils.html#mathutils.Vector)

      rotation 

(array of 4 items, in [-inf, inf], default (0.0, 0.0, 0.0, 0.0))

  Type: 

[`mathutils.Quaternion`](mathutils.html#mathutils.Quaternion)

      size 

(in [-inf, inf], default 0.0)

  Type: 

float

      velocity 

(array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

  Type: 

[`mathutils.Vector`](mathutils.html#mathutils.Vector)

      uv_on_emitter(modifier) 

Obtain UV coordinates for a particle on an evaluated mesh.

  Parameters: 

modifier ([`ParticleSystemModifier`](bpy.types.ParticleSystemModifier.html#bpy.types.ParticleSystemModifier) | None) – Particle modifier from an evaluated object (never None)

  Returns: 

uv, (array of 2 items, in [-inf, inf])

  Return type: 

[`mathutils.Vector`](mathutils.html#mathutils.Vector)

      classmethod bl_rna_get_subclass(id, default=None, /)  Parameters:  
- id (str) – The RNA type identifier. 
- default ([`bpy.types.Struct`](bpy.types.Struct.html#bpy.types.Struct) | None) – The value to return when not found.   Returns: 

The RNA type or default when not found.

  Return type: 

[`bpy.types.Struct`](bpy.types.Struct.html#bpy.types.Struct)

      classmethod bl_rna_get_subclass_py(id, default=None, /)  Parameters:  
- id (str) – The RNA type identifier. 
- default (type | None) – The value to return when not found.   Returns: 

The class or default when not found.

  Return type: 

type

      

## Inherited Properties

  
- [`bpy_struct.id_data`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.id_data)       

## Inherited Functions

  
- [`bpy_struct.as_pointer`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.as_pointer) 
- [`bpy_struct.driver_add`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.driver_add) 
- [`bpy_struct.driver_remove`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.driver_remove) 
- [`bpy_struct.get`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.get) 
- [`bpy_struct.id_properties_clear`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.id_properties_clear) 
- [`bpy_struct.id_properties_ensure`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.id_properties_ensure) 
- [`bpy_struct.id_properties_ui`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.id_properties_ui) 
- [`bpy_struct.is_property_hidden`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.is_property_hidden) 
- [`bpy_struct.is_property_overridable_library`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.is_property_overridable_library) 
- [`bpy_struct.is_property_readonly`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.is_property_readonly) 
- [`bpy_struct.is_property_set`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.is_property_set) 
- [`bpy_struct.items`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.items)   
- [`bpy_struct.keyframe_delete`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.keyframe_delete) 
- [`bpy_struct.keyframe_insert`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.keyframe_insert) 
- [`bpy_struct.keys`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.keys) 
- [`bpy_struct.path_from_id`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.path_from_id) 
- [`bpy_struct.path_from_module`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.path_from_module) 
- [`bpy_struct.path_resolve`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.path_resolve) 
- [`bpy_struct.pop`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.pop) 
- [`bpy_struct.property_overridable_library_set`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.property_overridable_library_set) 
- [`bpy_struct.property_unset`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.property_unset) 
- [`bpy_struct.rna_ancestors`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.rna_ancestors) 
- [`bpy_struct.type_recast`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.type_recast) 
- [`bpy_struct.values`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.values)     

## References

  
- [`ParticleHairKey.co_object`](bpy.types.ParticleHairKey.html#bpy.types.ParticleHairKey.co_object) 
- [`ParticleHairKey.co_object_set`](bpy.types.ParticleHairKey.html#bpy.types.ParticleHairKey.co_object_set) 
- [`ParticleSystem.mcol_on_emitter`](bpy.types.ParticleSystem.html#bpy.types.ParticleSystem.mcol_on_emitter)   
- [`ParticleSystem.particles`](bpy.types.ParticleSystem.html#bpy.types.ParticleSystem.particles) 
- [`ParticleSystem.uv_on_emitter`](bpy.types.ParticleSystem.html#bpy.types.ParticleSystem.uv_on_emitter)
