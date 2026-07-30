"""Root: Dispatcher feature composition container.

Wires concrete capabilities to the agent orchestrator and bootstraps the
dispatcher module: Capabilities → Agent Orchestrator → (exposed as DispatcherOrchestrator).

This file is the composition root for the dispatcher feature. It instantiates
the six dispatcher capabilities, connects them to the aggregate facade, and
provides the assembled orchestrator for dependency injection by callers.
"""

from __future__ import annotations

import logging

from modules.shared.src.job.contract_job_aggregate import IJobAggregate
from .agent_dispatcher_orchestrator import DispatcherOrchestrator
from .capabilities_action_discovery import ActionDiscoveryExecutor
from .capabilities_background_submit import BackgroundSubmitExecutor
from .capabilities_catalog_registration import CatalogRegistrationExecutor
from .capabilities_request_validation import RequestValidationExecutor
from .capabilities_result_normalization import ResultNormalizationExecutor
from .capabilities_sync_dispatch import SyncDispatchExecutor

logger = logging.getLogger("BlenderMCPServer")


class DispatcherContainer:
    """Dependency injection container for the dispatcher feature module.

    Wires the six dispatcher capabilities to the aggregate orchestrator.
    """

    def __init__(self, job_tracker: IJobAggregate | None = None) -> None:
        self._job_tracker = job_tracker
        self._orchestrator: DispatcherOrchestrator | None = None
        self._wired: bool = False

    def wire(self) -> None:
        """Wire the six dispatcher capabilities to the orchestrator."""
        if self._wired:
            return

        logger.info("Wiring dispatcher feature module")

        # Single shared catalog instance — registration, discovery, and validation
        # must observe the same catalog (FR-DSP-001: dispatcher owns the catalog).
        catalog: dict = {}

        catalog_registration = CatalogRegistrationExecutor(catalog)
        action_discovery = ActionDiscoveryExecutor(catalog)
        request_validation = RequestValidationExecutor(catalog)
        sync_dispatch = SyncDispatchExecutor()
        background_submit = BackgroundSubmitExecutor(job_tracker=self._job_tracker)
        result_normalization = ResultNormalizationExecutor()

        self._orchestrator = DispatcherOrchestrator(
            catalog_registration=catalog_registration,
            action_discovery=action_discovery,
            request_validation=request_validation,
            sync_dispatch=sync_dispatch,
            background_submit=background_submit,
            result_normalization=result_normalization,
        )

        self._wired = True
        logger.info("Dispatcher feature module wired successfully")

    @property
    def agent(self) -> DispatcherOrchestrator:
        """Return the assembled dispatcher orchestrator facade.

        Must call wire() first, or this property will raise RuntimeError.
        """
        if not self._wired or self._orchestrator is None:
            raise RuntimeError("DispatcherContainer not wired — call wire() first")
        return self._orchestrator


def create_dispatcher_feature() -> DispatcherOrchestrator:
    """Factory function to create and wire the dispatcher feature module."""
    container = DispatcherContainer()
    container.wire()
    return container.agent
