# bpy.types.Paint

# Paint(bpy_struct)

 

base class — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct)

  

Subclasses

  
- [CurvesSculpt(Paint)](bpy.types.CurvesSculpt.html) 
- [GpPaint(Paint)](bpy.types.GpPaint.html) 
- [GpSculptPaint(Paint)](bpy.types.GpSculptPaint.html) 
- [GpVertexPaint(Paint)](bpy.types.GpVertexPaint.html) 
- [GpWeightPaint(Paint)](bpy.types.GpWeightPaint.html) 
- [ImagePaint(Paint)](bpy.types.ImagePaint.html) 
- [Sculpt(Paint)](bpy.types.Sculpt.html) 
- [VertexPaint(Paint)](bpy.types.VertexPaint.html)     class bpy.types.Paint(bpy_struct)   brush 

Active brush (readonly)

  Type: 

[`Brush`](bpy.types.Brush.html#bpy.types.Brush) | None

      brush_asset_reference 

A weak reference to the matching brush asset, used e.g. to restore the last used brush on file load (readonly)

  Type: 

[`AssetWeakReference`](bpy.types.AssetWeakReference.html#bpy.types.AssetWeakReference) | None

      cavity_curve 

Editable cavity curve (readonly, never None)

  Type: 

[`CurveMapping`](bpy.types.CurveMapping.html#bpy.types.CurveMapping)

      mesh_automasking_settings 

(readonly, never None)

  Type: 

[`MeshAutomaskingSettings`](bpy.types.MeshAutomaskingSettings.html#bpy.types.MeshAutomaskingSettings)

      palette 

Active Palette

  Type: 

[`Palette`](bpy.types.Palette.html#bpy.types.Palette) | None

      show_brush 

(default True)

  Type: 

bool

      show_brush_on_surface 

(default False)

  Type: 

bool

      show_bvh_nodes 

Show the underlying BVH nodes as differently colored faces (default False)

  Type: 

bool

      show_jitter_curve 

(default False)

  Type: 

bool

      show_low_resolution 

For multires, show low resolution while navigating the view (default False)

  Type: 

bool

      show_size_curve 

(default False)

  Type: 

bool

      show_strength_curve 

(default False)

  Type: 

bool

      tile_offset 

Stride at which tiled strokes are copied (array of 3 items, in [0.01, inf], default (1.0, 1.0, 1.0))

  Type: 

[`mathutils.Vector`](mathutils.html#mathutils.Vector)

      tile_x 

Tile along X axis (default False)

  Type: 

bool

      tile_y 

Tile along Y axis (default False)

  Type: 

bool

      tile_z 

Tile along Z axis (default False)

  Type: 

bool

      unified_paint_settings 

(readonly, never None)

  Type: 

[`UnifiedPaintSettings`](bpy.types.UnifiedPaintSettings.html#bpy.types.UnifiedPaintSettings)

      use_cavity 

Mask painting according to mesh geometry cavity (default False)

  Type: 

bool

      use_sculpt_delay_updates 

Update the geometry when it enters the view, providing faster view navigation (default False)

  Type: 

bool

      use_symmetry_feather 

Reduce the strength of the brush where it overlaps symmetrical daubs (default True)

  Type: 

bool

      use_symmetry_x 

Mirror brush across the X axis (default False)

  Type: 

bool

      use_symmetry_y 

Mirror brush across the Y axis (default False)

  Type: 

bool

      use_symmetry_z 

Mirror brush across the Z axis (default False)

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
