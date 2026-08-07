"""Agent: Config orchestrator.

Coordinates configuration loading, retrieval, workspace resolution,
metadata, and redaction through IConfigAggregate.

Orchestration only — delegates all business logic to capabilities
via protocol interfaces. Owns the bounded event ring buffer (T-09)
since config has exactly 5 capabilities mapped 1:1 to FR-CFG-001..005.
"""

from __future__ import annotations

import json
import logging
from collections import deque
from dataclasses import asdict

from modules.shared.src.common.taxonomy_core_vo import ConfigMetadata, ConfigPath
from modules.shared.src.config.contract_config_aggregate import IConfigAggregate
from modules.shared.src.config.contract_redaction_rules_protocol import IRedactionRulesProtocol
from modules.shared.src.config.contract_settings_loader_protocol import ISettingsLoaderProtocol
from modules.shared.src.config.contract_settings_metadata_protocol import ISettingsMetadataProtocol
from modules.shared.src.config.contract_settings_retriever_protocol import ISettingsRetrieverProtocol
from modules.shared.src.config.contract_workspace_resolver_protocol import IWorkspaceResolverProtocol
from modules.shared.src.config.taxonomy_config_constant import EVENT_RING_BUFFER_SIZE
from modules.shared.src.config.taxonomy_config_event import (
    SettingsLoadedEvent,
    SettingsReloadEvent,
    SettingsValidationWarningEvent,
    WorkspaceResolvedEvent,
)
from modules.shared.src.config.taxonomy_config_vo import (
    EventPayload,
    RedactionRule,
    SettingsData,
    SettingsOverrides,
    SettingsSnapshot,
    SettingsValue,
    WorkspacePath,
)

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
        self._event_buffer: deque[EventPayload] = deque(maxlen=EVENT_RING_BUFFER_SIZE)

# ─── Block 2: Aggregate Method Implementation ─────────────

    def _ensure_loaded(self) -> SettingsSnapshot:
        """Lazy-load: populate snapshot + events if not yet loaded."""
        if self._snapshot is None:
            self._snapshot = self._loader.load_settings()
            self._record_event(self._loader.emit_loaded_event())
            validation_ev = self._loader.emit_validation_warning_event()
            if validation_ev is not None:
                self._record_event(validation_ev)
        return self._snapshot

    def load(
        self,
        path: ConfigPath | None = None,
        overrides: SettingsOverrides | None = None,
    ) -> SettingsSnapshot:
        """Load settings, record events, cache snapshot."""
        self._snapshot = self._loader.load_settings(path, overrides)
        self._record_event(self._loader.emit_loaded_event())
        validation_ev = self._loader.emit_validation_warning_event()
        if validation_ev is not None:
            self._record_event(validation_ev)
        return self._snapshot

    def reload(self, path: ConfigPath | None = None) -> SettingsSnapshot:
        """Atomically replace cached snapshot, record reload event."""
        self._snapshot = self._loader.reload_settings(path)
        self._record_event(self._loader.emit_reload_event())
        return self._snapshot

    def get_snapshot(self) -> SettingsSnapshot:
        """Return cached snapshot, lazy-loading if needed."""
        return self._ensure_loaded()

    def get(self, path: ConfigPath = "", default: SettingsValue = None) -> SettingsValue:
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
        """Resolve and record workspace resolution event."""
        ws = self._workspace_resolver.resolve()
        self._record_event(self._workspace_resolver.emit_resolved_event(ws))
        return ws

    def get_metadata(self) -> ConfigMetadata | None:
        """Delegate metadata retrieval (reflects latest load)."""
        return self._metadata_provider.get_metadata()

    def recent_events(self, limit: int = EVENT_RING_BUFFER_SIZE) -> tuple[EventPayload, ...]:
        """Return the most recent config domain events, oldest → newest.

        GIL assumption: CPython's GIL makes ``deque.append`` and
        ``list(deque)`` atomic enough for single-writer / single-reader
        patterns.  No external lock is needed for the bounded ring buffer.
        """
        if limit <= 0:
            return ()
        items = list(self._event_buffer)
        return tuple(items[-limit:])

    def get_redaction_rule(self) -> RedactionRule:
        """Delegate redaction rule retrieval."""
        return self._redaction_rules.get_redaction_rule()

    def redact_dict(self, data: SettingsData) -> SettingsData:
        """Delegate dictionary redaction."""
        return self._redaction_rules.redact_dict(data)

# ─── Block 3: Event Recording ─────────────────────────────

    def _record_event(
        self,
        event: SettingsLoadedEvent | SettingsReloadEvent | SettingsValidationWarningEvent | WorkspaceResolvedEvent,
    ) -> None:
        """Serialize and store a domain event into the bounded ring buffer."""
        payload = asdict(event)
        # Apply redaction to prevent secret leakage in event logs
        redacted_payload = self._redaction_rules.redact_dict(payload) if isinstance(payload, dict) else payload
        self._event_buffer.append(redacted_payload)
        logger.info("config_event %s", json.dumps(redacted_payload, default=str))

# ─── Dunder ────────────────────────────────────────────────

    def __repr__(self) -> str:
        return "ConfigOrchestrator()"
