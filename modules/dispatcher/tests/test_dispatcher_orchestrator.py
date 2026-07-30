"""Tests for DispatcherOrchestrator — integration tests covering FR-DSP-001 through DSP-006.

Tests verify the orchestrator's full pipeline: register → discover → validate → dispatch → normalize.
"""

from __future__ import annotations

import pytest

from modules.dispatcher.src.agent_dispatcher_orchestrator import DispatcherOrchestrator
from modules.dispatcher.src.capabilities_action_discovery import ActionDiscoveryExecutor
from modules.dispatcher.src.capabilities_catalog_registration import CatalogRegistrationExecutor
from modules.dispatcher.src.capabilities_request_validation import RequestValidationExecutor
from modules.dispatcher.src.capabilities_result_normalization import ResultNormalizationExecutor
from modules.dispatcher.src.capabilities_sync_dispatch import SyncDispatchExecutor
from modules.shared.src.dispatcher.taxonomy_action_command_vo import ActionCommandVO
from modules.shared.src.dispatcher.taxonomy_action_metadata_vo import ActionMetadataVO
from modules.shared.src.dispatcher.taxonomy_discovery_outcome_vo import DiscoveryOutcomeVO
from modules.shared.src.dispatcher.taxonomy_unified_result_envelope_vo import UnifiedResultEnvelopeVO


def _make_mock_execute():
    """Create a mock execute callable for SyncDispatchExecutor."""

    class MockExecute:
        def execute_action(self, action_name: str, params: dict) -> dict:
            return {"dispatched_to": action_name, "params": params}

    return MockExecute()


def _make_orchestrator(
    catalog: dict | None = None,
    with_discovery: bool = False,
    with_validation: bool = False,
    with_dispatch: bool = False,
    with_normalization: bool = False,
) -> DispatcherOrchestrator:
    """Create a DispatcherOrchestrator with minimal required dependencies."""
    catalog_reg = CatalogRegistrationExecutor(catalog)
    discovery = ActionDiscoveryExecutor(catalog or {})
    validation = RequestValidationExecutor(catalog or {})
    dispatch = SyncDispatchExecutor(_make_mock_execute()) if with_dispatch else None
    normalization = ResultNormalizationExecutor() if with_normalization else None
    return DispatcherOrchestrator(
        catalog_registration=catalog_reg,
        action_discovery=discovery,
        request_validation=validation,
        sync_dispatch=dispatch,
        background_submit=None,
        result_normalization=normalization,
    )


def _make_metadata(
    action_name: str = "test_action",
    usage_examples: list[str] | None = None,
    **kwargs: object,
) -> ActionMetadataVO:
    """Create a minimal valid ActionMetadataVO."""
    defaults: dict[str, object] = {
        "owning_feature_ref": "test_feature",
        "description": "Test action",
        "parameter_schema": {"type": "object", "properties": {}, "required": []},
        "usage_examples": usage_examples or ["example usage"],
    }
    defaults.update(kwargs)
    return ActionMetadataVO(action_name=action_name, **defaults)  # type: ignore[arg-type]


# ─── FR-DSP-001: Registration via Orchestrator ──────────────────────────────


class TestRegistrationViaOrchestrator:
    """FR-DSP-001: Action registration through orchestrator."""

    def test_register_action_succeeds(self) -> None:
        """FR-DSP-001: Orchestrator delegates registration to catalog capability."""
        orch = _make_orchestrator()
        metadata = _make_metadata(action_name="reg_test")
        result = orch.register_action(metadata)
        assert result.action_name == "reg_test"
        assert result.catalog_version == 1

    def test_register_duplicate_increments_version(self) -> None:
        """FR-DSP-001: Duplicate registration increments catalog version."""
        orch = _make_orchestrator()
        metadata1 = _make_metadata(action_name="dup_via_orch")
        orch.register_action(metadata1)
        metadata2 = _make_metadata(action_name="dup_via_orch", description="updated")
        result = orch.register_action(metadata2)
        assert result.catalog_version == 2


# ─── FR-DSP-002: Discovery via Orchestrator ────────────────────────────────


class TestDiscoveryViaOrchestrator:
    """FR-DSP-002: Action discovery through orchestrator."""

    def test_discover_returns_all_actions(self) -> None:
        """FR-DSP-002: discover_actions returns all registered actions."""
        metadata = _make_metadata(action_name="discover_me")
        catalog = {"discover_me": metadata}
        orch = _make_orchestrator(catalog=catalog)
        result = orch.discover_actions()
        assert isinstance(result, DiscoveryOutcomeVO)

    def test_discover_with_name_filter(self) -> None:
        """FR-DSP-002: discover_actions respects name_filter."""
        catalog: dict = {}
        orch = _make_orchestrator(catalog=catalog)
        result = orch.discover_actions(name_filter="missing")
        assert isinstance(result, DiscoveryOutcomeVO)


# ─── FR-DSP-003: Validation via Orchestrator ──────────────────────────────


