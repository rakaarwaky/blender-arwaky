Implementation Plan: config v1.7.0 — Developer-Ready Task Backlog

Source artifacts: BA review todo-config-business-analyst-20260726-0900.md · PM decision session 2026-07-26
Scope: Full remediation (P0+P1+P2) shipped as v1.7.0, new behaviors feature-flagged (BLENDERMCPCONFIGV2), breaking changes unflagged with changelog callout.
Test policy: Unit tests for every task (pytest -m unit); integration suite deferred to v1.7.1. Coverage gate fail_under = 60 must hold.

Decision Log (PM answers → plan effect)

| Q | Decision | Plan effect |
|---|----------|-------------|
| Q1=C | Full scope P0+P1+P2 | All tasks below in-sprint |
| Q2=C | Feature-flagged v1.7.0 | Flag matrix §2; flag default OFF; flip default in v1.8.0 |
| Q3=B | Python-native schema dict | SETTINGSSCHEMA in taxonomyconfig_constant.py; no new dependency |
| Q4=A | Compile-time defaults | DEFAULTSETTINGS in taxonomyconfig_constant.py |
| Q5=A | load(path, overrides) | Dotted keys, highest precedence, caller-scoped (not cached) |
| Q6=Custom | Config file is override-only; defaults are complete; missing file is never fatal in any mode | Loader falls back to defaults on missing file even in strict mode; strict raises only on malformed/unreadable/oversized content |
| Q7=C | Scalars only from env | Remove "may be parsed" from FRD; parseenvvalue unchanged, documented scalar-only |
| Q8=C | Remove legacy prefix now (BREAKING) | Delete ENVPREFIXLEGACY; BLENDERMCP* ignored; changelog BREAKING section |
| Q9=A | Mode-dependent size limit | strict → ConfigLoadError; permissive → warn + skip file source |
| Q10=A | Strict raises ConfigTypeError | Policy mode injected into retriever |
| Q11=A | Support \. escape | parsesettingspath utility, flag-gated |
| Q12=A | Align workspace to FRD | Add settings-file-parent strategy, cache result, manifest markers before VCS; legacy BLENDERMCPROOT removed per Q8 (see Assumption A4) |
| Q13=B | Keep 5 metadata fields | Freeze ConfigMetadata at 5 fields; amend FRD list |
| Q14=B | Keep substring matching | Code unchanged; FRD documents substring semantics + accepted false positives |
| Q15=B | No partial masking | Remove FRD clause; full_redact remains always True |
| Q16=— | Assumed B (constructor injection only) | FRD amends "extended through settings" → "extended via composition root" (Assumption A1) |
| Q17=B | Logging + 50-event ring buffer | New sink capability; exposed via IConfigAggregate.recent_events() |
| Q18=B | Typed callable, duties in loader | Callable[[ConfigPath], dict[str, Any]]; size/UTF-8/safe-parse enforced by loader + loadyamlsafe utility |
| Q19=A | Mandatory thread-safe init | threading.Lock + double-checked caching; 32-thread acceptance test |
| Q20=B | Unit tests now, integration deferred | Per-task unit test specs §4; integration backlog v1.7.1 |

Feature Flag Matrix — BLENDERMCPCONFIGV2

Read once at container construction: configv2enabled: bool | None = None → None resolves via parseenvvalue(os.environ.get("BLENDERMCPCONFIGV2", "")) truthiness; explicit bool wins.

| Behavior | Gated | Flag OFF (v1.7.0 default) | Flag ON |
|---|---|---|---|
| Schema validation (T-06) | ✅ | Skipped entirely | Enforced per policy mode |
| Runtime overrides param (T-06) | ✅ | Param ignored + parse warning logged | Applied, counted |
| Size limit > 1 MiB (T-06) | ✅ | Not checked | strict ConfigLoadError / permissive warn+skip |
| Strict ConfigTypeError (T-07) | ✅ | Default returned (current behavior) | Raise in strict mode |
| \. escaped separator (T-07) | ✅ | Literal split on every . | \. resolves literal dotted key |
| Defaults tier (T-06) | ❌ | Always ON (required by Q6) | — |
| Legacy prefix removal (T-01) | ❌ breaking | Removed | Removed |
| Metadata wiring, events, ring buffer (T-06/T-08/T-09) | ❌ | Always ON | — |
| Workspace fixes + caching (T-10) | ❌ | Always ON | — |
| Thread-safe init (T-06) | ❌ | Always ON | — |

v1.8.0 plan: flip flag default to ON; v1.9.0 remove flag. State this in CHANGELOG.

Task Cards

Dependency chain: T-01 → T-02 → T-03 → T-04 → T-05 → {T-06, T-07} → T-08 → T-09 → T-10 → T-11 → T-12.

