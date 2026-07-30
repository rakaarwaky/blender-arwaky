# bpy.types.FModifierStepped

# FModifierStepped(FModifier)

 

base classes — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct), [`FModifier`](bpy.types.FModifier.html#bpy.types.FModifier)

   class bpy.types.FModifierStepped(FModifier) 

Hold each interpolated value from the F-Curve for several frames without changing the timing

   frame_end 

Frame that modifier’s influence ends (if applicable) (in [-inf, inf], default 0.0)

  Type: 

float

      frame_offset 

Reference number of frames before frames get held (use to get hold for ‘1-3’ vs ‘5-7’ holding patterns) (in [-inf, inf], default 0.0)

  Type: 

float

      frame_start 

Frame that modifier’s influence starts (if applicable) (in [-inf, inf], default 0.0)

  Type: 

float

      frame_step 

Number of frames to hold each value (in [-inf, inf], default 2.0)

  Type: 

float

      use_frame_end 

Restrict modifier to only act before its ‘end’ frame (default False)

  Type: 

bool

      use_frame_start 

Restrict modifier to only act after its ‘start’ frame (default False)

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
