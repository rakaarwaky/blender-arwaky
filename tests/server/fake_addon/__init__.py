"""Fake Blender addon for functional testing.

Simulates a real Blender addon that responds to server commands
via an asyncio stream interface. Used by functional tests to verify
end-to-end server behavior without requiring an actual Blender instance.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Any, BinaryIO

logger = logging.getLogger("FakeBlenderAddon")


class FakeBlenderAddon:
    """Simulates a Blender addon responding to server protocol v2 messages.

    Supports handshake, ping, command dispatch, and code execution responses.
    Uses length-prefixed JSON framing (protocol v2).
    """

    def __init__(self) -> None:
        """Initialize fake addon with default state."""
        self._session_id = f"session_{int(time.time())}"
        self._active_file_path = "/tmp/blender_arwaky/sessions/test.blend"
        self._active_directory = "/tmp/blender_arwaky/sessions"
        self._commands_dispatched: list[dict] = []
        self._code_executions: list[str] = []
        self._running = False

    def start(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """Start the fake addon message loop.

        Args:
            reader: AsyncIO stream reader from client connection.
            writer: AsyncIO stream writer for responses.
        """
        self._running = True
        asyncio.create_task(self._handle_client(reader, writer))

    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """Handle incoming messages from the server."""
        while self._running:
            try:
                # Read length prefix
                header = await asyncio.wait_for(reader.readexactly(4), timeout=5.0)
                length = int.from_bytes(header, byteorder='big')

                # Read payload
                raw = await asyncio.wait_for(reader.read(length), timeout=5.0)
                message = json.loads(raw.decode('utf-8'))

                # Process message
                msg_type = message.get("type", "")
                request_id = message.get("request_id", "")

                if msg_type == "handshake":
                    response = self._handle_handshake(message, request_id)
                elif msg_type == "ping":
                    response = self._handle_ping(message, request_id)
                elif msg_type == "command":
                    response = await self._handle_command(message, request_id)
                elif msg_type == "execute_code":
                    response = await self._handle_execute_code(message, request_id)
                else:
                    response = {
                        "status": "error",
                        "request_id": request_id,
                        "message": f"Unknown message type: {msg_type}",
                    }

                # Send response
                await self._send_response(writer, response)

            except asyncio.TimeoutError:
                logger.debug("Fake addon read timeout")
                break
            except Exception as e:
                logger.error("Fake addon error: %s", e)
                break

    async def _send_response(self, writer: asyncio.StreamWriter, response: dict) -> None:
        """Send a length-prefixed JSON response.

        Args:
            writer: AsyncIO stream writer.
            response: Response dictionary.
        """
        payload = json.dumps(response).encode('utf-8')
        header = len(payload).to_bytes(4, byteorder='big')
        writer.write(header + payload)
        await writer.drain()

    def _handle_handshake(self, message: dict, request_id: str) -> dict:
        """Handle handshake request.

        Args:
            message: The handshake message.
            request_id: Request tracking ID.

        Returns:
            Handshake response with protocol version and session info.
        """
        return {
            "status": "ok",
            "request_id": request_id,
            "protocol_version": "2.0.0",
            "result": {
                "session_id": self._session_id,
                "active_file_path": self._active_file_path,
                "active_directory": self._active_directory,
            },
        }

    def _handle_ping(self, message: dict, request_id: str) -> dict:
        """Handle ping request.

        Args:
            message: The ping message.
            request_id: Request tracking ID.

        Returns:
            Ping response with status ok.
        """
        return {
            "status": "ok",
            "request_id": request_id,
            "result": {},
        }

    async def _handle_command(self, message: dict, request_id: str) -> dict:
        """Handle command dispatch request.

        Args:
            message: The command message.
            request_id: Request tracking ID.

        Returns:
            Command result with action response.
        """
        params = message.get("params", {})
        action = params.get("action", "")
        self._commands_dispatched.append({
            "action": action,
            "params": params,
            "request_id": request_id,
            "timestamp": time.monotonic(),
        })

        # Simulate command responses
        if action == "get_status":
            return {
                "status": "ok",
                "request_id": request_id,
                "result": {
                    "state": "connected",
                    "host": "localhost",
                    "port": 9876,
                },
            }
        elif action == "get_version":
            return {
                "status": "ok",
                "request_id": request_id,
                "result": {"version": "2.0.0"},
            }
        elif action == "execute_code":
            code = params.get("code", "")
            self._code_executions.append(code)
            return {
                "status": "ok",
                "request_id": request_id,
                "result": {"output": f"Executed {len(code)} bytes of code"},
            }

        return {
            "status": "ok",
            "request_id": request_id,
            "result": {"message": f"Command {action} executed"},
        }

    async def _handle_execute_code(self, message: dict, request_id: str) -> dict:
        """Handle direct code execution request.

        Args:
            message: The execute_code message.
            request_id: Request tracking ID.

        Returns:
            Code execution result.
        """
        code = message.get("code", "")
        self._code_executions.append(code)
        return {
            "status": "ok",
            "request_id": request_id,
            "result": {"output": f"Executed {len(code)} bytes of code"},
        }

    def get_commands_dispatched(self) -> list[dict]:
        """Return list of all commands dispatched.

        Returns:
            List of command dispatch records.
        """
        return list(self._commands_dispatched)

    def get_code_executions(self) -> list[str]:
        """Return list of all code strings executed.

        Returns:
            List of executed code strings.
        """
        return list(self._code_executions)

    def reset(self) -> None:
        """Reset addon state for testing."""
        self._commands_dispatched.clear()
        self._code_executions.clear()
        self._running = False
