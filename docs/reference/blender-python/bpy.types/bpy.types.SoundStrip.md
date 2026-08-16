# bpy.types.SoundStrip

# SoundStrip(Strip)

 

base classes — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct), [`Strip`](bpy.types.Strip.html#bpy.types.Strip)

   class bpy.types.SoundStrip(Strip) 

Sequence strip defining a sound to be played over a period of time

   animation_offset_end 

Animation end offset (trim end) (in [0, inf], default 0)

  

Deprecated since version 5.10: removal planned in version 6.0

 

Replaced by ‘.content_trim_end’.

   Type: 

int

      animation_offset_start 

Animation start offset (trim start) (in [0, inf], default 0)

  

Deprecated since version 5.10: removal planned in version 6.0

 

Replaced by ‘.content_trim_start’.

   Type: 

int

      content_trim_end 

Number of frames to ignore from the end of the underlying source. The source content is trimmed, and future frames are turned into holds (in [0, inf], default 0)

  Type: 

int

      content_trim_start 

Number of frames to ignore from the start of the underlying source. The source content is trimmed, and previous frames are turned into holds (in [0, inf], default 0)

  Type: 

int

      pan 

Playback panning of the sound (only for Mono sources) (in [-inf, inf], default 0.0)

  Type: 

float

      pitch_correction 

Maintain the original pitch of the audio when changing playback speed (default False)

  Type: 

bool

      retiming_keys 

(default None, readonly)

  Type: 

[`RetimingKeys`](bpy.types.RetimingKeys.html#bpy.types.RetimingKeys)[[`RetimingKey`](bpy.types.RetimingKey.html#bpy.types.RetimingKey)]

      show_waveform 

Display the audio waveform inside the strip (default False)

  Type: 

bool

      sound 

Sound data-block used by this strip

  Type: 

[`Sound`](bpy.types.Sound.html#bpy.types.Sound) | None

      sound_offset 

Subframe offset of the sound source start expressed in seconds (in [-inf, inf], default 0.0)

  Type: 

float

      volume 

Playback volume of the sound (in [0, 100], default 1.0)

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
- [`Strip.name`](bpy.types.Strip.html#bpy.types.Strip.name) 
- [`Strip.type`](bpy.types.Strip.html#bpy.types.Strip.type) 
- [`Strip.select`](bpy.types.Strip.html#bpy.types.Strip.select) 
- [`Strip.select_left_handle`](bpy.types.Strip.html#bpy.types.Strip.select_left_handle) 
- [`Strip.select_right_handle`](bpy.types.Strip.html#bpy.types.Strip.select_right_handle) 
- [`Strip.mute`](bpy.types.Strip.html#bpy.types.Strip.mute) 
- [`Strip.lock`](bpy.types.Strip.html#bpy.types.Strip.lock) 
- [`Strip.frame_final_duration`](bpy.types.Strip.html#bpy.types.Strip.frame_final_duration) 
- [`Strip.duration`](bpy.types.Strip.html#bpy.types.Strip.duration) 
- [`Strip.frame_duration`](bpy.types.Strip.html#bpy.types.Strip.frame_duration) 
- [`Strip.content_duration`](bpy.types.Strip.html#bpy.types.Strip.content_duration) 
- [`Strip.frame_start`](bpy.types.Strip.html#bpy.types.Strip.frame_start) 
- [`Strip.content_start`](bpy.types.Strip.html#bpy.types.Strip.content_start) 
- [`Strip.content_end`](bpy.types.Strip.html#bpy.types.Strip.content_end) 
- [`Strip.frame_final_start`](bpy.types.Strip.html#bpy.types.Strip.frame_final_start)   
- [`Strip.left_handle`](bpy.types.Strip.html#bpy.types.Strip.left_handle) 
- [`Strip.frame_final_end`](bpy.types.Strip.html#bpy.types.Strip.frame_final_end) 
- [`Strip.right_handle`](bpy.types.Strip.html#bpy.types.Strip.right_handle) 
- [`Strip.frame_offset_start`](bpy.types.Strip.html#bpy.types.Strip.frame_offset_start) 
- [`Strip.left_handle_offset`](bpy.types.Strip.html#bpy.types.Strip.left_handle_offset) 
- [`Strip.frame_offset_end`](bpy.types.Strip.html#bpy.types.Strip.frame_offset_end) 
- [`Strip.right_handle_offset`](bpy.types.Strip.html#bpy.types.Strip.right_handle_offset) 
- [`Strip.channel`](bpy.types.Strip.html#bpy.types.Strip.channel) 
- [`Strip.blend_type`](bpy.types.Strip.html#bpy.types.Strip.blend_type) 
- [`Strip.blend_alpha`](bpy.types.Strip.html#bpy.types.Strip.blend_alpha) 
- [`Strip.effect_fader`](bpy.types.Strip.html#bpy.types.Strip.effect_fader) 
- [`Strip.use_default_fade`](bpy.types.Strip.html#bpy.types.Strip.use_default_fade) 
- [`Strip.color_tag`](bpy.types.Strip.html#bpy.types.Strip.color_tag) 
- [`Strip.modifiers`](bpy.types.Strip.html#bpy.types.Strip.modifiers) 
- [`Strip.show_retiming_keys`](bpy.types.Strip.html#bpy.types.Strip.show_retiming_keys) 
- [`Strip.connections`](bpy.types.Strip.html#bpy.types.Strip.connections)     

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
- [`Strip.bl_system_properties_get`](bpy.types.Strip.html#bpy.types.Strip.bl_system_properties_get) 
- [`Strip.strip_elem_from_frame`](bpy.types.Strip.html#bpy.types.Strip.strip_elem_from_frame) 
- [`Strip.swap`](bpy.types.Strip.html#bpy.types.Strip.swap) 
- [`Strip.move_to_meta`](bpy.types.Strip.html#bpy.types.Strip.move_to_meta) 
- [`Strip.parent_meta`](bpy.types.Strip.html#bpy.types.Strip.parent_meta) 
- [`Strip.invalidate_cache`](bpy.types.Strip.html#bpy.types.Strip.invalidate_cache) 
- [`Strip.split`](bpy.types.Strip.html#bpy.types.Strip.split) 
- [`Strip.bl_rna_get_subclass`](bpy.types.Strip.html#bpy.types.Strip.bl_rna_get_subclass) 
- [`Strip.bl_rna_get_subclass_py`](bpy.types.Strip.html#bpy.types.Strip.bl_rna_get_subclass_py)
