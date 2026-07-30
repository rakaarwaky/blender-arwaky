"""Dispatcher domain contract: dispatcher aggregate (ABC).

Agent implements this aggregate. Surface layers depend on it.
Facade for action dispatch operations: discovery, validation, dispatch, normalization.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_action_command_vo import ActionCommandVO
from .taxonomy_action_metadata_vo import ActionMetadataVO
from .taxonomy_discovery_filter_vo import DiscoveryFilterVO
from .taxonomy_discovery_outcome_vo import DiscoveryOutcomeVO
from .taxonomy_raw_outcome_vo import RawOutcomeVO
from .taxonomy_unified_result_envelope_vo import UnifiedResultEnvelopeVO


class IDispatcherAggregate(ABC):
    """Aggregate facade for dispatcher operations.

    Agent implements this aggregate (DispatcherOrchestrator). Surface layers depend on it.
    Provides action discovery, request validation, synchronous dispatch, background submission, and result normalization.
    """

    @abstractmethod
    def register_action(self, metadata: ActionMetadataVO) -> ActionMetadataVO:
        ...

    @abstractmethod
    def discover_actions(
        self,
        filter_criteria: DiscoveryFilterVO,
    ) -> DiscoveryOutcomeVO:
        ...

    @abstractmethod
    def validate_request(self, request: ActionCommandVO) -> ActionCommandVO:
        ...

    @abstractmethod
    def dispatch_sync(self, request: ActionCommandVO) -> UnifiedResultEnvelopeVO:
        ...

    @abstractmethod
    def submit_background(self, request: ActionCommandVO) -> UnifiedResultEnvelopeVO:
        ...

    @abstractmethod
    def normalize_result(
        self,
        raw_outcome: RawOutcomeVO,
    ) -> UnifiedResultEnvelopeVO:
        ...

    @abstractmethod
    def execute_action(
        self,
        request: ActionCommandVO,
    ) -> UnifiedResultEnvelopeVO:
        ...
