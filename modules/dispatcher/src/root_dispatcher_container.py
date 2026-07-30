"""Root: Dispatcher feature composition container.

Wires concrete capabilities to the agent orchestrator and bootstraps the
dispatcher module: Capabilities → Agent Orchestrator → (exposed as DispatcherOrchestrator).

This file is the composition root for the dispatcher feature. It instantiates
the six dispatcher capabilities, connects them to the aggregate facade, and
provides the assembled orchestrator for dependency injection by callers.
"""

from __future__ import annotations

import logging

from modules.shared.src.job.contract_job_lifecycle_protocol import IJobLifecycle

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

    def __init__(self, job_lifecycle: IJobLifecycle | None = None) -> None:
        self._job_lifecycle = job_lifecycle
        self._orchestrator: DispatcherOrchestrator | None = None
        self._wired: bool = False
        self._execute_action: object | None = None

    def wire(self, execute_action: object | None = None) -> None:
        """Wire the six dispatcher capabilities to the orchestrator.

        FR-DSP-004: SyncDispatchExecutor requires a non-null action executor.
        Pass an execute_action callable (e.g., Gateway's code execution executor)
        to enable synchronous dispatch routing.
        """
        if self._wired:
            return

        logger.info("Wiring dispatcher feature module")

        # Single shared catalog instance — registration, discovery, and validation
        # must observe the same catalog (FR-DSP-001: dispatcher owns the catalog).
        catalog: dict = {}

        catalog_registration = CatalogRegistrationExecutor(catalog)
        action_discovery = ActionDiscoveryExecutor(catalog)
        request_validation = RequestValidationExecutor(catalog)
        background_submit = (
            BackgroundSubmitExecutor(
                job_tracker=self._job_lifecycle,
            )
            if self._job_lifecycle
            else None
        )
        result_normalization = ResultNormalizationExecutor()

        # FR-DSP-004: Wire SyncDispatchExecutor with provided action executor
        execute_action = execute_action or self._execute_action
        sync_dispatch: SyncDispatchExecutor | None = None
        if execute_action is not None:
            sync_dispatch = SyncDispatchExecutor(execute_action=execute_action)

        self._orchestrator = DispatcherOrchestrator(
            catalog_registration=catalog_registration,
            action_discovery=action_discovery,
            request_validation=request_validation,
            background_submit=background_submit,
            sync_dispatch=sync_dispatch,
            result_normalization=result_normalization,
        )

        self._wired = True
        logger.info("Dispatcher feature module wired successfully")

    def set_execute_action(self, executor: object) -> None:
        """Register an action executor for sync dispatch routing."""
        self._execute_action = executor

    @property
    def agent(self) -> DispatcherOrchestrator:
        """Return the assembled dispatcher orchestrator facade.

        Must call wire() first, or this property will raise RuntimeError.
        """
        if not self._wired or self._orchestrator is None:
            raise RuntimeError("DispatcherContainer not wired — call wire() first")
        return self._orchestrator


def create_dispatcher_feature(
    job_lifecycle: IJobLifecycle | None = None,
    execute_action: object | None = None,
) -> DispatcherOrchestrator:
    """Factory function to create and wire the dispatcher feature module.

    Args:
        job_lifecycle: Optional job lifecycle tracker for background submission.
        execute_action: Optional action executor for sync dispatch routing.
    """
    container = DispatcherContainer(job_lifecycle=job_lifecycle)
    container.wire(execute_action=execute_action)
    return container.agent
