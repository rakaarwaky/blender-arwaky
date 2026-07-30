# bpy.types.StripModifier

# StripModifier(bpy_struct)

 

base class — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct)

  

Subclasses

  
- [BrightContrastModifier(StripModifier)](bpy.types.BrightContrastModifier.html) 
- [ColorBalanceModifier(StripModifier)](bpy.types.ColorBalanceModifier.html) 
- [CurvesModifier(StripModifier)](bpy.types.CurvesModifier.html) 
- [EchoModifier(StripModifier)](bpy.types.EchoModifier.html) 
- [HueCorrectModifier(StripModifier)](bpy.types.HueCorrectModifier.html) 
- [MaskStripModifier(StripModifier)](bpy.types.MaskStripModifier.html) 
- [PitchModifier(StripModifier)](bpy.types.PitchModifier.html) 
- [SequencerCompositorModifierData(StripModifier)](bpy.types.SequencerCompositorModifierData.html) 
- [SequencerTonemapModifierData(StripModifier)](bpy.types.SequencerTonemapModifierData.html) 
- [SoundEqualizerModifier(StripModifier)](bpy.types.SoundEqualizerModifier.html) 
- [WhiteBalanceModifier(StripModifier)](bpy.types.WhiteBalanceModifier.html)     class bpy.types.StripModifier(bpy_struct) 

Modifier for sequence strip

   enable 

Use modifier during render (default True)

  Type: 

bool

      input_mask_id 

Mask ID used as mask input for the modifier

  Type: 

[`Mask`](bpy.types.Mask.html#bpy.types.Mask) | None

      input_mask_strip 

Strip used as mask input for the modifier

  Type: 

[`Strip`](bpy.types.Strip.html#bpy.types.Strip) | None

      input_mask_type 

Type of input data used for mask (default `'STRIP'`)

  
- `STRIP` Strip – Use sequencer strip as mask input. 
- `ID` Mask – Use mask ID as mask input.   Type: 

Literal[‘STRIP’, ‘ID’]

      is_active 

This modifier is active (default False)

  Type: 

bool

      mask_time 

Time to use for the Mask animation (default `'RELATIVE'`)

  
- `RELATIVE` Relative – Mask animation is offset to start of strip. 
- `ABSOLUTE` Absolute – Mask animation is in sync with scene frame.   Type: 

Literal[‘RELATIVE’, ‘ABSOLUTE’]

      mute 

Mute this modifier (default False)

  Type: 

bool

      name 

(default “”, never None)

  Type: 

str

      show_expanded 

Mute expanded settings for the modifier (default False)

  Type: 

bool

      show_preview 

Display modifier in preview (default False)

  Type: 

bool

      type 

(default `'BRIGHT_CONTRAST'`, readonly)

  Type: 

Literal[[Strip Modifier Type Items](bpy_types_enum_items/strip_modifier_type_items.html#rna-enum-strip-modifier-type-items)]

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

  
- `bpy.context.strip_modifier` 
- [`Strip.modifiers`](bpy.types.Strip.html#bpy.types.Strip.modifiers) 
- [`StripModifiers.active`](bpy.types.StripModifiers.html#bpy.types.StripModifiers.active)   
- [`StripModifiers.new`](bpy.types.StripModifiers.html#bpy.types.StripModifiers.new) 
- [`StripModifiers.remove`](bpy.types.StripModifiers.html#bpy.types.StripModifiers.remove)
