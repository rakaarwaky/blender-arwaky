# bpy.types.ContextTempOverride

# ContextTempOverride

   class bpy.types.ContextTempOverride   logging_set(enable, *, hide_missing=False) 

Set context member logging options for this temporary override.

  Parameters:  
- enable (bool) – Enable logging of context member access. 
- hide_missing (bool) – When true, suppress logging access to members that are not available in the current context.     Special Methods  __enter__()  Return type: 

`ContextTempOverride`

      __exit__(exc_type, exc_value, traceback)  Parameters:  
- exc_type (type | None) – Exception type, or `None`. 
- exc_value (BaseException | None) – Exception instance, or `None`. 
- traceback (BaseException | None) – Traceback object, or `None`.   Return type: 

bool
