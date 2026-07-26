"""Action discovery capability — canonical catalog listing.

FR-DSP-002: Discover Actions
- Returns same canonical catalog to CLI and MCP consumers
- Supports filtering by name, category, capability
- Deterministic, case-consistent ordering
"""

import logging

from modules.shared.src.dispatcher.contract_action_discovery_protocol import (
    ActionDiscoveryProtocol,
)
from modules.shared.src.dispatcher.taxonomy_discovery_result_vo import DiscoveryResultVO

logger = logging.getLogger("BlenderMCPServer")


class ActionDiscoveryExecutor(ActionDiscoveryProtocol):
    """Concrete implementation for action discovery.

    FR-DSP-002: Returns canonical shape to all consumers with optional filtering.
    Filter matching nothing returns empty list, not error.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(self, catalog: dict[str, any] = None) -> None:
        self._catalog = catalog or {}

    # ─── Block 2: Protocol Method Implementation ─────────────

    def discover_actions(
        self,
        name_filter: str | None = None,
        capability_filter: str | None = None,
        detail_level: str = "standard",
    ) -> DiscoveryResultVO:
        """Discover actions from the catalog with optional filtering.

        FR-DSP-002: Returns canonical shape to all consumers.
        Filter matching nothing returns empty list, not error.
        """
        actions = list(self._catalog.values())

        if name_filter:
            actions = [a for a in actions if name_filter.lower() in str(a.action_name).lower()]

        if capability_filter:
            actions = [
                a
                for a in actions
                if capability_filter.lower() in str(a.owning_feature_ref).lower()
                or capability_filter.lower() in str(a.risk_level).lower()
            ]

        result = DiscoveryResultVO(
            actions=[self._format_action(a, detail_level) for a in actions],
            catalog_version=max(
                (a.catalog_version for a in self._catalog.values()), default=0
            ),
            result_count=len(actions),
        )

        logger.debug(
            "Discovery: %d actions returned (filter=%s)",
            len(actions),
            name_filter or "none",
        )
        return result

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    def _format_action(self, metadata: any, detail_level: str) -> dict[str, any]:
        """Format action metadata for discovery output."""
        base = {
            "action_name": metadata.action_name,
            "description": metadata.description,
            "owning_feature_ref": metadata.owning_feature_ref,
            "default_timeout": metadata.default_timeout,
            "timeout_class": metadata.timeout_class,
            "idempotency_flag": metadata.idempotency_flag,
            "scene_mutation_flag": metadata.scene_mutation_flag,
            "background_eligibility_flag": metadata.background_eligibility_flag,
            "destructive_flag": metadata.destructive_flag,
            "read_only_flag": metadata.read_only_flag,
            "long_running_flag": metadata.long_running_flag,
            "risk_level": metadata.risk_level,
            "degraded": metadata.degraded,
        }

        if detail_level == "full":
            base["parameter_schema"] = metadata.parameter_schema
            base["usage_examples"] = metadata.usage_examples

        return base

    def __repr__(self) -> str:
        return f"ActionDiscoveryExecutor(actions={len(self._catalog)})"
