# bpy.types.Curves

# Curves(ID)

 

base classes — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct), [`ID`](bpy.types.ID.html#bpy.types.ID)

   class bpy.types.Curves(ID) 

Hair data-block for hair curves

   animation_data 

Animation data for this data-block (readonly)

  Type: 

[`AnimData`](bpy.types.AnimData.html#bpy.types.AnimData) | None

      attributes 

Geometry attributes (default None, readonly)

  Type: 

[`AttributeGroupCurves`](bpy.types.AttributeGroupCurves.html#bpy.types.AttributeGroupCurves)[[`Attribute`](bpy.types.Attribute.html#bpy.types.Attribute)]

      color_attributes 

Geometry color attributes (default None, readonly)

  Type: 

[`AttributeGroupCurves`](bpy.types.AttributeGroupCurves.html#bpy.types.AttributeGroupCurves)[[`Attribute`](bpy.types.Attribute.html#bpy.types.Attribute)]

      curve_offset_data 

(default None, readonly)

  Type: 

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.html#bpy.types.bpy_prop_collection)[[`IntAttributeValue`](bpy.types.IntAttributeValue.html#bpy.types.IntAttributeValue)]

      curves 

All curves in the data-block (default None, readonly)

  Type: 

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.html#bpy.types.bpy_prop_collection)[[`CurveSlice`](bpy.types.CurveSlice.html#bpy.types.CurveSlice)]

      materials 

(default None, readonly)

  Type: 

[`IDMaterials`](bpy.types.IDMaterials.html#bpy.types.IDMaterials)[[`Material`](bpy.types.Material.html#bpy.types.Material)]

      normals 

The curve normal value at each of the curve’s control points (default None, readonly)

  Type: 

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.html#bpy.types.bpy_prop_collection)[[`FloatVectorValueReadOnly`](bpy.types.FloatVectorValueReadOnly.html#bpy.types.FloatVectorValueReadOnly)]

      points 

Control points of all curves (default None, readonly)

  Type: 

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.html#bpy.types.bpy_prop_collection)[[`CurvePoint`](bpy.types.CurvePoint.html#bpy.types.CurvePoint)]

      position_data 

(default None, readonly)

  Type: 

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.html#bpy.types.bpy_prop_collection)[[`FloatVectorAttributeValue`](bpy.types.FloatVectorAttributeValue.html#bpy.types.FloatVectorAttributeValue)]

      selection_domain 

(default `'POINT'`)

  Type: 

Literal[[Attribute Curves Domain Items](bpy_types_enum_items/attribute_curves_domain_items.html#rna-enum-attribute-curves-domain-items)]

      surface 

Mesh object that the curves can be attached to

  Type: 

[`Object`](bpy.types.Object.html#bpy.types.Object) | None

      surface_collision_distance 

Distance to keep the curves away from the surface (in [1.192e-07, inf], default 0.005)

  Type: 

float

      surface_uv_map 

The name of the attribute on the surface mesh used to define the attachment of each curve (default “”, never None)

  Type: 

str

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

      use_sculpt_collision 

Enable collision with the surface while sculpting (default False)

  Type: 

bool

      add_curves(sizes) 

add_curves

  Parameters: 

sizes (Sequence[int]) – Sizes, The number of points in each curve (array of 1 items, in [0, inf])

      remove_curves(*, indices=(0,)) 

Remove all curves. If indices are provided, remove only the curves with the given indices.

  Parameters: 

indices (Sequence[int]) – Indices, The indices of the curves to remove (array of 1 items, in [0, inf], optional)

      resize_curves(sizes, *, indices=(0,)) 

Resize all existing curves. If indices are provided, resize only the curves with the given indices. If the new size for a curve is smaller, the curve is trimmed. If the new size for a curve is larger, the new end values are default initialized.

  Parameters:  
- sizes (Sequence[int]) – Sizes, The number of points in each curve (array of 1 items, in [1, inf]) 
- indices (Sequence[int]) – Indices, The indices of the curves to resize (array of 1 items, in [0, inf], optional)       reorder_curves(new_indices) 

Reorder the curves by the new indices.

  Parameters: 

new_indices (Sequence[int]) – New indices, The new index for each of the curves (array of 1 items, in [0, inf])

      set_types(*, type='CATMULL_ROM', indices=(0,)) 

Set the curve type. If indices are provided, set only the types with the given curve indices.

  Parameters:  
- type (Literal[[Curves Type Items](bpy_types_enum_items/curves_type_items.html#rna-enum-curves-type-items)]) – Type, (optional) 
- indices (Sequence[int]) – Indices, The indices of the curves to resize (array of 1 items, in [0, inf], optional)       unit_test_compare(*, curves=None, threshold=7.1526e-06) 

unit_test_compare

  Parameters:  
- curves (`Curves` | None) – Curves to compare to (optional) 
- threshold (float) – Threshold, Comparison tolerance threshold (in [0, inf], optional)   Returns: 

Return value, String description of result of comparison (never None)

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

## References

  
- `bpy.context.curves` 
- [`BlendData.hair_curves`](bpy.types.BlendData.html#bpy.types.BlendData.hair_curves) 
- [`BlendDataHairCurves.new`](bpy.types.BlendDataHairCurves.html#bpy.types.BlendDataHairCurves.new)   
- [`BlendDataHairCurves.remove`](bpy.types.BlendDataHairCurves.html#bpy.types.BlendDataHairCurves.remove) 
- `Curves.unit_test_compare`
