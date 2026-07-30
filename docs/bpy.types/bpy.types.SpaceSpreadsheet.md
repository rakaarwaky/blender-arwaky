# bpy.types.SpaceSpreadsheet

# SpaceSpreadsheet(Space)

 

base classes — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct), [`Space`](bpy.types.Space.html#bpy.types.Space)

   class bpy.types.SpaceSpreadsheet(Space) 

Spreadsheet space data

   attribute_domain 

Attribute domain to display (default `'POINT'`)

  Type: 

Literal[[Attribute Domain Items](bpy_types_enum_items/attribute_domain_items.html#rna-enum-attribute-domain-items)]

      geometry_component_type 

Part of the geometry to display data from (default `'MESH'`)

  Type: 

Literal[[Geometry Component Type Items](bpy_types_enum_items/geometry_component_type_items.html#rna-enum-geometry-component-type-items)]

      geometry_item_type 

Item Type (default `'DOMAIN'`)

  
- `DOMAIN` Domain – Domain data. 
- `BUNDLE` Bundle – Bundle data.   Type: 

Literal[‘DOMAIN’, ‘BUNDLE’]

      is_pinned 

Context path is pinned (default False)

  Type: 

bool

      object_eval_state 

(default `'EVALUATED'`)

  
- `EVALUATED` Evaluated – Use data from fully or partially evaluated object. 
- `ORIGINAL` Original – Use data from original object without any modifiers applied. 
- `VIEWER_NODE` Viewer Node – Use intermediate data from viewer node.   Type: 

Literal[‘EVALUATED’, ‘ORIGINAL’, ‘VIEWER_NODE’]

      row_filters 

Filters to remove rows from the displayed data (default None, readonly)

  Type: 

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.html#bpy.types.bpy_prop_collection)[[`SpreadsheetRowFilter`](bpy.types.SpreadsheetRowFilter.html#bpy.types.SpreadsheetRowFilter)]

      show_internal_attributes 

Display attributes with names starting with a period that are meant for internal use (default False)

  Type: 

bool

      show_only_selected 

Only include rows that correspond to selected elements (default False)

  Type: 

bool

      show_region_channels 

(default False)

  Type: 

bool

      show_region_footer 

(default False)

  Type: 

bool

      show_region_toolbar 

(default False)

  Type: 

bool

      show_region_ui 

(default False)

  Type: 

bool

      tables 

Persistent data for the tables shown in this spreadsheet editor (default None, readonly)

  Type: 

[`SpreadsheetTables`](bpy.types.SpreadsheetTables.html#bpy.types.SpreadsheetTables)[[`SpreadsheetTable`](bpy.types.SpreadsheetTable.html#bpy.types.SpreadsheetTable)]

      use_filter 

(default False)

  Type: 

bool

      viewer_path 

Path to the data that is displayed in the spreadsheet (readonly)

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

      classmethod draw_handler_add(callback, args, region_type, draw_type) 

Add a new draw handler to this space type. It will be called every time the specified region in the space type will be drawn. Note: All arguments are positional only for now.

  Parameters:  
- callback (Callable[..., Any]) – A function that will be called when the region is drawn. It gets the specified arguments as input, it’s return value is ignored. 
- args (tuple[Any, ...]) – Arguments that will be passed to the callback. 
- region_type (str) – The region type the callback draws in; usually `WINDOW`. ([`bpy.types.Region.type`](bpy.types.Region.html#bpy.types.Region.type)) 
- draw_type (str) – Usually `POST_PIXEL` for 2D drawing and `POST_VIEW` for 3D drawing. In some cases `PRE_VIEW` can be used. `BACKDROP` can be used for backdrops in the node editor.   Returns: 

Handler that can be removed later on.

  Return type: 

object

      classmethod draw_handler_remove(handler, region_type) 

Remove a draw handler that was added previously.

  Parameters:  
- handler (object) – The draw handler that should be removed. 
- region_type (str) – Region type the callback was added to.       

## Inherited Properties

  
- [`bpy_struct.id_data`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.id_data) 
- [`Space.type`](bpy.types.Space.html#bpy.types.Space.type)   
- [`Space.show_locked_time`](bpy.types.Space.html#bpy.types.Space.show_locked_time) 
- [`Space.show_region_header`](bpy.types.Space.html#bpy.types.Space.show_region_header)     

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
- [`Space.bl_rna_get_subclass`](bpy.types.Space.html#bpy.types.Space.bl_rna_get_subclass) 
- [`Space.bl_rna_get_subclass_py`](bpy.types.Space.html#bpy.types.Space.bl_rna_get_subclass_py) 
- [`Space.draw_handler_add`](bpy.types.Space.html#bpy.types.Space.draw_handler_add) 
- [`Space.draw_handler_remove`](bpy.types.Space.html#bpy.types.Space.draw_handler_remove)
