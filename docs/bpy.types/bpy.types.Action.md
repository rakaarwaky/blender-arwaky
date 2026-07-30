# bpy.types.Action

# Action(ID)

 

base classes — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct), [`ID`](bpy.types.ID.html#bpy.types.ID)

   class bpy.types.Action(ID) 

A collection of F-Curves for animation

   curve_frame_range 

The combined frame range of all F-Curves within this action (array of 2 items, in [-inf, inf], default (0.0, 0.0), readonly)

  Type: 

[`mathutils.Vector`](mathutils.html#mathutils.Vector)

      frame_end 

The end frame of the manually set intended playback range (in [-1.04857e+06, 1.04857e+06], default 0.0)

  Type: 

float

      frame_range 

The intended playback frame range of this action, using the manually set range if available, or the combined frame range of all F-Curves within this action if not (assigning sets the manual frame range) (array of 2 items, in [-inf, inf], default (0.0, 0.0))

  Type: 

[`mathutils.Vector`](mathutils.html#mathutils.Vector)

      frame_start 

The start frame of the manually set intended playback range (in [-1.04857e+06, 1.04857e+06], default 0.0)

  Type: 

float

      is_action_layered 

Return whether this is a layered Action. At this point all actions are layered through versioning and this function will always return true (default False, readonly)

  Type: 

bool

      is_action_legacy 

Return whether this is a legacy Action. Legacy Actions have no layers or slots. Since Blender 4.4 actions are automatically updated to layered actions. This will only return true on empty actions (default False, readonly)

  Type: 

bool

      is_empty 

False when there is any Layer, Slot, or legacy F-Curve (default False, readonly)

  Type: 

bool

      layers 

The list of layers that make up this Action (default None, readonly)

  Type: 

[`ActionLayers`](bpy.types.ActionLayers.html#bpy.types.ActionLayers)[[`ActionLayer`](bpy.types.ActionLayer.html#bpy.types.ActionLayer)]

      pose_markers 

Markers specific to this action, for labeling poses (default None, readonly)

  Type: 

[`ActionPoseMarkers`](bpy.types.ActionPoseMarkers.html#bpy.types.ActionPoseMarkers)[[`TimelineMarker`](bpy.types.TimelineMarker.html#bpy.types.TimelineMarker)]

      slots 

The list of slots in this Action (default None, readonly)

  Type: 

[`ActionSlots`](bpy.types.ActionSlots.html#bpy.types.ActionSlots)[[`ActionSlot`](bpy.types.ActionSlot.html#bpy.types.ActionSlot)]

      use_cyclic 

The action is intended to be used as a cycle looping over its manually set playback frame range (enabling this does not automatically make it loop) (default False)

  Type: 

bool

      use_frame_range 

Manually specify the intended playback frame range for the action (this range is used by some tools, but does not affect animation evaluation) (default False)

  Type: 

bool

      deselect_keys() 

Deselects all keys of the Action. The selection status of F-Curves is unchanged.

    fcurve_ensure_for_datablock(datablock, data_path, *, index=0, group_name='') 

Ensure that an F-Curve exists, with the given data path and array index, for the given data-block. This action must already be assigned to the data-block. This function will also create the layer, keyframe strip, and action slot if necessary, and take care of assigning the action slot too

  Parameters:  
- datablock ([`ID`](bpy.types.ID.html#bpy.types.ID) | None) – The data-block animated by this action, for which to ensure the F-Curve exists. This action must already be assigned to the data-block (never None) 
- data_path (str) – Data Path, F-Curve data path (never None) 
- index (int) – Index, Array index (in [0, inf], optional) 
- group_name (str) – Group Name, Name of the group for this F-Curve, if any. If the F-Curve already exists, this parameter is ignored (optional, never None)   Returns: 

The found or created F-Curve

  Return type: 

[`FCurve`](bpy.types.FCurve.html#bpy.types.FCurve)

      flip_with_pose(object) 

Flip the action around the X axis using a pose

  Parameters: 

object ([`Object`](bpy.types.Object.html#bpy.types.Object) | None) – The reference armature object to use when flipping (never None)

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

  
- `bpy.context.active_action` 
- `bpy.context.selected_editable_actions` 
- `bpy.context.selected_visible_actions` 
- [`ActionConstraint.action`](bpy.types.ActionConstraint.html#bpy.types.ActionConstraint.action) 
- [`AnimData.action`](bpy.types.AnimData.html#bpy.types.AnimData.action) 
- [`AnimData.action_tweak_storage`](bpy.types.AnimData.html#bpy.types.AnimData.action_tweak_storage) 
- [`BlendData.actions`](bpy.types.BlendData.html#bpy.types.BlendData.actions) 
- [`BlendDataActions.new`](bpy.types.BlendDataActions.html#bpy.types.BlendDataActions.new)   
- [`BlendDataActions.remove`](bpy.types.BlendDataActions.html#bpy.types.BlendDataActions.remove) 
- `GLTF2_filter_action.action` 
- [`NlaStrip.action`](bpy.types.NlaStrip.html#bpy.types.NlaStrip.action) 
- [`NlaStrips.new`](bpy.types.NlaStrips.html#bpy.types.NlaStrips.new) 
- [`Pose.apply_pose_from_action`](bpy.types.Pose.html#bpy.types.Pose.apply_pose_from_action) 
- [`Pose.backup_create`](bpy.types.Pose.html#bpy.types.Pose.backup_create) 
- [`Pose.blend_pose_from_action`](bpy.types.Pose.html#bpy.types.Pose.blend_pose_from_action) 
- [`WindowManager.poselib_previous_action`](bpy.types.WindowManager.html#bpy.types.WindowManager.poselib_previous_action)
