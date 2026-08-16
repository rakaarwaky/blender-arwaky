# bpy.types.MovieTrackingTrack

# MovieTrackingTrack(bpy_struct)

 

base class — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct)

   class bpy.types.MovieTrackingTrack(bpy_struct) 

Match-moving track data for tracking

   annotation 

Annotation data for this track

  Type: 

[`Annotation`](bpy.types.Annotation.html#bpy.types.Annotation) | None

      average_error 

Average error of re-projection (in [-inf, inf], default 0.0, readonly)

  Type: 

float

      bundle 

Position of bundle reconstructed from this track (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0), readonly)

  Type: 

[`mathutils.Vector`](mathutils.html#mathutils.Vector)

      color 

Color of the track in the Movie Clip Editor and the 3D viewport after a solve (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

  Type: 

[`mathutils.Color`](mathutils.html#mathutils.Color)

      correlation_min 

Minimal value of correlation between matched pattern and reference that is still treated as successful tracking (in [0, 1], default 0.0)

  Type: 

float

      frames_limit 

Every tracking cycle, this number of frames are tracked (in [0, 32767], default 0)

  Type: 

int

      has_bundle 

True if track has a valid bundle (default False, readonly)

  Type: 

bool

      hide 

Track is hidden (default False)

  Type: 

bool

      lock 

Track is locked and all changes to it are disabled (default False)

  Type: 

bool

      margin 

Distance from image boundary at which marker stops tracking (in [0, 300], default 0)

  Type: 

int

      markers 

Collection of markers in track (default None, readonly)

  Type: 

[`MovieTrackingMarkers`](bpy.types.MovieTrackingMarkers.html#bpy.types.MovieTrackingMarkers)[[`MovieTrackingMarker`](bpy.types.MovieTrackingMarker.html#bpy.types.MovieTrackingMarker)]

      motion_model 

Default motion model to use for tracking (default `'Loc'`)

  
- `Perspective` Perspective – Search for markers that are perspectively deformed (homography) between frames. 
- `Affine` Affine – Search for markers that are affine-deformed (t, r, k, and skew) between frames. 
- `LocRotScale` Location, Rotation & Scale – Search for markers that are translated, rotated, and scaled between frames. 
- `LocScale` Location & Scale – Search for markers that are translated and scaled between frames. 
- `LocRot` Location & Rotation – Search for markers that are translated and rotated between frames. 
- `Loc` Location – Search for markers that are translated between frames.   Type: 

Literal[‘Perspective’, ‘Affine’, ‘LocRotScale’, ‘LocScale’, ‘LocRot’, ‘Loc’]

      name 

Unique name of track (default “”, never None)

  Type: 

str

      offset 

Offset of track from the parenting point (array of 2 items, in [-inf, inf], default (0.0, 0.0))

  Type: 

[`mathutils.Vector`](mathutils.html#mathutils.Vector)

      pattern_match 

Track pattern from given frame when tracking marker to next frame (default `'KEYFRAME'`)

  
- `KEYFRAME` Keyframe – Track pattern from keyframe to next frame. 
- `PREV_FRAME` Previous frame – Track pattern from current frame to next frame.   Type: 

Literal[‘KEYFRAME’, ‘PREV_FRAME’]

      select 

Track is selected (default False)

  Type: 

bool

      select_anchor 

Track’s anchor point is selected (default False)

  Type: 

bool

      select_pattern 

Track’s pattern area is selected (default False)

  Type: 

bool

      select_search 

Track’s search area is selected (default False)

  Type: 

bool

      use_alpha_preview 

Apply track’s mask on displaying preview (default False)

  Type: 

bool

      use_blue_channel 

Use blue channel from footage for tracking (default True)

  Type: 

bool

      use_brute 

Use a brute-force translation only pre-track before refinement (default False)

  Type: 

bool

      use_custom_color 

Use custom color instead of theme-defined (default False)

  Type: 

bool

      use_grayscale_preview 

Display what the tracking algorithm sees in the preview (default False)

  Type: 

bool

      use_green_channel 

Use green channel from footage for tracking (default True)

  Type: 

bool

      use_mask 

Use a Grease Pencil data-block as a mask to use only specified areas of pattern when tracking (default False)

  Type: 

bool

      use_normalization 

Normalize light intensities while tracking (slower) (default False)

  Type: 

bool

      use_red_channel 

Use red channel from footage for tracking (default True)

  Type: 

bool

      weight 

Influence of this track on a final solution (in [0, 1], default 0.0)

  Type: 

float

      weight_stab 

Influence of this track on 2D stabilization (in [0, 1], default 0.0)

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

  
- `bpy.context.selected_movieclip_tracks` 
- [`MovieTracking.tracks`](bpy.types.MovieTracking.html#bpy.types.MovieTracking.tracks) 
- [`MovieTrackingObject.tracks`](bpy.types.MovieTrackingObject.html#bpy.types.MovieTrackingObject.tracks) 
- [`MovieTrackingObjectPlaneTracks.active`](bpy.types.MovieTrackingObjectPlaneTracks.html#bpy.types.MovieTrackingObjectPlaneTracks.active) 
- [`MovieTrackingObjectTracks.active`](bpy.types.MovieTrackingObjectTracks.html#bpy.types.MovieTrackingObjectTracks.active) 
- [`MovieTrackingObjectTracks.new`](bpy.types.MovieTrackingObjectTracks.html#bpy.types.MovieTrackingObjectTracks.new)   
- [`MovieTrackingStabilization.rotation_tracks`](bpy.types.MovieTrackingStabilization.html#bpy.types.MovieTrackingStabilization.rotation_tracks) 
- [`MovieTrackingStabilization.tracks`](bpy.types.MovieTrackingStabilization.html#bpy.types.MovieTrackingStabilization.tracks) 
- [`MovieTrackingTracks.active`](bpy.types.MovieTrackingTracks.html#bpy.types.MovieTrackingTracks.active) 
- [`MovieTrackingTracks.new`](bpy.types.MovieTrackingTracks.html#bpy.types.MovieTrackingTracks.new) 
- [`UILayout.template_marker`](bpy.types.UILayout.html#bpy.types.UILayout.template_marker)
