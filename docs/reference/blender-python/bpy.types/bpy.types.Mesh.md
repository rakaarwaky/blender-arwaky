# bpy.types.Mesh

# Mesh(ID)

  

## Mesh Data

 

The mesh data is accessed in object mode and intended for compact storage, for more flexible mesh editing from Python see [`bmesh`](bmesh.html#module-bmesh).

 

Blender stores 4 main arrays to define mesh geometry.

  
- `Mesh.vertices` (3 points in space) 
- `Mesh.edges` (reference 2 vertices) 
- `Mesh.loops` (reference a single vertex and edge) 
- `Mesh.polygons`: (reference a range of loops)  

Each polygon references a slice in the loop array, this way, polygons do not store vertices or corner data such as UVs directly, only a reference to loops that the polygon uses.

 

`Mesh.loops`, `Mesh.uv_layers` `Mesh.vertex_colors` are all aligned so the same polygon loop indices can be used to find the UVs and vertex colors as with as the vertices.

 

To compare mesh API options see: [NGons and Tessellation Faces](info_gotchas_meshes.html#info-gotcha-mesh-faces)

 

This example script prints the vertices and UVs for each polygon, assumes the active object is a mesh with UVs.

 

```python
import bpy

me = bpy.context.object.data
uv_layer = me.uv_layers.active.data

for poly in me.polygons:
    print("Polygon index: {:d}, length: {:d}".format(poly.index, poly.loop_total))

    # Range is used here to show how the polygons reference loops,
    # for convenience 'poly.loop_indices' can be used instead.
    for loop_index in range(poly.loop_start, poly.loop_start + poly.loop_total):
        print("    Vertex: {:d}".format(me.loops[loop_index].vertex_index))
        print("    UV: {!r}".format(uv_layer[loop_index].uv))
```

  

base classes — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct), [`ID`](bpy.types.ID.html#bpy.types.ID)

   class bpy.types.Mesh(ID) 

Mesh data-block defining geometric surfaces

   animation_data 

Animation data for this data-block (readonly)

  Type: 

[`AnimData`](bpy.types.AnimData.html#bpy.types.AnimData) | None

      attributes 

Geometry attributes (default None, readonly)

  Type: 

[`AttributeGroupMesh`](bpy.types.AttributeGroupMesh.html#bpy.types.AttributeGroupMesh)[[`Attribute`](bpy.types.Attribute.html#bpy.types.Attribute)]

      auto_texspace 

Adjust active object’s texture space automatically when transforming object (default True)

  Type: 

bool

      color_attributes 

Geometry color attributes (default None, readonly)

  Type: 

[`AttributeGroupMesh`](bpy.types.AttributeGroupMesh.html#bpy.types.AttributeGroupMesh)[[`Attribute`](bpy.types.Attribute.html#bpy.types.Attribute)]

      corner_normals 

The “slit” normal direction of each face corner, influenced by vertex normals, sharp faces, sharp edges, and custom normals. May be empty. (default None, readonly)

  Type: 

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.html#bpy.types.bpy_prop_collection)[[`MeshNormalValue`](bpy.types.MeshNormalValue.html#bpy.types.MeshNormalValue)]

      cycles 

Cycles mesh settings (readonly)

  Type: 

`CyclesMeshSettings` | None

      edges 

Edges of the mesh (default None, readonly)

  Type: 

[`MeshEdges`](bpy.types.MeshEdges.html#bpy.types.MeshEdges)[[`MeshEdge`](bpy.types.MeshEdge.html#bpy.types.MeshEdge)]

      has_custom_normals 

True if there is custom normal data for this mesh (default False, readonly)

  Type: 

bool

      is_editmode 

True when used in editmode (default False, readonly)

  Type: 

bool

      loop_triangle_polygons 

The face index for each loop triangle (default None, readonly)

  Type: 

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.html#bpy.types.bpy_prop_collection)[[`ReadOnlyInteger`](bpy.types.ReadOnlyInteger.html#bpy.types.ReadOnlyInteger)]

      loop_triangles 

Tessellation of mesh polygons into triangles (default None, readonly)

  Type: 

[`MeshLoopTriangles`](bpy.types.MeshLoopTriangles.html#bpy.types.MeshLoopTriangles)[[`MeshLoopTriangle`](bpy.types.MeshLoopTriangle.html#bpy.types.MeshLoopTriangle)]

      loops 

Loops of the mesh (face corners) (default None, readonly)

  Type: 

[`MeshLoops`](bpy.types.MeshLoops.html#bpy.types.MeshLoops)[[`MeshLoop`](bpy.types.MeshLoop.html#bpy.types.MeshLoop)]

      materials 

(default None, readonly)

  Type: 

[`IDMaterials`](bpy.types.IDMaterials.html#bpy.types.IDMaterials)[[`Material`](bpy.types.Material.html#bpy.types.Material)]

      normals_domain 

The attribute domain that gives enough information to represent the mesh’s normals (default `'FACE'`, readonly)

  Type: 

Literal[‘POINT’, ‘FACE’, ‘CORNER’]

      polygon_normals 

The normal direction of each face, defined by the winding order and position of its vertices (default None, readonly)

  Type: 

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.html#bpy.types.bpy_prop_collection)[[`MeshNormalValue`](bpy.types.MeshNormalValue.html#bpy.types.MeshNormalValue)]

      polygons 

Polygons of the mesh (default None, readonly)

  Type: 

[`MeshPolygons`](bpy.types.MeshPolygons.html#bpy.types.MeshPolygons)[[`MeshPolygon`](bpy.types.MeshPolygon.html#bpy.types.MeshPolygon)]

      radial_symmetry 

Number of mirrored regions around a central axis (array of 3 items, in [1, 64], default (1, 1, 1))

  Type: 

[`bpy_prop_array`](bpy.types.bpy_prop_array.html#bpy.types.bpy_prop_array)[int]

      remesh_mode 

(default `'VOXEL'`)

  
- `VOXEL` Voxel – Use the voxel remesher. 
- `QUAD` Quad – Use the quad remesher.   Type: 

Literal[‘VOXEL’, ‘QUAD’]

      remesh_voxel_adaptivity 

Reduces the final face count by simplifying geometry where detail is not needed, generating triangles. A value greater than 0 disables Fix Poles. (in [0, 1], default 0.0)

  Type: 

float

      remesh_voxel_size 

Size of the voxel in object space used for volume evaluation. Lower values preserve finer details. (in [0, inf], default 0.1)

  Type: 

float

      shape_keys 

(readonly)

  Type: 

[`Key`](bpy.types.Key.html#bpy.types.Key) | None

      skin_vertices 

All skin vertices (default None, readonly)

  Type: 

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.html#bpy.types.bpy_prop_collection)[[`MeshSkinVertexLayer`](bpy.types.MeshSkinVertexLayer.html#bpy.types.MeshSkinVertexLayer)]

      texco_mesh 

Derive texture coordinates from another mesh

  Type: 

`Mesh` | None

      texspace_location 

Texture space location (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

  Type: 

[`mathutils.Vector`](mathutils.html#mathutils.Vector)

      texspace_size 

Texture space size (array of 3 items, in [-inf, inf], default (1.0, 1.0, 1.0))

  Type: 

[`mathutils.Vector`](mathutils.html#mathutils.Vector)

      texture_mesh 

Use another mesh for texture indices (vertex indices must be aligned)

  Type: 

`Mesh` | None

      total_edge_sel 

Selected edge count in editmode (in [0, inf], default 0, readonly)

  Type: 

int

      total_face_sel 

Selected face count in editmode (in [0, inf], default 0, readonly)

  Type: 

int

      total_vert_sel 

Selected vertex count in editmode (in [0, inf], default 0, readonly)

  Type: 

int

      use_auto_texspace 

Adjust active object’s texture space automatically when transforming object (default True)

  Type: 

bool

      use_mirror_topology 

Use topology based mirroring (for when both sides of mesh have matching, unique topology) (default False)

  Type: 

bool

      use_mirror_vertex_groups 

Mirror the left/right vertex groups when painting. The symmetry axis is determined by the symmetry settings. (default True)

  Type: 

bool

      use_mirror_x 

Enable symmetry in the X axis (default False)

  Type: 

bool

      use_mirror_y 

Enable symmetry in the Y axis (default False)

  Type: 

bool

      use_mirror_z 

Enable symmetry in the Z axis (default False)

  Type: 

bool

      use_paint_bone_selection 

Bone selection during painting (default True)

  Type: 

bool

      use_paint_mask 

Face selection masking for painting (default False)

  Type: 

bool

      use_paint_mask_vertex 

Vertex selection masking for painting (default False)

  Type: 

bool

      use_remesh_fix_poles 

Produces fewer poles and a better topology flow (default False)

  Type: 

bool

      use_remesh_preserve_attributes 

Transfer all attributes to the new mesh (default False)

  Type: 

bool

      use_remesh_preserve_volume 

Projects the mesh to preserve the volume and details of the original mesh (default False)

  Type: 

bool

      uv_layer_clone 

UV loop layer to be used as cloning source

  Type: 

[`MeshUVLoopLayer`](bpy.types.MeshUVLoopLayer.html#bpy.types.MeshUVLoopLayer) | None

      uv_layer_clone_index 

Clone UV loop layer index (in [0, inf], default 0)

  Type: 

int

      uv_layer_stencil 

UV loop layer to mask the painted area

  Type: 

[`MeshUVLoopLayer`](bpy.types.MeshUVLoopLayer.html#bpy.types.MeshUVLoopLayer) | None

      uv_layer_stencil_index 

Mask UV loop layer index (in [0, inf], default 0)

  Type: 

int

      uv_layers 

All UV loop layers (default None, readonly)

  Type: 

[`UVLoopLayers`](bpy.types.UVLoopLayers.html#bpy.types.UVLoopLayers)[[`MeshUVLoopLayer`](bpy.types.MeshUVLoopLayer.html#bpy.types.MeshUVLoopLayer)]

      vertex_colors 

Legacy vertex color layers. Deprecated, use color attributes instead. (default None, readonly)

  Type: 

[`LoopColors`](bpy.types.LoopColors.html#bpy.types.LoopColors)[[`MeshLoopColorLayer`](bpy.types.MeshLoopColorLayer.html#bpy.types.MeshLoopColorLayer)]

      vertex_normals 

The normal direction of each vertex, defined as the average of the surrounding face normals (default None, readonly)

  Type: 

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.html#bpy.types.bpy_prop_collection)[[`MeshNormalValue`](bpy.types.MeshNormalValue.html#bpy.types.MeshNormalValue)]

      vertices 

Vertices of the mesh (default None, readonly)

  Type: 

[`MeshVertices`](bpy.types.MeshVertices.html#bpy.types.MeshVertices)[[`MeshVertex`](bpy.types.MeshVertex.html#bpy.types.MeshVertex)]

      edge_creases 

Edge crease values for subdivision surface, corresponding to the “crease_edge” attribute.

 

(readonly)

    edge_keys 

(readonly)

    vertex_creases 

Vertex crease values for subdivision surface, corresponding to the “crease_vert” attribute.

 

(readonly)

    vertex_paint_mask 

Mask values for sculpting and painting, corresponding to the “.sculpt_mask” attribute.

 

(readonly)

    transform(matrix, *, shape_keys=False) 

Transform mesh vertices by a matrix (Warning: inverts normals if matrix is negative)

  Parameters:  
- matrix ([`mathutils.Matrix`](mathutils.html#mathutils.Matrix) | Sequence[Sequence[float]]) – Matrix (multi-dimensional array of 4 * 4 items, in [-inf, inf]) 
- shape_keys (bool) – Transform Shape Keys (optional)       flip_normals() 

Invert winding of all polygons (clears tessellation, does not handle custom normals)

    set_sharp_from_angle(*, angle=3.14159) 

Reset and fill the “sharp_edge” attribute based on the angle of faces neighboring manifold edges

  Parameters: 

angle (float) – Angle, Angle between faces beyond which edges are marked sharp (in [0, 3.14159], optional)

      split_faces() 

Split faces based on the edge angle

    calc_tangents(*, uvmap='') 

Compute tangents and bitangent signs, to be used together with the custom normals to get a complete tangent space for normal mapping (custom normals are also computed if not yet present)

  Parameters: 

uvmap (str) – Name of the UV map to use for tangent space computation (optional, never None)

      free_tangents() 

Free tangents

    calc_loop_triangles() 

Calculate loop triangle tessellation (supports editmode too)

    calc_smooth_groups(*, use_bitflags=False, use_boundary_vertices_for_bitflags=False) 

Calculate smooth groups from sharp edges

  Parameters:  
- use_bitflags (bool) – Produce bitflags groups instead of simple numeric values (optional) 
- use_boundary_vertices_for_bitflags (bool) – Also consider different smoothgroups sharing only vertices (but without any common edge) as neighbors, preventing them from sharing the same bitflag value. Only effective when `use_bitflags` is set. WARNING: Will overflow (run out of available bits) easily with some types of topology, e.g. large fans of sharp edges (optional)   Returns: 

`poly_groups`, Smooth Groups, [`bpy_prop_array`](bpy.types.bpy_prop_array.html#bpy.types.bpy_prop_array)[int]

 

`groups`, Total number of groups, int

  Return type: 

tuple[[`bpy_prop_array`](bpy.types.bpy_prop_array.html#bpy.types.bpy_prop_array)[int], int]

      normals_split_custom_set(normals) 

Define custom normals of this mesh (use zero-vectors to keep auto ones)

  Parameters: 

normals (Sequence[Sequence[float]]) – Normals (multi-dimensional array of 1 * 3 items, in [-1, 1])

      normals_split_custom_set_from_vertices(normals) 

Define custom normals of this mesh, from vertices’ normals (use zero-vectors to keep auto ones)

  Parameters: 

normals (Sequence[Sequence[float]]) – Normals (multi-dimensional array of 1 * 3 items, in [-1, 1])

      update(*, calc_edges=False, calc_edges_loose=False) 

update

  Parameters:  
- calc_edges (bool) – Calculate Edges, Force recalculation of edges (optional) 
- calc_edges_loose (bool) – Calculate Loose Edges, Calculate the loose state of each edge (optional)       update_gpu_tag() 

update_gpu_tag

    unit_test_compare(*, mesh=None, threshold=7.1526e-06) 

unit_test_compare

  Parameters:  
- mesh (`Mesh` | None) – Mesh to compare to (optional) 
- threshold (float) – Threshold, Comparison tolerance threshold (in [0, inf], optional)   Returns: 

Return value, String description of result of comparison (never None)

  Return type: 

str

      clear_geometry() 

Remove all geometry from the mesh. Note that this does not free shape keys or materials.

    validate(*, verbose=False, clean_customdata=True) 

Validate geometry, return True when the mesh has had invalid geometry corrected/removed

  Parameters:  
- verbose (bool) – Verbose, Output information about the errors found (optional) 
- clean_customdata (bool) – Clean Custom Data, Deprecated, has no effect (optional)   Returns: 

Result

  Return type: 

bool

      validate_material_indices() 

Validate material indices of polygons, return True when the mesh has had invalid indices corrected (to default 0)

  Returns: 

Result

  Return type: 

bool

      count_selected_items() 

Return the number of selected items (vert, edge, face)

  Returns: 

Result, (array of 3 items, in [0, inf])

  Return type: 

[`bpy_prop_array`](bpy.types.bpy_prop_array.html#bpy.types.bpy_prop_array)[int]

      edge_creases_ensure() 

Ensure the “crease_edge” attribute exists, creating it if needed.

  Returns: 

The edge crease attribute.

  Return type: 

[`FloatAttribute`](bpy.types.FloatAttribute.html#bpy.types.FloatAttribute)

      edge_creases_remove()    from_pydata(vertices, edges, faces, shade_flat=True) 

Make a mesh from a list of vertices/edges/faces Until we have a nicer way to make geometry, use this.

  Parameters:  
- vertices (Iterable[Sequence[float]]) – float triplets each representing (X, Y, Z) eg: [(0.0, 1.0, 0.5), …]. 
- edges (Iterable[Sequence[int]]) – 

int pairs, each pair contains two indices to the vertices argument. eg: [(1, 2), …]

 

When an empty iterable is passed in, the edges are inferred from the polygons. 
- faces (Iterable[Sequence[int]]) – iterator of faces, each faces contains three or more indices to the vertices argument. eg: [(5, 6, 8, 9), (1, 2, 3), …] 
- shade_flat (bool) – When true, mark new faces as flat-shaded.     

Warning

 

Invalid mesh data (out of range indices, edges with matching indices, 2 sided faces… etc) are not prevented. If the data used for mesh creation isn’t known to be valid, run `Mesh.validate` after this function.

     shade_flat() 

Render and display faces uniform, using face normals, setting the “sharp_face” attribute true for every face

    shade_smooth() 

Render and display faces smooth, using interpolated vertex normals, removing the “sharp_face” attribute

    vertex_creases_ensure() 

Ensure the “crease_vert” attribute exists, creating it if needed.

  Returns: 

The vertex crease attribute.

  Return type: 

[`FloatAttribute`](bpy.types.FloatAttribute.html#bpy.types.FloatAttribute)

      vertex_creases_remove()    vertex_paint_mask_ensure() 

Ensure the “.sculpt_mask” attribute exists, creating it if needed.

  Returns: 

The vertex paint mask attribute.

  Return type: 

[`FloatAttribute`](bpy.types.FloatAttribute.html#bpy.types.FloatAttribute)

      vertex_paint_mask_remove()    classmethod bl_rna_get_subclass(id, default=None, /)  Parameters:  
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

  
- `bpy.context.mesh` 
- [`BlendData.meshes`](bpy.types.BlendData.html#bpy.types.BlendData.meshes) 
- [`BlendDataMeshes.new`](bpy.types.BlendDataMeshes.html#bpy.types.BlendDataMeshes.new) 
- [`BlendDataMeshes.new_from_object`](bpy.types.BlendDataMeshes.html#bpy.types.BlendDataMeshes.new_from_object) 
- [`BlendDataMeshes.remove`](bpy.types.BlendDataMeshes.html#bpy.types.BlendDataMeshes.remove)   
- `Mesh.texco_mesh` 
- `Mesh.texture_mesh` 
- `Mesh.unit_test_compare` 
- [`Object.to_mesh`](bpy.types.Object.html#bpy.types.Object.to_mesh)
