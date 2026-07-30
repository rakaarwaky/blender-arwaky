# bpy.types.MeshLoopTriangle

# MeshLoopTriangle(bpy_struct)

 

base class — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct)

   class bpy.types.MeshLoopTriangle(bpy_struct) 

Tessellated triangle in a Mesh data-block

   area 

Area of this triangle (in [0, inf], default 0.0, readonly)

  Type: 

float

      index 

Index of this loop triangle (in [0, inf], default 0, readonly)

  Type: 

int

      loops 

Indices of mesh loops that make up the triangle (array of 3 items, in [0, inf], default (0, 0, 0), readonly)

  Type: 

[`bpy_prop_array`](bpy.types.bpy_prop_array.html#bpy.types.bpy_prop_array)[int]

      material_index 

Material slot index of this triangle (in [0, inf], default 0, readonly)

  Type: 

int

      normal 

Local space unit length normal vector for this triangle (array of 3 items, in [-1, 1], default (0.0, 0.0, 0.0), readonly)

  Type: 

[`mathutils.Vector`](mathutils.html#mathutils.Vector)

      polygon_index 

Index of mesh face that the triangle is a part of (in [0, inf], default 0, readonly)

  Type: 

int

      split_normals 

Local space unit length custom normal vectors of the face corners of this triangle (multi-dimensional array of 3 * 3 items, in [-1, 1], default ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)), readonly)

  Type: 

[`bpy_prop_array`](bpy.types.bpy_prop_array.html#bpy.types.bpy_prop_array)[[`bpy_prop_array`](bpy.types.bpy_prop_array.html#bpy.types.bpy_prop_array)[float]]

      use_smooth 

(default False, readonly)

  Type: 

bool

      vertices 

Indices of triangle vertices (array of 3 items, in [0, inf], default (0, 0, 0), readonly)

  Type: 

[`bpy_prop_array`](bpy.types.bpy_prop_array.html#bpy.types.bpy_prop_array)[int]

      center 

The midpoint of the face.

 

(readonly)

    edge_keys 

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

  
- [`Mesh.loop_triangles`](bpy.types.Mesh.html#bpy.types.Mesh.loop_triangles)
