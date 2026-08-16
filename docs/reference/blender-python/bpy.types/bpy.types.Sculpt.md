# bpy.types.Sculpt

# Sculpt(Paint)

 

base classes — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct), [`Paint`](bpy.types.Paint.html#bpy.types.Paint)

   class bpy.types.Sculpt(Paint)   constant_detail_resolution 

Maximum edge length for dynamic topology sculpting (as divisor of Blender unit - higher value means smaller edge length) (in [0.0001, inf], default 3.0)

  Type: 

float

      detail_percent 

Maximum edge length for dynamic topology sculpting (in brush percentage) (in [0.5, 100], default 25.0)

  Type: 

float

      detail_refine_method 

In dynamic-topology mode, how to add or remove mesh detail (default `'SUBDIVIDE_COLLAPSE'`)

  
- `SUBDIVIDE` Subdivide Edges – Subdivide long edges to add mesh detail where needed. 
- `COLLAPSE` Collapse Edges – Collapse short edges to remove mesh detail where possible. 
- `SUBDIVIDE_COLLAPSE` Subdivide Collapse – Both subdivide long edges and collapse short edges to refine mesh detail.   Type: 

Literal[‘SUBDIVIDE’, ‘COLLAPSE’, ‘SUBDIVIDE_COLLAPSE’]

      detail_size 

Maximum edge length for dynamic topology sculpting (in pixels) (in [0.5, 40], default 12.0)

  Type: 

float

      detail_type_method 

In dynamic-topology mode, how mesh detail size is calculated (default `'RELATIVE'`)

  
- `RELATIVE` Relative Detail – Mesh detail is relative to the brush size and detail size. 
- `CONSTANT` Constant Detail – Mesh detail is constant in world space according to detail size. 
- `BRUSH` Brush Detail – Mesh detail is relative to brush size. 
- `MANUAL` Manual Detail – Mesh detail does not change on each stroke, only when using Flood Fill.   Type: 

Literal[‘RELATIVE’, ‘CONSTANT’, ‘BRUSH’, ‘MANUAL’]

      gravity 

Amount of gravity after each dab (in [0, 1], default 0.0)

  Type: 

float

      gravity_object 

Object whose Z axis defines orientation of gravity

  Type: 

[`Object`](bpy.types.Object.html#bpy.types.Object) | None

      lock_x 

Disallow changes to the X axis of vertices (default False)

  Type: 

bool

      lock_y 

Disallow changes to the Y axis of vertices (default False)

  Type: 

bool

      lock_z 

Disallow changes to the Z axis of vertices (default False)

  Type: 

bool

      symmetrize_direction 

Source and destination for symmetrize operator (default `'NEGATIVE_X'`)

  Type: 

Literal[[Symmetrize Direction Items](bpy_types_enum_items/symmetrize_direction_items.html#rna-enum-symmetrize-direction-items)]

      transform_mode 

How the transformation is going to be applied to the target (default `'ALL_VERTICES'`)

  
- `ALL_VERTICES` All Vertices – Applies the transformation to all vertices in the mesh. 
- `RADIUS_ELASTIC` Elastic – Applies the transformation simulating elasticity using the radius of the cursor.   Type: 

Literal[‘ALL_VERTICES’, ‘RADIUS_ELASTIC’]

      use_deform_only 

Use only deformation modifiers (temporary disable all constructive modifiers except multi-resolution) (default False)

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
- [`Paint.brush`](bpy.types.Paint.html#bpy.types.Paint.brush) 
- [`Paint.brush_asset_reference`](bpy.types.Paint.html#bpy.types.Paint.brush_asset_reference) 
- [`Paint.palette`](bpy.types.Paint.html#bpy.types.Paint.palette) 
- [`Paint.show_brush`](bpy.types.Paint.html#bpy.types.Paint.show_brush) 
- [`Paint.show_brush_on_surface`](bpy.types.Paint.html#bpy.types.Paint.show_brush_on_surface) 
- [`Paint.show_low_resolution`](bpy.types.Paint.html#bpy.types.Paint.show_low_resolution) 
- [`Paint.use_sculpt_delay_updates`](bpy.types.Paint.html#bpy.types.Paint.use_sculpt_delay_updates) 
- [`Paint.show_bvh_nodes`](bpy.types.Paint.html#bpy.types.Paint.show_bvh_nodes) 
- [`Paint.use_symmetry_x`](bpy.types.Paint.html#bpy.types.Paint.use_symmetry_x) 
- [`Paint.use_symmetry_y`](bpy.types.Paint.html#bpy.types.Paint.use_symmetry_y) 
- [`Paint.use_symmetry_z`](bpy.types.Paint.html#bpy.types.Paint.use_symmetry_z)   
- [`Paint.use_symmetry_feather`](bpy.types.Paint.html#bpy.types.Paint.use_symmetry_feather) 
- [`Paint.cavity_curve`](bpy.types.Paint.html#bpy.types.Paint.cavity_curve) 
- [`Paint.use_cavity`](bpy.types.Paint.html#bpy.types.Paint.use_cavity) 
- [`Paint.tile_offset`](bpy.types.Paint.html#bpy.types.Paint.tile_offset) 
- [`Paint.tile_x`](bpy.types.Paint.html#bpy.types.Paint.tile_x) 
- [`Paint.tile_y`](bpy.types.Paint.html#bpy.types.Paint.tile_y) 
- [`Paint.tile_z`](bpy.types.Paint.html#bpy.types.Paint.tile_z) 
- [`Paint.show_strength_curve`](bpy.types.Paint.html#bpy.types.Paint.show_strength_curve) 
- [`Paint.show_size_curve`](bpy.types.Paint.html#bpy.types.Paint.show_size_curve) 
- [`Paint.show_jitter_curve`](bpy.types.Paint.html#bpy.types.Paint.show_jitter_curve) 
- [`Paint.unified_paint_settings`](bpy.types.Paint.html#bpy.types.Paint.unified_paint_settings) 
- [`Paint.mesh_automasking_settings`](bpy.types.Paint.html#bpy.types.Paint.mesh_automasking_settings)     

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
- [`Paint.bl_rna_get_subclass`](bpy.types.Paint.html#bpy.types.Paint.bl_rna_get_subclass) 
- [`Paint.bl_rna_get_subclass_py`](bpy.types.Paint.html#bpy.types.Paint.bl_rna_get_subclass_py)     

## References

  
- [`ToolSettings.sculpt`](bpy.types.ToolSettings.html#bpy.types.ToolSettings.sculpt)
