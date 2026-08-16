# bpy.types.SequencerTimelineOverlay

# SequencerTimelineOverlay(bpy_struct)

 

base class — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct)

   class bpy.types.SequencerTimelineOverlay(bpy_struct)   show_fcurves 

Display strip opacity/volume curve (default False)

  Type: 

bool

      show_grid 

Show vertical grid lines (default False)

  Type: 

bool

      show_strip_duration 

(default False)

  Type: 

bool

      show_strip_name 

(default False)

  Type: 

bool

      show_strip_offset 

Display strip in/out offsets (default False)

  Type: 

bool

      show_strip_retiming 

Display retiming keys on top of strips (default False)

  Type: 

bool

      show_strip_source 

Display path to source file, or name of source data-block (default False)

  Type: 

bool

      show_strip_tag_color 

Display the strip color tags in the sequencer (default False)

  Type: 

bool

      thumbnail_display_style 

How thumbnails are displayed (default `'NO_THUMBNAILS'`)

  
- `NO_THUMBNAILS` None – Do not show strip thumbnails. 
- `STRIP_ENDS` Strip Ends – Show thumbnails only at the beginning and end of the strip. 
- `CONTINUOUS` Continuous – Display thumbnails as a filmstrip.   Type: 

Literal[‘NO_THUMBNAILS’, ‘STRIP_ENDS’, ‘CONTINUOUS’]

      waveform_display_style 

How Waveforms are displayed (default `'FULL_WAVEFORMS'`)

  
- `FULL_WAVEFORMS` Full – Display full waveform. 
- `HALF_WAVEFORMS` Half – Display upper half of the absolute value waveform.   Type: 

Literal[‘FULL_WAVEFORMS’, ‘HALF_WAVEFORMS’]

      waveform_display_type 

How Waveforms are displayed (default `'DEFAULT_WAVEFORMS'`)

  
- `ALL_WAVEFORMS` On – Display waveforms for all sound strips. 
- `DEFAULT_WAVEFORMS` Strip – Display waveforms depending on strip setting. 
- `NO_WAVEFORMS` Off – Don’t display waveforms for any sound strips.   Type: 

Literal[‘ALL_WAVEFORMS’, ‘DEFAULT_WAVEFORMS’, ‘NO_WAVEFORMS’]

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

  
- [`SpaceSequenceEditor.timeline_overlay`](bpy.types.SpaceSequenceEditor.html#bpy.types.SpaceSequenceEditor.timeline_overlay)
