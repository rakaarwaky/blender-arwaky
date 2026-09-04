# bpy.types.KeyingSetPaths

# KeyingSetPaths(bpy_prop_collection)

 

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.html#bpy.types.bpy_prop_collection)

   class bpy.types.KeyingSetPaths(bpy_prop_collection) 

Collection of keying set paths

   active 

Active Keying Set used to insert/delete keyframes

  Type: 

[`KeyingSetPath`](bpy.types.KeyingSetPath.html#bpy.types.KeyingSetPath) | None

      active_index 

Current Keying Set index (in [-inf, inf], default 0)

  Type: 

int

      add(target_id, data_path, *, index=-1, group_method='KEYINGSET', group_name='') 

Add a new path for the Keying Set

  Parameters:  
- target_id ([`ID`](bpy.types.ID.html#bpy.types.ID) | None) – Target ID, ID data-block for the destination 
- data_path (str) – Data-Path, RNA-Path to destination property (never None) 
- index (int) – Index, The index of the destination property (i.e. axis of Location/Rotation/etc.), or -1 for the entire array (in [-1, inf], optional) 
- group_method (Literal[[Keyingset Path Grouping Items](bpy_types_enum_items/keyingset_path_grouping_items.html#rna-enum-keyingset-path-grouping-items)]) – Grouping Method, Method used to define which Group-name to use (optional) 
- group_name (str) – Group Name, Name of Action Group to assign destination to (only if grouping mode is to use this name) (optional, never None)   Returns: 

New Path, Path created and added to the Keying Set

  Return type: 

[`KeyingSetPath`](bpy.types.KeyingSetPath.html#bpy.types.KeyingSetPath)

      remove(path) 

Remove the given path from the Keying Set

  Parameters: 

path ([`KeyingSetPath`](bpy.types.KeyingSetPath.html#bpy.types.KeyingSetPath) | None) – Path, (never None)

      clear() 

Remove all the paths from the Keying Set

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

  
- [`KeyingSet.paths`](bpy.types.KeyingSet.html#bpy.types.KeyingSet.paths)
