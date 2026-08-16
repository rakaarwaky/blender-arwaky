# bpy.types.Macro

# Macro(bpy_struct)

  

## Example Macro

 

This example creates a simple macro operator that moves the active object and then rotates it. It demonstrates:

  
- Defining a macro operator class. 
- Registering it and defining sub-operators. 
- Setting property values for each step.  

```python
import bpy

class OBJECT_OT_simple_macro(bpy.types.Macro):
    bl_idname = "object.simple_macro"
    bl_label = "Simple Transform Macro"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

def register():
    bpy.utils.register_class(OBJECT_OT_simple_macro)

    # Define steps after registration and set operator values via .properties
    step = OBJECT_OT_simple_macro.define("transform.translate")
    props = step.properties
    props.value = (1.0, 0.0, 0.0)
    props.constraint_axis = (True, False, False)

    step = OBJECT_OT_simple_macro.define("transform.rotate")
    props = step.properties
    props.value = 0.785398  # 45 degrees in radians
    props.orient_axis = 'Z'

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_simple_macro)

if __name__ == "__main__":
    register()

    # To run the macro:
    bpy.ops.object.simple_macro()
```

  

base class — [`bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct)

   class bpy.types.Macro(bpy_struct) 

Storage of a macro operator being executed, or registered after execution

   bl_cursor_pending 

Cursor to use when waiting for the user to select a location to activate the operator (when `bl_options` has `DEPENDS_ON_CURSOR` set) (default `'DEFAULT'`)

  Type: 

Literal[[Window Cursor Items](bpy_types_enum_items/window_cursor_items.html#rna-enum-window-cursor-items)]

      bl_description 

(default “”, never None)

  Type: 

str

      bl_idname 

(default “”, never None)

  Type: 

str

      bl_label 

(default “”, never None)

  Type: 

str

      bl_options 

Options for this operator type (default set())

  Type: 

set[Literal[[Operator Type Flag Items](bpy_types_enum_items/operator_type_flag_items.html#rna-enum-operator-type-flag-items)]]

      bl_translation_context 

(default “Operator”, never None)

  Type: 

str

      bl_undo_group 

(default “”, never None)

  Type: 

str

      has_reports 

Operator has a set of reports (warnings and errors) from last execution (default False, readonly)

  Type: 

bool

      name 

(default “”, readonly, never None)

  Type: 

str

      properties 

(readonly, never None)

  Type: 

[`OperatorProperties`](bpy.types.OperatorProperties.html#bpy.types.OperatorProperties)

      report(type, message) 

report

  Parameters:  
- type (set[Literal[[Wm Report Items](bpy_types_enum_items/wm_report_items.html#rna-enum-wm-report-items)]]) – Type 
- message (str) – Report Message, (never None)       classmethod poll(context) 

Test if the operator can be called or not

  Parameters: 

context ([`Context`](bpy.types.Context.html#bpy.types.Context) | None) – (never None)

  Return type: 

bool

      draw(context) 

Draw function for the operator

  Parameters: 

context ([`Context`](bpy.types.Context.html#bpy.types.Context) | None) – (never None)

      classmethod define(operator) 

Append an operator to a registered macro class.

  Parameters: 

operator (str) – Identifier of the operator. This does not have to be defined when this function is called.

  Returns: 

The operator macro for property access.

  Return type: 

[`OperatorMacro`](bpy.types.OperatorMacro.html#bpy.types.OperatorMacro)

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

      

### Inherited Properties

  
- [`bpy_struct.id_data`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.id_data)       

### Inherited Functions

  
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

### References

  
- [`Operator.macros`](bpy.types.Operator.html#bpy.types.Operator.macros)
