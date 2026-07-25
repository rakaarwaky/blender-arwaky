"""
Infrastructure: Adapter for Blender Socket Connection.
"""

import asyncio
import contextlib
import logging
import os
import tempfile
from uuid import uuid4

from modules.shared.src.common import BlenderConnectionPort, BlenderPort
from modules.shared.src.common import (
    ActionName,
    BlenderObject,
    ConnectionFailure as ConnectionError,
    ErrorMessage,
    ExecutionError,
    ImageBytes,
    MaxSize,
    ObjectName,
    PythonCode,
    SceneInfo,
    StatusString,
)

logger = logging.getLogger("BlenderMCPServer")

# Default timeout for Blender IPC calls (seconds)
IPC_TIMEOUT_S: float = 30.0


class BlenderSocketAdapter(BlenderPort):
    """Implementation of BlenderPort using a persistent socket connection."""

    def __init__(self, connection_port: BlenderConnectionPort):
        self._connection = connection_port

    def _get_conn(self) -> BlenderConnectionPort:
        """Internal helper for connection access."""
        if not self._connection:
            raise ConnectionError(ErrorMessage("Blender connection not initialized"))
        return self._connection

    def _send(self, action: ActionName, params: dict | None = None) -> dict:
        """Synchronous IPC call to Blender (to be wrapped in asyncio.to_thread)."""
        return self._get_conn().send_command(action, params or {})

    async def execute_code(self, code: PythonCode) -> StatusString:
        try:
            result = await asyncio.wait_for(
                asyncio.to_thread(self._send, ActionName("execute_code"), {"code": str(code)}),
                timeout=IPC_TIMEOUT_S,
            )
            return StatusString(result.get("result", ""))
        except ConnectionError:
            raise
        except asyncio.TimeoutError:
            logger.warning("execute_code timed out after %ss", IPC_TIMEOUT_S)
            raise ExecutionError(ErrorMessage("Blender IPC timed out")) from None
        except Exception as e:
            logger.error("Execution error: %s", e)
            raise ExecutionError(ErrorMessage(str(e))) from e

    async def get_scene_info(self) -> SceneInfo:
        try:
            result = await asyncio.wait_for(
                asyncio.to_thread(self._send, ActionName("get_scene_info")),
                timeout=IPC_TIMEOUT_S,
            )
            return SceneInfo(**result)
        except ConnectionError:
            raise
        except asyncio.TimeoutError:
            logger.warning("get_scene_info timed out after %ss", IPC_TIMEOUT_S)
            raise ExecutionError(ErrorMessage("Blender IPC timed out")) from None
        except Exception as e:
            logger.error("Error getting scene info: %s", e)
            raise ExecutionError(ErrorMessage(str(e))) from e

    async def get_object_info(self, name: ObjectName) -> BlenderObject:
        try:
            result = await asyncio.wait_for(
                asyncio.to_thread(self._send, ActionName("get_object_info"), {"name": str(name)}),
                timeout=IPC_TIMEOUT_S,
            )
            if not result:
                raise ExecutionError(ErrorMessage(f"Object '{name}' not found"))
            return BlenderObject(**result)
        except ConnectionError:
            raise
        except asyncio.TimeoutError:
            logger.warning("get_object_info timed out after %ss", IPC_TIMEOUT_S)
            raise ExecutionError(ErrorMessage("Blender IPC timed out")) from None
        except ExecutionError:
            raise
        except Exception as e:
            logger.error("Error getting object info: %s", e)
            raise ExecutionError(ErrorMessage(str(e))) from e

    async def get_screenshot(
        self,
        max_size: MaxSize | None = None,
        view_angle: str = "PERSPECTIVE",
        shading_mode: str = "MATERIAL",
        show_overlays: bool = True,
        focus_object: str | None = None,
    ) -> tuple[ImageBytes, int, int]:
        """Capture viewport screenshot with AI optimizations. Returns (image_bytes, width, height)."""
        max_size = max_size or MaxSize(800)
        temp_path = os.path.join(tempfile.gettempdir(), f"blender_ss_{uuid4().hex}.png")
        try:
            result = await asyncio.wait_for(
                asyncio.to_thread(
                    self._send,
                    ActionName("get_viewport_screenshot"),
                    {
                        "max_size": int(max_size),
                        "filepath": temp_path,
                        "format": "png",
                        "view_angle": view_angle,
                        "shading_mode": shading_mode,
                        "show_overlays": show_overlays,
                        "focus_object": focus_object,
                    },
                ),
                timeout=IPC_TIMEOUT_S,
            )
            if isinstance(result, dict) and "error" in result:
                raise ExecutionError(ErrorMessage(result["error"]))
            if not os.path.exists(temp_path):
                raise ExecutionError(ErrorMessage("Screenshot file was not created by Blender"))
            with open(temp_path, "rb") as f:
                image_bytes = ImageBytes(f.read())
            width = result.get("width", 800) if isinstance(result, dict) else 800
            height = result.get("height", 600) if isinstance(result, dict) else 600
            return image_bytes, width, height
        except ConnectionError:
            raise
        except asyncio.TimeoutError:
            logger.warning("get_screenshot timed out after %ss", IPC_TIMEOUT_S)
            raise ExecutionError(ErrorMessage("Blender IPC timed out")) from None
        except ExecutionError:
            raise
        except Exception as e:
            logger.error("Error getting screenshot: %s", e)
            raise ExecutionError(ErrorMessage(str(e))) from e
        finally:
            if os.path.exists(temp_path):
                with contextlib.suppress(OSError):
                    os.remove(temp_path)
