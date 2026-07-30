"""Tests for request validation capability — FR-DSP-003.

FR-DSP-003: Validate Action Request
- Validates action name exists in catalog
- Validates parameters against registered schema (types, ranges, lengths, enums, size)
- Enforces execution-mode compatibility, destructive confirmation, timeout-override bounds
- Generates tracking ID when absent
- Does not mutate request or catalog state
"""

from __future__ import annotations

import pytest

from modules.dispatcher.src.capabilities_request_validation import (
    RequestValidationExecutor,
)
from modules.shared.src.dispatcher.taxonomy_action_command_vo import ActionCommandVO
from modules.shared.src.dispatcher.taxonomy_action_metadata_vo import ActionMetadataVO
from modules.shared.src.dispatcher.taxonomy_dispatch_error import DispatchError


def _make_catalog_entry(
    action_name: str = "test_action",
    background_eligible: bool = False,
    destructive: bool = False,
    parameter_schema: dict | None = None,
    **kwargs: object,
) -> ActionMetadataVO:
    """Create a minimal valid ActionMetadataVO for catalog."""
    defaults: dict[str, object] = {
        "owning_feature_ref": "test_feature",
        "description": "Test action",
        "parameter_schema": parameter_schema or {"type": "object", "properties": {}, "required": []},
        "usage_examples": [],
        "background_eligibility_flag": background_eligible,
        "destructive_flag": destructive,
    }
    defaults.update(kwargs)
    return ActionMetadataVO(action_name=action_name, **defaults)  # type: ignore[arg-type]


def _make_request(
    action_name: str = "test_action",
    parameters: dict | None = None,
    **kwargs: object,
) -> ActionCommandVO:
    """Create a minimal ActionCommandVO for testing."""
    defaults: dict[str, object] = {"action_name": action_name}
    if parameters is not None:
        defaults["parameters"] = parameters
    defaults.update(kwargs)
    return ActionCommandVO(**defaults)  # type: ignore[arg-type]


# ─── FR-DSP-003: Unknown Action ─────────────────────────────────────────────


class TestUnknownAction:
    """Unknown action validation per FR-DSP-003."""

    def test_unknown_action_raises_not_found(self) -> None:
        """FR-DSP-003: Unknown action produces not-found error."""
        executor = RequestValidationExecutor(catalog={})
        request = _make_request(action_name="unknown")
        with pytest.raises(DispatchError) as exc_info:
            executor.validate_request(request)
        assert exc_info.value.error_category == "not_found_error"


# ─── FR-DSP-003: Parameter Validation ──────────────────────────────────────


