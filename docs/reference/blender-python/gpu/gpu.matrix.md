# gpu.matrix

# GPU Matrix Utilities (gpu.matrix)

 

This module provides access to the matrix stack.

   gpu.matrix.get_model_view_matrix() 

Return a copy of the model-view matrix.

  Returns: 

A 4x4 view matrix.

  Return type: 

[`mathutils.Matrix`](mathutils.html#mathutils.Matrix)

      gpu.matrix.get_normal_matrix() 

Return a copy of the normal matrix.

  Returns: 

A 3x3 normal matrix.

  Return type: 

[`mathutils.Matrix`](mathutils.html#mathutils.Matrix)

      gpu.matrix.get_projection_matrix() 

Return a copy of the projection matrix.

  Returns: 

A 4x4 projection matrix.

  Return type: 

[`mathutils.Matrix`](mathutils.html#mathutils.Matrix)

      gpu.matrix.load_identity() 

Load an identity matrix into the stack.

    gpu.matrix.load_matrix(matrix) 

Load a matrix into the stack.

  Parameters: 

matrix ([`mathutils.Matrix`](mathutils.html#mathutils.Matrix)) – A 4x4 matrix.

      gpu.matrix.load_projection_matrix(matrix) 

Load a projection matrix into the stack.

  Parameters: 

matrix ([`mathutils.Matrix`](mathutils.html#mathutils.Matrix)) – A 4x4 matrix.

      gpu.matrix.multiply_matrix(matrix) 

Multiply the current stack matrix.

  Parameters: 

matrix ([`mathutils.Matrix`](mathutils.html#mathutils.Matrix)) – A 4x4 matrix.

      gpu.matrix.pop() 

Remove the last model-view matrix from the stack.

    gpu.matrix.pop_projection() 

Remove the last projection matrix from the stack.

    gpu.matrix.push() 

Add to the model-view matrix stack.

    gpu.matrix.push_pop() 

Context manager to ensure balanced push/pop calls, even in the case of an error.

  Returns: 

The context manager.

  Return type: 

[`gpu.types.MatrixStackContext`](gpu.types.html#gpu.types.MatrixStackContext)

      gpu.matrix.push_pop_projection() 

Context manager to ensure balanced push/pop calls, even in the case of an error.

  Returns: 

The context manager.

  Return type: 

[`gpu.types.MatrixStackContext`](gpu.types.html#gpu.types.MatrixStackContext)

      gpu.matrix.push_projection() 

Add to the projection matrix stack.

    gpu.matrix.reset() 

Empty stack and set to identity.

    gpu.matrix.scale(scale) 

Scale the current stack matrix.

  Parameters: 

scale (Sequence[float]) – Scale the current stack matrix with 2 or 3 floats.

      gpu.matrix.scale_uniform(scale) 

Scale the current stack matrix uniformly.

  Parameters: 

scale (float) – Uniform scale factor.

      gpu.matrix.translate(offset) 

Translate the current stack matrix.

  Parameters: 

offset (Sequence[float]) – Translate the current stack matrix with 2 or 3 floats.
