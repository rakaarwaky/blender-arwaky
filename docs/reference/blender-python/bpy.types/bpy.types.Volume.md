# bpy.types.Volume

# Volume(ID)

 

base classes — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct), [`ID`](bpy.types.ID.html#bpy.types.ID)

   class bpy.types.Volume(ID) 

Volume data-block for 3D volume grids

   animation_data 

Animation data for this data-block (readonly)

  Type: 

[`AnimData`](bpy.types.AnimData.html#bpy.types.AnimData) | None

      display 

Volume display settings for 3D viewport (readonly)

  Type: 

[`VolumeDisplay`](bpy.types.VolumeDisplay.html#bpy.types.VolumeDisplay) | None

      filepath 

Volume file used by this Volume data-block (default “”, never None, blend relative `//` prefix supported)

  Type: 

str

      frame_duration 

Number of frames of the sequence to use (in [0, 1048574], default 0)

  Type: 

int

      frame_offset 

Offset the number of the frame to use in the animation (in [-inf, inf], default 0)

  Type: 

int

      frame_start 

Global starting frame of the sequence, assuming first has a #1 (in [-1048574, 1048574], default 1)

  Type: 

int

      grids 

3D volume grids (default None, readonly)

  Type: 

[`VolumeGrids`](bpy.types.VolumeGrids.html#bpy.types.VolumeGrids)[[`VolumeGrid`](bpy.types.VolumeGrid.html#bpy.types.VolumeGrid)]

      is_sequence 

Whether the cache is separated in a series of files (default False)

  Type: 

bool

      materials 

(default None, readonly)

  Type: 

[`IDMaterials`](bpy.types.IDMaterials.html#bpy.types.IDMaterials)[[`Material`](bpy.types.Material.html#bpy.types.Material)]

      packed_file 

(readonly)

  Type: 

[`PackedFile`](bpy.types.PackedFile.html#bpy.types.PackedFile) | None

      render 

Volume render settings for 3D viewport (readonly)

  Type: 

[`VolumeRender`](bpy.types.VolumeRender.html#bpy.types.VolumeRender) | None

      sequence_mode 

Sequence playback mode (default `'CLIP'`)

  
- `CLIP` Clip – Hide frames outside the specified frame range. 
- `EXTEND` Extend – Repeat the start frame before, and the end frame after the frame range. 
- `REPEAT` Repeat – Cycle the frames in the sequence. 
- `PING_PONG` Ping-Pong – Repeat the frames, reversing the playback direction every other cycle.   Type: 

Literal[‘CLIP’, ‘EXTEND’, ‘REPEAT’, ‘PING_PONG’]

      velocity_grid 

Name of the velocity field, or the base name if the velocity is split into multiple grids (default “”, never None)

  Type: 

str

      velocity_scale 

Factor to control the amount of motion blur (in [0, inf], default 1.0)

  Type: 

float

      velocity_unit 

Define how the velocity vectors are interpreted with regard to time, ‘frame’ means the delta time is 1 frame, ‘second’ means the delta time is 1 / FPS (default `'FRAME'`)

  Type: 

Literal[[Velocity Unit Items](bpy_types_enum_items/velocity_unit_items.html#rna-enum-velocity-unit-items)]

      velocity_x_grid 

Name of the grid for the X axis component of the velocity field if it was split into multiple grids (default “”, readonly, never None)

  Type: 

str

      velocity_y_grid 

Name of the grid for the Y axis component of the velocity field if it was split into multiple grids (default “”, readonly, never None)

  Type: 

str

      velocity_z_grid 

Name of the grid for the Z axis component of the velocity field if it was split into multiple grids (default “”, readonly, never None)

  Type: 

str

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

  
- `bpy.context.volume` 
- [`BlendData.volumes`](bpy.types.BlendData.html#bpy.types.BlendData.volumes)   
- [`BlendDataVolumes.new`](bpy.types.BlendDataVolumes.html#bpy.types.BlendDataVolumes.new) 
- [`BlendDataVolumes.remove`](bpy.types.BlendDataVolumes.html#bpy.types.BlendDataVolumes.remove)
