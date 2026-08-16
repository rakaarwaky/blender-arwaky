# bpy.types.NodeInternal

# NodeInternal(Node)

 

base classes — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct), [`Node`](bpy.types.Node.html#bpy.types.Node)

  

Subclasses

  
- [CompositorNode(NodeInternal)](bpy.types.CompositorNode.html) 
- [FunctionNode(NodeInternal)](bpy.types.FunctionNode.html) 
- [GeometryNode(NodeInternal)](bpy.types.GeometryNode.html) 
- [NodeClosureInput(NodeInternal)](bpy.types.NodeClosureInput.html) 
- [NodeClosureOutput(NodeInternal)](bpy.types.NodeClosureOutput.html) 
- [NodeCombineBundle(NodeInternal)](bpy.types.NodeCombineBundle.html) 
- [NodeEnableOutput(NodeInternal)](bpy.types.NodeEnableOutput.html) 
- [NodeEvaluateClosure(NodeInternal)](bpy.types.NodeEvaluateClosure.html) 
- [NodeFrame(NodeInternal)](bpy.types.NodeFrame.html) 
- [NodeGetBundleItem(NodeInternal)](bpy.types.NodeGetBundleItem.html) 
- [NodeGetNestedBundlePaths(NodeInternal)](bpy.types.NodeGetNestedBundlePaths.html) 
- [NodeGroup(NodeInternal)](bpy.types.NodeGroup.html) 
- [NodeGroupInput(NodeInternal)](bpy.types.NodeGroupInput.html) 
- [NodeGroupOutput(NodeInternal)](bpy.types.NodeGroupOutput.html) 
- [NodeImplicitConversion(NodeInternal)](bpy.types.NodeImplicitConversion.html) 
- [NodeJoinBundle(NodeInternal)](bpy.types.NodeJoinBundle.html) 
- [NodeReroute(NodeInternal)](bpy.types.NodeReroute.html) 
- [NodeSeparateBundle(NodeInternal)](bpy.types.NodeSeparateBundle.html) 
- [NodeStoreBundleItem(NodeInternal)](bpy.types.NodeStoreBundleItem.html) 
- [ShaderNode(NodeInternal)](bpy.types.ShaderNode.html) 
- [TextureNode(NodeInternal)](bpy.types.TextureNode.html)     class bpy.types.NodeInternal(Node)   classmethod poll(node_tree) 

If non-null output is returned, the node type can be added to the tree

  Parameters: 

node_tree ([`NodeTree`](bpy.types.NodeTree.html#bpy.types.NodeTree) | None) – Node Tree

  Return type: 

bool

      poll_instance(node_tree) 

If non-null output is returned, the node can be added to the tree

  Parameters: 

node_tree ([`NodeTree`](bpy.types.NodeTree.html#bpy.types.NodeTree) | None) – Node Tree

  Return type: 

bool

      update() 

Update on node graph topology changes (adding or removing nodes and links)

    draw_buttons(context, layout) 

Draw node buttons

  Parameters:  
- context ([`Context`](bpy.types.Context.html#bpy.types.Context) | None) – (never None) 
- layout ([`UILayout`](bpy.types.UILayout.html#bpy.types.UILayout) | None) – Layout, Layout in the UI (never None)       draw_buttons_ext(context, layout) 

Draw node buttons in the sidebar

  Parameters:  
- context ([`Context`](bpy.types.Context.html#bpy.types.Context) | None) – (never None) 
- layout ([`UILayout`](bpy.types.UILayout.html#bpy.types.UILayout) | None) – Layout, Layout in the UI (never None)       classmethod bl_rna_get_subclass(id, default=None, /)  Parameters:  
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
- [`Node.type`](bpy.types.Node.html#bpy.types.Node.type) 
- [`Node.location`](bpy.types.Node.html#bpy.types.Node.location) 
- [`Node.location_absolute`](bpy.types.Node.html#bpy.types.Node.location_absolute) 
- [`Node.width`](bpy.types.Node.html#bpy.types.Node.width) 
- [`Node.height`](bpy.types.Node.html#bpy.types.Node.height) 
- [`Node.dimensions`](bpy.types.Node.html#bpy.types.Node.dimensions) 
- [`Node.name`](bpy.types.Node.html#bpy.types.Node.name) 
- [`Node.label`](bpy.types.Node.html#bpy.types.Node.label) 
- [`Node.inputs`](bpy.types.Node.html#bpy.types.Node.inputs) 
- [`Node.outputs`](bpy.types.Node.html#bpy.types.Node.outputs) 
- [`Node.panel_states`](bpy.types.Node.html#bpy.types.Node.panel_states) 
- [`Node.internal_links`](bpy.types.Node.html#bpy.types.Node.internal_links) 
- [`Node.parent`](bpy.types.Node.html#bpy.types.Node.parent) 
- [`Node.warning_propagation`](bpy.types.Node.html#bpy.types.Node.warning_propagation) 
- [`Node.use_custom_color`](bpy.types.Node.html#bpy.types.Node.use_custom_color) 
- [`Node.color`](bpy.types.Node.html#bpy.types.Node.color) 
- [`Node.color_tag`](bpy.types.Node.html#bpy.types.Node.color_tag)   
- [`Node.select`](bpy.types.Node.html#bpy.types.Node.select) 
- [`Node.show_options`](bpy.types.Node.html#bpy.types.Node.show_options) 
- [`Node.show_preview`](bpy.types.Node.html#bpy.types.Node.show_preview) 
- [`Node.hide`](bpy.types.Node.html#bpy.types.Node.hide) 
- [`Node.mute`](bpy.types.Node.html#bpy.types.Node.mute) 
- [`Node.show_texture`](bpy.types.Node.html#bpy.types.Node.show_texture) 
- [`Node.bl_idname`](bpy.types.Node.html#bpy.types.Node.bl_idname) 
- [`Node.bl_label`](bpy.types.Node.html#bpy.types.Node.bl_label) 
- [`Node.bl_description`](bpy.types.Node.html#bpy.types.Node.bl_description) 
- [`Node.bl_icon`](bpy.types.Node.html#bpy.types.Node.bl_icon) 
- [`Node.bl_static_type`](bpy.types.Node.html#bpy.types.Node.bl_static_type) 
- [`Node.bl_width_default`](bpy.types.Node.html#bpy.types.Node.bl_width_default) 
- [`Node.bl_width_min`](bpy.types.Node.html#bpy.types.Node.bl_width_min) 
- [`Node.bl_width_max`](bpy.types.Node.html#bpy.types.Node.bl_width_max) 
- [`Node.bl_height_default`](bpy.types.Node.html#bpy.types.Node.bl_height_default) 
- [`Node.bl_height_min`](bpy.types.Node.html#bpy.types.Node.bl_height_min) 
- [`Node.bl_height_max`](bpy.types.Node.html#bpy.types.Node.bl_height_max)     

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
- [`Node.bl_system_properties_get`](bpy.types.Node.html#bpy.types.Node.bl_system_properties_get) 
- [`Node.socket_value_update`](bpy.types.Node.html#bpy.types.Node.socket_value_update) 
- [`Node.is_registered_node_type`](bpy.types.Node.html#bpy.types.Node.is_registered_node_type) 
- [`Node.poll`](bpy.types.Node.html#bpy.types.Node.poll) 
- [`Node.poll_instance`](bpy.types.Node.html#bpy.types.Node.poll_instance) 
- [`Node.update`](bpy.types.Node.html#bpy.types.Node.update) 
- [`Node.insert_link`](bpy.types.Node.html#bpy.types.Node.insert_link) 
- [`Node.init`](bpy.types.Node.html#bpy.types.Node.init) 
- [`Node.copy`](bpy.types.Node.html#bpy.types.Node.copy) 
- [`Node.free`](bpy.types.Node.html#bpy.types.Node.free) 
- [`Node.draw_buttons`](bpy.types.Node.html#bpy.types.Node.draw_buttons) 
- [`Node.draw_buttons_ext`](bpy.types.Node.html#bpy.types.Node.draw_buttons_ext) 
- [`Node.draw_label`](bpy.types.Node.html#bpy.types.Node.draw_label) 
- [`Node.debug_zone_body_lazy_function_graph`](bpy.types.Node.html#bpy.types.Node.debug_zone_body_lazy_function_graph) 
- [`Node.debug_zone_lazy_function_graph`](bpy.types.Node.html#bpy.types.Node.debug_zone_lazy_function_graph) 
- [`Node.poll`](bpy.types.Node.html#bpy.types.Node.poll) 
- [`Node.bl_rna_get_subclass`](bpy.types.Node.html#bpy.types.Node.bl_rna_get_subclass) 
- [`Node.bl_rna_get_subclass_py`](bpy.types.Node.html#bpy.types.Node.bl_rna_get_subclass_py)     

## References

  
- [`GeometryNodeForeachGeometryElementInput.pair_with_output`](bpy.types.GeometryNodeForeachGeometryElementInput.html#bpy.types.GeometryNodeForeachGeometryElementInput.pair_with_output) 
- [`GeometryNodeRepeatInput.pair_with_output`](bpy.types.GeometryNodeRepeatInput.html#bpy.types.GeometryNodeRepeatInput.pair_with_output)   
- [`GeometryNodeSimulationInput.pair_with_output`](bpy.types.GeometryNodeSimulationInput.html#bpy.types.GeometryNodeSimulationInput.pair_with_output) 
- [`NodeClosureInput.pair_with_output`](bpy.types.NodeClosureInput.html#bpy.types.NodeClosureInput.pair_with_output)
