# bpy.types.FModifierCycles

# FModifierCycles(FModifier)

 

base classes — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct), [`FModifier`](bpy.types.FModifier.html#bpy.types.FModifier)

   class bpy.types.FModifierCycles(FModifier) 

Repeat the values of the modified F-Curve

   cycles_after 

Maximum number of cycles to allow after last keyframe (0 = infinite) (in [-32768, 32767], default 0)

  Type: 

int

      cycles_before 

Maximum number of cycles to allow before first keyframe (0 = infinite) (in [-32768, 32767], default 0)

  Type: 

int

      mode_after 

Cycling mode to use after last keyframe (default `'NONE'`)

  
- `NONE` No Cycles – Don’t do anything. 
- `REPEAT` Repeat Motion – Repeat keyframe range as-is. 
- `REPEAT_OFFSET` Repeat with Offset – Repeat keyframe range, but with offset based on gradient between start and end values. 
- `MIRROR` Repeat Mirrored – Alternate between forward and reverse playback of keyframe range.   Type: 

Literal[‘NONE’, ‘REPEAT’, ‘REPEAT_OFFSET’, ‘MIRROR’]

      mode_before 

Cycling mode to use before first keyframe (default `'NONE'`)

  
- `NONE` No Cycles – Don’t do anything. 
- `REPEAT` Repeat Motion – Repeat keyframe range as-is. 
- `REPEAT_OFFSET` Repeat with Offset – Repeat keyframe range, but with offset based on gradient between start and end values. 
- `MIRROR` Repeat Mirrored – Alternate between forward and reverse playback of keyframe range.   Type: 

Literal[‘NONE’, ‘REPEAT’, ‘REPEAT_OFFSET’, ‘MIRROR’]

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
- [`FModifier.name`](bpy.types.FModifier.html#bpy.types.FModifier.name) 
- [`FModifier.type`](bpy.types.FModifier.html#bpy.types.FModifier.type) 
- [`FModifier.show_expanded`](bpy.types.FModifier.html#bpy.types.FModifier.show_expanded) 
- [`FModifier.mute`](bpy.types.FModifier.html#bpy.types.FModifier.mute) 
- [`FModifier.is_valid`](bpy.types.FModifier.html#bpy.types.FModifier.is_valid) 
- [`FModifier.active`](bpy.types.FModifier.html#bpy.types.FModifier.active)   
- [`FModifier.use_restricted_range`](bpy.types.FModifier.html#bpy.types.FModifier.use_restricted_range) 
- [`FModifier.frame_start`](bpy.types.FModifier.html#bpy.types.FModifier.frame_start) 
- [`FModifier.frame_end`](bpy.types.FModifier.html#bpy.types.FModifier.frame_end) 
- [`FModifier.blend_in`](bpy.types.FModifier.html#bpy.types.FModifier.blend_in) 
- [`FModifier.blend_out`](bpy.types.FModifier.html#bpy.types.FModifier.blend_out) 
- [`FModifier.use_influence`](bpy.types.FModifier.html#bpy.types.FModifier.use_influence) 
- [`FModifier.influence`](bpy.types.FModifier.html#bpy.types.FModifier.influence)     

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
- [`FModifier.bl_rna_get_subclass`](bpy.types.FModifier.html#bpy.types.FModifier.bl_rna_get_subclass) 
- [`FModifier.bl_rna_get_subclass_py`](bpy.types.FModifier.html#bpy.types.FModifier.bl_rna_get_subclass_py)
