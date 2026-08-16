# bpy.ops.script

# Script Operators

   bpy.ops.script.execute_preset(*, filepath='', menu_idname='') 

Load a preset

  Parameters:  
- filepath (str) – filepath, (optional, never None) 
- menu_idname (str) – Menu ID Name, ID name of the menu this was called from (optional, never None)   Returns: 

Result of the operator call.

  Return type: 

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.html#rna-enum-operator-return-items)]]

  File: 

[startup/bl_operators/presets.py:285](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/presets.py#L285)

      bpy.ops.script.python_file_run(*, filepath='') 

Run Python file

  Parameters: 

filepath (str) – Path, (optional, never None)

  Returns: 

Result of the operator call.

  Return type: 

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.html#rna-enum-operator-return-items)]]

      bpy.ops.script.reload() 

Reload scripts

  Returns: 

Result of the operator call.

  Return type: 

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.html#rna-enum-operator-return-items)]]
