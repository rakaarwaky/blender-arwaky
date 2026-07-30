# bpy.types.SoundEqualizerModifier

# SoundEqualizerModifier(StripModifier)

 

base classes — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct), [`StripModifier`](bpy.types.StripModifier.html#bpy.types.StripModifier)

   class bpy.types.SoundEqualizerModifier(StripModifier) 

Equalize audio

   graphics 

Graphical definition equalization (default None, readonly)

  Type: 

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.html#bpy.types.bpy_prop_collection)[[`EQCurveMappingData`](bpy.types.EQCurveMappingData.html#bpy.types.EQCurveMappingData)]

      new_graphic(min_freq, max_freq) 

Add a new EQ band

  Parameters:  
- min_freq (float) – Minimum Frequency, Minimum Frequency (in [0, 20000]) 
- max_freq (float) – Maximum Frequency, Maximum Frequency (in [0, 20000])   Returns: 

Newly created graphical Equalizer definition

  Return type: 

[`EQCurveMappingData`](bpy.types.EQCurveMappingData.html#bpy.types.EQCurveMappingData)

      clear_soundeqs() 

Remove all graphical equalizers from the Equalizer modifier

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
- [`StripModifier.name`](bpy.types.StripModifier.html#bpy.types.StripModifier.name) 
- [`StripModifier.type`](bpy.types.StripModifier.html#bpy.types.StripModifier.type) 
- [`StripModifier.mute`](bpy.types.StripModifier.html#bpy.types.StripModifier.mute) 
- [`StripModifier.enable`](bpy.types.StripModifier.html#bpy.types.StripModifier.enable) 
- [`StripModifier.show_preview`](bpy.types.StripModifier.html#bpy.types.StripModifier.show_preview)   
- [`StripModifier.show_expanded`](bpy.types.StripModifier.html#bpy.types.StripModifier.show_expanded) 
- [`StripModifier.input_mask_type`](bpy.types.StripModifier.html#bpy.types.StripModifier.input_mask_type) 
- [`StripModifier.mask_time`](bpy.types.StripModifier.html#bpy.types.StripModifier.mask_time) 
- [`StripModifier.input_mask_strip`](bpy.types.StripModifier.html#bpy.types.StripModifier.input_mask_strip) 
- [`StripModifier.input_mask_id`](bpy.types.StripModifier.html#bpy.types.StripModifier.input_mask_id) 
- [`StripModifier.is_active`](bpy.types.StripModifier.html#bpy.types.StripModifier.is_active)     

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
- [`StripModifier.bl_rna_get_subclass`](bpy.types.StripModifier.html#bpy.types.StripModifier.bl_rna_get_subclass) 
- [`StripModifier.bl_rna_get_subclass_py`](bpy.types.StripModifier.html#bpy.types.StripModifier.bl_rna_get_subclass_py)
