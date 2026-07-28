"""Root: Security feature composition container.

Wires concrete implementations to contracts and bootstraps the security module:
  Capabilities (5 individual) → Agent Orchestrator → (exposed as SecurityOperateAggregate)

This file is the composition root for the security feature. It instantiates
concrete implementations, connects them to protocol/aggregate contracts,
and provides the assembled aggregate for dependency injection by callers.

Structure:
  1. Constants & imports
  2. SecurityContainer — wires 5 individual capabilities to aggregate
"""

import logging

from modules.shared.src.security.contract_security_operate_aggregate import ISecurityOperateAggregate
from modules.shared.src.security.taxonomy_security_vo import SecurityPolicyVO

from .agent_security_orchestrator import SecurityOrchestrator
from .capabilities_archive_guard import ArchiveGuard
from .capabilities_audit_emitter import AuditEmitter
from .capabilities_code_validator import CodeValidator
from .capabilities_path_validator import PathValidator
from .capabilities_sensitive_redactor import SensitiveRedactor

logger = logging.getLogger("BlenderMCPServer")


class SecurityContainer:
    """Dependency injection container for the security feature module.

    Wires 5 individual capability protocols to their executors,
    then assembles them into the SecurityOrchestrator aggregate facade.

    Capabilities → Agent Orchestrator → (exposed as SecurityOperateAggregate)
    """

    def __init__(self, policy: SecurityPolicyVO | None = None) -> None:
        """Initialize the security feature container.

        Args:
            policy: Optional security policy configuration.
        """
        self._policy = policy or SecurityPolicyVO()
        self._orchestrator: SecurityOrchestrator | None = None
        self._wired: bool = False

    def wire(self) -> None:
        """Wire 5 individual capability executors to the orchestrator.

        Creates the capability → orchestrator chain for each FR:
          PathValidator, ArchiveGuard, CodeValidator, SensitiveRedactor, AuditEmitter
          All 5 → SecurityOrchestrator (implements SecurityOperateAggregate)
        """
        if self._wired:
            return

        logger.info("Wiring security feature module (5 individual capabilities)")

        # Capabilities layer — each implements its own protocol
        validate_path_cap = PathValidator(policy=self._policy)
        validate_archive_cap = ArchiveGuard()
        validate_code_cap = CodeValidator(policy=self._policy)
        redact_cap = SensitiveRedactor(debug_mode=self._policy.redaction_debug_mode)
        emit_audit_cap = AuditEmitter()

        # Agent layer — implements aggregate, depends on all 5 protocols
        self._orchestrator = SecurityOrchestrator(
            validate_path_cap=validate_path_cap,
            validate_archive_cap=validate_archive_cap,
            validate_code_cap=validate_code_cap,
            redact_cap=redact_cap,
            emit_audit_cap=emit_audit_cap,
        )

        self._wired = True
        logger.info("Security feature module wired successfully (5 capabilities)")

    @property
    def aggregate(self) -> SecurityOperateAggregate:
        """Return the assembled SecurityOperateAggregate facade.

        Must call wire() first, or this property will raise RuntimeError.
        """
        if not self._wired:
            raise RuntimeError("SecurityContainer not wired — call wire() first")
        if self._orchestrator is None:
            raise RuntimeError("Orchestrator not initialized — call wire() first")
        return self._orchestrator


def create_security_feature(
    policy: SecurityPolicyVO | None = None,
) -> SecurityOperateAggregate:
    """Factory function to create and wire the security feature module.

    Convenience function for top-level entry points that need the aggregate.

    Args:
        policy: Optional security policy configuration.

    Returns:
        The assembled SecurityOperateAggregate ready for use.
    """
    container = SecurityContainer(policy)
    container.wire()
    return container.aggregate