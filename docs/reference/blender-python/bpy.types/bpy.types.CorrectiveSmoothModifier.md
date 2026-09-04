# bpy.types.CorrectiveSmoothModifier

# CorrectiveSmoothModifier(Modifier)

 

base classes — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct), [`Modifier`](bpy.types.Modifier.html#bpy.types.Modifier)

   class bpy.types.CorrectiveSmoothModifier(Modifier) 

Correct distortion caused by deformation

   factor 

Smooth effect factor (in [-inf, inf], default 0.5)

  Type: 

float

      invert_vertex_group 

Invert vertex group influence (default False)

  Type: 

bool

      is_bind 

(default False, readonly)

  Type: 

bool

      iterations 

(in [0, 32767], default 5)

  Type: 

int

      rest_source 

Select the source of rest positions (default `'ORCO'`)

  
- `ORCO` Original Coords – Use base mesh vertex coordinates as the rest position. 
- `BIND` Bind Coords – Use bind vertex coordinates for rest position.   Type: 

Literal[‘ORCO’, ‘BIND’]

      scale 

Compensate for scale applied by other modifiers (in [-inf, inf], default 1.0)

  Type: 

float

      smooth_type 

Method used for smoothing (default `'SIMPLE'`)

  
- `SIMPLE` Simple – Use the average of adjacent edge-vertices. 
- `LENGTH_WEIGHTED` Length Weight – Use the average of adjacent edge-vertices weighted by their length.   Type: 

Literal[‘SIMPLE’, ‘LENGTH_WEIGHTED’]

      use_only_smooth 

Apply smoothing without reconstructing the surface (default False)

  Type: 

bool

      use_pin_boundary 

Excludes boundary vertices from being smoothed (default False)

  Type: 

bool

      vertex_group 

Name of Vertex Group which determines influence of modifier per point (default “”, never None)

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
