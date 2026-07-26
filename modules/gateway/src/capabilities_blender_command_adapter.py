"""Capability: Blender command dispatch with timeout enforcement.

Implements IBlenderCommandProtocol — dispatches named commands to the
Blender addon via asyncio stream with configurable timeout, command
catalog validation, and response truncation per FR-SRV-003 (v2.0.0).
No queue management — that's owned by the Agent layer orchestrator.
"""

from __future__ import annotations

import asyncio
import logging
import time

from modules.gateway.src import (
    CommandDispatched,
    CommandResult,
    CommandTimeoutError,
    IBlenderCommandProtocol,
    IBlenderConnectionProtocol,
    IEventPublisher,
    ProviderError,
    ValidationError,
    effective_command_timeout_ms,
    get_command_spec,
)

logger = logging.getLogger("BlenderMCPServer")


class BlenderCommandAdapter(IBlenderCommandProtocol):
    """Command dispatch capability for Blender TCP/stdio operations.

    Implements FR-SRV-003 (v2.0.0): dispatches named commands with
    catalog-driven validation, timeout enforcement, and response
    truncation. No queue management — queued by orchestrator.
    """

    def __init__(
        self,
        connection_port: IBlenderConnectionProtocol,
        event_publisher: IEventPublisher,
        max_command_response_bytes: int = 1_048_576,  # 1 MB
    ) -> None:
        """Initialize command adapter.

        Args:
            connection_port: The connection protocol for sending commands.
            event_publisher: Event bus for emitting command events.
            max_command_response_bytes: Maximum response size before truncation.
        """
        self._connection = connection_port
        self._event_publisher = event_publisher
        self._max_response_bytes = max_command_response_bytes

    async def send_command(
        self,
        action: str,
        params: dict | None = None,
        timeout_ms: float | None = None,
        request_id: str | None = None,
    ) -> CommandResult:
        """Dispatch a named command to Blender addon.

        Validates command against catalog, sends via connection protocol,
        enforces timeout, and truncates oversized responses.

        Args:
            action: Named action to dispatch.
            params: Optional command arguments.
            timeout_ms: Override timeout in milliseconds. Uses catalog default if None.
            request_id: Optional tracking ID.

        Returns:
            CommandResult with status, data, and timing.

        Raises:
            ValidationError: If command is unknown or params are invalid.
            CommandTimeoutError: If response exceeds configured timeout.
            ProviderError: If Blender addon returns a failure.
        """
        # Validate command
        spec = get_command_spec(action)

        # Validate parameters
        from modules.gateway.src import validate_command_args
        try:
            validate_command_args(action, params)
        except ValidationError:
            raise

        # Calculate effective timeout
        effective_timeout = effective_command_timeout_ms(action, timeout_ms)
        timeout_s = effective_timeout / 1000.0

        start = time.monotonic()

        try:
            result = await asyncio.wait_for(
                self._connection.send_command(
                    action=action,
                    params=params,
                    request_id=request_id,
                    timeout_ms=effective_timeout,
                ),
                timeout=timeout_s,
            )
            elapsed_ms = (time.monotonic() - start) * 1000

            # Truncate oversized responses
            if result.data is not None:
                data_bytes = len(result.data.encode("utf-8")) if isinstance(result.data, str) else len(result.data)
                if data_bytes > self._max_response_bytes:
                    if isinstance(result.data, str):
                        result.data = result.data[:self._max_response_bytes] + "\n...[truncated]"
                    result.truncated = True

            logger.info(
                "Command %s completed in %.1fms",
                action, elapsed_ms,
            )

            # Emit event
            await self._event_publisher.publish(
                CommandDispatched(action=action, execution_time_ms=elapsed_ms)
            )

            return result

        except asyncio.TimeoutError:
            logger.warning(
                "Command %s timed out after %.1fms",
                action, timeout_s * 1000,
            )
            raise CommandTimeoutError(
                action=action,
                timeout_ms=effective_timeout,
            ) from None
        except ValidationError:
            raise
        except ProviderError:
            raise
        except Exception as e:
            elapsed_ms = (time.monotonic() - start) * 1000
            logger.error("Command %s failed: %s", action, e)
            raise ProviderError(
                message=f"Command '{action}' failed: {e}",
                details={"action": action},
            )
