# bpy.types.WaveModifier

# WaveModifier(Modifier)

 

base classes — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct), [`Modifier`](bpy.types.Modifier.html#bpy.types.Modifier)

   class bpy.types.WaveModifier(Modifier) 

Wave effect modifier

   damping_time 

Number of frames in which the wave damps out after it dies (in [-1.04857e+06, 1.04857e+06], default 10.0)

  Type: 

float

      falloff_radius 

Distance after which it fades out (in [0, inf], default 0.0)

  Type: 

float

      height 

Height of the wave (in [-inf, inf], default 0.5)

  Type: 

float

      invert_vertex_group 

Invert vertex group influence (default False)

  Type: 

bool

      lifetime 

Lifetime of the wave in frames, zero means infinite (in [-1.04857e+06, 1.04857e+06], default 0.0)

  Type: 

float

      narrowness 

Distance between the top and the base of a wave, the higher the value, the more narrow the wave (in [0, inf], default 1.5)

  Type: 

float

      speed 

Speed of the wave, towards the starting point when negative (in [-inf, inf], default 0.25)

  Type: 

float

      start_position_object 

Object which defines the wave center

  Type: 

[`Object`](bpy.types.Object.html#bpy.types.Object) | None

      start_position_x 

X coordinate of the start position (in [-inf, inf], default 0.0)

  Type: 

float

      start_position_y 

Y coordinate of the start position (in [-inf, inf], default 0.0)

  Type: 

float

      texture  Type: 

[`Texture`](bpy.types.Texture.html#bpy.types.Texture) | None

      texture_coords 

(default `'LOCAL'`)

  
- `LOCAL` Local – Use the local coordinate system for the texture coordinates. 
- `GLOBAL` Global – Use the global coordinate system for the texture coordinates. 
- `OBJECT` Object – Use the linked object’s local coordinate system for the texture coordinates. 
- `UV` UV – Use UV coordinates for the texture coordinates.   Type: 

Literal[‘LOCAL’, ‘GLOBAL’, ‘OBJECT’, ‘UV’]

      texture_coords_bone 

Bone to set the texture coordinates (default “”, never None)

  Type: 

str

      texture_coords_object 

Object to set the texture coordinates

  Type: 

[`Object`](bpy.types.Object.html#bpy.types.Object) | None

      time_offset 

Either the starting frame (for positive speed) or ending frame (for negative speed) (in [-1.04857e+06, 1.04857e+06], default 0.0)

  Type: 

float

      use_cyclic 

Cyclic wave effect (default True)

  Type: 

bool

      use_normal 

Displace along normals (default False)

  Type: 

bool

      use_normal_x 

Enable displacement along the X normal (default True)

  Type: 

bool

      use_normal_y 

Enable displacement along the Y normal (default True)

  Type: 

bool

      use_normal_z 

Enable displacement along the Z normal (default True)

  Type: 

bool

      use_x 

X axis motion (default True)

  Type: 

bool

      use_y 

Y axis motion (default True)

  Type: 

bool

      uv_layer 

UV map name (default “”, never None)

  Type: 

str

      vertex_group 

Vertex group name for modulating the wave (default “”, never None)

  Type: 

str

      width 

Distance between the waves (in [0, inf], default 1.5)

  Type: 

float

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
