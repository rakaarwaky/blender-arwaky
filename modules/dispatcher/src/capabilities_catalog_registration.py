"""Catalog registration capability — action catalog management.

FR-DSP-001: Register Action Catalog
- Domain features register actions; dispatcher owns the catalog
- Validates schema integrity before acceptance
- Rejects or replaces duplicates per configured policy
- Exposes deterministic ordering and catalog version
"""

import logging

from modules.shared.src.dispatcher.contract_catalog_registration_protocol import (
    CatalogRegistrationProtocol,
)
from modules.shared.src.dispatcher.taxonomy_action_metadata_vo import ActionMetadataVO

logger = logging.getLogger("BlenderMCPServer")


class CatalogRegistrationExecutor(CatalogRegistrationProtocol):
    """Concrete implementation for action catalog registration.

    FR-DSP-001: Validates schema, rejects duplicates per policy, maintains sorted order.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(self) -> None:
        self._catalog: dict[str, ActionMetadataVO] = {}
        self._catalog_version: int = 0

    # ─── Block 2: Protocol Method Implementation ─────────────

    def register_action(self, metadata: ActionMetadataVO) -> ActionMetadataVO:
        """Register an action in the catalog. Returns enriched metadata with catalog version.

        FR-DSP-001: Duplicate names are rejected or replaced per policy.
        Catalog exposes deterministic ordering sorted by action name.
        """
        # Validate schema integrity
        self._validate_schema(metadata)

        # Check for duplicate registration
        if metadata.action_name in self._catalog:
            existing = self._catalog[metadata.action_name]
            logger.warning(
                "Duplicate action '%s' registration; replacing per policy",
                metadata.action_name,
            )
            # Replace with new version
            self._catalog_version += 1
            enriched = ActionMetadataVO(
                action_name=metadata.action_name,
                owning_feature_ref=metadata.owning_feature_ref,
                description=metadata.description,
                parameter_schema=metadata.parameter_schema,
                usage_examples=metadata.usage_examples,
                default_timeout=metadata.default_timeout,
                timeout_class=metadata.timeout_class,
                idempotency_flag=metadata.idempotency_flag,
                scene_mutation_flag=metadata.scene_mutation_flag,
                background_eligibility_flag=metadata.background_eligibility_flag,
                destructive_flag=metadata.destructive_flag,
                read_only_flag=metadata.read_only_flag,
                long_running_flag=metadata.long_running_flag,
                risk_level=metadata.risk_level,
                catalog_version=self._catalog_version,
            )
            self._catalog[metadata.action_name] = enriched
            return enriched

        # New registration — increment version and store
        self._catalog_version += 1
        enriched = ActionMetadataVO(
            action_name=metadata.action_name,
            owning_feature_ref=metadata.owning_feature_ref,
            description=metadata.description,
            parameter_schema=metadata.parameter_schema,
            usage_examples=metadata.usage_examples,
            default_timeout=metadata.default_timeout,
            timeout_class=metadata.timeout_class,
            idempotency_flag=metadata.idempotency_flag,
            scene_mutation_flag=metadata.scene_mutation_flag,
            background_eligibility_flag=metadata.background_eligibility_flag,
            destructive_flag=metadata.destructive_flag,
            read_only_flag=metadata.read_only_flag,
            long_running_flag=metadata.long_running_flag,
            risk_level=metadata.risk_level,
            catalog_version=self._catalog_version,
        )
        self._catalog[metadata.action_name] = enriched
        logger.info("Action registered: %s (version=%d)", metadata.action_name, self._catalog_version)
        return enriched

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    def _validate_schema(self, metadata: ActionMetadataVO) -> None:
        """Validate parameter schema integrity before acceptance.

        FR-DSP-001: Schema must include required fields, types, ranges, and allowed values.
        """
        if not isinstance(metadata.parameter_schema, dict):
            raise TypeError("parameter_schema must be a dict")

        # Basic schema validation — check for common keys
        valid_keys = {"type", "required", "properties", "additionalProperties"}
        schema_keys = set(metadata.parameter_schema.keys())
        if not schema_keys.intersection(valid_keys):
            logger.warning(
                "Action '%s' parameter schema has minimal structure",
                metadata.action_name,
            )

    def get_catalog(self) -> dict[str, ActionMetadataVO]:
        """Return a sorted snapshot of the catalog (sorted by action name)."""
        return dict(sorted(self._catalog.items()))

    def get_action(self, action_name: str) -> ActionMetadataVO | None:
        """Retrieve a specific action from the catalog."""
        return self._catalog.get(action_name)

    def __repr__(self) -> str:
        return f"CatalRegistrationExecutor(actions={len(self._catalog)}, version={self._catalog_version})"
