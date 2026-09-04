# bpy.types.ImageFormatSettings

# ImageFormatSettings(bpy_struct)

 

base class — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct)

   class bpy.types.ImageFormatSettings(bpy_struct) 

Settings for image formats

   cineon_black 

Log conversion reference blackpoint (in [0, 1024], default 0)

  Type: 

int

      cineon_gamma 

Log conversion gamma (in [0, 10], default 0.0)

  Type: 

float

      cineon_white 

Log conversion reference whitepoint (in [0, 1024], default 0)

  Type: 

int

      color_depth 

Bit depth per channel (default `'8'`)

  Type: 

Literal[[Image Color Depth Items](bpy_types_enum_items/image_color_depth_items.html#rna-enum-image-color-depth-items)]

      color_management 

Which color management settings to use for file saving (default `'FOLLOW_SCENE'`)

  Type: 

Literal[‘FOLLOW_SCENE’, ‘OVERRIDE’]

      color_mode 

Choose BW for saving grayscale images, RGB for saving red, green and blue channels, and RGBA for saving red, green, blue and alpha channels (default `'RGBA'`)

  Type: 

Literal[[Image Color Mode Items](bpy_types_enum_items/image_color_mode_items.html#rna-enum-image-color-mode-items)]

      compression 

Amount of time to determine best compression: 0 = no compression with fast file output, 100 = maximum lossless compression with slow file output (in [0, 100], default 15)

  Type: 

int

      display_settings 

Settings of device saved image would be displayed on (readonly)

  Type: 

[`ColorManagedDisplaySettings`](bpy.types.ColorManagedDisplaySettings.html#bpy.types.ColorManagedDisplaySettings) | None

      exr_codec 

Compression codec settings for OpenEXR (default `'NONE'`)

  Type: 

Literal[[Exr Codec Items](bpy_types_enum_items/exr_codec_items.html#rna-enum-exr-codec-items)]

      file_format 

File format to save the rendered images as (default `'PNG'`)

  Type: 

Literal[[Image Type All Items](bpy_types_enum_items/image_type_all_items.html#rna-enum-image-type-all-items)]

      has_linear_colorspace 

File format expects linear color space (default False, readonly)

  Type: 

bool

      jpeg2k_codec 

Codec settings for JPEG 2000 (default `'JP2'`)

  Type: 

Literal[‘JP2’, ‘J2K’]

      linear_colorspace_settings 

Output color space settings (readonly)

  Type: 

[`ColorManagedInputColorspaceSettings`](bpy.types.ColorManagedInputColorspaceSettings.html#bpy.types.ColorManagedInputColorspaceSettings) | None

      media_type 

The type of media to save (default `'IMAGE'`)

  Type: 

Literal[‘IMAGE’, ‘MULTI_LAYER_IMAGE’, ‘VIDEO’]

      quality 

Quality for image formats that support lossy compression (in [0, 100], default 90)

  Type: 

int

      stereo_3d_format 

Settings for stereo 3D (readonly, never None)

  Type: 

[`Stereo3dFormat`](bpy.types.Stereo3dFormat.html#bpy.types.Stereo3dFormat)

      tiff_codec 

Compression mode for TIFF (default `'DEFLATE'`)

  Type: 

Literal[‘NONE’, ‘DEFLATE’, ‘LZW’, ‘PACKBITS’]

      use_cineon_log 

Convert to logarithmic color space (default False)

  Type: 

bool

      use_exr_interleave 

Use legacy interleaved storage of views, layers and passes for compatibility with applications that do not support more efficient multi-part OpenEXR files. (default False)

  Type: 

bool

      use_jpeg2k_cinema_48 

Use OpenJPEG Cinema Preset (48fps) (default False)

  Type: 

bool

      use_jpeg2k_cinema_preset 

Use OpenJPEG Cinema Preset (default False)

  Type: 

bool

      use_jpeg2k_ycc 

Save luminance-chrominance-chrominance channels instead of RGB colors (default False)

  Type: 

bool

      use_preview 

When rendering animations, save JPG preview images in same directory (default False)

  Type: 

bool

      view_settings 

Color management settings applied on image before saving (readonly)

  Type: 

[`ColorManagedViewSettings`](bpy.types.ColorManagedViewSettings.html#bpy.types.ColorManagedViewSettings) | None

      views_format 

Format of multiview media (default `'INDIVIDUAL'`)

  Type: 

Literal[[Views Format Multiview Items](bpy_types_enum_items/views_format_multiview_items.html#rna-enum-views-format-multiview-items)]

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

  
- [`CompositorNodeOutputFile.format`](bpy.types.CompositorNodeOutputFile.html#bpy.types.CompositorNodeOutputFile.format) 
- [`NodeCompositorFileOutputItem.format`](bpy.types.NodeCompositorFileOutputItem.html#bpy.types.NodeCompositorFileOutputItem.format) 
- [`BakeSettings.image_settings`](bpy.types.BakeSettings.html#bpy.types.BakeSettings.image_settings)   
- [`RenderSettings.image_settings`](bpy.types.RenderSettings.html#bpy.types.RenderSettings.image_settings) 
- [`UILayout.template_image_settings`](bpy.types.UILayout.html#bpy.types.UILayout.template_image_settings) 
- [`UILayout.template_image_views`](bpy.types.UILayout.html#bpy.types.UILayout.template_image_views)
