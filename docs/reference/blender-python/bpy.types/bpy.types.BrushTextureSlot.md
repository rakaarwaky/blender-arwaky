# bpy.types.BrushTextureSlot

# BrushTextureSlot(TextureSlot)

 

base classes — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct), [`TextureSlot`](bpy.types.TextureSlot.html#bpy.types.TextureSlot)

   class bpy.types.BrushTextureSlot(TextureSlot) 

Texture slot for textures in a Brush data-block

   angle 

Brush texture rotation (in [0, 6.28319], default 0.0)

  Type: 

float

      has_random_texture_angle 

(default False, readonly)

  Type: 

bool

      has_texture_angle 

(default False, readonly)

  Type: 

bool

      has_texture_angle_source 

(default False, readonly)

  Type: 

bool

      map_mode 

(default `'VIEW_PLANE'`)

  Type: 

Literal[‘VIEW_PLANE’, ‘AREA_PLANE’, ‘TILED’, ‘3D’, ‘RANDOM’, ‘STENCIL’]

      mask_map_mode 

(default `'VIEW_PLANE'`)

  Type: 

Literal[‘VIEW_PLANE’, ‘TILED’, ‘RANDOM’, ‘STENCIL’]

      random_angle 

Brush texture random angle (in [0, 6.28319], default 6.28319)

  Type: 

float

      use_rake 

(default False)

  Type: 

bool

      use_random 

(default False)

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
- [`TextureSlot.texture`](bpy.types.TextureSlot.html#bpy.types.TextureSlot.texture) 
- [`TextureSlot.name`](bpy.types.TextureSlot.html#bpy.types.TextureSlot.name) 
- [`TextureSlot.offset`](bpy.types.TextureSlot.html#bpy.types.TextureSlot.offset) 
- [`TextureSlot.scale`](bpy.types.TextureSlot.html#bpy.types.TextureSlot.scale)   
- [`TextureSlot.color`](bpy.types.TextureSlot.html#bpy.types.TextureSlot.color) 
- [`TextureSlot.blend_type`](bpy.types.TextureSlot.html#bpy.types.TextureSlot.blend_type) 
- [`TextureSlot.default_value`](bpy.types.TextureSlot.html#bpy.types.TextureSlot.default_value) 
- [`TextureSlot.output_node`](bpy.types.TextureSlot.html#bpy.types.TextureSlot.output_node)     

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
- [`TextureSlot.bl_rna_get_subclass`](bpy.types.TextureSlot.html#bpy.types.TextureSlot.bl_rna_get_subclass) 
- [`TextureSlot.bl_rna_get_subclass_py`](bpy.types.TextureSlot.html#bpy.types.TextureSlot.bl_rna_get_subclass_py)     

## References

  
- [`Brush.mask_texture_slot`](bpy.types.Brush.html#bpy.types.Brush.mask_texture_slot)   
- [`Brush.texture_slot`](bpy.types.Brush.html#bpy.types.Brush.texture_slot)
