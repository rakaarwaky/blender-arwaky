"""Agent: Config orchestrator.

Coordinates configuration loading, retrieval, workspace resolution,
metadata, and redaction through IConfigAggregate.

Orchestration only — delegates all business logic to capabilities
via protocol interfaces.
"""

from __future__ import annotations

import logging
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import ConfigMetadata, ConfigPath
from modules.shared.src.config.contract_config_aggregate import IConfigAggregate
from modules.shared.src.config.contract_redaction_rules_protocol import IRedactionRulesProtocol
from modules.shared.src.config.contract_settings_loader_protocol import ISettingsLoaderProtocol
from modules.shared.src.config.contract_settings_metadata_protocol import ISettingsMetadataProtocol
from modules.shared.src.config.contract_settings_retriever_protocol import ISettingsRetrieverProtocol
from modules.shared.src.config.contract_workspace_resolver_protocol import IWorkspaceResolverProtocol
from modules.shared.src.config.taxonomy_config_vo import RedactionRule, SettingsSnapshot, WorkspacePath

logger = logging.getLogger("BlenderMCPServer")


# ─── Block 1: Class Definition & Constructor ───────────────
class ConfigOrchestrator(IConfigAggregate):
    """Orchestrator for the config feature.

    Coordinates capabilities through protocol interfaces.
    Zero I/O, zero business logic, zero domain computation.
    """

    def __init__(
        self,
        loader: ISettingsLoaderProtocol,
        retriever: ISettingsRetrieverProtocol,
        workspace_resolver: IWorkspaceResolverProtocol,
        metadata_provider: ISettingsMetadataProtocol,
        redaction_rules: IRedactionRulesProtocol,
    ) -> None:
        self._loader = loader
        self._retriever = retriever
        self._workspace_resolver = workspace_resolver
        self._metadata_provider = metadata_provider
        self._redaction_rules = redaction_rules
        self._snapshot: SettingsSnapshot | None = None

# ─── Block 2: Aggregate Method Implementation ─────────────

    def load(self, path: ConfigPath | None = None) -> SettingsSnapshot:
        """Load settings and cache snapshot."""
        self._snapshot = self._loader.load_settings(path)
        return self._snapshot

    def reload(self, path: ConfigPath | None = None) -> SettingsSnapshot:
        """Atomically replace cached snapshot."""
        self._snapshot = self._loader.reload_settings(path)
        return self._snapshot

    def get_snapshot(self) -> SettingsSnapshot:
        """Return cached snapshot, lazy-loading if needed."""
        if self._snapshot is None:
            self._snapshot = self._loader.load_settings()
        return self._snapshot

    def get(self, path: ConfigPath = "", default: Any = None) -> Any:
        """Retrieve value by dot-separated path."""
        return self._retriever.get_value(self.get_snapshot(), path, default)

    def has(self, path: ConfigPath) -> bool:
        """Check if a path exists in settings."""
        return self._retriever.has_value(self.get_snapshot(), path)

    def get_string(self, path: ConfigPath, default: str = "") -> str:
        """Retrieve string value."""
        return self._retriever.get_string(self.get_snapshot(), path, default)

    def get_int(self, path: ConfigPath, default: int = 0) -> int:
        """Retrieve integer value."""
        return self._retriever.get_int(self.get_snapshot(), path, default)

    def get_bool(self, path: ConfigPath, default: bool = False) -> bool:
        """Retrieve boolean value."""
        return self._retriever.get_bool(self.get_snapshot(), path, default)

    def get_float(self, path: ConfigPath, default: float = 0.0) -> float:
        """Retrieve float value."""
        return self._retriever.get_float(self.get_snapshot(), path, default)

    def resolve_workspace(self) -> WorkspacePath:
        """Delegate workspace resolution."""
        return self._workspace_resolver.resolve()

    def get_metadata(self) -> ConfigMetadata | None:
        """Delegate metadata retrieval."""
        return self._metadata_provider.get_metadata()

    def get_redaction_rule(self) -> RedactionRule:
        """Delegate redaction rule retrieval."""
        return self._redaction_rules.get_redaction_rule()

    def redact_dict(self, data: dict[str, Any]) -> dict[str, Any]:
        """Delegate dictionary redaction."""
        return self._redaction_rules.redact_dict(data)

# ─── Block 3: Dunder Methods, Factories, Helpers ──────────

    def __repr__(self) -> str:
        return "ConfigOrchestrator()"
