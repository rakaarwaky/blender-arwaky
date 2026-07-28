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


def _make_metadata(
    action_name: str = "test_action",
    **kwargs: object,
) -> ActionMetadataVO:
    """Create a minimal valid ActionMetadataVO."""
    defaults: dict[str, object] = {
        "owning_feature_ref": "test_feature",
        "description": "Test action",
        "parameter_schema": {"type": "object", "properties": {}, "required": []},
        "usage_examples": [],
    }
    defaults.update(kwargs)
    return ActionMetadataVO(action_name=action_name, **defaults)  # type: ignore[arg-type]


# ─── FR-DSP-001: Registration via Orchestrator ──────────────────────────────


class TestRegistrationViaOrchestrator:
    """FR-DSP-001: Action registration through orchestrator."""

    def test_register_action_succeeds(self) -> None:
        """FR-DSP-001: Orchestrator delegates registration to catalog capability."""
        catalog = CatalogRegistrationExecutor()
        orchestrator = DispatcherOrchestrator(catalog_registration=catalog)
        metadata = _make_metadata(action_name="reg_test")
        result = orchestrator.register_action(metadata)
        assert result.action_name == "reg_test"
        assert result.catalog_version == 1

    def test_register_duplicate_increments_version(self) -> None:
        """FR-DSP-001: Duplicate registration increments catalog version."""
        catalog = CatalogRegistrationExecutor()
        orchestrator = DispatcherOrchestrator(catalog_registration=catalog)
        metadata1 = _make_metadata(action_name="dup_via_orch")
        orchestrator.register_action(metadata1)
        metadata2 = _make_metadata(action_name="dup_via_orch", description="updated")
        result = orchestrator.register_action(metadata2)
        assert result.catalog_version == 2


# ─── FR-DSP-002: Discovery via Orchestrator ────────────────────────────────


class TestDiscoveryViaOrchestrator:
    """FR-DSP-002: Action discovery through orchestrator."""

    def test_discover_returns_all_actions(self) -> None:
        """FR-DSP-002: discover_actions returns all registered actions."""
        catalog = CatalogRegistrationExecutor()
        discovery = ActionDiscoveryExecutor(catalog={})
        orchestrator = DispatcherOrchestrator(
            catalog_registration=catalog,
            action_discovery=discovery,
        )
        metadata = _make_metadata(action_name="discover_me")
        catalog.register_action(metadata)
        discovery._catalog = catalog._catalog  # Share catalog state
        result = orchestrator.discover_actions()
        assert isinstance(result, DiscoveryOutcomeVO)

    def test_discover_with_name_filter(self) -> None:
        """FR-DSP-002: discover_actions respects name_filter."""
        catalog = CatalogRegistrationExecutor()
        discovery = ActionDiscoveryExecutor(catalog={})
        orchestrator = DispatcherOrchestrator(
            catalog_registration=catalog,
            action_discovery=discovery,
        )
        result = orchestrator.discover_actions(name_filter="missing")
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
        validation = RequestValidationExecutor(catalog=catalog)
        orchestrator = DispatcherOrchestrator(request_validation=validation)
        request = ActionCommandVO(action_name="valid")
        result = orchestrator.validate_request(request)
        assert result.validated_tracking_id != ""

    def test_validate_unknown_action_raises(self) -> None:
        """FR-DSP-003: Unknown action raises DispatchRequestError."""
        catalog: dict[str, ActionMetadataVO] = {}
        validation = RequestValidationExecutor(catalog=catalog)
        orchestrator = DispatcherOrchestrator(request_validation=validation)
        request = ActionCommandVO(action_name="unknown")
        with pytest.raises(Exception, match="Unknown action"):
            orchestrator.validate_request(request)


# ─── FR-DSP-004: Sync Dispatch via Orchestrator ───────────────────────────


