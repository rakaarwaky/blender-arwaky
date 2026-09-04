# bpy.types.GreasePencilDrawing

# GreasePencilDrawing(bpy_struct)

 

base class — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct)

   class bpy.types.GreasePencilDrawing(bpy_struct) 

A Grease Pencil drawing

   attributes 

Geometry attributes (default None, readonly)

  Type: 

[`AttributeGroupGreasePencilDrawing`](bpy.types.AttributeGroupGreasePencilDrawing.html#bpy.types.AttributeGroupGreasePencilDrawing)[[`Attribute`](bpy.types.Attribute.html#bpy.types.Attribute)]

      color_attributes 

Geometry color attributes (default None, readonly)

  Type: 

[`AttributeGroupGreasePencilDrawing`](bpy.types.AttributeGroupGreasePencilDrawing.html#bpy.types.AttributeGroupGreasePencilDrawing)[[`Attribute`](bpy.types.Attribute.html#bpy.types.Attribute)]

      curve_offsets 

Offset indices of the first point of each curve (default None, readonly)

  Type: 

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.html#bpy.types.bpy_prop_collection)[[`IntAttributeValue`](bpy.types.IntAttributeValue.html#bpy.types.IntAttributeValue)]

      type 

Drawing type (default `'DRAWING'`, readonly)

  Type: 

Literal[‘DRAWING’, ‘REFERENCE’]

      user_count 

The number of keyframes this drawing is used by (in [-inf, inf], default 0, readonly)

  Type: 

int

      strokes 

Return a collection of all the Grease Pencil strokes in this drawing.

  

Note

 

This API should not be used for performance critical operations. Use the `GreasePencilDrawing.attributes` API instead.

   

Note

 

When point/curves count of a drawing is changed, the slice returned by this call prior to the change is no longer valid. You need to get the new stroke slice via `drawing.strokes[n]`.

  

(readonly)

    add_strokes(sizes) 

Add new strokes with provided sizes at the end

  Parameters: 

sizes (Sequence[int]) – Sizes, The number of points in each stroke (array of 1 items, in [1, inf])

      remove_strokes(*, indices=(0,)) 

Remove all strokes. If indices are provided, remove only the strokes with the given indices.

  Parameters: 

indices (Sequence[int]) – Indices, The indices of the strokes to remove (array of 1 items, in [0, inf], optional)

      resize_strokes(sizes, *, indices=(0,)) 

Resize all existing strokes. If indices are provided, resize only the strokes with the given indices. If the new size for a stroke is smaller, the stroke is trimmed. If the new size for a stroke is larger, the new end values are default initialized.

  Parameters:  
- sizes (Sequence[int]) – Sizes, The number of points in each stroke (array of 1 items, in [1, inf]) 
- indices (Sequence[int]) – Indices, The indices of the stroke to resize (array of 1 items, in [0, inf], optional)       reorder_strokes(new_indices) 

Reorder the strokes by the new indices.

  Parameters: 

new_indices (Sequence[int]) – New indices, The new index for each of the strokes (array of 1 items, in [0, inf])

      set_types(*, type='CATMULL_ROM', indices=(0,)) 

Set the curve type. If indices are provided, set only the types with the given curve indices.

  Parameters:  
- type (Literal[[Curves Type Items](bpy_types_enum_items/curves_type_items.html#rna-enum-curves-type-items)]) – Type, (optional) 
- indices (Sequence[int]) – Indices, The indices of the curves to resize (array of 1 items, in [0, inf], optional)       tag_positions_changed() 

Indicate that the positions of points in the drawing have changed

    vertex_group_assign(vgroup_name, indices_ptr, weight) 

Assign points to vertex group

  Parameters:  
- vgroup_name (str) – Vertex Group Name, Name of the vertex group (never None) 
- indices_ptr (Sequence[int]) – Indices, The point indices to assign the weight to (array of 1 items, in [-inf, inf]) 
- weight (float) – Vertex weight (in [0, 1])       vertex_group_remove(vgroup_name, indices_ptr) 

Remove points from vertex group

  Parameters:  
- vgroup_name (str) – Vertex Group Name, Name of the vertex group (never None) 
- indices_ptr (Sequence[int]) – Indices, The point indices to remove from the vertex group (array of 1 items, in [-inf, inf])       set_vertex_weights(vertex_group_name, indices, weights, *, assign_mode='REPLACE') 

Set the weights of vertices in a grease pencil drawing

  Parameters:  
- vertex_group_name (str) – Vertex Group Name, Name of the vertex group (never None) 
- indices (Sequence[int]) – Indices, The point indices in the vertex group to modify (array of 1 items, in [-inf, inf]) 
- weights (Sequence[float]) – Weights, The weight for each corresponding index in the indices array (array of 1 items, in [0, 1]) 
- assign_mode (Literal['REPLACE', 'ADD', 'SUBTRACT']) – 

(optional)

  
- `REPLACE` Replace – Replace. 
- `ADD` Add – Add. 
- `SUBTRACT` Subtract – Subtract.       classmethod bl_rna_get_subclass(id, default=None, /)  Parameters:  
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

  
- [`GreasePencilFrame.drawing`](bpy.types.GreasePencilFrame.html#bpy.types.GreasePencilFrame.drawing)
