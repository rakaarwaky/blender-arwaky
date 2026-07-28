"""Aggregate contract for the cli feature.

Aggregates all protocol contracts into a single unified interface.
"""

from .contract_cli_command_protocol import CliCommandProtocol
from .contract_cli_error_protocol import CliErrorProtocol
from .contract_cli_lifecycle_protocol import CliLifecycleProtocol
from .contract_cli_render_protocol import CliRenderProtocol

__all__ = [
    "CliCommandProtocol",
    "CliErrorProtocol",
    "CliLifecycleProtocol",
    "CliRenderProtocol",
]