class TestSyncDispatchViaOrchestrator:
    """FR-DSP-004: Synchronous dispatch through orchestrator."""

    def test_sync_dispatch_returns_envelope(self) -> None:
        """FR-DSP-004: Sync dispatch returns a UnifiedResultEnvelopeVO."""
        mock = _make_mock_execute()
        catalog = {
            "sync_test": _make_metadata(
                action_name="sync_test",
                parameter_schema={"type": "object", "properties": {}, "required": []},
            ),
        }
        validation = RequestValidationExecutor(catalog=catalog)
        sync = SyncDispatchExecutor(execute_action=mock)
        orchestrator = DispatcherOrchestrator(
            request_validation=validation,
            sync_dispatch=sync,
        )
        request = ActionCommandVO(action_name="sync_test")
        validated = orchestrator.validate_request(request)
        result = orchestrator.dispatch_sync(validated)
        assert isinstance(result, UnifiedResultEnvelopeVO)
        assert result.success is True


# ─── FR-DSP-006: Result Normalization via Orchestrator ────────────────────


class TestNormalizationViaOrchestrator:
    """FR-DSP-006: Result normalization through orchestrator."""

    def test_normalize_success_envelope(self) -> None:
        """FR-DSP-006: Success result creates proper envelope."""
        normalization = ResultNormalizationExecutor()
        orchestrator = DispatcherOrchestrator(result_normalization=normalization)
        raw = {"success": True, "data": {"result": "ok"}}
        result = orchestrator.normalize_result(raw, "track-norm")
        assert isinstance(result, UnifiedResultEnvelopeVO)
        assert result.success is True

    def test_normalize_error_envelope(self) -> None:
        """FR-DSP-006: Error result creates proper envelope."""
        normalization = ResultNormalizationExecutor()
        orchestrator = DispatcherOrchestrator(result_normalization=normalization)
        raw = {"success": False, "message": "fail"}
        result = orchestrator.normalize_result(raw, "track-err")
        assert isinstance(result, UnifiedResultEnvelopeVO)
        assert result.success is False


# ─── FR-DSP-004/005: Full Pipeline via execute_action ─────────────────────


class TestFullPipeline:
    """Full dispatcher pipeline via execute_action facade (FR-DSP-004/005)."""

    def test_execute_action_unknown_raises(self) -> None:
        """FR-DSP-003: Unknown action in pipeline returns error envelope."""
        validation = RequestValidationExecutor(catalog={})
        normalization = ResultNormalizationExecutor()
        orchestrator = DispatcherOrchestrator(
            request_validation=validation,
            result_normalization=normalization,
        )
        result = orchestrator.execute_action("unknown", {})
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
        validation = RequestValidationExecutor(catalog=catalog)
        normalization = ResultNormalizationExecutor()
        orchestrator = DispatcherOrchestrator(
            request_validation=validation,
            result_normalization=normalization,
        )
        request = ActionCommandVO(action_name="test")
        validated = orchestrator.validate_request(request)
        # Without sync_dispatch configured, dispatch_sync raises RuntimeError
        with pytest.raises(RuntimeError, match="SyncDispatchProtocol not configured"):
            orchestrator.dispatch_sync(validated)

    def test_execute_action_with_exception_handled(self) -> None:
        """FR-DSP-006: Exceptions during execution produce error envelope."""
        catalog = {
            "failing": _make_metadata(
                action_name="failing",
                parameter_schema={"type": "object", "properties": {}, "required": []},
            ),
        }
        validation = RequestValidationExecutor(catalog=catalog)
        normalization = ResultNormalizationExecutor()

        class FailingExecute:
            def execute_action(self, action_name: str, params: dict) -> None:  # noqa: ARG002
                raise RuntimeError("boom")

        sync = SyncDispatchExecutor(execute_action=FailingExecute())
        orchestrator = DispatcherOrchestrator(
            request_validation=validation,
            sync_dispatch=sync,
            result_normalization=normalization,
        )
        request = ActionCommandVO(action_name="failing")
        validated = orchestrator.validate_request(request)
        result = orchestrator.dispatch_sync(validated)
        assert isinstance(result, UnifiedResultEnvelopeVO)
        assert result.success is False
