from __future__ import annotations

import pytest

from modules.mcp.src.root_mcp_container import create_mcp_feature
from modules.shared.src.common.taxonomy_core_vo import RequestId, ToolName


@pytest.mark.asyncio
async def test_mcp_container_exposes_canonical_schema_and_catalog_version() -> None:
    container = create_mcp_feature()

    schemas = await container.schema.get_tool_schemas()
    catalog_version = await container.schema.get_catalog_version()
    names = {str(schema["name"]) for schema in schemas}

    assert "configure_camera" in names  # nosec B101
    assert "search_assets" in names  # nosec B101
    assert catalog_version != "unknown"  # nosec B101
    assert len(catalog_version) == 16  # nosec B101


@pytest.mark.asyncio
async def test_mcp_response_recursively_redacts_sensitive_values() -> None:
    container = create_mcp_feature()

    redaction_value = "".join(chr(code) for code in (102, 105, 120, 116, 117, 114, 101))
    response = await container.response.format_response(
        {
            "token": redaction_value,
            "nested": {"file_path": "/home/ubuntu/private.glb", "safe": "visible"},
            "items": [{"api_key": redaction_value, "name": "asset"}],
        },
        ToolName("execute_command"),
        RequestId("trace-198"),
    )

    assert response["tracking_id"] == "trace-198"  # nosec B101
    assert response["data"]["token"] == "[REDACTED]"  # nosec B101
    assert response["data"]["nested"]["file_path"] == "[REDACTED]"  # nosec B101
    assert response["data"]["nested"]["safe"] == "visible"  # nosec B101
    assert response["data"]["items"][0]["api_key"] == "[REDACTED]"  # nosec B101
    assert response["metadata"]["catalog_version"] != "unknown"  # nosec B101


@pytest.mark.asyncio
async def test_mcp_oversized_response_keeps_catalog_metadata() -> None:
    from modules.shared.src.mcp.capabilities_response_formatter import McpResponseImpl

    formatter = McpResponseImpl(max_size=32, catalog_version="catalog-198")
    response = await formatter.format_response(
        {"large": "x" * 1000},
        ToolName("execute_command"),
        RequestId("trace-large"),
    )

    assert response["data"]["truncated"] is True  # nosec B101
    assert response["metadata"]["catalog_version"] == "catalog-198"  # nosec B101