class TestParameterValidation:
    """Parameter validation per FR-DSP-003."""

    def test_required_parameter_missing(self) -> None:
        """FR-DSP-003: Missing required parameter raises error."""
        catalog = {
            "create_obj": _make_catalog_entry(
                action_name="create_obj",
                parameter_schema={
                    "type": "object",
                    "properties": {"name": {"type": "string"}},
                    "required": ["name"],
                },
            ),
        }
        executor = RequestValidationExecutor(catalog=catalog)
        request = _make_request(action_name="create_obj", parameters={})
        with pytest.raises(DispatchError, match="Missing required parameter"):
            executor.validate_request(request)

    def test_type_mismatch_raises_error(self) -> None:
        """FR-DSP-003: Wrong type raises field-level error."""
        catalog = {
            "set_val": _make_catalog_entry(
                action_name="set_val",
                parameter_schema={
                    "type": "object",
                    "properties": {"count": {"type": "integer"}},
                    "required": [],
                },
            ),
        }
        executor = RequestValidationExecutor(catalog=catalog)
        request = _make_request(action_name="set_val", parameters={"count": "string"})
        with pytest.raises(DispatchError, match="must be integer"):
            executor.validate_request(request)

    def test_value_below_minimum(self) -> None:
        """FR-DSP-003: Value below minimum raises error."""
        catalog = {
            "adjust": _make_catalog_entry(
                action_name="adjust",
                parameter_schema={
                    "type": "object",
                    "properties": {"value": {"type": "integer", "minimum": 0}},
                    "required": [],
                },
            ),
        }
        executor = RequestValidationExecutor(catalog=catalog)
        request = _make_request(action_name="adjust", parameters={"value": -1})
        with pytest.raises(DispatchError, match="below minimum"):
            executor.validate_request(request)

    def test_value_above_maximum(self) -> None:
        """FR-DSP-003: Value above maximum raises error."""
        catalog = {
            "adjust": _make_catalog_entry(
                action_name="adjust",
                parameter_schema={
                    "type": "object",
                    "properties": {"value": {"type": "integer", "maximum": 100}},
                    "required": [],
                },
            ),
        }
        executor = RequestValidationExecutor(catalog=catalog)
        request = _make_request(action_name="adjust", parameters={"value": 200})
        with pytest.raises(DispatchError, match="above maximum"):
            executor.validate_request(request)

    def test_string_below_min_length(self) -> None:
        """FR-DSP-003: String below minLength raises error."""
        catalog = {
            "name_input": _make_catalog_entry(
                action_name="name_input",
                parameter_schema={
                    "type": "object",
                    "properties": {"name": {"type": "string", "minLength": 5}},
                    "required": [],
                },
            ),
        }
        executor = RequestValidationExecutor(catalog=catalog)
        request = _make_request(action_name="name_input", parameters={"name": "ab"})
        with pytest.raises(DispatchError, match="below minLength"):
            executor.validate_request(request)

    def test_string_above_max_length(self) -> None:
        """FR-DSP-003: String above maxLength raises error."""
        catalog = {
            "name_input": _make_catalog_entry(
                action_name="name_input",
                parameter_schema={
                    "type": "object",
                    "properties": {"name": {"type": "string", "maxLength": 10}},
                    "required": [],
                },
            ),
        }
        executor = RequestValidationExecutor(catalog=catalog)
        request = _make_request(action_name="name_input", parameters={"name": "a" * 20})
        with pytest.raises(DispatchError, match="above maxLength"):
            executor.validate_request(request)

    def test_enum_value_violation(self) -> None:
        """FR-DSP-003: Enum value not in allowed set raises error."""
        catalog = {
            "mode_select": _make_catalog_entry(
                action_name="mode_select",
                parameter_schema={
                    "type": "object",
                    "properties": {"mode": {"type": "string", "enum": ["fast", "slow"]}},
                    "required": [],
                },
            ),
        }
        executor = RequestValidationExecutor(catalog=catalog)
        request = _make_request(action_name="mode_select", parameters={"mode": "ultra"})
        with pytest.raises(DispatchError, match="not in allowed set"):
            executor.validate_request(request)

    def test_payload_size_exceeded(self) -> None:
        """FR-DSP-003: Oversized payload raises error."""
        catalog = {
            "big_action": _make_catalog_entry(
                action_name="big_action",
                parameter_schema={
                    "type": "object",
                    "properties": {"data": {"type": "string"}},
                    "required": [],
                },
            ),
        }
        executor = RequestValidationExecutor(catalog=catalog, max_payload_size=10)
        request = _make_request(action_name="big_action", parameters={"data": "x" * 100})
        with pytest.raises(DispatchError, match="exceeds limit"):
            executor.validate_request(request)

    def test_strict_mode_rejects_unknown_params(self) -> None:
        """FR-DSP-003: Strict mode rejects unknown extra parameters."""
        catalog = {
            "limited": _make_catalog_entry(
                action_name="limited",
                parameter_schema={
                    "type": "object",
                    "properties": {"known": {"type": "string"}},
                    "required": [],
                },
            ),
        }
        executor = RequestValidationExecutor(catalog=catalog, unknown_parameter_policy="strict")
        request = _make_request(action_name="limited", parameters={"known": "ok", "extra": "bad"})
        with pytest.raises(DispatchError, match="Unknown extra parameters"):
            executor.validate_request(request)

    def test_tolerant_mode_ignores_unknown_params(self) -> None:
        """FR-DSP-003: Tolerant mode ignores unknown extra parameters."""
        catalog = {
            "limited": _make_catalog_entry(
                action_name="limited",
                parameter_schema={
                    "type": "object",
                    "properties": {"known": {"type": "string"}},
                    "required": [],
                },
            ),
        }
        executor = RequestValidationExecutor(catalog=catalog, unknown_parameter_policy="tolerant")
        request = _make_request(action_name="limited", parameters={"known": "ok", "extra": "bad"})
        result = executor.validate_request(request)
        assert len(result.validation_warnings) == 1


# ─── FR-DSP-003: Execution Mode Compatibility ──────────────────────────────


class TestExecutionMode:
    """Execution mode compatibility per FR-DSP-003."""

    def test_background_on_non_eligible_raises_error(self) -> None:
        """FR-DSP-003: Background mode on non-eligible action raises error."""
        catalog = {
            "sync_only": _make_catalog_entry(action_name="sync_only", background_eligible=False),
        }
        executor = RequestValidationExecutor(catalog=catalog)
        request = _make_request(action_name="sync_only", execution_mode="background")
        with pytest.raises(DispatchError, match="does not support background"):
            executor.validate_request(request)

    def test_background_on_eligible_succeeds(self) -> None:
        """FR-DSP-003: Background mode on eligible action succeeds."""
        catalog = {
            "bg_ok": _make_catalog_entry(action_name="bg_ok", background_eligible=True),
        }
        executor = RequestValidationExecutor(catalog=catalog)
        request = _make_request(action_name="bg_ok", execution_mode="background")
        result = executor.validate_request(request)
        assert result.resolved_metadata["background_eligibility_flag"] is True


