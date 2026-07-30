# bpy.types.Gizmo

# Gizmo(bpy_struct)

 

base class — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct)

   class bpy.types.Gizmo(bpy_struct) 

Collection of gizmos

   alpha 

(in [0, 1], default 0.0)

  Type: 

float

      alpha_highlight 

(in [0, 1], default 0.0)

  Type: 

float

      bl_idname 

(default “”, never None)

  Type: 

str

      color 

(array of 3 items, in [0, inf], default (0.0, 0.0, 0.0))

  Type: 

[`mathutils.Color`](mathutils.html#mathutils.Color)

      color_highlight 

(array of 3 items, in [0, inf], default (0.0, 0.0, 0.0))

  Type: 

[`mathutils.Color`](mathutils.html#mathutils.Color)

      group 

Gizmo group this gizmo is a member of (readonly)

  Type: 

[`GizmoGroup`](bpy.types.GizmoGroup.html#bpy.types.GizmoGroup) | None

      hide 

(default False)

  Type: 

bool

      hide_keymap 

Ignore the key-map for this gizmo (default False)

  Type: 

bool

      hide_select 

(default False)

  Type: 

bool

      is_highlight 

(default False, readonly)

  Type: 

bool

      is_modal 

(default False, readonly)

  Type: 

bool

      line_width 

(in [0, inf], default 0.0)

  Type: 

float

      matrix_basis 

(multi-dimensional array of 4 * 4 items, in [-inf, inf], default ((0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)))

  Type: 

[`mathutils.Matrix`](mathutils.html#mathutils.Matrix)

      matrix_offset 

(multi-dimensional array of 4 * 4 items, in [-inf, inf], default ((0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)))

  Type: 

[`mathutils.Matrix`](mathutils.html#mathutils.Matrix)

      matrix_space 

(multi-dimensional array of 4 * 4 items, in [-inf, inf], default ((0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)))

  Type: 

[`mathutils.Matrix`](mathutils.html#mathutils.Matrix)

      matrix_world 

(multi-dimensional array of 4 * 4 items, in [-inf, inf], default ((0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)), readonly)

  Type: 

[`mathutils.Matrix`](mathutils.html#mathutils.Matrix)

      properties 

(readonly, never None)

  Type: 

[`GizmoProperties`](bpy.types.GizmoProperties.html#bpy.types.GizmoProperties)

      scale_basis 

(in [0, inf], default 0.0)

  Type: 

float

      select 

(default False)

  Type: 

bool

      select_bias 

Depth bias used for selection (in [-inf, inf], default 0.0)

  Type: 

float

      use_draw_hover 

(default False)

  Type: 

bool

      use_draw_modal 

Show while dragging (default False)

  Type: 

bool

      use_draw_offset_scale 

Scale the offset matrix (use to apply screen-space offset) (default False)

  Type: 

bool

      use_draw_scale 

Use scale when calculating the matrix (default True)

  Type: 

bool

      use_draw_value 

Show an indicator for the current value while dragging (default False)

  Type: 

bool

      use_event_handle_all 

When highlighted, do not pass events through to be handled by other keymaps (default False)

  Type: 

bool

      use_grab_cursor 

(default False)

  Type: 

bool

      use_operator_tool_properties 

Merge active tool properties on activation (does not overwrite existing) (default False)

  Type: 

bool

      use_select_background 

Don’t write into the depth buffer (default False)

  Type: 

bool

      use_tooltip 

Use tooltips when hovering over this gizmo (default True)

  Type: 

bool

      use_undo 

Push an undo step after each use of the gizmo (default False)

  Type: 

bool

      draw(context)  Parameters: 

context ([`Context`](bpy.types.Context.html#bpy.types.Context) | None) – (never None)

      draw_select(context, *, select_id=0)  Parameters:  
- context ([`Context`](bpy.types.Context.html#bpy.types.Context) | None) – (never None) 
- select_id (int) – (in [0, inf], optional)       test_select(context, location)  Parameters:  
- context ([`Context`](bpy.types.Context.html#bpy.types.Context) | None) – (never None) 
- location (Sequence[int]) – Location, Region coordinates (array of 2 items, in [-inf, inf], never None)   Returns: 

Use -1 to skip this gizmo (in [-1, inf])

  Return type: 

int

      modal(context, event, tweak)  Parameters:  
- context ([`Context`](bpy.types.Context.html#bpy.types.Context) | None) – (never None) 
- event ([`Event`](bpy.types.Event.html#bpy.types.Event) | None) – (never None) 
- tweak (set[Literal['PRECISE', 'SNAP']]) – Tweak   Returns: 

result

  Return type: 

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.html#rna-enum-operator-return-items)]]

      setup()    invoke(context, event)  Parameters:  
- context ([`Context`](bpy.types.Context.html#bpy.types.Context) | None) – (never None) 
- event ([`Event`](bpy.types.Event.html#bpy.types.Event) | None) – (never None)   Returns: 

result

  Return type: 

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.html#rna-enum-operator-return-items)]]

      exit(context, cancel)  Parameters:  
- context ([`Context`](bpy.types.Context.html#bpy.types.Context) | None) – (never None) 
- cancel (bool) – Cancel, otherwise confirm       select_refresh()    draw_preset_box(matrix, *, select_id=-1) 

Draw a box

  Parameters:  
- matrix ([`mathutils.Matrix`](mathutils.html#mathutils.Matrix) | Sequence[Sequence[float]]) – The matrix to transform (multi-dimensional array of 4 * 4 items, in [-inf, inf]) 
- select_id (int) – ID to use when gizmo is selectable. Use -1 when not selecting., (in [-1, inf], optional)       draw_preset_arrow(matrix, *, axis='POS_Z', select_id=-1) 

Draw a box

  Parameters:  
- matrix ([`mathutils.Matrix`](mathutils.html#mathutils.Matrix) | Sequence[Sequence[float]]) – The matrix to transform (multi-dimensional array of 4 * 4 items, in [-inf, inf]) 
- axis (Literal[[Object Axis Items](bpy_types_enum_items/object_axis_items.html#rna-enum-object-axis-items)]) – Arrow Orientation (optional) 
- select_id (int) – ID to use when gizmo is selectable. Use -1 when not selecting., (in [-1, inf], optional)       draw_preset_circle(matrix, *, axis='POS_Z', select_id=-1) 

Draw a box

  Parameters:  
- matrix ([`mathutils.Matrix`](mathutils.html#mathutils.Matrix) | Sequence[Sequence[float]]) – The matrix to transform (multi-dimensional array of 4 * 4 items, in [-inf, inf]) 
- axis (Literal[[Object Axis Items](bpy_types_enum_items/object_axis_items.html#rna-enum-object-axis-items)]) – Arrow Orientation (optional) 
- select_id (int) – ID to use when gizmo is selectable. Use -1 when not selecting., (in [-1, inf], optional)       target_set_prop(target, data, property, *, index=-1)  Parameters:  
- target (str) – Target property (never None) 
- data ([`AnyType`](bpy.types.AnyType.html#bpy.types.AnyType) | None) – Data from which to take property (never None) 
- property (str) – Identifier of property in data (never None) 
- index (int) – (in [-1, inf], optional)       target_set_operator(operator, *, index=0) 

Operator to run when activating the gizmo (overrides property targets)

  Parameters:  
- operator (str) – Target operator (never None) 
- index (int) – Part index, (in [0, 255], optional)   Returns: 

Operator properties to fill in

  Return type: 

[`OperatorProperties`](bpy.types.OperatorProperties.html#bpy.types.OperatorProperties)

      target_is_valid(property)  Parameters: 

property (str) – Property identifier (never None)

  Return type: 

bool

      draw_custom_shape(shape, *, matrix=None, select_id=None) 

Draw a shape created form `Gizmo.draw_custom_shape`.

  Parameters:  
- shape (Any) – The cached shape to draw. 
- matrix ([`mathutils.Matrix`](mathutils.html#mathutils.Matrix) | None) – 4x4 matrix, when not given `Gizmo.matrix_world` is used. 
- select_id (int | None) – The selection id. Only use when drawing within `Gizmo.draw_select`.       static new_custom_shape(type, verts) 

Create a new shape that can be passed to `Gizmo.draw_custom_shape`.

  Parameters:  
- type (Literal['POINTS', 'LINES', 'TRIS', 'LINE_STRIP']) – The type of shape to create. 
- verts (Sequence[Sequence[float]]) – Sequence of 2D or 3D coordinates.   Returns: 

The newly created shape (the return type make change).

  Return type: 

Any

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

      target_get_range(target) 

Get the range for this target property.

  Parameters: 

target (str) – Target property name.

  Returns: 

The range of this property (min, max).

  Return type: 

tuple[float, float]

      target_get_value(target) 

Get the value of this target property.

  Parameters: 

target (str) – Target property name.

  Returns: 

The value of the target property as a value or array based on the target type.

  Return type: 

float | tuple[float, …]

      target_set_handler(target, get, set, range=None) 

Assigns callbacks to a gizmos property.

  Parameters:  
- target (str) – Target property name. 
- get (Callable[[], float | Sequence[float]]) – Function that returns the value for this property (single value or sequence). 
- set (Callable[[tuple[float, ...]], Any]) – Function that takes a single value argument and applies it. 
- range (Callable[[], tuple[float, float]] | None) – Function that returns a (min, max) tuple for gizmos that use a range. The returned value is not used.       target_set_value(target) 

Set the value of this target property.

  Parameters: 

target (str) – Target property name.

      

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

  
- [`GizmoGroup.gizmos`](bpy.types.GizmoGroup.html#bpy.types.GizmoGroup.gizmos) 
- [`GizmoGroup.invoke_prepare`](bpy.types.GizmoGroup.html#bpy.types.GizmoGroup.invoke_prepare)   
- [`Gizmos.new`](bpy.types.Gizmos.html#bpy.types.Gizmos.new) 
- [`Gizmos.remove`](bpy.types.Gizmos.html#bpy.types.Gizmos.remove)