T-01 — Constants: defaults, schema, flag, breaking legacy removal
Priority P0 · Effort 2h · Depends — · Decisions Q3, Q4, Q6, Q8 · Findings C-1, C-2, C-7

Modify modules/shared/src/config/taxonomyconfigconstant.py
python
REMOVE
ENVPREFIXLEGACY: str = "BLENDERMCP"          # BREAKING (Q8)

ADD
CONFIGPATHENV: str = "BLENDERMCPCONFIGPATH"
WORKSPACEROOTENV: str = "BLENDERMCP_ROOT"      # replaces both legacy+product root lookup
CONFIGV2FLAGENV: str = "BLENDERMCPCONFIG_V2"
DEFAULTCONFIGFILENAME: str = "config.yaml"
EVENTRINGBUFFER_SIZE: int = 50
RESERVEDENVKEYS: tuple[str, ...] = (
    "BLENDERMCPCONFIGPATH", "BLENDERMCPROOT", "BLENDERMCPCONFIG_V2",
)
DEFAULT_SETTINGS: dict[str, Any] = {
    "blender": {"executable_path": "blender", "host": "localhost", "port": 9876},
    "server": {"transport": "stdio", "log_dir": "log"},
}
SETTINGS_SCHEMA: dict[str, Any] = {
    "blender": {"type": "dict", "required": False, "children": {
        "executable_path": {"type": "str", "required": False},
        "host":            {"type": "str", "required": False},
        "port":            {"type": "int", "required": False},
    }},
    "server": {"type": "dict", "required": False, "children": {
        "transport": {"type": "str", "required": False},
        "log_dir":   {"type": "str", "required": False},
    }},
}
REORDER (manifest before VCS per FRD FR-CFG-003)
PROJECT_MARKERS: tuple[str, ...] = (
    "config.yaml", "config.yml", "pyproject.toml",
    "setup.py", "setup.cfg", "requirements.txt", ".git",
)

Modify modules/shared/src/config/init.py — drop ENVPREFIXLEGACY export; add the seven new constants.

Schema mini-format spec (normative): node = {"type": "str"|"int"|"float"|"bool"|"dict"|"list"|"any", "required": bool, "children": dict}. int check must exclude bool. Unknown key → warning ": unknown key". Type mismatch / missing required → error ": expected , got ".

Acceptance: from modules.shared.src.config import DEFAULTSETTINGS, SETTINGSSCHEMA works; ENVPREFIXLEGACY import raises ImportError; ruff clean.
Tests: tests/unit/config/testconstants.py — defaults match README sample values (port == 9876, transport == "stdio"); PROJECTMARKERS.index("pyproject.toml")  dict[str, Any]:
        return {"source": self.source, "exists": self.exists, "overrides": self.overrides,
                "parsewarnings": list(self.parsewarnings),
                "validationwarnings": list(self.validationwarnings)}

REMOVE (unused after this plan): the ConfigValue alias

Modify modules/shared/src/config/taxonomyconfigvo.py — remove unused SensitiveKeyPattern dataclass.
Modify modules/shared/src/config/taxonomyconfigerror.py — remove unused ConfigProviderError.
Modify modules/shared/src/config/init.py — drop both removed names from imports/all.

Acceptance: ConfigMetadata() is hashable; attribute assignment raises FrozenInstanceError; no remaining references (grep -r "SensitiveKeyPattern\|ConfigProviderError\|ConfigValue" modules/ empty).
Tests: tests/unit/config/testcorevo.py — frozen behavior, to_dict shape, default empty tuples.

T-03 — Contract updates: loader, aggregate
Priority P0 · Effort 1.5h · Depends T-02 · Decisions Q5, Q17 · Findings R-2, R-5, C-3

Modify modules/shared/src/config/contractsettingsloader_protocol.py
python
@abstractmethod
def load_settings(self, path: ConfigPath | None = None,
                  overrides: Mapping[str, Any] | None = None) -> SettingsSnapshot: ...
@abstractmethod
def reload_settings(self, path: ConfigPath | None = None) -> SettingsSnapshot: ...
@abstractmethod
def getlastmetadata(self) -> ConfigMetadata: ...
@abstractmethod
def emitloadedevent(self, snapshot: SettingsSnapshot) -> SettingsLoadedEvent: ...
@abstractmethod
def emitreloadevent(self, snapshot: SettingsSnapshot) -> SettingsReloadEvent: ...
@abstractmethod
def emitvalidationwarning_event(self) -> SettingsValidationWarningEvent | None:
    """Return warning event when permissive-mode warnings exist, else None."""

