# idprop.types

# ID Property Access (idprop.types)

   class idprop.types.IDPropertyArray 

An array of values with a fixed type, supporting indexing and slicing.

   to_list() 

Return the array as a list.

  Returns: 

The array as a list.

  Return type: 

list[int] | list[float] | list[bool]

      typecode 

The type of the data in the array {‘f’: float (32-bit), ‘d’: double (64-bit), ‘i’: int, ‘b’: bool}. Both ‘f’ and ‘d’ use Python’s `float` type but differ in storage precision.

  Type: 

Literal[‘f’, ‘d’, ‘i’, ‘b’]

    Special Methods  __getitem__(key)  Parameters: 

key (int) – Index or key.

  Return type: 

float | int | bool

      __getitem__(key)  Parameters: 

key (slice) – Index or key.

  Return type: 

list[float] | list[int] | list[bool]

      __len__()  Return type: 

int

      __repr__()  Return type: 

str

      __setitem__(key, value)  Parameters:  
- key (int) – Index. 
- value (float | int | bool) – Value to assign.        class idprop.types.IDPropertyGroup 

A dictionary-like group of ID properties, supporting key access, iteration, and membership testing.

  

Note

 

Only supports a maximum of 1024 levels of nesting.

    clear() 

Clear all members from this group.

    get(key, default=None) 

Return the value for key, if it exists, else default.

  Parameters:  
- key (str) – The key to look up. 
- default (Any) – Value to return if key is not found.   Returns: 

The value for the key, or default if not found.

  Return type: 

Any

      items() 

Return a view of the items in the group, behaves like dictionary method items.

  Returns: 

A view of the items.

  Return type: 

`IDPropertyGroupViewItems`

      keys() 

Return a view of the keys in the group.

  Returns: 

A view of the keys.

  Return type: 

`IDPropertyGroupViewKeys`

      pop(key, default) 

Remove an item from the group, returning a Python representation.

  Raises: 

KeyError – When the item doesn’t exist and no default is given.

  Parameters:  
- key (str) – Name of item to remove. 
- default (Any) – Value to return when key isn’t found (optional, a `KeyError` is raised when omitted and the key is not found).   Returns: 

A Python representation of the removed item, or default.

  Return type: 

Any

      to_dict() 

Return a purely Python version of the group.

  Returns: 

A dictionary representation of the group.

  Return type: 

dict[str, Any]

      update(other) 

Update key-value pairs from other, overwriting existing keys.

  

Note

 

Unlike `dict.update()`, keyword arguments are not supported.

   Parameters: 

other (`IDPropertyGroup` | dict[str, Any]) – Updates the values in the group with this.

      values() 

Return the values associated with this group.

  Returns: 

A view of the values.

  Return type: 

`IDPropertyGroupViewValues`

      name 

The name of this Group.

  Type: 

str

    Special Methods  __contains__(item)  Parameters: 

item (object) – Item to test for membership.

  Return type: 

bool

      __getitem__(key)  Parameters: 

key (str) – Property name.

  Return type: 

Any

      __hash__()  Return type: 

int

      __iter__()  Return type: 

`IDPropertyGroupIterKeys`

      __len__()  Return type: 

int

      __repr__()  Return type: 

str

      __setitem__(key, value)  Parameters:  
- key (str) – Property name. 
- value (Any) – Value to assign.        class idprop.types.IDPropertyGroupIterItems 

Iterator over `IDPropertyGroup` items (key/value pairs).

 Special Methods  __eq__(other)  Parameters: 

other (object) – The other operand.

  Return type: 

bool

      __hash__()  Return type: 

int

      __iter__()  Return type: 

`IDPropertyGroupIterItems`

      __ne__(other)  Parameters: 

other (object) – The other operand.

  Return type: 

bool

      __next__()  Return type: 

tuple[str, Any]

      __repr__()  Return type: 

str

      __str__()  Return type: 

str

       class idprop.types.IDPropertyGroupIterKeys 

Iterator over `IDPropertyGroup` keys.

 Special Methods  __eq__(other)  Parameters: 

other (object) – The other operand.

  Return type: 

bool

      __hash__()  Return type: 

int

      __iter__()  Return type: 

`IDPropertyGroupIterKeys`

      __ne__(other)  Parameters: 

other (object) – The other operand.

  Return type: 

bool

      __next__()  Return type: 

str

      __repr__()  Return type: 

str

      __str__()  Return type: 

str

       class idprop.types.IDPropertyGroupIterValues 

Iterator over `IDPropertyGroup` values.

 Special Methods  __eq__(other)  Parameters: 

other (object) – The other operand.

  Return type: 

bool

      __hash__()  Return type: 

int

      __iter__()  Return type: 

`IDPropertyGroupIterValues`

      __ne__(other)  Parameters: 

other (object) – The other operand.

  Return type: 

bool

      __next__()  Return type: 

Any

      __repr__()  Return type: 

str

      __str__()  Return type: 

str

       class idprop.types.IDPropertyGroupViewItems 

A view of `IDPropertyGroup` items as key/value pairs (supports `len()`, `in`, iteration, and `reversed()`).

 Special Methods  __contains__(item)  Parameters: 

item (object) – Item to test for membership.

  Return type: 

bool

      __eq__(other)  Parameters: 

other (object) – The other operand.

  Return type: 

bool

      __hash__()  Return type: 

int

      __iter__()  Return type: 

`IDPropertyGroupIterItems`

      __len__()  Return type: 

int

      __ne__(other)  Parameters: 

other (object) – The other operand.

  Return type: 

bool

      __repr__()  Return type: 

str

      __str__()  Return type: 

str

       class idprop.types.IDPropertyGroupViewKeys 

A view of `IDPropertyGroup` keys (supports `len()`, `in`, iteration, and `reversed()`).

 Special Methods  __contains__(item)  Parameters: 

item (object) – Item to test for membership.

  Return type: 

bool

      __eq__(other)  Parameters: 

other (object) – The other operand.

  Return type: 

bool

      __hash__()  Return type: 

int

      __iter__()  Return type: 

`IDPropertyGroupIterKeys`

      __len__()  Return type: 

int

      __ne__(other)  Parameters: 

other (object) – The other operand.

  Return type: 

bool

      __repr__()  Return type: 

str

      __str__()  Return type: 

str

       class idprop.types.IDPropertyGroupViewValues 

A view of `IDPropertyGroup` values (supports `len()`, `in`, iteration, and `reversed()`).

 Special Methods  __contains__(item)  Parameters: 

item (object) – Item to test for membership.

  Return type: 

bool

      __eq__(other)  Parameters: 

other (object) – The other operand.

  Return type: 

bool

      __hash__()  Return type: 

int

      __iter__()  Return type: 

`IDPropertyGroupIterValues`

      __len__()  Return type: 

int

      __ne__(other)  Parameters: 

other (object) – The other operand.

  Return type: 

bool

      __repr__()  Return type: 

str

      __str__()  Return type: 

str
