"""Tests for catalog registration capability — FR-DSP-001.

FR-DSP-001: Register Action Catalog
- Domain features register actions; dispatcher owns the catalog
- Validates schema integrity before acceptance
- Rejects or replaces duplicates per configured policy
- Exposes deterministic ordering and catalog version
"""

from __future__ import annotations

import pytest

from modules.dispatcher.src.capabilities_catalog_registration import (
    CatalogRegistrationExecutor,
)
from modules.shared.src.dispatcher.taxonomy_action_metadata_vo import ActionMetadataVO


def _make_metadata(
    action_name: str = "test_action",
    parameter_schema: dict | None = None,
    **kwargs: object,
) -> ActionMetadataVO:
    """Create a minimal valid ActionMetadataVO for testing."""
    defaults: dict[str, object] = {
        "owning_feature_ref": "test_feature",
        "description": "Test action",
        "parameter_schema": parameter_schema or {"type": "object", "properties": {}, "required": []},
        "usage_examples": [],
    }
    defaults.update(kwargs)
    return ActionMetadataVO(action_name=action_name, **defaults)  # type: ignore[arg-type]


# ─── FR-DSP-001: Schema Validation ──────────────────────────────────────────


class TestSchemaValidation:
    """Schema integrity validation per FR-DSP-001."""

    def test_valid_schema_accepted(self) -> None:
        """FR-DSP-001: Valid schema is accepted and registered."""
        executor = CatalogRegistrationExecutor()
        metadata = _make_metadata(
            action_name="valid_action",
            parameter_schema={
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            },
        )
        result = executor.register_action(metadata)
        assert result.action_name == "valid_action"
        assert result.catalog_version == 1

    def test_missing_type_or_properties_rejected(self) -> None:
        """FR-DSP-001: Schema without type or properties is rejected."""
        executor = CatalogRegistrationExecutor()
        metadata = _make_metadata(
            action_name="bad_schema",
            parameter_schema={"format": "json"},
        )
        with pytest.raises(ValueError, match="must declare 'type' or 'properties'"):
            executor.register_action(metadata)

    def test_non_dict_schema_rejected(self) -> None:
        """FR-DSP-001: Non-dict schema is rejected."""
        executor = CatalogRegistrationExecutor()
        metadata = _make_metadata(
            action_name="non_dict",
            parameter_schema="string_schema",  # type: ignore
        )
        with pytest.raises(ValueError, match="must be a dict"):
            executor.register_action(metadata)

    def test_properties_not_dict_rejected(self) -> None:
        """FR-DSP-001: Schema with non-dict properties is rejected."""
        executor = CatalogRegistrationExecutor()
        metadata = _make_metadata(
            action_name="bad_props",
            parameter_schema={"type": "object", "properties": "not_a_dict"},  # type: ignore
        )
        with pytest.raises(ValueError, match="'properties' must be a dict"):
            executor.register_action(metadata)

    def test_field_without_type_rejected(self) -> None:
        """FR-DSP-001: Schema property without 'type' is rejected."""
        executor = CatalogRegistrationExecutor()
        metadata = _make_metadata(
            action_name="no_type_field",
            parameter_schema={"type": "object", "properties": {"field": {"default": 1}}},
        )
        with pytest.raises(ValueError, match="must declare a 'type'"):
            executor.register_action(metadata)

    def test_required_not_in_properties_rejected(self) -> None:
        """FR-DSP-001: Required field not declared in properties is rejected."""
        executor = CatalogRegistrationExecutor()
        metadata = _make_metadata(
            action_name="orphan_required",
            parameter_schema={
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["missing_field"],
            },
        )
        with pytest.raises(ValueError, match="is not declared in 'properties'"):
            executor.register_action(metadata)

    def test_required_not_list_rejected(self) -> None:
        """FR-DSP-001: Non-list required is rejected."""
        executor = CatalogRegistrationExecutor()
        metadata = _make_metadata(
            action_name="bad_required",
            parameter_schema={"type": "object", "properties": {}, "required": "string"},  # type: ignore
        )
        with pytest.raises(ValueError, match="must be a list"):
            executor.register_action(metadata)


# ─── FR-DSP-001: Duplicate Handling ─────────────────────────────────────────


class TestDuplicateHandling:
    """Duplicate registration per FR-DSP-001."""

    def test_first_registration_succeeds(self) -> None:
        """FR-DSP-001: First registration sets version to 1."""
        executor = CatalogRegistrationExecutor()
        metadata = _make_metadata(action_name="dup_test")
        result = executor.register_action(metadata)
        assert result.catalog_version == 1

    def test_duplicate_replacement_increments_version(self) -> None:
        """FR-DSP-001: Duplicate registration replaces and increments version."""
        executor = CatalogRegistrationExecutor()
        metadata1 = _make_metadata(action_name="dup_test")
        result1 = executor.register_action(metadata1)
        assert result1.catalog_version == 1

        metadata2 = _make_metadata(
            action_name="dup_test",
            description="Updated description",
        )
        result2 = executor.register_action(metadata2)
        assert result2.catalog_version == 2
        assert result2.description == "Updated description"

    def test_multiple_unique_registrations(self) -> None:
        """FR-DSP-001: Multiple unique actions each increment version."""
        executor = CatalogRegistrationExecutor()
        for i in range(5):
            metadata = _make_metadata(action_name=f"action_{i}")
            result = executor.register_action(metadata)
            assert result.catalog_version == i + 1


# ─── FR-DSP-001: Catalog Ordering ──────────────────────────────────────────


class TestCatalogOrdering:
    """Deterministic ordering per FR-DSP-001."""

    def test_catalog_sorted_by_name(self) -> None:
        """FR-DSP-001: get_catalog returns actions sorted by action name."""
        executor = CatalogRegistrationExecutor()
        for name in ["zulu", "alpha", "bravo"]:
            metadata = _make_metadata(action_name=name)
            executor.register_action(metadata)

        catalog = executor.get_catalog()
        names = list(catalog.keys())
        assert names == sorted(names)
        assert len(names) == 3

    def test_get_action_returns_registered(self) -> None:
        """FR-DSP-001: get_action returns the registered metadata."""
        executor = CatalogRegistrationExecutor()
        metadata = _make_metadata(action_name="find_me")
        executor.register_action(metadata)

        found = executor.get_action("find_me")
        assert found is not None
        assert found.action_name == "find_me"

    def test_get_action_missing_returns_none(self) -> None:
        """FR-DSP-001: get_action returns None for unregistered action."""
        executor = CatalogRegistrationExecutor()
        assert executor.get_action("missing") is None
