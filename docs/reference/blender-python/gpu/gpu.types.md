# gpu.types

# GPU Types (gpu.types)

   class gpu.types.Buffer 

For Python access to GPU functions requiring a pointer.

   __init__(format, dimensions, data)  Parameters:  
- format (Literal['FLOAT', 'INT', 'UINT', 'UBYTE', 'UINT_24_8', '10_11_11_REV']) – Format type to interpret the buffer. `UINT_24_8` is deprecated, use `FLOAT` instead. 
- dimensions (int | Sequence[int]) – Array describing the dimensions. 
- data (Buffer | Sequence[float] | Sequence[int]) – Optional data array.       to_list() 

Return the buffer as a list.

  Returns: 

The buffer as a list.

  Return type: 

list

      dimensions 

The size of the buffer for each dimension.

 

Setting the dimensions is supported when the total number of elements is unchanged.

  Type: 

list[int]

    Special Methods  __getitem__(key)  Parameters: 

key (int) – Index or key.

  Return type: 

float

      __len__()  Return type: 

int

      __repr__()  Return type: 

str

      __setitem__(key, value)  Parameters:  
- key (int) – Index or key. 
- value (object) – Value to assign.        class gpu.types.GPUBatch 

Reusable container for drawable geometry.

   __init__(type, buf, elem=None)  Parameters:  
- type (Literal['POINTS', 'LINES', 'TRIS', 'LINE_STRIP', 'LINE_LOOP', 'TRI_STRIP', 'TRI_FAN', 'LINES_ADJ', 'TRIS_ADJ', 'LINE_STRIP_ADJ']) – The primitive type of geometry to be drawn. 
- buf (`gpu.types.GPUVertBuf`) – Vertex buffer containing all or some of the attributes required for drawing. 
- elem (`gpu.types.GPUIndexBuf` | None) – An optional index buffer.       draw(shader=None) 

Run the drawing shader with the parameters assigned to the batch.

  Parameters: 

shader (`gpu.types.GPUShader` | None) – Shader that performs the drawing operations. If `None` is passed, the last shader set to this batch will run.

      draw_instanced(program, *, instance_start=0, instance_count=0) 

Draw multiple instances of the drawing program with the parameters assigned to the batch. In the vertex shader, `gl_InstanceID` will contain the instance number being drawn.

  Parameters:  
- program (`gpu.types.GPUShader`) – Program that performs the drawing operations. 
- instance_start (int) – Number of the first instance to draw. 
- instance_count (int) – Number of instances to draw. When not provided or set to 0 the number of instances will be determined by the number of rows in the first vertex buffer.       draw_range(program, *, elem_start=0, elem_count=0) 

Run the drawing program with the parameters assigned to the batch. Only draw the `elem_count` elements of the index buffer starting at `elem_start`.

  Parameters:  
- program (`gpu.types.GPUShader`) – Program that performs the drawing operations. 
- elem_start (int) – First index to draw. When not provided or set to 0 drawing will start from the first element of the index buffer. 
- elem_count (int) – Number of elements of the index buffer to draw. When not provided or set to 0 all elements from `elem_start` to the end of the index buffer will be drawn.       program_set(program) 

Assign a shader to this batch that will be used for drawing when not overwritten later. Note: This method has to be called in the draw context that the batch will be drawn in. This function does not need to be called when you always set the shader when calling `gpu.types.GPUBatch.draw()`.

  Parameters: 

program (`gpu.types.GPUShader`) – The program/shader the batch will use in future draw calls.

      vertbuf_add(buf) 

Add another vertex buffer to the Batch. It is not possible to add more vertices to the batch using this method. Instead it can be used to add more attributes to the existing vertices. A good use case would be when you have a separate vertex buffer for vertex positions and vertex normals. Current a batch can have at most GPU_BATCH_VBO_MAX_LEN vertex buffers.

  Parameters: 

buf (`gpu.types.GPUVertBuf`) – The vertex buffer that will be added to the batch.

       class gpu.types.GPUDevice 

