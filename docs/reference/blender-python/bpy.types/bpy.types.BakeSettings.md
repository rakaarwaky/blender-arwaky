# bpy.types.BakeSettings

# BakeSettings(bpy_struct)

 

base class — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct)

   class bpy.types.BakeSettings(bpy_struct) 

Bake data for a Scene data-block

   cage_extrusion 

Inflate the active object by the specified distance for baking. This helps matching to points nearer to the outside of the selected object meshes. (in [0, inf], default 0.0)

  Type: 

float

      cage_object 

Object to use as cage instead of calculating the cage from the active object with cage extrusion

  Type: 

[`Object`](bpy.types.Object.html#bpy.types.Object) | None

      displacement_space 

Choose displacement space for baking (default `'OBJECT'`)

  
- `OBJECT` Object – Bake the displacement in object space. 
- `TANGENT` Tangent – Bake the displacement in tangent space.   Type: 

Literal[‘OBJECT’, ‘TANGENT’]

      filepath 

Image filepath to use when saving externally (default “//”, never None, blend relative `//` prefix supported)

  Type: 

str

      height 

Vertical dimension of the baking map (in [4, 10000], default 512)

  Type: 

int

      image_settings 

(readonly, never None)

  Type: 

[`ImageFormatSettings`](bpy.types.ImageFormatSettings.html#bpy.types.ImageFormatSettings)

      margin 

Extends the baked result as a post process filter (in [0, 32767], default 16)

  Type: 

int

      margin_type 

Algorithm to extend the baked result (default `'ADJACENT_FACES'`)

  Type: 

Literal[[Bake Margin Type Items](bpy_types_enum_items/bake_margin_type_items.html#rna-enum-bake-margin-type-items)]

      max_ray_distance 

The maximum ray distance for matching points between the active and selected objects. If zero, there is no limit. (in [0, inf], default 0.0)

  Type: 

float

      normal_b 

Axis to bake in blue channel (default `'POS_X'`)

  Type: 

Literal[[Normal Swizzle Items](bpy_types_enum_items/normal_swizzle_items.html#rna-enum-normal-swizzle-items)]

      normal_g 

Axis to bake in green channel (default `'POS_X'`)

  Type: 

Literal[[Normal Swizzle Items](bpy_types_enum_items/normal_swizzle_items.html#rna-enum-normal-swizzle-items)]

      normal_r 

Axis to bake in red channel (default `'POS_X'`)

  Type: 

Literal[[Normal Swizzle Items](bpy_types_enum_items/normal_swizzle_items.html#rna-enum-normal-swizzle-items)]

      normal_space 

Choose normal space for baking (default `'TANGENT'`)

  Type: 

Literal[[Normal Space Items](bpy_types_enum_items/normal_space_items.html#rna-enum-normal-space-items)]

      pass_filter 

Passes to include in the active baking pass (default {`'COLOR'`, `'DIFFUSE'`, `'DIRECT'`, `'EMIT'`, `'GLOSSY'`, `'INDIRECT'`, `'TRANSMISSION'`}, readonly)

  Type: 

set[Literal[[Bake Pass Filter Type Items](bpy_types_enum_items/bake_pass_filter_type_items.html#rna-enum-bake-pass-filter-type-items)]]

      save_mode 

Where to save baked image textures (default `'INTERNAL'`)

  Type: 

Literal[[Bake Save Mode Items](bpy_types_enum_items/bake_save_mode_items.html#rna-enum-bake-save-mode-items)]

      target 

Where to output the baked map (default `'IMAGE_TEXTURES'`)

  Type: 

Literal[[Bake Target Items](bpy_types_enum_items/bake_target_items.html#rna-enum-bake-target-items)]

      type 

Choose shading information to bake into the image (default `'NORMALS'`)

  
- `NORMALS` Normals – Bake normals. 
- `DISPLACEMENT` Displacement – Bake displacement. 
- `VECTOR_DISPLACEMENT` Vector Displacement – Bake vector displacement.   Type: 

Literal[‘NORMALS’, ‘DISPLACEMENT’, ‘VECTOR_DISPLACEMENT’]

      use_automatic_name 

Automatically name the output file with the pass type (external only) (default False)

  Type: 

bool

      use_cage 

Cast rays to active object from a cage (default False)

  Type: 

bool

      use_clear 

Clear Images before baking (internal only) (default True)

  Type: 

bool

      use_lores_mesh 

Calculate heights against unsubdivided low resolution mesh (default False)

  Type: 

bool

      use_multires 

Bake directly from multires object (default False)

  Type: 

bool

      use_pass_color 

Color the pass (default True)

  Type: 

bool

      use_pass_diffuse 

Add diffuse contribution (default True)

  Type: 

bool

      use_pass_direct 

Add direct lighting contribution (default True)

  Type: 

bool

      use_pass_emit 

Add emission contribution (default True)

  Type: 

bool

      use_pass_glossy 

Add glossy contribution (default True)

  Type: 

bool

      use_pass_indirect 

Add indirect lighting contribution (default True)

  Type: 

bool

      use_pass_transmission 

Add transmission contribution (default True)

  Type: 

bool

      use_selected_to_active 

Bake shading on the surface of selected objects to the active object (default False)

  Type: 

bool

      use_split_materials 

Split external images per material (external only) (default False)

  Type: 

bool

      view_from 

Source of reflection ray directions (default `'ABOVE_SURFACE'`)

  
- `ABOVE_SURFACE` Above Surface – Cast rays from above the surface. 
- `ACTIVE_CAMERA` Active Camera – Use the active camera’s position to cast rays.   Type: 

Literal[‘ABOVE_SURFACE’, ‘ACTIVE_CAMERA’]

      width 

Horizontal dimension of the baking map (in [4, 10000], default 512)

  Type: 

int

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

  
- [`RenderSettings.bake`](bpy.types.RenderSettings.html#bpy.types.RenderSettings.bake)
