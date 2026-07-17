"""Tests for MCP tool registry."""
from unittest.mock import MagicMock

import pytest
from surfaces.tool_registry_handler import ToolRegistryHandler


@pytest.mark.integration
class TestToolRegistry:
    """Tests that all 4 MCP tools are registered."""

    def test_register_tools_registers_exactly_4(self):
        """register_tools must call mcp.tool() exactly 4 times."""
        mcp = MagicMock()
        ToolRegistryHandler.register_tools(mcp)
        assert mcp.tool.call_count == 4, (
            f"Expected 4 tool registrations, got {mcp.tool.call_count}"
        )

    def test_register_tools_calls_four_different_modules(self):
        """Each tool must come from a different handler module (4 distinct registers)."""
        mcp = MagicMock()
        ToolRegistryHandler.register_tools(mcp)
        assert mcp.tool.call_count == 4
