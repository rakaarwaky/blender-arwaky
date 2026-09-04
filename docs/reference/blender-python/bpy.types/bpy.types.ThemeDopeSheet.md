# bpy.types.ThemeDopeSheet

# ThemeDopeSheet(bpy_struct)

 

base class — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct)

   class bpy.types.ThemeDopeSheet(bpy_struct) 

Theme settings for the Dope Sheet

   anim_interpolation_constant 

Color of lines showing constant interpolation mode (array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

  Type: 

[`bpy_prop_array`](bpy.types.bpy_prop_array.html#bpy.types.bpy_prop_array)[float]

      anim_interpolation_linear 

Color of lines showing linear interpolation mode (array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

  Type: 

[`bpy_prop_array`](bpy.types.bpy_prop_array.html#bpy.types.bpy_prop_array)[float]

      anim_interpolation_other 

Color of lines showing easings & dynamic interpolation mode (array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

  Type: 

[`bpy_prop_array`](bpy.types.bpy_prop_array.html#bpy.types.bpy_prop_array)[float]

      grid 

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

  Type: 

[`mathutils.Color`](mathutils.html#mathutils.Color)

      keyframe_border 

Color of keyframe border (array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

  Type: 

[`bpy_prop_array`](bpy.types.bpy_prop_array.html#bpy.types.bpy_prop_array)[float]

      keyframe_border_selected 

Color of selected keyframe border (array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

  Type: 

[`bpy_prop_array`](bpy.types.bpy_prop_array.html#bpy.types.bpy_prop_array)[float]

      keyframe_scale_factor 

Scale factor for adjusting the height of keyframes (in [0.8, 5], default 1.0)

  Type: 

float

      simulated_frames 

(array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

  Type: 

[`bpy_prop_array`](bpy.types.bpy_prop_array.html#bpy.types.bpy_prop_array)[float]

      space 

Settings for space (readonly, never None)

  Type: 

[`ThemeSpaceGeneric`](bpy.types.ThemeSpaceGeneric.html#bpy.types.ThemeSpaceGeneric)

      summary 

Color of summary channel (array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

  Type: 

[`bpy_prop_array`](bpy.types.bpy_prop_array.html#bpy.types.bpy_prop_array)[float]

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

  
- [`Theme.dopesheet_editor`](bpy.types.Theme.html#bpy.types.Theme.dopesheet_editor)
