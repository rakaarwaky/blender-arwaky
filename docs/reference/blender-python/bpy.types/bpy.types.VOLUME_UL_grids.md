# bpy.types.VOLUME_UL_grids

# VOLUME_UL_grids(UIList)

 

base classes — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct), [`UIList`](bpy.types.UIList.html#bpy.types.UIList)

   class bpy.types.VOLUME_UL_grids(UIList)   classmethod bl_rna_get_subclass(id, default=None, /)  Parameters:  
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
- [`UIList.bl_idname`](bpy.types.UIList.html#bpy.types.UIList.bl_idname) 
- [`UIList.list_id`](bpy.types.UIList.html#bpy.types.UIList.list_id) 
- [`UIList.layout_type`](bpy.types.UIList.html#bpy.types.UIList.layout_type) 
- [`UIList.use_filter_show`](bpy.types.UIList.html#bpy.types.UIList.use_filter_show) 
- [`UIList.filter_name`](bpy.types.UIList.html#bpy.types.UIList.filter_name)   
- [`UIList.use_filter_invert`](bpy.types.UIList.html#bpy.types.UIList.use_filter_invert) 
- [`UIList.use_filter_sort_alpha`](bpy.types.UIList.html#bpy.types.UIList.use_filter_sort_alpha) 
- [`UIList.use_filter_sort_reverse`](bpy.types.UIList.html#bpy.types.UIList.use_filter_sort_reverse) 
- [`UIList.use_filter_sort_lock`](bpy.types.UIList.html#bpy.types.UIList.use_filter_sort_lock) 
- [`UIList.bitflag_filter_item`](bpy.types.UIList.html#bpy.types.UIList.bitflag_filter_item) 
- [`UIList.bitflag_item_never_show`](bpy.types.UIList.html#bpy.types.UIList.bitflag_item_never_show)     

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
- [`UIList.bl_system_properties_get`](bpy.types.UIList.html#bpy.types.UIList.bl_system_properties_get) 
- [`UIList.draw_item`](bpy.types.UIList.html#bpy.types.UIList.draw_item) 
- [`UIList.draw_filter`](bpy.types.UIList.html#bpy.types.UIList.draw_filter) 
- [`UIList.filter_items`](bpy.types.UIList.html#bpy.types.UIList.filter_items) 
- [`UIList.append`](bpy.types.UIList.html#bpy.types.UIList.append) 
- [`UIList.is_extended`](bpy.types.UIList.html#bpy.types.UIList.is_extended) 
- [`UIList.prepend`](bpy.types.UIList.html#bpy.types.UIList.prepend) 
- [`UIList.remove`](bpy.types.UIList.html#bpy.types.UIList.remove) 
- [`UIList.bl_rna_get_subclass`](bpy.types.UIList.html#bpy.types.UIList.bl_rna_get_subclass) 
- [`UIList.bl_rna_get_subclass_py`](bpy.types.UIList.html#bpy.types.UIList.bl_rna_get_subclass_py)
