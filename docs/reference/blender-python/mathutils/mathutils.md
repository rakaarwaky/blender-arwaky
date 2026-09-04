# mathutils

# Math Types & Utilities (mathutils)

 

This module provides access to math operations.

  

Note

 

Classes, methods and attributes that accept vectors also accept other numeric sequences, such as tuples, lists.

  

The `mathutils` module provides the following classes:

  
- `Color`, 
- `Euler`, 
- `Matrix`, 
- `Quaternion`, 
- `Vector`,   

Submodules

  
- [Geometry Utilities (mathutils.geometry)](mathutils.geometry.html) 
- [BVHTree Utilities (mathutils.bvhtree)](mathutils.bvhtree.html) 
- [KDTree Utilities (mathutils.kdtree)](mathutils.kdtree.html) 
- [Interpolation Utilities (mathutils.interpolate)](mathutils.interpolate.html) 
- [Noise Utilities (mathutils.noise)](mathutils.noise.html)   

```python
import mathutils
from math import radians

vec = mathutils.Vector((1.0, 2.0, 3.0))

mat_rot = mathutils.Matrix.Rotation(radians(90.0), 4, 'X')
mat_trans = mathutils.Matrix.Translation(vec)

mat = mat_trans @ mat_rot
mat.invert()

mat3 = mat.to_3x3()
quat1 = mat.to_quaternion()
quat2 = mat3.to_quaternion()

quat_diff = quat1.rotation_difference(quat2)

print(quat_diff.angle)
```

    class mathutils.Color(rgb=(0.0, 0.0, 0.0), /) 

This object gives access to Colors in Blender.

 

Most colors returned by Blender APIs are in scene linear color space, as defined by the OpenColorIO configuration. The notable exception is user interface theming colors, which are in sRGB color space.

  Parameters: 

rgb (Sequence[float]) – (red, green, blue) color values where (0, 0, 0) is black & (1, 1, 1) is white.

   

```python
import mathutils

# Color values are represented as RGB values from 0 - 1, this is blue.
col = mathutils.Color((0.0, 0.0, 1.0))

# As well as r/g/b attribute access you can adjust them by h/s/v.
col.s *= 0.5

# You can access its components by attribute or index.
print("Color R:", col.r)
print("Color G:", col[1])
print("Color B:", col[-1])
print("Color HSV: {:.2f}, {:.2f}, {:.2f}".format(*col))

# Components of an existing color can be set.
col[:] = 0.0, 0.5, 1.0

# Components of an existing color can use slice notation to get a tuple.
print("Values: {:f}, {:f}, {:f}".format(*col))

# Colors can be added and subtracted.
col += mathutils.Color((0.25, 0.0, 0.0))

# Color can be multiplied, in this example color is scaled to 0-255
# can printed as integers.
print("Color: {:d}, {:d}, {:d}".format(*(int(c) for c in (col * 255.0))))

# This example prints the color as hexadecimal.
print("Hexadecimal: {:02x}{:02x}{:02x}".format(int(col.r * 255), int(col.g * 255), int(col.b * 255)))

# Direct buffer access is supported.
print(memoryview(col).tobytes())
```

    copy() 

Returns a copy of this color.

  Returns: 

A copy of the color.

  Return type: 

`Color`

    

Note

 

use this to get a copy of a wrapped color with no reference to the original data.

     freeze() 

Make this object immutable.

 

After this the object can be hashed, used in dictionaries & sets.

  Returns: 

An instance of this object.

  Return type: 

Self

      from_aces_to_scene_linear() 

Convert from ACES2065-1 linear to scene linear color space.

  Returns: 

A color in scene linear color space.

  Return type: 

`Color`

      from_acescg_to_scene_linear() 

Convert from ACEScg linear to scene linear color space.

  Returns: 

A color in scene linear color space.

  Return type: 

`Color`

      from_rec2020_linear_to_scene_linear() 

Convert from Rec.2020 linear color space to scene linear color space.

  Returns: 

A color in scene linear color space.

  Return type: 

`Color`

      from_rec709_linear_to_scene_linear() 

Convert from Rec.709 linear color space to scene linear color space.

  Returns: 

A color in scene linear color space.

  Return type: 

`Color`

      from_scene_linear_to_aces() 

Convert from scene linear to ACES2065-1 linear color space.

  Returns: 

A color in ACES2065-1 linear color space.

  Return type: 

`Color`

      from_scene_linear_to_acescg() 

Convert from scene linear to ACEScg linear color space.

  Returns: 

A color in ACEScg linear color space.

  Return type: 

`Color`

      from_scene_linear_to_rec2020_linear() 

Convert from scene linear to Rec.2020 linear color space.

  Returns: 

A color in Rec.2020 linear color space.

  Return type: 

`Color`

      from_scene_linear_to_rec709_linear() 

Convert from scene linear to Rec.709 linear color space.

  Returns: 

A color in Rec.709 linear color space.

  Return type: 

`Color`

      from_scene_linear_to_srgb() 

Convert from scene linear to sRGB color space.

  Returns: 

A color in sRGB color space.

  Return type: 

`Color`

      from_scene_linear_to_xyz_d65() 

Convert from scene linear to CIE XYZ (Illuminant D65) color space.

  Returns: 

A color in XYZ color space.

  Return type: 

`Color`

      from_srgb_to_scene_linear() 

Convert from sRGB to scene linear color space.

  Returns: 

A color in scene linear color space.

  Return type: 

`Color`

      from_xyz_d65_to_scene_linear() 

Convert from CIE XYZ (Illuminant D65) to scene linear color space.

  Returns: 

A color in scene linear color space.

  Return type: 

`Color`

      b 

Blue color channel.

  Type: 

float

      g 

Green color channel.

  Type: 

float

      h 

HSV Hue component in [0, 1].

  Type: 

float

      hsv 

HSV Values in [0, 1].

  Type: 

tuple[float, float, float]

      is_frozen 

True when this object has been frozen (read-only).

  Type: 

bool

      is_valid 

True when the owner of this data is valid.

  Type: 

bool

      is_wrapped 

True when this object wraps external data (read-only).

  Type: 

bool

      owner 

The item this is wrapping or None (read-only).

  Type: 

Any

      r 

Red color channel.

  Type: 

float

      s 

HSV Saturation component in [0, 1].

  Type: 

float

      v 

HSV Value component in [0, 1].

  Type: 

float

    Special Methods  __add__(other)  Parameters: 

other (Self) – The other operand.

  Return type: 

`Color`

      __eq__(other)  Parameters: 

other (object) – The other operand.

  Return type: 

bool

      __getitem__(key)  Parameters: 

key (int) – Index or key.

  Return type: 

float

      __hash__()  Return type: 

int

      __iadd__(other)  Parameters: 

other (Self) – The other operand.

  Return type: 

`Color`

      __imul__(other)  Parameters: 

other (float) – Scalar.

  Return type: 

`Color`

      __isub__(other)  Parameters: 

other (Self) – The other operand.

  Return type: 

`Color`

      __itruediv__(other)  Parameters: 

other (float) – Scalar divisor.

  Return type: 

`Color`

      __len__()  Return type: 

int

      __mul__(other)  Parameters: 

other (float) – Scalar.

  Return type: 

`Color`

      __ne__(other)  Parameters: 

other (object) – The other operand.

  Return type: 

bool

      __neg__()  Return type: 

`Color`

      __pos__()  Return type: 

`Color`

      __repr__()  Return type: 

str

      __rmul__(other)  Parameters: 

other (float) – Scalar.

  Return type: 

`Color`

      __setitem__(key, value)  Parameters:  
