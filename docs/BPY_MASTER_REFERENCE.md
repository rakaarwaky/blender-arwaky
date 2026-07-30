# Blender Python API (`bpy`) Master Technical Reference

Unified, comprehensive master reference guide for Blender Python development. For detailed class-by-class API specifications, click on the corresponding modular documentation links below.

---

## Table of Contents & Modular Documentation Index

| Module / Topic | Summary | Modular Folder Link |
| :--- | :--- | :--- |
| **`bpy.data`** | Access all database objects (meshes, materials, scenes, etc.) | [docs/bpy.data/](file:///home/raka/mcp-arwaky/blender-arwaky/docs/bpy.data/bpy.data.md) |
| **`bpy.context`** | Active selection, scene, window, and mode context | [docs/bpy.context/](file:///home/raka/mcp-arwaky/blender-arwaky/docs/bpy.context/bpy.context.md) |
| **`bpy.ops`** | Execution of UI operators and tools | [docs/bpy.ops/](file:///home/raka/mcp-arwaky/blender-arwaky/docs/bpy.ops/bpy.ops.md) |
| **`bpy.types`** | Class definitions for operators, panels, and properties | [docs/bpy.types/](file:///home/raka/mcp-arwaky/blender-arwaky/docs/bpy.types/bpy.types.md) |
| **`bpy.app.timers`** | Application timers and event loops | [docs/bpy.app/timers](file:///home/raka/mcp-arwaky/blender-arwaky/docs/bpy.app/bpy.app.timers.md) |
| **`bpy.app.handlers`** | Application event hooks and callbacks | [docs/bpy.app/handlers](file:///home/raka/mcp-arwaky/blender-arwaky/docs/bpy.app/bpy.app.handlers.md) |
| **`bmesh`** | Advanced mesh topology editing API | [docs/bmesh/](file:///home/raka/mcp-arwaky/blender-arwaky/docs/bmesh/bmesh.md) |
| **`gpu`** | Real-time viewport drawing & GLSL shaders | [docs/gpu/](file:///home/raka/mcp-arwaky/blender-arwaky/docs/gpu/gpu.md) |
| **`mathutils`** | Vector, Matrix, Quaternion linear algebra | [docs/mathutils/](file:///home/raka/mcp-arwaky/blender-arwaky/docs/mathutils/mathutils.md) |
| **`mathutils.bvhtree`** | Bounding Volume Hierarchy 3D ray casting | [docs/mathutils/bvhtree](file:///home/raka/mcp-arwaky/blender-arwaky/docs/mathutils/mathutils.bvhtree.md) |
| **`mathutils.kdtree`** | 3D point cloud nearest neighbor search | [docs/mathutils/kdtree](file:///home/raka/mcp-arwaky/blender-arwaky/docs/mathutils/mathutils.kdtree.md) |
| **`bpy.props`** | Custom property definitions | [docs/bpy.utils_props/props](file:///home/raka/mcp-arwaky/blender-arwaky/docs/bpy.utils_props/bpy.props.md) |
| **`bpy.msgbus`** | Property change event subscriptions | [docs/bpy.utils_props/msgbus](file:///home/raka/mcp-arwaky/blender-arwaky/docs/bpy.utils_props/bpy.msgbus.md) |
| **`bpy.utils`** | Addon registration and resource directory paths | [docs/bpy.utils_props/utils](file:///home/raka/mcp-arwaky/blender-arwaky/docs/bpy.utils_props/bpy.utils.md) |
| **`guides`** | Quickstart and Blender Python guides | [docs/guides/](file:///home/raka/mcp-arwaky/blender-arwaky/docs/guides/info_quickstart.md) |
| **`core`** | Core Blender architecture and Python module integration | [docs/core/](file:///home/raka/mcp-arwaky/blender-arwaky/docs/core/) |

---

## 1. Core Architecture & `bpy` Namespaces

Detailed overview of main namespaces:
- **`bpy.data`**: Database container. See modular reference: [docs/bpy.data/bpy.data.md](file:///home/raka/mcp-arwaky/blender-arwaky/docs/bpy.data/bpy.data.md)
- **`bpy.context`**: Active execution state. See modular reference: [docs/bpy.context/bpy.context.md](file:///home/raka/mcp-arwaky/blender-arwaky/docs/bpy.context/bpy.context.md)
- **`bpy.ops`**: Operator triggers. See modular reference: [docs/bpy.ops/bpy.ops.md](file:///home/raka/mcp-arwaky/blender-arwaky/docs/bpy.ops/bpy.ops.md)

---

## 2. Data Model & Memory Management (`bpy.data`, `bpy.context`)

Detailed file reference: [docs/bpy.data/bpy.data.md](file:///home/raka/mcp-arwaky/blender-arwaky/docs/bpy.data/bpy.data.md) & [docs/bpy.context/bpy.context.md](file:///home/raka/mcp-arwaky/blender-arwaky/docs/bpy.context/bpy.context.md)

```python
import bpy

# Create object manually without UI operators (Fastest method)
mesh = bpy.data.meshes.new("CubeMesh")
obj = bpy.data.objects.new("CubeObject", mesh)
bpy.context.collection.objects.link(obj)

# Safely delete datablock with reference unlinking
bpy.data.objects.remove(obj, do_unlink=True)
bpy.data.meshes.remove(mesh, do_unlink=True)

# Context Override (Run operator in target context)
with bpy.context.temp_override(active_object=obj, selected_objects=[obj]):
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')
```

---

## 3. Linear Algebra & Geometry (`mathutils`, `bmesh`)

Detailed file references: [docs/mathutils/mathutils.md](file:///home/raka/mcp-arwaky/blender-arwaky/docs/mathutils/mathutils.md) & [docs/bmesh/bmesh.md](file:///home/raka/mcp-arwaky/blender-arwaky/docs/bmesh/bmesh.md)

```python
import bpy
import bmesh
from mathutils import Vector, Matrix, Euler

# Transformation Matrix
loc = Vector((0.0, 0.0, 2.0))
rot = Euler((0.0, 0.0, 1.5708), 'XYZ').to_matrix().to_4x4()
obj = bpy.context.active_object
obj.matrix_world = Matrix.Translation(loc) @ rot

# Topology Edit with BMesh
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(obj.data)
bmesh.ops.bevel(bm, geom=bm.edges, offset=0.1, segments=2)
bmesh.update_edit_mesh(obj.data)
bpy.ops.object.mode_set(mode='OBJECT')
```

---

## 4. Shading, Materials & Rendering Engine (Cycles / EEVEE Next)

Detailed file reference: [docs/bpy.types/bpy.types.Material.md](file:///home/raka/mcp-arwaky/blender-arwaky/docs/bpy.types/bpy.types.Material.md)

```python
import bpy

scene = bpy.context.scene
scene.render.engine = 'CYCLES'  # or 'BLENDER_EEVEE_NEXT'
scene.display_settings.display_device = 'sRGB'
scene.view_settings.view_transform = 'AgX'

# Create Shader Material
mat = bpy.data.materials.new("PBR_Material")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.8, 0.1, 0.1, 1.0)
bsdf.inputs['Roughness'].default_value = 0.2

obj.data.materials.append(mat)
```

---

## 5. Animation, Keyframing & Application Handlers

Detailed file references: [docs/bpy.app/bpy.app.timers.md](file:///home/raka/mcp-arwaky/blender-arwaky/docs/bpy.app/bpy.app.timers.md) & [docs/bpy.app/bpy.app.handlers.md](file:///home/raka/mcp-arwaky/blender-arwaky/docs/bpy.app/bpy.app.handlers.md)

```python
import bpy
from bpy.app.handlers import persistent

# Insert Animation Keyframes
for frame in [1, 20, 40]:
    scene.frame_set(frame)
    obj.location.z = frame * 0.1
    obj.keyframe_insert(data_path="location", index=2)

# Persistent Application Event Handler
@persistent
def on_frame_change(scene):
    print("Active Frame:", scene.frame_current)

if on_frame_change not in bpy.app.handlers.frame_change_post:
    bpy.app.handlers.frame_change_post.append(on_frame_change)
```

---

## 6. Viewport Drawing & Custom Shaders (`gpu`, `gpu_extras`, `blf`)

Detailed file reference: [docs/gpu/gpu.md](file:///home/raka/mcp-arwaky/blender-arwaky/docs/gpu/gpu.md)

```python
import bpy
import gpu
import blf
from gpu_extras.batch import batch_for_shader

shader = gpu.shader.from_builtin('POLYLINE_UNIFORM_COLOR')
batch = batch_for_shader(shader, 'LINES', {"pos": [(0, 0, 0), (0, 0, 5)]})

def draw_viewport_callback():
    shader.bind()
    shader.uniform_float("color", (1.0, 1.0, 0.0, 1.0))
    batch.draw(shader)
    
    # 2D Screen Text Overlay
    blf.position(0, 30, 30, 0)
    blf.size(0, 18)
    blf.draw(0, "Viewport Status: OK")

bpy.types.SpaceView3D.draw_handler_add(draw_viewport_callback, (), 'WINDOW', 'POST_VIEW')
```

---

## 7. Addon Development & Extension Manifest (Blender 4.2+)

Detailed file reference: [docs/bpy.types/bpy.types.Operator.md](file:///home/raka/mcp-arwaky/blender-arwaky/docs/bpy.types/bpy.types.Operator.md) & [blender_manifest.toml](file:///home/raka/mcp-arwaky/blender-arwaky/blender_mcp_addon/blender_manifest.toml)

```python
import bpy

class MESH_OT_my_op(bpy.types.Operator):
    bl_idname = "mesh.my_op"
    bl_label = "My Custom Operator"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        self.report({'INFO'}, "Operator Executed")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(MESH_OT_my_op)

def unregister():
    bpy.utils.unregister_class(MESH_OT_my_op)
```

---

## 8. Advanced Utilities (`aud`, `idprop`, `bvhtree`, `kdtree`, `msgbus`)

Detailed file references: [docs/mathutils/mathutils.bvhtree.md](file:///home/raka/mcp-arwaky/blender-arwaky/docs/mathutils/mathutils.bvhtree.md), [docs/mathutils/mathutils.kdtree.md](file:///home/raka/mcp-arwaky/blender-arwaky/docs/mathutils/mathutils.kdtree.md), & [docs/bpy.utils_props/bpy.msgbus.md](file:///home/raka/mcp-arwaky/blender-arwaky/docs/bpy.utils_props/bpy.msgbus.md)

```python
import bpy

# Custom ID Properties
obj["asset_tag"] = "building_01"

# Real-time Message Bus Subscription
def on_active_change():
    print("Active object changed")

bpy.msgbus.subscribe_rna(
    key=(bpy.types.LayerObjects, "active"),
    owner=bpy,
    args=(),
    notify=on_active_change
)
```
