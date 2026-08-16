# bpy.types.AnyType

# AnyType(bpy_struct)

 

base class — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct)

   class bpy.types.AnyType(bpy_struct) 

RNA type used for pointers to any possible data

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

  
- `bpy.context.property` 
- [`BoneCollection.assign`](bpy.types.BoneCollection.html#bpy.types.BoneCollection.assign) 
- [`BoneCollection.unassign`](bpy.types.BoneCollection.html#bpy.types.BoneCollection.unassign) 
- [`FCurve.update_autoflags`](bpy.types.FCurve.html#bpy.types.FCurve.update_autoflags) 
- [`Gizmo.target_set_prop`](bpy.types.Gizmo.html#bpy.types.Gizmo.target_set_prop) 
- [`KeyingSetInfo.generate`](bpy.types.KeyingSetInfo.html#bpy.types.KeyingSetInfo.generate) 
- [`Region.data`](bpy.types.Region.html#bpy.types.Region.data) 
- [`UILayout.context_pointer_set`](bpy.types.UILayout.html#bpy.types.UILayout.context_pointer_set) 
- [`UILayout.enum_item_description`](bpy.types.UILayout.html#bpy.types.UILayout.enum_item_description) 
- [`UILayout.enum_item_icon`](bpy.types.UILayout.html#bpy.types.UILayout.enum_item_icon) 
- [`UILayout.enum_item_name`](bpy.types.UILayout.html#bpy.types.UILayout.enum_item_name) 
- [`UILayout.icon`](bpy.types.UILayout.html#bpy.types.UILayout.icon) 
- [`UILayout.panel_prop`](bpy.types.UILayout.html#bpy.types.UILayout.panel_prop) 
- [`UILayout.prop`](bpy.types.UILayout.html#bpy.types.UILayout.prop) 
- [`UILayout.prop_decorator`](bpy.types.UILayout.html#bpy.types.UILayout.prop_decorator) 
- [`UILayout.prop_enum`](bpy.types.UILayout.html#bpy.types.UILayout.prop_enum) 
- [`UILayout.prop_menu_enum`](bpy.types.UILayout.html#bpy.types.UILayout.prop_menu_enum) 
- [`UILayout.prop_search`](bpy.types.UILayout.html#bpy.types.UILayout.prop_search) 
- [`UILayout.prop_search`](bpy.types.UILayout.html#bpy.types.UILayout.prop_search) 
- [`UILayout.prop_tabs_enum`](bpy.types.UILayout.html#bpy.types.UILayout.prop_tabs_enum) 
- [`UILayout.prop_tabs_enum`](bpy.types.UILayout.html#bpy.types.UILayout.prop_tabs_enum) 
- [`UILayout.prop_with_menu`](bpy.types.UILayout.html#bpy.types.UILayout.prop_with_menu) 
- [`UILayout.prop_with_popover`](bpy.types.UILayout.html#bpy.types.UILayout.prop_with_popover) 
- [`UILayout.props_enum`](bpy.types.UILayout.html#bpy.types.UILayout.props_enum) 
- [`UILayout.template_ID`](bpy.types.UILayout.html#bpy.types.UILayout.template_ID) 
- [`UILayout.template_ID_preview`](bpy.types.UILayout.html#bpy.types.UILayout.template_ID_preview) 
- [`UILayout.template_ID_session_uid`](bpy.types.UILayout.html#bpy.types.UILayout.template_ID_session_uid) 
- [`UILayout.template_ID_tabs`](bpy.types.UILayout.html#bpy.types.UILayout.template_ID_tabs) 
- [`UILayout.template_any_ID`](bpy.types.UILayout.html#bpy.types.UILayout.template_any_ID) 
- [`UILayout.template_cache_file`](bpy.types.UILayout.html#bpy.types.UILayout.template_cache_file) 
- [`UILayout.template_cache_file_layers`](bpy.types.UILayout.html#bpy.types.UILayout.template_cache_file_layers) 
- [`UILayout.template_cache_file_time_settings`](bpy.types.UILayout.html#bpy.types.UILayout.template_cache_file_time_settings) 
- [`UILayout.template_cache_file_velocity`](bpy.types.UILayout.html#bpy.types.UILayout.template_cache_file_velocity) 
- [`UILayout.template_color_picker`](bpy.types.UILayout.html#bpy.types.UILayout.template_color_picker)   
- [`UILayout.template_color_ramp`](bpy.types.UILayout.html#bpy.types.UILayout.template_color_ramp) 
- [`UILayout.template_colormanaged_view_settings`](bpy.types.UILayout.html#bpy.types.UILayout.template_colormanaged_view_settings) 
- [`UILayout.template_colorspace_settings`](bpy.types.UILayout.html#bpy.types.UILayout.template_colorspace_settings) 
- [`UILayout.template_component_menu`](bpy.types.UILayout.html#bpy.types.UILayout.template_component_menu) 
- [`UILayout.template_curve_mapping`](bpy.types.UILayout.html#bpy.types.UILayout.template_curve_mapping) 
- [`UILayout.template_curveprofile`](bpy.types.UILayout.html#bpy.types.UILayout.template_curveprofile) 
- [`UILayout.template_greasepencil_color`](bpy.types.UILayout.html#bpy.types.UILayout.template_greasepencil_color) 
- [`UILayout.template_histogram`](bpy.types.UILayout.html#bpy.types.UILayout.template_histogram) 
- [`UILayout.template_icon_view`](bpy.types.UILayout.html#bpy.types.UILayout.template_icon_view) 
- [`UILayout.template_image`](bpy.types.UILayout.html#bpy.types.UILayout.template_image) 
- [`UILayout.template_layers`](bpy.types.UILayout.html#bpy.types.UILayout.template_layers) 
- [`UILayout.template_layers`](bpy.types.UILayout.html#bpy.types.UILayout.template_layers) 
- [`UILayout.template_light_linking_collection`](bpy.types.UILayout.html#bpy.types.UILayout.template_light_linking_collection) 
- [`UILayout.template_list`](bpy.types.UILayout.html#bpy.types.UILayout.template_list) 
- [`UILayout.template_list`](bpy.types.UILayout.html#bpy.types.UILayout.template_list) 
- [`UILayout.template_marker`](bpy.types.UILayout.html#bpy.types.UILayout.template_marker) 
- [`UILayout.template_matrix`](bpy.types.UILayout.html#bpy.types.UILayout.template_matrix) 
- [`UILayout.template_movieclip`](bpy.types.UILayout.html#bpy.types.UILayout.template_movieclip) 
- [`UILayout.template_movieclip_information`](bpy.types.UILayout.html#bpy.types.UILayout.template_movieclip_information) 
- [`UILayout.template_palette`](bpy.types.UILayout.html#bpy.types.UILayout.template_palette) 
- [`UILayout.template_path_builder`](bpy.types.UILayout.html#bpy.types.UILayout.template_path_builder) 
- [`UILayout.template_search`](bpy.types.UILayout.html#bpy.types.UILayout.template_search) 
- [`UILayout.template_search`](bpy.types.UILayout.html#bpy.types.UILayout.template_search) 
- [`UILayout.template_search_preview`](bpy.types.UILayout.html#bpy.types.UILayout.template_search_preview) 
- [`UILayout.template_search_preview`](bpy.types.UILayout.html#bpy.types.UILayout.template_search_preview) 
- [`UILayout.template_track`](bpy.types.UILayout.html#bpy.types.UILayout.template_track) 
- [`UILayout.template_vectorscope`](bpy.types.UILayout.html#bpy.types.UILayout.template_vectorscope) 
- [`UILayout.template_waveform`](bpy.types.UILayout.html#bpy.types.UILayout.template_waveform) 
- [`UILayout.textbox`](bpy.types.UILayout.html#bpy.types.UILayout.textbox) 
- [`UILayout.textbox_with_state`](bpy.types.UILayout.html#bpy.types.UILayout.textbox_with_state) 
- [`UIList.draw_item`](bpy.types.UIList.html#bpy.types.UIList.draw_item) 
- [`UIList.draw_item`](bpy.types.UIList.html#bpy.types.UIList.draw_item) 
- [`UIList.draw_item`](bpy.types.UIList.html#bpy.types.UIList.draw_item) 
- [`UIList.filter_items`](bpy.types.UIList.html#bpy.types.UIList.filter_items)
