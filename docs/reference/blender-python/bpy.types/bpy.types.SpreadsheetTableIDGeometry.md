# bpy.types.SpreadsheetTableIDGeometry

# SpreadsheetTableIDGeometry(SpreadsheetTableID)

 

base classes — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct), [`SpreadsheetTableID`](bpy.types.SpreadsheetTableID.html#bpy.types.SpreadsheetTableID)

   class bpy.types.SpreadsheetTableIDGeometry(SpreadsheetTableID)   attribute_domain 

Attribute domain to display (default `'POINT'`, readonly)

  Type: 

Literal[[Attribute Domain Items](bpy_types_enum_items/attribute_domain_items.html#rna-enum-attribute-domain-items)]

      geometry_component_type 

Part of the geometry to display data from (default `'MESH'`, readonly)

  Type: 

Literal[[Geometry Component Type Items](bpy_types_enum_items/geometry_component_type_items.html#rna-enum-geometry-component-type-items)]

      geometry_item_type 

Item Type (default `'DOMAIN'`, readonly)

  
- `DOMAIN` Domain – Domain data. 
- `BUNDLE` Bundle – Bundle data.   Type: 

Literal[‘DOMAIN’, ‘BUNDLE’]

      layer_index 

Index of the Grease Pencil layer (in [-inf, inf], default 0, readonly)

  Type: 

int

      object_eval_state 

(default `'EVALUATED'`, readonly)

  
- `EVALUATED` Evaluated – Use data from fully or partially evaluated object. 
- `ORIGINAL` Original – Use data from original object without any modifiers applied. 
- `VIEWER_NODE` Viewer Node – Use intermediate data from viewer node.   Type: 

Literal[‘EVALUATED’, ‘ORIGINAL’, ‘VIEWER_NODE’]

      viewer_path 

Path to the data that is displayed (readonly)

  Type: 

[`ViewerPath`](bpy.types.ViewerPath.html#bpy.types.ViewerPath) | None

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
- [`SpreadsheetTableID.type`](bpy.types.SpreadsheetTableID.html#bpy.types.SpreadsheetTableID.type)     

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
- [`SpreadsheetTableID.bl_rna_get_subclass`](bpy.types.SpreadsheetTableID.html#bpy.types.SpreadsheetTableID.bl_rna_get_subclass) 
- [`SpreadsheetTableID.bl_rna_get_subclass_py`](bpy.types.SpreadsheetTableID.html#bpy.types.SpreadsheetTableID.bl_rna_get_subclass_py)
