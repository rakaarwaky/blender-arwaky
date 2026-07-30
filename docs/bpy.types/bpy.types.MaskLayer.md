# bpy.types.MaskLayer

# MaskLayer(bpy_struct)

 

base class — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct)

   class bpy.types.MaskLayer(bpy_struct) 

Single layer used for masking pixels

   alpha 

Render Opacity (in [-inf, inf], default 0.0)

  Type: 

float

      blend 

Method of blending mask layers (default `'ADD'`)

  Type: 

Literal[‘MERGE_ADD’, ‘MERGE_SUBTRACT’, ‘ADD’, ‘SUBTRACT’, ‘LIGHTEN’, ‘DARKEN’, ‘MUL’, ‘REPLACE’, ‘DIFFERENCE’]

      falloff 

Falloff type of the feather (default `'SMOOTH'`)

  Type: 

Literal[[Proportional Falloff Curve Only Items](bpy_types_enum_items/proportional_falloff_curve_only_items.html#rna-enum-proportional-falloff-curve-only-items)]

      fill_solver 

Triangulation solver for filling 2D curves (default `'CDT'`)

  
- `SWEEP_LINE` Sweep Line – Fast without support for self-intersection. 
- `CDT` Delaunay – Constrained Delaunay Triangulation (CDT), robust with support for self-intersections.   Type: 

Literal[‘SWEEP_LINE’, ‘CDT’]

      hide 

Restrict visibility in the viewport (default False)

  Type: 

bool

      hide_render 

Restrict renderability (default False)

  Type: 

bool

      hide_select 

Restrict selection in the viewport (default False)

  Type: 

bool

      invert 

Invert the mask black/white (default False)

  Type: 

bool

      name 

Unique name of layer (default “”, never None)

  Type: 

str

      select 

Layer is selected for editing in the Dope Sheet (default False)

  Type: 

bool

      splines 

Collection of splines which defines this layer (default None, readonly)

  Type: 

[`MaskSplines`](bpy.types.MaskSplines.html#bpy.types.MaskSplines)[[`MaskSpline`](bpy.types.MaskSpline.html#bpy.types.MaskSpline)]

      use_fill_holes 

Calculate holes when filling overlapping curves (default True)

  Type: 

bool

      use_fill_overlap 

Calculate self intersections and overlap before filling (only for the sweep-line solver) (default False)

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

  
- [`Mask.layers`](bpy.types.Mask.html#bpy.types.Mask.layers) 
- [`MaskLayers.active`](bpy.types.MaskLayers.html#bpy.types.MaskLayers.active)   
- [`MaskLayers.new`](bpy.types.MaskLayers.html#bpy.types.MaskLayers.new) 
- [`MaskLayers.remove`](bpy.types.MaskLayers.html#bpy.types.MaskLayers.remove)
