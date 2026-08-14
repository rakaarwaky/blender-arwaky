"""Bridge asynchronous audit emitters into synchronous launcher capabilities."""

from __future__ import annotations

import asyncio
import inspect


def emit_audit_sync(audit_events: object, event: object) -> None:
    """Deliver an audit event without leaking an un-awaited coroutine."""
    result = audit_events.emit_audit(event)
    if not inspect.isawaitable(result):
        return
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        asyncio.run(result)
    else:
        loop.create_task(result)
