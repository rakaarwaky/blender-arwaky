# bpy.types.ShaderFx

# ShaderFx(bpy_struct)

 

base class — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct)

  

Subclasses

  
- [ShaderFxBlur(ShaderFx)](bpy.types.ShaderFxBlur.html) 
- [ShaderFxColorize(ShaderFx)](bpy.types.ShaderFxColorize.html) 
- [ShaderFxFlip(ShaderFx)](bpy.types.ShaderFxFlip.html) 
- [ShaderFxGlow(ShaderFx)](bpy.types.ShaderFxGlow.html) 
- [ShaderFxPixel(ShaderFx)](bpy.types.ShaderFxPixel.html) 
- [ShaderFxRim(ShaderFx)](bpy.types.ShaderFxRim.html) 
- [ShaderFxShadow(ShaderFx)](bpy.types.ShaderFxShadow.html) 
- [ShaderFxSwirl(ShaderFx)](bpy.types.ShaderFxSwirl.html) 
- [ShaderFxWave(ShaderFx)](bpy.types.ShaderFxWave.html)     class bpy.types.ShaderFx(bpy_struct) 

Effect affecting the Grease Pencil object

   name 

Effect name (default “”, never None)

  Type: 

str

      show_expanded 

Set effect expansion in the user interface (default False)

  Type: 

bool

      show_in_editmode 

Display effect in Edit mode (default False)

  Type: 

bool

      show_render 

Use effect during render (default False)

  Type: 

bool

      show_viewport 

Display effect in viewport (default False)

  Type: 

bool

      type 

(default `'FX_BLUR'`, readonly)

  Type: 

Literal[[Object Shaderfx Type Items](bpy_types_enum_items/object_shaderfx_type_items.html#rna-enum-object-shaderfx-type-items)]

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

  
- [`Object.shader_effects`](bpy.types.Object.html#bpy.types.Object.shader_effects) 
- [`ObjectShaderFx.new`](bpy.types.ObjectShaderFx.html#bpy.types.ObjectShaderFx.new)   
- [`ObjectShaderFx.remove`](bpy.types.ObjectShaderFx.html#bpy.types.ObjectShaderFx.remove)
