# bpy.types.BlendDataPathMeta

# BlendDataPathMeta

   class bpy.types.BlendDataPathMeta 

Metadata about a file path visited by [`bpy.types.BlendData.file_path_foreach`](bpy.types.BlendData.html#bpy.types.BlendData.file_path_foreach).

   is_cache 

True when the path is a cache file, like the image texture cache. These paths can not be edited.

  Type: 

bool

      is_expanded 

True when the path was expanded from a UDIM tile or sequence frame. These paths can not be edited.

  Type: 

bool

      is_readonly 

True when the path is read-only and can not be edited.

  Type: 

bool
