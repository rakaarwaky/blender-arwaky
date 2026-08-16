# bpy.types.GreasePencilLengthModifier

# GreasePencilLengthModifier(Modifier)

 

base classes — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct), [`Modifier`](bpy.types.Modifier.html#bpy.types.Modifier)

   class bpy.types.GreasePencilLengthModifier(Modifier) 

Stretch or shrink strokes

   end_factor 

Added length to the end of each stroke relative to its length (in [-inf, inf], default 0.1)

  Type: 

float

      end_length 

Absolute added length to the end of each stroke (in [-inf, inf], default 0.1)

  Type: 

float

      invert_curvature 

Invert the curvature of the stroke’s extension (default False)

  Type: 

bool

      invert_layer_filter 

Invert layer filter (default False)

  Type: 

bool

      invert_layer_pass_filter 

Invert layer pass filter (default False)

  Type: 

bool

      invert_material_filter 

Invert material filter (default False)

  Type: 

bool

      invert_material_pass_filter 

Invert material pass filter (default False)

  Type: 

bool

      layer_pass_filter 

Layer pass filter (in [0, 100], default 0)

  Type: 

int

      material_filter 

Material used for filtering

  Type: 

[`Material`](bpy.types.Material.html#bpy.types.Material) | None

      material_pass_filter 

Material pass (in [0, 100], default 0)

  Type: 

int

      max_angle 

Ignore points on the stroke that deviate from their neighbors by more than this angle when determining the extrapolation shape (in [0, 3.14159], default 2.96706)

  Type: 

float

      mode 

Mode to define length (default `'RELATIVE'`)

  
- `RELATIVE` Relative – Length in ratio to the stroke’s length. 
- `ABSOLUTE` Absolute – Length in geometry space.   Type: 

Literal[‘RELATIVE’, ‘ABSOLUTE’]

      open_curvature_panel 

(default False)

  Type: 

bool

      open_influence_panel 

(default False)

  Type: 

bool

      open_random_panel 

(default False)

  Type: 

bool

      overshoot_factor 

Defines what portion of the stroke is used for the calculation of the extension (in [0, 1], default 0.1)

  Type: 

float

      point_density 

Multiplied by Start/End for the total added point count (in [0.1, 1000], default 30.0)

  Type: 

float

      random_end_factor 

Size of random length added to the end of each stroke (in [-inf, inf], default 0.0)

  Type: 

float

      random_offset 

Smoothly offset each stroke’s random value (in [-inf, inf], default 0.0)

  Type: 

float

      random_start_factor 

Size of random length added to the start of each stroke (in [-inf, inf], default 0.0)

  Type: 

float

      seed 

Random seed (in [0, inf], default 0)

  Type: 

int

      segment_influence 

Factor to determine how much the length of the individual segments should influence the final computed curvature. Higher factors makes small segments influence the overall curvature less. (in [-2, 3], default 0.0)

  Type: 

float

      start_factor 

Added length to the start of each stroke relative to its length (in [-inf, inf], default 0.1)

  Type: 

float

      start_length 

Absolute added length to the start of each stroke (in [-inf, inf], default 0.1)

  Type: 

float

      step 

Number of frames between randomization steps (in [1, 100], default 4)

  Type: 

int

      tree_node_filter 

Layer name (default “”, never None)

  Type: 

str

      use_curvature 

Follow the curvature of the stroke (default True)

  Type: 

bool

      use_layer_group_filter 

Filter by layer group name (default False)

  Type: 

bool

      use_layer_pass_filter 

Use layer pass filter (default False)

  Type: 

bool

      use_material_pass_filter 

Use material pass filter (default False)

  Type: 

bool

      use_random 

Use random values over time (default False)

  Type: 

bool

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
- [`Modifier.name`](bpy.types.Modifier.html#bpy.types.Modifier.name) 
- [`Modifier.type`](bpy.types.Modifier.html#bpy.types.Modifier.type) 
- [`Modifier.show_viewport`](bpy.types.Modifier.html#bpy.types.Modifier.show_viewport) 
- [`Modifier.show_render`](bpy.types.Modifier.html#bpy.types.Modifier.show_render) 
- [`Modifier.show_in_editmode`](bpy.types.Modifier.html#bpy.types.Modifier.show_in_editmode) 
- [`Modifier.show_on_cage`](bpy.types.Modifier.html#bpy.types.Modifier.show_on_cage)   
- [`Modifier.show_expanded`](bpy.types.Modifier.html#bpy.types.Modifier.show_expanded) 
- [`Modifier.is_active`](bpy.types.Modifier.html#bpy.types.Modifier.is_active) 
- [`Modifier.use_pin_to_last`](bpy.types.Modifier.html#bpy.types.Modifier.use_pin_to_last) 
- [`Modifier.is_override_data`](bpy.types.Modifier.html#bpy.types.Modifier.is_override_data) 
- [`Modifier.use_apply_on_spline`](bpy.types.Modifier.html#bpy.types.Modifier.use_apply_on_spline) 
- [`Modifier.execution_time`](bpy.types.Modifier.html#bpy.types.Modifier.execution_time) 
- [`Modifier.persistent_uid`](bpy.types.Modifier.html#bpy.types.Modifier.persistent_uid)     

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
- [`Modifier.bl_rna_get_subclass`](bpy.types.Modifier.html#bpy.types.Modifier.bl_rna_get_subclass) 
- [`Modifier.bl_rna_get_subclass_py`](bpy.types.Modifier.html#bpy.types.Modifier.bl_rna_get_subclass_py)
