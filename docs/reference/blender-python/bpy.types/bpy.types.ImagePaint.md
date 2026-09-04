# bpy.types.ImagePaint

# ImagePaint(Paint)

 

base classes — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct), [`Paint`](bpy.types.Paint.html#bpy.types.Paint)

   class bpy.types.ImagePaint(Paint) 

Properties of image and texture painting mode

   canvas 

Image used as canvas

  Type: 

[`Image`](bpy.types.Image.html#bpy.types.Image) | None

      clone_alpha 

Opacity of clone image display (in [0, 1], default 0.5)

  Type: 

float

      clone_image 

Image used as clone source

  Type: 

[`Image`](bpy.types.Image.html#bpy.types.Image) | None

      clone_offset 

(array of 2 items, in [-inf, inf], default (0.0, 0.0))

  Type: 

[`mathutils.Vector`](mathutils.html#mathutils.Vector)

      dither 

Amount of dithering when painting on byte images (in [0, 2], default 0.0)

  Type: 

float

      interpolation 

Texture filtering type (default `'LINEAR'`)

  
- `LINEAR` Linear – Linear interpolation. 
- `CLOSEST` Closest – No interpolation (sample closest texel).   Type: 

Literal[‘LINEAR’, ‘CLOSEST’]

      invert_stencil 

Invert the stencil layer (default False)

  Type: 

bool

      missing_materials 

The mesh is missing materials (default False, readonly)

  Type: 

bool

      missing_stencil 

Image Painting does not have a stencil (default False, readonly)

  Type: 

bool

      missing_texture 

Image Painting does not have a texture to paint on (default False, readonly)

  Type: 

bool

      missing_uvs 

A UV layer is missing on the mesh (default False, readonly)

  Type: 

bool

      mode 

Mode of operation for projection painting (default `'MATERIAL'`)

  
- `MATERIAL` Material – Detect image slots from the material. 
- `IMAGE` Single Image – Set image for texture painting directly.   Type: 

Literal[‘MATERIAL’, ‘IMAGE’]

      normal_angle 

Paint most on faces pointing towards the view according to this angle (in [0, 90], default 80)

  Type: 

int

      screen_grab_size 

Size to capture the image for re-projecting (array of 2 items, in [512, 16384], default (0, 0))

  Type: 

[`bpy_prop_array`](bpy.types.bpy_prop_array.html#bpy.types.bpy_prop_array)[int]

      seam_bleed 

Extend paint beyond the faces’ UVs to reduce seams (in pixels, slower) (in [-32768, 32767], default 2)

  Type: 

int

      stencil_color 

Stencil color in the viewport (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

  Type: 

[`mathutils.Color`](mathutils.html#mathutils.Color)

      stencil_image 

Image used as stencil

  Type: 

[`Image`](bpy.types.Image.html#bpy.types.Image) | None

      use_backface_culling 

Ignore faces pointing away from the view (faster) (default True)

  Type: 

bool

      use_clone_layer 

Use another UV map as clone source, otherwise use the 3D cursor as the source (default False)

  Type: 

bool

      use_normal_falloff 

Paint most on faces pointing towards the view (default True)

  Type: 

bool

      use_occlude 

Only paint onto the faces directly under the brush (slower) (default True)

  Type: 

bool

      use_stencil_layer 

Set the mask layer from the UV map buttons (default False)

  Type: 

bool

      detect_data() 

Check if required texpaint data exist

  Return type: 

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

  
- [`ToolSettings.image_paint`](bpy.types.ToolSettings.html#bpy.types.ToolSettings.image_paint)