# ─── FR-DSP-003: Destructive Confirmation ──────────────────────────────────


class TestDestructiveConfirmation:
    """Destructive confirmation enforcement per FR-DSP-003."""

    def test_destructive_without_confirmation_raises_error(self) -> None:
        """FR-DSP-003: Destructive action without confirmation raises error."""
        catalog = {
            "delete": _make_catalog_entry(action_name="delete", destructive=True),
        }
        executor = RequestValidationExecutor(catalog=catalog)
        request = _make_request(action_name="delete")
        with pytest.raises(DispatchError, match="requires explicit confirmation"):
            executor.validate_request(request)

    def test_destructive_with_confirmation_succeeds(self) -> None:
        """FR-DSP-003: Destructive action with confirmation succeeds."""
        catalog = {
            "delete": _make_catalog_entry(action_name="delete", destructive=True),
        }
        executor = RequestValidationExecutor(catalog=catalog)
        request = _make_request(action_name="delete", confirmation_flag=True)
        result = executor.validate_request(request)
        assert result.confirmation_flag is True


# ─── FR-DSP-003: Timeout Override Bounds ───────────────────────────────────


class TestTimeoutOverride:
    """Timeout override bounds per FR-DSP-003."""

    def test_negative_timeout_raises_error(self) -> None:
        """FR-DSP-003: Negative timeout override raises error."""
        catalog = {"action": _make_catalog_entry(action_name="action")}
        executor = RequestValidationExecutor(catalog=catalog)
        request = _make_request(action_name="action", timeout_override=-1.0)
        with pytest.raises(DispatchError, match="out of bounds"):
            executor.validate_request(request)

    def test_excessive_timeout_raises_error(self) -> None:
        """FR-DSP-003: Timeout exceeding max raises error."""
        catalog = {"action": _make_catalog_entry(action_name="action")}
        executor = RequestValidationExecutor(catalog=catalog, max_timeout_override=100.0)
        request = _make_request(action_name="action", timeout_override=200.0)
        with pytest.raises(DispatchError, match="out of bounds"):
            executor.validate_request(request)

    def test_valid_timeout_succeeds(self) -> None:
        """FR-DSP-003: Valid timeout override passes."""
        catalog = {"action": _make_catalog_entry(action_name="action")}
        executor = RequestValidationExecutor(catalog=catalog, max_timeout_override=3600.0)
        request = _make_request(action_name="action", timeout_override=60.0)
        result = executor.validate_request(request)
        assert result.timeout_override == 60.0


# ─── FR-DSP-003: Tracking ID Generation ────────────────────────────────────


class TestTrackingIdGeneration:
    """Tracking ID generation per FR-DSP-003."""

    def test_absent_tracking_id_auto_generated(self) -> None:
        """FR-DSP-003: Missing tracking ID is auto-generated."""
        catalog = {"action": _make_catalog_entry(action_name="action")}
        executor = RequestValidationExecutor(catalog=catalog)
        request = _make_request(action_name="action", tracking_id=None)
        result = executor.validate_request(request)
        assert result.validated_tracking_id != ""

    def test_present_tracking_id_preserved(self) -> None:
        """FR-DSP-003: Existing tracking ID is preserved."""
        catalog = {"action": _make_catalog_entry(action_name="action")}
        executor = RequestValidationExecutor(catalog=catalog)
        request = _make_request(action_name="action", tracking_id="my-id-123")
        result = executor.validate_request(request)
        assert result.validated_tracking_id == "my-id-123"


# ─── FR-DSP-003: No State Mutation ──────────────────────────────────────────


class TestNoStateMutation:
    """No mutation of request or catalog per FR-DSP-003."""

    def test_catalog_unchanged_after_validation(self) -> None:
        """FR-DSP-003: Validation does not mutate the catalog."""
        original_version = 1
        catalog = {
            "action": _make_catalog_entry(
                action_name="action",
                parameter_schema={"type": "object", "properties": {}, "required": []},
            ),
        }
        executor = RequestValidationExecutor(catalog=catalog)
        request = _make_request(action_name="action")
        executor.validate_request(request)
        assert len(executor._catalog) == original_version

    def test_request_unchanged_after_validation(self) -> None:
        """FR-DSP-003: Validation returns a new VO, not mutated input."""
        catalog = {
            "action": _make_catalog_entry(
                action_name="action",
                parameter_schema={"type": "object", "properties": {}, "required": []},
            ),
        }
        executor = RequestValidationExecutor(catalog=catalog)
        request = _make_request(action_name="action")
        result = executor.validate_request(request)
        assert result is not request
