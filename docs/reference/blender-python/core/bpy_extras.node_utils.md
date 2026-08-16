# bpy_extras.node_utils

# bpy_extras submodule (bpy_extras.node_utils)

   bpy_extras.node_utils.connect_sockets(input, output) 

Connect sockets in a node tree.

 

This is useful because the links created through the normal Python API are invalid when one of the sockets is a virtual socket (grayed out sockets in Group Input and Group Output nodes).

 

It replaces node_tree.links.new(input, output)

  Parameters:  
- input ([`bpy.types.NodeSocket`](bpy.types.NodeSocket.html#bpy.types.NodeSocket)) – The input socket. 
- output ([`bpy.types.NodeSocket`](bpy.types.NodeSocket.html#bpy.types.NodeSocket)) – The output socket.   Returns: 

The created link, or `None` when the sockets cannot be connected.

  Return type: 

[`bpy.types.NodeLink`](bpy.types.NodeLink.html#bpy.types.NodeLink) | None

      bpy_extras.node_utils.find_base_socket_type(socket) 

Find the base class of the socket.

 

Sockets can have a subtype such as NodeSocketFloatFactor, but only the base type is allowed, e.g. NodeSocketFloat

  Parameters: 

socket ([`bpy.types.NodeSocket`](bpy.types.NodeSocket.html#bpy.types.NodeSocket)) – The socket to find the base type for.

  Returns: 

The base socket type identifier.

  Return type: 

str

      bpy_extras.node_utils.find_node_input(node, name) 

Find a node input socket by name.

 

Note that names are not unique, returns the first match.

  Parameters:  
- node ([`bpy.types.Node`](bpy.types.Node.html#bpy.types.Node)) – The node to search. 
- name (str) – The name of the input socket.   Returns: 

The input socket or None if not found.

  Return type: 

[`bpy.types.NodeSocket`](bpy.types.NodeSocket.html#bpy.types.NodeSocket) | None