Create modules/shared/src/config/contractconfigeventsinkprotocol.py
python
class IConfigEventSinkProtocol(ABC):
    @abstractmethod
    def record_event(self, event: Any) -> None: ...
    @abstractmethod
    def recentevents(self, limit: int = EVENTRINGBUFFERSIZE) -> tuple[dict[str, Any], ...]:
        """Oldest → newest, last limit events, asdict-serialized."""

Modify modules/shared/src/config/contractconfigaggregate.py — load/reload gain overrides: Mapping[str, Any] | None = None (load only; reload does not take overrides); add:
python
@abstractmethod
def recentevents(self, limit: int = EVENTRINGBUFFERSIZE) -> tuple[dict[str, Any], ...]: ...

Modify modules/shared/src/config/init.py — export IConfigEventSinkProtocol.

Acceptance: mypy-style signature parity between contracts and (future) implementations; aggregate remains the only surface entry point.
Tests: none (pure ABCs); covered by implementation tests.

T-04 — Snapshot segment traversal (VO support for escaping)
Priority P0 · Effort 1h · Depends — · Decisions Q11 · Findings C-4

Modify modules/shared/src/config/taxonomyconfigvo.py (SettingsSnapshot only)
python
_MISSING = object()  # module-private sentinel

ADD methods (no new imports — taxonomy depends on nothing):
def get_segments(self, segments: tuple[str, ...], default: Any = None) -> Any: ...
def has_segments(self, segments: tuple[str, ...]) -> bool: ...
REWRITE existing get()/has() to delegate:
def get(self, path: str, default: Any = None) -> Any:
    return self.get_segments(tuple(path.split(".")) if path else (), default)
def has(self, path: str) -> bool:
    return self.has_segments(tuple(path.split(".")) if path else ())

Traversal spec (normative): empty segment tuple → deepcopy(self.data); dict node + key present → descend; list node + segment parses as int in range → descend, else return default (False for hassegments); any other node → default. Return value always copy.deepcopy-ed. Fix current bug: out-of-range list index must return default immediately, not continue traversal with default as node.

Acceptance: existing get(path) behavior preserved for all non-escape paths; empty path returns full deep copy.
Tests: tests/unit/config/testsettingssnapshot.py — nested get, list index, out-of-range returns default (regression for node-continuation bug), mutation of returned dict does not affect snapshot, has parity.

T-05 — Utility functions (stateless, pure)
Priority P0 · Effort 3h · Depends T-01 · Decisions Q6, Q7, Q8, Q11, Q18 · Findings R-4, R-6, S-1

Modify modules/shared/src/config/utilityconfighelpers.py — keep parseenvvalue (document: scalar-only per Q7) and searchprojectroot; add:
python
def resolvedefaultconfig_path(explicit: ConfigPath | None = None) -> ConfigPath:
    """explicit → env CONFIGPATHENV → Path.cwd()/DEFAULTCONFIGFILENAME."""

def loadyamlsafe(path: ConfigPath) -> dict[str, Any]:
    """Read bytes; decode 'utf-8-sig' (BOM tolerated); UnicodeDecodeError → ConfigParseError.
    yaml.safe_load ONLY. yaml.YAMLError → ConfigParseError. None → {}. Non-dict root → ConfigParseError."""

