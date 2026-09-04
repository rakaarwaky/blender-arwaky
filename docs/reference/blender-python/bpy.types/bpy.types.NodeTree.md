# bpy.types.NodeTree

# NodeTree(ID)

  

## Poll Function

 

The `NodeTree.poll` function determines if a node tree is visible in the given context (similar to how [`Panel.poll`](bpy.types.Panel.html#bpy.types.Panel.poll) and [`Menu.poll`](bpy.types.Menu.html#bpy.types.Menu.poll) define visibility). If it returns False, the node tree type will not be selectable in the node editor.

 

A typical condition for shader nodes would be to check the active render engine of the scene and only show nodes of the renderer they are designed for.

 

```python
import bpy

class CyclesNodeTree(bpy.types.NodeTree):
    """ This operator is only visible when Cycles is the selected render engine"""
    bl_label = "Cycles Node Tree"
    bl_icon = 'NONE'

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'CYCLES'

bpy.utils.register_class(CyclesNodeTree)
```

  

base classes — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct), [`ID`](bpy.types.ID.html#bpy.types.ID)

  

Subclasses

  
- [CompositorNodeTree(NodeTree)](bpy.types.CompositorNodeTree.html) 
- [GeometryNodeTree(NodeTree)](bpy.types.GeometryNodeTree.html) 
- [ShaderNodeTree(NodeTree)](bpy.types.ShaderNodeTree.html) 
- [TextureNodeTree(NodeTree)](bpy.types.TextureNodeTree.html)     class bpy.types.NodeTree(ID) 

Node tree consisting of linked nodes used for shading, textures and compositing

   animation_data 

Animation data for this data-block (readonly)

  Type: 

[`AnimData`](bpy.types.AnimData.html#bpy.types.AnimData) | None

      annotation 

Annotation data

  Type: 

[`Annotation`](bpy.types.Annotation.html#bpy.types.Annotation) | None

      bl_description 

(default “”, never None)

  Type: 

str

      bl_icon 

The node tree icon (default `'NODETREE'`)

  Type: 

Literal[[Icon Items](bpy_types_enum_items/icon_items.html#rna-enum-icon-items)]

      bl_idname 

(default “”, never None)

  Type: 

str

      bl_label 

The node tree label (default “”, never None)

  Type: 

str

      bl_use_group_interface 

Determines the visibility of some UI elements related to node groups (default True)

  Type: 

bool

      color_tag 

Color tag of the node group which influences the header color (default `'NONE'`)

  
- `NONE` None – Default color tag for new nodes and node groups. 
- `ATTRIBUTE` Attribute. 
- `COLOR` Color. 
- `CONVERTER` Converter. 
- `DISTORT` Distort. 
- `FILTER` Filter. 
- `GEOMETRY` Geometry. 
- `INPUT` Input. 
- `MATTE` Matte. 
- `OUTPUT` Output. 
- `SCRIPT` Script. 
- `SHADER` Shader. 
- `TEXTURE` Texture. 
- `VECTOR` Vector. 
- `PATTERN` Pattern. 
- `INTERFACE` Interface. 
- `GROUP` Group.   Type: 

Literal[‘NONE’, ‘ATTRIBUTE’, ‘COLOR’, ‘CONVERTER’, ‘DISTORT’, ‘FILTER’, ‘GEOMETRY’, ‘INPUT’, ‘MATTE’, ‘OUTPUT’, ‘SCRIPT’, ‘SHADER’, ‘TEXTURE’, ‘VECTOR’, ‘PATTERN’, ‘INTERFACE’, ‘GROUP’]

      default_group_node_width 

The width for newly created group nodes (in [60, 700], default 140)

  Type: 

int

      description 

Description of the node tree (default “”, never None)

  Type: 

str

      interface 

Interface declaration for this node tree (readonly)

  Type: 

[`NodeTreeInterface`](bpy.types.NodeTreeInterface.html#bpy.types.NodeTreeInterface) | None

      links 

(default None, readonly)

  Type: 

[`NodeLinks`](bpy.types.NodeLinks.html#bpy.types.NodeLinks)[[`NodeLink`](bpy.types.NodeLink.html#bpy.types.NodeLink)]

      nodes 

(default None, readonly)

  Type: 

[`Nodes`](bpy.types.Nodes.html#bpy.types.Nodes)[[`Node`](bpy.types.Node.html#bpy.types.Node)]

      type 

Node Tree type (deprecated, bl_idname is the actual node tree type identifier) (default `'SHADER'`, readonly)

  
- `UNDEFINED` Undefined – Undefined type of nodes (can happen e.g. when a linked node tree goes missing). 
- `CUSTOM` Custom – Custom nodes. 
- `SHADER` Shader – Shader nodes. 
- `TEXTURE` Texture – Texture nodes. 
- `COMPOSITING` Compositing – Compositing nodes. 
- `GEOMETRY` Geometry – Geometry nodes.   Type: 

Literal[‘UNDEFINED’, ‘CUSTOM’, ‘SHADER’, ‘TEXTURE’, ‘COMPOSITING’, ‘GEOMETRY’]

      view_center 

The current location (offset) of the view for this Node Tree (array of 2 items, in [-inf, inf], default (0.0, 0.0), readonly)

  Type: 

[`mathutils.Vector`](mathutils.html#mathutils.Vector)

      interface_update(context) 

Updated node group interface

  Parameters: 

context ([`Context`](bpy.types.Context.html#bpy.types.Context) | None) – (never None)

      contains_tree(sub_tree) 

Check if the node tree contains another. Used to avoid creating recursive node groups.

  Parameters: 

sub_tree (`NodeTree` | None) – Node Tree, Node tree for recursive check (never None)

  Returns: 

contained

  Return type: 

bool

      classmethod poll(context) 

Check visibility in the editor

  Parameters: 

context ([`Context`](bpy.types.Context.html#bpy.types.Context) | None) – (never None)

  Return type: 

bool

      update() 

Update on editor changes

    classmethod get_from_context(context) 

Get a node tree from the context

  Parameters: 

context ([`Context`](bpy.types.Context.html#bpy.types.Context) | None) – (never None)

  Returns: 

`result_1`, Active node tree from context, `NodeTree`

 

`result_2`, ID data-block that owns the node tree, [`ID`](bpy.types.ID.html#bpy.types.ID)

 

`result_3`, Original ID data-block selected from the context, [`ID`](bpy.types.ID.html#bpy.types.ID)

  Return type: 

tuple[`NodeTree`, [`ID`](bpy.types.ID.html#bpy.types.ID), [`ID`](bpy.types.ID.html#bpy.types.ID)]

      classmethod valid_socket_type(idname) 

Check if the socket type is valid for the node tree

  Parameters: 

idname (str) – Socket Type, Identifier of the socket type (never None)

  Return type: 

bool

      debug_lazy_function_graph() 

Get the internal lazy-function graph for this node tree

  Returns: 

Dot Graph, Graph in dot format

  Return type: 

str

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

      

### Inherited Properties

  
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

### Inherited Functions

  
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

### References

  
- [`BlendData.node_groups`](bpy.types.BlendData.html#bpy.types.BlendData.node_groups) 
- [`BlendDataNodeTrees.new`](bpy.types.BlendDataNodeTrees.html#bpy.types.BlendDataNodeTrees.new) 
- [`BlendDataNodeTrees.remove`](bpy.types.BlendDataNodeTrees.html#bpy.types.BlendDataNodeTrees.remove) 
- [`CompositorNodeCustomGroup.node_tree`](bpy.types.CompositorNodeCustomGroup.html#bpy.types.CompositorNodeCustomGroup.node_tree) 
- [`CompositorNodeGroup.node_tree`](bpy.types.CompositorNodeGroup.html#bpy.types.CompositorNodeGroup.node_tree) 
- [`CompositorStrip.node_group`](bpy.types.CompositorStrip.html#bpy.types.CompositorStrip.node_group) 
- [`EvaluateClosureNodeViewerPathElem.source_node_tree`](bpy.types.EvaluateClosureNodeViewerPathElem.html#bpy.types.EvaluateClosureNodeViewerPathElem.source_node_tree) 
- [`FreestyleLineStyle.node_tree`](bpy.types.FreestyleLineStyle.html#bpy.types.FreestyleLineStyle.node_tree) 
- [`GeometryNodeCustomGroup.node_tree`](bpy.types.GeometryNodeCustomGroup.html#bpy.types.GeometryNodeCustomGroup.node_tree) 
- [`GeometryNodeGroup.node_tree`](bpy.types.GeometryNodeGroup.html#bpy.types.GeometryNodeGroup.node_tree) 
- [`Light.node_tree`](bpy.types.Light.html#bpy.types.Light.node_tree) 
- [`Material.node_tree`](bpy.types.Material.html#bpy.types.Material.node_tree) 
- [`Node.poll`](bpy.types.Node.html#bpy.types.Node.poll) 
- [`Node.poll_instance`](bpy.types.Node.html#bpy.types.Node.poll_instance) 
- [`NodeCustomGroup.node_tree`](bpy.types.NodeCustomGroup.html#bpy.types.NodeCustomGroup.node_tree) 
- [`NodeGroup.node_tree`](bpy.types.NodeGroup.html#bpy.types.NodeGroup.node_tree) 
- [`NodeInternal.poll`](bpy.types.NodeInternal.html#bpy.types.NodeInternal.poll) 
- [`NodeInternal.poll_instance`](bpy.types.NodeInternal.html#bpy.types.NodeInternal.poll_instance)   
- `NodeTree.contains_tree` 
- `NodeTree.get_from_context` 
- [`NodeTreePath.node_tree`](bpy.types.NodeTreePath.html#bpy.types.NodeTreePath.node_tree) 
- [`NodesModifier.node_group`](bpy.types.NodesModifier.html#bpy.types.NodesModifier.node_group) 
- [`Scene.compositing_node_group`](bpy.types.Scene.html#bpy.types.Scene.compositing_node_group) 
- [`SequencerCompositorModifierData.node_group`](bpy.types.SequencerCompositorModifierData.html#bpy.types.SequencerCompositorModifierData.node_group) 
- [`ShaderNodeCustomGroup.node_tree`](bpy.types.ShaderNodeCustomGroup.html#bpy.types.ShaderNodeCustomGroup.node_tree) 
- [`ShaderNodeGroup.node_tree`](bpy.types.ShaderNodeGroup.html#bpy.types.ShaderNodeGroup.node_tree) 
- [`SpaceNodeEditor.edit_tree`](bpy.types.SpaceNodeEditor.html#bpy.types.SpaceNodeEditor.edit_tree) 
- [`SpaceNodeEditor.node_tree`](bpy.types.SpaceNodeEditor.html#bpy.types.SpaceNodeEditor.node_tree) 
- [`SpaceNodeEditor.selected_node_group`](bpy.types.SpaceNodeEditor.html#bpy.types.SpaceNodeEditor.selected_node_group) 
- [`SpaceNodeEditorPath.append`](bpy.types.SpaceNodeEditorPath.html#bpy.types.SpaceNodeEditorPath.append) 
- [`SpaceNodeEditorPath.start`](bpy.types.SpaceNodeEditorPath.html#bpy.types.SpaceNodeEditorPath.start) 
- [`Texture.node_tree`](bpy.types.Texture.html#bpy.types.Texture.node_tree) 
- [`TextureNodeGroup.node_tree`](bpy.types.TextureNodeGroup.html#bpy.types.TextureNodeGroup.node_tree) 
- [`UILayout.template_node_link`](bpy.types.UILayout.html#bpy.types.UILayout.template_node_link) 
- [`UILayout.template_node_view`](bpy.types.UILayout.html#bpy.types.UILayout.template_node_view) 
- [`World.node_tree`](bpy.types.World.html#bpy.types.World.node_tree)
