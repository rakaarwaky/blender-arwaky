# imbuf

# Image Buffer (imbuf)

 

This module provides access to Blender’s image manipulation API.

 

It provides access to image buffers outside of Blender’s [`bpy.types.Image`](bpy.types.Image.html#bpy.types.Image) data-block context.

  

Submodules

  
- [Image Buffer Types (imbuf.types)](imbuf.types.html)     imbuf.file_type_from_buffer(buffer) 

Detect the image file type from a buffer.

  Parameters: 

buffer (collections.abc.Buffer) – A buffer containing image data.

  Returns: 

The detected file type, or None if unrecognized.

  Return type: 

`ImBufFileType` or None

      imbuf.load(filepath) 

Load an image from a file.

  Parameters: 

filepath (str | bytes) – The filepath of the image.

  Returns: 

The newly loaded image.

  Return type: 

`ImBuf`

      imbuf.load_from_buffer(buffer) 

Load an image from a buffer.

  Parameters: 

buffer (collections.abc.Buffer) – A buffer containing the image data.

  Returns: 

The newly loaded image.

  Return type: 

`ImBuf`

      imbuf.new(size, *, planes=32, buffer_type='BYTE') 

Create a new image.

  Parameters:  
- size (tuple[int, int]) – The size of the image in pixels. 
- planes (Literal[8, 16, 24, 32]) – Number of bits per pixel. 
- buffer_type (Literal['BYTE', 'FLOAT']) – The buffer type.   Returns: 

The newly created image.

  Return type: 

`ImBuf`

      imbuf.write(image, *, filepath=None) 

Write an image.

  Parameters:  
- image (`ImBuf`) – The image to write. 
- filepath (str | bytes | None) – Optional filepath of the image (fallback to the image’s file path).       imbuf.write_to_buffer(image, file) 

Write an image to a file-like object.

  Parameters:  
- image (`ImBuf`) – The image to write. 
- file (`BinaryIO`) – A writable file-like object (e.g. `io.BytesIO`).
