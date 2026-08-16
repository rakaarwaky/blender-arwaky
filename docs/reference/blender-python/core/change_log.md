# change_log

# Change Log

 

Changes in Blender’s Python API between releases.

  

## 5.1 to 5.2

  

### bpy.types.AnnotationStroke

  

#### Added

  
- [`bpy.types.AnnotationStroke.display_mode`](bpy.types.AnnotationStroke.html#bpy.types.AnnotationStroke.display_mode)     

### bpy.types.AssetMetaData

  

#### Added

  
- [`bpy.types.AssetMetaData.preferred_import_method`](bpy.types.AssetMetaData.html#bpy.types.AssetMetaData.preferred_import_method) 
- [`bpy.types.AssetMetaData.use_preferred_import_method`](bpy.types.AssetMetaData.html#bpy.types.AssetMetaData.use_preferred_import_method)     

### bpy.types.AssetRepresentation

  

#### Added

  
- [`bpy.types.AssetRepresentation.is_online`](bpy.types.AssetRepresentation.html#bpy.types.AssetRepresentation.is_online) 
- [`bpy.types.AssetRepresentation.owner_asset_library`](bpy.types.AssetRepresentation.html#bpy.types.AssetRepresentation.owner_asset_library)     

### bpy.types.BlendData

  

#### Added

  
- [`bpy.types.BlendData.all_ids`](bpy.types.BlendData.html#bpy.types.BlendData.all_ids)     

### bpy.types.Brush

  

#### Added

  
- [`bpy.types.Brush.minimum_distance`](bpy.types.Brush.html#bpy.types.Brush.minimum_distance) 
- [`bpy.types.Brush.project_ray_direction_type`](bpy.types.Brush.html#bpy.types.Brush.project_ray_direction_type)    

#### Removed

  
- automasking_boundary_edges_propagation_steps 
- automasking_cavity_blur_steps 
- automasking_cavity_factor 
- automasking_start_normal_falloff 
- automasking_start_normal_limit 
- automasking_view_normal_falloff 
- automasking_view_normal_limit 
- use_automasking_boundary_edges 
- use_automasking_boundary_face_sets 
- use_automasking_cavity_inverted 
- use_automasking_custom_cavity_curve 
- use_automasking_face_sets 
- use_automasking_start_normal 
- use_automasking_topology 
- use_automasking_view_normal 
- use_automasking_view_occlusion    

#### Renamed

  
- automasking_cavity_curve -> [`bpy.types.Brush.mesh_automasking_settings`](bpy.types.Brush.html#bpy.types.Brush.mesh_automasking_settings) 
- use_automasking_cavity -> [`bpy.types.Brush.use_bidirectional`](bpy.types.Brush.html#bpy.types.Brush.use_bidirectional)     

### bpy.types.BrushGpencilSettings

  

#### Added

  
- [`bpy.types.BrushGpencilSettings.conversion_threshold`](bpy.types.BrushGpencilSettings.html#bpy.types.BrushGpencilSettings.conversion_threshold) 
- [`bpy.types.BrushGpencilSettings.curve_type`](bpy.types.BrushGpencilSettings.html#bpy.types.BrushGpencilSettings.curve_type) 
- [`bpy.types.BrushGpencilSettings.fill_gap_factor`](bpy.types.BrushGpencilSettings.html#bpy.types.BrushGpencilSettings.fill_gap_factor) 
- [`bpy.types.BrushGpencilSettings.fill_internal_gaps`](bpy.types.BrushGpencilSettings.html#bpy.types.BrushGpencilSettings.fill_internal_gaps) 
- [`bpy.types.BrushGpencilSettings.fill_solver`](bpy.types.BrushGpencilSettings.html#bpy.types.BrushGpencilSettings.fill_solver)     

### bpy.types.ColorStrip

  

#### Added

  
- [`bpy.types.ColorStrip.height`](bpy.types.ColorStrip.html#bpy.types.ColorStrip.height) 
- [`bpy.types.ColorStrip.width`](bpy.types.ColorStrip.html#bpy.types.ColorStrip.width)     

### bpy.types.CompositorNodeOutputFile

  

#### Added

  
- [`bpy.types.CompositorNodeOutputFile.use_file_extension`](bpy.types.CompositorNodeOutputFile.html#bpy.types.CompositorNodeOutputFile.use_file_extension)     

### bpy.types.CompositorNodeTree

  

#### Added

  
- [`bpy.types.CompositorNodeTree.is_strip_modifier`](bpy.types.CompositorNodeTree.html#bpy.types.CompositorNodeTree.is_strip_modifier)     

### bpy.types.CyclesRenderLayerSettings

  

#### Added

  
- `bpy.types.CyclesRenderLayerSettings.denoising_pass_follow_reflections` 
- `bpy.types.CyclesRenderLayerSettings.denoising_pass_use_albedo_roughness_weighting`     

### bpy.types.CyclesRenderSettings

  

#### Added

  
- `bpy.types.CyclesRenderSettings.debug_texture_cache_preserve_unused` 
- `bpy.types.CyclesRenderSettings.debug_use_texture_cache_eviction` 
- `bpy.types.CyclesRenderSettings.texture_resolution` 
- `bpy.types.CyclesRenderSettings.texture_resolution_render` 
- `bpy.types.CyclesRenderSettings.use_pixel_jitter`     

### bpy.types.CyclesWorldSettings

  

#### Added

  
- `bpy.types.CyclesWorldSettings.use_shadows`     

### bpy.types.FileAssetSelectParams

  

#### Added

  
- [`bpy.types.FileAssetSelectParams.asset_access`](bpy.types.FileAssetSelectParams.html#bpy.types.FileAssetSelectParams.asset_access) 
- [`bpy.types.FileAssetSelectParams.asset_catalog_visibility`](bpy.types.FileAssetSelectParams.html#bpy.types.FileAssetSelectParams.asset_catalog_visibility)     

### bpy.types.FunctionNodeInputString

  

#### Added

  
- [`bpy.types.FunctionNodeInputString.textbox_state`](bpy.types.FunctionNodeInputString.html#bpy.types.FunctionNodeInputString.textbox_state)     

### bpy.types.FunctionNodeInputVector

  

#### Added

  
- [`bpy.types.FunctionNodeInputVector.vector_dimensions`](bpy.types.FunctionNodeInputVector.html#bpy.types.FunctionNodeInputVector.vector_dimensions)     

### bpy.types.GreasePencil

  

#### Added

  
- [`bpy.types.GreasePencil.unit_test_compare`](bpy.types.GreasePencil.html#bpy.types.GreasePencil.unit_test_compare)     

### bpy.types.GreasePencilLayerMasks

  

#### Added

  
- [`bpy.types.GreasePencilLayerMasks.add`](bpy.types.GreasePencilLayerMasks.html#bpy.types.GreasePencilLayerMasks.add) 
- [`bpy.types.GreasePencilLayerMasks.remove`](bpy.types.GreasePencilLayerMasks.html#bpy.types.GreasePencilLayerMasks.remove)     

### bpy.types.GreasePencilLineartModifier

  

#### Added

  
- [`bpy.types.GreasePencilLineartModifier.fill_strokes`](bpy.types.GreasePencilLineartModifier.html#bpy.types.GreasePencilLineartModifier.fill_strokes)     

### bpy.types.IDOverrideLibraryPropertyOperation

  

#### Added

  
- [`bpy.types.IDOverrideLibraryPropertyOperation.label`](bpy.types.IDOverrideLibraryPropertyOperation.html#bpy.types.IDOverrideLibraryPropertyOperation.label) 
- [`bpy.types.IDOverrideLibraryPropertyOperation.tooltip`](bpy.types.IDOverrideLibraryPropertyOperation.html#bpy.types.IDOverrideLibraryPropertyOperation.tooltip)     

### bpy.types.LightProbePlane

  

#### Added

  
- [`bpy.types.LightProbePlane.parallax_distance`](bpy.types.LightProbePlane.html#bpy.types.LightProbePlane.parallax_distance)     

### bpy.types.MaskLayer

  

#### Added

  
- [`bpy.types.MaskLayer.fill_solver`](bpy.types.MaskLayer.html#bpy.types.MaskLayer.fill_solver)     

### bpy.types.MaterialGPencilStyle

  

#### Added

  
- [`bpy.types.MaterialGPencilStyle.placement_count`](bpy.types.MaterialGPencilStyle.html#bpy.types.MaterialGPencilStyle.placement_count) 
- [`bpy.types.MaterialGPencilStyle.placement_density`](bpy.types.MaterialGPencilStyle.html#bpy.types.MaterialGPencilStyle.placement_density) 
- [`bpy.types.MaterialGPencilStyle.placement_mode`](bpy.types.MaterialGPencilStyle.html#bpy.types.MaterialGPencilStyle.placement_mode) 
- [`bpy.types.MaterialGPencilStyle.placement_radius_spacing`](bpy.types.MaterialGPencilStyle.html#bpy.types.MaterialGPencilStyle.placement_radius_spacing) 
- [`bpy.types.MaterialGPencilStyle.random_hue_factor`](bpy.types.MaterialGPencilStyle.html#bpy.types.MaterialGPencilStyle.random_hue_factor) 
- [`bpy.types.MaterialGPencilStyle.random_noise_scale`](bpy.types.MaterialGPencilStyle.html#bpy.types.MaterialGPencilStyle.random_noise_scale) 
- [`bpy.types.MaterialGPencilStyle.random_rotation_factor`](bpy.types.MaterialGPencilStyle.html#bpy.types.MaterialGPencilStyle.random_rotation_factor) 
- [`bpy.types.MaterialGPencilStyle.random_saturation_factor`](bpy.types.MaterialGPencilStyle.html#bpy.types.MaterialGPencilStyle.random_saturation_factor) 
- [`bpy.types.MaterialGPencilStyle.random_size_factor`](bpy.types.MaterialGPencilStyle.html#bpy.types.MaterialGPencilStyle.random_size_factor) 
- [`bpy.types.MaterialGPencilStyle.random_strength_factor`](bpy.types.MaterialGPencilStyle.html#bpy.types.MaterialGPencilStyle.random_strength_factor) 
- [`bpy.types.MaterialGPencilStyle.random_value_factor`](bpy.types.MaterialGPencilStyle.html#bpy.types.MaterialGPencilStyle.random_value_factor) 
- [`bpy.types.MaterialGPencilStyle.use_randomization`](bpy.types.MaterialGPencilStyle.html#bpy.types.MaterialGPencilStyle.use_randomization)     

### bpy.types.Menu

  

#### Function Arguments

  
- [`bpy.types.Menu.draw_preset`](bpy.types.Menu.html#bpy.types.Menu.draw_preset) (self, context), was (self, _context) 
- [`bpy.types.Menu.path_menu`](bpy.types.Menu.html#bpy.types.Menu.path_menu) (self, searchpaths, operator, props_default, prop_filepath, filter_ext, filter_path, display_name, add_operator, add_operator_props, translate, recursive_paths), was (self, searchpaths, operator, props_default, prop_filepath, filter_ext, filter_path, display_name, add_operator, add_operator_props, translate)     

### bpy.types.MovieClipProxy

  

#### Removed

  
- build_record_run 
- timecode     

### bpy.types.Node

  

#### Added

  
- [`bpy.types.Node.panel_states`](bpy.types.Node.html#bpy.types.Node.panel_states)    

#### Function Arguments

  
- [`bpy.types.Node.poll`](bpy.types.Node.html#bpy.types.Node.poll) (ntree), was (_ntree)     

### bpy.types.NodeCustomGroup

  

#### Function Arguments

  
- `bpy.types.NodeCustomGroup.poll` (ntree), was (_ntree)     

### bpy.types.NodeTreeInterfacePanel

  

#### Added

  
- [`bpy.types.NodeTreeInterfacePanel.identifier`](bpy.types.NodeTreeInterfacePanel.html#bpy.types.NodeTreeInterfacePanel.identifier)     

### bpy.types.NodesModifier

  

#### Added

  
- [`bpy.types.NodesModifier.is_input_used`](bpy.types.NodesModifier.html#bpy.types.NodesModifier.is_input_used) 
- [`bpy.types.NodesModifier.is_input_visible`](bpy.types.NodesModifier.html#bpy.types.NodesModifier.is_input_visible) 
- [`bpy.types.NodesModifier.properties`](bpy.types.NodesModifier.html#bpy.types.NodesModifier.properties)    

#### Removed

  
- bl_system_properties_get     

### bpy.types.Object

  

#### Added

  
- [`bpy.types.Object.parent_bone_head_tail_factor`](bpy.types.Object.html#bpy.types.Object.parent_bone_head_tail_factor) 
- [`bpy.types.Object.visible_raycast`](bpy.types.Object.html#bpy.types.Object.visible_raycast)     

### bpy.types.Paint

  

#### Removed

  
- eraser_brush    

#### Renamed

  
- eraser_brush_asset_reference -> [`bpy.types.Paint.mesh_automasking_settings`](bpy.types.Paint.html#bpy.types.Paint.mesh_automasking_settings)     

### bpy.types.Panel

  

#### Added

  
- [`bpy.types.Panel.bl_icon`](bpy.types.Panel.html#bpy.types.Panel.bl_icon) 
- [`bpy.types.Panel.bl_icon_value`](bpy.types.Panel.html#bpy.types.Panel.bl_icon_value)     

### bpy.types.Preferences

  

#### Added

  
- [`bpy.types.Preferences.asset_libraries`](bpy.types.Preferences.html#bpy.types.Preferences.asset_libraries)     

### bpy.types.PreferencesExperimental

  

#### Removed

  
- use_geometry_bundle    

#### Renamed

  
- use_geometry_nodes_lists -> [`bpy.types.PreferencesExperimental.use_collection_importer`](bpy.types.PreferencesExperimental.html#bpy.types.PreferencesExperimental.use_collection_importer) 
- use_geometry_nodes_lists -> [`bpy.types.PreferencesExperimental.use_remote_asset_libraries`](bpy.types.PreferencesExperimental.html#bpy.types.PreferencesExperimental.use_remote_asset_libraries)     

### bpy.types.PreferencesFilePaths

  

#### Added

  
- [`bpy.types.PreferencesFilePaths.save_modified_images`](bpy.types.PreferencesFilePaths.html#bpy.types.PreferencesFilePaths.save_modified_images) 
- [`bpy.types.PreferencesFilePaths.texture_cache_directory`](bpy.types.PreferencesFilePaths.html#bpy.types.PreferencesFilePaths.texture_cache_directory)     

### bpy.types.PreferencesSystem

  

#### Added

  
- [`bpy.types.PreferencesSystem.geometry_nodes_stack_limit`](bpy.types.PreferencesSystem.html#bpy.types.PreferencesSystem.geometry_nodes_stack_limit) 
- [`bpy.types.PreferencesSystem.show_panel_tabs_compact`](bpy.types.PreferencesSystem.html#bpy.types.PreferencesSystem.show_panel_tabs_compact)    

#### Removed

  
- image_draw_method     

### bpy.types.PreferencesView

  

#### Added

  
- [`bpy.types.PreferencesView.asset_access`](bpy.types.PreferencesView.html#bpy.types.PreferencesView.asset_access) 
- [`bpy.types.PreferencesView.date_format`](bpy.types.PreferencesView.html#bpy.types.PreferencesView.date_format) 
- [`bpy.types.PreferencesView.time_format`](bpy.types.PreferencesView.html#bpy.types.PreferencesView.time_format)     

### bpy.types.RaytraceEEVEE

  

#### Added

  
- [`bpy.types.RaytraceEEVEE.backface_radiance_scale`](bpy.types.RaytraceEEVEE.html#bpy.types.RaytraceEEVEE.backface_radiance_scale) 
- [`bpy.types.RaytraceEEVEE.use_backface_hit`](bpy.types.RaytraceEEVEE.html#bpy.types.RaytraceEEVEE.use_backface_hit)     

### bpy.types.RenderSettings

  

#### Added

  
- [`bpy.types.RenderSettings.anisotropic_filter`](bpy.types.RenderSettings.html#bpy.types.RenderSettings.anisotropic_filter) 
- [`bpy.types.RenderSettings.save_output`](bpy.types.RenderSettings.html#bpy.types.RenderSettings.save_output) 
- [`bpy.types.RenderSettings.use_auto_generate_texture_cache`](bpy.types.RenderSettings.html#bpy.types.RenderSettings.use_auto_generate_texture_cache) 
- [`bpy.types.RenderSettings.use_texture_cache`](bpy.types.RenderSettings.html#bpy.types.RenderSettings.use_texture_cache)     

### bpy.types.SCENE_UL_gltf2_filter_action

  

#### Added

  
- `bpy.types.SCENE_UL_gltf2_filter_action.filter_items`     

### bpy.types.Scene

  

#### Added

  
- [`bpy.types.Scene.allow_preroll`](bpy.types.Scene.html#bpy.types.Scene.allow_preroll) 
- [`bpy.types.Scene.playback_loop_mode`](bpy.types.Scene.html#bpy.types.Scene.playback_loop_mode)     

### bpy.types.SceneEEVEE

  

#### Removed

  
- fast_gi_thickness_far     

### bpy.types.SceneStrip

  

#### Added

  
- [`bpy.types.SceneStrip.view_layer`](bpy.types.SceneStrip.html#bpy.types.SceneStrip.view_layer)     

### bpy.types.Sculpt

  

#### Removed

  
- automasking_boundary_edges_propagation_steps 
- automasking_cavity_blur_steps 
- automasking_cavity_curve 
- automasking_cavity_curve_op 
- automasking_cavity_factor 
- automasking_start_normal_falloff 
- automasking_start_normal_limit 
- automasking_view_normal_falloff 
- automasking_view_normal_limit 
- use_automasking_boundary_edges 
- use_automasking_boundary_face_sets 
- use_automasking_cavity 
- use_automasking_cavity_inverted 
- use_automasking_custom_cavity_curve 
- use_automasking_face_sets 
- use_automasking_start_normal 
- use_automasking_topology 
- use_automasking_view_normal 
- use_automasking_view_occlusion     

### bpy.types.SequencerCompositorModifierData

  

#### Added

  
- [`bpy.types.SequencerCompositorModifierData.properties`](bpy.types.SequencerCompositorModifierData.html#bpy.types.SequencerCompositorModifierData.properties) 
- [`bpy.types.SequencerCompositorModifierData.show_group_selector`](bpy.types.SequencerCompositorModifierData.html#bpy.types.SequencerCompositorModifierData.show_group_selector)     

### bpy.types.SequencerPreviewOverlay

  

#### Added

  
- [`bpy.types.SequencerPreviewOverlay.composition_guide_color`](bpy.types.SequencerPreviewOverlay.html#bpy.types.SequencerPreviewOverlay.composition_guide_color) 
- [`bpy.types.SequencerPreviewOverlay.show_composition_center`](bpy.types.SequencerPreviewOverlay.html#bpy.types.SequencerPreviewOverlay.show_composition_center) 
- [`bpy.types.SequencerPreviewOverlay.show_composition_center_diagonal`](bpy.types.SequencerPreviewOverlay.html#bpy.types.SequencerPreviewOverlay.show_composition_center_diagonal) 
- [`bpy.types.SequencerPreviewOverlay.show_composition_golden`](bpy.types.SequencerPreviewOverlay.html#bpy.types.SequencerPreviewOverlay.show_composition_golden) 
- [`bpy.types.SequencerPreviewOverlay.show_composition_golden_tria_a`](bpy.types.SequencerPreviewOverlay.html#bpy.types.SequencerPreviewOverlay.show_composition_golden_tria_a) 
- [`bpy.types.SequencerPreviewOverlay.show_composition_golden_tria_b`](bpy.types.SequencerPreviewOverlay.html#bpy.types.SequencerPreviewOverlay.show_composition_golden_tria_b) 
- [`bpy.types.SequencerPreviewOverlay.show_composition_guides`](bpy.types.SequencerPreviewOverlay.html#bpy.types.SequencerPreviewOverlay.show_composition_guides) 
- [`bpy.types.SequencerPreviewOverlay.show_composition_harmony_tri_a`](bpy.types.SequencerPreviewOverlay.html#bpy.types.SequencerPreviewOverlay.show_composition_harmony_tri_a) 
- [`bpy.types.SequencerPreviewOverlay.show_composition_harmony_tri_b`](bpy.types.SequencerPreviewOverlay.html#bpy.types.SequencerPreviewOverlay.show_composition_harmony_tri_b) 
- [`bpy.types.SequencerPreviewOverlay.show_composition_thirds`](bpy.types.SequencerPreviewOverlay.html#bpy.types.SequencerPreviewOverlay.show_composition_thirds)     

### bpy.types.SequencerTimelineOverlay

  

#### Added

  
- [`bpy.types.SequencerTimelineOverlay.thumbnail_display_style`](bpy.types.SequencerTimelineOverlay.html#bpy.types.SequencerTimelineOverlay.thumbnail_display_style)    

#### Removed

  
- show_thumbnails     

### bpy.types.SequencerToolSettings

  

#### Added

  
- [`bpy.types.SequencerToolSettings.snap_to_all_channels`](bpy.types.SequencerToolSettings.html#bpy.types.SequencerToolSettings.snap_to_all_channels)     

### bpy.types.ShaderNodeRaycast

  

#### Added

  
- [`bpy.types.ShaderNodeRaycast.active_index`](bpy.types.ShaderNodeRaycast.html#bpy.types.ShaderNodeRaycast.active_index) 
- [`bpy.types.ShaderNodeRaycast.active_item`](bpy.types.ShaderNodeRaycast.html#bpy.types.ShaderNodeRaycast.active_item) 
- [`bpy.types.ShaderNodeRaycast.sample_attribute_items`](bpy.types.ShaderNodeRaycast.html#bpy.types.ShaderNodeRaycast.sample_attribute_items)     

### bpy.types.SpaceImageEditor

  

#### Added

  
- [`bpy.types.SpaceImageEditor.show_gizmo_active_node`](bpy.types.SpaceImageEditor.html#bpy.types.SpaceImageEditor.show_gizmo_active_node)     

### bpy.types.SpaceNodeOverlay

  

#### Added

  
- [`bpy.types.SpaceNodeOverlay.passepartout_alpha`](bpy.types.SpaceNodeOverlay.html#bpy.types.SpaceNodeOverlay.passepartout_alpha) 
- [`bpy.types.SpaceNodeOverlay.show_render_size`](bpy.types.SpaceNodeOverlay.html#bpy.types.SpaceNodeOverlay.show_render_size)     

### bpy.types.SpaceOutliner

  

#### Added

  
- [`bpy.types.SpaceOutliner.scroll_to_active`](bpy.types.SpaceOutliner.html#bpy.types.SpaceOutliner.scroll_to_active)     

### bpy.types.SpaceSequenceEditor

  

#### Added

  
- [`bpy.types.SpaceSequenceEditor.show_scrubbing_region`](bpy.types.SpaceSequenceEditor.html#bpy.types.SpaceSequenceEditor.show_scrubbing_region)     

### bpy.types.SpreadsheetRowFilter

  

#### Added

  
- [`bpy.types.SpreadsheetRowFilter.value_float4`](bpy.types.SpreadsheetRowFilter.html#bpy.types.SpreadsheetRowFilter.value_float4)     

### bpy.types.Strip

  

#### Added

  
- [`bpy.types.Strip.connections`](bpy.types.Strip.html#bpy.types.Strip.connections)    

#### Removed

  
- use_linear_modifiers     

### bpy.types.StripModifier

  

#### Added

  
- [`bpy.types.StripModifier.show_preview`](bpy.types.StripModifier.html#bpy.types.StripModifier.show_preview)     

### bpy.types.StripProxy

  

#### Removed

  
- build_record_run 
- timecode     

### bpy.types.StripsMeta

  

#### Function Arguments

  
- [`bpy.types.StripsMeta.new_movie`](bpy.types.StripsMeta.html#bpy.types.StripsMeta.new_movie) (name, filepath, channel, frame_start, fit_method, stream), was (name, filepath, channel, frame_start, fit_method) 
- [`bpy.types.StripsMeta.new_sound`](bpy.types.StripsMeta.html#bpy.types.StripsMeta.new_sound) (name, filepath, channel, frame_start, stream), was (name, filepath, channel, frame_start)     

### bpy.types.StripsTopLevel

  

#### Function Arguments

  
- [`bpy.types.StripsTopLevel.new_movie`](bpy.types.StripsTopLevel.html#bpy.types.StripsTopLevel.new_movie) (name, filepath, channel, frame_start, fit_method, stream), was (name, filepath, channel, frame_start, fit_method) 
- [`bpy.types.StripsTopLevel.new_sound`](bpy.types.StripsTopLevel.html#bpy.types.StripsTopLevel.new_sound) (name, filepath, channel, frame_start, stream), was (name, filepath, channel, frame_start)     

### bpy.types.TextStrip

  

#### Added

  
- [`bpy.types.TextStrip.abs_space_line`](bpy.types.TextStrip.html#bpy.types.TextStrip.abs_space_line) 
- [`bpy.types.TextStrip.space_line`](bpy.types.TextStrip.html#bpy.types.TextStrip.space_line) 
- [`bpy.types.TextStrip.textbox_state`](bpy.types.TextStrip.html#bpy.types.TextStrip.textbox_state) 
- [`bpy.types.TextStrip.use_absolute_line_spacing`](bpy.types.TextStrip.html#bpy.types.TextStrip.use_absolute_line_spacing)     

### bpy.types.ThemeUserInterface

  

#### Added

  
- [`bpy.types.ThemeUserInterface.link`](bpy.types.ThemeUserInterface.html#bpy.types.ThemeUserInterface.link)     

### bpy.types.ThemeView3D

  

#### Added

  
- [`bpy.types.ThemeView3D.grid_axis_brightness`](bpy.types.ThemeView3D.html#bpy.types.ThemeView3D.grid_axis_brightness)     

### bpy.types.UILayout

  

#### Added

  
- [`bpy.types.UILayout.link`](bpy.types.UILayout.html#bpy.types.UILayout.link) 
- [`bpy.types.UILayout.template_collection_importer`](bpy.types.UILayout.html#bpy.types.UILayout.template_collection_importer) 
- [`bpy.types.UILayout.textbox`](bpy.types.UILayout.html#bpy.types.UILayout.textbox) 
- [`bpy.types.UILayout.textbox_with_state`](bpy.types.UILayout.html#bpy.types.UILayout.textbox_with_state)    

#### Function Arguments

  
- [`bpy.types.UILayout.prop`](bpy.types.UILayout.html#bpy.types.UILayout.prop) (data, property, text, text_ctxt, translate, icon, placeholder, expand, slider, toggle, icon_only, event, full_event, emboss, index, icon_value, invert_checkbox, text_align), was (data, property, text, text_ctxt, translate, icon, placeholder, expand, slider, toggle, icon_only, event, full_event, emboss, index, icon_value, invert_checkbox) 
- [`bpy.types.UILayout.template_palette`](bpy.types.UILayout.html#bpy.types.UILayout.template_palette) (data, property), was (data, property, color)     

### bpy.types.UVLoopLayers

  

#### Added

  
- [`bpy.types.UVLoopLayers.active_render`](bpy.types.UVLoopLayers.html#bpy.types.UVLoopLayers.active_render) 
- [`bpy.types.UVLoopLayers.active_render_index`](bpy.types.UVLoopLayers.html#bpy.types.UVLoopLayers.active_render_index)     

### bpy.types.UserAssetLibrary

  

#### Added

  
- [`bpy.types.UserAssetLibrary.remote_url`](bpy.types.UserAssetLibrary.html#bpy.types.UserAssetLibrary.remote_url) 
- [`bpy.types.UserAssetLibrary.use_remote_url`](bpy.types.UserAssetLibrary.html#bpy.types.UserAssetLibrary.use_remote_url)     

### bpy.types.WindowManager

  

#### Added

  
- [`bpy.types.WindowManager.asset_library_status_begin_loading`](bpy.types.WindowManager.html#bpy.types.WindowManager.asset_library_status_begin_loading) 
- [`bpy.types.WindowManager.asset_library_status_failed_loading`](bpy.types.WindowManager.html#bpy.types.WindowManager.asset_library_status_failed_loading) 
- [`bpy.types.WindowManager.asset_library_status_finished_loading`](bpy.types.WindowManager.html#bpy.types.WindowManager.asset_library_status_finished_loading) 
- [`bpy.types.WindowManager.asset_library_status_ping_asset_file_failed`](bpy.types.WindowManager.html#bpy.types.WindowManager.asset_library_status_ping_asset_file_failed) 
- [`bpy.types.WindowManager.asset_library_status_ping_asset_file_progress`](bpy.types.WindowManager.html#bpy.types.WindowManager.asset_library_status_ping_asset_file_progress) 
- [`bpy.types.WindowManager.asset_library_status_ping_asset_file_succeeded`](bpy.types.WindowManager.html#bpy.types.WindowManager.asset_library_status_ping_asset_file_succeeded) 
- [`bpy.types.WindowManager.asset_library_status_ping_finished_download_queue`](bpy.types.WindowManager.html#bpy.types.WindowManager.asset_library_status_ping_finished_download_queue) 
- [`bpy.types.WindowManager.asset_library_status_ping_loaded_new_pages`](bpy.types.WindowManager.html#bpy.types.WindowManager.asset_library_status_ping_loaded_new_pages) 
- [`bpy.types.WindowManager.asset_library_status_ping_loaded_new_preview`](bpy.types.WindowManager.html#bpy.types.WindowManager.asset_library_status_ping_loaded_new_preview) 
- [`bpy.types.WindowManager.asset_library_status_ping_metafiles_in_place`](bpy.types.WindowManager.html#bpy.types.WindowManager.asset_library_status_ping_metafiles_in_place) 
- [`bpy.types.WindowManager.asset_library_status_ping_still_loading`](bpy.types.WindowManager.html#bpy.types.WindowManager.asset_library_status_ping_still_loading) 
- [`bpy.types.WindowManager.is_event_handling_break`](bpy.types.WindowManager.html#bpy.types.WindowManager.is_event_handling_break) 
- [`bpy.types.WindowManager.register_node_group_operators`](bpy.types.WindowManager.html#bpy.types.WindowManager.register_node_group_operators) 
- [`bpy.types.WindowManager.reports`](bpy.types.WindowManager.html#bpy.types.WindowManager.reports)     

### bpy.types.XrSessionSettings

  

#### Added

  
- [`bpy.types.XrSessionSettings.viewfinder_crosshair_enabled`](bpy.types.XrSessionSettings.html#bpy.types.XrSessionSettings.viewfinder_crosshair_enabled) 
- [`bpy.types.XrSessionSettings.viewfinder_enabled`](bpy.types.XrSessionSettings.html#bpy.types.XrSessionSettings.viewfinder_enabled) 
- [`bpy.types.XrSessionSettings.viewfinder_hand`](bpy.types.XrSessionSettings.html#bpy.types.XrSessionSettings.viewfinder_hand) 
- [`bpy.types.XrSessionSettings.viewfinder_passepartout_opacity`](bpy.types.XrSessionSettings.html#bpy.types.XrSessionSettings.viewfinder_passepartout_opacity) 
- [`bpy.types.XrSessionSettings.viewfinder_passepartout_overscan`](bpy.types.XrSessionSettings.html#bpy.types.XrSessionSettings.viewfinder_passepartout_overscan) 
- [`bpy.types.XrSessionSettings.viewfinder_scale`](bpy.types.XrSessionSettings.html#bpy.types.XrSessionSettings.viewfinder_scale)     

### bpy.types.XrSessionState

  

#### Added

  
- [`bpy.types.XrSessionState.viewfinder`](bpy.types.XrSessionState.html#bpy.types.XrSessionState.viewfinder)
