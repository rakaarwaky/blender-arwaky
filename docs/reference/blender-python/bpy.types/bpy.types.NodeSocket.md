# bpy.types.NodeSocket

# NodeSocket(bpy_struct)

 

base class — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct)

  

Subclasses

  
- [NodeSocketStandard(NodeSocket)](bpy.types.NodeSocketStandard.html)     class bpy.types.NodeSocket(bpy_struct) 

Input or output socket of a node

   bl_idname 

(default “”, never None)

  Type: 

str

      bl_label 

Label to display for the socket type in the UI (default “”, never None)

  Type: 

str

      bl_subtype_label 

Label to display for the socket subtype in the UI (default “”, never None)

  Type: 

str

      description 

Socket tooltip (default “”, never None)

  Type: 

str

      display_shape 

Socket shape (default `'CIRCLE'`)

  Type: 

Literal[‘CIRCLE’, ‘SQUARE’, ‘DIAMOND’, ‘CIRCLE_DOT’, ‘SQUARE_DOT’, ‘DIAMOND_DOT’, ‘LINE’, ‘VOLUME_GRID’, ‘LIST’]

      enabled 

Enable the socket (default True)

  Type: 

bool

      hide 

Hide the socket (default False)

  Type: 

bool

      hide_value 

Hide the socket input value (default False)

  Type: 

bool

      identifier 

Unique identifier for mapping sockets (default “”, readonly, never None)

  Type: 

str

      inferred_structure_type 

Best known structure type of the socket. This may not match the socket shape, e.g. for unlinked input sockets (default `'AUTO'`, readonly)

  Type: 

