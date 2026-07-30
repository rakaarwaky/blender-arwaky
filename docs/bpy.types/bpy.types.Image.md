# bpy.types.Image

# Image(ID)

  

## Image Data

 

The Image data-block is a shallow wrapper around image or video file(s) (on disk, as packed data, or generated).

 

All actual data like the pixel buffer, size, resolution etc. is cached in an [`imbuf.types.ImBuf`](imbuf.types.html#imbuf.types.ImBuf) image buffer (or several buffers in some cases, like UDIM textures, multi-views, animations…).

 

Several properties and functions of the Image data-block are then actually using/modifying its image buffer, and not the Image data-block itself.

  

Warning

 

One key limitation is that image buffers are not shared between different Image data-blocks, and they are not duplicated when copying an image.

 

So until a modified image buffer is saved on disk, duplicating its Image data-block will not propagate the underlying buffer changes to the new Image.

  

This example script generates an Image data-block with a given size, change its first pixel, rescale it, and duplicates the image.

 

The duplicated image still has the same size and colors as the original image at its creation, all editing in the original image’s buffer is ‘lost’ in its copy.

 

```python
import bpy

image_src = bpy.data.images.new('src', 1024, 102)
print(image_src.size)
print(image_src.pixels[0:4])

image_src.scale(1024, 720)
image_src.pixels[0:4] = (0.5, 0.5, 0.5, 0.5)
image_src.update()
print(image_src.size)
print(image_src.pixels[0:4])

image_dest = image_src.copy()
image_dest.update()
print(image_dest.size)
print(image_dest.pixels[0:4])
```

  

base classes — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct), [`ID`](bpy.types.ID.html#bpy.types.ID)

   class bpy.types.Image(ID) 

Image data-block referencing an external or packed image

   alpha_mode 

Representation of alpha in the image file, to convert to and from when saving and loading the image (default `'STRAIGHT'`)

  
- `STRAIGHT` Straight – Store RGB and alpha channels separately with alpha acting as a mask, also known as unassociated alpha. Commonly used by image editing applications and file formats like PNG.. 
- `PREMUL` Premultiplied – Store RGB channels with alpha multiplied in, also known as associated alpha. The natural format for renders and used by file formats like OpenEXR.. 
- `CHANNEL_PACKED` Channel Packed – Different images are packed in the RGB and alpha channels, and they should not affect each other. Channel packing is commonly used by game engines to save memory.. 
- `NONE` None – Ignore alpha channel from the file and make image fully opaque.   Type: 

Literal[‘STRAIGHT’, ‘PREMUL’, ‘CHANNEL_PACKED’, ‘NONE’]

      channels 

Number of channels in pixels buffer (in [0, inf], default 0, readonly)

  Type: 

int

      colorspace_settings 

Input color space settings (readonly)

  Type: 

[`ColorManagedInputColorspaceSettings`](bpy.types.ColorManagedInputColorspaceSettings.html#bpy.types.ColorManagedInputColorspaceSettings) | None

      depth 

Image bit depth (in [0, inf], default 0, readonly)

  Type: 

int

      display_aspect 

Display Aspect for this image, does not affect rendering (array of 2 items, in [0.1, inf], default (1.0, 1.0))

  Type: 

[`mathutils.Vector`](mathutils.html#mathutils.Vector)

      file_format 

Format used for re-saving this file (default `'TARGA'`)

  Type: 

Literal[[Image Type All Items](bpy_types_enum_items/image_type_all_items.html#rna-enum-image-type-all-items)]

      filepath 

Image/Movie file name (default “”, never None, blend relative `//` prefix supported)

  Type: 

str

      filepath_raw 

Image/Movie file name (without data refreshing) (default “”, never None, blend relative `//` prefix supported)

  Type: 

str

      frame_duration 

Duration (in frames) of the image (1 when not a video/sequence) (in [0, inf], default 0, readonly)

  Type: 

int

      generated_color 

Fill color for the generated image (array of 4 items, in [0, inf], default (0.0, 0.0, 0.0, 0.0))

  Type: 

[`bpy_prop_array`](bpy.types.bpy_prop_array.html#bpy.types.bpy_prop_array)[float]

      generated_height 

Generated image height (in [1, 65536], default 1024)

  Type: 

int

      generated_type 

Generated image type (default `'UV_GRID'`)

  Type: 

Literal[[Image Generated Type Items](bpy_types_enum_items/image_generated_type_items.html#rna-enum-image-generated-type-items)]

      generated_width 

Generated image width (in [1, 65536], default 1024)

  Type: 

int

      has_data 

True if the image data is loaded into memory (default False, readonly)

  Type: 

bool

      is_dirty 

Image has changed and is not saved (default False, readonly)

  Type: 

bool

      is_float 

True if this image is stored in floating-point buffer (default False, readonly)

  Type: 

bool

      is_multiview 

Image has more than one view (default False, readonly)

  Type: 

bool

      is_stereo_3d 

Image has left and right views (default False, readonly)

  Type: 

bool

      packed_file 

First packed file of the image (readonly)

  Type: 

[`PackedFile`](bpy.types.PackedFile.html#bpy.types.PackedFile) | None

      packed_files 

Collection of packed images (default None, readonly)

  Type: 

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.html#bpy.types.bpy_prop_collection)[[`ImagePackedFile`](bpy.types.ImagePackedFile.html#bpy.types.ImagePackedFile)]

      pixels 

Image buffer pixels in floating-point values (dynamic array, in [-inf, inf], default 0.0)

  Type: 

[`bpy_prop_array`](bpy.types.bpy_prop_array.html#bpy.types.bpy_prop_array)[float]

      render_slots 

Render slots of the image (default None, readonly)

  Type: 

[`RenderSlots`](bpy.types.RenderSlots.html#bpy.types.RenderSlots)[[`RenderSlot`](bpy.types.RenderSlot.html#bpy.types.RenderSlot)]

      resolution 

X/Y pixels per meter, for the image buffer (array of 2 items, in [-inf, inf], default (0.0, 0.0))

  Type: 

[`mathutils.Vector`](mathutils.html#mathutils.Vector)

      seam_margin 

Margin to take into account when fixing UV seams during painting. Higher number would improve seam-fixes for mipmaps, but decreases performance. (in [-32768, 32767], default 8)

  Type: 

int

      size 

Width and height of the image buffer in pixels, zero when image data cannot be loaded (array of 2 items, in [-inf, inf], default (0, 0), readonly)

  Type: 

[`bpy_prop_array`](bpy.types.bpy_prop_array.html#bpy.types.bpy_prop_array)[int]

      source 

Where the image comes from (default `'FILE'`)

  
- `FILE` Single Image – Single image file. 
- `SEQUENCE` Image Sequence – Multiple image files, as a sequence. 
- `MOVIE` Movie – Movie file. 
- `GENERATED` Generated – Generated image. 
- `VIEWER` Viewer – Compositing node viewer. 
- `TILED` UDIM Tiles – Tiled UDIM image texture.   Type: 

Literal[‘FILE’, ‘SEQUENCE’, ‘MOVIE’, ‘GENERATED’, ‘VIEWER’, ‘TILED’]

      stereo_3d_format 

Settings for stereo 3d (readonly, never None)

  Type: 

[`Stereo3dFormat`](bpy.types.Stereo3dFormat.html#bpy.types.Stereo3dFormat)

      tiles 

Tiles of the image (default None, readonly)

  Type: 

[`UDIMTiles`](bpy.types.UDIMTiles.html#bpy.types.UDIMTiles)[[`UDIMTile`](bpy.types.UDIMTile.html#bpy.types.UDIMTile)]

      type 

How to generate the image (default `'IMAGE'`, readonly)

  Type: 

Literal[‘IMAGE’, ‘MULTILAYER’, ‘UV_TEST’, ‘RENDER_RESULT’, ‘COMPOSITING’]

      use_deinterlace 

Deinterlace movie file on load (default False)

  Type: 

bool

      use_generated_float 

Generate floating-point buffer (default False)

  Type: 

bool

      use_half_precision 

Use 16 bits per channel to lower the memory usage during rendering. Note: Not supported by Cycles

 

(default True)

  Type: 

bool

      use_multiview 

Use Multiple Views (when available) (default False)

  Type: 

bool

      use_view_as_render 

Apply render part of display transformation when displaying this image on the screen (default False)

  Type: 

bool

      views_format 

Mode to load image views (default `'INDIVIDUAL'`)

  Type: 

Literal[[Views Format Items](bpy_types_enum_items/views_format_items.html#rna-enum-views-format-items)]

      save_render(filepath, *, scene=None, quality=0) 

Save image to a specific path using a scenes render settings

  Parameters:  
- filepath (str) – Output path (never None) 
- scene ([`Scene`](bpy.types.Scene.html#bpy.types.Scene) | None) – Scene to take image parameters from (optional) 
- quality (int) – Quality, Quality for image formats that support lossy compression, uses default quality if not specified (in [0, 100], optional)       save(*, filepath='', quality=0, save_copy=False) 

Save image

  Parameters:  
- filepath (str) – Output path, uses image data-block filepath if not specified (optional, never None) 
- quality (int) – Quality, Quality for image formats that support lossy compression, uses default quality if not specified (in [0, 100], optional) 
- save_copy (bool) – Save Copy, Save the image as a copy, without updating current image’s filepath (optional)       pack(*, data=b'', data_len=0) 

Pack an image as embedded data into the .blend file

  Parameters:  
- data (bytes) – data, Raw data (bytes, exact content of the embedded file) (optional, never None) 
- data_len (int) – data_len, length of given data (mandatory if data is provided) (in [0, inf], optional)       unpack(*, method='USE_LOCAL') 

Save an image packed in the .blend file to disk

  Parameters: 

method (Literal[[Unpack Method Items](bpy_types_enum_items/unpack_method_items.html#rna-enum-unpack-method-items)]) – method, How to unpack (optional)

      reload() 

Reload the image from its source path

    update() 

Update the display image from the floating-point buffer

    scale(width, height, *, frame=0, tile_index=0) 

Scale the buffer of the image, in pixels

  Parameters:  
- width (int) – Width (in [1, inf]) 
- height (int) – Height (in [1, inf]) 
- frame (int) – Frame, Frame (for image sequences) (in [0, inf], optional) 
- tile_index (int) – Tile, Tile index (for tiled images) (in [0, inf], optional)       gl_touch(*, frame=0, layer_index=0, pass_index=0) 

Delay the image from being cleaned from the cache due inactivity

  Parameters:  
- frame (int) – Frame, Frame of image sequence or movie (in [0, inf], optional) 
- layer_index (int) – Layer, Index of layer that should be loaded (in [0, inf], optional) 
- pass_index (int) – Pass, Index of pass that should be loaded (in [0, inf], optional)   Returns: 

Error, OpenGL error value (in [-inf, inf])

  Return type: 

int

      gl_load(*, frame=0, layer_index=0, pass_index=0) 

Load the image into an OpenGL texture. On success, image.bindcode will contain the OpenGL texture bindcode. Colors read from the texture will be in scene linear color space and have premultiplied or straight alpha matching the image alpha mode.

  Parameters:  
- frame (int) – Frame, Frame of image sequence or movie (in [0, inf], optional) 
- layer_index (int) – Layer, Index of layer that should be loaded (in [0, inf], optional) 
- pass_index (int) – Pass, Index of pass that should be loaded (in [0, inf], optional)   Returns: 

Error, OpenGL error value (in [-inf, inf])

  Return type: 

int

      gl_free() 

Free the image from OpenGL graphics memory

    filepath_from_user(*, image_user=None) 

Return the absolute path to the filepath of an image frame specified by the image user

  Parameters: 

image_user ([`ImageUser`](bpy.types.ImageUser.html#bpy.types.ImageUser) | None) – Image user of the image to get filepath for (optional)

  Returns: 

File Path, The resulting filepath from the image and its user (never None)

  Return type: 

str

      buffers_free() 

Free the image buffers from memory

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

      

### Inherited Properties

  
- [`bpy_struct.id_data`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.id_data) 
- [`ID.name`](bpy.types.ID.html#bpy.types.ID.name) 
- [`ID.name_full`](bpy.types.ID.html#bpy.types.ID.name_full) 
- [`ID.id_type`](bpy.types.ID.html#bpy.types.ID.id_type) 
- [`ID.session_uid`](bpy.types.ID.html#bpy.types.ID.session_uid) 
- [`ID.is_evaluated`](bpy.types.ID.html#bpy.types.ID.is_evaluated) 
- [`ID.original`](bpy.types.ID.html#bpy.types.ID.original) 
- [`ID.users`](bpy.types.ID.html#bpy.types.ID.users) 
- [`ID.use_fake_user`](bpy.types.ID.html#bpy.types.ID.use_fake_user) 
- [`ID.use_extra_user`](bpy.types.ID.html#bpy.types.ID.use_extra_user) 
- [`ID.is_embedded_data`](bpy.types.ID.html#bpy.types.ID.is_embedded_data)   
- [`ID.is_linked_packed`](bpy.types.ID.html#bpy.types.ID.is_linked_packed) 
- [`ID.is_missing`](bpy.types.ID.html#bpy.types.ID.is_missing) 
- [`ID.is_runtime_data`](bpy.types.ID.html#bpy.types.ID.is_runtime_data) 
- [`ID.is_editable`](bpy.types.ID.html#bpy.types.ID.is_editable) 
- [`ID.tag`](bpy.types.ID.html#bpy.types.ID.tag) 
- [`ID.is_library_indirect`](bpy.types.ID.html#bpy.types.ID.is_library_indirect) 
- [`ID.library`](bpy.types.ID.html#bpy.types.ID.library) 
- [`ID.library_weak_reference`](bpy.types.ID.html#bpy.types.ID.library_weak_reference) 
- [`ID.asset_data`](bpy.types.ID.html#bpy.types.ID.asset_data) 
- [`ID.override_library`](bpy.types.ID.html#bpy.types.ID.override_library) 
- [`ID.preview`](bpy.types.ID.html#bpy.types.ID.preview)     

### Inherited Functions

  
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
- [`ID.bl_system_properties_get`](bpy.types.ID.html#bpy.types.ID.bl_system_properties_get) 
- [`ID.rename`](bpy.types.ID.html#bpy.types.ID.rename) 
- [`ID.evaluated_get`](bpy.types.ID.html#bpy.types.ID.evaluated_get) 
- [`ID.copy`](bpy.types.ID.html#bpy.types.ID.copy) 
- [`ID.asset_mark`](bpy.types.ID.html#bpy.types.ID.asset_mark) 
- [`ID.asset_clear`](bpy.types.ID.html#bpy.types.ID.asset_clear) 
- [`ID.asset_generate_preview`](bpy.types.ID.html#bpy.types.ID.asset_generate_preview) 
- [`ID.override_create`](bpy.types.ID.html#bpy.types.ID.override_create) 
- [`ID.override_hierarchy_create`](bpy.types.ID.html#bpy.types.ID.override_hierarchy_create) 
- [`ID.user_clear`](bpy.types.ID.html#bpy.types.ID.user_clear) 
- [`ID.user_remap`](bpy.types.ID.html#bpy.types.ID.user_remap) 
- [`ID.make_local`](bpy.types.ID.html#bpy.types.ID.make_local) 
- [`ID.user_of_id`](bpy.types.ID.html#bpy.types.ID.user_of_id) 
- [`ID.animation_data_create`](bpy.types.ID.html#bpy.types.ID.animation_data_create) 
- [`ID.animation_data_clear`](bpy.types.ID.html#bpy.types.ID.animation_data_clear) 
- [`ID.update_tag`](bpy.types.ID.html#bpy.types.ID.update_tag) 
- [`ID.preview_ensure`](bpy.types.ID.html#bpy.types.ID.preview_ensure) 
- [`ID.bl_rna_get_subclass`](bpy.types.ID.html#bpy.types.ID.bl_rna_get_subclass) 
- [`ID.bl_rna_get_subclass_py`](bpy.types.ID.html#bpy.types.ID.bl_rna_get_subclass_py)     

### References

  
- `bpy.context.edit_image` 
- [`BlendData.images`](bpy.types.BlendData.html#bpy.types.BlendData.images) 
- [`BlendDataImages.load`](bpy.types.BlendDataImages.html#bpy.types.BlendDataImages.load) 
- [`BlendDataImages.new`](bpy.types.BlendDataImages.html#bpy.types.BlendDataImages.new) 
- [`BlendDataImages.remove`](bpy.types.BlendDataImages.html#bpy.types.BlendDataImages.remove) 
- [`CameraBackgroundImage.image`](bpy.types.CameraBackgroundImage.html#bpy.types.CameraBackgroundImage.image) 
- [`CompositorNodeCryptomatteV2.image`](bpy.types.CompositorNodeCryptomatteV2.html#bpy.types.CompositorNodeCryptomatteV2.image) 
- [`CompositorNodeImage.image`](bpy.types.CompositorNodeImage.html#bpy.types.CompositorNodeImage.image) 
- [`GeometryNodeInputImage.image`](bpy.types.GeometryNodeInputImage.html#bpy.types.GeometryNodeInputImage.image) 
- [`ImagePaint.canvas`](bpy.types.ImagePaint.html#bpy.types.ImagePaint.canvas) 
- [`ImagePaint.clone_image`](bpy.types.ImagePaint.html#bpy.types.ImagePaint.clone_image) 
- [`ImagePaint.stencil_image`](bpy.types.ImagePaint.html#bpy.types.ImagePaint.stencil_image) 
- [`ImageTexture.image`](bpy.types.ImageTexture.html#bpy.types.ImageTexture.image)   
- [`Material.texture_paint_images`](bpy.types.Material.html#bpy.types.Material.texture_paint_images) 
- [`MaterialGPencilStyle.fill_image`](bpy.types.MaterialGPencilStyle.html#bpy.types.MaterialGPencilStyle.fill_image) 
- [`MaterialGPencilStyle.stroke_image`](bpy.types.MaterialGPencilStyle.html#bpy.types.MaterialGPencilStyle.stroke_image) 
- [`MovieTrackingPlaneTrack.image`](bpy.types.MovieTrackingPlaneTrack.html#bpy.types.MovieTrackingPlaneTrack.image) 
- [`NodeSocketImage.default_value`](bpy.types.NodeSocketImage.html#bpy.types.NodeSocketImage.default_value) 
- [`NodeTreeInterfaceSocketImage.default_value`](bpy.types.NodeTreeInterfaceSocketImage.html#bpy.types.NodeTreeInterfaceSocketImage.default_value) 
- [`PaintModeSettings.canvas_image`](bpy.types.PaintModeSettings.html#bpy.types.PaintModeSettings.canvas_image) 
- [`ShaderNodeTexEnvironment.image`](bpy.types.ShaderNodeTexEnvironment.html#bpy.types.ShaderNodeTexEnvironment.image) 
- [`ShaderNodeTexImage.image`](bpy.types.ShaderNodeTexImage.html#bpy.types.ShaderNodeTexImage.image) 
- [`SpaceImageEditor.image`](bpy.types.SpaceImageEditor.html#bpy.types.SpaceImageEditor.image) 
- [`TextureNodeImage.image`](bpy.types.TextureNodeImage.html#bpy.types.TextureNodeImage.image) 
- [`UILayout.template_image_layers`](bpy.types.UILayout.html#bpy.types.UILayout.template_image_layers)
