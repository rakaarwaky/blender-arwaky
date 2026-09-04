# bpy.types.KeyingSet

# KeyingSet(bpy_struct)

 

base class — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct)

   class bpy.types.KeyingSet(bpy_struct) 

Settings that should be keyframed together

   bl_description 

A short description of the keying set (default “”, never None)

  Type: 

str

      bl_idname 

If this is set, the Keying Set gets a custom ID, otherwise it takes the name of the class used to define the Keying Set (for example, if the class name is “BUILTIN_KSI_location”, and bl_idname is not set by the script, then bl_idname = “BUILTIN_KSI_location”) (default “”, never None)

  Type: 

str

      bl_label 

(default “”, never None)

  Type: 

str

      is_path_absolute 

Keying Set defines specific paths/settings to be keyframed (i.e. is not reliant on context info) (default False, readonly)

  Type: 

bool

      paths 

Keying Set Paths to define settings that get keyframed together (default None, readonly)

  Type: 

[`KeyingSetPaths`](bpy.types.KeyingSetPaths.html#bpy.types.KeyingSetPaths)[[`KeyingSetPath`](bpy.types.KeyingSetPath.html#bpy.types.KeyingSetPath)]

      type_info 

Callback function defines for built-in Keying Sets (readonly)

  Type: 

[`KeyingSetInfo`](bpy.types.KeyingSetInfo.html#bpy.types.KeyingSetInfo) | None

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

      refresh() 

Refresh Keying Set to ensure that it is valid for the current context (call before each use of one)

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

  
- [`KeyingSetInfo.generate`](bpy.types.KeyingSetInfo.html#bpy.types.KeyingSetInfo.generate) 
- [`KeyingSetInfo.iterator`](bpy.types.KeyingSetInfo.html#bpy.types.KeyingSetInfo.iterator) 
- [`KeyingSets.active`](bpy.types.KeyingSets.html#bpy.types.KeyingSets.active) 
- [`KeyingSets.new`](bpy.types.KeyingSets.html#bpy.types.KeyingSets.new)   
- [`KeyingSetsAll.active`](bpy.types.KeyingSetsAll.html#bpy.types.KeyingSetsAll.active) 
- [`Scene.keying_sets`](bpy.types.Scene.html#bpy.types.Scene.keying_sets) 
- [`Scene.keying_sets_all`](bpy.types.Scene.html#bpy.types.Scene.keying_sets_all)
