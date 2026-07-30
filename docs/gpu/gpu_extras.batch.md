# gpu_extras.batch

# gpu_extras submodule (gpu_extras.batch)

   gpu_extras.batch.batch_for_shader(shader, type, content, *, indices=None) 

Return a batch already configured and compatible with the shader.

  Parameters:  
- shader ([`gpu.types.GPUShader`](gpu.types.html#gpu.types.GPUShader)) – shader for which a compatible format will be computed. 
- type (Literal['POINTS', 'LINES', 'TRIS', 'LINE_STRIP', 'TRI_STRIP', 'LINES_ADJ', 'TRIS_ADJ', 'LINE_STRIP_ADJ']) – The primitive type of batch geometry. 
- content (dict[str, Buffer | Sequence[float] | Sequence[int] | Sequence[Sequence[float]] | Sequence[Sequence[int]]]) – Maps the name of the shader attribute with the data to fill the vertex buffer. For the dictionary values see documentation for [`gpu.types.GPUVertBuf.attr_fill`](gpu.types.html#gpu.types.GPUVertBuf.attr_fill) data argument. 
- indices (Sequence[int] | Sequence[Sequence[int]] | None) – Optional index buffer contents. When omitted, the batch draws all vertices in order.   Returns: 

compatible batch

  Return type: 

[`gpu.types.GPUBatch`](gpu.types.html#gpu.types.GPUBatch)
