# bpy.types.XrActionMaps

# XrActionMaps(bpy_prop_collection)

 

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.html#bpy.types.bpy_prop_collection)

   class bpy.types.XrActionMaps(bpy_prop_collection) 

Collection of XR action maps

   classmethod new(xr_session_state, name, replace_existing) 

new

  Parameters:  
- xr_session_state ([`XrSessionState`](bpy.types.XrSessionState.html#bpy.types.XrSessionState) | None) – XR Session State, (never None) 
- name (str) – Name, (never None) 
- replace_existing (bool) – Replace Existing, Replace any existing actionmap with the same name   Returns: 

Action Map, Added action map

  Return type: 

[`XrActionMap`](bpy.types.XrActionMap.html#bpy.types.XrActionMap)

      classmethod new_from_actionmap(xr_session_state, actionmap) 

new_from_actionmap

  Parameters:  
- xr_session_state ([`XrSessionState`](bpy.types.XrSessionState.html#bpy.types.XrSessionState) | None) – XR Session State, (never None) 
- actionmap ([`XrActionMap`](bpy.types.XrActionMap.html#bpy.types.XrActionMap) | None) – Action Map, Action map to use as a reference (never None)   Returns: 

Action Map, Added action map

  Return type: 

[`XrActionMap`](bpy.types.XrActionMap.html#bpy.types.XrActionMap)

      classmethod remove(xr_session_state, actionmap) 

remove

  Parameters:  
- xr_session_state ([`XrSessionState`](bpy.types.XrSessionState.html#bpy.types.XrSessionState) | None) – XR Session State, (never None) 
- actionmap ([`XrActionMap`](bpy.types.XrActionMap.html#bpy.types.XrActionMap) | None) – Action Map, Removed action map (never None)       classmethod find(xr_session_state, name) 

find

  Parameters:  
- xr_session_state ([`XrSessionState`](bpy.types.XrSessionState.html#bpy.types.XrSessionState) | None) – XR Session State, (never None) 
- name (str) – Name, (never None)   Returns: 

Action Map, The action map with the given name

  Return type: 

[`XrActionMap`](bpy.types.XrActionMap.html#bpy.types.XrActionMap)

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

  
- [`XrSessionState.actionmaps`](bpy.types.XrSessionState.html#bpy.types.XrSessionState.actionmaps)
