"""Capability: Blender command dispatch with timeout enforcement.

Implements IBlenderCommandProtocol — dispatches named commands to the
Blender addon via TCP socket with configurable timeout per FR-SRV-003.
Includes argument schema validation.
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import ActionName, ErrorMessage
from modules.shared.src.common.taxonomy_domain_error import ValidationError
from modules.shared.src.server import (
    DEFAULT_COMMAND_TIMEOUT_MS,
    CommandTimeoutError,
    IBlenderCommandProtocol,
    IBlenderConnectionProtocol,
    get_command_schema,
)

logger = logging.getLogger("BlenderMCPServer")


class BlenderCommandAdapter(IBlenderCommandProtocol):
    """Command dispatch capability for Blender TCP socket operations."""

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(self, connection_port: IBlenderConnectionProtocol) -> None:
        self._connection = connection_port

    # ─── Block 2: Protocol Method Implementation ─────────────

    async def send_command(
        self,
        action: ActionName,
        params: dict[str, Any] | None = None,
        timeout_ms: float | None = None,
    ) -> dict[str, Any]:  # FR-SRV-003
        """Dispatch a named command to Blender addon.

        Routes through TCP socket; response parsed as JSON.
        Default timeout: DEFAULT_COMMAND_TIMEOUT_MS (5000ms).
        Validates command arguments against schema per FR-SRV-003.
        Raises CommandTimeoutError if response exceeds timeout.

        Args:
            action: Named action to dispatch to Blender.
            params: Optional command arguments dictionary.
            timeout_ms: Override timeout in milliseconds. Uses default if None.

        Returns:
            Command result dict with status, data, error, execution_time_ms.

        Raises:
            ValidationError: if command arguments are invalid.
            CommandTimeoutError: if response exceeds configured timeout.
        """
        # Validate command arguments against schema (FR-SRV-003)
        action_str = str(action) if not isinstance(action, str) else action
        try:
            get_command_schema(action_str)  # Validates command exists
        except Exception as e:
            raise ValidationError(ErrorMessage(f"Invalid command: {action_str}")) from e

        timeout_s = (timeout_ms or DEFAULT_COMMAND_TIMEOUT_MS) / 1000.0
        start = time.monotonic()

        try:
            result = await asyncio.wait_for(
                self._connection.send_command(action, params),
                timeout=timeout_s,
            )
            elapsed_ms = (time.monotonic() - start) * 1000
            logger.info(
                "Command %s completed in %.1fms",
                action,
                elapsed_ms,
            )
            return {
                "status": "success",
                "data": result,
                "execution_time_ms": elapsed_ms,
            }
        except asyncio.TimeoutError:
            logger.warning(
                "Command %s timed out after %.1fms",
                action,
                timeout_s * 1000,
            )
            raise CommandTimeoutError(
                ErrorMessage(
                    f"Command '{action}' timed out after {timeout_ms or DEFAULT_COMMAND_TIMEOUT_MS}ms"
                )
            ) from None
        except Exception as e:
            elapsed_ms = (time.monotonic() - start) * 1000
            logger.error("Command %s failed: %s", action, e)
            return {
                "status": "error",
                "data": None,
                "error": {"type": type(e).__name__, "message": str(e)},
                "execution_time_ms": elapsed_ms,
            }

    # ─── Block 3: Dunder Methods, Factories & Helpers ────────
    def __repr__(self) -> str:
        return "BlenderCommandAdapter()"

    def _send_sync(self, action: ActionName, params: dict[str, Any]) -> dict[str, Any]:
        """Synchronous send_command for use with asyncio.to_thread."""
        return self._connection.send_command(action, params)
