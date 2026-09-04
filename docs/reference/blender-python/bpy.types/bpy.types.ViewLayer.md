# bpy.types.ViewLayer

# ViewLayer(bpy_struct)

 

base class — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct)

   class bpy.types.ViewLayer(bpy_struct) 

View layer

   active_aov 

Active AOV (readonly)

  Type: 

[`AOV`](bpy.types.AOV.html#bpy.types.AOV) | None

      active_aov_index 

Index of active AOV (in [0, inf], default 0)

  Type: 

int

      active_layer_collection 

Active layer collection in this view layer’s hierarchy (never None)

  Type: 

[`LayerCollection`](bpy.types.LayerCollection.html#bpy.types.LayerCollection)

      active_lightgroup 

Active Lightgroup (readonly)

  Type: 

[`Lightgroup`](bpy.types.Lightgroup.html#bpy.types.Lightgroup) | None

      active_lightgroup_index 

Index of active lightgroup (in [0, inf], default 0)

  Type: 

int

      aovs 

(default None, readonly)

  Type: 

[`AOVs`](bpy.types.AOVs.html#bpy.types.AOVs)[[`AOV`](bpy.types.AOV.html#bpy.types.AOV)]

      cycles 

Cycles ViewLayer Settings (readonly)

  Type: 

`CyclesRenderLayerSettings` | None

      depsgraph 

Dependencies in the scene data (readonly)

  Type: 

[`Depsgraph`](bpy.types.Depsgraph.html#bpy.types.Depsgraph) | None

      eevee 

View layer settings for EEVEE (readonly, never None)

  Type: 

[`ViewLayerEEVEE`](bpy.types.ViewLayerEEVEE.html#bpy.types.ViewLayerEEVEE)

      freestyle_settings 

(readonly, never None)

  Type: 

[`FreestyleSettings`](bpy.types.FreestyleSettings.html#bpy.types.FreestyleSettings)

      has_export_collections 

At least one Collection in this View Layer has an exporter (default False, readonly)

  Type: 

bool

      layer_collection 

Root of collections hierarchy of this view layer, its ‘collection’ pointer property is the same as the scene’s master collection (readonly, never None)

  Type: 

[`LayerCollection`](bpy.types.LayerCollection.html#bpy.types.LayerCollection)

      lightgroups 

(default None, readonly)

  Type: 

[`Lightgroups`](bpy.types.Lightgroups.html#bpy.types.Lightgroups)[[`Lightgroup`](bpy.types.Lightgroup.html#bpy.types.Lightgroup)]

      material_override 

Material to override all other materials in this view layer

  Type: 

[`Material`](bpy.types.Material.html#bpy.types.Material) | None

      name 

View layer name (default “”, never None)

  Type: 

str

      objects 

All the objects in this layer (default None, readonly)

  Type: 

[`LayerObjects`](bpy.types.LayerObjects.html#bpy.types.LayerObjects)[[`Object`](bpy.types.Object.html#bpy.types.Object)]

      pass_alpha_threshold 

Z, Index, normal, UV and vector passes are only affected by surfaces with alpha transparency equal to or higher than this threshold (in [0, 1], default 0.5)

  Type: 

float

      pass_cryptomatte_depth 

Sets how many unique objects can be distinguished per pixel (in [2, 16], default 6)

  Type: 

int

      samples 

Override number of render samples for this view layer, 0 will use the scene setting (in [0, inf], default 0)

  Type: 

int

      use 

Enable or disable rendering of this View Layer (default True)

  Type: 

bool

      use_ao 

Render Ambient Occlusion in this Layer (default True)

  Type: 

bool

      use_freestyle 

Render stylized strokes in this Layer (default True)

  Type: 

bool

      use_grease_pencil 

Render Grease Pencil on this layer (default True)

  Type: 

bool

      use_motion_blur 

Render motion blur in this Layer, if enabled in the scene (default True)

  Type: 

bool

      use_pass_ambient_occlusion 

Deliver Ambient Occlusion pass (default False)

  Type: 

bool

      use_pass_combined 

Deliver full combined RGBA buffer (default True)

  Type: 

bool

      use_pass_cryptomatte_accurate 

Generate a more accurate cryptomatte pass (default True)

  Type: 

bool

      use_pass_cryptomatte_asset 

Render cryptomatte asset pass, for isolating groups of objects with the same parent (default False)

  Type: 

bool

      use_pass_cryptomatte_material 

Render cryptomatte material pass, for isolating materials in compositing (default False)

  Type: 

bool

      use_pass_cryptomatte_object 

Render cryptomatte object pass, for isolating objects in compositing (default False)

  Type: 

bool

      use_pass_diffuse_color 

Deliver diffuse color pass (default False)

  Type: 

bool

      use_pass_diffuse_direct 

Deliver diffuse direct pass (default False)

  Type: 

bool

      use_pass_diffuse_indirect 

Deliver diffuse indirect pass (default False)

  Type: 

bool

      use_pass_emit 

Deliver emission pass (default False)

  Type: 

bool

      use_pass_environment 

Deliver environment lighting pass (default False)

  Type: 

bool

      use_pass_glossy_color 

Deliver glossy color pass (default False)

  Type: 

bool

      use_pass_glossy_direct 

Deliver glossy direct pass (default False)

  Type: 

bool

      use_pass_glossy_indirect 

Deliver glossy indirect pass (default False)

  Type: 

bool

      use_pass_grease_pencil 

Deliver Grease Pencil render result in a separate pass (default False)

  Type: 

bool

      use_pass_material_index 

Deliver material index pass (default False)

  Type: 

bool

      use_pass_mist 

Deliver mist factor pass (0.0 to 1.0) (default False)

  Type: 

bool

      use_pass_normal 

Deliver normal pass (default False)

  Type: 

bool

      use_pass_object_index 

Deliver object index pass (default False)

  Type: 

bool

      use_pass_position 

Deliver position pass (default False)

  Type: 

bool

      use_pass_shadow 

Deliver shadow pass (default False)

  Type: 

bool

      use_pass_subsurface_color 

Deliver subsurface color pass (default False)

  Type: 

bool

      use_pass_subsurface_direct 

Deliver subsurface direct pass (default False)

  Type: 

bool

      use_pass_subsurface_indirect 

Deliver subsurface indirect pass (default False)

  Type: 

bool

      use_pass_transmission_color 

Deliver transmission color pass (default False)

  Type: 

bool

      use_pass_transmission_direct 

Deliver transmission direct pass (default False)

  Type: 

bool

      use_pass_transmission_indirect 

Deliver transmission indirect pass (default False)

  Type: 

bool

      use_pass_uv 

Deliver texture UV pass (default False)

  Type: 

bool

      use_pass_vector 

Deliver speed vector pass (default False)

  Type: 

bool

      use_pass_z 

Deliver depth values pass (default False)

  Type: 

bool

      use_sky 

Render Sky in this Layer (default True)

  Type: 

bool

      use_solid 

Render Solid faces in this Layer (default True)

  Type: 

bool

      use_strand 

Render Strands in this Layer (default True)

  Type: 

bool

      use_volumes 

Render volumes in this Layer (default True)

  Type: 

bool

      world_override 

Override world in this view layer

  Type: 

[`World`](bpy.types.World.html#bpy.types.World) | None

      bl_system_properties_get(*, do_create=False) 

DEBUG ONLY. Internal access to runtime-defined RNA data storage, intended solely for testing and debugging purposes. Do not access it in regular scripting work, and in particular, do not assume that it contains writable data

  Parameters: 

do_create (bool) – Ensure that system properties are created if they do not exist yet (optional)

  Returns: 

The system properties root container, or None if there are no system properties stored in this data yet, and its creation was not requested

  Return type: 

[`PropertyGroup`](bpy.types.PropertyGroup.html#bpy.types.PropertyGroup)

      classmethod update_render_passes() 

Requery the enabled render passes from the render engine

    update() 

Update data tagged to be updated from previous access to data or operators

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

  
- `bpy.context.view_layer` 
- [`Context.view_layer`](bpy.types.Context.html#bpy.types.Context.view_layer) 
- [`Depsgraph.view_layer`](bpy.types.Depsgraph.html#bpy.types.Depsgraph.view_layer) 
- [`Depsgraph.view_layer_eval`](bpy.types.Depsgraph.html#bpy.types.Depsgraph.view_layer_eval) 
- [`ID.override_hierarchy_create`](bpy.types.ID.html#bpy.types.ID.override_hierarchy_create) 
- [`IDOverrideLibrary.resync`](bpy.types.IDOverrideLibrary.html#bpy.types.IDOverrideLibrary.resync) 
- [`LayerCollection.has_selected_objects`](bpy.types.LayerCollection.html#bpy.types.LayerCollection.has_selected_objects) 
- [`Object.hide_get`](bpy.types.Object.html#bpy.types.Object.hide_get) 
- [`Object.hide_set`](bpy.types.Object.html#bpy.types.Object.hide_set) 
- [`Object.holdout_get`](bpy.types.Object.html#bpy.types.Object.holdout_get) 
- [`Object.indirect_only_get`](bpy.types.Object.html#bpy.types.Object.indirect_only_get)   
- [`Object.select_get`](bpy.types.Object.html#bpy.types.Object.select_get) 
- [`Object.select_set`](bpy.types.Object.html#bpy.types.Object.select_set) 
- [`Object.visible_get`](bpy.types.Object.html#bpy.types.Object.visible_get) 
- [`RenderEngine.register_pass`](bpy.types.RenderEngine.html#bpy.types.RenderEngine.register_pass) 
- [`RenderEngine.update_render_passes`](bpy.types.RenderEngine.html#bpy.types.RenderEngine.update_render_passes) 
- [`Scene.statistics`](bpy.types.Scene.html#bpy.types.Scene.statistics) 
- [`Scene.view_layers`](bpy.types.Scene.html#bpy.types.Scene.view_layers) 
- [`SceneStrip.view_layer`](bpy.types.SceneStrip.html#bpy.types.SceneStrip.view_layer) 
- [`ViewLayers.new`](bpy.types.ViewLayers.html#bpy.types.ViewLayers.new) 
- [`ViewLayers.remove`](bpy.types.ViewLayers.html#bpy.types.ViewLayers.remove) 
- [`Window.view_layer`](bpy.types.Window.html#bpy.types.Window.view_layer)
