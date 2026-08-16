# bpy.types.ThemeSpaceGeneric

# ThemeSpaceGeneric(bpy_struct)

 

base class — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct)

   class bpy.types.ThemeSpaceGeneric(bpy_struct)   back 

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

  Type: 

[`mathutils.Color`](mathutils.html#mathutils.Color)

      header 

(array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

  Type: 

[`bpy_prop_array`](bpy.types.bpy_prop_array.html#bpy.types.bpy_prop_array)[float]

      header_text 

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

  Type: 

[`mathutils.Color`](mathutils.html#mathutils.Color)

      header_text_hi 

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

  Type: 

[`mathutils.Color`](mathutils.html#mathutils.Color)

      text 

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

  Type: 

[`mathutils.Color`](mathutils.html#mathutils.Color)

      text_hi 

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

  Type: 

[`mathutils.Color`](mathutils.html#mathutils.Color)

      title 

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

  Type: 

[`mathutils.Color`](mathutils.html#mathutils.Color)

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

  
- [`ThemeClipEditor.space`](bpy.types.ThemeClipEditor.html#bpy.types.ThemeClipEditor.space) 
- [`ThemeConsole.space`](bpy.types.ThemeConsole.html#bpy.types.ThemeConsole.space) 
- [`ThemeDopeSheet.space`](bpy.types.ThemeDopeSheet.html#bpy.types.ThemeDopeSheet.space) 
- [`ThemeFileBrowser.space`](bpy.types.ThemeFileBrowser.html#bpy.types.ThemeFileBrowser.space) 
- [`ThemeGraphEditor.space`](bpy.types.ThemeGraphEditor.html#bpy.types.ThemeGraphEditor.space) 
- [`ThemeImageEditor.space`](bpy.types.ThemeImageEditor.html#bpy.types.ThemeImageEditor.space) 
- [`ThemeInfo.space`](bpy.types.ThemeInfo.html#bpy.types.ThemeInfo.space) 
- [`ThemeNLAEditor.space`](bpy.types.ThemeNLAEditor.html#bpy.types.ThemeNLAEditor.space) 
- [`ThemeNodeEditor.space`](bpy.types.ThemeNodeEditor.html#bpy.types.ThemeNodeEditor.space)   
- [`ThemeOutliner.space`](bpy.types.ThemeOutliner.html#bpy.types.ThemeOutliner.space) 
- [`ThemePreferences.space`](bpy.types.ThemePreferences.html#bpy.types.ThemePreferences.space) 
- [`ThemeProperties.space`](bpy.types.ThemeProperties.html#bpy.types.ThemeProperties.space) 
- [`ThemeSequenceEditor.space`](bpy.types.ThemeSequenceEditor.html#bpy.types.ThemeSequenceEditor.space) 
- [`ThemeSpreadsheet.space`](bpy.types.ThemeSpreadsheet.html#bpy.types.ThemeSpreadsheet.space) 
- [`ThemeStatusBar.space`](bpy.types.ThemeStatusBar.html#bpy.types.ThemeStatusBar.space) 
- [`ThemeTextEditor.space`](bpy.types.ThemeTextEditor.html#bpy.types.ThemeTextEditor.space) 
- [`ThemeTopBar.space`](bpy.types.ThemeTopBar.html#bpy.types.ThemeTopBar.space)
