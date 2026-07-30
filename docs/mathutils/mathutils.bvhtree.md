# mathutils.bvhtree

# BVHTree Utilities (mathutils.bvhtree)

 

BVH tree structures for proximity searches and ray casts on geometry.

   class mathutils.bvhtree.BVHTree   classmethod FromBMesh(bmesh, *, epsilon=0.0) 

BVH tree based on `BMesh` data.

  Parameters:  
- bmesh (`BMesh`) – BMesh data. 
- epsilon (float) – Increase the threshold for detecting overlap and raycast hits.   Returns: 

BVHTree from BMesh data.

  Return type: 

`BVHTree`

      classmethod FromObject(object, depsgraph, *, deform=True, cage=False, epsilon=0.0) 

BVH tree based on `Object` data.

  Parameters:  
- object (`Object`) – Mesh object. 
- depsgraph (`Depsgraph`) – Depsgraph to use for evaluating the mesh. 
- deform (bool) – Use mesh with deformations. 
- cage (bool) – Use modifiers cage. 
- epsilon (float) – Increase the threshold for detecting overlap and raycast hits.   Returns: 

BVHTree from Object data.

  Return type: 

`BVHTree`

      classmethod FromPolygons(vertices, polygons, *, all_triangles=False, epsilon=0.0) 

BVH tree constructed from geometry passed in as arguments.

  Parameters:  
- vertices (Sequence[Sequence[float]]) – float triplets each representing `(x, y, z)` coordinates. 
- polygons (Sequence[Sequence[int]]) – Sequence of polygons, each containing indices to the vertices argument. 
- all_triangles (bool) – Use when all polygons are triangles for more efficient conversion. 
- epsilon (float) – Increase the threshold for detecting overlap and raycast hits.   Returns: 

BVHTree from polygon data.

  Return type: 

`BVHTree`

      find_nearest(origin, distance=1.84467e+19, /) 

Find the nearest element (typically face index) to a point.

  Parameters:  
- origin (`Vector`) – Find nearest element to this point. 
- distance (float) – Maximum distance threshold.   Returns: 

Returns a tuple: (position, normal, index, distance), Values will all be None if no hit is found.

  Return type: 

tuple[`Vector` | None, `Vector` | None, int | None, float | None]

      find_nearest_range(origin, distance=1.84467e+19, /) 

Find the nearest elements (typically face index) to a point in the distance range.

  Parameters:  
- origin (`Vector`) – Find nearest elements to this point. 
- distance (float) – Maximum distance threshold.   Returns: 

Returns a list of tuples (position, normal, index, distance)

  Return type: 

list[tuple[`Vector`, `Vector`, int, float]]

      overlap(other_tree, /) 

Find overlapping indices between 2 trees.

  Parameters: 

other_tree (`BVHTree`) – Other tree to perform overlap test on.

  Returns: 

Returns a list of unique index pairs, the first index referencing this tree, the second referencing the other_tree.

  Return type: 

list[tuple[int, int]]

      ray_cast(origin, direction, distance=sys.float_info.max, /) 

Cast a ray onto the geometry.

  Parameters:  
- origin (`Vector`) – Start location of the ray. 
- direction (`Vector`) – Direction of the ray (normalized internally). 
- distance (float) – Maximum distance threshold.   Returns: 

Returns a tuple: (position, normal, index, distance), Values will all be None if no hit is found.

  Return type: 

tuple[`Vector` | None, `Vector` | None, int | None, float | None]
