"""CLI domain contract: command routing protocol (ABC based).

Defines the protocol for parsing terminal input and routing to owning
feature aggregates. Surface only — no business logic.

FR-CLI-001: Parse and Route Commands
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class CliCommandProtocol(ABC):
    """Protocol for parsing CLI commands and routing to feature aggregates."""

    @abstractmethod
    async def parse_and_route(
        self,
        command: str,
        args: list[str] | None = None,
        flags: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Parse terminal input and route to owning feature aggregate.

        FR-CLI-001: Each CLI command maps to exactly one owning feature aggregate.
        Parsing validates surface shape only; semantic validation belongs to owning feature.
        Unknown command produces validation error with closest commands suggested.

        Args:
            command: The command name.
            args: Optional positional arguments.
            flags: Optional flags and options.

        Returns:
            Dict with success indicator, result data, and message.
        """
        pass