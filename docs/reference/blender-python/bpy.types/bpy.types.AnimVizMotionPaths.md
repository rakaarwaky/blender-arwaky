# bpy.types.AnimVizMotionPaths

# AnimVizMotionPaths(bpy_struct)

 

base class — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct)

   class bpy.types.AnimVizMotionPaths(bpy_struct) 

Motion Path settings for animation visualization

   bake_location 

When calculating Bone Paths, use Head or Tips (default `'TAILS'`)

  Type: 

Literal[[Motionpath Bake Location Items](bpy_types_enum_items/motionpath_bake_location_items.html#rna-enum-motionpath-bake-location-items)]

      frame_after 

Number of frames to show after the current frame (only for ‘Around Frame’ Onion-skinning method) (in [1, 524287], default 0)

  Type: 

int

      frame_before 

Number of frames to show before the current frame (only for ‘Around Frame’ Onion-skinning method) (in [1, 524287], default 0)

  Type: 

int

      frame_end 

End frame of range of paths to display/calculate (not for ‘Around Frame’ Onion-skinning method) (in [-inf, inf], default 0)

  Type: 

int

      frame_start 

Starting frame of range of paths to display/calculate (not for ‘Around Frame’ Onion-skinning method) (in [-inf, inf], default 0)

  Type: 

int

      frame_step 

Number of frames between paths shown (not for ‘On Keyframes’ Onion-skinning method) (in [1, 100], default 0)

  Type: 

int

      has_motion_paths 

Are there any bone paths that will need updating (read-only) (default False, readonly)

  Type: 

bool

      range 

Type of range to calculate for Motion Paths (default `'SCENE'`)

  Type: 

Literal[[Motionpath Range Items](bpy_types_enum_items/motionpath_range_items.html#rna-enum-motionpath-range-items)]

      show_frame_numbers 

Show frame numbers on Motion Paths (default False)

  Type: 

bool

      show_keyframe_action_all 

For bone motion paths, search whole Action for keyframes instead of in group with matching name only (is slower) (default False)

  Type: 

bool

      show_keyframe_highlight 

Emphasize position of keyframes on Motion Paths (default False)

  Type: 

bool

      show_keyframe_numbers 

Show frame numbers of Keyframes on Motion Paths (default False)

  Type: 

bool

      type 

Type of range to show for Motion Paths (default `'RANGE'`)

  Type: 

Literal[[Motionpath Display Type Items](bpy_types_enum_items/motionpath_display_type_items.html#rna-enum-motionpath-display-type-items)]

      use_camera_space_bake 

Motion path points will be baked into the camera space of the active camera. This means they will only look right when looking through that camera. Switching cameras using markers is not supported. (default False)

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

## References

  
- [`AnimViz.motion_path`](bpy.types.AnimViz.html#bpy.types.AnimViz.motion_path)
