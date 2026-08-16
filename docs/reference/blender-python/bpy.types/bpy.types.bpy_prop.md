# bpy.types.bpy_prop

# bpy_prop

   class bpy.types.bpy_prop 

built-in base class for all property classes.

   as_bytes() 

Returns this string property as a byte rather than a Python string.

  Returns: 

The string as bytes.

  Return type: 

bytes

      path_from_id() 

Returns the data path from the ID to this property (string).

  Returns: 

The path from [`bpy.types.bpy_struct.id_data`](bpy.types.bpy_struct.html#bpy.types.bpy_struct.id_data) to this property.

  Return type: 

str

      path_from_module() 

Returns the full data path to this struct (as a string) from the bpy module.

  Returns: 

The full path to the data.

  Return type: 

str

  Raises: 

ValueError – 

if the input data cannot be converted into a full data path.

  

Note

 

Even if all input data is correct, this function might error out because Blender cannot derive a valid path. The incomplete path will be printed in the error message.

      update() 

Execute the properties update callback.

  

Note

 

This is called when assigning a property, however in rare cases it’s useful to call explicitly.

     data 

The data this property is using, (readonly)

  Type: 

[`bpy.types.bpy_struct`](bpy.types.bpy_struct.html#bpy.types.bpy_struct)

      id_data 

The [`bpy.types.ID`](bpy.types.ID.html#bpy.types.ID) object this data-block is from or None, (not available for all data types) (readonly)

  Type: 

[`bpy.types.ID`](bpy.types.ID.html#bpy.types.ID)

      rna_type 

The property type for introspection.

  Type: 

[`bpy.types.Property`](bpy.types.Property.html#bpy.types.Property)

    Special Methods  __eq__(other)  Parameters: 

other (object) – The other operand.

  Return type: 

bool

      __ge__(other)  Parameters: 

other (Self) – The other operand.

  Return type: 

bool

      __gt__(other)  Parameters: 

other (Self) – The other operand.

  Return type: 

bool

      __hash__()  Return type: 

int

      __le__(other)  Parameters: 

other (Self) – The other operand.

  Return type: 

bool

      __lt__(other)  Parameters: 

other (Self) – The other operand.

  Return type: 

bool

      __ne__(other)  Parameters: 

other (object) – The other operand.

  Return type: 

bool

      __repr__()  Return type: 

str

      __str__()  Return type: 

str