Literal[[Node Socket Structure Type Items](bpy_types_enum_items/node_socket_structure_type_items.html#rna-enum-node-socket-structure-type-items)]

      is_icon_visible 

Socket is drawn as interactive icon in the node editor (default False, readonly)

  Type: 

bool

      is_inactive 

Socket is grayed out because it has been detected to not have any effect on the output (default False, readonly)

  Type: 

bool

      is_linked 

True if the socket is connected (default False, readonly)

  Type: 

bool

      is_multi_input 

True if the socket can accept multiple ordered input links (default False, readonly)

  Type: 

bool

      is_output 

True if the socket is an output, otherwise input (default False, readonly)

  Type: 

bool

      is_unavailable 

True if the socket is unavailable (default False, readonly)

  Type: 

bool

      label 

Custom dynamic defined UI label for the socket. Can be translated if translation is enabled in the preferences (default “”, readonly, never None)

  Type: 

str

      link_limit 

Max number of links allowed for this socket (in [1, 4095], default 0)

  Type: 

int

      name 

Socket name (default “”, never None)

  Type: 

str

      node 

Node owning this socket (readonly)

  Type: 

[`Node`](bpy.types.Node.html#bpy.types.Node) | None

      pin_gizmo 

Keep gizmo visible even when the node is not selected (default False)

  Type: 

bool

      select 

True if the socket is selected (default False, readonly)

  Type: 

bool

      show_expanded 

Socket links are expanded in the user interface (default True)

  Type: 

bool

      type 

Data type (default `'VALUE'`)

  Type: 

Literal[[Node Socket Type Items](bpy_types_enum_items/node_socket_type_items.html#rna-enum-node-socket-type-items)]

      links 

List of node links from or to this socket.

  Type: 

[`NodeLinks`](bpy.types.NodeLinks.html#bpy.types.NodeLinks)

    

Note

 

Takes `O(len(nodetree.links))` time.

  

(readonly)

    bl_system_properties_get(*, do_create=False) 

DEBUG ONLY. Internal access to runtime-defined RNA data storage, intended solely for testing and debugging purposes. Do not access it in regular scripting work, and in particular, do not assume that it contains writable data

  Parameters: 

do_create (bool) – Ensure that system properties are created if they do not exist yet (optional)

  Returns: 

The system properties root container, or None if there are no system properties stored in this data yet, and its creation was not requested

  Return type: 

[`PropertyGroup`](bpy.types.PropertyGroup.html#bpy.types.PropertyGroup)

      draw(context, layout, node, text) 

Draw socket

  Parameters:  
- context ([`Context`](bpy.types.Context.html#bpy.types.Context) | None) – (never None) 
- layout ([`UILayout`](bpy.types.UILayout.html#bpy.types.UILayout) | None) – Layout, Layout in the UI (never None) 
- node ([`Node`](bpy.types.Node.html#bpy.types.Node) | None) – Node, Node the socket belongs to (never None) 
- text (str) – Text, Text label to draw alongside properties (never None)       draw_color(context, node) 

Color of the socket icon

  Parameters:  
- context ([`Context`](bpy.types.Context.html#bpy.types.Context) | None) – (never None) 
- node ([`Node`](bpy.types.Node.html#bpy.types.Node) | None) – Node, Node the socket belongs to (never None)   Returns: 

Color, (array of 4 items, in [0, 1])

  Return type: 

[`bpy_prop_array`](bpy.types.bpy_prop_array.html#bpy.types.bpy_prop_array)[float]

      classmethod draw_color_simple() 

Color of the socket icon. Used to draw sockets in places where the socket does not belong to a node, like the node interface panel. Also used to draw node sockets if draw_color is not defined.

  Returns: 

Color, (array of 4 items, in [0, 1])

  Return type: 

[`bpy_prop_array`](bpy.types.bpy_prop_array.html#bpy.types.bpy_prop_array)[float]

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

  
- [`Node.inputs`](bpy.types.Node.html#bpy.types.Node.inputs) 
- [`Node.outputs`](bpy.types.Node.html#bpy.types.Node.outputs) 
- [`NodeInputs.new`](bpy.types.NodeInputs.html#bpy.types.NodeInputs.new) 
- [`NodeInputs.remove`](bpy.types.NodeInputs.html#bpy.types.NodeInputs.remove) 
- [`NodeLink.from_socket`](bpy.types.NodeLink.html#bpy.types.NodeLink.from_socket) 
- [`NodeLink.to_socket`](bpy.types.NodeLink.html#bpy.types.NodeLink.to_socket) 
- [`NodeLinks.new`](bpy.types.NodeLinks.html#bpy.types.NodeLinks.new) 
- [`NodeLinks.new`](bpy.types.NodeLinks.html#bpy.types.NodeLinks.new) 
- [`NodeOutputs.new`](bpy.types.NodeOutputs.html#bpy.types.NodeOutputs.new) 
- [`NodeOutputs.remove`](bpy.types.NodeOutputs.html#bpy.types.NodeOutputs.remove) 
- [`NodeTreeInterfaceSocket.from_socket`](bpy.types.NodeTreeInterfaceSocket.html#bpy.types.NodeTreeInterfaceSocket.from_socket) 
- [`NodeTreeInterfaceSocket.init_socket`](bpy.types.NodeTreeInterfaceSocket.html#bpy.types.NodeTreeInterfaceSocket.init_socket) 
- [`NodeTreeInterfaceSocketBool.from_socket`](bpy.types.NodeTreeInterfaceSocketBool.html#bpy.types.NodeTreeInterfaceSocketBool.from_socket) 
- [`NodeTreeInterfaceSocketBool.init_socket`](bpy.types.NodeTreeInterfaceSocketBool.html#bpy.types.NodeTreeInterfaceSocketBool.init_socket) 
- [`NodeTreeInterfaceSocketBundle.from_socket`](bpy.types.NodeTreeInterfaceSocketBundle.html#bpy.types.NodeTreeInterfaceSocketBundle.from_socket) 
- [`NodeTreeInterfaceSocketBundle.init_socket`](bpy.types.NodeTreeInterfaceSocketBundle.html#bpy.types.NodeTreeInterfaceSocketBundle.init_socket) 
- [`NodeTreeInterfaceSocketClosure.from_socket`](bpy.types.NodeTreeInterfaceSocketClosure.html#bpy.types.NodeTreeInterfaceSocketClosure.from_socket) 
- [`NodeTreeInterfaceSocketClosure.init_socket`](bpy.types.NodeTreeInterfaceSocketClosure.html#bpy.types.NodeTreeInterfaceSocketClosure.init_socket) 
- [`NodeTreeInterfaceSocketCollection.from_socket`](bpy.types.NodeTreeInterfaceSocketCollection.html#bpy.types.NodeTreeInterfaceSocketCollection.from_socket) 
- [`NodeTreeInterfaceSocketCollection.init_socket`](bpy.types.NodeTreeInterfaceSocketCollection.html#bpy.types.NodeTreeInterfaceSocketCollection.init_socket) 
- [`NodeTreeInterfaceSocketColor.from_socket`](bpy.types.NodeTreeInterfaceSocketColor.html#bpy.types.NodeTreeInterfaceSocketColor.from_socket) 
- [`NodeTreeInterfaceSocketColor.init_socket`](bpy.types.NodeTreeInterfaceSocketColor.html#bpy.types.NodeTreeInterfaceSocketColor.init_socket) 
- [`NodeTreeInterfaceSocketFloat.from_socket`](bpy.types.NodeTreeInterfaceSocketFloat.html#bpy.types.NodeTreeInterfaceSocketFloat.from_socket) 
- [`NodeTreeInterfaceSocketFloat.init_socket`](bpy.types.NodeTreeInterfaceSocketFloat.html#bpy.types.NodeTreeInterfaceSocketFloat.init_socket) 
- [`NodeTreeInterfaceSocketFloatAngle.from_socket`](bpy.types.NodeTreeInterfaceSocketFloatAngle.html#bpy.types.NodeTreeInterfaceSocketFloatAngle.from_socket) 
- [`NodeTreeInterfaceSocketFloatAngle.init_socket`](bpy.types.NodeTreeInterfaceSocketFloatAngle.html#bpy.types.NodeTreeInterfaceSocketFloatAngle.init_socket) 
- [`NodeTreeInterfaceSocketFloatColorTemperature.from_socket`](bpy.types.NodeTreeInterfaceSocketFloatColorTemperature.html#bpy.types.NodeTreeInterfaceSocketFloatColorTemperature.from_socket) 
- [`NodeTreeInterfaceSocketFloatColorTemperature.init_socket`](bpy.types.NodeTreeInterfaceSocketFloatColorTemperature.html#bpy.types.NodeTreeInterfaceSocketFloatColorTemperature.init_socket) 
- [`NodeTreeInterfaceSocketFloatDistance.from_socket`](bpy.types.NodeTreeInterfaceSocketFloatDistance.html#bpy.types.NodeTreeInterfaceSocketFloatDistance.from_socket) 
- [`NodeTreeInterfaceSocketFloatDistance.init_socket`](bpy.types.NodeTreeInterfaceSocketFloatDistance.html#bpy.types.NodeTreeInterfaceSocketFloatDistance.init_socket) 
- [`NodeTreeInterfaceSocketFloatFactor.from_socket`](bpy.types.NodeTreeInterfaceSocketFloatFactor.html#bpy.types.NodeTreeInterfaceSocketFloatFactor.from_socket) 
- [`NodeTreeInterfaceSocketFloatFactor.init_socket`](bpy.types.NodeTreeInterfaceSocketFloatFactor.html#bpy.types.NodeTreeInterfaceSocketFloatFactor.init_socket) 
- [`NodeTreeInterfaceSocketFloatFrequency.from_socket`](bpy.types.NodeTreeInterfaceSocketFloatFrequency.html#bpy.types.NodeTreeInterfaceSocketFloatFrequency.from_socket) 
- [`NodeTreeInterfaceSocketFloatFrequency.init_socket`](bpy.types.NodeTreeInterfaceSocketFloatFrequency.html#bpy.types.NodeTreeInterfaceSocketFloatFrequency.init_socket) 
- [`NodeTreeInterfaceSocketFloatMass.from_socket`](bpy.types.NodeTreeInterfaceSocketFloatMass.html#bpy.types.NodeTreeInterfaceSocketFloatMass.from_socket) 
- [`NodeTreeInterfaceSocketFloatMass.init_socket`](bpy.types.NodeTreeInterfaceSocketFloatMass.html#bpy.types.NodeTreeInterfaceSocketFloatMass.init_socket) 
- [`NodeTreeInterfaceSocketFloatPercentage.from_socket`](bpy.types.NodeTreeInterfaceSocketFloatPercentage.html#bpy.types.NodeTreeInterfaceSocketFloatPercentage.from_socket) 
- [`NodeTreeInterfaceSocketFloatPercentage.init_socket`](bpy.types.NodeTreeInterfaceSocketFloatPercentage.html#bpy.types.NodeTreeInterfaceSocketFloatPercentage.init_socket) 
- [`NodeTreeInterfaceSocketFloatPixel.from_socket`](bpy.types.NodeTreeInterfaceSocketFloatPixel.html#bpy.types.NodeTreeInterfaceSocketFloatPixel.from_socket) 
- [`NodeTreeInterfaceSocketFloatPixel.init_socket`](bpy.types.NodeTreeInterfaceSocketFloatPixel.html#bpy.types.NodeTreeInterfaceSocketFloatPixel.init_socket) 
- [`NodeTreeInterfaceSocketFloatTime.from_socket`](bpy.types.NodeTreeInterfaceSocketFloatTime.html#bpy.types.NodeTreeInterfaceSocketFloatTime.from_socket) 
- [`NodeTreeInterfaceSocketFloatTime.init_socket`](bpy.types.NodeTreeInterfaceSocketFloatTime.html#bpy.types.NodeTreeInterfaceSocketFloatTime.init_socket) 
- [`NodeTreeInterfaceSocketFloatTimeAbsolute.from_socket`](bpy.types.NodeTreeInterfaceSocketFloatTimeAbsolute.html#bpy.types.NodeTreeInterfaceSocketFloatTimeAbsolute.from_socket) 
- [`NodeTreeInterfaceSocketFloatTimeAbsolute.init_socket`](bpy.types.NodeTreeInterfaceSocketFloatTimeAbsolute.html#bpy.types.NodeTreeInterfaceSocketFloatTimeAbsolute.init_socket) 
- [`NodeTreeInterfaceSocketFloatUnsigned.from_socket`](bpy.types.NodeTreeInterfaceSocketFloatUnsigned.html#bpy.types.NodeTreeInterfaceSocketFloatUnsigned.from_socket) 
- [`NodeTreeInterfaceSocketFloatUnsigned.init_socket`](bpy.types.NodeTreeInterfaceSocketFloatUnsigned.html#bpy.types.NodeTreeInterfaceSocketFloatUnsigned.init_socket) 
- [`NodeTreeInterfaceSocketFloatWavelength.from_socket`](bpy.types.NodeTreeInterfaceSocketFloatWavelength.html#bpy.types.NodeTreeInterfaceSocketFloatWavelength.from_socket) 
- [`NodeTreeInterfaceSocketFloatWavelength.init_socket`](bpy.types.NodeTreeInterfaceSocketFloatWavelength.html#bpy.types.NodeTreeInterfaceSocketFloatWavelength.init_socket) 
- [`NodeTreeInterfaceSocketGeometry.from_socket`](bpy.types.NodeTreeInterfaceSocketGeometry.html#bpy.types.NodeTreeInterfaceSocketGeometry.from_socket) 
- [`NodeTreeInterfaceSocketGeometry.init_socket`](bpy.types.NodeTreeInterfaceSocketGeometry.html#bpy.types.NodeTreeInterfaceSocketGeometry.init_socket) 
- [`NodeTreeInterfaceSocketImage.from_socket`](bpy.types.NodeTreeInterfaceSocketImage.html#bpy.types.NodeTreeInterfaceSocketImage.from_socket) 
- [`NodeTreeInterfaceSocketImage.init_socket`](bpy.types.NodeTreeInterfaceSocketImage.html#bpy.types.NodeTreeInterfaceSocketImage.init_socket) 
- [`NodeTreeInterfaceSocketInt.from_socket`](bpy.types.NodeTreeInterfaceSocketInt.html#bpy.types.NodeTreeInterfaceSocketInt.from_socket) 
- [`NodeTreeInterfaceSocketInt.init_socket`](bpy.types.NodeTreeInterfaceSocketInt.html#bpy.types.NodeTreeInterfaceSocketInt.init_socket) 
- [`NodeTreeInterfaceSocketIntFactor.from_socket`](bpy.types.NodeTreeInterfaceSocketIntFactor.html#bpy.types.NodeTreeInterfaceSocketIntFactor.from_socket) 
- [`NodeTreeInterfaceSocketIntFactor.init_socket`](bpy.types.NodeTreeInterfaceSocketIntFactor.html#bpy.types.NodeTreeInterfaceSocketIntFactor.init_socket) 
- [`NodeTreeInterfaceSocketIntPercentage.from_socket`](bpy.types.NodeTreeInterfaceSocketIntPercentage.html#bpy.types.NodeTreeInterfaceSocketIntPercentage.from_socket) 
- [`NodeTreeInterfaceSocketIntPercentage.init_socket`](bpy.types.NodeTreeInterfaceSocketIntPercentage.html#bpy.types.NodeTreeInterfaceSocketIntPercentage.init_socket) 
- [`NodeTreeInterfaceSocketIntPixel.from_socket`](bpy.types.NodeTreeInterfaceSocketIntPixel.html#bpy.types.NodeTreeInterfaceSocketIntPixel.from_socket) 
- [`NodeTreeInterfaceSocketIntPixel.init_socket`](bpy.types.NodeTreeInterfaceSocketIntPixel.html#bpy.types.NodeTreeInterfaceSocketIntPixel.init_socket) 
- [`NodeTreeInterfaceSocketIntUnsigned.from_socket`](bpy.types.NodeTreeInterfaceSocketIntUnsigned.html#bpy.types.NodeTreeInterfaceSocketIntUnsigned.from_socket) 
- [`NodeTreeInterfaceSocketIntUnsigned.init_socket`](bpy.types.NodeTreeInterfaceSocketIntUnsigned.html#bpy.types.NodeTreeInterfaceSocketIntUnsigned.init_socket) 
- [`NodeTreeInterfaceSocketIntVector2D.from_socket`](bpy.types.NodeTreeInterfaceSocketIntVector2D.html#bpy.types.NodeTreeInterfaceSocketIntVector2D.from_socket) 
- [`NodeTreeInterfaceSocketIntVector2D.init_socket`](bpy.types.NodeTreeInterfaceSocketIntVector2D.html#bpy.types.NodeTreeInterfaceSocketIntVector2D.init_socket) 
- [`NodeTreeInterfaceSocketIntVector3D.from_socket`](bpy.types.NodeTreeInterfaceSocketIntVector3D.html#bpy.types.NodeTreeInterfaceSocketIntVector3D.from_socket) 
- [`NodeTreeInterfaceSocketIntVector3D.init_socket`](bpy.types.NodeTreeInterfaceSocketIntVector3D.html#bpy.types.NodeTreeInterfaceSocketIntVector3D.init_socket) 
- [`NodeTreeInterfaceSocketIntVectorFactor2D.from_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorFactor2D.html#bpy.types.NodeTreeInterfaceSocketIntVectorFactor2D.from_socket) 
- [`NodeTreeInterfaceSocketIntVectorFactor2D.init_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorFactor2D.html#bpy.types.NodeTreeInterfaceSocketIntVectorFactor2D.init_socket) 
- [`NodeTreeInterfaceSocketIntVectorFactor3D.from_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorFactor3D.html#bpy.types.NodeTreeInterfaceSocketIntVectorFactor3D.from_socket) 
- [`NodeTreeInterfaceSocketIntVectorFactor3D.init_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorFactor3D.html#bpy.types.NodeTreeInterfaceSocketIntVectorFactor3D.init_socket) 
- [`NodeTreeInterfaceSocketIntVectorPercentage2D.from_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorPercentage2D.html#bpy.types.NodeTreeInterfaceSocketIntVectorPercentage2D.from_socket) 
- [`NodeTreeInterfaceSocketIntVectorPercentage2D.init_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorPercentage2D.html#bpy.types.NodeTreeInterfaceSocketIntVectorPercentage2D.init_socket) 
- [`NodeTreeInterfaceSocketIntVectorPercentage3D.from_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorPercentage3D.html#bpy.types.NodeTreeInterfaceSocketIntVectorPercentage3D.from_socket) 
- [`NodeTreeInterfaceSocketIntVectorPercentage3D.init_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorPercentage3D.html#bpy.types.NodeTreeInterfaceSocketIntVectorPercentage3D.init_socket) 
- [`NodeTreeInterfaceSocketIntVectorPixel2D.from_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorPixel2D.html#bpy.types.NodeTreeInterfaceSocketIntVectorPixel2D.from_socket) 
- [`NodeTreeInterfaceSocketIntVectorPixel2D.init_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorPixel2D.html#bpy.types.NodeTreeInterfaceSocketIntVectorPixel2D.init_socket) 
- [`NodeTreeInterfaceSocketIntVectorPixel3D.from_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorPixel3D.html#bpy.types.NodeTreeInterfaceSocketIntVectorPixel3D.from_socket) 
- [`NodeTreeInterfaceSocketIntVectorPixel3D.init_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorPixel3D.html#bpy.types.NodeTreeInterfaceSocketIntVectorPixel3D.init_socket) 
- [`NodeTreeInterfaceSocketIntVectorUnsigned2D.from_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned2D.html#bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned2D.from_socket) 
- [`NodeTreeInterfaceSocketIntVectorUnsigned2D.init_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned2D.html#bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned2D.init_socket) 
- [`NodeTreeInterfaceSocketIntVectorUnsigned3D.from_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned3D.html#bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned3D.from_socket)   
- [`NodeTreeInterfaceSocketIntVectorUnsigned3D.init_socket`](bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned3D.html#bpy.types.NodeTreeInterfaceSocketIntVectorUnsigned3D.init_socket) 
- [`NodeTreeInterfaceSocketMaterial.from_socket`](bpy.types.NodeTreeInterfaceSocketMaterial.html#bpy.types.NodeTreeInterfaceSocketMaterial.from_socket) 
- [`NodeTreeInterfaceSocketMaterial.init_socket`](bpy.types.NodeTreeInterfaceSocketMaterial.html#bpy.types.NodeTreeInterfaceSocketMaterial.init_socket) 
- [`NodeTreeInterfaceSocketMatrix.from_socket`](bpy.types.NodeTreeInterfaceSocketMatrix.html#bpy.types.NodeTreeInterfaceSocketMatrix.from_socket) 
- [`NodeTreeInterfaceSocketMatrix.init_socket`](bpy.types.NodeTreeInterfaceSocketMatrix.html#bpy.types.NodeTreeInterfaceSocketMatrix.init_socket) 
- [`NodeTreeInterfaceSocketMenu.from_socket`](bpy.types.NodeTreeInterfaceSocketMenu.html#bpy.types.NodeTreeInterfaceSocketMenu.from_socket) 
- [`NodeTreeInterfaceSocketMenu.init_socket`](bpy.types.NodeTreeInterfaceSocketMenu.html#bpy.types.NodeTreeInterfaceSocketMenu.init_socket) 
- [`NodeTreeInterfaceSocketObject.from_socket`](bpy.types.NodeTreeInterfaceSocketObject.html#bpy.types.NodeTreeInterfaceSocketObject.from_socket) 
- [`NodeTreeInterfaceSocketObject.init_socket`](bpy.types.NodeTreeInterfaceSocketObject.html#bpy.types.NodeTreeInterfaceSocketObject.init_socket) 
- [`NodeTreeInterfaceSocketRotation.from_socket`](bpy.types.NodeTreeInterfaceSocketRotation.html#bpy.types.NodeTreeInterfaceSocketRotation.from_socket) 
- [`NodeTreeInterfaceSocketRotation.init_socket`](bpy.types.NodeTreeInterfaceSocketRotation.html#bpy.types.NodeTreeInterfaceSocketRotation.init_socket) 
- [`NodeTreeInterfaceSocketShader.from_socket`](bpy.types.NodeTreeInterfaceSocketShader.html#bpy.types.NodeTreeInterfaceSocketShader.from_socket) 
- [`NodeTreeInterfaceSocketShader.init_socket`](bpy.types.NodeTreeInterfaceSocketShader.html#bpy.types.NodeTreeInterfaceSocketShader.init_socket) 
- [`NodeTreeInterfaceSocketString.from_socket`](bpy.types.NodeTreeInterfaceSocketString.html#bpy.types.NodeTreeInterfaceSocketString.from_socket) 
- [`NodeTreeInterfaceSocketString.init_socket`](bpy.types.NodeTreeInterfaceSocketString.html#bpy.types.NodeTreeInterfaceSocketString.init_socket) 
- [`NodeTreeInterfaceSocketStringFilePath.from_socket`](bpy.types.NodeTreeInterfaceSocketStringFilePath.html#bpy.types.NodeTreeInterfaceSocketStringFilePath.from_socket) 
- [`NodeTreeInterfaceSocketStringFilePath.init_socket`](bpy.types.NodeTreeInterfaceSocketStringFilePath.html#bpy.types.NodeTreeInterfaceSocketStringFilePath.init_socket) 
- [`NodeTreeInterfaceSocketTexture.from_socket`](bpy.types.NodeTreeInterfaceSocketTexture.html#bpy.types.NodeTreeInterfaceSocketTexture.from_socket) 
- [`NodeTreeInterfaceSocketTexture.init_socket`](bpy.types.NodeTreeInterfaceSocketTexture.html#bpy.types.NodeTreeInterfaceSocketTexture.init_socket) 
- [`NodeTreeInterfaceSocketVector.from_socket`](bpy.types.NodeTreeInterfaceSocketVector.html#bpy.types.NodeTreeInterfaceSocketVector.from_socket) 
- [`NodeTreeInterfaceSocketVector.init_socket`](bpy.types.NodeTreeInterfaceSocketVector.html#bpy.types.NodeTreeInterfaceSocketVector.init_socket) 
- [`NodeTreeInterfaceSocketVector2D.from_socket`](bpy.types.NodeTreeInterfaceSocketVector2D.html#bpy.types.NodeTreeInterfaceSocketVector2D.from_socket) 
- [`NodeTreeInterfaceSocketVector2D.init_socket`](bpy.types.NodeTreeInterfaceSocketVector2D.html#bpy.types.NodeTreeInterfaceSocketVector2D.init_socket) 
- [`NodeTreeInterfaceSocketVector4D.from_socket`](bpy.types.NodeTreeInterfaceSocketVector4D.html#bpy.types.NodeTreeInterfaceSocketVector4D.from_socket) 
- [`NodeTreeInterfaceSocketVector4D.init_socket`](bpy.types.NodeTreeInterfaceSocketVector4D.html#bpy.types.NodeTreeInterfaceSocketVector4D.init_socket) 
- [`NodeTreeInterfaceSocketVectorAcceleration.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorAcceleration.html#bpy.types.NodeTreeInterfaceSocketVectorAcceleration.from_socket) 
- [`NodeTreeInterfaceSocketVectorAcceleration.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorAcceleration.html#bpy.types.NodeTreeInterfaceSocketVectorAcceleration.init_socket) 
- [`NodeTreeInterfaceSocketVectorAcceleration2D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorAcceleration2D.html#bpy.types.NodeTreeInterfaceSocketVectorAcceleration2D.from_socket) 
- [`NodeTreeInterfaceSocketVectorAcceleration2D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorAcceleration2D.html#bpy.types.NodeTreeInterfaceSocketVectorAcceleration2D.init_socket) 
- [`NodeTreeInterfaceSocketVectorAcceleration4D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorAcceleration4D.html#bpy.types.NodeTreeInterfaceSocketVectorAcceleration4D.from_socket) 
- [`NodeTreeInterfaceSocketVectorAcceleration4D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorAcceleration4D.html#bpy.types.NodeTreeInterfaceSocketVectorAcceleration4D.init_socket) 
- [`NodeTreeInterfaceSocketVectorDirection.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorDirection.html#bpy.types.NodeTreeInterfaceSocketVectorDirection.from_socket) 
- [`NodeTreeInterfaceSocketVectorDirection.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorDirection.html#bpy.types.NodeTreeInterfaceSocketVectorDirection.init_socket) 
- [`NodeTreeInterfaceSocketVectorDirection2D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorDirection2D.html#bpy.types.NodeTreeInterfaceSocketVectorDirection2D.from_socket) 
- [`NodeTreeInterfaceSocketVectorDirection2D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorDirection2D.html#bpy.types.NodeTreeInterfaceSocketVectorDirection2D.init_socket) 
- [`NodeTreeInterfaceSocketVectorDirection4D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorDirection4D.html#bpy.types.NodeTreeInterfaceSocketVectorDirection4D.from_socket) 
- [`NodeTreeInterfaceSocketVectorDirection4D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorDirection4D.html#bpy.types.NodeTreeInterfaceSocketVectorDirection4D.init_socket) 
- [`NodeTreeInterfaceSocketVectorEuler.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorEuler.html#bpy.types.NodeTreeInterfaceSocketVectorEuler.from_socket) 
- [`NodeTreeInterfaceSocketVectorEuler.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorEuler.html#bpy.types.NodeTreeInterfaceSocketVectorEuler.init_socket) 
- [`NodeTreeInterfaceSocketVectorEuler2D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorEuler2D.html#bpy.types.NodeTreeInterfaceSocketVectorEuler2D.from_socket) 
- [`NodeTreeInterfaceSocketVectorEuler2D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorEuler2D.html#bpy.types.NodeTreeInterfaceSocketVectorEuler2D.init_socket) 
- [`NodeTreeInterfaceSocketVectorEuler4D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorEuler4D.html#bpy.types.NodeTreeInterfaceSocketVectorEuler4D.from_socket) 
- [`NodeTreeInterfaceSocketVectorEuler4D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorEuler4D.html#bpy.types.NodeTreeInterfaceSocketVectorEuler4D.init_socket) 
- [`NodeTreeInterfaceSocketVectorFactor.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorFactor.html#bpy.types.NodeTreeInterfaceSocketVectorFactor.from_socket) 
- [`NodeTreeInterfaceSocketVectorFactor.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorFactor.html#bpy.types.NodeTreeInterfaceSocketVectorFactor.init_socket) 
- [`NodeTreeInterfaceSocketVectorFactor2D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorFactor2D.html#bpy.types.NodeTreeInterfaceSocketVectorFactor2D.from_socket) 
- [`NodeTreeInterfaceSocketVectorFactor2D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorFactor2D.html#bpy.types.NodeTreeInterfaceSocketVectorFactor2D.init_socket) 
- [`NodeTreeInterfaceSocketVectorFactor4D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorFactor4D.html#bpy.types.NodeTreeInterfaceSocketVectorFactor4D.from_socket) 
- [`NodeTreeInterfaceSocketVectorFactor4D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorFactor4D.html#bpy.types.NodeTreeInterfaceSocketVectorFactor4D.init_socket) 
- [`NodeTreeInterfaceSocketVectorPercentage.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorPercentage.html#bpy.types.NodeTreeInterfaceSocketVectorPercentage.from_socket) 
- [`NodeTreeInterfaceSocketVectorPercentage.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorPercentage.html#bpy.types.NodeTreeInterfaceSocketVectorPercentage.init_socket) 
- [`NodeTreeInterfaceSocketVectorPercentage2D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorPercentage2D.html#bpy.types.NodeTreeInterfaceSocketVectorPercentage2D.from_socket) 
- [`NodeTreeInterfaceSocketVectorPercentage2D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorPercentage2D.html#bpy.types.NodeTreeInterfaceSocketVectorPercentage2D.init_socket) 
- [`NodeTreeInterfaceSocketVectorPercentage4D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorPercentage4D.html#bpy.types.NodeTreeInterfaceSocketVectorPercentage4D.from_socket) 
- [`NodeTreeInterfaceSocketVectorPercentage4D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorPercentage4D.html#bpy.types.NodeTreeInterfaceSocketVectorPercentage4D.init_socket) 
- [`NodeTreeInterfaceSocketVectorPixel.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorPixel.html#bpy.types.NodeTreeInterfaceSocketVectorPixel.from_socket) 
- [`NodeTreeInterfaceSocketVectorPixel.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorPixel.html#bpy.types.NodeTreeInterfaceSocketVectorPixel.init_socket) 
- [`NodeTreeInterfaceSocketVectorPixel2D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorPixel2D.html#bpy.types.NodeTreeInterfaceSocketVectorPixel2D.from_socket) 
- [`NodeTreeInterfaceSocketVectorPixel2D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorPixel2D.html#bpy.types.NodeTreeInterfaceSocketVectorPixel2D.init_socket) 
- [`NodeTreeInterfaceSocketVectorPixel4D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorPixel4D.html#bpy.types.NodeTreeInterfaceSocketVectorPixel4D.from_socket) 
- [`NodeTreeInterfaceSocketVectorPixel4D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorPixel4D.html#bpy.types.NodeTreeInterfaceSocketVectorPixel4D.init_socket) 
- [`NodeTreeInterfaceSocketVectorTranslation.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorTranslation.html#bpy.types.NodeTreeInterfaceSocketVectorTranslation.from_socket) 
- [`NodeTreeInterfaceSocketVectorTranslation.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorTranslation.html#bpy.types.NodeTreeInterfaceSocketVectorTranslation.init_socket) 
- [`NodeTreeInterfaceSocketVectorTranslation2D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorTranslation2D.html#bpy.types.NodeTreeInterfaceSocketVectorTranslation2D.from_socket) 
- [`NodeTreeInterfaceSocketVectorTranslation2D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorTranslation2D.html#bpy.types.NodeTreeInterfaceSocketVectorTranslation2D.init_socket) 
- [`NodeTreeInterfaceSocketVectorTranslation4D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorTranslation4D.html#bpy.types.NodeTreeInterfaceSocketVectorTranslation4D.from_socket) 
- [`NodeTreeInterfaceSocketVectorTranslation4D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorTranslation4D.html#bpy.types.NodeTreeInterfaceSocketVectorTranslation4D.init_socket) 
- [`NodeTreeInterfaceSocketVectorVelocity.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorVelocity.html#bpy.types.NodeTreeInterfaceSocketVectorVelocity.from_socket) 
- [`NodeTreeInterfaceSocketVectorVelocity.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorVelocity.html#bpy.types.NodeTreeInterfaceSocketVectorVelocity.init_socket) 
- [`NodeTreeInterfaceSocketVectorVelocity2D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorVelocity2D.html#bpy.types.NodeTreeInterfaceSocketVectorVelocity2D.from_socket) 
- [`NodeTreeInterfaceSocketVectorVelocity2D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorVelocity2D.html#bpy.types.NodeTreeInterfaceSocketVectorVelocity2D.init_socket) 
- [`NodeTreeInterfaceSocketVectorVelocity4D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorVelocity4D.html#bpy.types.NodeTreeInterfaceSocketVectorVelocity4D.from_socket) 
- [`NodeTreeInterfaceSocketVectorVelocity4D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorVelocity4D.html#bpy.types.NodeTreeInterfaceSocketVectorVelocity4D.init_socket) 
- [`NodeTreeInterfaceSocketVectorXYZ.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorXYZ.html#bpy.types.NodeTreeInterfaceSocketVectorXYZ.from_socket) 
- [`NodeTreeInterfaceSocketVectorXYZ.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorXYZ.html#bpy.types.NodeTreeInterfaceSocketVectorXYZ.init_socket) 
- [`NodeTreeInterfaceSocketVectorXYZ2D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorXYZ2D.html#bpy.types.NodeTreeInterfaceSocketVectorXYZ2D.from_socket) 
- [`NodeTreeInterfaceSocketVectorXYZ2D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorXYZ2D.html#bpy.types.NodeTreeInterfaceSocketVectorXYZ2D.init_socket) 
- [`NodeTreeInterfaceSocketVectorXYZ4D.from_socket`](bpy.types.NodeTreeInterfaceSocketVectorXYZ4D.html#bpy.types.NodeTreeInterfaceSocketVectorXYZ4D.from_socket) 
- [`NodeTreeInterfaceSocketVectorXYZ4D.init_socket`](bpy.types.NodeTreeInterfaceSocketVectorXYZ4D.html#bpy.types.NodeTreeInterfaceSocketVectorXYZ4D.init_socket) 
- [`UILayout.template_node_link`](bpy.types.UILayout.html#bpy.types.UILayout.template_node_link) 
- [`UILayout.template_node_view`](bpy.types.UILayout.html#bpy.types.UILayout.template_node_view)