Represents a GPU device.

  Variables:  
- index – Device index. 
- identifier – Device identifier. 
- name – Device name.      identifier 

Device identifier.

  Type: 

str

      index 

Device index.

  Type: 

int

      name 

Device name.

  Type: 

str

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

       class gpu.types.GPUFrameBuffer 

This object gives access to framebuffer functionalities. When a ‘layer’ is specified in a argument, a single layer of a 3D or array texture is attached to the frame-buffer. For cube map textures, layer is translated into a cube map face.

   __init__(*, depth_slot=None, color_slots=None)  Parameters:  
- depth_slot (`gpu.types.GPUTexture` | dict[str, int | `gpu.types.GPUTexture`] | None) – GPUTexture to attach or a `dict` containing keywords: ‘texture’, ‘layer’ and ‘mip’. 
- color_slots (`gpu.types.GPUTexture` | dict[str, int | `gpu.types.GPUTexture`] | Sequence[`gpu.types.GPUTexture` | dict[str, int | `gpu.types.GPUTexture`]] | None) – Tuple where each item can be a GPUTexture or a `dict` containing keywords: ‘texture’, ‘layer’ and ‘mip’.       bind() 

Context manager to ensure balanced bind calls, even in the case of an error.

    clear(*, color=None, depth=None, stencil=None) 

Fill color, depth and stencil textures with specific value. Common values: color=(0.0, 0.0, 0.0, 1.0), depth=1.0, stencil=0.

  Parameters:  
- color (Sequence[float] | None) – Sequence of 3 or 4 floats representing `(r, g, b, a)`. 
- depth (float | None) – depth value. 
- stencil (int | None) – stencil value.       read_color(x, y, xsize, ysize, channels, slot, format, *, data=None) 

Read a block of pixels from the frame buffer.

  Parameters:  
- x (int) – Lower left corner x of a rectangular block of pixels. 
- y (int) – Lower left corner y of a rectangular block of pixels. 
- xsize (int) – Width of the pixel rectangle. 
- ysize (int) – Height of the pixel rectangle. 
- channels (int) – Number of components to read. 
- slot (int) – The framebuffer slot to read data from. 
- format (Literal['FLOAT', 'INT', 'UINT', 'UBYTE', 'UINT_24_8', '10_11_11_REV']) – The format that describes the content of a single channel. `UINT_24_8` is deprecated, use `FLOAT` instead. 
- data (`gpu.types.Buffer` | None) – Optional Buffer object to fill with the pixels values.   Returns: 

The Buffer with the read pixels.

  Return type: 

`gpu.types.Buffer`

      read_depth(x, y, xsize, ysize, *, data=None) 

Read a pixel depth block from the frame buffer.

  Parameters:  
- x (int) – Lower left corner x of a rectangular block of pixels. 
- y (int) – Lower left corner y of a rectangular block of pixels. 
- xsize (int) – Width of the pixel rectangle. 
- ysize (int) – Height of the pixel rectangle. 
- data (`gpu.types.Buffer` | None) – Optional Buffer object to fill with the pixels values.   Returns: 

The Buffer with the read pixels.

  Return type: 

`gpu.types.Buffer`

      viewport_get() 

Returns position and dimension to current viewport.

  Returns: 

The viewport as `(x, y, width, height)`.

  Return type: 

tuple[int, int, int, int]

      viewport_set(x, y, xsize, ysize) 

Set the viewport for this framebuffer object. Note: The viewport state is not saved upon framebuffer rebind.

  Parameters:  
- x (int) – Lower left corner x of the viewport rectangle, in pixels. 
- y (int) – Lower left corner y of the viewport rectangle, in pixels. 
- xsize (int) – Width of the viewport. 
- ysize (int) – Height of the viewport.       is_bound 

Checks if this is the active frame-buffer in the context.

  Type: 

bool

       class gpu.types.GPUIndexBuf 

Contains an index buffer.

   __init__(type, seq)  Parameters:  
