# CRITICAL: Dispatcher contracts use Any and primitive types instead of taxonomy VOs

## Summary

Dispatcher aggregate and protocol contracts use `Any`, `dict[str, Any]`, and raw `str` values in domain-facing signatures. Examples include `register_action(metadata: Any) -> Any`, `execute_action(action_name: str, parameters: dict[str, Any])`, and `normalize_result(raw_outcome: dict[str, Any], tracking_id: str, is_background: bool)`. This violates AES402/AES405 intent and bypasses taxonomy VOs, reducing type safety.

## Violations
- **AES402**: Contract role — primitive/generic values instead of taxonomy VOs
- **AES405**: Agent role — `Any` annotations in aggregate-facing methods

## Current Code Issue
```python
# modules/shared/src/dispatcher/contract_dispatcher_aggregate.py
class IDispatcherAggregate(ABC):
    @abstractmethod
    def register_action(self, metadata: Any) -> Any: ...  # BAD
    
    @abstractmethod
    def execute_action(self, action_name: str, parameters: dict[str, Any]) -> Any: ...  # BAD
```

## Proposed Fix
```python
# New shared taxonomy: modules/shared/src/dispatcher/taxonomy_discovery_filter_vo.py
@dataclass(frozen=True)
class DiscoveryFilterVO:
    name_filter: str | None = None
    capability_filter: str | None = None
    detail_level: str = "standard"

# New shared taxonomy: modules/shared/src/dispatcher/taxonomy_raw_outcome_vo.py
@dataclass(frozen=True)
class RawOutcomeVO:
    success: bool
    message: str
    tracking_id: str
    is_background: bool = False
    data: dict[str, Any] | None = None
    error_category: str | None = None

# Updated contract
from modules.shared.src.dispatcher.taxonomy_action_command_vo import ActionCommandVO
from modules.shared.src.dispatcher.taxonomy_action_metadata_vo import ActionMetadataVO
from modules.shared.src.dispatcher.taxonomy_discovery_filter_vo import DiscoveryFilterVO
from modules.shared.src.dispatcher.taxonomy_raw_outcome_vo import RawOutcomeVO

class IDispatcherAggregate(ABC):
    @abstractmethod
    def register_action(self, metadata: ActionMetadataVO) -> ActionMetadataVO: ...

    @abstractmethod
    def discover_actions(self, filter_criteria: DiscoveryFilterVO) -> DiscoveryOutcomeVO: ...

    @abstractmethod
    def validate_request(self, request: ActionCommandVO) -> ActionCommandVO: ...

    @abstractmethod
    def dispatch_sync(self, request: ActionCommandVO) -> UnifiedResultEnvelopeVO: ...

    @abstractmethod
    def submit_background(self, request: ActionCommandVO) -> UnifiedResultEnvelopeVO: ...

    @abstractmethod
    def normalize_result(self, raw_outcome: RawOutcomeVO) -> UnifiedResultEnvelopeVO: ...

    @abstractmethod
    def execute_action(self, request: ActionCommandVO) -> UnifiedResultEnvelopeVO: ...
```

## Labels
critical, enhancement
