"""Contract: Workspace resolver protocol (FR-CFG-003).

Defines the inbound behavior interface for resolving the project
workspace directory using deterministic strategies.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_config_event import WorkspaceResolvedEvent
from .taxonomy_config_vo import WorkspacePath


class IWorkspaceResolverProtocol(ABC):
    """Protocol for resolving project workspace directory (FR-CFG-003)."""

    @abstractmethod
    def resolve(self) -> WorkspacePath:
        """Resolve workspace using deterministic strategy order. Returns first valid candidate."""
        ...

    @abstractmethod
    def emit_resolved_event(self, workspace: WorkspacePath) -> WorkspaceResolvedEvent:
        """Build a workspace-resolved event payload."""
        ...