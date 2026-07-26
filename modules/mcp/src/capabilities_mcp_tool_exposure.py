"""MCP tool exposure capability — renders dispatcher catalog as MCP tool schemas.

FR-MCP-001: Expose MCP Tools
- Publishes capabilities as MCP-compliant tool schemas
- The dispatcher action catalog is the single source of action semantics
- This capability renders the catalog; it never redefines action meaning

AES Capabilities layer — concrete implementation of McpToolExposureProtocol.
"""

from __future__ import annotations

import logging
from typing import Callable

from modules.shared.src.dispatcher.taxonomy_action_metadata_vo import ActionMetadataVO
from modules.shared.src.mcp.contract_mcp_tool_exposure_protocol import McpToolExposureProtocol

logger = logging.getLogger("BlenderMCPServer")


class McpToolExposure(McpToolExposureProtocol):
    """Concrete capability that projects the dispatcher catalog into MCP schemas.

    FR-MCP-001: The catalog source is injected so the capability is testable
    without a live dispatcher registry. Schemas are projected, not redefined.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(self, catalog_source: Callable[[], list[ActionMetadataVO]] | None = None) -> None:
        self._catalog_source = catalog_source or (lambda: [])

    # ─── Block 2: Protocol Method Implementation ─────────────

    def expose_tool_schemas(self) -> list[dict]:
        """Render every registered action as an MCP tool schema.

        FR-MCP-001: name, description, inputSchema, and examples all derive from
        the catalog. Order is preserved from the catalog source.
        """
        return [self._project(action) for action in self._catalog_source()]

    def expose_tool(self, action_name: str) -> dict | None:
        """Render a single action as an MCP tool schema, or None if absent."""
        for action in self._catalog_source():
            if action.action_name == action_name:
                return self._project(action)
        return None

    def source_catalog_version(self) -> int:
        """Return the catalog version this exposure was rendered from (max seen)."""
        actions = self._catalog_source()
        if not actions:
            return 0
        return max(a.catalog_version for a in actions)

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    @staticmethod
    def _project(action: ActionMetadataVO) -> dict:
        """Project a catalog entry into an MCP tool schema (no redefinition)."""
        return {
            "name": action.action_name,
            "description": action.description,
            "inputSchema": {
                "type": "object",
                "properties": action.parameter_schema,
            },
            "examples": list(action.usage_examples),
            "x-owning-feature": action.owning_feature_ref,
            "x-read-only": action.read_only_flag,
            "x-destructive": action.destructive_flag,
            "x-background-eligible": action.background_eligibility_flag,
            "x-risk-level": action.risk_level,
        }

    def __repr__(self) -> str:
        return f"McpToolExposure(catalog_size={len(self._catalog_source())})"