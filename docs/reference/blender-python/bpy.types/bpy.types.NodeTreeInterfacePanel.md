# bpy.types.NodeTreeInterfacePanel

# NodeTreeInterfacePanel(NodeTreeInterfaceItem)

 

base classes — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct), [`NodeTreeInterfaceItem`](bpy.types.NodeTreeInterfaceItem.html#bpy.types.NodeTreeInterfaceItem)

   class bpy.types.NodeTreeInterfacePanel(NodeTreeInterfaceItem) 

Declaration of a node panel

   default_closed 

Panel is closed by default on new nodes (default False)

  Type: 

bool

      description 

Panel description (default “”, never None)

  Type: 

str

      identifier 

Unique identifier for this panel within this node tree (in [-inf, inf], default 0, readonly)

  Type: 

int

      interface_items 

Items in the node panel (default None, readonly)

  Type: 

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.html#bpy.types.bpy_prop_collection)[[`NodeTreeInterfaceItem`](bpy.types.NodeTreeInterfaceItem.html#bpy.types.NodeTreeInterfaceItem)]

      name 

Panel name (default “”, never None)

  Type: 

str

      persistent_uid 

Unique identifier for this panel within this node tree (in [-inf, inf], default 0, readonly)

  Type: 

int

      select 

Panel is selected in the interface (default False)

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
- [`NodeTreeInterfaceItem.item_type`](bpy.types.NodeTreeInterfaceItem.html#bpy.types.NodeTreeInterfaceItem.item_type) 
- [`NodeTreeInterfaceItem.parent`](bpy.types.NodeTreeInterfaceItem.html#bpy.types.NodeTreeInterfaceItem.parent)   
- [`NodeTreeInterfaceItem.position`](bpy.types.NodeTreeInterfaceItem.html#bpy.types.NodeTreeInterfaceItem.position) 
- [`NodeTreeInterfaceItem.index`](bpy.types.NodeTreeInterfaceItem.html#bpy.types.NodeTreeInterfaceItem.index)     

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
- [`NodeTreeInterfaceItem.bl_rna_get_subclass`](bpy.types.NodeTreeInterfaceItem.html#bpy.types.NodeTreeInterfaceItem.bl_rna_get_subclass) 
- [`NodeTreeInterfaceItem.bl_rna_get_subclass_py`](bpy.types.NodeTreeInterfaceItem.html#bpy.types.NodeTreeInterfaceItem.bl_rna_get_subclass_py)     

## References

  
- [`NodeTreeInterface.move_to_parent`](bpy.types.NodeTreeInterface.html#bpy.types.NodeTreeInterface.move_to_parent) 
- [`NodeTreeInterface.new_panel`](bpy.types.NodeTreeInterface.html#bpy.types.NodeTreeInterface.new_panel)   
- [`NodeTreeInterface.new_socket`](bpy.types.NodeTreeInterface.html#bpy.types.NodeTreeInterface.new_socket) 
- [`NodeTreeInterfaceItem.parent`](bpy.types.NodeTreeInterfaceItem.html#bpy.types.NodeTreeInterfaceItem.parent)
