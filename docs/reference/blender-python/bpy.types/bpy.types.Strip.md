# bpy.types.Strip

# Strip(bpy_struct)

 

base class — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct)

  

Subclasses

  
- [EffectStrip(Strip)](bpy.types.EffectStrip.html) 
- [ImageStrip(Strip)](bpy.types.ImageStrip.html) 
- [MaskStrip(Strip)](bpy.types.MaskStrip.html) 
- [MetaStrip(Strip)](bpy.types.MetaStrip.html) 
- [MovieClipStrip(Strip)](bpy.types.MovieClipStrip.html) 
- [MovieStrip(Strip)](bpy.types.MovieStrip.html) 
- [SceneStrip(Strip)](bpy.types.SceneStrip.html) 
- [SoundStrip(Strip)](bpy.types.SoundStrip.html)     class bpy.types.Strip(bpy_struct) 

A single container for content in the Video Sequence Editor

   blend_alpha 

Percentage of how much the strip’s colors affect other strips (in [0, 1], default 1.0)

  Type: 

float

      blend_type 

Method for controlling how the strip combines with other strips (default `'ALPHA_OVER'`)

  Type: 

Literal[‘REPLACE’, ‘CROSS’, ‘DARKEN’, ‘MULTIPLY’, ‘BURN’, ‘LINEAR_BURN’, ‘LIGHTEN’, ‘SCREEN’, ‘DODGE’, ‘ADD’, ‘OVERLAY’, ‘SOFT_LIGHT’, ‘HARD_LIGHT’, ‘VIVID_LIGHT’, ‘LINEAR_LIGHT’, ‘PIN_LIGHT’, ‘DIFFERENCE’, ‘EXCLUSION’, ‘SUBTRACT’, ‘HUE’, ‘SATURATION’, ‘COLOR’, ‘VALUE’, ‘ALPHA_OVER’, ‘ALPHA_UNDER’, ‘GAMMA_CROSS’]

      channel 

Vertical position of the strip (in [1, 128], default 0)

  Type: 

int

      color_tag 

Color tag for a strip (default `'COLOR_01'`)

  Type: 

