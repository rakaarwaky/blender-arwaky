# bpy.types.KeyingSetPath

# KeyingSetPath(bpy_struct)

 

base class — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct)

   class bpy.types.KeyingSetPath(bpy_struct) 

Path to a setting for use in a Keying Set

   array_index 

Index to the specific setting if applicable (in [-inf, inf], default 0)

  Type: 

int

      data_path 

Path to property setting (default “”, never None)

  Type: 

str

      group 

Name of Action Group to assign setting(s) for this path to (default “”, never None)

  Type: 

str

      group_method 

Method used to define which Group-name to use (default `'NAMED'`)

  Type: 

Literal[[Keyingset Path Grouping Items](bpy_types_enum_items/keyingset_path_grouping_items.html#rna-enum-keyingset-path-grouping-items)]

      id 

ID-Block that keyframes for Keying Set should be added to (for Absolute Keying Sets only)

  Type: 

[`ID`](bpy.types.ID.html#bpy.types.ID) | None

      id_type 

Type of ID-block that can be used (default `'OBJECT'`)

  Type: 

Literal[[Id Type Items](bpy_types_enum_items/id_type_items.html#rna-enum-id-type-items)]

      use_entire_array 

When an ‘array/vector’ type is chosen (Location, Rotation, Color, etc.), entire array is to be used (default False)

  Type: 

bool

      use_insertkey_needed 

Only insert keyframes where they’re needed in the relevant F-Curves (default False)

  Type: 

bool

      use_insertkey_override_needed 

Override default setting to only insert keyframes where they’re needed in the relevant F-Curves (default False)

  Type: 

bool

      use_insertkey_override_visual 

Override default setting to insert keyframes based on ‘visual transforms’ (default False)

  Type: 

bool

      use_insertkey_visual 

Insert keyframes based on ‘visual transforms’ (default False)

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

  
- [`KeyingSet.paths`](bpy.types.KeyingSet.html#bpy.types.KeyingSet.paths) 
- [`KeyingSetPaths.active`](bpy.types.KeyingSetPaths.html#bpy.types.KeyingSetPaths.active)   
- [`KeyingSetPaths.add`](bpy.types.KeyingSetPaths.html#bpy.types.KeyingSetPaths.add) 
- [`KeyingSetPaths.remove`](bpy.types.KeyingSetPaths.html#bpy.types.KeyingSetPaths.remove)
