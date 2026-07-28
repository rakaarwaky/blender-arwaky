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

from .agent_security_orchestrator import SecurityOrchestrator
from .capabilities_archive_guard import ArchiveGuard
from .capabilities_audit_emitter import AuditEmitter
from .capabilities_code_validator import CodeValidator
from .capabilities_path_validator import PathValidator
from .capabilities_sensitive_redactor import SensitiveRedactor
from .root_security_container import SecurityContainer, create_security_feature

__all__ = [
    "SecurityOrchestrator",
    "ArchiveGuard",
    "AuditEmitter",
    "CodeValidator",
    "PathValidator",
    "SensitiveRedactor",
    "SecurityContainer",
    "create_security_feature",
]
