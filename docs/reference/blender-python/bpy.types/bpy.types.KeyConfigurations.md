# bpy.types.KeyConfigurations

# KeyConfigurations(bpy_prop_collection)

 

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.html#bpy.types.bpy_prop_collection)

   class bpy.types.KeyConfigurations(bpy_prop_collection) 

Collection of KeyConfigs

   active 

Active key configuration (preset)

  Type: 

[`KeyConfig`](bpy.types.KeyConfig.html#bpy.types.KeyConfig) | None

      addon 

Key configuration that can be extended by add-ons, and is added to the active configuration when handling events (readonly)

  Type: 

[`KeyConfig`](bpy.types.KeyConfig.html#bpy.types.KeyConfig) | None

      default 

Default builtin key configuration (readonly)

  Type: 

[`KeyConfig`](bpy.types.KeyConfig.html#bpy.types.KeyConfig) | None

      user 

Final key configuration that combines keymaps from the active and add-on configurations, and can be edited by the user (readonly)

  Type: 

[`KeyConfig`](bpy.types.KeyConfig.html#bpy.types.KeyConfig) | None

      new(name) 

new

  Parameters: 

name (str) – Name, (never None)

  Returns: 

Key Configuration, Added key configuration

  Return type: 

[`KeyConfig`](bpy.types.KeyConfig.html#bpy.types.KeyConfig)

      remove(keyconfig) 

remove

  Parameters: 

keyconfig ([`KeyConfig`](bpy.types.KeyConfig.html#bpy.types.KeyConfig) | None) – Key Configuration, Removed key configuration (never None)

      find_item_from_operator(idname, *, context='INVOKE_DEFAULT', properties=None, include={'ACTIONZONE', 'KEYBOARD', 'MOUSE', 'NDOF'}, exclude=set()) 

find_item_from_operator

  Parameters:  
- idname (str) – Operator Identifier, (never None) 
- context (Literal[[Operator Context Items](bpy_types_enum_items/operator_context_items.html#rna-enum-operator-context-items)]) – context, (optional) 
- properties ([`OperatorProperties`](bpy.types.OperatorProperties.html#bpy.types.OperatorProperties) | None) – (optional) 
- include (set[Literal[[Event Type Mask Items](bpy_types_enum_items/event_type_mask_items.html#rna-enum-event-type-mask-items)]]) – Include, (optional) 
- exclude (set[Literal[[Event Type Mask Items](bpy_types_enum_items/event_type_mask_items.html#rna-enum-event-type-mask-items)]]) – Exclude, (optional)   Returns: 

`keymap`, [`KeyMap`](bpy.types.KeyMap.html#bpy.types.KeyMap)

 

`item`, [`KeyMapItem`](bpy.types.KeyMapItem.html#bpy.types.KeyMapItem)

  Return type: 

tuple[[`KeyMap`](bpy.types.KeyMap.html#bpy.types.KeyMap), [`KeyMapItem`](bpy.types.KeyMapItem.html#bpy.types.KeyMapItem)]

      update(*, keep_properties=False) 

update

  Parameters: 

keep_properties (bool) – Keep Properties, Operator properties are kept to allow the operators to be registered again in the future (optional)

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

  
- [`WindowManager.keyconfigs`](bpy.types.WindowManager.html#bpy.types.WindowManager.keyconfigs)
