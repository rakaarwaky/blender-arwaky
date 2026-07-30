# bpy.types.MaterialGPencilStyle

# MaterialGPencilStyle(bpy_struct)

 

base class — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct)

   class bpy.types.MaterialGPencilStyle(bpy_struct)   alignment_mode 

Defines how align Dots and Boxes with drawing path and object rotation (default `'PATH'`)

  
- `PATH` Path – Follow stroke drawing path and object rotation. 
- `OBJECT` Object – Follow object rotation only. 
- `FIXED` Fixed – Do not follow drawing path or object rotation and keeps aligned with viewport.   Type: 

Literal[‘PATH’, ‘OBJECT’, ‘FIXED’]

      alignment_rotation 

Additional rotation applied to dots and square texture of strokes (in [-1.5708, 1.5708], default 0.0)

  Type: 

float

      color 

(array of 4 items, in [0, inf], default (0.0, 0.0, 0.0, 0.0))

  Type: 

[`bpy_prop_array`](bpy.types.bpy_prop_array.html#bpy.types.bpy_prop_array)[float]

      fill_color 

Color for filling region bounded by each stroke (array of 4 items, in [0, inf], default (0.0, 0.0, 0.0, 0.0))

  Type: 

[`bpy_prop_array`](bpy.types.bpy_prop_array.html#bpy.types.bpy_prop_array)[float]

      fill_image  Type: 

[`Image`](bpy.types.Image.html#bpy.types.Image) | None

      fill_style 

Select style used to fill strokes (default `'SOLID'`)

  
- `SOLID` Solid – Fill area with solid color. 
- `GRADIENT` Gradient – Fill area with gradient color. 
- `TEXTURE` Texture – Fill area with image texture.   Type: 

Literal[‘SOLID’, ‘GRADIENT’, ‘TEXTURE’]

      flip 

Flip filling colors (default False)

  Type: 

bool

      ghost 

Display strokes using this color when showing onion skins (default False)

  Type: 

bool

      gradient_type 

Select type of gradient used to fill strokes (default `'LINEAR'`)

  
- `LINEAR` Linear – Fill area with gradient color. 
- `RADIAL` Radial – Fill area with radial gradient.   Type: 

Literal[‘LINEAR’, ‘RADIAL’]

      hide 

Set color Visibility (default False)

  Type: 

bool

      is_fill_visible 

True when opacity of fill is set high enough to be visible (default False, readonly)

  Type: 

bool

      is_stroke_visible 

True when opacity of stroke is set high enough to be visible (default False, readonly)

  Type: 

bool

      lock 

Protect color from further editing and/or frame changes (default False)

  Type: 

bool

      mix_color 

Color for mixing with primary filling color (array of 4 items, in [0, inf], default (0.0, 0.0, 0.0, 0.0))

  Type: 

[`bpy_prop_array`](bpy.types.bpy_prop_array.html#bpy.types.bpy_prop_array)[float]

      mix_factor 

Mix Factor (in [0, 1], default 0.0)

  Type: 

float

      mix_stroke_factor 

Mix Stroke Factor (in [0, 1], default 0.0)

  Type: 

float

      mode 

Select line type for strokes (default `'LINE'`)

  
- `LINE` Line – Draw strokes using a continuous line. 
- `DOTS` Dots – Draw strokes using separated dots. 
- `BOX` Squares – Draw strokes using separated squares.   Type: 

Literal[‘LINE’, ‘DOTS’, ‘BOX’]

      pass_index 

Index number for the “Color Index” pass (in [0, 32767], default 0)

  Type: 

int

      pixel_size 

Texture Pixel Size factor along the stroke (in [1, 5000], default 0.0)

  Type: 

float

      placement_count 

Number of dots placed per segment (in [1, inf], default 0)

  Type: 

int

      placement_density 

Density of dots along the stroke (in [0, inf], default 10.0)

  Type: 

float

      placement_mode 

Defines how Dots or Squares are placed along strokes (default `'RADIUS'`)

  
- `COUNT` Count – Place dots evenly along each segment of the stroke. 
- `RADIUS` Radius – Place dots evenly with respect to radius. 
- `DENSITY` Density – Place dots evenly along the length of the stroke.   Type: 

Literal[‘COUNT’, ‘RADIUS’, ‘DENSITY’]

      placement_radius_spacing 

Spacing between dots as a percentage of the diameter (in [0, inf], default 100.0)

  Type: 

float

      random_hue_factor 

Randomize color hue (in [0, 1], default 0.0)

  Type: 

float

      random_noise_scale 

Scale the noise frequency (in [0, inf], default 1.0)

  Type: 

float

      random_rotation_factor 

Randomize texture rotation (in [0, 1], default 0.0)

  Type: 

float

      random_saturation_factor 

Randomize color saturation (in [0, 1], default 0.0)

  Type: 

float

      random_size_factor 

Randomize the size (in [0, 1], default 0.0)

  Type: 

float

      random_strength_factor 

Randomize strength (in [0, 1], default 0.0)

  Type: 

float

      random_value_factor 

Randomize color value (in [0, 1], default 0.0)

  Type: 

float

      show_fill 

Show stroke fills of this material (default False)

  

Deprecated since version 5.10: removal planned in version 6.0

 

Unused but kept for compatibility with older versions of Blender.

   Type: 

bool

      show_stroke 

Show stroke lines of this material (default False)

  

Deprecated since version 5.10: removal planned in version 6.0

 

Unused but kept for compatibility with older versions of Blender.

   Type: 

bool

      stroke_image  Type: 

[`Image`](bpy.types.Image.html#bpy.types.Image) | None

      stroke_style 

Select style used to draw strokes (default `'SOLID'`)

  
- `SOLID` Solid – Draw strokes with solid color. 
- `TEXTURE` Texture – Draw strokes using texture.   Type: 

Literal[‘SOLID’, ‘TEXTURE’]

      texture_angle 

Texture Orientation Angle (in [-inf, inf], default 0.0)

  Type: 

float

      texture_clamp 

Do not repeat texture and clamp to one instance only (default False)

  Type: 

bool

      texture_offset 

Shift Texture in 2d Space (array of 2 items, in [-inf, inf], default (0.0, 0.0))

  Type: 

[`mathutils.Vector`](mathutils.html#mathutils.Vector)

      texture_scale 

Scale Factor for Texture (array of 2 items, in [-inf, inf], default (0.0, 0.0))

  Type: 

[`mathutils.Vector`](mathutils.html#mathutils.Vector)

      use_fill_holdout 

Remove the color from underneath this stroke by using it as a mask (default False)

  Type: 

bool

      use_overlap_strokes 

Disable stencil and overlap self intersections with alpha materials (default False)

  Type: 

bool

      use_randomization 

Use material randomization (default False)

  Type: 

bool

      use_stroke_holdout 

Remove the color from underneath this stroke by using it as a mask (default False)

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

  
- [`Material.grease_pencil`](bpy.types.Material.html#bpy.types.Material.grease_pencil)
