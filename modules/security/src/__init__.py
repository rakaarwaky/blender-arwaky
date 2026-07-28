"""Security feature module — AES implementation.

Layers:
  - Taxonomy (shared/src/security/)   → VOs, Errors, Events, Constants
  - Contract (shared/src/security/)   → 5 individual protocols + Aggregate ABC
  - Capabilities (5 executors)        → One per FR-SEC operation
  - Agent                             → SecurityOrchestrator (implements Aggregate facade)
  - Root                              → SecurityContainer (DI wiring)

Surface layer is intentionally absent — MCP/CLI command handlers live in
their respective feature modules (modules/mcp, modules/cli).
"""

from . import root_security_container
from .root_security_container import SecurityContainer, create_security_feature

__all__ = [
    "SecurityContainer",
    "create_security_feature",
    "root_security_container",
]