def deepmergedicts(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """New dict; recursive on dict+dict; override wins otherwise; inputs never mutated."""

def setnestedvalue(target: dict[str, Any], segments: tuple[str, ...], value: Any) -> None:
    """Create intermediate dicts for missing/non-dict nodes."""

def applyenvoverrides(config: dict[str, Any], environ: Mapping[str, str],
                        prefix: str, reserved: tuple[str, ...]) -> tuple[dict[str, Any], int]:
    """Iterate sorted(environ.items()) for determinism. Skip keys in reserved and keys
    where remainder after prefix is empty. Lowercase remainder. Split on '.'.
    setnestedvalue creates intermediates (env MAY introduce new keys — precedence over file).
    Returns (newdict, appliedcount)."""

def validatesettingsschema(data: dict[str, Any], schema: dict[str, Any]
                             ) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Returns (errors, warnings) per T-01 mini-format spec. 'int' excludes bool."""

def parsesettingspath(path: str, escape_enabled: bool) -> tuple[str, ...]:
    """Split on '.'; when escape_enabled, '\\.' yields a literal '.' inside a segment.
    Empty path → (). Trailing/leading/repeated separators produce empty segments
    which resolve as missing keys (returns default)."""

Acceptance: every function stateless, no capability imports, only Taxonomy + stdlib + yaml.
Tests: tests/unit/config/testutilityconfig_helpers.py —
parseenvvalue: "true"→True, "42"→42, "3.14"→3.14, "null"→None, '["a"]'→'["a"]' (string, not list — Q7 regression).
applyenvoverrides: both BLENDERMCPA and a hypothetical later key → deterministic sorted order; reserved keys skipped; BLENDERMCPBLENDER.PORT=9999 creates/overrides nested int; count correct; inputs not mutated.
loadyamlsafe: valid file; malformed → ConfigParseError; UTF-16 bytes → ConfigParseError; root list → ConfigParseError; empty → {}; BOM file parses.
validatesettingsschema: unknown key → warning; port: "x" → error; port: True against int → error (bool exclusion).
parsesettingspath: "a.b"→("a","b"); "a\\.b" escape ON → ("a.b",); escape OFF → ("a\\","b"); ""→().
deepmergedicts: nested override, list replacement, no input mutation.

T-06 — Loader capability rebuild (the P0 core)
Priority P0 · Effort 6h · Depends T-01..T-05 · Decisions Q5, Q6, Q8, Q9, Q18, Q19 · Findings C-1, C-2, C-3, R-3, R-5, R-6, T-1

Modify modules/config/src/capabilitiessettingsloader.py — full rewrite of internals; class name and file unchanged.
python
ConfigFileLoader = Callable[[ConfigPath], dict[str, Any]]

class SettingsLoaderCapability(ISettingsLoaderProtocol):
    def init(self,
                 configfileloader: ConfigFileLoader | None = None,  # default: loadyamlsafe
                 policymode: str = POLICYMODE_STRICT,
                 defaults: Mapping[str, Any] | None = None,           # None → DEFAULT_SETTINGS
                 schema: Mapping[str, Any] | None = None,             # None → SETTINGS_SCHEMA
                 configv2enabled: bool = False) -> None:
        self._lock = threading.Lock()
        # state: cached: SettingsSnapshot | None, cacheddata: dict, last_metadata: ConfigMetadata

load_settings(path, overrides) spec (normative):
Acquire self._lock.
If overrides is None and path is None and self.cached is not None → return self.cached (Q19 single-load guarantee).
If path is not None or self.cached is None → rebuild core via buildcore(path) (steps 4–10); store cacheddata, cached, lastmetadata.
buildcore: resolved = resolvedefaultconfig_path(path); p = Path(resolved).
Path faults: p.isdir() → strict: raise ConfigPathError(" is a directory"); permissive: append parse warning, filedata = {}. p missing → never fatal in any mode (Q6): append ParseWarning(f"settings file not found: {resolved}; using defaults"), file_data = {}.
Size (flag-gated): if v2 AND p.isfile() AND p.stat().stsize > MAXCONFIGSIZEBYTES → strict: raise ConfigLoadError; permissive: warn + filedata = {}.
Parse: filedata = self.file_loader(ConfigPath(str(p))); ConfigParseError/ConfigLoadError/ConfigValidationError → strict: re-raise; permissive: warn + {}. Other exceptions → strict: wrap in ConfigLoadError; permissive: warn + {}.
Merge precedence: merged = deepmergedicts(dict(self.defaults), filedata); then (merged, envcount) = applyenvoverrides(merged, os.environ, ENVPREFIXPRODUCT, RESERVEDENVKEYS). Legacy BLENDERMCP_* keys are simply not matched (Q8).
Schema (flag-gated): errors, warnings = validatesettingsschema(merged, self.schema); strict + errors → raise ConfigValidationError("; ".join(errors)); permissive → validationwarnings = warnings + errors.
Metadata: ConfigMetadata(source=SourceLocation(str(resolved)), exists=p.isfile(), overrides=OverrideCount(envcount), parsewarnings=tuple(...), validationwarnings=tuple(...)).
Runtime overrides (flag-gated, Q5): if overrides provided and v2 ON: final = deepmergedicts(self.cacheddata, structured) where structured built via setnestedvalue on dotted keys; count = len(overrides); return SettingsSnapshot(data=final) without touching cached/lastmetadata (caller-scoped). If overrides provided and v2 OFF: log one parse warning "runtime overrides ignored; BLENDERMCPCONFIGV2 off" and return the cached snapshot.
Return snapshot.

reloadsettings(path) spec: under lock; buildcore(path) into locals first (build-then-swap = atomic); on success swap cacheddata/cached/lastmetadata, return new snapshot. On exception: if self.cached exists → keep it; strict re-raises, permissive returns self.cached. If no previous snapshot → strict raises; permissive cannot fail here (all file faults degrade to defaults) — any residual exception propagates. Never set cache to None before build (removes current race).

Event builders: emitloadedevent / emitreloadevent use lastmetadata real values: sourcesummary = str(metadata.source), overridecount = metadata.overrides, warningcount = len(parsewarnings) + len(validationwarnings), timestamp = Timestamp(time.time()). emitvalidationwarningevent() → event iff policymode == permissive and validationwarnings non-empty, else None.

Acceptance: all QA items for FR-CFG-001 pass; grep MAXCONFIGSIZEBYTES shows enforcement; no self.cached = None before build.
Tests: tests/unit/config/testsettingsloader.py —
Precedence stack: defaults only → +file → +env (BLENDERMCP_SERVER.TRANSPORT=ws) → +runtime override wins.
Missing file: strict AND permissive both return defaults snapshot, metadata.exists is False, warning present (Q6).
Malformed: strict raises ConfigParseError; permissive returns defaults + warning; previous snapshot retained on permissive reload failure.
Directory path: strict ConfigPathError; permissive warn+defaults.
Oversized (v2 ON, tmp file 1 MiB+1): strict ConfigLoadError; permissive warn+skip. Oversized with v2 OFF: parses (flag regression).
Schema (v2 ON): blender.port: "oops" strict → ConfigValidationError; permissive → snapshot + validation warning; emitvalidationwarning_event non-None.
Overrides: returned snapshot has override; second load_settings() (no args) returns snapshot WITHOUT override (caller-scoped regression); v2 OFF → ignored + warning.
Reserved keys: BLENDERMCPCONFIGPATH=/x does not create config_path setting.
Legacy: BLENDERMCPFOO=1 ignored entirely (Q8 regression).
Events: emitloadedevent(...).override_count equals real env override count; timestamp > 0.
Concurrency (Q19): counting fake file loader; 32 threads × barrier × load_settings(); assert loader invoked exactly once and all threads got the same snapshot object.
Metadata: getlastmetadata() reflects latest load; counts real.

T-07 — Retriever: policy mode + escaped separator
Priority P1 · Effort 2.5h · Depends T-04, T-05 · Decisions Q10, Q11 · Findings T-2, C-4

Modify modules/config/src/capabilitiessettingsretriever.py
python
class SettingsRetrieverCapability(ISettingsRetrieverProtocol):
    def init(self, policymode: str = POLICYMODESTRICT, escapeenabled: bool = False) -> None: ...
    def get_value(self, snapshot, path, default=None):
        return snapshot.getsegments(parsesettingspath(path, self.escape_enabled), default)
    def has_value(self, snapshot, path):
        return snapshot.hassegments(parsesettingspath(path, self.escape_enabled))
    # typed getters — normative pattern:
    def get_int(self, snapshot, path, default=0):
        raw = snapshot.getsegments(parsesettingspath(path, self.escapeenabled), MISSING)
        if raw is _MISSING: return default                       # missing → default in BOTH modes
        if isinstance(raw, int) and not isinstance(raw, bool): return raw
        if self._strict: raise ConfigTypeError(ErrorString(f"{path}: expected int, got {type(raw).name}"))
        return default

Same pattern for getstring/getbool/getfloat. getfloat must accept int and coerce (float(raw)) — fixes current int-rejection gap. MISSING sentinel imported from taxonomyconfig_vo.

Acceptance: strict raises only on present-but-wrong-type; missing key never raises; get_float("port") on 9876 returns 9876.0.
Tests: tests/unit/config/testsettingsretriever.py — missing-vs-mismatch matrix (both modes × 4 getters); escape ON resolves get("a\\.b") where data {"a.b": 1}; escape OFF returns default; bool not accepted by getint; int coerced by getfloat; flag-OFF parity with v1.6.5 behavior.

T-08 — Metadata capability wiring
Priority P0 · Effort 1h · Depends T-02, T-06 · Decisions Q13 · Findings R-1

Modify modules/config/src/capabilitiessettingsmetadata.py
python
class SettingsMetadataCapability(ISettingsMetadataProtocol):
    def init(self, metadata_supplier: Callable[[], ConfigMetadata] | None = None) -> None: ...
    def get_metadata(self) -> ConfigMetadata:
        return self.metadatasupplier() if self.metadatasupplier else ConfigMetadata()
    def tosafedict(self, metadata): return metadata.to_dict()

No capability-to-capability import: the supplier is a bound method (self.loader.getlast_metadata) wired by the container (T-11).

Acceptance: after load(), getmetadata().source is the resolved path, overrides > 0 when env overrides applied; no secret values anywhere in tosafe_dict output (payload contains counts/warnings only).
Tests: tests/unit/config/testsettingsmetadata.py — supplier called per request (reflects reload); None supplier → empty metadata; tosafedict keys exact.

T-09 — Event sink capability + orchestrator emission
Priority P0 · Effort 3h · Depends T-03, T-06 · Decisions Q17 · Findings R-2

Create modules/config/src/capabilitiesconfigevent_sink.py
python
class ConfigEventSinkCapability(IConfigEventSinkProtocol):
    def init(self, maxlen: int = EVENTRINGBUFFER_SIZE) -> None:
        self._buffer: deque[dict[str, Any]] = deque(maxlen=maxlen)
        self._lock = threading.Lock()
    def record_event(self, event: Any) -> None:
        payload = dataclasses.asdict(event)
        with self.lock: self.buffer.append(payload)
        logger.info("config_event %s", json.dumps(payload, default=str))  # logger "BlenderMCPServer"
    def recentevents(self, limit: int = EVENTRINGBUFFERSIZE) -> tuple[dict[str, Any], ...]:
        with self.lock: items = list(self.buffer)
        return tuple(items[-limit:])  # oldest → newest

Modify modules/config/src/agentconfigorchestrator.py
Constructor gains event_sink: IConfigEventSinkProtocol | None = None (last param, backward compatible).
load(path=None, overrides=None): snapshot = self.loader.loadsettings(path, overrides); if sink: recordevent(self.loader.emitloadedevent(snapshot)); ev = self.loader.emitvalidationwarningevent(); if ev and sink: record_event(ev). Return snapshot.
reload(path=None): same with emitreloadevent.
resolveworkspace(): ws = self.workspaceresolver.resolve(); if sink: recordevent(self.workspaceresolver.emitresolvedevent(ws)); return ws.
get_snapshot(): lazy load unchanged (now safe — loader locked).
recentevents(limit=EVENTRINGBUFFERSIZE): delegate to sink; () when sink is None.

Acceptance: after load() the sink holds a SettingsLoadedEvent dict with real counts; recentevents() exposes it; log capture shows one configevent INFO line; payloads contain no settings values (structural guarantee — events carry counts/summary only).
Tests: tests/unit/config/testeventsink.py — 60 events → buffer holds 50, oldest dropped; ordering; limit slicing; log record emitted (caplog). tests/unit/config/testorchestratorevents.py — load/reload/resolve each record exactly one event; permissive schema warning records a fifth event type; recent_events on sink-less orchestrator → ().

T-10 — Workspace resolver: FRD alignment + caching
Priority P1 · Effort 2.5h · Depends T-01, T-05 · Decisions Q8, Q12 · Findings R-4

Modify modules/config/src/capabilitiesworkspaceresolver.py
python
class WorkspaceResolverCapability(IWorkspaceResolverProtocol):
    def init(self, explicit_override: str | None = None,
                 config_path: ConfigPath | None = None) -> None:
        self._lock = threading.Lock()
        self._cached: WorkspacePath | None = None
    def resolve(self) -> WorkspacePath:
        with self._lock:
            if self.cached is not None: return self.cached
            self.cached = self.resolve_uncached()
            return self._cached

resolveuncached strategy order (normative, per FRD minus legacy per Q8):
explicitoverride → Path(...).resolve(); isdir() → strategy="explicit_override"; else warn + fallthrough.
os.environ.get(WORKSPACEROOTENV) (BLENDERMCPROOT only) → resolve; invalid/OSError/non-dir → warn + fallthrough; else "envsignal".
Settings file parent (NEW): if self.configpath: Path(self.configpath).resolve().parent; isdir() → "settingsfile_location".
searchprojectroot(PROJECTMARKERS) → "markersearch".
XDGCONFIGHOME/~/.config + "blender-arwaky"; isdir() → "platformconfig".
Path.cwd().resolve() → "cwd_fallback"; OSError → ConfigRootResolutionError.

emitresolvedevent: real source_summary=workspace.strategy, timestamp=Timestamp(time.time()).

Acceptance: strategy order provable via monkeypatched env/tmp dirs; second resolve() returns cached object without filesystem access (counter-probe).
Tests: tests/unit/config/testworkspaceresolver.py — one test per strategy (isolate via monkeypatch clearing env + tmppath chdir); explicit-invalid falls through; BLENDERMCPROOT set → ignored (Q8 regression); caching: patch searchproject_root with counter, call twice, counter == 1; symlinked dir resolves without error.

T-11 — Container rewiring + flag resolution
Priority P0 · Effort 2h · Depends T-06..T-10 · Decisions Q2, Q18 · Findings S-1, R-9

Modify modules/config/src/rootconfigcontainer.py
python
class ConfigContainer:
    def init(self,
                 configfileloader: Callable[[ConfigPath], dict[str, Any]] | None = None,
                 policymode: str = POLICYMODE_STRICT,
                 explicit_workspace: str | None = None,
                 extraredactionpatterns: tuple[str, ...] = (),
                 configv2enabled: bool | None = None) -> None:
        v2 = (parseenvvalue(os.environ.get(CONFIGV2FLAG_ENV, "")) is True) \
             if configv2enabled is None else configv2enabled
        defaultconfigpath = resolvedefaultconfig_path(None)   # single computation, shared
        self._loader = SettingsLoaderCapability(
            configfileloader=configfileloader or loadyamlsafe,
            policymode=policymode, configv2enabled=v2)
        self._retriever = SettingsRetrieverCapability(
            policymode=policymode, escape_enabled=v2)
        self.workspaceresolver = WorkspaceResolverCapability(
            explicitoverride=explicitworkspace, configpath=defaultconfig_path)
        self.metadataprovider = SettingsMetadataCapability(
            metadatasupplier=self.loader.getlastmetadata)
        self.eventsink = ConfigEventSinkCapability()
        self.redactionrules = RedactionRulesCapability(extrapatterns=extraredaction_patterns)
    def build(self) -> IConfigAggregate:
        return ConfigOrchestrator(loader=..., ..., eventsink=self.event_sink)

Single-cache ownership (R-9): orchestrator keeps its snapshot reference purely as a fast path; loader remains the authoritative cache. configfile_loader typed — no more object.

Acceptance: ConfigContainer().build() works with zero arguments; getmetadata() non-empty after load(); recentevents() non-empty after load(); flag read once at construction.
Tests: tests/unit/config/testcontainer.py — zero-arg build + load returns DEFAULTSETTINGS values with no file (tmp chdir); supplier wiring: metadata source ends with config.yaml; v2 flag from env (monkeypatch.setenv("BLENDERMCPCONFIGV2","true")) enables schema errors; explicit False beats env true.

T-12 — Redaction: documented substring semantics (code-stable)
Priority P2 · Effort 1h · Depends — · Decisions Q14, Q15, Q16 · Findings R-10

Modify modules/config/src/capabilitiesredactionrules.py — docstrings only: state substring semantics are intentional (PM Q14), full redaction only (Q15), extension via composition root extraredactionpatterns (Q16). No behavior change.

Tests: tests/unit/config/testredactionrules.py — authtoken/oauth.secret redacted; documented false positive: author → placeholder (assert as accepted behavior, Q14); redactdict recursion into nested dicts and lists of dicts; placeholder constant exact; extra patterns via constructor applied.

T-13 — Taxonomy & import hygiene sweep
Priority P2 · Effort 1h · Depends T-01..T-11 · Findings R-7, R-8

Verify ConfigTypeError (T-07) and ConfigPathError (T-06) now have raise sites; remove nothing else.
grep for ENVPREFIXLEGACY, BLENDERMCP, SensitiveKeyPattern, ConfigProviderError, ConfigValue across modules/ → zero hits.
ruff check . and ruff format --check . clean.

Tests: static-only; add tests/unit/config/testlayerimports.py — assert capabilities module does not import other capability modules (AST scan), agent imports no capability module (AST scan). (Enforces AES §8/§9 permanently.)

T-14 — FRD amendment patch + README + CHANGELOG
Priority P0 (docs gate the release) · Effort 2h · Depends all · Decisions all

Modify modules/config/FRD.md — exact amendments:

| § | Amendment |
|---|-----------|
| FR-CFG-001 Precedence | Add note: "Built-in defaults are complete; the settings file is optional and exists to override defaults. A missing settings file is never fatal in any policy mode." |
| FR-CFG-001 Env conversion | DELETE bullet "list-like or mapping-like values may be parsed when safely detectable"; replace with "Environment values are scalar-only (Q7)". |
| FR-CFG-001 Legacy | DELETE "Legacy environment prefix may be accepted as fallback"; add "Removed in v1.7.0 (BREAKING). Only BLENDERMCP_ prefix is recognized." |
| FR-CFG-001 Schema | Add: "Schema is a Python-native mapping (SETTINGS_SCHEMA); unknown keys produce warnings; type/required violations are errors." |
| FR-CFG-001 Size | Replace "Conservative size limit" with "1 MiB (MAXCONFIGSIZE_BYTES); strict raises ConfigLoadError, permissive warns and skips the file source." |
| FR-CFG-002 | Replace "Escaped separator may resolve … when supported" with "\. resolves a literal dotted key when BLENDERMCPCONFIGV2 is enabled". |
| FR-CFG-003 | DELETE strategy 3 (legacy workspace signal); renumber; add "resolution result is cached for process lifetime". |
| FR-CFG-004 | Replace 10-field "should include" list with the shipped 5: source, exists, override count, parse warnings, validation warnings. |
| FR-CFG-005 | DELETE "partial masking where supported"; replace extension rule with "rules are extended via composition-root injection (extraredactionpatterns)"; add "matching is substring-based; e.g., auth also matches author — accepted false positive (Q14)". |
| Edge cases | Add duplicate-mapping-keys note: "last occurrence wins (YAML parser behavior)". |
| QA Checklist | Add: "Legacy BLENDERMCP* variables are ignored", "Runtime overrides are caller-scoped and not cached", "32-thread first access performs exactly one load". |
| New § | "Feature Flag" section documenting §2 matrix of this plan. |

Modify README.md — env table: replace BLENDERHOST/BLENDERPORT rows with BLENDERMCPBLENDER.HOST / BLENDERMCPBLENDER.PORT; add BLENDERMCPCONFIGV2 row.
Create/append CHANGELOG.md:
markdown
[1.7.0] - 2026-07-XX
⚠ BREAKING
Removed legacy BLENDERMCP environment prefix (settings overrides) — use BLENDERMCP_.
Removed BLENDERMCPROOT workspace variable — use BLENDERMCP_ROOT.
Added
Built-in defaults tier; settings file is now optional/override-only.
Runtime overrides via load(path, overrides=...) (flag-gated).
Schema validation, 1 MiB size limit, \. path escaping, strict ConfigTypeError (flag-gated via BLENDERMCPCONFIGV2, default OFF; default ON in v1.8.0).
Settings metadata now populated; domain events emitted; recent_events() (50-event ring buffer).
Workspace: settings-file-location strategy, result caching, manifest-before-VCS markers.
Thread-safe singleton initialization.

Acceptance: FRD diff reviewed against this table; README sample env vars match code constants exactly.

Sprint Sequencing (≈ 8 dev-days, single developer)

| Day | Tasks | Merge gate |
|-----|-------|-----------|
| 1 | T-01, T-02, T-04 | constants + VO frozen; snapshot regressions green |
| 2 | T-03, T-05 | contracts compile; utility suite green |
| 3–4 | T-06 (+ concurrency test) | full loader matrix green incl. 32-thread test |
| 5 | T-07, T-08 | retriever matrix + metadata wiring green |
| 6 | T-09, T-11 | event flow end-to-end via container; flag matrix verified ON and OFF |
| 7 | T-10, T-12, T-13 | workspace strategies green; hygiene sweep clean |
| 8 | T-14 + full uv run pytest -m unit + ruff check . + coverage report | release cut |

Definition of Done (release gate)

[ ] All task acceptance criteria checked; every unit test spec in §3 implemented and green (uv run pytest -m unit)
[ ] Coverage fail_under = 60 holds (uv run pytest coverage report)
[ ] ruff check . zero findings; AST import test (T-13) green
[ ] Flag matrix §2 manually verified in both states (smoke script in PR description)
[ ] 32-thread single-load test passes on CI (not just local)
[ ] FRD amendments (T-14) merged in the same PR; README env table matches constants
[ ] CHANGELOG BREAKING section present; legacy removal called out in PR title
[ ] grep -r "BLENDERMCP" modules/ returns zero code references (FRD history note only)
[ ] No secrets in any event/metadata payload (structural: payloads carry counts + source path only — asserted in T-08/T-09 tests)

Assumptions (PM to confirm within 24h; silence = accepted)

A1 (Q16 unanswered): redaction extension stays constructor-injection-only; FRD amended accordingly — consistent with your Q14/Q15 conservatism.
A2 (Q6 interpretation): "config is just for override" ⇒ missing settings file is never fatal in any mode, including strict; strict raises only on malformed/unreadable/oversized content.
A3 (Q20 interpretation): "unit tests only" still covers the Q19-mandated concurrency test (it is a unit test); the deferred item is the integration suite → v1.7.1 backlog.
A4 (Q12×Q8 conflict): FRD strategy 3 (legacy workspace signal) is deleted rather than implemented, because Q8 removes the entire BLENDERMCP namespace. Breaking, changelog-covered.
A5: runtime overrides are caller-scoped (not cached) — caching them would leak one caller's overrides into every subsequent reader; FRD precedence is honored per-call.
A6: flag default OFF at v1.7.0 ships the breaking removals unconditionally but keeps all new enforcement opt-in; default flips ON in v1.8.0, flag deleted in v1.9.0.

Rollback Plan

Flag-gated behaviors: set BLENDERMCPCONFIGV2=false (or unset) — instant reversion to v1.6.5-equivalent behavior for schema/size/overrides/strict-types/escaping. Non-flagged changes (metadata, events, workspace caching, thread safety) are additive and low-risk. Legacy prefix removal is not rollback-able without a revert — mitigated by changelog + one-release deprecation note; if stakeholder pushback occurs, hotfix v1.7.1 re-adding ENVPREFIXLEGACY is a 2-line change confined to T-01/T-06 files.