# bpy.types.MovieClip

# MovieClip(ID)

 

base classes — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct), [`ID`](bpy.types.ID.html#bpy.types.ID)

   class bpy.types.MovieClip(ID) 

MovieClip data-block referencing an external movie file

   animation_data 

Animation data for this data-block (readonly)

  Type: 

[`AnimData`](bpy.types.AnimData.html#bpy.types.AnimData) | None

      annotation 

Annotation data for this movie clip

  Type: 

[`Annotation`](bpy.types.Annotation.html#bpy.types.Annotation) | None

      colorspace_settings 

Input color space settings (readonly)

  Type: 

[`ColorManagedInputColorspaceSettings`](bpy.types.ColorManagedInputColorspaceSettings.html#bpy.types.ColorManagedInputColorspaceSettings) | None

      display_aspect 

Display Aspect for this clip, does not affect rendering (array of 2 items, in [0.1, inf], default (1.0, 1.0))

  Type: 

[`mathutils.Vector`](mathutils.html#mathutils.Vector)

      filepath 

Filename of the movie or sequence file (default “”, never None, blend relative `//` prefix supported)

  Type: 

str

      fps 

Detected frame rate of the movie clip in frames per second (in [-inf, inf], default 0.0, readonly)

  Type: 

float

      frame_duration 

Detected duration of movie clip in frames (in [-inf, inf], default 0, readonly)

  Type: 

int

      frame_offset 

Offset of footage first frame relative to its file name (affects only how footage is loading, does not change data associated with a clip) (in [-inf, inf], default 0)

  Type: 

int

      frame_start 

Global scene frame number at which this movie starts playing (affects all data associated with a clip) (in [-inf, inf], default 1)

  Type: 

int

      proxy 

(readonly)

  Type: 

[`MovieClipProxy`](bpy.types.MovieClipProxy.html#bpy.types.MovieClipProxy) | None

      size 

Width and height in pixels, zero when image data cannot be loaded (array of 2 items, in [-inf, inf], default (0, 0), readonly)

  Type: 

[`bpy_prop_array`](bpy.types.bpy_prop_array.html#bpy.types.bpy_prop_array)[int]

      source 

Where the clip comes from (default `'SEQUENCE'`, readonly)

  
- `SEQUENCE` Image Sequence – Multiple image files, as a sequence. 
- `MOVIE` Movie File – Movie file.   Type: 

Literal[‘SEQUENCE’, ‘MOVIE’]

      tracking 

(readonly)

  Type: 

[`MovieTracking`](bpy.types.MovieTracking.html#bpy.types.MovieTracking) | None

      use_proxy 

Use a preview proxy for this clip (default False)

  Type: 

bool

      use_proxy_custom_directory 

Create proxy images in a custom directory (default is movie location) (default False)

  Type: 

bool

      metadata() 

Retrieve metadata of the movie file

  Returns: 

Dict-like object containing the metadata

  Return type: 

[`IDPropertyWrapPtr`](bpy.types.IDPropertyWrapPtr.html#bpy.types.IDPropertyWrapPtr)

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

## References

  
- `bpy.context.edit_movieclip` 
- [`BlendData.movieclips`](bpy.types.BlendData.html#bpy.types.BlendData.movieclips) 
- [`BlendDataMovieClips.load`](bpy.types.BlendDataMovieClips.html#bpy.types.BlendDataMovieClips.load) 
- [`BlendDataMovieClips.remove`](bpy.types.BlendDataMovieClips.html#bpy.types.BlendDataMovieClips.remove) 
- [`CameraBackgroundImage.clip`](bpy.types.CameraBackgroundImage.html#bpy.types.CameraBackgroundImage.clip) 
- [`CameraSolverConstraint.clip`](bpy.types.CameraSolverConstraint.html#bpy.types.CameraSolverConstraint.clip) 
- [`CompositorNodeKeyingScreen.clip`](bpy.types.CompositorNodeKeyingScreen.html#bpy.types.CompositorNodeKeyingScreen.clip) 
- [`CompositorNodeMovieClip.clip`](bpy.types.CompositorNodeMovieClip.html#bpy.types.CompositorNodeMovieClip.clip) 
- [`CompositorNodeMovieDistortion.clip`](bpy.types.CompositorNodeMovieDistortion.html#bpy.types.CompositorNodeMovieDistortion.clip) 
- [`CompositorNodePlaneTrackDeform.clip`](bpy.types.CompositorNodePlaneTrackDeform.html#bpy.types.CompositorNodePlaneTrackDeform.clip)   
- [`CompositorNodeStabilize.clip`](bpy.types.CompositorNodeStabilize.html#bpy.types.CompositorNodeStabilize.clip) 
- [`CompositorNodeTrackPos.clip`](bpy.types.CompositorNodeTrackPos.html#bpy.types.CompositorNodeTrackPos.clip) 
- [`FollowTrackConstraint.clip`](bpy.types.FollowTrackConstraint.html#bpy.types.FollowTrackConstraint.clip) 
- [`MovieClipStrip.clip`](bpy.types.MovieClipStrip.html#bpy.types.MovieClipStrip.clip) 
- [`ObjectSolverConstraint.clip`](bpy.types.ObjectSolverConstraint.html#bpy.types.ObjectSolverConstraint.clip) 
- [`Scene.active_clip`](bpy.types.Scene.html#bpy.types.Scene.active_clip) 
- [`SpaceClipEditor.clip`](bpy.types.SpaceClipEditor.html#bpy.types.SpaceClipEditor.clip) 
- [`StripsMeta.new_clip`](bpy.types.StripsMeta.html#bpy.types.StripsMeta.new_clip) 
- [`StripsTopLevel.new_clip`](bpy.types.StripsTopLevel.html#bpy.types.StripsTopLevel.new_clip)
