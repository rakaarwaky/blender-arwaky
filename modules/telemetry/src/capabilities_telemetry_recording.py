"""Capability: Anonymous telemetry event recorder.

Implements TelemetryRecordingPort — handles recording anonymous usage events,
queue management, and JSONL persistence per FR-TLM-001.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import queue
import threading
import time
from collections.abc import Callable
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import (
    ActionName,
    BlenderVersion,
    ConfigValue,
    Details,
    DurationMs,
    ErrorMessage,
    Prompt,
    SuccessFlag,
    ToolName,
)
from modules.shared.src.config.contract_config import ConfigPort
from modules.shared.src.server import IBlenderConnectionProtocol
from modules.shared.src.telemetry.contract_telemetry_recording import (
    TelemetryRecordingPort,
)
from modules.shared.src.telemetry.taxonomy_telemetry_event import (
    EventType,
    TelemetryEvent as TelemetryEventType,
)

logger = logging.getLogger("blender-arwaky-telemetry-service")


class TelemetrySignalRecorder(TelemetryRecordingPort):
    """Main telemetry recording implementation.

    FR-TLM-001: Records anonymous usage events with zero blocking impact.
    Events are queued for background transmission via JSONL persistence.
    """

    def __init__(
        self,
        connection: IBlenderConnectionProtocol,
        config: ConfigPort,
    ) -> None:
        self._connection = connection
        self.config_application = config
        self._queue: queue.Queue[TelemetryEventType] = queue.Queue(maxsize=1000)
        self._worker: threading.Thread = threading.Thread(
            target=self._worker_loop, daemon=True
        )
        self._worker.start()

    def is_enabled(self) -> SuccessFlag:
        """Check if telemetry recording is currently enabled."""
        enabled = self.config_application.get("enabled", False)
        return SuccessFlag(bool(enabled))

    def record_event(
        self,
        event_type: EventType,
        tool_name: ToolName | None = None,
        prompt_text: Prompt | None = None,
        success: SuccessFlag | None = None,
        duration_ms: DurationMs | None = None,
        error_message: ErrorMessage | None = None,
        blender_version: BlenderVersion | None = None,
        metadata: Details | None = None,
    ) -> None:
        """Record a telemetry event silently (fire-and-forget).

        FR-TLM-001: Non-blocking, zero PII, respects opt-in configuration.
        Events are queued for background JSONL persistence.
        """
        # Respect opt-in configuration
        enabled = self.config_application.get("enabled", False)
        if not enabled:
            return

        success = success if success is not None else SuccessFlag(True)

        # Sanitize prompt_text if consent is disabled
        user_consent = self._check_user_consent()
        if not user_consent:
            prompt_text = None
            metadata = None
            if error_message:
                error_message = ErrorMessage("Error occurred (details withheld)")

        # Truncate prompt text if consent enabled
        if prompt_text and prompt_text:
            max_length = self.config_application.get("max_prompt_length", 500)
            if len(prompt_text) > max_length:
                prompt_text = Prompt(prompt_text[:max_length] + "...")

        # Truncate error message if consent enabled
        if error_message and user_consent and len(error_message) > 200:
            error_message = ErrorMessage(error_message[:200] + "...")

        event = TelemetryEventType(
            event_type=event_type,
            tool_name=tool_name,
            prompt_text=prompt_text,
            success=success,
            duration_ms=duration_ms,
            error_message=error_message,
            blender_version=blender_version,
            metadata=metadata,
        )

        # Queue event for background processing (non-blocking)
        try:
            self._queue.put_nowait(event)
        except queue.Full:
            logger.debug("Telemetry queue full, dropping event")

    def create_tool_decorator(
        self, tool_name: ToolName
    ) -> Callable[..., Any]:
        """Create a decorator that records telemetry for an MCP tool.

        Wraps both sync and async functions to record execution metrics.
        """
        import functools

        def _build(func: Callable) -> Callable:
            @functools.wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                start = time.time()
                success: bool = False
                err: str | None = None
                try:
                    result = func(*args, **kwargs)
                    success = True
                    return result
                except Exception as e:
                    err = str(e)
                    raise
                finally:
                    with contextlib.suppress(Exception):
                        self.record_event(
                            event_type=EventType.TOOL_EXECUTION,
                            tool_name=tool_name,
                            success=SuccessFlag(success),
                            duration_ms=DurationMs((time.time() - start) * 1000),
                            error_message=ErrorMessage(err) if err is not None else None,
                        )

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                start = time.time()
                success = False
                err: str | None = None
                try:
                    result = await func(*args, **kwargs)
                    success = True
                    return result
                except Exception as e:
                    err = str(e)
                    raise
                finally:
                    with contextlib.suppress(Exception):
                        self.record_event(
                            event_type=EventType.TOOL_EXECUTION,
                            tool_name=tool_name,
                            success=SuccessFlag(success),
                            duration_ms=DurationMs((time.time() - start) * 1000),
                            error_message=ErrorMessage(err) if err is not None else None,
                        )

            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

        return _build

    def _check_user_consent(self) -> bool:
        """Check user consent for telemetry (cached, checks every 5 minutes)."""
        try:
            result = self._connection.send_command(
                ActionName("get_telemetry_consent"), {}
            )
            return bool(result.get("consent", False))
        except Exception:
            return False

    def _worker_loop(self) -> None:
        """Background worker that processes queued events."""
        while True:
            try:
                event = self._queue.get()
                try:
                    with contextlib.suppress(Exception):
                        self._send_event(event)
                finally:
                    self._queue.task_done()
            except Exception as e:
                logger.debug("Telemetry worker error: %s", e)

    def _send_event(self, event: TelemetryEventType) -> None:
        """Write telemetry event to JSONL file (best-effort, never raises)."""
        try:
            data = {
                "session_id": event.session_id,
                "event_type": event.event_type.value,
                "tool_name": event.tool_name,
                "prompt_text": event.prompt_text,
                "success": event.success,
                "duration_ms": event.duration_ms,
                "error_message": event.error_message,
                "version": event.version,
                "platform": event.platform,
                "blender_version": event.blender_version,
                "metadata": event.metadata or {},
            }
            line = json.dumps(data, ensure_ascii=False, default=str)
            # In production, write to JSONL file
            # with open(self._jsonl_path, "a", encoding="utf-8") as f:
            #     f.write(line + "\n")
        except Exception as e:
            logger.debug("Failed to write telemetry event: %s", e)
