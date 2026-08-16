# bpy.types.StripColorBalance

# StripColorBalance(StripColorBalanceData)

 

base classes — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct), [`StripColorBalanceData`](bpy.types.StripColorBalanceData.html#bpy.types.StripColorBalanceData)

   class bpy.types.StripColorBalance(StripColorBalanceData) 

Color balance parameters for a sequence strip

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
- [`StripColorBalanceData.correction_method`](bpy.types.StripColorBalanceData.html#bpy.types.StripColorBalanceData.correction_method) 
- [`StripColorBalanceData.lift`](bpy.types.StripColorBalanceData.html#bpy.types.StripColorBalanceData.lift) 
- [`StripColorBalanceData.gamma`](bpy.types.StripColorBalanceData.html#bpy.types.StripColorBalanceData.gamma) 
- [`StripColorBalanceData.gain`](bpy.types.StripColorBalanceData.html#bpy.types.StripColorBalanceData.gain) 
- [`StripColorBalanceData.slope`](bpy.types.StripColorBalanceData.html#bpy.types.StripColorBalanceData.slope) 
- [`StripColorBalanceData.offset`](bpy.types.StripColorBalanceData.html#bpy.types.StripColorBalanceData.offset)   
- [`StripColorBalanceData.power`](bpy.types.StripColorBalanceData.html#bpy.types.StripColorBalanceData.power) 
- [`StripColorBalanceData.invert_lift`](bpy.types.StripColorBalanceData.html#bpy.types.StripColorBalanceData.invert_lift) 
- [`StripColorBalanceData.invert_gamma`](bpy.types.StripColorBalanceData.html#bpy.types.StripColorBalanceData.invert_gamma) 
- [`StripColorBalanceData.invert_gain`](bpy.types.StripColorBalanceData.html#bpy.types.StripColorBalanceData.invert_gain) 
- [`StripColorBalanceData.invert_slope`](bpy.types.StripColorBalanceData.html#bpy.types.StripColorBalanceData.invert_slope) 
- [`StripColorBalanceData.invert_offset`](bpy.types.StripColorBalanceData.html#bpy.types.StripColorBalanceData.invert_offset) 
- [`StripColorBalanceData.invert_power`](bpy.types.StripColorBalanceData.html#bpy.types.StripColorBalanceData.invert_power)     

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
- [`StripColorBalanceData.bl_rna_get_subclass`](bpy.types.StripColorBalanceData.html#bpy.types.StripColorBalanceData.bl_rna_get_subclass) 
- [`StripColorBalanceData.bl_rna_get_subclass_py`](bpy.types.StripColorBalanceData.html#bpy.types.StripColorBalanceData.bl_rna_get_subclass_py)
