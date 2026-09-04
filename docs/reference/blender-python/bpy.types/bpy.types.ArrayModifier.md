# bpy.types.ArrayModifier

# ArrayModifier(Modifier)

 

base classes — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct), [`Modifier`](bpy.types.Modifier.html#bpy.types.Modifier)

   class bpy.types.ArrayModifier(Modifier) 

Array duplication modifier

   constant_offset_displace 

Value for the distance between arrayed items (array of 3 items, in [-inf, inf], default (1.0, 0.0, 0.0))

  Type: 

[`mathutils.Vector`](mathutils.html#mathutils.Vector)

      count 

Number of duplicates to make (in [1, inf], default 2)

  Type: 

int

      curve 

Curve object to fit array length to

  Type: 

[`Object`](bpy.types.Object.html#bpy.types.Object) | None

      end_cap 

Mesh object to use as an end cap

  Type: 

[`Object`](bpy.types.Object.html#bpy.types.Object) | None

      fit_length 

Length to fit array within (in [0, inf], default 0.0)

  Type: 

float

      fit_type 

Array length calculation method (default `'FIXED_COUNT'`)

  
- `FIXED_COUNT` Fixed Count – Duplicate the object a certain number of times. 
- `FIT_LENGTH` Fit Length – Duplicate the object as many times as fits in a certain length. 
- `FIT_CURVE` Fit Curve – Fit the duplicated objects to a curve.   Type: 

Literal[‘FIXED_COUNT’, ‘FIT_LENGTH’, ‘FIT_CURVE’]

      merge_threshold 

Limit below which to merge vertices (in [0, inf], default 0.01)

  Type: 

float

      offset_object 

Use the location and rotation of another object to determine the distance and rotational change between arrayed items

  Type: 

[`Object`](bpy.types.Object.html#bpy.types.Object) | None

      offset_u 

Amount to offset array UVs on the U axis (in [-1, 1], default 0.0)

  Type: 

float

      offset_v 

Amount to offset array UVs on the V axis (in [-1, 1], default 0.0)

  Type: 

float

      relative_offset_displace 

The size of the geometry will determine the distance between arrayed items (array of 3 items, in [-inf, inf], default (1.0, 0.0, 0.0))

  Type: 

[`mathutils.Vector`](mathutils.html#mathutils.Vector)

      start_cap 

Mesh object to use as a start cap

  Type: 

[`Object`](bpy.types.Object.html#bpy.types.Object) | None

      use_constant_offset 

Add a constant offset (default False)

  Type: 

bool

      use_merge_vertices 

Merge vertices in adjacent duplicates (default False)

  Type: 

bool

      use_merge_vertices_cap 

Merge vertices in first and last duplicates (default False)

  Type: 

bool

      use_object_offset 

Add another object’s transformation to the total offset (default False)

  Type: 

bool

      use_relative_offset 

Add an offset relative to the object’s bounding box (default True)

  Type: 

bool

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
