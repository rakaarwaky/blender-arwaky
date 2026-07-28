"""Gateway domain entity types — runtime entities for connection tracking.

References shared core types and gateway-specific constants.
"""

from __future__ import annotations

from modules.shared.src.common.taxonomy_core_vo import Host, PortNumber


class GatewayEntity:
    """Runtime entity representing a gateway connection target."""

    def __init__(self, host: Host, port: PortNumber) -> None:
        self.host = host
        self.port = port
