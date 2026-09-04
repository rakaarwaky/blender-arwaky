# bpy.types.Header

# Header(bpy_struct)

 

base class — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct)

   class bpy.types.Header(bpy_struct) 

Editor header containing UI elements

   bl_idname 

If this is set, the header gets a custom ID, otherwise it takes the name of the class used to define the header; for example, if the class name is “OBJECT_HT_hello”, and bl_idname is not set by the script, then bl_idname = “OBJECT_HT_hello” (default “”, never None)

  Type: 

str

      bl_region_type 

The region where the header is going to be used in (defaults to header region) (default `'HEADER'`)

  Type: 

Literal[[Region Type Items](bpy_types_enum_items/region_type_items.html#rna-enum-region-type-items)]

      bl_space_type 

The space where the header is going to be used in (default `'EMPTY'`)

  Type: 

Literal[[Space Type Items](bpy_types_enum_items/space_type_items.html#rna-enum-space-type-items)]

      layout 

Structure of the header in the UI (readonly)

  Type: 

[`UILayout`](bpy.types.UILayout.html#bpy.types.UILayout) | None

      draw(context) 

Draw UI elements into the header UI layout

  Parameters: 

context ([`Context`](bpy.types.Context.html#bpy.types.Context) | None) – The context

      classmethod append(draw_func) 

Append a draw function to this menu, takes the same arguments as the menus draw function

  Parameters: 

draw_func (Callable[[Self, [`Context`](bpy.types.Context.html#bpy.types.Context)], None]) – Draw function to append.

      classmethod is_extended() 

Test if any draw function has been added via `append()` or `prepend()`.

  Returns: 

True when at least one draw function has been added.

  Return type: 

bool

      classmethod prepend(draw_func) 

Prepend a draw function to this menu, takes the same arguments as the menus draw function

  Parameters: 

draw_func (Callable[[Self, [`Context`](bpy.types.Context.html#bpy.types.Context)], None]) – Draw function to prepend.

      classmethod remove(draw_func) 

Remove a draw function that has been added to this menu.

  Parameters: 

draw_func (Callable[[Self, [`Context`](bpy.types.Context.html#bpy.types.Context)], None]) – Draw function previously registered via `append()` or `prepend()`.

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
