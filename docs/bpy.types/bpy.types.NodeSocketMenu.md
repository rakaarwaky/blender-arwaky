# bpy.types.NodeSocketMenu

# NodeSocketMenu(NodeSocketStandard)

 

base classes — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct), [`NodeSocket`](bpy.types.NodeSocket.html#bpy.types.NodeSocket), [`NodeSocketStandard`](bpy.types.NodeSocketStandard.html#bpy.types.NodeSocketStandard)

   class bpy.types.NodeSocketMenu(NodeSocketStandard) 

Menu socket of a node

   default_value  Type: 

str

      links 

List of node links from or to this socket.

  Type: 

[`NodeLinks`](bpy.types.NodeLinks.html#bpy.types.NodeLinks)

    

Note

 

Takes `O(len(nodetree.links))` time.

  

(readonly)

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
- [`NodeSocket.name`](bpy.types.NodeSocket.html#bpy.types.NodeSocket.name) 
- [`NodeSocket.label`](bpy.types.NodeSocket.html#bpy.types.NodeSocket.label) 
- [`NodeSocket.identifier`](bpy.types.NodeSocket.html#bpy.types.NodeSocket.identifier) 
- [`NodeSocket.description`](bpy.types.NodeSocket.html#bpy.types.NodeSocket.description) 
- [`NodeSocket.is_output`](bpy.types.NodeSocket.html#bpy.types.NodeSocket.is_output) 
- [`NodeSocket.select`](bpy.types.NodeSocket.html#bpy.types.NodeSocket.select) 
- [`NodeSocket.hide`](bpy.types.NodeSocket.html#bpy.types.NodeSocket.hide) 
- [`NodeSocket.enabled`](bpy.types.NodeSocket.html#bpy.types.NodeSocket.enabled) 
- [`NodeSocket.link_limit`](bpy.types.NodeSocket.html#bpy.types.NodeSocket.link_limit) 
- [`NodeSocket.is_linked`](bpy.types.NodeSocket.html#bpy.types.NodeSocket.is_linked) 
- [`NodeSocket.is_unavailable`](bpy.types.NodeSocket.html#bpy.types.NodeSocket.is_unavailable) 
- [`NodeSocket.is_multi_input`](bpy.types.NodeSocket.html#bpy.types.NodeSocket.is_multi_input) 
- [`NodeSocket.show_expanded`](bpy.types.NodeSocket.html#bpy.types.NodeSocket.show_expanded)   
- [`NodeSocket.is_inactive`](bpy.types.NodeSocket.html#bpy.types.NodeSocket.is_inactive) 
- [`NodeSocket.is_icon_visible`](bpy.types.NodeSocket.html#bpy.types.NodeSocket.is_icon_visible) 
- [`NodeSocket.hide_value`](bpy.types.NodeSocket.html#bpy.types.NodeSocket.hide_value) 
- [`NodeSocket.pin_gizmo`](bpy.types.NodeSocket.html#bpy.types.NodeSocket.pin_gizmo) 
- [`NodeSocket.node`](bpy.types.NodeSocket.html#bpy.types.NodeSocket.node) 
- [`NodeSocket.type`](bpy.types.NodeSocket.html#bpy.types.NodeSocket.type) 
- [`NodeSocket.display_shape`](bpy.types.NodeSocket.html#bpy.types.NodeSocket.display_shape) 
- [`NodeSocket.inferred_structure_type`](bpy.types.NodeSocket.html#bpy.types.NodeSocket.inferred_structure_type) 
- [`NodeSocket.bl_idname`](bpy.types.NodeSocket.html#bpy.types.NodeSocket.bl_idname) 
- [`NodeSocket.bl_label`](bpy.types.NodeSocket.html#bpy.types.NodeSocket.bl_label) 
- [`NodeSocket.bl_subtype_label`](bpy.types.NodeSocket.html#bpy.types.NodeSocket.bl_subtype_label) 
- [`NodeSocket.links`](bpy.types.NodeSocket.html#bpy.types.NodeSocket.links) 
- [`NodeSocketStandard.links`](bpy.types.NodeSocketStandard.html#bpy.types.NodeSocketStandard.links)     

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
- [`NodeSocket.bl_system_properties_get`](bpy.types.NodeSocket.html#bpy.types.NodeSocket.bl_system_properties_get) 
- [`NodeSocket.draw`](bpy.types.NodeSocket.html#bpy.types.NodeSocket.draw) 
- [`NodeSocket.draw_color`](bpy.types.NodeSocket.html#bpy.types.NodeSocket.draw_color) 
- [`NodeSocket.draw_color_simple`](bpy.types.NodeSocket.html#bpy.types.NodeSocket.draw_color_simple) 
- [`NodeSocket.bl_rna_get_subclass`](bpy.types.NodeSocket.html#bpy.types.NodeSocket.bl_rna_get_subclass) 
- [`NodeSocket.bl_rna_get_subclass_py`](bpy.types.NodeSocket.html#bpy.types.NodeSocket.bl_rna_get_subclass_py) 
- [`NodeSocketStandard.draw`](bpy.types.NodeSocketStandard.html#bpy.types.NodeSocketStandard.draw) 
- [`NodeSocketStandard.draw_color`](bpy.types.NodeSocketStandard.html#bpy.types.NodeSocketStandard.draw_color) 
- [`NodeSocketStandard.draw_color_simple`](bpy.types.NodeSocketStandard.html#bpy.types.NodeSocketStandard.draw_color_simple) 
- [`NodeSocketStandard.bl_rna_get_subclass`](bpy.types.NodeSocketStandard.html#bpy.types.NodeSocketStandard.bl_rna_get_subclass) 
- [`NodeSocketStandard.bl_rna_get_subclass_py`](bpy.types.NodeSocketStandard.html#bpy.types.NodeSocketStandard.bl_rna_get_subclass_py)