- key (int) – Index or key. 
- value (object) – Value to assign.       __str__()  Return type: 

str

      __sub__(other)  Parameters: 

other (Self) – The other operand.

  Return type: 

`Color`

      __truediv__(other)  Parameters: 

other (float) – Scalar divisor.

  Return type: 

`Color`

       class mathutils.Euler(angles=(0.0, 0.0, 0.0), order='XYZ', /) 

This object gives access to Eulers in Blender.

  

See also

 

[Euler angles](https://en.wikipedia.org/wiki/Euler_angles) on Wikipedia.

   Parameters:  
- angles (Sequence[float]) – (X, Y, Z) angles in radians. 
- order (Literal['XYZ', 'XZY', 'YXZ', 'YZX', 'ZXY', 'ZYX']) – Euler rotation order.    

```python
import mathutils
import math

# Create a new euler with default axis rotation order.
eul = mathutils.Euler((0.0, math.radians(45.0), 0.0), 'XYZ')

# Rotate the euler.
eul.rotate_axis('Z', math.radians(10.0))

# You can access its components by attribute or index.
print("Euler X", eul.x)
print("Euler Y", eul[1])
print("Euler Z", eul[-1])

# Components of an existing euler can be set.
eul[:] = 1.0, 2.0, 3.0

# Components of an existing euler can use slice notation to get a tuple.
print("Values: {:f}, {:f}, {:f}".format(*eul))

# The order can be set at any time too.
eul.order = 'ZYX'

# Eulers can be used to rotate vectors.
vec = mathutils.Vector((0.0, 0.0, 1.0))
vec.rotate(eul)

# Often its useful to convert the euler into a matrix so it can be used as
# transformations with more flexibility.
mat_rot = eul.to_matrix()
mat_loc = mathutils.Matrix.Translation((2.0, 3.0, 4.0))
mat = mat_loc @ mat_rot.to_4x4()

# Direct buffer access is supported.
print(memoryview(eul).tobytes())
```

    copy() 

Returns a copy of this euler.

  Returns: 

A copy of the euler.

  Return type: 

`Euler`

    

Note

 

use this to get a copy of a wrapped euler with no reference to the original data.

     freeze() 

Make this object immutable.

 

After this the object can be hashed, used in dictionaries & sets.

  Returns: 

An instance of this object.

  Return type: 

Self

      make_compatible(other, /) 

Make this euler compatible with another, so interpolating between them works as intended.

  Parameters: 

other (`Euler`) – Other euler rotation.

    

Note

 

the rotation order is not taken into account for this function.

     rotate(other, /) 

Rotates the euler by another mathutils value.

  Parameters: 

other (`Euler` | `Quaternion` | `Matrix`) – rotation component of mathutils value

      rotate_axis(axis, angle, /) 

Rotates the euler a certain amount, wrapping the result to produce a unique euler rotation (no 720 degree pitches).

  Parameters:  
- axis (Literal['X', 'Y', 'Z']) – An axis string. 
- angle (float) – angle in radians.       to_matrix() 

Return a matrix representation of the euler.

  Returns: 

A 3x3 rotation matrix representation of the euler.

  Return type: 

`Matrix`

      to_quaternion() 

Return a quaternion representation of the euler.

  Returns: 

Quaternion representation of the euler.

  Return type: 

`Quaternion`

      zero() 

Set all values to zero.

    is_frozen 

True when this object has been frozen (read-only).

  Type: 

bool

      is_valid 

True when the owner of this data is valid.

  Type: 

bool

      is_wrapped 

True when this object wraps external data (read-only).

  Type: 

bool

      order 

Euler rotation order.

  Type: 

Literal[‘XYZ’, ‘XZY’, ‘YXZ’, ‘YZX’, ‘ZXY’, ‘ZYX’]

      owner 

The item this is wrapping or None (read-only).

  Type: 

Any

      x 

Euler axis angle in radians.

  Type: 

float

      y 

Euler axis angle in radians.

  Type: 

float

      z 

Euler axis angle in radians.

  Type: 

float

    Special Methods  __eq__(other)  Parameters: 

other (object) – The other operand.

  Return type: 

bool

      __getitem__(key)  Parameters: 

key (int) – Index or key.

  Return type: 

float

      __hash__()  Return type: 

int

      __len__()  Return type: 

int

      __ne__(other)  Parameters: 

other (object) – The other operand.

  Return type: 

bool

      __repr__()  Return type: 

str

      __setitem__(key, value)  Parameters:  
- key (int) – Index or key. 
- value (object) – Value to assign.       __str__()  Return type: 

str

       class mathutils.Matrix(rows=((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)), /) 

This object gives access to Matrices in Blender, supporting square and rectangular matrices from 2x2 up to 4x4.

  Parameters: 

rows (Sequence[Sequence[float]]) – Sequence of rows.

   

```python
import mathutils
import math

# Create a location matrix.
mat_loc = mathutils.Matrix.Translation((2.0, 3.0, 4.0))

# Create an identity matrix.
mat_sca = mathutils.Matrix.Scale(0.5, 4, (0.0, 0.0, 1.0))

# Create a rotation matrix.
mat_rot = mathutils.Matrix.Rotation(math.radians(45.0), 4, 'X')

# Combine transformations.
mat_out = mat_loc @ mat_rot @ mat_sca
print(mat_out)

# Extract components back out of the matrix as two vectors and a quaternion.
loc, rot, sca = mat_out.decompose()
print(loc, rot, sca)

# Recombine extracted components.
mat_out2 = mathutils.Matrix.LocRotScale(loc, rot, sca)
print(mat_out2)

# It can also be useful to access components of a matrix directly.
mat = mathutils.Matrix()
mat[0][0], mat[1][0], mat[2][0] = 0.0, 1.0, 2.0

mat[0][0:3] = 0.0, 1.0, 2.0

# Each item in a matrix is a vector so vector utility functions can be used.
mat[0].xyz = 0.0, 1.0, 2.0

# Direct buffer access is supported.
print(memoryview(mat).tobytes())
```

    classmethod Diagonal(vector, /) 

Create a diagonal (scaling) matrix using the values from the vector.

  Parameters: 

vector (Sequence[float]) – The vector of values for the diagonal.

  Returns: 

A diagonal matrix.

  Return type: 

`Matrix`

      classmethod Identity(size, /) 

Create an identity matrix.

  Parameters: 

size (int) – The size of the identity matrix to construct [2, 4].

  Returns: 

A new identity matrix.

  Return type: 

`Matrix`

      classmethod LocRotScale(location, rotation, scale, /) 

Create a matrix combining translation, rotation and scale, acting as the inverse of the decompose() method.

 

Any of the inputs may be replaced with None if not needed.

  Parameters:  
- location (Sequence[float] | None) – The translation component. 
- rotation (`Matrix` | `Quaternion` | `Euler` | None) – The rotation component as a 3x3 matrix, quaternion, euler or None for no rotation. 
- scale (Sequence[float] | None) – The scale component.   Returns: 

Combined transformation as a 4x4 matrix.

  Return type: 

`Matrix`

   

```python
# Compute local object transformation matrix:

import bpy
import mathutils

obj = bpy.context.object
if obj.rotation_mode == 'QUATERNION':
    matrix = mathutils.Matrix.LocRotScale(obj.location, obj.rotation_quaternion, obj.scale)
else:
    matrix = mathutils.Matrix.LocRotScale(obj.location, obj.rotation_euler, obj.scale)
```

     classmethod OrthoProjection(axis, size, /) 

Create a matrix to represent an orthographic projection.

  Parameters:  
- axis (Literal['X', 'Y', 'XY', 'XZ', 'YZ'] | Sequence[float]) – An axis string, where a single axis is for a 2D matrix. Or a vector for an arbitrary axis 
- size (int) – The size of the projection matrix to construct [2, 4].   Returns: 

A new projection matrix.

  Return type: 

`Matrix`

      classmethod Rotation(angle, size, axis=None, /) 

Create a matrix representing a rotation.

  Parameters:  
- angle (float) – The angle of rotation desired, in radians. 
- size (int) – The size of the rotation matrix to construct [2, 4]. 
- axis (Literal['X', 'Y', 'Z'] | Sequence[float] | None) – Axis of rotation: a single-character string (‘X’, ‘Y’ or ‘Z’) or a 3D vector. Required for `size` 3 or 4. Must be None (or omitted) when `size` is 2 - 2D rotation has no axis.   Returns: 

A new rotation matrix.

  Return type: 

`Matrix`

      classmethod Scale(factor, size, axis=None, /) 

Create a matrix representing a scaling.

  Parameters:  
- factor (float) – The factor of scaling to apply. 
- size (int) – The size of the scale matrix to construct [2, 4]. 
- axis (Sequence[float] | None) – Direction along which to scale. When None (or omitted), `factor` is applied uniformly along all axes.   Returns: 

A new scale matrix.

  Return type: 

`Matrix`

      classmethod Shear(plane, size, factor, /) 

Create a matrix to represent a shear transformation.

  Parameters:  
- plane (Literal['X', 'Y', 'XY', 'XZ', 'YZ']) – An axis string, where a single axis is for a 2D matrix only. 
- size (int) – The size of the shear matrix to construct [2, 4]. 
- factor (float | Sequence[float]) – The factor of shear to apply. For a 2 size matrix use a single float. For a 3 or 4 size matrix pass a pair of floats corresponding with the plane axis.   Returns: 

A new shear matrix.

  Return type: 

`Matrix`

      classmethod Translation(vector, /) 

Create a matrix representing a translation.

  Parameters: 

vector (Sequence[float]) – The translation vector.

  Returns: 

An identity matrix with a translation.

  Return type: 

`Matrix`

      adjugate() 

Set the matrix to its adjugate.

  Raises: 

ValueError – if the matrix cannot be adjugated.

    

See also

 

[Adjugate matrix](https://en.wikipedia.org/wiki/Adjugate_matrix) on Wikipedia.

     adjugated() 

Return an adjugated copy of the matrix.

  Returns: 

the adjugated matrix.

  Return type: 

`Matrix`

  Raises: 

ValueError – if the matrix cannot be adjugated

      copy() 

Returns a copy of this matrix.

  Returns: 

A copy of the matrix.

  Return type: 

`Matrix`

      decompose() 

Return the translation, rotation, and scale components of this 4x4 matrix.

  Returns: 

Tuple of translation, rotation, and scale.

  Return type: 

tuple[`Vector`, `Quaternion`, `Vector`]

      determinant() 

Return the determinant of a matrix.

  Returns: 

Return the determinant of a matrix.

  Return type: 

float

    

See also

 

[Determinant](https://en.wikipedia.org/wiki/Determinant) on Wikipedia.

     freeze() 

Make this object immutable.

 

After this the object can be hashed, used in dictionaries & sets.

  Returns: 

An instance of this object.

  Return type: 

Self

      identity() 

Set the matrix to the identity matrix.

  

Note

 

An object with a location and rotation of zero, and a scale of one will have an identity matrix.

   

See also

 

[Identity matrix](https://en.wikipedia.org/wiki/Identity_matrix) on Wikipedia.

     invert(fallback=None, /) 

Set the matrix to its inverse.

  Parameters: 

fallback (`Matrix` | None) – Set the matrix to this value when the inverse cannot be calculated (instead of raising a `ValueError` exception).

    

See also

 

[Inverse matrix](https://en.wikipedia.org/wiki/Inverse_matrix) on Wikipedia.

     invert_safe() 

Set the matrix to its inverse, will never error. If degenerated (e.g. zero scale on an axis), add some epsilon to its diagonal, to get an invertible one. If tweaked matrix is still degenerated, set to the identity matrix instead.

  

See also

 

[Inverse Matrix](https://en.wikipedia.org/wiki/Inverse_matrix) on Wikipedia.

     inverted(fallback=None, /) 

Return an inverted copy of the matrix.

  Parameters: 

fallback (Any) – return this when the inverse can’t be calculated (instead of raising a `ValueError`).

  Returns: 

The inverted matrix or fallback when given.

  Return type: 

`Matrix` | Any

      inverted_safe() 

Return an inverted copy of the matrix, will never error. If degenerated (e.g. zero scale on an axis), add some epsilon to its diagonal, to get an invertible one. If tweaked matrix is still degenerated, return the identity matrix instead.

  Returns: 

the inverted matrix.

  Return type: 

`Matrix`

      lerp(other, factor, /) 

Returns the interpolation of two matrices. Uses polar decomposition, see “Matrix Animation and Polar Decomposition”, Shoemake and Duff, 1992.

  Parameters:  
- other (`Matrix`) – value to interpolate with. 
- factor (float) – The interpolation value in [0.0, 1.0].   Returns: 

The interpolated matrix.

  Return type: 

`Matrix`

      normalize() 

Normalize each of the matrix columns (3x3 and 4x4 only).

  

Note

 

for 4x4 matrices, the 4th column (translation) is left untouched.

     normalized() 

Return a column normalized matrix (3x3 and 4x4 only).

  Returns: 

a column normalized matrix

  Return type: 

`Matrix`

    

Note

 

for 4x4 matrices, the 4th column (translation) is left untouched.

     resize_4x4() 

Resize the matrix to 4x4.

    rotate(other, /) 

Rotates the matrix by another mathutils value.

  

Note

 

The matrix must be 3x3.

   

Note

 

If any of the columns are not unit length this may not have desired results.

   Parameters: 

other (`Euler` | `Quaternion` | `Matrix`) – rotation component of mathutils value

      to_2x2() 

Return a 2x2 copy of this matrix.

  Returns: 

a new matrix.

  Return type: 

`Matrix`

      to_3x3() 

Return a 3x3 copy of this matrix.

  Returns: 

a new matrix.

  Return type: 

`Matrix`

      to_4x4() 

Return a 4x4 copy of this matrix.

  Returns: 

a new matrix.

  Return type: 

`Matrix`

      to_euler(order='XYZ', euler_compat=None, /) 

Return an Euler representation of the rotation matrix (3x3 or 4x4 matrix only).

  Parameters:  
- order (Literal['XYZ', 'XZY', 'YXZ', 'YZX', 'ZXY', 'ZYX']) – A rotation order string. 
- euler_compat (`Euler` | None) – Optional euler argument the new euler will be made compatible with (no axis flipping between them). Useful for converting a series of matrices to animation curves.   Returns: 

Euler representation of the matrix.

  Return type: 

`Euler`

      to_quaternion() 

Return a quaternion representation of the rotation matrix.

  Returns: 

Quaternion representation of the rotation matrix.

  Return type: 

`Quaternion`

      to_scale() 

Return the scale part of a 3x3 or 4x4 matrix.

  Returns: 

Return the scale of a matrix.

  Return type: 

`Vector`

    

Note

 

This method does not return a negative scale on any axis because it is not possible to obtain this data from the matrix alone.

     to_translation() 

Return the translation part of a 4x4 matrix.

  Returns: 

Return the translation of a matrix.

  Return type: 

`Vector`

      transpose() 

Set the matrix to its transpose.

  

See also

 

[Transpose](https://en.wikipedia.org/wiki/Transpose) on Wikipedia.

     transposed() 

Return a new, transposed matrix.

  Returns: 

a transposed matrix

  Return type: 

`Matrix`

      zero() 

Set all the matrix values to zero.

    col 

Access the matrix by columns (read-only).

  Type: 

`MatrixAccess`

      is_frozen 

True when this object has been frozen (read-only).

  Type: 

bool

      is_identity 

True if this is an identity matrix (read-only).

  Type: 

bool

      is_negative 

True if this matrix results in a negative scale, 3x3 and 4x4 only, (read-only).

  Type: 

bool

      is_orthogonal 

True if this matrix is orthogonal, 3x3 and 4x4 only, (read-only).

  Type: 

bool

      is_orthogonal_axis_vectors 

True if this matrix has orthogonal axis vectors, 3x3 and 4x4 only, (read-only).

  Type: 

bool

      is_valid 

True when the owner of this data is valid.

  Type: 

bool

      is_wrapped 

True when this object wraps external data (read-only).

  Type: 

bool

      median_scale 

The average scale applied to each axis (read-only).

  Type: 

float

      owner 

The item this is wrapping or None (read-only).

  Type: 

Any

      row 

Access the matrix by rows (default), (read-only).

  Type: 

`MatrixAccess`

      translation 

The translation component of the matrix.

  Type: 

`Vector`

    Special Methods  __add__(other)  Parameters: 

other (Self) – The other operand.

  Return type: 

`Matrix`

      __eq__(other)  Parameters: 

other (object) – The other operand.

  Return type: 

bool

      __getitem__(key)  Parameters: 

key (int) – Index or key.

  Return type: 

`Vector`

      __hash__()  Return type: 

int

      __imatmul__(other)  Parameters: 

other (Self) – The other operand.

  Return type: 

`Matrix`

      __imul__(other)  Parameters: 

other (`Matrix`) – The other operand.

  Return type: 

`Matrix`

      __imul__(other)  Parameters: 

other (float) – The other operand.

  Return type: 

`Matrix`

      __invert__()  Return type: 

`Matrix`

      __len__()  Return type: 

int

      __matmul__(other)  Parameters: 

other (`Matrix`) – The other operand.

  Return type: 

`Matrix`

      __matmul__(other)  Parameters: 

other (`Vector`) – The other operand.

  Return type: 

`Vector`

      __mul__(other)  Parameters: 

other (`Matrix`) – The other operand.

  Return type: 

`Matrix`

      __mul__(other)  Parameters: 

other (float) – The other operand.

  Return type: 

`Matrix`

      __ne__(other)  Parameters: 

other (object) – The other operand.

  Return type: 

bool

      __repr__()  Return type: 

str

      __rmul__(other)  Parameters: 

other (float) – Scalar.

  Return type: 

`Matrix`

      __setitem__(key, value)  Parameters:  
- key (int) – Index or key. 
- value (object) – Value to assign.       __str__()  Return type: 

str

      __sub__(other)  Parameters: 

other (Self) – The other operand.

  Return type: 

`Matrix`

       class mathutils.MatrixAccess 

An indexable type for accessing matrix rows or columns as `Vector` types.

 Special Methods  __getitem__(key)  Parameters: 

key (int) – Index or key.

  Return type: 

float

      __iter__()  Return type: 

`MatrixAccess`

      __len__()  Return type: 

int

      __setitem__(key, value)  Parameters:  
- key (int) – Index or key. 
- value (object) – Value to assign.        class mathutils.Quaternion(seq=(1.0, 0.0, 0.0, 0.0), angle=0.0, /) 

This object gives access to Quaternions in Blender.

  Parameters:  
- seq (Sequence[float]) – A (w, x, y, z) quaternion, a 3D exponential map vector, or a 3D axis vector (when angle is also provided). 
- angle (float) – rotation angle, in radians    

The constructor takes arguments in various forms:

  (), no args

Create an identity quaternion

  (wxyz)

Create a quaternion from a `(w, x, y, z)` vector.

  (exponential_map)

Create a quaternion from a 3d exponential map vector.

  

See also

 

`to_exponential_map()`

   (axis, angle)

Create a quaternion representing a rotation of angle radians over axis.

  

See also

 

`to_axis_angle()`

    

```python
import mathutils
import math

# A new rotation 90 degrees about the Y axis.
quat_a = mathutils.Quaternion((0.7071068, 0.0, 0.7071068, 0.0))

# Passing values to Quaternion's directly can be confusing so axis, angle
# is supported for initializing too.
quat_b = mathutils.Quaternion((0.0, 1.0, 0.0), math.radians(90.0))

print("Check quaternions match", quat_a == quat_b)

# Like matrices, quaternions can be multiplied to accumulate rotational values.
quat_a = mathutils.Quaternion((0.0, 1.0, 0.0), math.radians(90.0))
quat_b = mathutils.Quaternion((0.0, 0.0, 1.0), math.radians(45.0))
quat_out = quat_a @ quat_b

# Print the quaternion, euler degrees for mere mortals and (axis, angle).
print("Final Rotation:")
print(quat_out)
print("{:.2f}, {:.2f}, {:.2f}".format(*(math.degrees(a) for a in quat_out.to_euler())))
print("({:.2f}, {:.2f}, {:.2f}), {:.2f}".format(*quat_out.axis, math.degrees(quat_out.angle)))

# Multiple rotations can be interpolated using the exponential map.
quat_c = mathutils.Quaternion((1.0, 0.0, 0.0), math.radians(15.0))
exp_avg = (quat_a.to_exponential_map() +
           quat_b.to_exponential_map() +
           quat_c.to_exponential_map()) / 3.0
quat_avg = mathutils.Quaternion(exp_avg)
print("Average rotation:")
print(quat_avg)

# Direct buffer access is supported.
print(memoryview(quat_avg).tobytes())
```

    conjugate() 

Set the quaternion to its conjugate (negate x, y, z).

    conjugated() 

Return a new conjugated quaternion.

  Returns: 

a new quaternion.

  Return type: 

`Quaternion`

      copy() 

Returns a copy of this quaternion.

  Returns: 

A copy of the quaternion.

  Return type: 

`Quaternion`

    

Note

 

use this to get a copy of a wrapped quaternion with no reference to the original data.

     cross(other, /) 

Return the cross product of this quaternion and another.

  Parameters: 

other (`Quaternion`) – The other quaternion to perform the cross product with.

  Returns: 

The cross product.

  Return type: 

`Quaternion`

      dot(other, /) 

Return the dot product of this quaternion and another.

  Parameters: 

other (`Quaternion`) – The other quaternion to perform the dot product with.

  Returns: 

The dot product.

  Return type: 

float

      freeze() 

Make this object immutable.

 

After this the object can be hashed, used in dictionaries & sets.

  Returns: 

An instance of this object.

  Return type: 

Self

      identity() 

Set the quaternion to an identity quaternion.

    invert() 

Set the quaternion to its inverse.

    inverted() 

Return a new, inverted quaternion.

  Returns: 

the inverted value.

  Return type: 

`Quaternion`

      make_compatible(other, /) 

Make this quaternion compatible with another, so interpolating between them works as intended.

  Parameters: 

other (`Quaternion`) – The reference quaternion to make this one compatible with.

      negate() 

Set the quaternion to its negative.

    normalize() 

Normalize the quaternion.

    normalized() 

Return a new normalized quaternion.

  Returns: 

a normalized copy.

  Return type: 

`Quaternion`

      rotate(other, /) 

Rotates the quaternion by another mathutils value.

  Parameters: 

other (`Euler` | `Quaternion` | `Matrix`) – rotation component of mathutils value

      rotation_difference(other, /) 

Returns a quaternion representing the rotational difference.

  Parameters: 

other (`Quaternion`) – second quaternion.

  Returns: 

the rotational difference between the two quat rotations.

  Return type: 

`Quaternion`

      slerp(other, factor, /) 

Returns the interpolation of two quaternions.

  Parameters:  
- other (`Quaternion`) – value to interpolate with. 
- factor (float) – The interpolation value in [0.0, 1.0].   Returns: 

The interpolated rotation.

  Return type: 

`Quaternion`

      to_axis_angle() 

Return the axis, angle representation of the quaternion.

  Returns: 

Axis, angle.

  Return type: 

tuple[`Vector`, float]

      to_euler(order='XYZ', euler_compat=None, /) 

Return Euler representation of the quaternion.

  Parameters:  
- order (Literal['XYZ', 'XZY', 'YXZ', 'YZX', 'ZXY', 'ZYX']) – Rotation order. 
- euler_compat (`Euler` | None) – Optional euler argument the new euler will be made compatible with (no axis flipping between them). Useful for converting a series of quaternions to animation curves.   Returns: 

Euler representation of the quaternion.

  Return type: 

`Euler`

      to_exponential_map() 

Return the exponential map representation of the quaternion.

 

This representation consists of the rotation axis multiplied by the rotation angle. Such a representation is useful for interpolation between multiple orientations.

  Returns: 

3D exponential map.

  Return type: 

`Vector`

   

To convert back to a quaternion, pass it to the `Quaternion` constructor.

    to_matrix() 

Return a matrix representation of the quaternion.

  Returns: 

A 3x3 rotation matrix representation of the quaternion.

  Return type: 

`Matrix`

      to_swing_twist(axis, /) 

Split the rotation into a swing quaternion with the specified axis fixed at zero, and the remaining twist rotation angle.

  Parameters: 

axis (Literal['X', 'Y', 'Z']) – Twist axis as a string.

  Returns: 

Swing, twist angle.

  Return type: 

tuple[`Quaternion`, float]

      angle 

Angle of the quaternion.

  Type: 

float

      axis 

Quaternion axis as a vector.

  Type: 

`Vector`

      is_frozen 

True when this object has been frozen (read-only).

  Type: 

bool

      is_valid 

True when the owner of this data is valid.

  Type: 

bool

      is_wrapped 

True when this object wraps external data (read-only).

  Type: 

bool

      magnitude 

Size of the quaternion (read-only).

  Type: 

float

      owner 

The item this is wrapping or None (read-only).

  Type: 

Any

      w 

Quaternion component value.

  Type: 

float

      x 

Quaternion component value.

  Type: 

float

      y 

Quaternion component value.

  Type: 

float

      z 

Quaternion component value.

  Type: 

float

    Special Methods  __add__(other)  Parameters: 

other (Self) – The other operand.

  Return type: 

`Quaternion`

      __eq__(other)  Parameters: 

other (object) – The other operand.

  Return type: 

bool

      __getitem__(key)  Parameters: 

key (int) – Index or key.

  Return type: 

float

      __hash__()  Return type: 

int

      __imatmul__(other)  Parameters: 

other (Self) – The other operand.

  Return type: 

`Quaternion`

      __imul__(other)  Parameters: 

other (`Quaternion`) – The other operand.

  Return type: 

`Quaternion`

      __imul__(other)  Parameters: 

other (float) – The other operand.

  Return type: 

`Quaternion`

      __len__()  Return type: 

int

      __matmul__(other)  Parameters: 

other (`Quaternion`) – The other operand.

  Return type: 

`Quaternion`

      __matmul__(other)  Parameters: 

other (`Vector`) – The other operand.

  Return type: 

`Vector`

      __mul__(other)  Parameters: 

other (`Quaternion`) – The other operand.

  Return type: 

`Quaternion`

      __mul__(other)  Parameters: 

other (float) – The other operand.

  Return type: 

`Quaternion`

      __ne__(other)  Parameters: 

other (object) – The other operand.

  Return type: 

bool

      __neg__()  Return type: 

`Quaternion`

      __pos__()  Return type: 

`Quaternion`

      __repr__()  Return type: 

str

      __rmul__(other)  Parameters: 

other (float) – Scalar.

  Return type: 

`Quaternion`

      __setitem__(key, value)  Parameters:  
- key (int) – Index or key. 
- value (object) – Value to assign.       __str__()  Return type: 

str

      __sub__(other)  Parameters: 

other (Self) – The other operand.

  Return type: 

`Quaternion`

       class mathutils.Vector(seq=(0.0, 0.0, 0.0), /) 

This object gives access to Vectors in Blender.

  Parameters: 

seq (Sequence[float]) – Components of the vector, must be a sequence of at least two.

   

```python
import mathutils

# Zero length vector.
vec = mathutils.Vector((0.0, 0.0, 1.0))

# Unit length vector.
vec_a = vec.normalized()

vec_b = mathutils.Vector((0.0, 1.0, 2.0))

vec2d = mathutils.Vector((1.0, 2.0))
vec3d = mathutils.Vector((1.0, 0.0, 0.0))
vec4d = vec_a.to_4d()

# Other `mathutils` types.
quat = mathutils.Quaternion()
matrix = mathutils.Matrix()

# Comparison operators can be done on Vector classes:

# (In)equality operators == and != test component values, e.g. 1,2,3 != 3,2,1
vec_a == vec_b
vec_a != vec_b

# Ordering operators >, >=, > and <= test vector length.
vec_a > vec_b
vec_a >= vec_b
vec_a < vec_b
vec_a <= vec_b

# Math can be performed on Vector classes.
vec_a + vec_b
vec_a - vec_b
vec_a @ vec_b
vec_a * 10.0
matrix @ vec_a
quat @ vec_a
-vec_a

# You can access a vector object like a sequence.
x = vec_a[0]
len(vec)
vec_a[:] = vec_b
vec_a[:] = 1.0, 2.0, 3.0
vec2d[:] = vec3d[:2]

# Vectors support 'swizzle' operations.
# See https://en.wikipedia.org/wiki/Swizzling_(computer_graphics)
vec.xyz = vec.zyx
vec.xy = vec4d.zw
vec.xyz = vec4d.wzz
vec4d.wxyz = vec.yxyx

# Direct buffer access is supported.
raw_data = memoryview(vec).tobytes()
```

    classmethod Fill(size, fill=0.0, /) 

Create a vector of length size with all values set to fill.

  Parameters:  
- size (int) – The length of the vector to be created. 
- fill (float) – The value used to fill the vector.   Returns: 

A new vector.

  Return type: 

`Vector`

      classmethod Linspace(start, stop, size, /) 

Create a vector of the specified size which is filled with linearly spaced values between start and stop values.

  Parameters:  
- start (float) – The start of the range used to fill the vector. 
- stop (float) – The end of the range used to fill the vector. 
- size (int) – The size of the vector to be created.   Returns: 

A new vector.

  Return type: 

`Vector`

      classmethod Range(start, stop, step=1, /) 

Create a vector filled with a range of values.

 

This method can also be called with a single argument, in which case the argument is interpreted as `stop` and `start` defaults to 0.

  Parameters:  
- start (int) – The start of the range used to fill the vector. 
- stop (int) – The end of the range used to fill the vector. 
- step (int) – The step between successive values in the vector.   Returns: 

A new vector.

  Return type: 

`Vector`

      classmethod Repeat(vector, size, /) 

Create a vector by repeating the values in vector until the required size is reached.

  Parameters:  
- vector (`Vector`) – The vector to draw values from. 
- size (int) – The size of the vector to be created.   Returns: 

A new vector.

  Return type: 

`Vector`

      angle(other, fallback=None, /) 

Return the angle between two vectors.

  

Note

 

For 4D vectors, only the x, y, z components are used.

   Parameters:  
- other (`Vector`) – another vector to compare the angle with 
- fallback (Any) – return this when the angle can’t be calculated (zero length vector), (instead of raising a `ValueError`).   Returns: 

angle in radians or fallback when given

  Return type: 

float | Any

      angle_signed(other, fallback=None, /) 

Return the signed angle between two 2D vectors (clockwise is positive).

  Parameters:  
- other (`Vector`) – another vector to compare the angle with 
- fallback (Any) – return this when the angle can’t be calculated (zero length vector), (instead of raising a `ValueError`).   Returns: 

angle in radians or fallback when given

  Return type: 

float | Any

      copy() 

Returns a copy of this vector.

  Returns: 

A copy of the vector.

  Return type: 

`Vector`

    

Note

 

use this to get a copy of a wrapped vector with no reference to the original data.

     cross(other, /) 

Return the cross product of this vector and another.

  Parameters: 

other (`Vector`) – The other vector to perform the cross product with.

  Returns: 

The cross product as a vector or a float when 2D vectors are used.

  Return type: 

`Vector` | float

    

Note

 

both vectors must be 2D or 3D

     dot(other, /) 

Return the dot product of this vector and another.

  Parameters: 

other (`Vector`) – The other vector to perform the dot product with.

  Returns: 

The dot product.

  Return type: 

float

      freeze() 

Make this object immutable.

 

After this the object can be hashed, used in dictionaries & sets.

  Returns: 

An instance of this object.

  Return type: 

Self

      lerp(other, factor, /) 

Returns the interpolation of two vectors.

  Parameters:  
- other (`Vector`) – value to interpolate with. 
- factor (float) – The interpolation value in [0.0, 1.0].   Returns: 

The interpolated vector.

  Return type: 

`Vector`

      negate() 

Set all values to their negative.

    normalize() 

Normalize the vector, making the length of the vector always 1.0.

  

Warning

 

Normalizing a vector where all values are zero has no effect.

   

Note

 

For 4D vectors, only the x, y, z components are normalized; the w component is left untouched. The resulting 4D vector may not have unit length.

     normalized() 

Return a new, normalized vector.

  

Note

 

For 4D vectors, only the x, y, z components are normalized; the w component is left untouched. The resulting 4D vector may not have unit length.

   Returns: 

a normalized copy of the vector

  Return type: 

`Vector`

      orthogonal() 

Return a perpendicular vector.

  Returns: 

a new vector 90 degrees from this vector.

  Return type: 

`Vector`

    

Note

 

the axis is undefined, only use when any orthogonal vector is acceptable.

     project(other, /) 

Return the projection of this vector onto the other.

  Parameters: 

other (`Vector`) – second vector.

  Returns: 

the parallel projection vector

  Return type: 

`Vector`

      reflect(mirror, /) 

Return the reflection vector from the mirror argument.

  Parameters: 

mirror (`Vector`) – This vector could be a normal from the reflecting surface.

  Returns: 

The reflected vector matching the size of this vector.

  Return type: 

`Vector`

      resize(size, /) 

Resize the vector to have size number of elements.

  Parameters: 

size (int) – The new size of the vector.

      resize_2d() 

Resize the vector to 2D (x, y).

    resize_3d() 

Resize the vector to 3D (x, y, z).

    resize_4d() 

Resize the vector to 4D (x, y, z, w).

    resized(size, /) 

Return a resized copy of the vector with size number of elements.

  Parameters: 

size (int) – The new size of the vector.

  Returns: 

A new vector.

  Return type: 

`Vector`

      rotate(other, /) 

Rotate the vector by a rotation value.

  

Note

 

2D vectors are a special case that can only be rotated by a 2x2 matrix.

   Parameters: 

other (`Euler` | `Quaternion` | `Matrix`) – rotation component of mathutils value

      rotation_difference(other, /) 

Returns a quaternion representing the rotational difference between this vector and another.

  Parameters: 

other (`Vector`) – second vector.

  Returns: 

the rotational difference between the two vectors.

  Return type: 

`Quaternion`

    

Note

 

2D vectors raise an `AttributeError`.

     slerp(other, factor, fallback=None, /) 

Returns the interpolation of two non-zero vectors (spherical coordinates).

  Parameters:  
- other (`Vector`) – value to interpolate with. 
- factor (float) – The interpolation value typically in [0.0, 1.0]. 
- fallback (Any) – return this when the vector can’t be calculated (zero length vector or direct opposites), (instead of raising a `ValueError`).   Returns: 

The interpolated vector.

  Return type: 

`Vector`

      to_2d() 

Return a 2d copy of the vector.

  Returns: 

a new vector

  Return type: 

`Vector`

      to_3d() 

Return a 3d copy of the vector.

  Returns: 

a new vector

  Return type: 

`Vector`

      to_4d() 

Return a 4d copy of the vector.

  Returns: 

a new vector

  Return type: 

`Vector`

      to_track_quat(track='Z', up='Y', /) 

Return a quaternion rotation from the vector and the track and up axis.

  Parameters:  
- track (Literal['X', 'Y', 'Z', '-X', '-Y', '-Z']) – Track axis string. 
- up (Literal['X', 'Y', 'Z']) – Up axis string.   Returns: 

rotation from the vector and the track and up axis.

  Return type: 

`Quaternion`

      to_tuple(precision=-1, /) 

Return this vector as a tuple with a given precision.

  Parameters: 

precision (int) – The number to round the value to in [-1, 21].

  Returns: 

the values of the vector rounded by precision

  Return type: 

tuple[float, …]

      zero() 

Set all values to zero.

    is_frozen 

True when this object has been frozen (read-only).

  Type: 

bool

      is_valid 

True when the owner of this data is valid.

  Type: 

bool

      is_wrapped 

True when this object wraps external data (read-only).

  Type: 

bool

      length 

Vector Length.

  Type: 

float

      length_squared 

Vector length squared (v.dot(v)).

  Type: 

float

      magnitude 

Vector Length.

  Type: 

float

      owner 

The item this is wrapping or None (read-only).

  Type: 

Any

      w 

Vector W axis (4D Vectors only).

  Type: 

float

      ww  Type: 

`Vector`

      www  Type: 

`Vector`

      wwww  Type: 

`Vector`

      wwwx  Type: 

`Vector`

      wwwy  Type: 

`Vector`

      wwwz  Type: 

`Vector`

      wwx  Type: 

`Vector`

      wwxw  Type: 

`Vector`

      wwxx  Type: 

`Vector`

      wwxy  Type: 

`Vector`

      wwxz  Type: 

`Vector`

      wwy  Type: 

`Vector`

      wwyw  Type: 

`Vector`

      wwyx  Type: 

`Vector`

      wwyy  Type: 

`Vector`

      wwyz  Type: 

`Vector`

      wwz  Type: 

`Vector`

      wwzw  Type: 

`Vector`

      wwzx  Type: 

`Vector`

      wwzy  Type: 

`Vector`

      wwzz  Type: 

`Vector`

      wx  Type: 

`Vector`

      wxw  Type: 

`Vector`

      wxww  Type: 

`Vector`

      wxwx  Type: 

`Vector`

      wxwy  Type: 

`Vector`

      wxwz  Type: 

`Vector`

      wxx  Type: 

`Vector`

      wxxw  Type: 

`Vector`

      wxxx  Type: 

`Vector`

      wxxy  Type: 

`Vector`

      wxxz  Type: 

`Vector`

      wxy  Type: 

`Vector`

      wxyw  Type: 

`Vector`

      wxyx  Type: 

`Vector`

      wxyy  Type: 

`Vector`

      wxyz  Type: 

`Vector`

      wxz  Type: 

`Vector`

      wxzw  Type: 

`Vector`

      wxzx  Type: 

`Vector`

      wxzy  Type: 

`Vector`

      wxzz  Type: 

`Vector`

      wy  Type: 

`Vector`

      wyw  Type: 

`Vector`

      wyww  Type: 

`Vector`

      wywx  Type: 

`Vector`

      wywy  Type: 

`Vector`

      wywz  Type: 

`Vector`

      wyx  Type: 

`Vector`

      wyxw  Type: 

`Vector`

      wyxx  Type: 

`Vector`

      wyxy  Type: 

`Vector`

      wyxz  Type: 

`Vector`

      wyy  Type: 

`Vector`

      wyyw  Type: 

`Vector`

      wyyx  Type: 

`Vector`

      wyyy  Type: 

`Vector`

      wyyz  Type: 

`Vector`

      wyz  Type: 

`Vector`

      wyzw  Type: 

`Vector`

      wyzx  Type: 

`Vector`

      wyzy  Type: 

`Vector`

      wyzz  Type: 

`Vector`

      wz  Type: 

`Vector`

      wzw  Type: 

`Vector`

      wzww  Type: 

`Vector`

      wzwx  Type: 

`Vector`

      wzwy  Type: 

`Vector`

      wzwz  Type: 

`Vector`

      wzx  Type: 

`Vector`

      wzxw  Type: 

`Vector`

      wzxx  Type: 

`Vector`

      wzxy  Type: 

`Vector`

      wzxz  Type: 

`Vector`

      wzy  Type: 

`Vector`

      wzyw  Type: 

`Vector`

      wzyx  Type: 

`Vector`

      wzyy  Type: 

`Vector`

      wzyz  Type: 

`Vector`

      wzz  Type: 

`Vector`

      wzzw  Type: 

`Vector`

      wzzx  Type: 

`Vector`

      wzzy  Type: 

`Vector`

      wzzz  Type: 

`Vector`

      x 

Vector X axis.

  Type: 

float

      xw  Type: 

`Vector`

      xww  Type: 

`Vector`

      xwww  Type: 

`Vector`

      xwwx  Type: 

`Vector`

      xwwy  Type: 

`Vector`

      xwwz  Type: 

`Vector`

      xwx  Type: 

`Vector`

      xwxw  Type: 

`Vector`

      xwxx  Type: 

`Vector`

      xwxy  Type: 

`Vector`

      xwxz  Type: 

`Vector`

      xwy  Type: 

`Vector`

      xwyw  Type: 

`Vector`

      xwyx  Type: 

`Vector`

      xwyy  Type: 

`Vector`

      xwyz  Type: 

`Vector`

      xwz  Type: 

`Vector`

      xwzw  Type: 

`Vector`

      xwzx  Type: 

`Vector`

      xwzy  Type: 

`Vector`

      xwzz  Type: 

`Vector`

      xx  Type: 

`Vector`

      xxw  Type: 

`Vector`

      xxww  Type: 

`Vector`

      xxwx  Type: 

`Vector`

      xxwy  Type: 

`Vector`

      xxwz  Type: 

`Vector`

      xxx  Type: 

`Vector`

      xxxw  Type: 

`Vector`

      xxxx  Type: 

`Vector`

      xxxy  Type: 

`Vector`

      xxxz  Type: 

`Vector`

      xxy  Type: 

`Vector`

      xxyw  Type: 

`Vector`

      xxyx  Type: 

`Vector`

      xxyy  Type: 

`Vector`

      xxyz  Type: 

`Vector`

      xxz  Type: 

`Vector`

      xxzw  Type: 

`Vector`

      xxzx  Type: 

`Vector`

      xxzy  Type: 

`Vector`

      xxzz  Type: 

`Vector`

      xy  Type: 

`Vector`

      xyw  Type: 

`Vector`

      xyww  Type: 

`Vector`

      xywx  Type: 

`Vector`

      xywy  Type: 

`Vector`

      xywz  Type: 

`Vector`

      xyx  Type: 

`Vector`

      xyxw  Type: 

`Vector`

      xyxx  Type: 

`Vector`

      xyxy  Type: 

`Vector`

      xyxz  Type: 

`Vector`

      xyy  Type: 

`Vector`

      xyyw  Type: 

`Vector`

      xyyx  Type: 

`Vector`

      xyyy  Type: 

`Vector`

      xyyz  Type: 

`Vector`

      xyz  Type: 

`Vector`

      xyzw  Type: 

`Vector`

      xyzx  Type: 

`Vector`

      xyzy  Type: 

`Vector`

      xyzz  Type: 

`Vector`

      xz  Type: 

`Vector`

      xzw  Type: 

`Vector`

      xzww  Type: 

`Vector`

      xzwx  Type: 

`Vector`

      xzwy  Type: 

`Vector`

      xzwz  Type: 

`Vector`

      xzx  Type: 

`Vector`

      xzxw  Type: 

`Vector`

      xzxx  Type: 

`Vector`

      xzxy  Type: 

`Vector`

      xzxz  Type: 

`Vector`

      xzy  Type: 

`Vector`

      xzyw  Type: 

`Vector`

      xzyx  Type: 

`Vector`

      xzyy  Type: 

`Vector`

      xzyz  Type: 

`Vector`

      xzz  Type: 

`Vector`

      xzzw  Type: 

`Vector`

      xzzx  Type: 

`Vector`

      xzzy  Type: 

`Vector`

      xzzz  Type: 

`Vector`

      y 

Vector Y axis.

  Type: 

float

      yw  Type: 

`Vector`

      yww  Type: 

`Vector`

      ywww  Type: 

`Vector`

      ywwx  Type: 

`Vector`

      ywwy  Type: 

`Vector`

      ywwz  Type: 

`Vector`

      ywx  Type: 

`Vector`

      ywxw  Type: 

`Vector`

      ywxx  Type: 

`Vector`

      ywxy  Type: 

`Vector`

      ywxz  Type: 

`Vector`

      ywy  Type: 

`Vector`

      ywyw  Type: 

`Vector`

      ywyx  Type: 

`Vector`

      ywyy  Type: 

`Vector`

      ywyz  Type: 

`Vector`

      ywz  Type: 

`Vector`

      ywzw  Type: 

`Vector`

      ywzx  Type: 

`Vector`

      ywzy  Type: 

`Vector`

      ywzz  Type: 

`Vector`

      yx  Type: 

`Vector`

      yxw  Type: 

`Vector`

      yxww  Type: 

`Vector`

      yxwx  Type: 

`Vector`

      yxwy  Type: 

`Vector`

      yxwz  Type: 

`Vector`

      yxx  Type: 

`Vector`

      yxxw  Type: 

`Vector`

      yxxx  Type: 

`Vector`

      yxxy  Type: 

`Vector`

      yxxz  Type: 

`Vector`

      yxy  Type: 

`Vector`

      yxyw  Type: 

`Vector`

      yxyx  Type: 

`Vector`

      yxyy  Type: 

`Vector`

      yxyz  Type: 

`Vector`

      yxz  Type: 

`Vector`

      yxzw  Type: 

`Vector`

      yxzx  Type: 

`Vector`

      yxzy  Type: 

`Vector`

      yxzz  Type: 

`Vector`

      yy  Type: 

`Vector`

      yyw  Type: 

`Vector`

      yyww  Type: 

`Vector`

      yywx  Type: 

`Vector`

      yywy  Type: 

`Vector`

      yywz  Type: 

`Vector`

      yyx  Type: 

`Vector`

      yyxw  Type: 

`Vector`

      yyxx  Type: 

`Vector`

      yyxy  Type: 

`Vector`

      yyxz  Type: 

`Vector`

      yyy  Type: 

`Vector`

      yyyw  Type: 

`Vector`

      yyyx  Type: 

`Vector`

      yyyy  Type: 

`Vector`

      yyyz  Type: 

`Vector`

      yyz  Type: 

`Vector`

      yyzw  Type: 

`Vector`

      yyzx  Type: 

`Vector`

      yyzy  Type: 

`Vector`

      yyzz  Type: 

`Vector`

      yz  Type: 

`Vector`

      yzw  Type: 

`Vector`

      yzww  Type: 

`Vector`

      yzwx  Type: 

`Vector`

      yzwy  Type: 

`Vector`

      yzwz  Type: 

`Vector`

      yzx  Type: 

`Vector`

      yzxw  Type: 

`Vector`

      yzxx  Type: 

`Vector`

      yzxy  Type: 

`Vector`

      yzxz  Type: 

`Vector`

      yzy  Type: 

`Vector`

      yzyw  Type: 

`Vector`

      yzyx  Type: 

`Vector`

      yzyy  Type: 

`Vector`

      yzyz  Type: 

`Vector`

      yzz  Type: 

`Vector`

      yzzw  Type: 

`Vector`

      yzzx  Type: 

`Vector`

      yzzy  Type: 

`Vector`

      yzzz  Type: 

`Vector`

      z 

Vector Z axis (3D Vectors only).

  Type: 

float

      zw  Type: 

`Vector`

      zww  Type: 

`Vector`

      zwww  Type: 

`Vector`

      zwwx  Type: 

`Vector`

      zwwy  Type: 

`Vector`

      zwwz  Type: 

`Vector`

      zwx  Type: 

`Vector`

      zwxw  Type: 

`Vector`

      zwxx  Type: 

`Vector`

      zwxy  Type: 

`Vector`

      zwxz  Type: 

`Vector`

      zwy  Type: 

`Vector`

      zwyw  Type: 

`Vector`

      zwyx  Type: 

`Vector`

      zwyy  Type: 

`Vector`

      zwyz  Type: 

`Vector`

      zwz  Type: 

`Vector`

      zwzw  Type: 

`Vector`

      zwzx  Type: 

`Vector`

      zwzy  Type: 

`Vector`

      zwzz  Type: 

`Vector`

      zx  Type: 

`Vector`

      zxw  Type: 

`Vector`

      zxww  Type: 

`Vector`

      zxwx  Type: 

`Vector`

      zxwy  Type: 

`Vector`

      zxwz  Type: 

`Vector`

      zxx  Type: 

`Vector`

      zxxw  Type: 

`Vector`

      zxxx  Type: 

`Vector`

      zxxy  Type: 

`Vector`

      zxxz  Type: 

`Vector`

      zxy  Type: 

`Vector`

      zxyw  Type: 

`Vector`

      zxyx  Type: 

`Vector`

      zxyy  Type: 

`Vector`

      zxyz  Type: 

`Vector`

      zxz  Type: 

`Vector`

      zxzw  Type: 

`Vector`

      zxzx  Type: 

`Vector`

      zxzy  Type: 

`Vector`

      zxzz  Type: 

`Vector`

      zy  Type: 

`Vector`

      zyw  Type: 

`Vector`

      zyww  Type: 

`Vector`

      zywx  Type: 

`Vector`

      zywy  Type: 

`Vector`

      zywz  Type: 

`Vector`

      zyx  Type: 

`Vector`

      zyxw  Type: 

`Vector`

      zyxx  Type: 

`Vector`

      zyxy  Type: 

`Vector`

      zyxz  Type: 

`Vector`

      zyy  Type: 

`Vector`

      zyyw  Type: 

`Vector`

      zyyx  Type: 

`Vector`

      zyyy  Type: 

`Vector`

      zyyz  Type: 

`Vector`

      zyz  Type: 

`Vector`

      zyzw  Type: 

`Vector`

      zyzx  Type: 

`Vector`

      zyzy  Type: 

`Vector`

      zyzz  Type: 

`Vector`

      zz  Type: 

`Vector`

      zzw  Type: 

`Vector`

      zzww  Type: 

`Vector`

      zzwx  Type: 

`Vector`

      zzwy  Type: 

`Vector`

      zzwz  Type: 

`Vector`

      zzx  Type: 

`Vector`

      zzxw  Type: 

`Vector`

      zzxx  Type: 

`Vector`

      zzxy  Type: 

`Vector`

      zzxz  Type: 

`Vector`

      zzy  Type: 

`Vector`

      zzyw  Type: 

`Vector`

      zzyx  Type: 

`Vector`

      zzyy  Type: 

`Vector`

      zzyz  Type: 

`Vector`

      zzz  Type: 

`Vector`

      zzzw  Type: 

`Vector`

      zzzx  Type: 

`Vector`

      zzzy  Type: 

`Vector`

      zzzz  Type: 

`Vector`

    Special Methods  __add__(other)  Parameters: 

other (Self) – The other operand.

  Return type: 

`Vector`

      __eq__(other)  Parameters: 

other (object) – The other operand.

  Return type: 

bool

      __ge__(other)  Parameters: 

other (Self) – The other operand.

  Return type: 

bool

      __getitem__(key)  Parameters: 

key (int) – Index or key.

  Return type: 

float

      __gt__(other)  Parameters: 

other (Self) – The other operand.

  Return type: 

bool

      __hash__()  Return type: 

int

      __iadd__(other)  Parameters: 

other (Self) – The other operand.

  Return type: 

`Vector`

      __imul__(other)  Parameters: 

other (`Vector`) – The other operand.

  Return type: 

`Vector`

      __imul__(other)  Parameters: 

other (float) – The other operand.

  Return type: 

`Vector`

      __isub__(other)  Parameters: 

other (Self) – The other operand.

  Return type: 

`Vector`

      __itruediv__(other)  Parameters: 

other (float) – Scalar divisor.

  Return type: 

`Vector`

      __le__(other)  Parameters: 

other (Self) – The other operand.

  Return type: 

bool

      __len__()  Return type: 

int

      __lt__(other)  Parameters: 

other (Self) – The other operand.

  Return type: 

bool

      __matmul__(other)  Parameters: 

other (`Vector`) – The other operand.

  Return type: 

float

      __matmul__(other)  Parameters: 

other (`Matrix`) – The other operand.

  Return type: 

`Vector`

      __mul__(other)  Parameters: 

other (`Vector`) – The other operand.

  Return type: 

`Vector`

      __mul__(other)  Parameters: 

other (float) – The other operand.

  Return type: 

`Vector`

      __ne__(other)  Parameters: 

other (object) – The other operand.

  Return type: 

bool

      __neg__()  Return type: 

`Vector`

      __pos__()  Return type: 

`Vector`

      __repr__()  Return type: 

str

      __rmul__(other)  Parameters: 

other (float) – Scalar.

  Return type: 

`Vector`

      __setitem__(key, value)  Parameters:  
- key (int) – Index or key. 
- value (object) – Value to assign.       __str__()  Return type: 

str

      __sub__(other)  Parameters: 

other (Self) – The other operand.

  Return type: 

`Vector`

      __truediv__(other)  Parameters: 

other (float) – Scalar divisor.

  Return type: 

`Vector`