class TestValidationViaOrchestrator:
    """FR-DSP-003: Request validation through orchestrator."""

    def test_validate_known_action_succeeds(self) -> None:
        """FR-DSP-003: Known action passes validation."""
        catalog = {
            "valid": _make_metadata(
                action_name="valid",
                parameter_schema={"type": "object", "properties": {}, "required": []},
            ),
        }
        orch = _make_orchestrator(catalog=catalog)
        request = ActionCommandVO(action_name="valid")
        result = orch.validate_request(request)
        assert result.validated_tracking_id != ""

    def test_validate_unknown_action_raises(self) -> None:
        """FR-DSP-003: Unknown action raises DispatchError."""
        catalog: dict[str, ActionMetadataVO] = {}
        orch = _make_orchestrator(catalog=catalog)
        request = ActionCommandVO(action_name="unknown")
        with pytest.raises(Exception, match="Unknown action"):
            orch.validate_request(request)


# ─── FR-DSP-004: Sync Dispatch via Orchestrator ───────────────────────────


class TestSyncDispatchViaOrchestrator:
    """FR-DSP-004: Synchronous dispatch through orchestrator."""

    def test_sync_dispatch_returns_envelope(self) -> None:
        """FR-DSP-004: Sync dispatch returns a UnifiedResultEnvelopeVO."""
        catalog = {
            "sync_test": _make_metadata(
                action_name="sync_test",
                parameter_schema={"type": "object", "properties": {}, "required": []},
            ),
        }
        orch = _make_orchestrator(catalog=catalog, with_dispatch=True)
        request = ActionCommandVO(action_name="sync_test")
        validated = orch.validate_request(request)
        result = orch.dispatch_sync(validated)
        assert isinstance(result, UnifiedResultEnvelopeVO)
        assert result.success is True


# ─── FR-DSP-006: Result Normalization via Orchestrator ────────────────────


class TestNormalizationViaOrchestrator:
    """FR-DSP-006: Result normalization through orchestrator."""

    def test_normalize_success_envelope(self) -> None:
        """FR-DSP-006: Success result creates proper envelope."""
        orch = _make_orchestrator(with_normalization=True)
        raw = {"success": True, "data": {"result": "ok"}}
        result = orch.normalize_result(raw, "track-norm")
        assert isinstance(result, UnifiedResultEnvelopeVO)
        assert result.success is True

    def test_normalize_error_envelope(self) -> None:
        """FR-DSP-006: Error result creates proper envelope."""
        orch = _make_orchestrator(with_normalization=True)
        raw = {"success": False, "message": "fail"}
        result = orch.normalize_result(raw, "track-err")
        assert isinstance(result, UnifiedResultEnvelopeVO)
        assert result.success is False


# ─── FR-DSP-004/005: Full Pipeline via execute_action ─────────────────────


class TestFullPipeline:
    """Full dispatcher pipeline via execute_action facade (FR-DSP-004/005)."""

    def test_execute_action_unknown_returns_error(self) -> None:
        """FR-DSP-003: Unknown action in pipeline returns error envelope."""
        orch = _make_orchestrator(with_dispatch=True)
        request = ActionCommandVO(action_name="unknown")
        result = orch.execute_action(request)
        assert isinstance(result, UnifiedResultEnvelopeVO)
        assert result.success is False

    def test_execute_action_missing_dispatch_returns_error(self) -> None:
        """FR-DSP-004: Orchestrator without dispatch returns error for execution."""
        catalog = {
            "test": _make_metadata(
                action_name="test",
                parameter_schema={"type": "object", "properties": {}, "required": []},
            ),
        }
        orch = _make_orchestrator(catalog=catalog)
        request = ActionCommandVO(action_name="test")
        validated = orch.validate_request(request)
        with pytest.raises(RuntimeError, match="SyncDispatchProtocol not configured"):
            orch.dispatch_sync(validated)

    def test_execute_action_with_exception_handled(self) -> None:
        """FR-DSP-006: Exceptions during execution produce error envelope."""
        catalog = {
            "failing": _make_metadata(
                action_name="failing",
                parameter_schema={"type": "object", "properties": {}, "required": []},
            ),
        }

        class FailingExecute:
            def execute_action(self, action_name: str, params: dict) -> None:  # noqa: ARG002
                raise RuntimeError("boom")

        catalog_reg = CatalogRegistrationExecutor(catalog)
        discovery = ActionDiscoveryExecutor(catalog)
        validation = RequestValidationExecutor(catalog)
        dispatch = SyncDispatchExecutor(execute_action=FailingExecute())
        orch = DispatcherOrchestrator(
            catalog_registration=catalog_reg,
            action_discovery=discovery,
            request_validation=validation,
            sync_dispatch=dispatch,
        )
        request = ActionCommandVO(action_name="failing")
        validated = orch.validate_request(request)
        result = orch.dispatch_sync(validated)
        assert isinstance(result, UnifiedResultEnvelopeVO)
        assert result.success is False
