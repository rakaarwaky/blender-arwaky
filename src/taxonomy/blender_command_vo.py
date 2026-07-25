"""Compatibility shim for legacy blender_command_vo imports."""

from modules.shared.src.taxonomy_command_catalog_constant import (
    ACTION_NAMES,
    COMMAND_CATALOG,
    CommandSpec,
)


class CommandCatalog:
    """Canonical command catalog wrapper for backward compatibility."""

    COMMAND_CATALOG = COMMAND_CATALOG

    @staticmethod
    def list_actions() -> list[str]:
        return ACTION_NAMES


__all__ = ["CommandCatalog", "CommandSpec", "COMMAND_CATALOG", "ACTION_NAMES"]
