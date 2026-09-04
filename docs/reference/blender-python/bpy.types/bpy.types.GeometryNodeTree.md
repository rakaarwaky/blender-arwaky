# bpy.types.GeometryNodeTree

# GeometryNodeTree(NodeTree)

 

base classes — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct), [`ID`](bpy.types.ID.html#bpy.types.ID), [`NodeTree`](bpy.types.NodeTree.html#bpy.types.NodeTree)

   class bpy.types.GeometryNodeTree(NodeTree) 

Node tree consisting of linked nodes used for geometries

   is_mode_edit 

The node group is used in edit mode (default False)

  Type: 

bool

      is_mode_object 

The node group is used in object mode (default False)

  Type: 

bool

      is_mode_paint 

The node group is used in paint mode (default False)

  Type: 

bool

      is_mode_sculpt 

The node group is used in sculpt mode (default False)

  Type: 

bool

      is_modifier 

The node group is used as a geometry modifier (default False)

  Type: 

bool

      is_tool 

The node group is used as a tool (default False)

  Type: 

bool

      is_type_curve 

The node group is used for curves (default False)

  Type: 

bool

      is_type_grease_pencil 

The node group is used for Grease Pencil (default False)

  Type: 

bool

      is_type_mesh 

The node group is used for meshes (default False)

  Type: 

bool

      is_type_pointcloud 

The node group is used for point clouds (default False)

  Type: 

bool

      node_tool_idname 

Unique operator identifier for the node tool (default “”, never None)

  Type: 

str

      show_modifier_manage_panel 

Turn on the option to display the manage panel when creating a modifier (default True)

  Type: 

bool

      use_wait_for_click 

Wait for mouse click input before running the operator from a menu (default False)

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
- [`ID.name`](bpy.types.ID.html#bpy.types.ID.name) 
- [`ID.name_full`](bpy.types.ID.html#bpy.types.ID.name_full) 
- [`ID.id_type`](bpy.types.ID.html#bpy.types.ID.id_type) 
- [`ID.session_uid`](bpy.types.ID.html#bpy.types.ID.session_uid) 
- [`ID.is_evaluated`](bpy.types.ID.html#bpy.types.ID.is_evaluated) 
- [`ID.original`](bpy.types.ID.html#bpy.types.ID.original) 
- [`ID.users`](bpy.types.ID.html#bpy.types.ID.users) 
- [`ID.use_fake_user`](bpy.types.ID.html#bpy.types.ID.use_fake_user) 
- [`ID.use_extra_user`](bpy.types.ID.html#bpy.types.ID.use_extra_user) 
- [`ID.is_embedded_data`](bpy.types.ID.html#bpy.types.ID.is_embedded_data) 
- [`ID.is_linked_packed`](bpy.types.ID.html#bpy.types.ID.is_linked_packed) 
- [`ID.is_missing`](bpy.types.ID.html#bpy.types.ID.is_missing) 
- [`ID.is_runtime_data`](bpy.types.ID.html#bpy.types.ID.is_runtime_data) 
- [`ID.is_editable`](bpy.types.ID.html#bpy.types.ID.is_editable) 
- [`ID.tag`](bpy.types.ID.html#bpy.types.ID.tag) 
- [`ID.is_library_indirect`](bpy.types.ID.html#bpy.types.ID.is_library_indirect) 
- [`ID.library`](bpy.types.ID.html#bpy.types.ID.library) 
- [`ID.library_weak_reference`](bpy.types.ID.html#bpy.types.ID.library_weak_reference)   
- [`ID.asset_data`](bpy.types.ID.html#bpy.types.ID.asset_data) 
- [`ID.override_library`](bpy.types.ID.html#bpy.types.ID.override_library) 
- [`ID.preview`](bpy.types.ID.html#bpy.types.ID.preview) 
- [`NodeTree.color_tag`](bpy.types.NodeTree.html#bpy.types.NodeTree.color_tag) 
- [`NodeTree.default_group_node_width`](bpy.types.NodeTree.html#bpy.types.NodeTree.default_group_node_width) 
- [`NodeTree.view_center`](bpy.types.NodeTree.html#bpy.types.NodeTree.view_center) 
- [`NodeTree.description`](bpy.types.NodeTree.html#bpy.types.NodeTree.description) 
- [`NodeTree.animation_data`](bpy.types.NodeTree.html#bpy.types.NodeTree.animation_data) 
- [`NodeTree.nodes`](bpy.types.NodeTree.html#bpy.types.NodeTree.nodes) 
- [`NodeTree.links`](bpy.types.NodeTree.html#bpy.types.NodeTree.links) 
- [`NodeTree.annotation`](bpy.types.NodeTree.html#bpy.types.NodeTree.annotation) 
- [`NodeTree.type`](bpy.types.NodeTree.html#bpy.types.NodeTree.type) 
- [`NodeTree.interface`](bpy.types.NodeTree.html#bpy.types.NodeTree.interface) 
- [`NodeTree.bl_idname`](bpy.types.NodeTree.html#bpy.types.NodeTree.bl_idname) 
- [`NodeTree.bl_label`](bpy.types.NodeTree.html#bpy.types.NodeTree.bl_label) 
- [`NodeTree.bl_description`](bpy.types.NodeTree.html#bpy.types.NodeTree.bl_description) 
- [`NodeTree.bl_icon`](bpy.types.NodeTree.html#bpy.types.NodeTree.bl_icon) 
- [`NodeTree.bl_use_group_interface`](bpy.types.NodeTree.html#bpy.types.NodeTree.bl_use_group_interface)     

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
- [`ID.bl_system_properties_get`](bpy.types.ID.html#bpy.types.ID.bl_system_properties_get) 
- [`ID.rename`](bpy.types.ID.html#bpy.types.ID.rename)   
- [`ID.evaluated_get`](bpy.types.ID.html#bpy.types.ID.evaluated_get) 
- [`ID.copy`](bpy.types.ID.html#bpy.types.ID.copy) 
- [`ID.asset_mark`](bpy.types.ID.html#bpy.types.ID.asset_mark) 
- [`ID.asset_clear`](bpy.types.ID.html#bpy.types.ID.asset_clear) 
- [`ID.asset_generate_preview`](bpy.types.ID.html#bpy.types.ID.asset_generate_preview) 
- [`ID.override_create`](bpy.types.ID.html#bpy.types.ID.override_create) 
- [`ID.override_hierarchy_create`](bpy.types.ID.html#bpy.types.ID.override_hierarchy_create) 
- [`ID.user_clear`](bpy.types.ID.html#bpy.types.ID.user_clear) 
- [`ID.user_remap`](bpy.types.ID.html#bpy.types.ID.user_remap) 
- [`ID.make_local`](bpy.types.ID.html#bpy.types.ID.make_local) 
- [`ID.user_of_id`](bpy.types.ID.html#bpy.types.ID.user_of_id) 
- [`ID.animation_data_create`](bpy.types.ID.html#bpy.types.ID.animation_data_create) 
- [`ID.animation_data_clear`](bpy.types.ID.html#bpy.types.ID.animation_data_clear) 
- [`ID.update_tag`](bpy.types.ID.html#bpy.types.ID.update_tag) 
- [`ID.preview_ensure`](bpy.types.ID.html#bpy.types.ID.preview_ensure) 
- [`ID.bl_rna_get_subclass`](bpy.types.ID.html#bpy.types.ID.bl_rna_get_subclass) 
- [`ID.bl_rna_get_subclass_py`](bpy.types.ID.html#bpy.types.ID.bl_rna_get_subclass_py) 
- [`NodeTree.interface_update`](bpy.types.NodeTree.html#bpy.types.NodeTree.interface_update) 
- [`NodeTree.contains_tree`](bpy.types.NodeTree.html#bpy.types.NodeTree.contains_tree) 
- [`NodeTree.poll`](bpy.types.NodeTree.html#bpy.types.NodeTree.poll) 
- [`NodeTree.update`](bpy.types.NodeTree.html#bpy.types.NodeTree.update) 
- [`NodeTree.get_from_context`](bpy.types.NodeTree.html#bpy.types.NodeTree.get_from_context) 
- [`NodeTree.valid_socket_type`](bpy.types.NodeTree.html#bpy.types.NodeTree.valid_socket_type) 
- [`NodeTree.debug_lazy_function_graph`](bpy.types.NodeTree.html#bpy.types.NodeTree.debug_lazy_function_graph) 
- [`NodeTree.bl_rna_get_subclass`](bpy.types.NodeTree.html#bpy.types.NodeTree.bl_rna_get_subclass) 
- [`NodeTree.bl_rna_get_subclass_py`](bpy.types.NodeTree.html#bpy.types.NodeTree.bl_rna_get_subclass_py)
