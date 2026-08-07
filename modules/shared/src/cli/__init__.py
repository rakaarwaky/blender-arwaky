"""CLI domain — re-exports for contract protocols and taxonomy types."""

from .taxonomy_cli_constant import (
    CATEGORY_CAPACITY,
    CATEGORY_CONFIGURATION,
    CATEGORY_CONNECTION,
    CATEGORY_NOT_FOUND,
    CATEGORY_SECURITY,
    CATEGORY_STATE,
    CATEGORY_TASK,
    CATEGORY_TIMEOUT,
    CATEGORY_UNEXPECTED,
    CATEGORY_VALIDATION,
    ERROR_CATEGORY_MAP,
    EXIT_SUCCESS,
    EXIT_UNEXPECTED,
    EXIT_UPSTREAM,
    EXIT_VALIDATION,
)
from .taxonomy_cli_event import CliEvent, CliEventKind
from .taxonomy_cli_vo import CliErrorVo, CliResultVo

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
