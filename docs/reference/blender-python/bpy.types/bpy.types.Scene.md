# bpy.types.Scene

# Scene(ID)

 

base classes — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct), [`ID`](bpy.types.ID.html#bpy.types.ID)

   class bpy.types.Scene(ID) 

Scene data-block, consisting in objects and defining time and render related settings

   active_clip 

Active Movie Clip that can be used by motion tracking constraints or as a camera’s background image

  Type: 

[`MovieClip`](bpy.types.MovieClip.html#bpy.types.MovieClip) | None

      allow_preroll 

Allows playing back frames before the playback start frame (default False)

  Type: 

bool

      animation_data 

Animation data for this data-block (readonly)

  Type: 

[`AnimData`](bpy.types.AnimData.html#bpy.types.AnimData) | None

      annotation 

Data-block used for annotations in the 3D view

  Type: 

[`Annotation`](bpy.types.Annotation.html#bpy.types.Annotation) | None

      audio_distance_model 

Distance model for distance attenuation calculation (default `'INVERSE_CLAMPED'`)

  
- `NONE` None – No distance attenuation. 
- `INVERSE` Inverse – Inverse distance model. 
- `INVERSE_CLAMPED` Inverse Clamped – Inverse distance model with clamping. 
- `LINEAR` Linear – Linear distance model. 
- `LINEAR_CLAMPED` Linear Clamped – Linear distance model with clamping. 
- `EXPONENT` Exponential – Exponential distance model. 
- `EXPONENT_CLAMPED` Exponential Clamped – Exponential distance model with clamping.   Type: 

Literal[‘NONE’, ‘INVERSE’, ‘INVERSE_CLAMPED’, ‘LINEAR’, ‘LINEAR_CLAMPED’, ‘EXPONENT’, ‘EXPONENT_CLAMPED’]

      audio_doppler_factor 

Pitch factor for Doppler effect calculation (in [0, inf], default 1.0)

  Type: 

float

      audio_doppler_speed 

Speed of sound for Doppler effect calculation (in [0.01, inf], default 343.3)

  Type: 

float

      audio_volume 

Audio volume (in [0, 100], default 1.0)

  Type: 

float

      background_set 

Background set scene

  Type: 

`Scene` | None

      camera 

Active camera, used for rendering the scene

  Type: 

[`Object`](bpy.types.Object.html#bpy.types.Object) | None

      collection 

Scene root collection that owns all the objects and other collections instantiated in the scene (readonly, never None)

  Type: 

[`Collection`](bpy.types.Collection.html#bpy.types.Collection)

      compositing_node_group 

Compositor Nodes

  Type: 

[`NodeTree`](bpy.types.NodeTree.html#bpy.types.NodeTree) | None

      cursor 

(readonly, never None)

  Type: 

[`View3DCursor`](bpy.types.View3DCursor.html#bpy.types.View3DCursor)

      cycles 

Cycles render settings (readonly)

  Type: 

`CyclesRenderSettings` | None

      cycles_curves 

Cycles curves rendering settings (readonly)

  Type: 

`CyclesCurveRenderSettings` | None

      display 

Scene display settings for 3D viewport (readonly)

  Type: 

[`SceneDisplay`](bpy.types.SceneDisplay.html#bpy.types.SceneDisplay) | None

      display_settings 

Settings of device saved image would be displayed on (readonly)

  Type: 

[`ColorManagedDisplaySettings`](bpy.types.ColorManagedDisplaySettings.html#bpy.types.ColorManagedDisplaySettings) | None

      eevee 

EEVEE settings for the scene (readonly)

  Type: 

[`SceneEEVEE`](bpy.types.SceneEEVEE.html#bpy.types.SceneEEVEE) | None

      frame_current 

Current frame, to update animation data from Python frame_set() instead (in [-1048574, 1048574], default 1)

  Type: 

int

      frame_current_final 

Current frame with subframe and time remapping applied (in [-1.04857e+06, 1.04857e+06], default 0.0, readonly)

  Type: 

float

      frame_end 

Final frame of the playback/rendering range (in [0, 1048574], default 250)

  Type: 

int

      frame_float 

(in [-1.04857e+06, 1.04857e+06], default 0.0)

  Type: 

float

      frame_preview_end 

Alternative end frame for UI playback (in [-inf, inf], default 0)

  Type: 

int

      frame_preview_start 

Alternative start frame for UI playback (in [-inf, inf], default 0)

  Type: 

int

      frame_start 

First frame of the playback/rendering range (in [0, 1048574], default 1)

  Type: 

int

      frame_step 

Number of frames to skip forward while rendering/playing back each frame (in [0, 1048574], default 1)

  Type: 

int

      frame_subframe 

(in [0, 1], default 0.0)

  Type: 

float

      gravity 

Constant acceleration in a given direction (array of 3 items, in [-inf, inf], default (0.0, 0.0, -9.81))

  Type: 

[`mathutils.Vector`](mathutils.html#mathutils.Vector)

      grease_pencil_settings 

Grease Pencil settings for the scene (readonly)

  Type: 

[`SceneGpencil`](bpy.types.SceneGpencil.html#bpy.types.SceneGpencil) | None

      hydra 

Hydra settings for the scene (readonly)

  Type: 

[`SceneHydra`](bpy.types.SceneHydra.html#bpy.types.SceneHydra) | None

      is_nla_tweakmode 

Whether there is any action referenced by NLA being edited (strictly read-only) (default False, readonly)

  Type: 

bool

      keying_sets 

Absolute Keying Sets for this Scene (default None, readonly)

  Type: 

[`KeyingSets`](bpy.types.KeyingSets.html#bpy.types.KeyingSets)[[`KeyingSet`](bpy.types.KeyingSet.html#bpy.types.KeyingSet)]

      keying_sets_all 

All Keying Sets available for use (Builtins and Absolute Keying Sets for this Scene) (default None, readonly)

  Type: 

[`KeyingSetsAll`](bpy.types.KeyingSetsAll.html#bpy.types.KeyingSetsAll)[[`KeyingSet`](bpy.types.KeyingSet.html#bpy.types.KeyingSet)]

      lock_frame_selection_to_range 

Don’t allow frame to be selected with mouse outside of frame range (default False)

  Type: 

bool

      objects 

(default None, readonly)

  Type: 

[`SceneObjects`](bpy.types.SceneObjects.html#bpy.types.SceneObjects)[[`Object`](bpy.types.Object.html#bpy.types.Object)]

      playback_loop_mode 

What to do when playback reaches the last frame (default `'INFINITE'`)

  
- `INFINITE` Infinite – After the last frame, jump back to the first and keep playing, infinitely. 
- `STOP_END_FRAME` Stop at End Frame – Stop playback at the last frame, without looping. 
- `STOP_START_FRAME` Stop at Start Frame – After the last frame, jump back to the first and stop playback. 
- `RESTORE` Restore Frame – After the last frame, stop at the frame the playback started from. 
- `BOUNCE` Bounce – At the last frame, reverse playback.   Type: 

Literal[‘INFINITE’, ‘STOP_END_FRAME’, ‘STOP_START_FRAME’, ‘RESTORE’, ‘BOUNCE’]

      render 

(readonly, never None)

  Type: 

[`RenderSettings`](bpy.types.RenderSettings.html#bpy.types.RenderSettings)

      rigidbody_world 

(readonly)

  Type: 

[`RigidBodyWorld`](bpy.types.RigidBodyWorld.html#bpy.types.RigidBodyWorld) | None

      safe_areas 

(readonly, never None)

  Type: 

[`DisplaySafeAreas`](bpy.types.DisplaySafeAreas.html#bpy.types.DisplaySafeAreas)

      sequence_editor 

(readonly)

  Type: 

[`SequenceEditor`](bpy.types.SequenceEditor.html#bpy.types.SequenceEditor) | None

      sequencer_colorspace_settings 

Settings of color space sequencer is working in (readonly)

  Type: 

[`ColorManagedSequencerColorspaceSettings`](bpy.types.ColorManagedSequencerColorspaceSettings.html#bpy.types.ColorManagedSequencerColorspaceSettings) | None

      show_keys_from_selected_only 

Only include channels relating to selected objects and data (default True)

  Type: 

bool

      show_subframe 

Display and allow setting fractional frame values for the current frame (default False)

  Type: 

bool

      simulation_frame_end 

Frame at which simulations end (in [-inf, inf], default 250)

  Type: 

int

      simulation_frame_start 

Frame at which simulations start (in [-inf, inf], default 1)

  Type: 

int

      sync_mode 

How to sync playback (default `'AUDIO_SYNC'`)

  
- `NONE` Play Every Frame – Do not sync, play every frame. 
- `FRAME_DROP` Frame Dropping – Drop frames if playback is too slow. 
- `AUDIO_SYNC` Sync to Audio – Sync to audio playback, dropping frames.   Type: 

Literal[‘NONE’, ‘FRAME_DROP’, ‘AUDIO_SYNC’]

      time_jump_delta 

Number of frames or seconds to jump forward or backward (in [0.1, inf], default 1.0)

  Type: 

float

      time_jump_unit 

Which unit to use for time jumps in the timeline (default `'SECOND'`)

  
- `FRAME` Frame – Jump by frames. 
- `SECOND` Second – Jump by seconds.   Type: 

Literal[‘FRAME’, ‘SECOND’]

      timeline_markers 

Markers used in all timelines for the current scene (default None, readonly)

  Type: 

[`TimelineMarkers`](bpy.types.TimelineMarkers.html#bpy.types.TimelineMarkers)[[`TimelineMarker`](bpy.types.TimelineMarker.html#bpy.types.TimelineMarker)]

      tool_settings 

(readonly, never None)

  Type: 

[`ToolSettings`](bpy.types.ToolSettings.html#bpy.types.ToolSettings)

      transform_orientation_slots 

(default None, readonly)

  Type: 

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.html#bpy.types.bpy_prop_collection)[[`TransformOrientationSlot`](bpy.types.TransformOrientationSlot.html#bpy.types.TransformOrientationSlot)]

      unit_settings 

Unit editing settings (readonly, never None)

  Type: 

[`UnitSettings`](bpy.types.UnitSettings.html#bpy.types.UnitSettings)

      use_audio 

Play back of audio from Sequence Editor, otherwise mute audio (default False)

  Type: 

bool

      use_audio_scrub 

Play audio from Sequence Editor while scrubbing (default False)

  Type: 

bool

      use_custom_simulation_range 

Use a simulation range that is different from the scene range for simulation nodes that don’t override the frame range themselves (default False)

  Type: 

bool

      use_gravity 

Use global gravity for all dynamics (default True)

  Type: 

bool

      use_nodes 

Enable the compositing node group. (default False)

  

Deprecated since version 5.0: removal planned in version 6.0

 

Unused but kept for compatibility reasons. Setting the property has no effect, and getting it always returns True. Use #scene.render.use_compositing to turn compositing to enable or disable compositing.

   Type: 

bool

      use_preview_range 

Use an alternative start/end frame range for animation playback and view renders (default False)

  Type: 

bool

      use_stamp_note 

User defined note for the render stamping (default “”, never None)

  Type: 

str

      view_layers 

(default None, readonly)

  Type: 

[`ViewLayers`](bpy.types.ViewLayers.html#bpy.types.ViewLayers)[[`ViewLayer`](bpy.types.ViewLayer.html#bpy.types.ViewLayer)]

      view_settings 

Color management settings applied on image before saving (readonly)

  Type: 

[`ColorManagedViewSettings`](bpy.types.ColorManagedViewSettings.html#bpy.types.ColorManagedViewSettings) | None

      world 

World used for rendering the scene

  Type: 

[`World`](bpy.types.World.html#bpy.types.World) | None

      classmethod update_render_engine() 

Trigger a render engine update

    statistics(view_layer) 

statistics

  Parameters: 

view_layer ([`ViewLayer`](bpy.types.ViewLayer.html#bpy.types.ViewLayer) | None) – View Layer, (never None)

  Returns: 

Statistics, (never None)

  Return type: 

str

      frame_set(frame, *, subframe=0.0) 

Set scene frame updating all objects and view layers immediately

  Parameters:  
- frame (int) – Frame number to set (in [-1048574, 1048574]) 
- subframe (float) – Subframe time, between 0.0 and 1.0 (in [0, 1], optional)       uvedit_aspect(object) 

Get uv aspect for current object

  Parameters: 

object ([`Object`](bpy.types.Object.html#bpy.types.Object) | None) – Object (never None)

  Returns: 

aspect (array of 2 items, in [0, inf])

  Return type: 

[`mathutils.Vector`](mathutils.html#mathutils.Vector)

      ray_cast(depsgraph, origin, direction, *, distance=1.70141e+38) 

Cast a ray onto evaluated geometry in world-space

  Parameters:  
- depsgraph ([`Depsgraph`](bpy.types.Depsgraph.html#bpy.types.Depsgraph) | None) – The current dependency graph (never None) 
- origin ([`mathutils.Vector`](mathutils.html#mathutils.Vector) | Sequence[float]) – (array of 3 items, in [-inf, inf]) 
- direction ([`mathutils.Vector`](mathutils.html#mathutils.Vector) | Sequence[float]) – (array of 3 items, in [-inf, inf]) 
- distance (float) – Maximum distance (in [0, inf], optional)   Returns: 

`result`, bool

 

`location`, The hit location of this ray cast, [`mathutils.Vector`](mathutils.html#mathutils.Vector)

 

`normal`, The face normal at the ray cast hit location, [`mathutils.Vector`](mathutils.html#mathutils.Vector)

 

`index`, The face index, -1 when original data isn’t available, int

 

`object`, The original (un-evaluated) object that was hit. Note that `location`, `normal`, and `index` correspond to the evaluated object’s mesh., [`Object`](bpy.types.Object.html#bpy.types.Object)

 

`matrix`, Matrix, [`mathutils.Matrix`](mathutils.html#mathutils.Matrix)

  Return type: 

tuple[bool, [`mathutils.Vector`](mathutils.html#mathutils.Vector), [`mathutils.Vector`](mathutils.html#mathutils.Vector), int, [`Object`](bpy.types.Object.html#bpy.types.Object), [`mathutils.Matrix`](mathutils.html#mathutils.Matrix)]

      sequence_editor_create() 

Ensure sequence editor is valid in this scene

  Returns: 

New sequence editor data or None

  Return type: 

[`SequenceEditor`](bpy.types.SequenceEditor.html#bpy.types.SequenceEditor)

      sequence_editor_clear() 

Clear sequence editor in this scene

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

  
- `bpy.context.scene` 
- `bpy.context.sequencer_scene` 
- [`BlendData.scenes`](bpy.types.BlendData.html#bpy.types.BlendData.scenes) 
- [`BlendDataScenes.new`](bpy.types.BlendDataScenes.html#bpy.types.BlendDataScenes.new) 
- [`BlendDataScenes.remove`](bpy.types.BlendDataScenes.html#bpy.types.BlendDataScenes.remove) 
- [`Camera.view_frame`](bpy.types.Camera.html#bpy.types.Camera.view_frame) 
- [`CompositorNodeCryptomatteV2.scene`](bpy.types.CompositorNodeCryptomatteV2.html#bpy.types.CompositorNodeCryptomatteV2.scene) 
- [`CompositorNodeDefocus.scene`](bpy.types.CompositorNodeDefocus.html#bpy.types.CompositorNodeDefocus.scene) 
- [`CompositorNodeRLayers.scene`](bpy.types.CompositorNodeRLayers.html#bpy.types.CompositorNodeRLayers.scene) 
- [`Context.scene`](bpy.types.Context.html#bpy.types.Context.scene) 
- [`Depsgraph.scene`](bpy.types.Depsgraph.html#bpy.types.Depsgraph.scene) 
- [`Depsgraph.scene_eval`](bpy.types.Depsgraph.html#bpy.types.Depsgraph.scene_eval) 
- [`ID.override_hierarchy_create`](bpy.types.ID.html#bpy.types.ID.override_hierarchy_create) 
- [`IDOverrideLibrary.resync`](bpy.types.IDOverrideLibrary.html#bpy.types.IDOverrideLibrary.resync) 
- [`Image.save_render`](bpy.types.Image.html#bpy.types.Image.save_render) 
- [`NodeSocketScene.default_value`](bpy.types.NodeSocketScene.html#bpy.types.NodeSocketScene.default_value)   
- [`NodeTreeInterfaceSocketScene.default_value`](bpy.types.NodeTreeInterfaceSocketScene.html#bpy.types.NodeTreeInterfaceSocketScene.default_value) 
- [`Object.crazyspace_eval`](bpy.types.Object.html#bpy.types.Object.crazyspace_eval) 
- [`Object.is_deform_modified`](bpy.types.Object.html#bpy.types.Object.is_deform_modified) 
- [`Object.is_modified`](bpy.types.Object.html#bpy.types.Object.is_modified) 
- [`RenderEngine.bind_display_space_shader`](bpy.types.RenderEngine.html#bpy.types.RenderEngine.bind_display_space_shader) 
- [`RenderEngine.get_preview_pixel_size`](bpy.types.RenderEngine.html#bpy.types.RenderEngine.get_preview_pixel_size) 
- [`RenderEngine.register_pass`](bpy.types.RenderEngine.html#bpy.types.RenderEngine.register_pass) 
- [`RenderEngine.support_display_space_shader`](bpy.types.RenderEngine.html#bpy.types.RenderEngine.support_display_space_shader) 
- [`RenderEngine.update_render_passes`](bpy.types.RenderEngine.html#bpy.types.RenderEngine.update_render_passes) 
- `Scene.background_set` 
- [`SceneStrip.scene`](bpy.types.SceneStrip.html#bpy.types.SceneStrip.scene) 
- [`StripsMeta.new_scene`](bpy.types.StripsMeta.html#bpy.types.StripsMeta.new_scene) 
- [`StripsTopLevel.new_scene`](bpy.types.StripsTopLevel.html#bpy.types.StripsTopLevel.new_scene) 
- [`Window.find_playing_scene`](bpy.types.Window.html#bpy.types.Window.find_playing_scene) 
- [`Window.scene`](bpy.types.Window.html#bpy.types.Window.scene) 
- [`WorkSpace.sequencer_scene`](bpy.types.WorkSpace.html#bpy.types.WorkSpace.sequencer_scene)
