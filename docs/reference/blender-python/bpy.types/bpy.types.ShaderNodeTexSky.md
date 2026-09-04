# bpy.types.ShaderNodeTexSky

# ShaderNodeTexSky(ShaderNode)

 

base classes — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct), [`Node`](bpy.types.Node.html#bpy.types.Node), [`NodeInternal`](bpy.types.NodeInternal.html#bpy.types.NodeInternal), [`ShaderNode`](bpy.types.ShaderNode.html#bpy.types.ShaderNode)

   class bpy.types.ShaderNodeTexSky(ShaderNode) 

Generate a procedural sky texture

   aerosol_density 

Density of dust, pollution and water droplets. 0 means no aerosols, 1 means urban city aerosols

 

(in [0, 1000], default 1.0)

  Type: 

float

      air_density 

Density of air molecules. 0 means no air, 1 means urban city air

 

(in [0, 1000], default 1.0)

  Type: 

float

      altitude 

Height from sea level (in [0, 100000], default 100.0)

  Type: 

float

      color_mapping 

Color mapping settings (readonly, never None)

  Type: 

[`ColorMapping`](bpy.types.ColorMapping.html#bpy.types.ColorMapping)

      ground_albedo 

Ground color that is subtly reflected in the sky (in [0, 1], default 0.0)

  Type: 

float

      ozone_density 

Density of ozone layer. 0 means no ozone, 1 means urban city ozone

 

(in [0, 1000], default 1.0)

  Type: 

float

      sky_type 

Which sky model should be used (default `'PREETHAM'`)

  
- `SINGLE_SCATTERING` Single Scattering – Single scattering sky model. 
- `MULTIPLE_SCATTERING` Multiple Scattering – Multiple scattering sky model (more accurate). 
- `PREETHAM` Preetham – Preetham 1999 (Legacy). 
- `HOSEK_WILKIE` Hosek / Wilkie – Hosek / Wilkie 2012 (Legacy).   Type: 

Literal[‘SINGLE_SCATTERING’, ‘MULTIPLE_SCATTERING’, ‘PREETHAM’, ‘HOSEK_WILKIE’]

      sun_direction 

Direction from where the sun is shining (array of 3 items, in [-inf, inf], default (0.0, 0.0, 1.0))

  Type: 

[`mathutils.Vector`](mathutils.html#mathutils.Vector)

      sun_disc 

Include the sun itself in the output (default True)

  Type: 

bool

      sun_elevation 

Sun angle from horizon (in [-inf, inf], default 0.261799)

  Type: 

float

      sun_intensity 

Strength of Sun (in [0, 1000], default 1.0)

  Type: 

float

      sun_rotation 

Rotation of sun around zenith (in [-inf, inf], default 0.0)

  Type: 

float

      sun_size 

Size of sun disc (in [0, 1.5708], default 0.00951204)

  Type: 

float

      texture_mapping 

Texture coordinate mapping settings (readonly, never None)

  Type: 

[`TexMapping`](bpy.types.TexMapping.html#bpy.types.TexMapping)

      turbidity 

Atmospheric turbidity (in [1, 10], default 0.0)

  Type: 

float

      classmethod is_registered_node_type() 

True if a registered node type

  Returns: 

Result

  Return type: 

bool

      classmethod input_template(index) 

Input socket template

  Parameters: 

index (int) – Index, (in [0, inf])

  Returns: 

result

  Return type: 

[`NodeInternalSocketTemplate`](bpy.types.NodeInternalSocketTemplate.html#bpy.types.NodeInternalSocketTemplate)

      classmethod output_template(index) 

Output socket template

  Parameters: 

index (int) – Index, (in [0, inf])

  Returns: 

result

  Return type: 

[`NodeInternalSocketTemplate`](bpy.types.NodeInternalSocketTemplate.html#bpy.types.NodeInternalSocketTemplate)

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
- [`Node.type`](bpy.types.Node.html#bpy.types.Node.type) 
- [`Node.location`](bpy.types.Node.html#bpy.types.Node.location) 
- [`Node.location_absolute`](bpy.types.Node.html#bpy.types.Node.location_absolute) 
- [`Node.width`](bpy.types.Node.html#bpy.types.Node.width) 
- [`Node.height`](bpy.types.Node.html#bpy.types.Node.height) 
- [`Node.dimensions`](bpy.types.Node.html#bpy.types.Node.dimensions) 
- [`Node.name`](bpy.types.Node.html#bpy.types.Node.name) 
- [`Node.label`](bpy.types.Node.html#bpy.types.Node.label) 
- [`Node.inputs`](bpy.types.Node.html#bpy.types.Node.inputs) 
- [`Node.outputs`](bpy.types.Node.html#bpy.types.Node.outputs) 
- [`Node.panel_states`](bpy.types.Node.html#bpy.types.Node.panel_states) 
- [`Node.internal_links`](bpy.types.Node.html#bpy.types.Node.internal_links) 
- [`Node.parent`](bpy.types.Node.html#bpy.types.Node.parent) 
- [`Node.warning_propagation`](bpy.types.Node.html#bpy.types.Node.warning_propagation) 
- [`Node.use_custom_color`](bpy.types.Node.html#bpy.types.Node.use_custom_color) 
- [`Node.color`](bpy.types.Node.html#bpy.types.Node.color) 
- [`Node.color_tag`](bpy.types.Node.html#bpy.types.Node.color_tag)   
- [`Node.select`](bpy.types.Node.html#bpy.types.Node.select) 
- [`Node.show_options`](bpy.types.Node.html#bpy.types.Node.show_options) 
- [`Node.show_preview`](bpy.types.Node.html#bpy.types.Node.show_preview) 
- [`Node.hide`](bpy.types.Node.html#bpy.types.Node.hide) 
- [`Node.mute`](bpy.types.Node.html#bpy.types.Node.mute) 
- [`Node.show_texture`](bpy.types.Node.html#bpy.types.Node.show_texture) 
- [`Node.bl_idname`](bpy.types.Node.html#bpy.types.Node.bl_idname) 
- [`Node.bl_label`](bpy.types.Node.html#bpy.types.Node.bl_label) 
- [`Node.bl_description`](bpy.types.Node.html#bpy.types.Node.bl_description) 
- [`Node.bl_icon`](bpy.types.Node.html#bpy.types.Node.bl_icon) 
- [`Node.bl_static_type`](bpy.types.Node.html#bpy.types.Node.bl_static_type) 
- [`Node.bl_width_default`](bpy.types.Node.html#bpy.types.Node.bl_width_default) 
- [`Node.bl_width_min`](bpy.types.Node.html#bpy.types.Node.bl_width_min) 
- [`Node.bl_width_max`](bpy.types.Node.html#bpy.types.Node.bl_width_max) 
- [`Node.bl_height_default`](bpy.types.Node.html#bpy.types.Node.bl_height_default) 
- [`Node.bl_height_min`](bpy.types.Node.html#bpy.types.Node.bl_height_min) 
- [`Node.bl_height_max`](bpy.types.Node.html#bpy.types.Node.bl_height_max)     

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
- [`Node.bl_system_properties_get`](bpy.types.Node.html#bpy.types.Node.bl_system_properties_get) 
- [`Node.socket_value_update`](bpy.types.Node.html#bpy.types.Node.socket_value_update)   
- [`Node.is_registered_node_type`](bpy.types.Node.html#bpy.types.Node.is_registered_node_type) 
- [`Node.poll`](bpy.types.Node.html#bpy.types.Node.poll) 
- [`Node.poll_instance`](bpy.types.Node.html#bpy.types.Node.poll_instance) 
- [`Node.update`](bpy.types.Node.html#bpy.types.Node.update) 
- [`Node.insert_link`](bpy.types.Node.html#bpy.types.Node.insert_link) 
- [`Node.init`](bpy.types.Node.html#bpy.types.Node.init) 
- [`Node.copy`](bpy.types.Node.html#bpy.types.Node.copy) 
- [`Node.free`](bpy.types.Node.html#bpy.types.Node.free) 
- [`Node.draw_buttons`](bpy.types.Node.html#bpy.types.Node.draw_buttons) 
- [`Node.draw_buttons_ext`](bpy.types.Node.html#bpy.types.Node.draw_buttons_ext) 
- [`Node.draw_label`](bpy.types.Node.html#bpy.types.Node.draw_label) 
- [`Node.debug_zone_body_lazy_function_graph`](bpy.types.Node.html#bpy.types.Node.debug_zone_body_lazy_function_graph) 
- [`Node.debug_zone_lazy_function_graph`](bpy.types.Node.html#bpy.types.Node.debug_zone_lazy_function_graph) 
- [`Node.poll`](bpy.types.Node.html#bpy.types.Node.poll) 
- [`Node.bl_rna_get_subclass`](bpy.types.Node.html#bpy.types.Node.bl_rna_get_subclass) 
- [`Node.bl_rna_get_subclass_py`](bpy.types.Node.html#bpy.types.Node.bl_rna_get_subclass_py) 
- [`NodeInternal.poll`](bpy.types.NodeInternal.html#bpy.types.NodeInternal.poll) 
- [`NodeInternal.poll_instance`](bpy.types.NodeInternal.html#bpy.types.NodeInternal.poll_instance) 
- [`NodeInternal.update`](bpy.types.NodeInternal.html#bpy.types.NodeInternal.update) 
- [`NodeInternal.draw_buttons`](bpy.types.NodeInternal.html#bpy.types.NodeInternal.draw_buttons) 
- [`NodeInternal.draw_buttons_ext`](bpy.types.NodeInternal.html#bpy.types.NodeInternal.draw_buttons_ext) 
- [`NodeInternal.bl_rna_get_subclass`](bpy.types.NodeInternal.html#bpy.types.NodeInternal.bl_rna_get_subclass) 
- [`NodeInternal.bl_rna_get_subclass_py`](bpy.types.NodeInternal.html#bpy.types.NodeInternal.bl_rna_get_subclass_py) 
- `ShaderNode.poll` 
- [`ShaderNode.bl_rna_get_subclass`](bpy.types.ShaderNode.html#bpy.types.ShaderNode.bl_rna_get_subclass) 
- [`ShaderNode.bl_rna_get_subclass_py`](bpy.types.ShaderNode.html#bpy.types.ShaderNode.bl_rna_get_subclass_py)
