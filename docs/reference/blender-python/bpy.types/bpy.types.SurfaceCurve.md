# bpy.types.SurfaceCurve

# SurfaceCurve(Curve)

 

base classes — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct), [`ID`](bpy.types.ID.html#bpy.types.ID), [`Curve`](bpy.types.Curve.html#bpy.types.Curve)

   class bpy.types.SurfaceCurve(Curve) 

Curve data-block used for storing surfaces

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
- [`Curve.shape_keys`](bpy.types.Curve.html#bpy.types.Curve.shape_keys) 
- [`Curve.splines`](bpy.types.Curve.html#bpy.types.Curve.splines) 
- [`Curve.path_duration`](bpy.types.Curve.html#bpy.types.Curve.path_duration) 
- [`Curve.use_path`](bpy.types.Curve.html#bpy.types.Curve.use_path) 
- [`Curve.use_path_follow`](bpy.types.Curve.html#bpy.types.Curve.use_path_follow) 
- [`Curve.use_path_clamp`](bpy.types.Curve.html#bpy.types.Curve.use_path_clamp) 
- [`Curve.use_stretch`](bpy.types.Curve.html#bpy.types.Curve.use_stretch) 
- [`Curve.use_deform_bounds`](bpy.types.Curve.html#bpy.types.Curve.use_deform_bounds) 
- [`Curve.use_radius`](bpy.types.Curve.html#bpy.types.Curve.use_radius) 
- [`Curve.bevel_mode`](bpy.types.Curve.html#bpy.types.Curve.bevel_mode)   
- [`Curve.bevel_profile`](bpy.types.Curve.html#bpy.types.Curve.bevel_profile) 
- [`Curve.bevel_resolution`](bpy.types.Curve.html#bpy.types.Curve.bevel_resolution) 
- [`Curve.offset`](bpy.types.Curve.html#bpy.types.Curve.offset) 
- [`Curve.extrude`](bpy.types.Curve.html#bpy.types.Curve.extrude) 
- [`Curve.bevel_depth`](bpy.types.Curve.html#bpy.types.Curve.bevel_depth) 
- [`Curve.resolution_u`](bpy.types.Curve.html#bpy.types.Curve.resolution_u) 
- [`Curve.resolution_v`](bpy.types.Curve.html#bpy.types.Curve.resolution_v) 
- [`Curve.render_resolution_u`](bpy.types.Curve.html#bpy.types.Curve.render_resolution_u) 
- [`Curve.render_resolution_v`](bpy.types.Curve.html#bpy.types.Curve.render_resolution_v) 
- [`Curve.eval_time`](bpy.types.Curve.html#bpy.types.Curve.eval_time) 
- [`Curve.bevel_object`](bpy.types.Curve.html#bpy.types.Curve.bevel_object) 
- [`Curve.taper_object`](bpy.types.Curve.html#bpy.types.Curve.taper_object) 
- [`Curve.dimensions`](bpy.types.Curve.html#bpy.types.Curve.dimensions) 
- [`Curve.fill_mode`](bpy.types.Curve.html#bpy.types.Curve.fill_mode) 
- [`Curve.fill_solver`](bpy.types.Curve.html#bpy.types.Curve.fill_solver) 
- [`Curve.fill_rule`](bpy.types.Curve.html#bpy.types.Curve.fill_rule) 
- [`Curve.twist_mode`](bpy.types.Curve.html#bpy.types.Curve.twist_mode) 
- [`Curve.taper_radius_mode`](bpy.types.Curve.html#bpy.types.Curve.taper_radius_mode) 
- [`Curve.bevel_factor_mapping_start`](bpy.types.Curve.html#bpy.types.Curve.bevel_factor_mapping_start) 
- [`Curve.bevel_factor_mapping_end`](bpy.types.Curve.html#bpy.types.Curve.bevel_factor_mapping_end) 
- [`Curve.twist_smooth`](bpy.types.Curve.html#bpy.types.Curve.twist_smooth) 
- [`Curve.use_fill_caps`](bpy.types.Curve.html#bpy.types.Curve.use_fill_caps) 
- [`Curve.use_map_taper`](bpy.types.Curve.html#bpy.types.Curve.use_map_taper) 
- [`Curve.use_auto_texspace`](bpy.types.Curve.html#bpy.types.Curve.use_auto_texspace) 
- [`Curve.texspace_location`](bpy.types.Curve.html#bpy.types.Curve.texspace_location) 
- [`Curve.texspace_size`](bpy.types.Curve.html#bpy.types.Curve.texspace_size) 
- [`Curve.materials`](bpy.types.Curve.html#bpy.types.Curve.materials) 
- [`Curve.bevel_factor_start`](bpy.types.Curve.html#bpy.types.Curve.bevel_factor_start) 
- [`Curve.bevel_factor_end`](bpy.types.Curve.html#bpy.types.Curve.bevel_factor_end) 
- [`Curve.is_editmode`](bpy.types.Curve.html#bpy.types.Curve.is_editmode) 
- [`Curve.animation_data`](bpy.types.Curve.html#bpy.types.Curve.animation_data) 
- [`Curve.cycles`](bpy.types.Curve.html#bpy.types.Curve.cycles)     

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
- [`Curve.transform`](bpy.types.Curve.html#bpy.types.Curve.transform) 
- [`Curve.validate_material_indices`](bpy.types.Curve.html#bpy.types.Curve.validate_material_indices) 
- [`Curve.update_gpu_tag`](bpy.types.Curve.html#bpy.types.Curve.update_gpu_tag) 
- [`Curve.bl_rna_get_subclass`](bpy.types.Curve.html#bpy.types.Curve.bl_rna_get_subclass) 
- [`Curve.bl_rna_get_subclass_py`](bpy.types.Curve.html#bpy.types.Curve.bl_rna_get_subclass_py)
