"""Job feature module — AES implementation.

Layers:
  - Taxonomy (shared/src/job/)      → VOs, Entities, Events, Errors, Constants
  - Contract (shared/src/job/)      → individual protocols + aggregate
  - Capabilities (executors)        → One per FR operation
  - Agent                           → JobOrchestrator (implements Aggregate facade)
  - Root                            → JobContainer (DI wiring)

Surface layer is intentionally absent — MCP/CLI command handlers live in
their respective feature modules (modules/mcp, modules/cli).
"""

from .agent_job_orchestrator import JobOrchestrator
from .capabilities_job_cancel import JobCancel
from .capabilities_job_capacity import CapacityError, JobCapacityEnforcer
from .capabilities_job_cleanup import JobCleanup
from .capabilities_job_monitor import JobMonitor
from .capabilities_job_tracker import JobTracker, StateError

__all__ = [
    "JobCancel",
    "JobCapacityEnforcer",
    "CapacityError",
    "JobCleanup",
    "JobMonitor",
    "JobOrchestrator",
    "JobTracker",
    "StateError",
]
