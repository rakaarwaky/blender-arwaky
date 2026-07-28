"""Job feature module — AES implementation.

Layers:
  - Taxonomy (shared/src/job/)      → VOs, Entities, Events, Errors, Constants
  - Contract (shared/src/job/)      → aggregate (IJobAggregate)
  - Agent                           → JobOrchestrator (implements IJobAggregate facade)
  - Root                            → JobContainer (DI wiring)

The JobOrchestrator is self-contained: it owns task state directly and
implements every FR-JOB requirement (track / monitor / cancel / cleanup /
capacity) without delegating to a separate capabilities layer. The
per-FR capability files (cancel / capacity / cleanup / monitor / tracker)
were redundant duplicates of the orchestrator's logic and were removed
(see AUDIT.md, cycle 27).

Surface layer is intentionally absent — MCP/CLI command handlers live in
their respective feature modules (modules/mcp, modules/cli).
"""

from .agent_job_orchestrator import JobOrchestrator

__all__ = [
    "JobOrchestrator",
]
