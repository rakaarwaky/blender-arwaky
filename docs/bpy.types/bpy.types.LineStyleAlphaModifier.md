# bpy.types.LineStyleAlphaModifier

# LineStyleAlphaModifier(LineStyleModifier)

 

base classes — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct), [`LineStyleModifier`](bpy.types.LineStyleModifier.html#bpy.types.LineStyleModifier)

  

Subclasses

  
- [LineStyleAlphaModifier_AlongStroke(LineStyleAlphaModifier)](bpy.types.LineStyleAlphaModifier_AlongStroke.html) 
- [LineStyleAlphaModifier_CreaseAngle(LineStyleAlphaModifier)](bpy.types.LineStyleAlphaModifier_CreaseAngle.html) 
- [LineStyleAlphaModifier_Curvature_3D(LineStyleAlphaModifier)](bpy.types.LineStyleAlphaModifier_Curvature_3D.html) 
- [LineStyleAlphaModifier_DistanceFromCamera(LineStyleAlphaModifier)](bpy.types.LineStyleAlphaModifier_DistanceFromCamera.html) 
- [LineStyleAlphaModifier_DistanceFromObject(LineStyleAlphaModifier)](bpy.types.LineStyleAlphaModifier_DistanceFromObject.html) 
- [LineStyleAlphaModifier_Material(LineStyleAlphaModifier)](bpy.types.LineStyleAlphaModifier_Material.html) 
- [LineStyleAlphaModifier_Noise(LineStyleAlphaModifier)](bpy.types.LineStyleAlphaModifier_Noise.html) 
- [LineStyleAlphaModifier_Tangent(LineStyleAlphaModifier)](bpy.types.LineStyleAlphaModifier_Tangent.html)     class bpy.types.LineStyleAlphaModifier(LineStyleModifier) 

Base type to define alpha transparency modifiers

   name 

Name of the modifier (default “”, never None)

  Type: 

str

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
- [`LineStyleModifier.bl_rna_get_subclass`](bpy.types.LineStyleModifier.html#bpy.types.LineStyleModifier.bl_rna_get_subclass) 
- [`LineStyleModifier.bl_rna_get_subclass_py`](bpy.types.LineStyleModifier.html#bpy.types.LineStyleModifier.bl_rna_get_subclass_py)     

## References

  
- [`FreestyleLineStyle.alpha_modifiers`](bpy.types.FreestyleLineStyle.html#bpy.types.FreestyleLineStyle.alpha_modifiers) 
- [`LineStyleAlphaModifiers.new`](bpy.types.LineStyleAlphaModifiers.html#bpy.types.LineStyleAlphaModifiers.new)   
- [`LineStyleAlphaModifiers.remove`](bpy.types.LineStyleAlphaModifiers.html#bpy.types.LineStyleAlphaModifiers.remove)
