"""MCP schema exposure backed by the canonical dispatcher catalog."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from modules.shared.src.dispatcher.taxonomy_dispatcher_constant import DISPATCHER_ACTION_SCHEMAS
from modules.shared.src.mcp.contract_mcp_protocol import McpSchemaProtocol


class McpSchemaImpl(McpSchemaProtocol):
    """Expose deterministic MCP tool schemas without executing domain actions."""

    def __init__(self, catalog: dict[str, dict[str, dict[str, object]]] | None = None) -> None:
        self._catalog = catalog if catalog is not None else DISPATCHER_ACTION_SCHEMAS

    async def get_tool_schemas(self) -> list[dict[str, Any]]:
        schemas: list[dict[str, Any]] = []
        for owner, actions in sorted(self._catalog.items()):
            for action_name, raw_spec in sorted(actions.items()):
                parameters = raw_spec.get("parameters", {})
                normalized_parameters = self._normalize_parameters(parameters if isinstance(parameters, dict) else {})
                schemas.append(
                    {
                        "name": action_name,
                        "description": str(raw_spec.get("description", action_name)),
                        "inputSchema": {
                            "type": "object",
                            "properties": normalized_parameters["properties"],
                            "required": normalized_parameters["required"],
                            "additionalProperties": False,
                        },
                        "owner": owner,
                        "availability": {"status": "executable", "degraded": False},
                        "metadata": {
                            "catalog_version": await self.get_catalog_version(),
                            "example": f"{action_name}(...)",
                        },
                    }
                )
        return schemas

    @staticmethod
    def _normalize_parameters(parameters: dict[str, object]) -> dict[str, object]:
        properties: dict[str, dict[str, object]] = {}
        required: list[str] = []
        for name, raw_spec in parameters.items():
            spec = dict(raw_spec) if isinstance(raw_spec, dict) else {}
            declared_type = spec.get("type")
            if declared_type == "array[number]":
                spec["type"] = "array"
                spec["items"] = {"type": "number"}
            elif declared_type == "array[string]":
                spec["type"] = "array"
                spec["items"] = {"type": "string"}
            elif declared_type == "any":
                spec.pop("type", None)
            properties[str(name)] = spec
            if bool(spec.get("required")):
                required.append(str(name))
            spec.pop("required", None)
        return {"properties": properties, "required": required}

    def catalog_version(self) -> str:
        canonical = json.dumps(self._catalog, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
        return hashlib.sha256(canonical).hexdigest()[:16]

    async def get_catalog_version(self) -> str:
        return self.catalog_version()

    def __repr__(self) -> str:
        return "McpSchemaImpl()"
