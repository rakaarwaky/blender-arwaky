# bpy.types.LineStyleAlphaModifier_Noise

# LineStyleAlphaModifier_Noise(LineStyleAlphaModifier)

 

base classes — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct), [`LineStyleModifier`](bpy.types.LineStyleModifier.html#bpy.types.LineStyleModifier), [`LineStyleAlphaModifier`](bpy.types.LineStyleAlphaModifier.html#bpy.types.LineStyleAlphaModifier)

   class bpy.types.LineStyleAlphaModifier_Noise(LineStyleAlphaModifier) 

Alpha transparency based on random noise

   amplitude 

Amplitude of the noise (in [-inf, inf], default 0.0)

  Type: 

float

      blend 

Specify how the modifier value is blended into the base value (default `'MIX'`)

  Type: 

Literal[‘MIX’, ‘ADD’, ‘SUBTRACT’, ‘MULTIPLY’, ‘DIVIDE’, ‘DIFFERENCE’, ‘MINIMUM’, ‘MAXIMUM’]

      curve 

Curve used for the curve mapping (readonly)

  Type: 

[`CurveMapping`](bpy.types.CurveMapping.html#bpy.types.CurveMapping) | None

      expanded 

True if the modifier tab is expanded (default False)

  Type: 

bool

      influence 

Influence factor by which the modifier changes the property (in [0, 1], default 0.0)

  Type: 

float

      invert 

Invert the fade-out direction of the linear mapping (default False)

  Type: 

bool

      mapping 

Select the mapping type (default `'LINEAR'`)

  
- `LINEAR` Linear – Use linear mapping. 
- `CURVE` Curve – Use curve mapping.   Type: 

Literal[‘LINEAR’, ‘CURVE’]

      period 

Period of the noise (in [-inf, inf], default 0.0)

  Type: 

float

      seed 

Seed for the noise generation (in [1, 32767], default 0)

  Type: 

int

      type 

Type of the modifier (default `'ALONG_STROKE'`, readonly)

  Type: 

Literal[[Linestyle Alpha Modifier Type Items](bpy_types_enum_items/linestyle_alpha_modifier_type_items.html#rna-enum-linestyle-alpha-modifier-type-items)]

      use 

Enable or disable this modifier during stroke rendering (default False)

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
- [`LineStyleAlphaModifier.name`](bpy.types.LineStyleAlphaModifier.html#bpy.types.LineStyleAlphaModifier.name)     

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
- [`LineStyleModifier.bl_rna_get_subclass`](bpy.types.LineStyleModifier.html#bpy.types.LineStyleModifier.bl_rna_get_subclass) 
- [`LineStyleModifier.bl_rna_get_subclass_py`](bpy.types.LineStyleModifier.html#bpy.types.LineStyleModifier.bl_rna_get_subclass_py) 
- [`LineStyleAlphaModifier.bl_rna_get_subclass`](bpy.types.LineStyleAlphaModifier.html#bpy.types.LineStyleAlphaModifier.bl_rna_get_subclass) 
- [`LineStyleAlphaModifier.bl_rna_get_subclass_py`](bpy.types.LineStyleAlphaModifier.html#bpy.types.LineStyleAlphaModifier.bl_rna_get_subclass_py)