- type (Literal['POINTS', 'LINES', 'TRIS', 'LINES_ADJ', 'TRIS_ADJ']) – The primitive type this index buffer is composed of. 
- seq (Buffer | Sequence[int] | Sequence[Sequence[int]]) – Indices this index buffer will contain. Whether a 1D or 2D sequence is required depends on the type. Optionally the sequence can support the buffer protocol.        class gpu.types.GPUOffScreen 

This object gives access to off screen buffers.

   __init__(width, height, *, format='RGBA8')  Parameters:  
- width (int) – Horizontal dimension of the buffer. 
- height (int) – Vertical dimension of the buffer. 
- format (Literal['RGBA8', 'RGBA16', 'RGBA16F', 'RGBA32F']) – Internal data format inside GPU memory for color attachment texture.       bind() 

Context manager to ensure balanced bind calls, even in the case of an error.

  Returns: 

A context manager for the off-screen binding.

  Return type: 

`gpu.types.OffScreenStackContext`

      draw_view3d(scene, view_layer, view3d, region, view_matrix, projection_matrix, *, do_color_management=False, draw_background=True) 

Draw the 3d viewport in the offscreen object.

  Parameters:  
- scene ([`bpy.types.Scene`](bpy.types.Scene.html#bpy.types.Scene)) – Scene to draw. 
- view_layer ([`bpy.types.ViewLayer`](bpy.types.ViewLayer.html#bpy.types.ViewLayer)) – View layer to draw. 
- view3d ([`bpy.types.SpaceView3D`](bpy.types.SpaceView3D.html#bpy.types.SpaceView3D)) – 3D View to get the drawing settings from. 
- region ([`bpy.types.Region`](bpy.types.Region.html#bpy.types.Region)) – Region of the 3D View (required as temporary draw target). 
- view_matrix ([`mathutils.Matrix`](mathutils.html#mathutils.Matrix)) – View Matrix (e.g. `camera.matrix_world.inverted()`). 
- projection_matrix ([`mathutils.Matrix`](mathutils.html#mathutils.Matrix)) – Projection Matrix (e.g. `camera.calc_matrix_camera(...)`). 
- do_color_management (bool) – Color manage the output. 
- draw_background (bool) – Draw background.       free() 

Free the offscreen object. The framebuffer, texture and render objects will no longer be accessible.

    unbind(*, restore=True) 

Unbind the offscreen object.

  Parameters: 

restore (bool) – Restore the OpenGL state, can only be used when the state has been saved before.

      height 

Height of the texture.

  Type: 

int

      texture_color 

The color texture attached.

  Type: 

`gpu.types.GPUTexture`

      width 

Width of the texture.

  Type: 

int

       class gpu.types.GPUShader   attr_from_name(name) 

Get attribute location by name.

  Parameters: 

name (str) – The name of the attribute variable whose location is to be queried.

  Returns: 

The location of an attribute variable.

  Return type: 

int

      attrs_info_get() 

Information about the attributes used in the Shader.

  Returns: 

tuples containing information about the attributes in order (name, type)

  Return type: 

tuple[tuple[str, str | None], …]

      bind() 

Bind the shader object. Required to be able to change uniforms of this shader.

    format_calc() 

Build a new format based on the attributes of the shader.

  Returns: 

vertex attribute format for the shader

  Return type: 

`gpu.types.GPUVertFormat`

      image(name, texture) 

Specify the value of an image variable for the current GPUShader.

  Parameters:  
- name (str) – Name of the image variable to which the texture is to be bound. 
- texture (`gpu.types.GPUTexture`) – Texture to attach.       uniform_block(name, ubo) 

Specify the value of a uniform buffer object variable for the current GPUShader.

  Parameters:  
- name (str) – Name of the uniform variable whose UBO is to be specified. 
- ubo (`gpu.types.GPUUniformBuf`) – Uniform Buffer to attach.       uniform_block_from_name(name) 

Get uniform block location by name.

  Parameters: 

name (str) – Name of the uniform block variable whose location is to be queried.

  Returns: 

The location of the uniform block variable.

  Return type: 

int

      uniform_bool(name, value) 

Specify the value of a uniform variable for the current program object.

  Parameters:  
- name (str) – Name of the uniform variable whose value is to be changed. 
- value (bool | Sequence[bool]) – Value that will be used to update the specified uniform variable.       uniform_float(name, value) 

Specify the value of a uniform variable for the current program object.

  Parameters:  
- name (str) – Name of the uniform variable whose value is to be changed. 
- value (float | Sequence[float]) – Value that will be used to update the specified uniform variable.       uniform_from_name(name) 

Get uniform location by name.

  Parameters: 

name (str) – Name of the uniform variable whose location is to be queried.

  Returns: 

Location of the uniform variable.

  Return type: 

int

      uniform_int(name, seq) 

Specify the value of a uniform variable for the current program object.

  Parameters:  
- name (str) – Name of the uniform variable whose value is to be changed. 
- seq (int | Sequence[int]) – Value that will be used to update the specified uniform variable.       uniform_sampler(name, texture) 

Specify the value of a texture uniform variable for the current GPUShader.

  Parameters:  
- name (str) – Name of the uniform variable whose texture is to be specified. 
- texture (`gpu.types.GPUTexture`) – Texture to attach.       uniform_vector_float(location, buffer, length, count) 

Set the buffer to fill the uniform.

  Parameters:  
- location (int) – Location of the uniform variable to be modified. 
- buffer (Sequence[float]) – The data that should be set. Can support the buffer protocol. 
- length (int) – 

Size of the uniform data type:

  
- 1: float 
- 2: vec2 or float[2] 
- 3: vec3 or float[3] 
- 4: vec4 or float[4] 
- 9: mat3 
- 16: mat4 
- count (int) – Specifies the number of elements, vector or matrices that are to be modified.       uniform_vector_int(location, buffer, length, count) 

Set the buffer to fill the uniform.

  Parameters:  
- location (int) – Location of the uniform variable to be modified. 
- buffer (Buffer) – Buffer object with format matching the uniform. 
- length (int) – Size of the uniform data type. 
- count (int) – Specifies the number of elements that are to be modified.       name 

The name of the shader object for debugging purposes (read-only).

  Type: 

str

      program 

The name of the program object for use by the OpenGL API (read-only). This is deprecated and will always return -1.

  Type: 

int

       class gpu.types.GPUShaderCreateInfo 

Stores and describes types and variables that are used in shader sources.

   compute_source(source) 

compute shader source code written in GLSL.

 

Example:

 

```python
"""void main() {
   int2 index = int2(gl_GlobalInvocationID.xy);
   vec4 color = vec4(0.0, 0.0, 0.0, 1.0);
   imageStore(img_output, index, color);
}"""
```

   Parameters: 

source (str) – The compute shader source code.

    

See also

 

[GLSL Cross Compilation](https://developer.blender.org/docs/features/gpu/glsl_cross_compilation/)

     define(name, value) 

Add a preprocessing define directive. In GLSL it would be something like:

 

```python
#define name value
```

   Parameters:  
- name (str) – Token name. 
- value (str) – Text that replaces token occurrences.       depth_write(value) 

Specify a depth write behavior when modifying gl_FragDepth.

 

There is a common optimization for GPUs that relies on an early depth test to be run before the fragment shader so that the shader evaluation can be skipped if the fragment ends up being discarded because it is occluded.

 

This optimization does not affect the final rendering, and is typically possible when the fragment does not change the depth programmatically. There is, however, a class of operations on the depth in the shader which could still be performed while allowing the early depth test to operate.

 

This function alters the behavior of the optimization to allow those operations to be performed.

  Parameters: 

value (Literal['UNCHANGED', 'ANY', 'GREATER', 'LESS']) – Depth write value. :UNCHANGED: disables depth write in a fragment shader and execution of the fragments can be optimized away. :ANY: enables depth write in a fragment shader for any fragments :GREATER: enables depth write in a fragment shader for depth values that are greater than the depth value in the output buffer. :LESS: enables depth write in a fragment shader for depth values that are less than the depth value in the output buffer.

      fragment_out(slot, type, name, *, blend='NONE') 

Specify a fragment output corresponding to a framebuffer target slot.

  Parameters:  
- slot (int) – The attribute index. 
- type (Literal['FLOAT', 'VEC2', 'VEC3', 'VEC4', 'MAT3', 'MAT4', 'UINT', 'UVEC2', 'UVEC3', 'UVEC4', 'INT', 'IVEC2', 'IVEC3', 'IVEC4', 'BOOL']) – The data type of the output. 
- name (str) – Name of the attribute. 
- blend (Literal['NONE', 'SRC_0', 'SRC_1']) – Dual Source Blending Index.       fragment_source(source) 

Fragment shader source code written in GLSL.

 

Example:

 

```python
"void main() {fragColor = vec4(0.0, 0.0, 0.0, 1.0);}"
```

   Parameters: 

source (str) – The fragment shader source code.

    

See also

 

[GLSL Cross Compilation](https://developer.blender.org/docs/features/gpu/glsl_cross_compilation/)

     image(slot, format, type, name, *, qualifiers={'NO_RESTRICT'}) 

Specify an image resource used for arbitrary load and store operations.

  Parameters:  
- slot (int) – The image resource index. 
- format (Literal['RGBA8UI', 'RGBA8I', 'RGBA8', 'RGBA32UI', 'RGBA32I', 'RGBA32F', 'RGBA16UI', 'RGBA16I', 'RGBA16F', 'RGBA16', 'RG8UI', 'RG8I', 'RG8', 'RG32UI', 'RG32I', 'RG32F', 'RG16UI', 'RG16I', 'RG16F', 'RG16', 'R8UI', 'R8I', 'R8', 'R32UI', 'R32I', 'R32F', 'R16UI', 'R16I', 'R16F', 'R16', 'R11F_G11F_B10F', 'DEPTH32F_STENCIL8', 'DEPTH24_STENCIL8', 'SRGB8_A8', 'RGB16F', 'SRGB8_A8_DXT1', 'SRGB8_A8_DXT3', 'SRGB8_A8_DXT5', 'RGBA8_DXT1', 'RGBA8_DXT3', 'RGBA8_DXT5', 'DEPTH_COMPONENT32F', 'DEPTH_COMPONENT24', 'DEPTH_COMPONENT16']) – The GPUTexture format that is passed to the shader. 
- type (Literal['FLOAT_BUFFER', 'FLOAT_1D', 'FLOAT_1D_ARRAY', 'FLOAT_2D', 'FLOAT_2D_ARRAY', 'FLOAT_3D', 'FLOAT_CUBE', 'FLOAT_CUBE_ARRAY', 'INT_BUFFER', 'INT_1D', 'INT_1D_ARRAY', 'INT_2D', 'INT_2D_ARRAY', 'INT_3D', 'INT_CUBE', 'INT_CUBE_ARRAY', 'UINT_BUFFER', 'UINT_1D', 'UINT_1D_ARRAY', 'UINT_2D', 'UINT_2D_ARRAY', 'UINT_3D', 'UINT_CUBE', 'UINT_CUBE_ARRAY', 'SHADOW_2D', 'SHADOW_2D_ARRAY', 'SHADOW_CUBE', 'SHADOW_CUBE_ARRAY', 'DEPTH_2D', 'DEPTH_2D_ARRAY', 'DEPTH_CUBE', 'DEPTH_CUBE_ARRAY']) – The data type describing how the image is to be read in the shader. 
- name (str) – The image resource name. 
- qualifiers (set[Literal['NO_RESTRICT', 'READ', 'WRITE']]) – Set containing values that describe how the image resource is to be read or written.       local_group_size(x, y=1, z=1) 

Specify the local group size for compute shaders.

  Parameters:  
- x (int) – The local group size in the x dimension. 
- y (int) – The local group size in the y dimension. Optional. Defaults to 1. 
- z (int) – The local group size in the z dimension. Optional. Defaults to 1.       push_constant(type, name, size=0) 

Specify a global access constant.

  Parameters:  
- type (Literal['FLOAT', 'VEC2', 'VEC3', 'VEC4', 'MAT3', 'MAT4', 'UINT', 'UVEC2', 'UVEC3', 'UVEC4', 'INT', 'IVEC2', 'IVEC3', 'IVEC4', 'BOOL']) – The data type of the constant. 
- name (str) – Name of the constant. 
- size (int) – If not zero, indicates that the constant is an array with the specified size.       sampler(slot, type, name) 

Specify an image texture sampler.

  Parameters:  
- slot (int) – The image texture sampler index. 
- type (Literal['FLOAT_BUFFER', 'FLOAT_1D', 'FLOAT_1D_ARRAY', 'FLOAT_2D', 'FLOAT_2D_ARRAY', 'FLOAT_3D', 'FLOAT_CUBE', 'FLOAT_CUBE_ARRAY', 'INT_BUFFER', 'INT_1D', 'INT_1D_ARRAY', 'INT_2D', 'INT_2D_ARRAY', 'INT_3D', 'INT_CUBE', 'INT_CUBE_ARRAY', 'UINT_BUFFER', 'UINT_1D', 'UINT_1D_ARRAY', 'UINT_2D', 'UINT_2D_ARRAY', 'UINT_3D', 'UINT_CUBE', 'UINT_CUBE_ARRAY', 'SHADOW_2D', 'SHADOW_2D_ARRAY', 'SHADOW_CUBE', 'SHADOW_CUBE_ARRAY', 'DEPTH_2D', 'DEPTH_2D_ARRAY', 'DEPTH_CUBE', 'DEPTH_CUBE_ARRAY']) – The data type describing the format of each sampler unit. 
- name (str) – The image texture sampler name.       typedef_source(source) 

Source code included before resource declaration. Useful for defining structs used by Uniform Buffers.

 

Example:

 

```python
"struct MyType {int foo; float bar;};"
```

   Parameters: 

source (str) – The source code defining types.

      uniform_buf(slot, type_name, name) 

Specify a uniform variable whose type can be one of those declared in `gpu.types.GPUShaderCreateInfo.typedef_source()`.

  Parameters:  
- slot (int) – The uniform variable index. 
- type_name (str) – Name of the data type. It can be a struct type defined in the source passed through the `gpu.types.GPUShaderCreateInfo.typedef_source()`. 
- name (str) – The uniform variable name.       vertex_in(slot, type, name) 

Add a vertex shader input attribute.

  Parameters:  
- slot (int) – The attribute index. 
- type (Literal['FLOAT', 'VEC2', 'VEC3', 'VEC4', 'MAT3', 'MAT4', 'UINT', 'UVEC2', 'UVEC3', 'UVEC4', 'INT', 'IVEC2', 'IVEC3', 'IVEC4', 'BOOL']) – The data type of the attribute. 
- name (str) – name of the attribute.       vertex_out(interface) 

Add a vertex shader output interface block.

  Parameters: 

interface (`gpu.types.GPUStageInterfaceInfo`) – Object describing the block.

      vertex_source(source) 

Vertex shader source code written in GLSL.

 

Example:

 

```python
"void main() {gl_Position = vec4(pos, 1.0);}"
```

   Parameters: 

source (str) – The vertex shader source code.

    

See also

 

[GLSL Cross Compilation](https://developer.blender.org/docs/features/gpu/glsl_cross_compilation/)

      class gpu.types.GPUStageInterfaceInfo 

List of varyings between shader stages.

   __init__(name)  Parameters: 

name (str) – Name of the interface block.

      flat(type, name) 

Add an attribute with qualifier of type `flat` to the interface block.

  Parameters:  
- type (Literal['FLOAT', 'VEC2', 'VEC3', 'VEC4', 'MAT3', 'MAT4', 'UINT', 'UVEC2', 'UVEC3', 'UVEC4', 'INT', 'IVEC2', 'IVEC3', 'IVEC4', 'BOOL']) – The data type of the attribute. 
- name (str) – name of the attribute.       no_perspective(type, name) 

Add an attribute with qualifier of type `no_perspective` to the interface block.

  Parameters:  
- type (Literal['FLOAT', 'VEC2', 'VEC3', 'VEC4', 'MAT3', 'MAT4', 'UINT', 'UVEC2', 'UVEC3', 'UVEC4', 'INT', 'IVEC2', 'IVEC3', 'IVEC4', 'BOOL']) – The data type of the attribute. 
- name (str) – name of the attribute.       smooth(type, name) 

Add an attribute with qualifier of type smooth to the interface block.

  Parameters:  
- type (Literal['FLOAT', 'VEC2', 'VEC3', 'VEC4', 'MAT3', 'MAT4', 'UINT', 'UVEC2', 'UVEC3', 'UVEC4', 'INT', 'IVEC2', 'IVEC3', 'IVEC4', 'BOOL']) – The data type of the attribute. 
- name (str) – name of the attribute.       name 

Name of the interface block.

  Type: 

str

       class gpu.types.GPUTexture 

This object gives access to GPU textures.

   __init__(size, *, layers=0, is_cubemap=False, format='RGBA8', data=None)  Parameters:  
- size (int | Sequence[int]) – Dimensions of the texture 1D, 2D, 3D or cubemap. 
- layers (int) – Number of layers in texture array or number of cubemaps in cubemap array 
- is_cubemap (bool) – Indicates the creation of a cubemap texture. 
- format (Literal['RGBA8UI', 'RGBA8I', 'RGBA8', 'RGBA32UI', 'RGBA32I', 'RGBA32F', 'RGBA16UI', 'RGBA16I', 'RGBA16F', 'RGBA16', 'RG8UI', 'RG8I', 'RG8', 'RG32UI', 'RG32I', 'RG32F', 'RG16UI', 'RG16I', 'RG16F', 'RG16', 'R8UI', 'R8I', 'R8', 'R32UI', 'R32I', 'R32F', 'R16UI', 'R16I', 'R16F', 'R16', 'R11F_G11F_B10F', 'DEPTH32F_STENCIL8', 'DEPTH24_STENCIL8', 'SRGB8_A8', 'RGB16F', 'SRGB8_A8_DXT1', 'SRGB8_A8_DXT3', 'SRGB8_A8_DXT5', 'RGBA8_DXT1', 'RGBA8_DXT3', 'RGBA8_DXT5', 'DEPTH_COMPONENT32F', 'DEPTH_COMPONENT24', 'DEPTH_COMPONENT16']) – Internal data format inside GPU memory. `DEPTH24_STENCIL8` is deprecated, use `DEPTH32F_STENCIL8`. `DEPTH_COMPONENT24` is deprecated, use `DEPTH_COMPONENT32F`. 
- data (`gpu.types.Buffer` | None) – Buffer object to fill the texture.       anisotropic_filter(use_anisotropic) 

Set anisotropic filter usage. This only has effect if mipmapping is enabled.

  Parameters: 

use_anisotropic (bool) – If set to true, the texture will use anisotropic filtering.

      clear(format='FLOAT', value=(0.0, 0.0, 0.0, 1.0)) 

Fill texture with specific value.

  Parameters:  
- format (Literal['FLOAT', 'INT', 'UINT', 'UBYTE', 'UINT_24_8', '10_11_11_REV']) – The format that describes the content of a single item. `UINT_24_8` is deprecated, use `FLOAT` instead. 
- value (Sequence[float] | Sequence[int]) – Sequence each representing the value to fill. Sizes 1..4 are supported.       extend_mode(extend_mode='EXTEND', /) 

Set texture sampling method for coordinates outside of the [0..1] uv range along both the x and y axis.

  Parameters: 

extend_mode (Literal['EXTEND', 'REPEAT', 'MIRRORED_REPEAT', 'CLAMP_TO_BORDER']) – the specified extent mode.

      extend_mode_x(extend_mode='EXTEND', /) 

Set texture sampling method for coordinates outside of the [0..1] uv range along the x axis.

  Parameters: 

extend_mode (Literal['EXTEND', 'REPEAT', 'MIRRORED_REPEAT', 'CLAMP_TO_BORDER']) – the specified extent mode.

      extend_mode_y(extend_mode='EXTEND', /) 

Set texture sampling method for coordinates outside of the [0..1] uv range along the y axis.

  Parameters: 

extend_mode (Literal['EXTEND', 'REPEAT', 'MIRRORED_REPEAT', 'CLAMP_TO_BORDER']) – the specified extent mode.

      filter_mode(use_filter) 

Set texture filter usage.

  Parameters: 

use_filter (bool) – If set to true, the texture will use linear interpolation between neighboring texels.

      mipmap_mode(use_mipmap=True, use_filter=True) 

Set texture filter and mip-map usage.

  Parameters:  
- use_mipmap (bool) – If set to true, the texture will use mip-mapping as anti-aliasing method. 
- use_filter (bool) – If set to true, the texture will use linear interpolation between neighboring texels.       read() 

Creates a buffer with the value of all pixels.

  Returns: 

The Buffer with the read pixels.

  Return type: 

`gpu.types.Buffer`

      format 

Format of the texture.

  Type: 

str

      height 

Height of the texture.

  Type: 

int

      width 

Width of the texture.

  Type: 

int

       class gpu.types.GPUUniformBuf 

This object gives access to uniform buffers.

   __init__(data)  Parameters: 

data (Buffer) – Data to fill the buffer.

      update(data) 

Update the data of the uniform buffer object.

  Parameters: 

data (Buffer) – Data to fill the buffer.

       class gpu.types.GPUVertBuf 

Contains a VBO.

   __init__(format, len)  Parameters:  
- format (`gpu.types.GPUVertFormat`) – Vertex format. 
- len (int) – Amount of vertices that will fit into this buffer.       attr_fill(id, data) 

Insert data into the buffer for a single attribute.

  Parameters:  
- id (int | str) – Either the name or the id of the attribute. 
- data (Buffer | Sequence[float] | Sequence[int] | Sequence[Sequence[float]] | Sequence[Sequence[int]]) – Buffer or sequence of data that should be stored in the buffer        class gpu.types.GPUVertFormat 

This object contains information about the structure of a vertex buffer.

   attr_add(id, comp_type, len, fetch_mode) 

Add a new attribute to the format.

  Parameters:  
- id (str) – Name of the attribute. Often `position`, `normal`, … 
- comp_type (Literal['I8', 'U8', 'I16', 'U16', 'I32', 'U32', 'F32', 'I10']) – The data type that will be used to store the value in memory. 
- len (int) – How many individual values the attribute consists of (e.g. 2 for uv coordinates). 
- fetch_mode (Literal['FLOAT', 'INT', 'INT_TO_FLOAT_UNIT']) – How values from memory will be converted when used in the shader. This is mainly useful for memory optimizations when you want to store values with reduced precision. E.g. you can store a float in only 1 byte but it will be converted to a normal 4 byte float when used.        class gpu.types.MatrixStackContext 

Context manager for matrix stack push/pop.

 Special Methods  __enter__()  Return type: 

`MatrixStackContext`

      __exit__(exc_type, exc_value, traceback)  Parameters:  
- exc_type (type | None) – Exception type, or `None`. 
- exc_value (BaseException | None) – Exception instance, or `None`. 
- traceback (BaseException | None) – Traceback object, or `None`.   Return type: 

bool

       class gpu.types.OffScreenStackContext 

Context manager for off-screen framebuffer binding.

 Special Methods  __enter__()  Return type: 

`OffScreenStackContext`

      __exit__(exc_type, exc_value, traceback)  Parameters:  
- exc_type (type | None) – Exception type, or `None`. 
- exc_value (BaseException | None) – Exception instance, or `None`. 
- traceback (BaseException | None) – Traceback object, or `None`.   Return type: 

bool
