# bpy.types.bpy_prop_array

# bpy_prop_array

 

base classes — [`bpy_prop`](bpy.types.bpy_prop.html#bpy.types.bpy_prop)

   class bpy.types.bpy_prop_array(bpy_prop) 

built-in class used for array properties.

   foreach_get(seq) 

This is a function to give fast access to array data.

  Parameters: 

seq (MutableSequence[Any]) – Buffer to read element values into, must match the length of this array.

      foreach_set(seq) 

This is a function to give fast access to array data.

  Parameters: 

seq (Sequence[Any]) – Element values to write, must match the length of this array.

    Special Methods  __contains__(item)  Parameters: 

item (object) – Item to test for membership.

  Return type: 

bool

      __getitem__(key)  Parameters: 

key (int) – Index or key.

  Return type: 

float

      __iter__()  Return type: 

`bpy_prop_array`

      __len__()  Return type: 

int

      __repr__()  Return type: 

str

      __setitem__(key, value)  Parameters:  
- key (int) – Index or key. 
- value (object) – Value to assign.
