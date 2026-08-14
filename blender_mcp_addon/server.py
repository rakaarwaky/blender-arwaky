import contextlib
import io
import json
import logging
import queue
import socket
import struct
import threading
import time
from contextlib import redirect_stdout

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
            "get_object_info": self.get_object_info,
            "get_viewport_screenshot": utils.get_viewport_screenshot,
            "render": self.render,
            "execute_code": self.execute_code,
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

    def get_object_info(self, name):
        obj = bpy.data.objects.get(name)
        if not obj:
            return {"error": "Not found"}
        return {
            "name": obj.name,
            "type": obj.type,
            "location": list(obj.location),
            "rotation": list(obj.rotation_euler),
            "scale": list(obj.scale),
        }

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

    def execute_code(self, code):
        out = io.StringIO()
        try:
            with redirect_stdout(out):
                exec(code, {"bpy": bpy, "mathutils": __import__("mathutils")})  # nosec B102
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