Literal[[Strip Color Items](bpy_types_enum_items/strip_color_items.html#rna-enum-strip-color-items)]

      connections 

Other strips currently connected to this strip (default None, readonly)

  Type: 

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.html#bpy.types.bpy_prop_collection)[`Strip`]

      content_duration 

Length of the underlying strip source in frames, excluding handles (in [1, 1048574], default 0, readonly)

  Type: 

int

      content_end 

Timeline frame where underlying strip source ends (in [-inf, inf], default 0, readonly)

  Type: 

int

      content_start 

Timeline frame where underlying strip source begins (in [-inf, inf], default 0.0)

  Type: 

float

      duration 

Length of the strip in frames from left handle to right handle (in [-inf, inf], default 0)

  Type: 

int

      effect_fader 

Custom fade value (in [0, 1], default 0.0)

  Type: 

float

      frame_duration 

The length of the contents of this strip before the handles are applied (in [1, 1048574], default 0, readonly)

  

Deprecated since version 5.10: removal planned in version 6.0

 

Replaced by ‘.content_duration’.

   Type: 

int

      frame_final_duration 

The length of the contents of this strip after the handles are applied (in [-inf, inf], default 0)

  

Deprecated since version 5.10: removal planned in version 6.0

 

Replaced by ‘.duration’.

   Type: 

int

      frame_final_end 

End frame displayed in the sequence editor after offsets are applied (in [-inf, inf], default 0)

  

Deprecated since version 5.10: removal planned in version 6.0

 

Replaced by ‘.right_handle’.

   Type: 

int

      frame_final_start 

Start frame displayed in the sequence editor after offsets are applied, setting this is equivalent to moving the handle, not the actual start frame (in [-inf, inf], default 0)

  

Deprecated since version 5.10: removal planned in version 6.0

 

Replaced by ‘.left_handle’.

   Type: 

int

      frame_offset_end 

Offset from the end of the strip in frames (in [-inf, inf], default 0.0)

  

Deprecated since version 5.10: removal planned in version 6.0

 

Replaced by ‘.right_handle_offset’.

   Type: 

float

      frame_offset_start 

Offset from the start of the strip in frames (in [-inf, inf], default 0.0)

  

Deprecated since version 5.10: removal planned in version 6.0

 

Replaced by ‘.left_handle_offset’.

   Type: 

float

      frame_start 

X position where the strip begins (in [-inf, inf], default 0.0)

  

Deprecated since version 5.10: removal planned in version 6.0

 

Replaced by ‘.content_start’.

   Type: 

float

      left_handle 

Timeline frame of the left handle and the start frame of the strip (in [-inf, inf], default 0)

  Type: 

int

      left_handle_offset 

Rightward frame offset of the left handle from the start of the strip content (in [-inf, inf], default 0.0)

  Type: 

float

      lock 

Lock strip so that it cannot be transformed (default False)

  Type: 

bool

      modifiers 

Modifiers affecting this strip (default None, readonly)

  Type: 

[`StripModifiers`](bpy.types.StripModifiers.html#bpy.types.StripModifiers)[[`StripModifier`](bpy.types.StripModifier.html#bpy.types.StripModifier)]

      mute 

Disable strip so that it does not contribute any output (default False)

  Type: 

bool

      name 

(default “”, never None)

  Type: 

str

      right_handle 

Timeline frame of the right handle, which is the first frame where the strip no longer contributes to the output (in [-inf, inf], default 0)

  Type: 

int

      right_handle_offset 

Leftward frame offset of the right handle from the end of the strip content (in [-inf, inf], default 0.0)

  Type: 

float

      select 

Whether the strip is selected (default False)

  Type: 

bool

      select_left_handle 

Whether the left handle is selected (default False)

  Type: 

bool

      select_right_handle 

Whether the right handle is selected (default False)

  Type: 

bool

      show_retiming_keys 

Show retiming keys, so they can be moved (default False)

  Type: 

bool

      type 

(default `'IMAGE'`, readonly)

  Type: 

Literal[‘IMAGE’, ‘META’, ‘SCENE’, ‘MOVIE’, ‘MOVIECLIP’, ‘MASK’, ‘SOUND’, ‘CROSS’, ‘ADD’, ‘SUBTRACT’, ‘ALPHA_OVER’, ‘ALPHA_UNDER’, ‘GAMMA_CROSS’, ‘COMPOSITOR’, ‘MULTIPLY’, ‘WIPE’, ‘GLOW’, ‘COLOR’, ‘SPEED’, ‘MULTICAM’, ‘ADJUSTMENT’, ‘GAUSSIAN_BLUR’, ‘TEXT’, ‘COLORMIX’]

      use_default_fade 

Fade effect using the built-in default (usually makes the transition as long as the effect strip) (default False)

  Type: 

bool

      bl_system_properties_get(*, do_create=False) 

DEBUG ONLY. Internal access to runtime-defined RNA data storage, intended solely for testing and debugging purposes. Do not access it in regular scripting work, and in particular, do not assume that it contains writable data

  Parameters: 

do_create (bool) – Ensure that system properties are created if they do not exist yet (optional)

  Returns: 

The system properties root container, or None if there are no system properties stored in this data yet, and its creation was not requested

  Return type: 

[`PropertyGroup`](bpy.types.PropertyGroup.html#bpy.types.PropertyGroup)

      strip_elem_from_frame(frame) 

Return the strip element from a given frame or None

  Parameters: 

frame (int) – Frame, The frame to get the strip element from (in [-1048574, 1048574])

  Returns: 

strip element of the current frame

  Return type: 

[`StripElement`](bpy.types.StripElement.html#bpy.types.StripElement)

      swap(other) 

Swap the position of this strip with another

  Parameters: 

other (`Strip` | None) – Other, Other strip to swap with (never None)

      move_to_meta(meta_sequence) 

Move this strip into a meta Strip

  Parameters: 

meta_sequence (`Strip` | None) – Destination Meta Strip, Meta to move the strip into (never None)

      parent_meta() 

Returns parent meta Strip

  Returns: 

Parent meta strip

  Return type: 

`Strip`

      invalidate_cache(type) 

Invalidate cached images for strip and all dependent strips

  Parameters: 

type (Literal['RAW', 'COMPOSITE']) – Type, Cache Type (never None)

      split(frame, split_method, *, ignore_connections=False) 

Split Strip

  Parameters:  
- frame (int) – Frame where to split the strip (in [-inf, inf]) 
- split_method (Literal['SOFT', 'HARD']) – Split Method, The type of split operation to perform on strips (never None) 
- ignore_connections (bool) – Don’t propagate split to connected strips (optional)   Returns: 

Right side Strip

  Return type: 

`Strip`

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

  
- `bpy.context.active_strip` 
- `bpy.context.selected_editable_strips` 
- `bpy.context.selected_strips` 
- `bpy.context.strip` 
- `bpy.context.strips` 
- [`AddStrip.input_1`](bpy.types.AddStrip.html#bpy.types.AddStrip.input_1) 
- [`AddStrip.input_2`](bpy.types.AddStrip.html#bpy.types.AddStrip.input_2) 
- [`AlphaOverStrip.input_1`](bpy.types.AlphaOverStrip.html#bpy.types.AlphaOverStrip.input_1) 
- [`AlphaOverStrip.input_2`](bpy.types.AlphaOverStrip.html#bpy.types.AlphaOverStrip.input_2) 
- [`AlphaUnderStrip.input_1`](bpy.types.AlphaUnderStrip.html#bpy.types.AlphaUnderStrip.input_1) 
- [`AlphaUnderStrip.input_2`](bpy.types.AlphaUnderStrip.html#bpy.types.AlphaUnderStrip.input_2) 
- [`ColorMixStrip.input_1`](bpy.types.ColorMixStrip.html#bpy.types.ColorMixStrip.input_1) 
- [`ColorMixStrip.input_2`](bpy.types.ColorMixStrip.html#bpy.types.ColorMixStrip.input_2) 
- [`CompositorStrip.input_1`](bpy.types.CompositorStrip.html#bpy.types.CompositorStrip.input_1) 
- [`CompositorStrip.input_2`](bpy.types.CompositorStrip.html#bpy.types.CompositorStrip.input_2) 
- [`CrossStrip.input_1`](bpy.types.CrossStrip.html#bpy.types.CrossStrip.input_1) 
- [`CrossStrip.input_2`](bpy.types.CrossStrip.html#bpy.types.CrossStrip.input_2) 
- [`GammaCrossStrip.input_1`](bpy.types.GammaCrossStrip.html#bpy.types.GammaCrossStrip.input_1) 
- [`GammaCrossStrip.input_2`](bpy.types.GammaCrossStrip.html#bpy.types.GammaCrossStrip.input_2) 
- [`GaussianBlurStrip.input_1`](bpy.types.GaussianBlurStrip.html#bpy.types.GaussianBlurStrip.input_1) 
- [`GlowStrip.input_1`](bpy.types.GlowStrip.html#bpy.types.GlowStrip.input_1) 
- [`MetaStrip.strips`](bpy.types.MetaStrip.html#bpy.types.MetaStrip.strips) 
- [`MultiplyStrip.input_1`](bpy.types.MultiplyStrip.html#bpy.types.MultiplyStrip.input_1) 
- [`MultiplyStrip.input_2`](bpy.types.MultiplyStrip.html#bpy.types.MultiplyStrip.input_2) 
- [`SequenceEditor.active_strip`](bpy.types.SequenceEditor.html#bpy.types.SequenceEditor.active_strip) 
- [`SequenceEditor.display_stack`](bpy.types.SequenceEditor.html#bpy.types.SequenceEditor.display_stack) 
- [`SequenceEditor.meta_stack`](bpy.types.SequenceEditor.html#bpy.types.SequenceEditor.meta_stack) 
- [`SequenceEditor.strips`](bpy.types.SequenceEditor.html#bpy.types.SequenceEditor.strips) 
- [`SequenceEditor.strips_all`](bpy.types.SequenceEditor.html#bpy.types.SequenceEditor.strips_all) 
- [`SpeedControlStrip.input_1`](bpy.types.SpeedControlStrip.html#bpy.types.SpeedControlStrip.input_1) 
- `Strip.connections`   
- `Strip.move_to_meta` 
- `Strip.parent_meta` 
- `Strip.split` 
- `Strip.swap` 
- [`StripModifier.input_mask_strip`](bpy.types.StripModifier.html#bpy.types.StripModifier.input_mask_strip) 
- [`StripsMeta.new_clip`](bpy.types.StripsMeta.html#bpy.types.StripsMeta.new_clip) 
- [`StripsMeta.new_effect`](bpy.types.StripsMeta.html#bpy.types.StripsMeta.new_effect) 
- [`StripsMeta.new_effect`](bpy.types.StripsMeta.html#bpy.types.StripsMeta.new_effect) 
- [`StripsMeta.new_effect`](bpy.types.StripsMeta.html#bpy.types.StripsMeta.new_effect) 
- [`StripsMeta.new_image`](bpy.types.StripsMeta.html#bpy.types.StripsMeta.new_image) 
- [`StripsMeta.new_mask`](bpy.types.StripsMeta.html#bpy.types.StripsMeta.new_mask) 
- [`StripsMeta.new_meta`](bpy.types.StripsMeta.html#bpy.types.StripsMeta.new_meta) 
- [`StripsMeta.new_movie`](bpy.types.StripsMeta.html#bpy.types.StripsMeta.new_movie) 
- [`StripsMeta.new_scene`](bpy.types.StripsMeta.html#bpy.types.StripsMeta.new_scene) 
- [`StripsMeta.new_sound`](bpy.types.StripsMeta.html#bpy.types.StripsMeta.new_sound) 
- [`StripsMeta.remove`](bpy.types.StripsMeta.html#bpy.types.StripsMeta.remove) 
- [`StripsTopLevel.new_clip`](bpy.types.StripsTopLevel.html#bpy.types.StripsTopLevel.new_clip) 
- [`StripsTopLevel.new_effect`](bpy.types.StripsTopLevel.html#bpy.types.StripsTopLevel.new_effect) 
- [`StripsTopLevel.new_effect`](bpy.types.StripsTopLevel.html#bpy.types.StripsTopLevel.new_effect) 
- [`StripsTopLevel.new_effect`](bpy.types.StripsTopLevel.html#bpy.types.StripsTopLevel.new_effect) 
- [`StripsTopLevel.new_image`](bpy.types.StripsTopLevel.html#bpy.types.StripsTopLevel.new_image) 
- [`StripsTopLevel.new_mask`](bpy.types.StripsTopLevel.html#bpy.types.StripsTopLevel.new_mask) 
- [`StripsTopLevel.new_meta`](bpy.types.StripsTopLevel.html#bpy.types.StripsTopLevel.new_meta) 
- [`StripsTopLevel.new_movie`](bpy.types.StripsTopLevel.html#bpy.types.StripsTopLevel.new_movie) 
- [`StripsTopLevel.new_scene`](bpy.types.StripsTopLevel.html#bpy.types.StripsTopLevel.new_scene) 
- [`StripsTopLevel.new_sound`](bpy.types.StripsTopLevel.html#bpy.types.StripsTopLevel.new_sound) 
- [`StripsTopLevel.remove`](bpy.types.StripsTopLevel.html#bpy.types.StripsTopLevel.remove) 
- [`SubtractStrip.input_1`](bpy.types.SubtractStrip.html#bpy.types.SubtractStrip.input_1) 
- [`SubtractStrip.input_2`](bpy.types.SubtractStrip.html#bpy.types.SubtractStrip.input_2) 
- [`WipeStrip.input_1`](bpy.types.WipeStrip.html#bpy.types.WipeStrip.input_1) 
- [`WipeStrip.input_2`](bpy.types.WipeStrip.html#bpy.types.WipeStrip.input_2)
