# bpy.types.LineStyleThicknessModifier

# LineStyleThicknessModifier(LineStyleModifier)

 

base classes — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct), [`LineStyleModifier`](bpy.types.LineStyleModifier.html#bpy.types.LineStyleModifier)

  

Subclasses

  
- [LineStyleThicknessModifier_AlongStroke(LineStyleThicknessModifier)](bpy.types.LineStyleThicknessModifier_AlongStroke.html) 
- [LineStyleThicknessModifier_Calligraphy(LineStyleThicknessModifier)](bpy.types.LineStyleThicknessModifier_Calligraphy.html) 
- [LineStyleThicknessModifier_CreaseAngle(LineStyleThicknessModifier)](bpy.types.LineStyleThicknessModifier_CreaseAngle.html) 
- [LineStyleThicknessModifier_Curvature_3D(LineStyleThicknessModifier)](bpy.types.LineStyleThicknessModifier_Curvature_3D.html) 
- [LineStyleThicknessModifier_DistanceFromCamera(LineStyleThicknessModifier)](bpy.types.LineStyleThicknessModifier_DistanceFromCamera.html) 
- [LineStyleThicknessModifier_DistanceFromObject(LineStyleThicknessModifier)](bpy.types.LineStyleThicknessModifier_DistanceFromObject.html) 
- [LineStyleThicknessModifier_Material(LineStyleThicknessModifier)](bpy.types.LineStyleThicknessModifier_Material.html) 
- [LineStyleThicknessModifier_Noise(LineStyleThicknessModifier)](bpy.types.LineStyleThicknessModifier_Noise.html) 
- [LineStyleThicknessModifier_Tangent(LineStyleThicknessModifier)](bpy.types.LineStyleThicknessModifier_Tangent.html)     class bpy.types.LineStyleThicknessModifier(LineStyleModifier) 

Base type to define line thickness modifiers

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

  
- [`FreestyleLineStyle.thickness_modifiers`](bpy.types.FreestyleLineStyle.html#bpy.types.FreestyleLineStyle.thickness_modifiers) 
- [`LineStyleThicknessModifiers.new`](bpy.types.LineStyleThicknessModifiers.html#bpy.types.LineStyleThicknessModifiers.new)   
- [`LineStyleThicknessModifiers.remove`](bpy.types.LineStyleThicknessModifiers.html#bpy.types.LineStyleThicknessModifiers.remove)
