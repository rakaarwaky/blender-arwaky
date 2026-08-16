# bpy.types.NODE_AST_compositor

# NODE_AST_compositor(AssetShelf)

 

base classes — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct), [`AssetShelf`](bpy.types.AssetShelf.html#bpy.types.AssetShelf)

   class bpy.types.NODE_AST_compositor(AssetShelf)   classmethod bl_rna_get_subclass(id, default=None, /)  Parameters:  
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
- [`AssetShelf.bl_idname`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.bl_idname) 
- [`AssetShelf.bl_space_type`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.bl_space_type) 
- [`AssetShelf.bl_options`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.bl_options) 
- [`AssetShelf.bl_activate_operator`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.bl_activate_operator) 
- [`AssetShelf.bl_drag_operator`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.bl_drag_operator) 
- [`AssetShelf.bl_default_preview_size`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.bl_default_preview_size) 
- [`AssetShelf.filter_action`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.filter_action) 
- [`AssetShelf.filter_armature`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.filter_armature) 
- [`AssetShelf.filter_brush`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.filter_brush) 
- [`AssetShelf.filter_camera`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.filter_camera) 
- [`AssetShelf.filter_cachefile`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.filter_cachefile) 
- [`AssetShelf.filter_curve`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.filter_curve) 
- [`AssetShelf.filter_annotations`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.filter_annotations) 
- [`AssetShelf.filter_grease_pencil`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.filter_grease_pencil) 
- [`AssetShelf.filter_group`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.filter_group) 
- [`AssetShelf.filter_curves`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.filter_curves) 
- [`AssetShelf.filter_image`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.filter_image) 
- [`AssetShelf.filter_light`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.filter_light) 
- [`AssetShelf.filter_light_probe`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.filter_light_probe) 
- [`AssetShelf.filter_linestyle`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.filter_linestyle) 
- [`AssetShelf.filter_lattice`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.filter_lattice) 
- [`AssetShelf.filter_material`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.filter_material)   
- [`AssetShelf.filter_metaball`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.filter_metaball) 
- [`AssetShelf.filter_movie_clip`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.filter_movie_clip) 
- [`AssetShelf.filter_mesh`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.filter_mesh) 
- [`AssetShelf.filter_mask`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.filter_mask) 
- [`AssetShelf.filter_node_tree`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.filter_node_tree) 
- [`AssetShelf.filter_object`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.filter_object) 
- [`AssetShelf.filter_particle_settings`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.filter_particle_settings) 
- [`AssetShelf.filter_palette`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.filter_palette) 
- [`AssetShelf.filter_paint_curve`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.filter_paint_curve) 
- [`AssetShelf.filter_pointcloud`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.filter_pointcloud) 
- [`AssetShelf.filter_scene`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.filter_scene) 
- [`AssetShelf.filter_speaker`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.filter_speaker) 
- [`AssetShelf.filter_sound`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.filter_sound) 
- [`AssetShelf.filter_texture`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.filter_texture) 
- [`AssetShelf.filter_text`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.filter_text) 
- [`AssetShelf.filter_font`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.filter_font) 
- [`AssetShelf.filter_volume`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.filter_volume) 
- [`AssetShelf.filter_world`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.filter_world) 
- [`AssetShelf.filter_work_space`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.filter_work_space) 
- [`AssetShelf.asset_library_reference`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.asset_library_reference) 
- [`AssetShelf.show_names`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.show_names) 
- [`AssetShelf.preview_size`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.preview_size) 
- [`AssetShelf.search_filter`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.search_filter)     

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
- [`AssetShelf.poll`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.poll) 
- [`AssetShelf.asset_poll`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.asset_poll) 
- [`AssetShelf.get_active_asset`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.get_active_asset) 
- [`AssetShelf.draw_context_menu`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.draw_context_menu) 
- [`AssetShelf.bl_rna_get_subclass`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.bl_rna_get_subclass) 
- [`AssetShelf.bl_rna_get_subclass_py`](bpy.types.AssetShelf.html#bpy.types.AssetShelf.bl_rna_get_subclass_py)
