# bpy.types.ParticleInstanceModifier

# ParticleInstanceModifier(Modifier)

 

base classes — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct), [`Modifier`](bpy.types.Modifier.html#bpy.types.Modifier)

   class bpy.types.ParticleInstanceModifier(Modifier) 

Particle system instancing modifier

   axis 

Pole axis for rotation (default `'Z'`)

  Type: 

Literal[[Axis Xyz Items](bpy_types_enum_items/axis_xyz_items.html#rna-enum-axis-xyz-items)]

      index_layer_name 

Custom data layer name for the index (default “”, never None)

  Type: 

str

      object 

Object that has the particle system

  Type: 

[`Object`](bpy.types.Object.html#bpy.types.Object) | None

      particle_amount 

Amount of particles to use for instancing (in [0, 1], default 1.0)

  Type: 

float

      particle_offset 

Relative offset of particles to use for instancing, to avoid overlap of multiple instances (in [0, 1], default 0.0)

  Type: 

float

      particle_system  Type: 

[`ParticleSystem`](bpy.types.ParticleSystem.html#bpy.types.ParticleSystem) | None

      particle_system_index 

(in [1, 32767], default 1)

  Type: 

int

      position 

Position along path (in [0, 1], default 1.0)

  Type: 

float

      random_position 

Randomize position along path (in [0, 1], default 0.0)

  Type: 

float

      random_rotation 

Randomize rotation around path (in [0, 1], default 0.0)

  Type: 

float

      rotation 

Rotation around path (in [0, 1], default 0.0)

  Type: 

float

      show_alive 

Show instances when particles are alive (default True)

  Type: 

bool

      show_dead 

Show instances when particles are dead (default True)

  Type: 

bool

      show_unborn 

Show instances when particles are unborn (default True)

  Type: 

bool

      space 

Space to use for copying mesh data (default `'WORLD'`)

  
- `LOCAL` Local – Use offset from the particle object in the instance object. 
- `WORLD` World – Use world space offset in the instance object.   Type: 

Literal[‘LOCAL’, ‘WORLD’]

      use_children 

Create instances from child particles (default False)

  Type: 

bool

      use_normal 

Create instances from normal particles (default True)

  Type: 

bool

      use_path 

Create instances along particle paths (default False)

  Type: 

bool

      use_preserve_shape 

Don’t stretch the object (default False)

  Type: 

bool

      use_size 

Use particle size to scale the instances (default False)

  Type: 

bool

      value_layer_name 

Custom data layer name for the randomized value (default “”, never None)

  Type: 

str

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
- [`Modifier.name`](bpy.types.Modifier.html#bpy.types.Modifier.name) 
- [`Modifier.type`](bpy.types.Modifier.html#bpy.types.Modifier.type) 
- [`Modifier.show_viewport`](bpy.types.Modifier.html#bpy.types.Modifier.show_viewport) 
- [`Modifier.show_render`](bpy.types.Modifier.html#bpy.types.Modifier.show_render) 
- [`Modifier.show_in_editmode`](bpy.types.Modifier.html#bpy.types.Modifier.show_in_editmode) 
- [`Modifier.show_on_cage`](bpy.types.Modifier.html#bpy.types.Modifier.show_on_cage)   
- [`Modifier.show_expanded`](bpy.types.Modifier.html#bpy.types.Modifier.show_expanded) 
- [`Modifier.is_active`](bpy.types.Modifier.html#bpy.types.Modifier.is_active) 
- [`Modifier.use_pin_to_last`](bpy.types.Modifier.html#bpy.types.Modifier.use_pin_to_last) 
- [`Modifier.is_override_data`](bpy.types.Modifier.html#bpy.types.Modifier.is_override_data) 
- [`Modifier.use_apply_on_spline`](bpy.types.Modifier.html#bpy.types.Modifier.use_apply_on_spline) 
- [`Modifier.execution_time`](bpy.types.Modifier.html#bpy.types.Modifier.execution_time) 
- [`Modifier.persistent_uid`](bpy.types.Modifier.html#bpy.types.Modifier.persistent_uid)     

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
- [`Modifier.bl_rna_get_subclass`](bpy.types.Modifier.html#bpy.types.Modifier.bl_rna_get_subclass) 
- [`Modifier.bl_rna_get_subclass_py`](bpy.types.Modifier.html#bpy.types.Modifier.bl_rna_get_subclass_py)
