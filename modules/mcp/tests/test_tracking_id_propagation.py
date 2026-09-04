from __future__ import annotations

import pytest

from modules.shared.src.mcp.capabilities_response_formatter import McpResponseImpl


@pytest.mark.asyncio
async def test_formatter_preserves_upstream_tracking_id() -> None:
    formatter = McpResponseImpl()

    response = await formatter.format_response(
        {"tracking_id": "track-mcp-001", "value": "ok"},
        tool_name="execute_command",
        tracking_id="",
    )

    assert response["tracking_id"] == "track-mcp-001"  # nosec B101


@pytest.mark.asyncio
async def test_formatter_preserves_tracking_id_when_truncating() -> None:
    formatter = McpResponseImpl(max_size=128)

    response = await formatter.format_response(
        {"tracking_id": "track-mcp-002", "payload": "x" * 10_000},
        tool_name="execute_command",
        tracking_id="",
    )

    assert response["tracking_id"] == "track-mcp-002"  # nosec B101
    assert response["data"]["truncated"] is True  # nosec B101
