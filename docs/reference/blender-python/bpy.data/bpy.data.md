# bpy.data

# Data Access (bpy.data)

 

This module is used for all Blender/Python access.

   bpy.data.data 

Access to Blender’s internal data

  Type: 

[`bpy.types.BlendData`](bpy.types.BlendData.html#bpy.types.BlendData)

    

```python
import bpy

# Print all objects.
for obj in bpy.data.objects:
    print(obj.name)

# Print all scene names in a list.
print(bpy.data.scenes.keys())

# Remove mesh Cube.
if "Cube" in bpy.data.meshes:
    mesh = bpy.data.meshes["Cube"]
    print("removing mesh", mesh)
    bpy.data.meshes.remove(mesh)

# Write images into a file next to the blend.
import os
with open(os.path.splitext(bpy.data.filepath)[0] + ".txt", 'w') as fs:
    for image in bpy.data.images:
        fs.write("{:s} {:d} x {:d}\n".format(image.filepath, image.size[0], image.size[1]))
```
