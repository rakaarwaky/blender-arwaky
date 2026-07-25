"""Asset feature module — search, download, import/export across providers.

Layers:
  - Taxonomy (shared/src/asset/)    → VOs for import/export requests/responses
  - Contract (shared/src/asset/)    → ImportExportProtocol, AssetSearchProtocol, etc.
  - Capabilities                    → Concrete implementations (search, adapters, import/export)
  - Agent                           → Orchestrator coordinating asset operations
"""

from . import capabilities_import_export_executor

__all__ = ["capabilities_import_export_executor"]
