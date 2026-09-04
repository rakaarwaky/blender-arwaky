# bpy.types.LightProbeVolume

# LightProbeVolume(LightProbe)

 

base classes — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct), [`ID`](bpy.types.ID.html#bpy.types.ID), [`LightProbe`](bpy.types.LightProbe.html#bpy.types.LightProbe)

   class bpy.types.LightProbeVolume(LightProbe) 

Light probe that captures low frequency lighting inside a volume

   bake_samples 

Number of ray directions to evaluate when baking (in [1, inf], default 2048)

  Type: 

int

      capture_distance 

Distance around the probe volume that will be considered during the bake (in [1e-06, inf], default 20.0)

  Type: 

float

      capture_emission 

Bake emissive surfaces for more accurate lighting (default True)

  Type: 

bool

      capture_indirect 

Bake light bounces from light sources for more accurate lighting (default True)

  Type: 

bool

      capture_world 

Bake incoming light from the world instead of just the visibility for more accurate lighting, but lose correct blending to surrounding irradiance volumes (default False)

  Type: 

bool

      clamp_direct 

Clamp the direct lighting intensity to reduce noise (0 to disable) (in [0, inf], default 0.0)

  Type: 

float

      clamp_indirect 

Clamp the indirect lighting intensity to reduce noise (0 to disable) (in [0, inf], default 10.0)

  Type: 

float

      dilation_radius 

Radius in grid sample to search valid grid samples to copy into invalid grid samples (in [1, 5], default 1.0)

  Type: 

float

      dilation_threshold 

Ratio of front-facing surface hits under which a grid sample will reuse neighbors grid sample lighting (in [0, 1], default 0.5)

  Type: 

float

      escape_bias 

Distance to search for valid capture positions to prevent lighting artifacts (in [0, 1], default 0.1)

  Type: 

float

      facing_bias 

Smoother irradiance interpolation but introduce light bleeding (in [0, inf], default 0.5)

  Type: 

float

      intensity 

Modify the intensity of the lighting captured by this probe (in [0, inf], default 1.0)

  Type: 

float

      normal_bias 

Offset sampling of the irradiance grid in the surface normal direction to reduce light bleeding (in [0, inf], default 0.3)

  Type: 

float

      resolution_x 

Number of samples along the x axis of the volume (in [1, 256], default 4)

  Type: 

int

      resolution_y 

Number of samples along the y axis of the volume (in [1, 256], default 4)

  Type: 

int

      resolution_z 

Number of samples along the z axis of the volume (in [1, 256], default 4)

  Type: 

int

      surface_bias 

Moves capture points away from surfaces to prevent artifacts (in [0, 1], default 0.05)

  Type: 

float

      surfel_density 

Number of surfels to spawn in one local unit distance (higher values improve quality) (in [1, inf], default 20)

  Type: 

int

      validity_threshold 

Ratio of front-facing surface hits under which a grid sample will not be considered for lighting (in [0, 1], default 0.4)

  Type: 

float

      view_bias 

Offset sampling of the irradiance grid in the viewing direction to reduce light bleeding (in [0, inf], default 0.0)

  Type: 

float

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
- [`LightProbe.type`](bpy.types.LightProbe.html#bpy.types.LightProbe.type) 
- [`LightProbe.clip_start`](bpy.types.LightProbe.html#bpy.types.LightProbe.clip_start) 
- [`LightProbe.show_clip`](bpy.types.LightProbe.html#bpy.types.LightProbe.show_clip) 
- [`LightProbe.show_influence`](bpy.types.LightProbe.html#bpy.types.LightProbe.show_influence) 
- [`LightProbe.influence_distance`](bpy.types.LightProbe.html#bpy.types.LightProbe.influence_distance) 
- [`LightProbe.visibility_buffer_bias`](bpy.types.LightProbe.html#bpy.types.LightProbe.visibility_buffer_bias) 
- [`LightProbe.visibility_bleed_bias`](bpy.types.LightProbe.html#bpy.types.LightProbe.visibility_bleed_bias) 
- [`LightProbe.visibility_blur`](bpy.types.LightProbe.html#bpy.types.LightProbe.visibility_blur) 
- [`LightProbe.visibility_collection`](bpy.types.LightProbe.html#bpy.types.LightProbe.visibility_collection) 
- [`LightProbe.invert_visibility_collection`](bpy.types.LightProbe.html#bpy.types.LightProbe.invert_visibility_collection) 
- [`LightProbe.show_data`](bpy.types.LightProbe.html#bpy.types.LightProbe.show_data) 
- [`LightProbe.use_data_display`](bpy.types.LightProbe.html#bpy.types.LightProbe.use_data_display) 
- [`LightProbe.data_display_size`](bpy.types.LightProbe.html#bpy.types.LightProbe.data_display_size) 
- [`LightProbe.animation_data`](bpy.types.LightProbe.html#bpy.types.LightProbe.animation_data)     

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
- [`LightProbe.bl_rna_get_subclass`](bpy.types.LightProbe.html#bpy.types.LightProbe.bl_rna_get_subclass) 
- [`LightProbe.bl_rna_get_subclass_py`](bpy.types.LightProbe.html#bpy.types.LightProbe.bl_rna_get_subclass_py)
