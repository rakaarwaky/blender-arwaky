import contextlib
import io
import json
import logging
import math
import queue
import socket
import struct
import threading
import time
from contextlib import redirect_stdout
from pathlib import Path

import bpy

from . import polyhaven, sketchfab, utils

logger = logging.getLogger(__name__)

# Max message size (10MB)
MAX_MESSAGE_SIZE = 10 * 1024 * 1024


class BlenderMCPServer:
    def __init__(self, host="localhost", port=9876):
        self.host = host
        self.port = port
        self.running = False
        self.socket = None
        self.server_thread = None
        self.command_queue = queue.Queue()
        self._timer_handle = None
        self._shutdown_lock = threading.Lock()
        self._shutdown_requested = False
        self._pending_responses = []  # Track pending res_q for shutdown signaling

    def start(self):
        if self.running:
            return
        self.running = True
        self._shutdown_requested = False
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.socket.settimeout(1.0)

            self.server_thread = threading.Thread(target=self._server_loop)
            self.server_thread.daemon = True
            self.server_thread.start()

            # Timer for processing commands in main thread (GUI mode)
            if not bpy.app.background:
                self._timer_handle = bpy.app.timers.register(self.process_commands, first_interval=0.1, persistent=True)

            logger.info("BlenderMCP server started on %s:%s", self.host, self.port)
        except Exception as e:
            logger.error("Failed to start server: %s", e)
            self.stop()

    def stop(self):
        with self._shutdown_lock:
            if self._shutdown_requested:
                return
            self._shutdown_requested = True
            self.running = False

        # Signal all pending response queues to unblock waiting threads
        for res_q in self._pending_responses:
            with contextlib.suppress(queue.Full):
                res_q.put_nowait(None)
        self._pending_responses.clear()

        if self.socket:
            try:
                self.socket.close()
            except Exception as e:
                logger.debug("Error closing socket: %s", e)
            self.socket = None

        if self._timer_handle:
            try:
                bpy.app.timers.unregister(self.process_commands)
            except Exception as e:
                logger.debug("Error unregistering timer: %s", e)
            self._timer_handle = None

        # Clear queue
        while not self.command_queue.empty():
            try:
                self.command_queue.get_nowait()
            except queue.Empty:
                break

        if self.server_thread:
            self.server_thread.join(timeout=2.0)
            self.server_thread = None
        logger.info("BlenderMCP server stopped")

    def _server_loop(self):
        while self.running:
            try:
                client, addr = self.socket.accept()
                t = threading.Thread(target=self._handle_client, args=(client,))
                t.daemon = True
                t.start()
            except TimeoutError:
                continue
            except Exception as e:
                if self.running:
                    logger.error("Server accept error: %s", e)
                time.sleep(0.1)

    def _handle_client(self, client):
        """Handle a single client connection with length-prefixed message framing."""
        client.settimeout(30.0)
        try:
            while self.running:
                try:
                    # Read 4-byte length header
                    header = b""
                    while len(header) < 4:
                        chunk = client.recv(4 - len(header))
                        if not chunk:
                            return
                        header += chunk

                    msg_len = struct.unpack("!I", header)[0]
                    if msg_len > MAX_MESSAGE_SIZE:
                        logger.warning("Message too large: %d bytes", msg_len)
                        return

                    # Read message body
                    body = b""
                    while len(body) < msg_len:
                        chunk = client.recv(min(8192, msg_len - len(body)))
                        if not chunk:
                            return
                        body += chunk

                    command = json.loads(body.decode("utf-8"))

                    res_q = queue.Queue()
                    self._pending_responses.append(res_q)
                    try:
                        self.command_queue.put((command, client, res_q))
                        try:
                            res_q.get(timeout=30.0)
                        except queue.Empty:
                            logger.warning("Command %s timed out", command.get("type"))
                            self._send_response(client, {"status": "error", "message": "Command timed out"})
                    finally:
                        with contextlib.suppress(ValueError):
                            self._pending_responses.remove(res_q)

                except TimeoutError:
                    continue
                except (ConnectionError, BrokenPipeError, OSError) as e:
                    logger.error("Client connection error: %s", e)
                    break
                except (json.JSONDecodeError, UnicodeDecodeError) as e:
                    logger.warning("Invalid message: %s", e)
                    continue
        finally:
            with contextlib.suppress(Exception):
                client.close()

    def _send_response(self, client, response):
        """Send a length-prefixed JSON response."""
        try:
            data = json.dumps(response).encode("utf-8")
            header = struct.pack("!I", len(data))
            client.sendall(header + data)
        except Exception as e:
            logger.debug("Error sending response: %s", e)

    def process_commands(self):
        if self._shutdown_requested:
            return 0.1

        while not self.command_queue.empty():
            try:
                cmd, client, res_q = self.command_queue.get_nowait()
                try:
                    if self._shutdown_requested:
                        break
                    response = self.execute_command(cmd)
                    self._send_response(client, response)
                except Exception as e:
                    logger.exception("Exec error: %s", e)
                    self._send_response(client, {"status": "error", "message": str(e)})
                finally:
                    res_q.put(True)
            except queue.Empty:
                break
        return 0.1

    def execute_command(self, command):
        cmd_type = command.get("type")
        params = command.get("params", {})

        # Dispatch table (removed hunyuan/hyper3d handlers)
        handlers = {
            "get_scene_info": self.get_scene_info,
            "cleanup_scene": self.cleanup_scene,
            "list_scene_objects": self.list_scene_objects,
            "get_object_hierarchy": self.get_object_hierarchy,
            "undo": self.undo,
            "redo": self.redo,
            "setup_environment": self.setup_environment,
            "configure_camera": self.configure_camera,
            "get_object_info": self.get_object_info,
            "place_asset": self.place_asset,
            "create_primitive": self.create_primitive,
            "set_object_transform": self.set_object_transform,
            "delete_object": self.delete_object,
            "set_material": self.set_material,
            "create_material": self.create_material,
            "set_material_properties": self.set_material_properties,
            "set_material_texture": self.set_material_texture,
            "apply_modifier": self.apply_modifier,
            "import_glb": self.import_glb,
            "import_asset": self.import_asset,
            "export_model": self.export_model,
            "get_viewport_screenshot": utils.get_viewport_screenshot,
            "render": self.render,
            "set_render_settings": self.set_render_settings,
            "inspect_geometry_node_group": self.inspect_geometry_node_group,
            "create_geometry_node_group": self.create_geometry_node_group,
            "set_geometry_node_link": self.set_geometry_node_link,
            "set_geometry_node_modifier": self.set_geometry_node_modifier,
            "get_animation_state": self.get_animation_state,
            "insert_object_keyframe": self.insert_object_keyframe,
            "set_timeline_range": self.set_timeline_range,
            "list_object_keyframes": self.list_object_keyframes,
            "get_mesh_statistics": self.get_mesh_statistics,
            "validate_mesh": self.validate_mesh,
            "perform_mesh_edit_operation": self.perform_mesh_edit_operation,
            "ensure_mesh_uv_layer": self.ensure_mesh_uv_layer,
            "execute_code": self.execute_code,
            "execute_blender_code": self.execute_code,
            "get_polyhaven_categories": polyhaven.get_polyhaven_categories,
            "search_polyhaven_assets": polyhaven.search_polyhaven_assets,
            "download_polyhaven_asset": polyhaven.download_polyhaven_asset,
            "set_texture": polyhaven.set_texture,
            "cleanup_polyhaven": polyhaven.cleanup_polyhaven,
            "get_polyhaven_status": polyhaven.get_polyhaven_status,
            "get_polyhaven_asset_details": polyhaven.get_polyhaven_asset_details,
            "get_sketchfab_status": sketchfab.get_sketchfab_status,
            "get_telemetry_consent": self.get_telemetry_consent,
            "search_sketchfab_models": sketchfab.search_sketchfab_models,
            "get_sketchfab_model_preview": sketchfab.get_sketchfab_model_preview,
            "download_sketchfab_model": sketchfab.download_sketchfab_model,
        }

        handler = handlers.get(cmd_type)
        if not handler:
            return {"status": "error", "message": f"Unknown command: {cmd_type}"}

        try:
            result = handler(**params)
            return {"status": "success", "result": result}
        except Exception as e:
            logger.exception("Command execution failed: %s", command.get("type"))
            return {"status": "error", "message": str(e)}

    def get_scene_info(self):
        scene = bpy.context.scene
        total_objects = len(scene.objects)
        return {
            "name": scene.name,
            "objects": [{"name": o.name, "type": o.type} for o in scene.objects[:50]],
            "total_count": total_objects,
            "truncated": total_objects > 50,
        }

    def cleanup_scene(self, mode):
        """Remove scene content according to the validated cleanup mode."""
        if mode not in {"all", "objects", "meshes"}:
            raise ValueError(f"Unsupported cleanup mode: {mode}")
        if mode in {"all", "objects"}:
            bpy.ops.object.select_all(action="SELECT")
            bpy.ops.object.delete(use_global=False)
        else:
            for obj in list(bpy.data.objects):
                if obj.type == "MESH":
                    bpy.data.objects.remove(obj, do_unlink=True)
        return {"mode": mode, "removed": True}

    def list_scene_objects(self, include_hidden=False, object_type=None, limit=100):
        """List bounded structured object summaries from the active scene."""
        limit = int(limit)
        if not 1 <= limit <= 1000:
            raise ValueError("limit must be between 1 and 1000")
        requested_type = str(object_type).upper() if object_type else None
        objects = []
        for obj in bpy.context.scene.objects:
            if not include_hidden and obj.hide_get():
                continue
            if requested_type and obj.type != requested_type:
                continue
            objects.append(
                {
                    "name": obj.name,
                    "type": obj.type,
                    "parent": obj.parent.name if obj.parent else None,
                    "collections": [collection.name for collection in obj.users_collection],
                    "visible": not obj.hide_get(),
                    "location": list(obj.location),
                }
            )
            if len(objects) >= limit:
                break
        total_matching = sum(
            1
            for obj in bpy.context.scene.objects
            if (include_hidden or not obj.hide_get()) and (not requested_type or obj.type == requested_type)
        )
        return {
            "objects": objects,
            "count": len(objects),
            "total_matching": total_matching,
            "truncated": total_matching > len(objects),
            "include_hidden": bool(include_hidden),
            "object_type": requested_type,
        }

    def get_object_hierarchy(self, object_name=None, include_hidden=False, max_depth=32):
        """Return a bounded parent-child hierarchy for one object or scene roots."""
        max_depth = int(max_depth)
        if not 1 <= max_depth <= 64:
            raise ValueError("max_depth must be between 1 and 64")

        def visible(obj):
            return bool(include_hidden) or not obj.hide_get()

        def node(obj, depth):
            item = {"name": obj.name, "type": obj.type, "children": []}
            if depth >= max_depth:
                item["truncated"] = bool(obj.children)
                return item
            for child in sorted(obj.children, key=lambda value: value.name):
                if visible(child):
                    item["children"].append(node(child, depth + 1))
            return item

        if object_name:
            root = bpy.data.objects.get(str(object_name))
            if root is None:
                raise ValueError(f"Object not found: {object_name}")
            roots = [root] if visible(root) else []
        else:
            roots = sorted(
                [obj for obj in bpy.context.scene.objects if obj.parent is None and visible(obj)],
                key=lambda value: value.name,
            )
        return {
            "roots": [node(root, 0) for root in roots],
            "root_count": len(roots),
            "object_name": str(object_name) if object_name else None,
            "include_hidden": bool(include_hidden),
            "max_depth": max_depth,
        }

    def undo(self):
        """Undo the most recent Blender edit operation."""
        try:
            result = bpy.ops.ed.undo()
        except RuntimeError as error:
            if not bpy.app.background:
                raise
            try:
                bpy.ops.ed.undo_push(message="Blender Arwaky")
                result = bpy.ops.ed.undo()
            except RuntimeError as background_error:
                return {
                    "operation": "undo",
                    "status": "unavailable",
                    "reason": "background_context",
                    "message": str(background_error or error),
                }
        return {"operation": "undo", "status": "finished" if "FINISHED" in result else str(result)}

    def redo(self):
        """Redo the most recently undone Blender edit operation."""
        try:
            result = bpy.ops.ed.redo()
        except RuntimeError as error:
            if not bpy.app.background:
                raise
            return {
                "operation": "redo",
                "status": "unavailable",
                "reason": "background_context",
                "message": str(error),
            }
        return {"operation": "redo", "status": "finished" if "FINISHED" in result else str(result)}

    def setup_environment(self, hdri_id, strength=1.0):
        """Configure a local HDRI file as the active World environment.

        ``hdri_id`` is a local, already-available asset reference. Asset
        acquisition remains owned by the Asset feature; this handler only
        applies the resolved file in Blender.
        """
        hdri_path = Path(str(hdri_id)).expanduser()
        if not hdri_path.is_file():
            raise FileNotFoundError(f"HDRI asset not found: {hdri_id}")
        if hdri_path.suffix.lower() not in {".hdr", ".exr"}:
            raise ValueError("HDRI asset must use .hdr or .exr format")
        strength = float(strength)
        if not math.isfinite(strength) or not 0.0 <= strength <= 10.0:
            raise ValueError("HDRI strength must be between 0 and 10")

        scene = bpy.context.scene
        world = scene.world or bpy.data.worlds.new(name="World")
        scene.world = world
        world.use_nodes = True
        nodes = world.node_tree.nodes
        links = world.node_tree.links
        nodes.clear()
        output = nodes.new("ShaderNodeOutputWorld")
        background = nodes.new("ShaderNodeBackground")
        environment = nodes.new("ShaderNodeTexEnvironment")
        environment.image = bpy.data.images.load(str(hdri_path.resolve()), check_existing=True)
        background.inputs["Strength"].default_value = strength
        links.new(environment.outputs["Color"], background.inputs["Color"])
        links.new(background.outputs["Background"], output.inputs["Surface"])
        return {
            "hdri_id": str(hdri_path.resolve()),
            "environment_ref": world.name,
            "strength": strength,
        }

    def configure_camera(
        self,
        camera_ref=None,
        focal_length=50.0,
        sensor_fit="AUTO",
        framing_target=None,
        set_active=False,
        depth_of_field_enabled=False,
        focus_distance=None,
        focus_object=None,
        aperture=2.8,
        create_if_missing=True,
    ):
        """Configure a real Blender camera according to FR-RND-003."""
        focal_length = float(focal_length)
        aperture = float(aperture)
        if not math.isfinite(focal_length) or not 1.0 <= focal_length <= 500.0:
            raise ValueError("focal_length must be between 1 and 500")
        if sensor_fit not in {"AUTO", "HORIZONTAL", "VERTICAL"}:
            raise ValueError(f"Unsupported sensor_fit: {sensor_fit}")
        if not math.isfinite(aperture) or aperture <= 0.0:
            raise ValueError("aperture must be a positive finite number")

        scene = bpy.context.scene
        camera = bpy.data.objects.get(str(camera_ref)) if camera_ref else scene.camera
        if camera is None:
            if not create_if_missing:
                raise ValueError("Camera not found and create_if_missing is false")
            camera_data = bpy.data.cameras.new("Camera")
            camera = bpy.data.objects.new("Camera", camera_data)
            scene.collection.objects.link(camera)
        if camera.type != "CAMERA":
            raise ValueError(f"Object is not a camera: {camera.name}")

        camera.data.lens = focal_length
        camera.data.sensor_fit = sensor_fit
        camera.data.dof.use_dof = bool(depth_of_field_enabled)
        camera.data.dof.aperture_fstop = aperture

        if focus_distance is not None:
            focus_distance = float(focus_distance)
            if not math.isfinite(focus_distance) or focus_distance <= 0.0:
                raise ValueError("focus_distance must be positive and finite")
            camera.data.dof.focus_distance = focus_distance

        if focus_object:
            target = bpy.data.objects.get(str(focus_object))
            if target is None:
                raise ValueError(f"Focus object not found: {focus_object}")
            camera.data.dof.focus_object = target

        if framing_target:
            target = bpy.data.objects.get(str(framing_target))
            if target is None:
                raise ValueError(f"Framing target not found: {framing_target}")
            direction = target.location - camera.location
            if direction.length == 0:
                raise ValueError("Framing target must not share the camera location")
            camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

        if set_active:
            scene.camera = camera

        return {
            "camera_ref": camera.name,
            "focal_length": camera.data.lens,
            "sensor_fit": camera.data.sensor_fit,
            "active": scene.camera == camera,
            "depth_of_field_enabled": camera.data.dof.use_dof,
            "focus_distance": camera.data.dof.focus_distance,
            "focus_object": camera.data.dof.focus_object.name if camera.data.dof.focus_object else None,
            "aperture": camera.data.dof.aperture_fstop,
        }

    def place_asset(self, asset_id, location=None, rotation=None, scale=None):
        """Place an existing scene object identified by an exact asset reference."""
        obj = bpy.data.objects.get(str(asset_id))
        if obj is None:
            raise ValueError(f"Asset object not found: {asset_id}")
        if location is not None:
            if len(location) != 3 or not all(math.isfinite(float(value)) for value in location):
                raise ValueError("location must contain three finite numbers")
            obj.location = tuple(float(value) for value in location)
        if rotation is not None:
            if len(rotation) != 3 or not all(math.isfinite(float(value)) for value in rotation):
                raise ValueError("rotation must contain three finite degree values")
            obj.rotation_euler = tuple(math.radians(float(value)) for value in rotation)
        if scale is not None:
            if len(scale) != 3 or not all(math.isfinite(float(value)) and float(value) != 0.0 for value in scale):
                raise ValueError("scale must contain three finite non-zero numbers")
            obj.scale = tuple(float(value) for value in scale)
        return {
            "asset_id": str(asset_id),
            "object_name": obj.name,
            "location": list(obj.location),
            "rotation": list(obj.rotation_euler),
            "scale": list(obj.scale),
        }

    def get_object_info(self, object_name):
        obj = bpy.data.objects.get(object_name)
        if not obj:
            return {"error": "Not found"}
        return {
            "name": obj.name,
            "type": obj.type,
            "location": list(obj.location),
            "rotation": list(obj.rotation_euler),
            "scale": list(obj.scale),
            "modifiers": [modifier.name for modifier in obj.modifiers],
            "materials": [slot.material.name for slot in obj.material_slots if slot.material],
        }

    def create_primitive(self, primitive_type, location=None, scale=None, name=None):
        """Create a primitive mesh through Blender's public operators."""
        operation = getattr(bpy.ops.mesh, f"primitive_{str(primitive_type).lower()}_add", None)
        if operation is None:
            raise ValueError(f"Unsupported primitive type: {primitive_type}")
        operation(location=tuple(location or (0, 0, 0)))
        obj = bpy.context.object
        if obj is None:
            raise RuntimeError("Blender did not create an active object")
        if scale is not None:
            obj.scale = tuple(scale)
        if name:
            obj.name = name
        return {"name": obj.name, "type": obj.type, "location": list(obj.location), "scale": list(obj.scale)}

    def set_object_transform(self, object_name, location=None, rotation=None, scale=None):
        """Update object transform; rotation input is expressed in degrees."""
        obj = bpy.data.objects.get(object_name)
        if obj is None:
            raise ValueError(f"Object not found: {object_name}")
        if location is not None:
            obj.location = tuple(location)
        if rotation is not None:
            import math

            obj.rotation_euler = tuple(math.radians(value) for value in rotation)
        if scale is not None:
            obj.scale = tuple(scale)
        return {
            "name": obj.name,
            "location": list(obj.location),
            "rotation": list(obj.rotation_euler),
            "scale": list(obj.scale),
        }

    def delete_object(self, object_name):
        """Delete a named object from the current scene."""
        obj = bpy.data.objects.get(object_name)
        if obj is None:
            raise ValueError(f"Object not found: {object_name}")
        bpy.data.objects.remove(obj, do_unlink=True)
        return {"name": object_name, "deleted": True}

    def set_material(self, object_name, material_name):
        """Assign an existing or newly-created material to an object."""
        obj = bpy.data.objects.get(object_name)
        if obj is None:
            raise ValueError(f"Object not found: {object_name}")
        material = bpy.data.materials.get(material_name) or bpy.data.materials.new(material_name)
        if (
            obj.data
            and hasattr(obj.data, "materials")
            and material.name not in [item.name for item in obj.data.materials if item]
        ):
            obj.data.materials.append(material)
        return {"object_name": object_name, "material_name": material.name}

    @staticmethod
    def _validate_rgba(base_color):
        """Validate and normalize an RGB/RGBA color in Blender's 0-1 range."""
        if base_color is None:
            return None
        values = [float(value) for value in base_color]
        if len(values) == 3:
            values.append(1.0)
        if len(values) != 4 or not all(math.isfinite(value) and 0.0 <= value <= 1.0 for value in values):
            raise ValueError("base_color must contain 3 or 4 finite channels in the range 0-1")
        return values

    @staticmethod
    def _principled_material(material):
        material.use_nodes = True
        node = material.node_tree.nodes.get("Principled BSDF")
        if node is None:
            raise RuntimeError(f"Material has no Principled BSDF node: {material.name}")
        return node

    def create_material(
        self,
        material_name,
        base_color=None,
        metallic=0.0,
        roughness=0.5,
        reuse_existing=True,
    ):
        """Create or reuse a bounded Principled BSDF material."""
        name = str(material_name).strip()
        if not name:
            raise ValueError("material_name is required")
        metallic = float(metallic)
        roughness = float(roughness)
        if not 0.0 <= metallic <= 1.0 or not math.isfinite(metallic):
            raise ValueError("metallic must be between 0 and 1")
        if not 0.0 <= roughness <= 1.0 or not math.isfinite(roughness):
            raise ValueError("roughness must be between 0 and 1")
        color = self._validate_rgba(base_color if base_color is not None else [0.8, 0.8, 0.8, 1.0])
        material = bpy.data.materials.get(name)
        created = material is None
        if material is not None and not reuse_existing:
            raise ValueError(f"Material already exists: {name}")
        if material is None:
            material = bpy.data.materials.new(name=name)
        node = self._principled_material(material)
        node.inputs["Base Color"].default_value = color
        node.inputs["Metallic"].default_value = metallic
        node.inputs["Roughness"].default_value = roughness
        return {
            "material_name": material.name,
            "created": created,
            "base_color": list(node.inputs["Base Color"].default_value),
            "metallic": float(node.inputs["Metallic"].default_value),
            "roughness": float(node.inputs["Roughness"].default_value),
        }

    def set_material_properties(self, material_name, base_color=None, metallic=None, roughness=None):
        """Update supplied Principled BSDF properties without changing omitted values."""
        material = bpy.data.materials.get(str(material_name))
        if material is None:
            raise ValueError(f"Material not found: {material_name}")
        node = self._principled_material(material)
        if base_color is not None:
            node.inputs["Base Color"].default_value = self._validate_rgba(base_color)
        for key, raw_value in (("Metallic", metallic), ("Roughness", roughness)):
            if raw_value is not None:
                value = float(raw_value)
                if not math.isfinite(value) or not 0.0 <= value <= 1.0:
                    raise ValueError(f"{key.lower()} must be between 0 and 1")
                node.inputs[key].default_value = value
        return {
            "material_name": material.name,
            "base_color": list(node.inputs["Base Color"].default_value),
            "metallic": float(node.inputs["Metallic"].default_value),
            "roughness": float(node.inputs["Roughness"].default_value),
        }

    def set_material_texture(self, material_name, file_path):
        """Attach a local image texture to a material's base color input."""
        material = bpy.data.materials.get(str(material_name))
        if material is None:
            raise ValueError(f"Material not found: {material_name}")
        path = Path(str(file_path)).expanduser()
        if not path.is_file():
            raise FileNotFoundError(f"Texture file not found: {file_path}")
        node = self._principled_material(material)
        image = bpy.data.images.load(str(path.resolve()), check_existing=True)
        texture = material.node_tree.nodes.new("ShaderNodeTexImage")
        texture.image = image
        material.node_tree.links.new(texture.outputs["Color"], node.inputs["Base Color"])
        return {
            "material_name": material.name,
            "file_path": str(path.resolve()),
            "texture_node": texture.name,
        }

    def apply_modifier(self, object_name, modifier_name):
        """Apply a named modifier to an object."""
        obj = bpy.data.objects.get(object_name)
        if obj is None:
            raise ValueError(f"Object not found: {object_name}")
        modifier = obj.modifiers.get(modifier_name)
        if modifier is None:
            raise ValueError(f"Modifier not found: {modifier_name}")
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.modifier_apply(modifier=modifier_name)
        return {"object_name": object_name, "modifier_name": modifier_name, "applied": True}

    def import_asset(
        self,
        file_path,
        asset_type="model",
        target_collection=None,
        scale_normalization=False,
        duplicate_policy="rename",
        format_hint=None,
    ):
        """Import a cached asset and return canonical Blender object references."""
        path = Path(str(file_path)).expanduser()
        if not path.is_file():
            raise FileNotFoundError(f"Asset file not found: {file_path}")
        before = {obj.name for obj in bpy.context.scene.objects}
        suffix = (format_hint or path.suffix).lower().lstrip(".")
        if suffix in {"glb", "gltf"}:
            bpy.ops.import_scene.gltf(filepath=str(path))
        elif suffix == "obj":
            bpy.ops.wm.obj_import(filepath=str(path))
        elif suffix == "fbx":
            bpy.ops.import_scene.fbx(filepath=str(path))
        else:
            raise ValueError(f"Unsupported asset import format: {suffix or asset_type}")
        imported = [obj for obj in bpy.context.scene.objects if obj.name not in before]
        if target_collection:
            collection = bpy.data.collections.get(str(target_collection)) or bpy.data.collections.new(
                str(target_collection)
            )
            if collection.name not in [item.name for item in bpy.context.scene.collection.children]:
                bpy.context.scene.collection.children.link(collection)
            for obj in imported:
                for old_collection in list(obj.users_collection):
                    old_collection.objects.unlink(obj)
                collection.objects.link(obj)
        if scale_normalization:
            for obj in imported:
                obj.scale = (1.0, 1.0, 1.0)
        if duplicate_policy == "reject" and any(obj.name in before for obj in imported):
            raise ValueError("Duplicate asset import rejected")
        return {
            "file_path": str(path),
            "asset_type": str(asset_type),
            "objects": [obj.name for obj in imported],
            "collection": target_collection,
            "duplicate_policy": duplicate_policy,
        }

    def import_glb(self, file_path, object_name=None):
        """Import a GLB/GLTF file and return imported object names."""
        before = {obj.name for obj in bpy.context.scene.objects}
        bpy.ops.import_scene.gltf(filepath=file_path)
        imported = [obj for obj in bpy.context.scene.objects if obj.name not in before]
        if object_name and imported:
            imported[0].name = object_name
        return {"file_path": file_path, "objects": [obj.name for obj in imported]}

    def export_model(self, object_name, file_path, export_format="glb"):
        """Export one selected object using Blender's supported exporter."""
        obj = bpy.data.objects.get(object_name)
        if obj is None:
            raise ValueError(f"Object not found: {object_name}")
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        if export_format == "glb":
            bpy.ops.export_scene.gltf(filepath=file_path, export_format="GLB", use_selection=True)
        elif export_format == "fbx":
            bpy.ops.export_scene.fbx(filepath=file_path, use_selection=True)
        elif export_format == "obj":
            bpy.ops.wm.obj_export(filepath=file_path, export_selected_objects=True)
        else:
            raise ValueError(f"Unsupported export format: {export_format}")
        return {"object_name": object_name, "file_path": file_path, "export_format": export_format}

    def render(self, output_path, resolution_x=1920, resolution_y=1080):
        """Render the active scene to an image file and return its metadata."""
        scene = bpy.context.scene
        previous_resolution = (scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage)
        previous_filepath = scene.render.filepath
        try:
            scene.render.resolution_x = int(resolution_x)
            scene.render.resolution_y = int(resolution_y)
            scene.render.resolution_percentage = 100
            scene.render.filepath = output_path
            bpy.ops.render.render(write_still=True)
            return {
                "filepath": output_path,
                "width": scene.render.resolution_x,
                "height": scene.render.resolution_y,
            }
        finally:
            scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = (
                previous_resolution
            )
            scene.render.filepath = previous_filepath

    def set_render_settings(
        self,
        engine=None,
        resolution_x=1920,
        resolution_y=1080,
        resolution_percentage=100,
        samples=None,
        use_transparent=None,
    ):
        """Apply bounded scene render settings and return the effective values."""
        scene = bpy.context.scene
        resolution_x = int(resolution_x)
        resolution_y = int(resolution_y)
        resolution_percentage = int(resolution_percentage)
        if not 1 <= resolution_x <= 16384 or not 1 <= resolution_y <= 16384:
            raise ValueError("resolution dimensions must be between 1 and 16384")
        if not 1 <= resolution_percentage <= 100:
            raise ValueError("resolution_percentage must be between 1 and 100")
        if engine:
            engine = str(engine).upper()
            valid_engines = {item.identifier for item in scene.render.bl_rna.properties["engine"].enum_items}
            if engine not in valid_engines:
                raise ValueError(f"Unsupported render engine: {engine}")
            scene.render.engine = engine
        scene.render.resolution_x = resolution_x
        scene.render.resolution_y = resolution_y
        scene.render.resolution_percentage = resolution_percentage
        if samples is not None:
            samples = int(samples)
            if not 1 <= samples <= 65536:
                raise ValueError("samples must be between 1 and 65536")
            if hasattr(scene, "cycles"):
                scene.cycles.samples = samples
            eevee = getattr(scene, "eevee", None)
            if eevee is not None and hasattr(eevee, "taa_render_samples"):
                eevee.taa_render_samples = samples
        if use_transparent is not None:
            scene.render.film_transparent = bool(use_transparent)
        result = {
            "engine": scene.render.engine,
            "resolution_x": scene.render.resolution_x,
            "resolution_y": scene.render.resolution_y,
            "resolution_percentage": scene.render.resolution_percentage,
            "use_transparent": scene.render.film_transparent,
        }
        if hasattr(scene, "cycles"):
            result["cycles_samples"] = scene.cycles.samples
        return result

    @staticmethod
    def _bounded_wave_two_limit(value):
        limit = int(value)
        if not 1 <= limit <= 1000:
            raise ValueError("limit must be between 1 and 1000")
        return limit

    @staticmethod
    def _bounded_wave_two_frame(value):
        frame = int(value)
        if not -100000 <= frame <= 100000:
            raise ValueError("frame must be between -100000 and 100000")
        return frame

    def inspect_geometry_node_group(self, node_group_name):
        """Inspect a bounded Geometry Nodes graph and its interface sockets."""
        name = str(node_group_name).strip()
        if not name:
            raise ValueError("node_group_name is required")
        group = bpy.data.node_groups.get(name)
        if group is None:
            raise ValueError(f"Geometry Nodes group not found: {name}")
        links = []
        for link in list(group.links)[:256]:
            links.append(
                {
                    "from_node": link.from_node.name,
                    "from_socket": link.from_socket.name,
                    "to_node": link.to_node.name,
                    "to_socket": link.to_socket.name,
                }
            )
        sockets = []
        interface = getattr(group, "interface", None)
        if interface is not None and hasattr(interface, "items_tree"):
            for item in list(interface.items_tree)[:256]:
                if hasattr(item, "socket_type"):
                    sockets.append(
                        {
                            "name": item.name,
                            "socket_type": item.socket_type,
                            "is_output": getattr(item, "in_out", "INPUT") == "OUTPUT",
                        }
                    )
        return {
            "name": group.name,
            "node_count": len(group.nodes),
            "link_count": len(links),
            "links": links,
            "sockets": sockets,
        }

    def create_geometry_node_group(self, node_group_name, object_name=None):
        """Create or reuse a Geometry Nodes group and optionally bind a modifier."""
        name = str(node_group_name).strip()
        if not name or len(name) > 128:
            raise ValueError("node_group_name must be 1-128 characters")
        group = bpy.data.node_groups.get(name)
        created = group is None
        if group is None:
            group = bpy.data.node_groups.new(name, "GeometryNodeTree")
            interface = getattr(group, "interface", None)
            if interface is not None:
                interface.new_socket(name="Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
                interface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
            input_node = group.nodes.new("NodeGroupInput")
            output_node = group.nodes.new("NodeGroupOutput")
            input_socket = input_node.outputs.get("Geometry")
            output_socket = output_node.inputs.get("Geometry")
            if input_socket is not None and output_socket is not None:
                group.links.new(input_socket, output_socket)
        modifier_name = None
        resolved_object = None
        if object_name:
            obj = bpy.data.objects.get(str(object_name))
            if obj is None:
                raise ValueError(f"Object not found: {object_name}")
            modifier = next((item for item in obj.modifiers if item.type == "NODES"), None)
            if modifier is None:
                modifier = obj.modifiers.new(name="GeometryNodes", type="NODES")
            modifier.node_group = group
            modifier_name = modifier.name
            resolved_object = obj.name
        return {
            "group_name": group.name,
            "created": created,
            "changed": created or bool(modifier_name),
            "object_name": resolved_object,
            "modifier_name": modifier_name,
        }

    def set_geometry_node_link(self, node_group_name, from_node, from_socket, to_node, to_socket):
        """Create one validated Geometry Nodes socket link."""
        group = bpy.data.node_groups.get(str(node_group_name))
        if group is None:
            raise ValueError(f"Geometry Nodes group not found: {node_group_name}")
        source = group.nodes.get(str(from_node))
        target = group.nodes.get(str(to_node))
        if source is None or target is None:
            raise ValueError("Geometry Nodes source or target node not found")
        source_socket = source.outputs.get(str(from_socket))
        target_socket = target.inputs.get(str(to_socket))
        if source_socket is None or target_socket is None:
            raise ValueError("Geometry Nodes source or target socket not found")
        for link in group.links:
            if link.from_socket == source_socket and link.to_socket == target_socket:
                return {"group_name": group.name, "changed": False, "message": "Link already exists"}
        group.links.new(source_socket, target_socket)
        return {"group_name": group.name, "changed": True, "message": "Link created"}

    def set_geometry_node_modifier(self, object_name, node_group_name):
        """Bind an existing Geometry Nodes group to an object modifier."""
        obj = bpy.data.objects.get(str(object_name))
        if obj is None:
            raise ValueError(f"Object not found: {object_name}")
        group = bpy.data.node_groups.get(str(node_group_name))
        if group is None:
            raise ValueError(f"Geometry Nodes group not found: {node_group_name}")
        modifier = next((item for item in obj.modifiers if item.type == "NODES"), None)
        if modifier is None:
            modifier = obj.modifiers.new(name="GeometryNodes", type="NODES")
        changed = modifier.node_group != group
        modifier.node_group = group
        return {
            "group_name": group.name,
            "changed": changed,
            "object_name": obj.name,
            "modifier_name": modifier.name,
        }

    def get_animation_state(self, object_name, limit=100):
        """Inspect bounded action and F-curve state for one object."""
        limit = self._bounded_wave_two_limit(limit)
        obj = bpy.data.objects.get(str(object_name))
        if obj is None:
            raise ValueError(f"Object not found: {object_name}")
        action = obj.animation_data.action if obj.animation_data and obj.animation_data.action else None
        curves = []
        if action:
            for curve in list(action.fcurves)[:limit]:
                curves.append(
                    {
                        "data_path": curve.data_path,
                        "array_index": curve.array_index,
                        "keyframes": [
                            {
                                "frame": point.co.x,
                                "value": point.co.y,
                            }
                            for point in list(curve.keyframe_points)[:limit]
                        ],
                    }
                )
        scene = bpy.context.scene
        return {
            "object_name": obj.name,
            "action_name": action.name if action else None,
            "frame_start": scene.frame_start,
            "frame_end": scene.frame_end,
            "current_frame": scene.frame_current,
            "curve_count": len(curves),
            "curves": curves,
        }

    def insert_object_keyframe(self, object_name, frame, data_path, index=None):
        """Insert a keyframe only for supported transform data paths."""
        frame = self._bounded_wave_two_frame(frame)
        path = str(data_path)
        if path not in {"location", "rotation_euler", "scale"}:
            raise ValueError(f"Unsupported animation data path: {path}")
        if index is None:
            keyframe_index = -1
        else:
            keyframe_index = int(index)
            if not 0 <= keyframe_index <= 3:
                raise ValueError("index must be between 0 and 3")
        obj = bpy.data.objects.get(str(object_name))
        if obj is None:
            raise ValueError(f"Object not found: {object_name}")
        bpy.context.scene.frame_set(frame)
        obj.keyframe_insert(data_path=path, index=keyframe_index, frame=frame)
        return {"object_name": obj.name, "data_path": path, "frame": frame, "index": index, "changed": True}

    def set_timeline_range(self, frame_start, frame_end, current_frame=None):
        """Set a bounded scene timeline range."""
        start = self._bounded_wave_two_frame(frame_start)
        end = self._bounded_wave_two_frame(frame_end)
        if end < start:
            raise ValueError("frame_end must be greater than or equal to frame_start")
        scene = bpy.context.scene
        current = scene.frame_current if current_frame is None else self._bounded_wave_two_frame(current_frame)
        if not start <= current <= end:
            raise ValueError("current_frame must be within the timeline range")
        scene.frame_start = start
        scene.frame_end = end
        scene.frame_set(current)
        return {"frame_start": start, "frame_end": end, "current_frame": scene.frame_current}

    def list_object_keyframes(self, object_name, limit=100):
        """Return the same bounded animation state under an explicit list action."""
        return self.get_animation_state(object_name, limit)

    def get_mesh_statistics(self, object_name):
        """Return bounded mesh topology and UV statistics."""
        obj = bpy.data.objects.get(str(object_name))
        if obj is None:
            raise ValueError(f"Object not found: {object_name}")
        if obj.type != "MESH":
            raise ValueError(f"Object is not a mesh: {obj.name}")
        mesh = obj.data
        return {
            "object_name": obj.name,
            "vertex_count": len(mesh.vertices),
            "edge_count": len(mesh.edges),
            "polygon_count": len(mesh.polygons),
            "uv_layer_count": len(mesh.uv_layers),
            "has_custom_normals": bool(getattr(mesh, "has_custom_normals", False)),
        }

    def validate_mesh(self, object_name, limit=100):
        """Validate loose vertices, degenerate faces, and non-manifold edges."""
        limit = self._bounded_wave_two_limit(limit)
        obj = bpy.data.objects.get(str(object_name))
        if obj is None:
            raise ValueError(f"Object not found: {object_name}")
        if obj.type != "MESH":
            raise ValueError(f"Object is not a mesh: {obj.name}")
        import bmesh

        bm = bmesh.new()
        try:
            bm.from_mesh(obj.data)
            bm.verts.ensure_lookup_table()
            bm.edges.ensure_lookup_table()
            bm.faces.ensure_lookup_table()
            findings = []
            loose = [vertex.index for vertex in bm.verts if not vertex.link_edges][:limit]
            degenerate = [face.index for face in bm.faces if len(face.verts) < 3 or face.calc_area() <= 1.0e-12][:limit]
            non_manifold = [edge.index for edge in bm.edges if not edge.is_manifold][:limit]
            for category, values in (
                ("loose_vertices", loose),
                ("degenerate_faces", degenerate),
                ("non_manifold_edges", non_manifold),
            ):
                if values:
                    findings.append({"category": category, "count": len(values), "examples": values})
            return {"object_name": obj.name, "valid": not findings, "findings": findings}
        finally:
            bm.free()

    def perform_mesh_edit_operation(self, object_name, operation):
        """Perform one bounded bmesh operation without requiring edit-mode context."""
        operation = str(operation)
        if operation not in {"recalculate_normals", "triangulate", "remove_doubles"}:
            raise ValueError(f"Unsupported mesh operation: {operation}")
        obj = bpy.data.objects.get(str(object_name))
        if obj is None:
            raise ValueError(f"Object not found: {object_name}")
        if obj.type != "MESH":
            raise ValueError(f"Object is not a mesh: {obj.name}")
        import bmesh

        bm = bmesh.new()
        try:
            bm.from_mesh(obj.data)
            changed = False
            if operation == "recalculate_normals":
                bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
                changed = True
            elif operation == "triangulate":
                result = bmesh.ops.triangulate(bm, faces=list(bm.faces))
                changed = bool(result.get("faces"))
            else:
                result = bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1.0e-6)
                changed = bool(result.get("targetmap"))
            bm.to_mesh(obj.data)
            obj.data.update()
            return {"object_name": obj.name, "operation": operation, "changed": changed}
        finally:
            bm.free()

    def ensure_mesh_uv_layer(self, object_name, uv_layer_name="UVMap"):
        """Create or reuse a named UV layer for a mesh object."""
        name = str(uv_layer_name).strip() or "UVMap"
        if len(name) > 64:
            raise ValueError("uv_layer_name must not exceed 64 characters")
        obj = bpy.data.objects.get(str(object_name))
        if obj is None:
            raise ValueError(f"Object not found: {object_name}")
        if obj.type != "MESH":
            raise ValueError(f"Object is not a mesh: {obj.name}")
        layer = obj.data.uv_layers.get(name)
        created = layer is None
        if layer is None:
            layer = obj.data.uv_layers.new(name=name)
        return {
            "object_name": obj.name,
            "operation": "ensure_mesh_uv_layer",
            "changed": created,
            "uv_layer_name": layer.name,
        }

    def execute_code(self, code):
        out = io.StringIO()
        try:
            with redirect_stdout(out):
                exec(code, {"bpy": bpy, "mathutils": __import__("mathutils")})  # nosec
            return {"executed": True, "result": out.getvalue()}
        except Exception as e:
            return {"executed": False, "error": str(e)}

    def get_telemetry_consent(self):
        try:
            addon_prefs = bpy.context.preferences.addons[__package__].preferences
            return {
                "consent": getattr(addon_prefs, "telemetry_consent", False),
                "message": "Telemetry consent status retrieved",
            }
        except Exception as e:
            return {"error": f"Failed to get telemetry consent: {str(e)}"}
