"""Common contract: command catalog port interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_command_catalog_constant import CommandSpec
from .taxonomy_core_vo import ActionName, DomainRef


class CommandCatalogProtocol(ABC):
    """Port interface for querying the command catalog."""

    @abstractmethod
    def get_command_spec(self, action: ActionName) -> CommandSpec | None:
        """Retrieve command spec for a named action."""
        ...

    @abstractmethod
    def list_actions(self) -> list[ActionName]:
        """Return all available action names."""
        ...

    @abstractmethod
    def filter_by_domain(self, domain: DomainRef) -> dict[ActionName, CommandSpec]:
        """Return command specs filtered by domain."""
        ...
