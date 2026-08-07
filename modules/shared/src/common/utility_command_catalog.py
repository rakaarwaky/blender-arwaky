"""Stateless utility functions for command catalog queries."""

from __future__ import annotations

from .taxonomy_command_catalog_constant import ACTION_NAMES, COMMAND_CATALOG, CommandSpec


def list_actions() -> list[str]:
    """Return all available action names."""
    return list(ACTION_NAMES)


def get_command_spec(action: str) -> CommandSpec | None:
    """Retrieve command spec for a named action."""
    return COMMAND_CATALOG.get(action)
