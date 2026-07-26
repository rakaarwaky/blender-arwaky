"""TDD suite for FR-MCP-001 (Expose MCP Tools).

Exercises McpToolExposure by projecting an injected dispatcher catalog into
MCP tool schemas. Verifies the catalog stays the single source of truth.

RED → GREEN: targets McpToolExposureProtocol + McpToolExposure.
"""

from __future__ import annotations

from modules.mcp.src.capabilities_mcp_tool_exposure import McpToolExposure
from modules.shared.src.dispatcher.taxonomy_action_metadata_vo import ActionMetadataVO


def _catalog() -> list[ActionMetadataVO]:
    return [
        ActionMetadataVO(
            action_name="create_cube",
            owning_feature_ref="object",
            description="Create a cube primitive in the scene",
            parameter_schema={"size": {"type": "number"}},
            usage_examples=["create_cube size=2.0"],
            read_only_flag=False,
            catalog_version=3,
        ),
        ActionMetadataVO(
            action_name="get_scene_info",
            owning_feature_ref="scene",
            description="Read current scene overview",
            parameter_schema={},
            usage_examples=["get_scene_info"],
            read_only_flag=True,
            catalog_version=3,
        ),
    ]


def test_fr_mcp_001_exposes_all_catalog_actions():
    cap = McpToolExposure(catalog_source=_catalog)
    schemas = cap.expose_tool_schemas()
    assert len(schemas) == 2
    names = {s["name"] for s in schemas}
    assert names == {"create_cube", "get_scene_info"}


def test_fr_mcp_001_schema_derives_from_catalog_not_redefined():
    cap = McpToolExposure(catalog_source=_catalog)
    schema = cap.expose_tool("create_cube")
    assert schema is not None
    assert schema["description"] == "Create a cube primitive in the scene"
    assert schema["inputSchema"]["properties"] == {"size": {"type": "number"}}
    assert schema["examples"] == ["create_cube size=2.0"]
    # catalog metadata projected as capability indicators
    assert schema["x-owning-feature"] == "object"
    assert schema["x-read-only"] is False


def test_fr_mcp_001_expose_missing_tool_returns_none():
    cap = McpToolExposure(catalog_source=_catalog)
    assert cap.expose_tool("does_not_exist") is None


def test_fr_mcp_001_reports_catalog_version():
    cap = McpToolExposure(catalog_source=_catalog)
    assert cap.source_catalog_version() == 3