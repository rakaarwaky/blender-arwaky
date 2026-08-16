# bpy.types.NodeTreeInterfaceSocketFloatTimeAbsolute

# NodeTreeInterfaceSocketFloatTimeAbsolute(NodeTreeInterfaceSocket)

 

base classes — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct), [`NodeTreeInterfaceItem`](bpy.types.NodeTreeInterfaceItem.html#bpy.types.NodeTreeInterfaceItem), [`NodeTreeInterfaceSocket`](bpy.types.NodeTreeInterfaceSocket.html#bpy.types.NodeTreeInterfaceSocket)

   class bpy.types.NodeTreeInterfaceSocketFloatTimeAbsolute(NodeTreeInterfaceSocket) 

Floating-point number socket of a node

   default_value 

Input value used for unconnected socket (in [-inf, inf], default 0.0)

  Type: 

float

      max_value 

Maximum value (in [-inf, inf], default 0.0)

  Type: 

float

      min_value 

Minimum value (in [-inf, inf], default 0.0)

  Type: 

float

      subtype 

Subtype of the default value (default `'DEFAULT'`)

  Type: 

Literal[‘DEFAULT’]

      draw(context, layout) 

Draw interface socket settings

  Parameters:  
- context ([`Context`](bpy.types.Context.html#bpy.types.Context) | None) – (never None) 
- layout ([`UILayout`](bpy.types.UILayout.html#bpy.types.UILayout) | None) – Layout, Layout in the UI (never None)       init_socket(node, socket, data_path) 

Initialize a node socket instance

  Parameters:  
- node ([`Node`](bpy.types.Node.html#bpy.types.Node) | None) – Node, Node of the socket to initialize (never None) 
- socket ([`NodeSocket`](bpy.types.NodeSocket.html#bpy.types.NodeSocket) | None) – Socket, Socket to initialize (never None) 
- data_path (str) – Data Path, Path to specialized socket data (never None)       from_socket(node, socket) 

Setup template parameters from an existing socket

  Parameters:  
- node ([`Node`](bpy.types.Node.html#bpy.types.Node) | None) – Node, Node of the original socket (never None) 
- socket ([`NodeSocket`](bpy.types.NodeSocket.html#bpy.types.NodeSocket) | None) – Socket, Original socket (never None)       classmethod bl_rna_get_subclass(id, default=None, /)  Parameters:  
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
- [`NodeTreeInterfaceSocket.name`](bpy.types.NodeTreeInterfaceSocket.html#bpy.types.NodeTreeInterfaceSocket.name) 
- [`NodeTreeInterfaceSocket.identifier`](bpy.types.NodeTreeInterfaceSocket.html#bpy.types.NodeTreeInterfaceSocket.identifier) 
- [`NodeTreeInterfaceSocket.description`](bpy.types.NodeTreeInterfaceSocket.html#bpy.types.NodeTreeInterfaceSocket.description) 
- [`NodeTreeInterfaceSocket.socket_type`](bpy.types.NodeTreeInterfaceSocket.html#bpy.types.NodeTreeInterfaceSocket.socket_type) 
- [`NodeTreeInterfaceSocket.in_out`](bpy.types.NodeTreeInterfaceSocket.html#bpy.types.NodeTreeInterfaceSocket.in_out) 
- [`NodeTreeInterfaceSocket.hide_value`](bpy.types.NodeTreeInterfaceSocket.html#bpy.types.NodeTreeInterfaceSocket.hide_value) 
- [`NodeTreeInterfaceSocket.hide_in_modifier`](bpy.types.NodeTreeInterfaceSocket.html#bpy.types.NodeTreeInterfaceSocket.hide_in_modifier)   
- [`NodeTreeInterfaceSocket.force_non_field`](bpy.types.NodeTreeInterfaceSocket.html#bpy.types.NodeTreeInterfaceSocket.force_non_field) 
- [`NodeTreeInterfaceSocket.is_inspect_output`](bpy.types.NodeTreeInterfaceSocket.html#bpy.types.NodeTreeInterfaceSocket.is_inspect_output) 
- [`NodeTreeInterfaceSocket.is_panel_toggle`](bpy.types.NodeTreeInterfaceSocket.html#bpy.types.NodeTreeInterfaceSocket.is_panel_toggle) 
- [`NodeTreeInterfaceSocket.layer_selection_field`](bpy.types.NodeTreeInterfaceSocket.html#bpy.types.NodeTreeInterfaceSocket.layer_selection_field) 
- [`NodeTreeInterfaceSocket.menu_expanded`](bpy.types.NodeTreeInterfaceSocket.html#bpy.types.NodeTreeInterfaceSocket.menu_expanded) 
- [`NodeTreeInterfaceSocket.optional_label`](bpy.types.NodeTreeInterfaceSocket.html#bpy.types.NodeTreeInterfaceSocket.optional_label) 
- [`NodeTreeInterfaceSocket.select`](bpy.types.NodeTreeInterfaceSocket.html#bpy.types.NodeTreeInterfaceSocket.select) 
- [`NodeTreeInterfaceSocket.attribute_domain`](bpy.types.NodeTreeInterfaceSocket.html#bpy.types.NodeTreeInterfaceSocket.attribute_domain) 
- [`NodeTreeInterfaceSocket.default_attribute_name`](bpy.types.NodeTreeInterfaceSocket.html#bpy.types.NodeTreeInterfaceSocket.default_attribute_name) 
- [`NodeTreeInterfaceSocket.structure_type`](bpy.types.NodeTreeInterfaceSocket.html#bpy.types.NodeTreeInterfaceSocket.structure_type) 
- [`NodeTreeInterfaceSocket.default_input`](bpy.types.NodeTreeInterfaceSocket.html#bpy.types.NodeTreeInterfaceSocket.default_input) 
- [`NodeTreeInterfaceSocket.bl_socket_idname`](bpy.types.NodeTreeInterfaceSocket.html#bpy.types.NodeTreeInterfaceSocket.bl_socket_idname)     

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
- [`NodeTreeInterfaceSocket.bl_system_properties_get`](bpy.types.NodeTreeInterfaceSocket.html#bpy.types.NodeTreeInterfaceSocket.bl_system_properties_get) 
- [`NodeTreeInterfaceSocket.draw`](bpy.types.NodeTreeInterfaceSocket.html#bpy.types.NodeTreeInterfaceSocket.draw) 
- [`NodeTreeInterfaceSocket.init_socket`](bpy.types.NodeTreeInterfaceSocket.html#bpy.types.NodeTreeInterfaceSocket.init_socket) 
- [`NodeTreeInterfaceSocket.from_socket`](bpy.types.NodeTreeInterfaceSocket.html#bpy.types.NodeTreeInterfaceSocket.from_socket) 
- [`NodeTreeInterfaceSocket.bl_rna_get_subclass`](bpy.types.NodeTreeInterfaceSocket.html#bpy.types.NodeTreeInterfaceSocket.bl_rna_get_subclass) 
- [`NodeTreeInterfaceSocket.bl_rna_get_subclass_py`](bpy.types.NodeTreeInterfaceSocket.html#bpy.types.NodeTreeInterfaceSocket.bl_rna_get_subclass_py)
