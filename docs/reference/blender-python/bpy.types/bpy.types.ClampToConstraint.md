# bpy.types.ClampToConstraint

# ClampToConstraint(Constraint)

 

base classes — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct), [`Constraint`](bpy.types.Constraint.html#bpy.types.Constraint)

   class bpy.types.ClampToConstraint(Constraint) 

Constrain an object’s location to the nearest point along the target path

   main_axis 

Main axis of movement (default `'CLAMPTO_AUTO'`)

  Type: 

Literal[‘CLAMPTO_AUTO’, ‘CLAMPTO_X’, ‘CLAMPTO_Y’, ‘CLAMPTO_Z’]

      target 

Target Object (Curves only)

  Type: 

[`Object`](bpy.types.Object.html#bpy.types.Object) | None

      use_cyclic 

Treat curve as cyclic curve (no clamping to curve bounding box) (default False)

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
- [`Constraint.name`](bpy.types.Constraint.html#bpy.types.Constraint.name) 
- [`Constraint.type`](bpy.types.Constraint.html#bpy.types.Constraint.type) 
- [`Constraint.is_override_data`](bpy.types.Constraint.html#bpy.types.Constraint.is_override_data) 
- [`Constraint.owner_space`](bpy.types.Constraint.html#bpy.types.Constraint.owner_space) 
- [`Constraint.target_space`](bpy.types.Constraint.html#bpy.types.Constraint.target_space) 
- [`Constraint.space_object`](bpy.types.Constraint.html#bpy.types.Constraint.space_object) 
- [`Constraint.space_subtarget`](bpy.types.Constraint.html#bpy.types.Constraint.space_subtarget)   
- [`Constraint.mute`](bpy.types.Constraint.html#bpy.types.Constraint.mute) 
- [`Constraint.enabled`](bpy.types.Constraint.html#bpy.types.Constraint.enabled) 
- [`Constraint.show_expanded`](bpy.types.Constraint.html#bpy.types.Constraint.show_expanded) 
- [`Constraint.is_valid`](bpy.types.Constraint.html#bpy.types.Constraint.is_valid) 
- [`Constraint.active`](bpy.types.Constraint.html#bpy.types.Constraint.active) 
- [`Constraint.influence`](bpy.types.Constraint.html#bpy.types.Constraint.influence) 
- [`Constraint.error_location`](bpy.types.Constraint.html#bpy.types.Constraint.error_location) 
- [`Constraint.error_rotation`](bpy.types.Constraint.html#bpy.types.Constraint.error_rotation)     

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
- [`Constraint.bl_rna_get_subclass`](bpy.types.Constraint.html#bpy.types.Constraint.bl_rna_get_subclass) 
- [`Constraint.bl_rna_get_subclass_py`](bpy.types.Constraint.html#bpy.types.Constraint.bl_rna_get_subclass_py)
