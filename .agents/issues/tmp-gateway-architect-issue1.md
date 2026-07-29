# CRITICAL: Gateway utility file contains stateful class and imports contract

## Summary

`utility_scene_coordinator.py` is a Utility-layer file but contains a stateful class (`SceneCoordinatorUtility`) and imports `SceneQueueProtocol` from Contract layer. Utility must contain stateless standalone functions only and must not import Contract, Capabilities, Agent, Surface, or Root. This violates AES201 and AES404.

## Violations
- **AES201**: Forbidden import — utility imports contract
- **AES404**: Utility role — contains stateful class instead of stateless functions

## Current Code Issue
```python
# modules/gateway/src/utility_scene_coordinator.py:1
"""Utility: Scene coordination helpers."""

from modules.shared.src.gateway.contract_scene_queue_protocol import SceneQueueProtocol

class SceneCoordinatorUtility:  # STATEFUL CLASS IN UTILITY!
    def __init__(self, scene_queue: SceneQueueProtocol):
        self._scene_queue = scene_queue  # BREAKS AES201/AES404
```

## Proposed Fix
Delete `modules/gateway/src/utility_scene_coordinator.py` entirely. Let `GatewayOrchestrator` depend directly on `SceneQueueProtocol`, or move a private helper into the agent file if absolutely necessary. Do not create a utility class.

Update `root_gateway_container.py` to pass `SceneQueueExecutor` directly instead of `SceneCoordinatorUtility`:
```python
# modules/gateway/src/root_gateway_container.py
self._scene_queue = SceneQueueExecutor(...)

self._orchestrator = GatewayOrchestrator(
    connection=self._connection,
    maintenance=self._maintenance,
    transport=self._transport,
    scene_queue=self._scene_queue,  # Pass protocol implementation directly
    code_executor=self._code_executor,
)
```

## Labels
critical, bug
