# bpy.types.FModifier

# FModifier(bpy_struct)

 

base class — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct)

  

Subclasses

  
- [FModifierCycles(FModifier)](bpy.types.FModifierCycles.html) 
- [FModifierEnvelope(FModifier)](bpy.types.FModifierEnvelope.html) 
- [FModifierFunctionGenerator(FModifier)](bpy.types.FModifierFunctionGenerator.html) 
- [FModifierGenerator(FModifier)](bpy.types.FModifierGenerator.html) 
- [FModifierLimits(FModifier)](bpy.types.FModifierLimits.html) 
- [FModifierNoise(FModifier)](bpy.types.FModifierNoise.html) 
- [FModifierSmooth(FModifier)](bpy.types.FModifierSmooth.html) 
- [FModifierStepped(FModifier)](bpy.types.FModifierStepped.html)     class bpy.types.FModifier(bpy_struct) 

Modifier for values of F-Curve

   active 

F-Curve modifier will show settings in the editor (default False)

  Type: 

bool

      blend_in 

Number of frames from start frame for influence to take effect (in [-inf, inf], default 0.0)

  Type: 

float

      blend_out 

Number of frames from end frame for influence to fade out (in [-inf, inf], default 0.0)

  Type: 

float

      frame_end 

Frame that modifier’s influence ends (if Restrict Frame Range is in use) (in [-inf, inf], default 0.0)

  Type: 

float

      frame_start 

Frame that modifier’s influence starts (if Restrict Frame Range is in use) (in [-inf, inf], default 0.0)

  Type: 

float

      influence 

Amount of influence F-Curve Modifier will have when not fading in/out (in [0, 1], default 1.0)

  Type: 

float

      is_valid 

F-Curve Modifier has invalid settings and will not be evaluated (default True, readonly)

  Type: 

bool

      mute 

Enable F-Curve modifier evaluation (default False)

  Type: 

bool

      name 

F-Curve Modifier name (default “”, never None)

  Type: 

str

      show_expanded 

F-Curve Modifier’s panel is expanded in UI (default False)

  Type: 

bool

      type 

F-Curve Modifier Type (default `'NULL'`, readonly)

  Type: 

Literal[[Fmodifier Type Items](bpy_types_enum_items/fmodifier_type_items.html#rna-enum-fmodifier-type-items)]

      use_influence 

F-Curve Modifier’s effects will be tempered by a default factor (default False)

  Type: 

bool

      use_restricted_range 

F-Curve Modifier is only applied for the specified frame range to help mask off effects in order to chain them (default False)

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

  
- [`FCurve.modifiers`](bpy.types.FCurve.html#bpy.types.FCurve.modifiers) 
- [`FCurveModifiers.active`](bpy.types.FCurveModifiers.html#bpy.types.FCurveModifiers.active) 
- [`FCurveModifiers.new`](bpy.types.FCurveModifiers.html#bpy.types.FCurveModifiers.new)   
- [`FCurveModifiers.remove`](bpy.types.FCurveModifiers.html#bpy.types.FCurveModifiers.remove) 
- [`NlaStrip.modifiers`](bpy.types.NlaStrip.html#bpy.types.NlaStrip.modifiers)
