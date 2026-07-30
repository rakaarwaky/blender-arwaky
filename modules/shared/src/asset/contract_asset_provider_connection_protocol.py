"""Contract: Provider connection protocol (FR-AST-001).

Defines the minimal protocol for communicating with asset providers.
Replaces primitive `object` type annotations with a proper interface
for dependency inversion and AES 405 compliance.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from modules.shared.src.common.taxonomy_core_vo import ProviderName


class IAssetProviderConnection(ABC):
    """Minimal protocol for asset provider communication (FR-AST-001).

    Providers communicate via a gateway transport that can send commands
    and receive results.
    """

    @abstractmethod
    async def send_command(
        self,
        action: str,
        payload: dict[str, object],
        provider: ProviderName | None = None,
    ) -> dict[str, object]:
        """Send a command through the gateway and return the result."""
        ...
