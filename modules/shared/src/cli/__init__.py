"""CLI taxonomy — VOs, constants, and events for CLI surface type safety."""

from .taxonomy_cli_constant import (
    EXIT_SUCCESS,
    EXIT_VALIDATION,
    EXIT_UPSTREAM,
    EXIT_UNEXPECTED,
    CATEGORY_VALIDATION,
    CATEGORY_CONFIGURATION,
    CATEGORY_NOT_FOUND,
    CATEGORY_CAPACITY,
    CATEGORY_TIMEOUT,
    CATEGORY_SECURITY,
    CATEGORY_CONNECTION,
    CATEGORY_STATE,
    CATEGORY_TASK,
    CATEGORY_UNEXPECTED,
    ERROR_CATEGORY_MAP,
)
from .taxonomy_cli_event import CliEventKind, CliEvent
from .taxonomy_cli_vo import CliResultVo, CliErrorVo

__all__ = [
    "EXIT_SUCCESS",
    "EXIT_VALIDATION",
    "EXIT_UPSTREAM",
    "EXIT_UNEXPECTED",
    "CATEGORY_VALIDATION",
    "CATEGORY_CONFIGURATION",
    "CATEGORY_NOT_FOUND",
    "CATEGORY_CAPACITY",
    "CATEGORY_TIMEOUT",
    "CATEGORY_SECURITY",
    "CATEGORY_CONNECTION",
    "CATEGORY_STATE",
    "CATEGORY_TASK",
    "CATEGORY_UNEXPECTED",
    "ERROR_CATEGORY_MAP",
    "CliEventKind",
    "CliEvent",
    "CliResultVo",
    "CliErrorVo",
]
