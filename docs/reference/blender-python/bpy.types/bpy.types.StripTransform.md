# bpy.types.StripTransform

# StripTransform(bpy_struct)

 

base class — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct)

   class bpy.types.StripTransform(bpy_struct) 

Transform parameters for a sequence strip

   filter 

Type of filter to use for image transformation (default `'AUTO'`)

  
- `AUTO` Auto – Automatically choose filter based on scaling factor. 
- `NEAREST` Nearest – Use nearest sample. 
- `BILINEAR` Bilinear – Interpolate between 2×2 samples. 
- `CUBIC_MITCHELL` Cubic Mitchell – Cubic Mitchell filter on 4×4 samples. 
- `CUBIC_BSPLINE` Cubic B-Spline – Cubic B-Spline filter (blurry but no ringing) on 4×4 samples. 
- `BOX` Box – Averages source image samples that fall under destination pixel.   Type: 

Literal[‘AUTO’, ‘NEAREST’, ‘BILINEAR’, ‘CUBIC_MITCHELL’, ‘CUBIC_BSPLINE’, ‘BOX’]

      offset_x 

Move along X axis (in [-inf, inf], default 0.0)

  Type: 

float

      offset_y 

Move along Y axis (in [-inf, inf], default 0.0)

  Type: 

float

      origin 

Origin of image for transformation (array of 2 items, in [-inf, inf], default (0.0, 0.0))

  Type: 

[`bpy_prop_array`](bpy.types.bpy_prop_array.html#bpy.types.bpy_prop_array)[float]

      rotation 

Rotate around image center (in [-inf, inf], default 0.0)

  Type: 

float

      scale_x 

Scale along X axis (in [0, inf], default 1.0)

  Type: 

float

      scale_y 

Scale along Y axis (in [0, inf], default 1.0)

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

  
- [`EffectStrip.transform`](bpy.types.EffectStrip.html#bpy.types.EffectStrip.transform) 
- [`ImageStrip.transform`](bpy.types.ImageStrip.html#bpy.types.ImageStrip.transform) 
- [`MaskStrip.transform`](bpy.types.MaskStrip.html#bpy.types.MaskStrip.transform) 
- [`MetaStrip.transform`](bpy.types.MetaStrip.html#bpy.types.MetaStrip.transform)   
- [`MovieClipStrip.transform`](bpy.types.MovieClipStrip.html#bpy.types.MovieClipStrip.transform) 
- [`MovieStrip.transform`](bpy.types.MovieStrip.html#bpy.types.MovieStrip.transform) 
- [`SceneStrip.transform`](bpy.types.SceneStrip.html#bpy.types.SceneStrip.transform)
