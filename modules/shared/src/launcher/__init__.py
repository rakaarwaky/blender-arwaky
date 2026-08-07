"""Launcher domain — taxonomy types and contracts for the launcher feature.

Provides Value Objects, Errors, Constants, Events, 5 individual Protocol
interfaces, and the Aggregate facade for all 5 launcher operations per the
Launcher FRD (FR-LAU-001..005).
"""

from . import (
    taxonomy_launcher_constant,
    taxonomy_launcher_error,
    taxonomy_launcher_event,
    taxonomy_launcher_vo,
)
from .contract_launch_protocol import LaunchProtocol
from .contract_launcher_aggregate import ILauncherAggregate
from .contract_locate_register_protocol import LocateRegisterProtocol
from .contract_persist_state_protocol import PersistStateProtocol
from .contract_runtime_status_protocol import RuntimeStatusProtocol
from .contract_shutdown_protocol import ShutdownProtocol

__all__ = [
    "ILauncherAggregate",
    "LaunchProtocol",
    "LocateRegisterProtocol",
    "PersistStateProtocol",
    "RuntimeStatusProtocol",
    "ShutdownProtocol",
    "taxonomy_launcher_constant",
    "taxonomy_launcher_error",
    "taxonomy_launcher_event",
    "taxonomy_launcher_vo",
]
