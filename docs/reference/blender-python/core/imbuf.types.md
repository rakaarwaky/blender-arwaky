# imbuf.types

# Image Buffer Types (imbuf.types)

 

This module provides access to image buffer types.

  

Note

 

Image buffer is also the structure used by [`bpy.types.Image`](bpy.types.Image.html#bpy.types.Image) ID type to store and manipulate image data at runtime.

    class imbuf.types.ImBuf   convert_buffer_type(buffer_type) 

Convert the image’s pixel buffer to the given type. When the image is already of the given type this is a no-op. The previous buffer is freed.

  Parameters: 

buffer_type (Literal['BYTE', 'FLOAT']) – The buffer type.

      copy() 

Return a copy of the image.

  Returns: 

A copy of the image.

  Return type: 

`ImBuf`

      crop(min, max) 

Crop the image in-place.

  Parameters:  
- min (tuple[int, int]) – Minimum pixel coordinates (X, Y), inclusive. 
- max (tuple[int, int]) – Maximum pixel coordinates (X, Y), inclusive.       free() 

Clear image data immediately (causing an error on re-use).

    resize(size, *, method='FAST') 

Resize the image in-place.

  Parameters:  
- size (tuple[int, int]) – New size. 
- method (str) – Method of resizing (‘FAST’, ‘BILINEAR’).       with_buffer(*, write=False, region=None) 

Return a context manager that yields a `memoryview` of the image’s pixel data, shaped `(height, width, channels)`.

 

Usage:

 

```python
with image.with_buffer(write=True) as buf:
    buf[0, 0, 0] = 255  # set red channel of pixel (0, 0)
```

   Parameters:  
- write (bool) – When true the buffer is writable. 
- region (tuple[tuple[int, int], tuple[int, int]] | None) – Optional sub-region `((x_min, y_min), (x_max, y_max))`, clamped to image bounds. When set the shape becomes `(region_height, region_width, channels)`.   Returns: 

A context manager yielding a `memoryview` of pixel data.

  Return type: 

`ImBufBuffer`

      buffer_type 

Type of the image’s pixel buffer (`'BYTE'` or `'FLOAT'`).

  Type: 

str

      channels 

Number of color channels.

  Type: 

int

      compress 

Compression level for formats that support lossless compression levels (0 - 100, clamped).

  Type: 

int

      file_type 

The file type identifier.

  Type: 

str

      filepath 

Filepath associated with this image.

  Type: 

str | bytes

      planes 

Number of bits per pixel for the byte buffer. Used when reading and writing image files.

  
- 8: Gray-scale. 
- 16: Gray-scale with alpha. 
- 24: RGB. 
- 32: RGBA.   

Note

 

This value may be set by the file format on load, and determines how many channels are written on save.

   Type: 

int

      ppm 

Pixels per meter.

  Type: 

tuple[float, float]

      quality 

Quality for formats that support lossy compression (0 - 100, clamped).

  Type: 

int

      size 

Size of the image in pixels.

  Type: 

tuple[int, int]

    Special Methods  __hash__()  Return type: 

int

      __repr__()  Return type: 

str

       class imbuf.types.ImBufBuffer Special Methods  __enter__()  Return type: 

`ImBufBuffer`

      __exit__(exc_type, exc_value, traceback)  Parameters:  
- exc_type (type | None) – Exception type, or `None`. 
- exc_value (BaseException | None) – Exception instance, or `None`. 
- traceback (BaseException | None) – Traceback object, or `None`.   Return type: 

bool

      __repr__()  Return type: 

str

       class imbuf.types.ImBufFileType   file_extensions 

The file extensions associated with this image file type (e.g. `(".jpg", ".jpeg")`).

  Type: 

tuple[str, …]

      has_read_file 

True when images of this file type can be read from a file.

  Type: 

bool

      has_read_memory 

True when images of this file type can be read from memory.

  Type: 

bool

      has_write_file 

True when images of this file type can be written to a file.

  Type: 

bool

      has_write_memory 

True when images of this file type can be written to memory.

  Type: 

bool

      id 

The identifier for this image file type (e.g. `"PNG"`, `"JPEG"`).

  Type: 

str

    Special Methods  __hash__()  Return type: 

int

      __repr__()  Return type: 

str
