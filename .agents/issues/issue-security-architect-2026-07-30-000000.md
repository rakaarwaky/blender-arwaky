`.agents/issues/issue-security-architect-2026-07-30-000000.md`

```markdown
# Issue: security — Architectural Review & Refactoring

## Summary
The `security` feature has a mostly correct AES layer split — shared taxonomy/contracts, five capabilities, one agent orchestrator, and a root container — but it contains several architectural and security-critical gaps. The most urgent issues are fail-open path validation when `allowed_directories` is empty, missing archive destination enforcement, unwired symlink resolution, and incomplete audit orchestration for denied security operations. There are also maintainability concerns: duplicated redaction logic, duplicated archive VOs in the asset domain, unused taxonomy constants/config fields, and package exports that expose concrete capabilities instead of only the composition root. These issues should be fixed before the security module is treated as the authoritative delegate for path, archive, code, redaction, and audit policy.

## Findings by Category

### Layer Boundaries
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | `modules/shared/src/security/__init__.py` imports `taxonomy_security_error` and `taxonomy_security_event`, but those files are not present in the provided source snapshot. If absent, the shared security package fails on import. | `modules/shared/src/security/__init__.py:~10` | Add the missing taxonomy files or remove the imports until the files exist. If error/event taxonomy is planned, create `taxonomy_security_error.py` and `taxonomy_security_event.py` with AES-compliant VO-based fields. |
| 2 | 🟡 WARNING | `modules/security/src/__init__.py` re-exports concrete capabilities (`ArchiveGuard`, `AuditEmitter`, `CodeValidator`, `PathValidator`, `SensitiveRedactor`) and the agent orchestrator. This encourages consumers to bypass the root container and aggregate contract. | `modules/security/src/__init__.py:~14-27` | Export only composition-root entry points: `SecurityContainer`, `create_security_feature`. If direct aggregate access is needed, expose it through the container/factory, not by re-exporting concrete lower-layer classes. |
| 3 | 🟡 WARNING | Contract-like DI ports `_PathResolver` and `_AuditSink` are defined inside capabilities files. These are stable abstraction boundaries and may be reused by root or other features. | `modules/security/src/capabilities_path_validator.py:~20`, `modules/security/src/capabilities_audit_emitter.py:~25` | If these ports are part of the public wiring surface, promote them to shared contract files, e.g. `contract_path_resolve_protocol.py` and `contract_audit_sink_protocol.py`. If purely internal, document them as internal helper protocols. |
| 4 | 🟡 WARNING | Asset taxonomy duplicates security archive VOs: `ArchiveEntryVO`, `ArchiveExtractionOptionsVO`, and `ArchiveExtractionVO` are redefined in `modules/shared/src/asset/taxonomy_asset_vo.py`. The security contract uses the security-domain versions. This creates two structurally similar but nominally different archive-extraction types. | `modules/shared/src/asset/taxonomy_asset_vo.py:~235-285`, `modules/shared/src/security/taxonomy_security_vo.py:~80-130` | Make security archive VOs the single source of truth, or move shared archive-safety VOs to `modules/shared/src/common/`. Asset should import and use the canonical archive VOs instead of duplicating them. |

### Naming Convention
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟢 INFO | Capability role suffixes `emitter` and `redactor` are not in the standard role catalog listed in ARCHITECTURE.md. AES capabilities suffix policy is flexible, but role names should be registered or aligned with known roles. | `modules/security/src/capabilities_audit_emitter.py:1`, `modules/security/src/capabilities_sensitive_redactor.py:1` | Register `emitter` and `redactor` as allowed capability suffixes in AES config, or rename to standard roles such as `publisher`/`sanitizer` if the project wants strict catalog alignment. |
| 2 | 🟢 INFO | `utility_security_path.py` is valid but broad. The file currently provides path normalization and boundary checking; a more precise role suffix would improve discoverability. | `modules/shared/src/security/utility_security_path.py:1` | Consider renaming to `utility_security_path_resolver.py` or `utility_security_path_boundary.py` if the file grows. Not required now. |

### Dead Code / Orphan
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | Many security constants are unused: `SECURITY_DEFAULT_MAX_CODE_SIZE`, `SECURITY_DEFAULT_ARCHIVE_MAX_DEPTH`, `SECURITY_DEFAULT_ARCHIVE_MAX_TOTAL_SIZE`, `SECURITY_DEFAULT_ARCHIVE_MAX_ENTRY_SIZE`, `SECURITY_DEFAULT_ARCHIVE_MAX_ENTRY_COUNT`, `SECURITY_POLICY_STRICT`, `SECURITY_POLICY_PERMISSIVE`, `AUDIT_EVENT_*`, `SECURITY_SOURCE_FEATURE`. Meanwhile, VOs and capabilities repeat the same literals. | `modules/shared/src/security/taxonomy_security_constant.py:~8-30` | Use these constants in `SecurityPolicyVO`, `ArchiveExtractionOptionsVO`, `CodeValidationVO`, `AuditEmitter`, and orchestrator audit construction. Remove constants that remain unused after wiring. |
| 2 | 🟡 WARNING | `SecurityPolicyVO` contains fields that are not wired or consumed: `archive_max_depth`, `archive_max_total_size`, `archive_max_entry_count`, `archive_allow_symbolic_links`, `max_code_size`, `redaction_patterns`, `redaction_key_names`, `redaction_debug_mode`, `security_policy_mode`. | `modules/shared/src/security/taxonomy_security_vo.py:~220-245`, `modules/security/src/root_security_container.py:~60-70` | Wire these fields into the relevant capabilities, or remove them until they are required. Configuration fields that do nothing are a correctness and trust risk. |
| 3 | 🟢 INFO | Taxonomy aliases `ErrorCategory`, `FilePath`, `FileSize`, and `MetadataMap` appear unused by the provided security contracts/capabilities. | `modules/shared/src/security/taxonomy_security_vo.py:~245-255` | Remove unused aliases or adopt them in contracts/VOs where they represent domain meaning. Avoid keeping speculative taxonomy types. |
| 4 | 🟢 INFO | `ViolationCategory` and `AuditSeverity` are underused because the orchestrator does not automatically emit audit events for denied operations. | `modules/shared/src/security/taxonomy_security_vo.py:~185-210`, `modules/security/src/agent_security_orchestrator.py:~40-70` | Use these enums when adding automatic audit orchestration. If they remain unused, reconsider whether they belong in taxonomy now. |

### Scalability & Coupling
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | `ArchiveGuard` does not enforce allowed destination directories. It calls `is_within_allowed_dirs(dest, [])`, which always returns `True`, then executes `pass`. The capability has no `SecurityPolicyVO` injection and therefore cannot enforce FR-SEC-002 destination policy. | `modules/security/src/capabilities_archive_guard.py:~40-44` | Inject `SecurityPolicyVO` into `ArchiveGuard`. Deny extraction when `allowed_directories` is empty or when the normalized destination is outside allowed directories. |
| 2 | 🔴 CRITICAL | `PathValidator` fails open when `policy.allowed_directories` is empty. `is_within_allowed_dirs(normalized, [])` returns `True`, so absolute paths may be allowed without any configured safe directory. | `modules/security/src/capabilities_path_validator.py:~95-110`, `modules/shared/src/security/utility_security_path.py:~18-30` | Change security path checking to deny by default when no allowed directories are configured. Use a strict variant such as `is_within_allowed_dirs(..., allow_empty=False)`. |
| 3 | 🔴 CRITICAL | Symlink escape prevention is not wired by default. `SecurityContainer` creates `PathValidator(policy=self._policy)` without a `path_resolver`, so the symlink-resolution branch is skipped. | `modules/security/src/root_security_container.py:~60-70`, `modules/security/src/capabilities_path_validator.py:~70-90` | Wire a default resolver that uses `os.path.realpath` or equivalent. Validate the resolved path against allowed directories, not only the logical normalized path. |
| 4 | 🟡 WARNING | `AuditEmitter` creates a fallback audit event when sink delivery fails but discards it. FR-SEC-005 requires a local fallback record when the sink is unavailable. | `modules/security/src/capabilities_audit_emitter.py:~95-110` | Add a fallback buffer, fallback sink, or persistent local record. The fallback event must be retained or forwarded, not constructed and dropped. |
| 5 | 🟡 WARNING | Redaction logic is duplicated: `AuditEmitter._redact_sensitive()` recursively masks strings using `REDACTION_SENSITIVE_PATTERNS`, while `SensitiveRedactor.redact()` performs overlapping pattern-based redaction. | `modules/security/src/capabilities_audit_emitter.py:~30-50`, `modules/security/src/capabilities_sensitive_redactor.py:~30-55` | Extract shared redaction mechanics into a utility, e.g. `utility_security_redact.py`, or route audit metadata redaction through a shared redaction component. Capabilities must not duplicate security-critical mechanics. |
| 6 | 🟡 WARNING | `SensitiveRedactor` only supports text. FR-SEC-004 requires detection/redaction in structured data and nested mappings/lists while preserving structure. `RedactionVO` currently has only `text`. | `modules/shared/src/security/taxonomy_security_vo.py:~150-175`, `modules/security/src/capabilities_sensitive_redactor.py:~25-60` | Add structured redaction support, either by extending `RedactionVO` with a structured payload field or introducing a dedicated structured redaction VO/protocol. Preserve structure and never echo raw secrets on failure. |
| 7 | 🟡 WARNING | `SecurityContainer` ignores policy redaction settings. `SensitiveRedactor()` is created without `policy.redaction_patterns` or `policy.redaction_key_names`. | `modules/security/src/root_security_container.py:~64-66` | Pass `extra_patterns=self._policy.redaction_patterns` and `extra_key_names=self._policy.redaction_key_names` into `SensitiveRedactor`. |
| 8 | 🟢 INFO | Frozen VOs use mutable `dict` fields such as `audit_metadata`, `redacted_metadata`, and `target_metadata`. Frozen dataclasses prevent field reassignment but do not make dictionary contents immutable. | `modules/shared/src/security/taxonomy_security_vo.py:~60`, `~120`, `~180`, `~210` | Prefer immutable metadata representations: tuples of key/value pairs, `MappingProxyType`, or dedicated metadata VOs. At minimum, document that callers must not mutate returned metadata. |

### Data Flow
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | `SecurityOrchestrator` delegates validation/redaction operations but does not automatically emit audit events when operations are denied or fail. FR-SEC-005 states every security violation should produce an audit event. Current flow relies on callers to remember `emit_audit`, which is unsafe. | `modules/security/src/agent_security_orchestrator.py:~40-70` | Make the orchestrator emit audit events after denied path validation, rejected archive extraction, code violations, and redaction failures. Keep decision logic in capabilities; use the orchestrator only to route results to audit emission. |
| 2 | 🟡 WARNING | Asset-domain archive VOs duplicate security-domain archive VOs, creating parallel data-flow types for the same security supervision concept. This can cause type mismatch or divergent field evolution. | `modules/shared/src/asset/taxonomy_asset_vo.py:~235-285` | Asset should call security using the canonical security archive VOs, or shared/common should own archive-safety VOs consumed by both domains. |
| 3 | 🟢 INFO | `SecurityOrchestrator._delegate()` is placed in Block 2 and performs logging. Block 2 should contain only aggregate method implementations, and agent orchestration should avoid direct I/O where possible. | `modules/security/src/agent_security_orchestrator.py:~35-40` | Move `_delegate` to Block 3. Prefer audit events or diagnostics-layer emission over direct agent logging. If logging remains, keep it minimal and free of sensitive data. |

## Violations
- FR-SEC-001: Path validation can fail open when `allowed_directories` is empty.
- FR-SEC-001: Symlink escape prevention is not enforced by default because no resolver is wired.
- FR-SEC-002: Archive extraction destination is not enforced against allowed directories.
- FR-SEC-004: Structured-data redaction required by the FRD is not implemented; only text redaction exists.
- FR-SEC-005: Security violations are not automatically emitted as audit events by the orchestrator.
- FR-SEC-005: Audit sink fallback event is constructed but discarded, so no local fallback record exists.
- AES305: Duplicate redaction mechanics across `AuditEmitter` and `SensitiveRedactor`.
- AES305: Duplicate archive VOs in asset and security taxonomy.
- AES305 / AES405-related hygiene: Repeated default literals instead of using shared taxonomy constants.
- AES501: Unused taxonomy constants and aliases indicate orphan taxonomy content.
- AES boundary hygiene: Feature `__init__.py` re-exports concrete capabilities, encouraging bypass of root composition and aggregate contracts.
- create-agent-python 3-block convention: private helper `_delegate` is placed in Block 2 instead of Block 3.

## Action Items (For Developer)
- [ ] P0 Make path validation deny by default when `SecurityPolicyVO.allowed_directories` is empty.
- [ ] P0 Wire a default symlink/canonical path resolver into `PathValidator` via `SecurityContainer`.
- [ ] P0 Inject `SecurityPolicyVO` into `ArchiveGuard` and deny archive extraction destinations outside allowed directories.
- [ ] P0 Make `SecurityOrchestrator` emit audit events for denied path validation, rejected archive extraction, code validation violations, and redaction failures.
- [ ] P1 Implement a real fallback record or fallback buffer in `AuditEmitter` when sink delivery fails.
- [ ] P1 Extract shared redaction mechanics into a utility or shared component and remove duplicated redaction code from `AuditEmitter`.
- [ ] P1 Wire `SecurityPolicyVO.redaction_patterns` and `SecurityPolicyVO.redaction_key_names` into `SensitiveRedactor`.
- [ ] P1 Replace duplicated numeric/string defaults in VOs and capabilities with constants from `taxonomy_security_constant.py`.
- [ ] P1 Fix or remove missing `taxonomy_security_error` and `taxonomy_security_event` imports in shared security `__init__.py`.
- [ ] P2 Reduce `modules/security/src/__init__.py` exports to composition-root entry points only.
- [ ] P2 Promote `_PathResolver` and `_AuditSink` to shared contracts if they are wiring boundaries used outside the capability.
- [ ] P2 Add structured redaction support to `RedactionVO`/`SensitiveRedactor` or create a dedicated structured redaction protocol.
- [ ] P3 Remove unused taxonomy aliases/constants after wiring is complete.
- [ ] P3 Move agent helper methods to Block 3 and remove direct logging from the agent where practical.

## Proposed Fixes / Reference Code

### `modules/shared/src/security/utility_security_path.py`

```python
"""Utility: Security path helpers — FR-SEC-001, FR-SEC-002."""

from __future__ import annotations

import os


def normalize_path(path: str) -> str:
    """Return the absolute, normalized logical form of path."""
    return os.path.normpath(os.path.abspath(path))


def resolve_path(path: str) -> str:
    """Return the canonical resolved path, following symlinks safely."""
    return os.path.realpath(os.path.abspath(path))


def is_within_allowed_dirs(
    target: str,
    allowed_dirs: list[str] | tuple[str, ...],
    *,
    allow_empty: bool = False,
) -> bool:
    """Return True when target resolves inside one of allowed_dirs.

    For security enforcement, allow_empty defaults to False: an empty
    allow-list means no directory is allowed.
    """
    if not allowed_dirs:
        return allow_empty

    norm_target = normalize_path(target)

    for allowed_dir in allowed_dirs:
        norm_allowed = normalize_path(allowed_dir)
        if norm_target == norm_allowed:
            return True
        if norm_target.startswith(norm_allowed + os.sep):
            return True

    return False
```

### `modules/security/src/capabilities_path_validator.py`

```python
from modules.shared.src.security.utility_security_path import (
    is_within_allowed_dirs,
    normalize_path,
    resolve_path,
)

# Inside PathValidator.validate_path:

normalized = normalize_path(target)

resolved = (
    self._resolver.resolve(normalized)
    if self._resolver is not None
    else resolve_path(normalized)
)

allowed_dirs = tuple(self._policy.allowed_directories)

if not allowed_dirs:
    return PathValidationVO(
        target_path=request.target_path,
        access_mode=request.access_mode,
        base_directory=request.base_directory,
        operation_context=request.operation_context,
        allowed=False,
        denial_reason="No allowed directories configured",
        audit_metadata={"rule": "no_allowed_directory"},
    )

if not is_within_allowed_dirs(resolved, allowed_dirs):
    return PathValidationVO(
        target_path=request.target_path,
        access_mode=request.access_mode,
        base_directory=request.base_directory,
        operation_context=request.operation_context,
        allowed=False,
        denial_reason="Path outside allowed directories",
        audit_metadata={
            "rule": "unauthorized_access",
            "path": _redact_path(resolved),
        },
    )

return PathValidationVO(
    target_path=request.target_path,
    access_mode=request.access_mode,
    base_directory=request.base_directory,
    operation_context=request.operation_context,
    allowed=True,
    canonical_path=resolved,
    audit_metadata={
        "path": _redact_path(resolved),
        "mode": request.access_mode.value,
    },
)
```

### `modules/security/src/capabilities_archive_guard.py`

```python
from modules.shared.src.security.taxonomy_security_vo import (
    ArchiveExtractionVO,
    RejectedEntryVO,
    SecurityPolicyVO,
)
from modules.shared.src.security.utility_security_path import (
    is_within_allowed_dirs,
    normalize_path,
)


class ArchiveGuard(ExtractArchiveProtocol):
    def __init__(self, policy: SecurityPolicyVO | None = None) -> None:
        self._policy = policy or SecurityPolicyVO()

    async def validate_extraction(
        self,
        request: ArchiveExtractionVO,
    ) -> ArchiveExtractionVO:
        opts = request.options
        dest = normalize_path(request.destination_directory)
        rejected: list[RejectedEntryVO] = []
        warnings: list[str] = []

        allowed_dirs = tuple(self._policy.allowed_directories)

        if not dest:
            return ArchiveExtractionVO(
                destination_directory=request.destination_directory,
                entries=request.entries,
                options=request.options,
                allowed=False,
                rejected_entries=tuple(rejected),
                warnings=tuple(["Missing destination directory"]),
                audit_metadata={"rule": "missing_destination"},
            )

        if not allowed_dirs or not is_within_allowed_dirs(dest, allowed_dirs):
            return ArchiveExtractionVO(
                destination_directory=request.destination_directory,
                entries=request.entries,
                options=request.options,
                allowed=False,
                rejected_entries=tuple(rejected),
                warnings=tuple(["Destination outside allowed directories"]),
                audit_metadata={"rule": "unauthorized_archive_destination"},
            )

        # Existing entry checks remain unchanged, but use os.path.relpath
        # for depth calculation:
        #
        # relative = os.path.relpath(entry_resolved, dest)
        # nesting_depth = 0 if relative == "." else relative.count(os.sep) + 1
        #
        # Then compare nesting_depth against opts.max_depth.
```

### `modules/security/src/root_security_container.py`

```python
from modules.shared.src.security.utility_security_path import resolve_path


class _OsPathResolver:
    """Adapter exposing utility resolve_path as a resolver protocol."""

    def resolve(self, path: str) -> str:
        return resolve_path(path)


class SecurityContainer:
    def wire(self) -> None:
        if self._wired:
            return

        validate_path_cap = PathValidator(
            policy=self._policy,
            path_resolver=_OsPathResolver(),
        )

        validate_archive_cap = ArchiveGuard(
            policy=self._policy,
        )

        validate_code_cap = CodeValidator(
            policy=self._policy,
        )

        redact_cap = SensitiveRedactor(
            extra_patterns=self._policy.redaction_patterns,
            extra_key_names=self._policy.redaction_key_names,
        )

        emit_audit_cap = AuditEmitter(
            sink=None,
            fallback_buffer=[],
        )

        self._orchestrator = SecurityOrchestrator(
            validate_path_cap=validate_path_cap,
            validate_archive_cap=validate_archive_cap,
            validate_code_cap=validate_code_cap,
            redact_cap=redact_cap,
            emit_audit_cap=emit_audit_cap,
        )

        self._wired = True
```

### `modules/security/src/agent_security_orchestrator.py`

```python
from modules.shared.src.security.taxonomy_security_constant import (
    SECURITY_SOURCE_FEATURE,
)
from modules.shared.src.security.taxonomy_security_vo import (
    AuditSeverity,
    SecurityAuditEventVO,
    ViolationCategory,
)


class SecurityOrchestrator(ISecurityOperateAggregate):
    # Block 2: aggregate methods only.

    async def validate_path(self, request: PathValidationVO) -> PathValidationVO:
        result = await self._validate_path.validate_path(request)

        if not result.allowed:
            await self._emit_audit.emit_audit(
                SecurityAuditEventVO(
                    violation_category=ViolationCategory.PATH_TRAVERSAL,
                    operation_type="validate_path",
                    source_feature=SECURITY_SOURCE_FEATURE,
                    target_metadata=result.audit_metadata,
                    severity=AuditSeverity.WARNING,
                    redacted_reason=result.denial_reason,
                )
            )

        return result

    async def validate_extraction(
        self,
        request: ArchiveExtractionVO,
    ) -> ArchiveExtractionVO:
        result = await self._validate_archive.validate_extraction(request)

        if not result.allowed or result.rejected_entries:
            await self._emit_audit.emit_audit(
                SecurityAuditEventVO(
                    violation_category=ViolationCategory.UNSAFE_ARCHIVE_ENTRY,
                    operation_type="validate_extraction",
                    source_feature=SECURITY_SOURCE_FEATURE,
                    target_metadata=result.audit_metadata,
                    severity=AuditSeverity.WARNING,
                    redacted_reason="Archive extraction denied or entries rejected",
                )
            )

        return result

    async def validate_code(self, request: CodeValidationVO) -> CodeValidationVO:
        result = await self._validate_code.validate_code(request)

        if not result.allowed or result.violations:
            await self._emit_audit.emit_audit(
                SecurityAuditEventVO(
                    violation_category=ViolationCategory.CODE_VIOLATION,
                    operation_type="validate_code",
                    source_feature=SECURITY_SOURCE_FEATURE,
                    target_metadata=result.audit_metadata,
                    severity=AuditSeverity.WARNING,
                    redacted_reason="Code validation denied",
                )
            )

        return result

    async def redact(self, request: RedactionVO) -> RedactionVO:
        result = await self._redact.redact(request)

        if result.failed:
            await self._emit_audit.emit_audit(
                SecurityAuditEventVO(
                    violation_category=ViolationCategory.REDACTION_FAILURE,
                    operation_type="redact",
                    source_feature=SECURITY_SOURCE_FEATURE,
                    target_metadata={},
                    severity=AuditSeverity.ERROR,
                    redacted_reason=result.failure_reason or "Redaction failed",
                )
            )

        return result

    # Block 3: helpers, dunder methods, factories.
```

### `modules/security/src/capabilities_audit_emitter.py`

```python
class AuditEmitter(EmitAuditProtocol):
    def __init__(
        self,
        sink: _AuditSink | None = None,
        fallback_buffer: list[SecurityAuditEventVO] | None = None,
    ) -> None:
        self._sink = sink
        self._fallback_buffer = (
            fallback_buffer if fallback_buffer is not None else []
        )

    async def emit_audit(
        self,
        event: SecurityAuditEventVO,
    ) -> SecurityAuditEventVO:
        emitted = SecurityAuditEventVO(
            violation_category=event.violation_category,
            operation_type=event.operation_type,
            source_feature=event.source_feature,
            target_metadata=_redact_sensitive(event.target_metadata),
            severity=event.severity,
            correlation_id=event.correlation_id,
            redacted_reason=(
                _redact_sensitive(event.redacted_reason)
                if event.redacted_reason
                else None
            ),
            event_id=uuid.uuid4().hex[:16],
            timestamp=time.time(),
            policy_mode=event.policy_mode,
        )

        if self._sink is not None:
            try:
                self._sink.deliver(emitted)
            except Exception as exc:
                fallback = SecurityAuditEventVO(
                    violation_category=event.violation_category,
                    operation_type=event.operation_type,
                    source_feature=event.source_feature,
                    target_metadata=_redact_sensitive(event.target_metadata),
                    severity=AuditSeverity.ERROR,
                    correlation_id=event.correlation_id,
                    redacted_reason=_redact_sensitive(str(exc)),
                    event_id=uuid.uuid4().hex[:16],
                    timestamp=time.time(),
                    policy_mode="fallback",
                )
                self._fallback_buffer.append(fallback)
                logger.warning(
                    "Audit sink delivery failed; fallback record created: %s",
                    _redact_sensitive(str(exc)),
                )

        return emitted
```

### `modules/security/src/__init__.py`

```python
"""Security feature module — public composition root only."""

from .root_security_container import SecurityContainer, create_security_feature

__all__ = [
    "SecurityContainer",
    "create_security_feature",
]
```

### `modules/shared/src/security/__init__.py`

```python
"""Security domain — taxonomy types and contracts."""

from . import (
    taxonomy_security_constant,
    taxonomy_security_vo,
)

from .contract_emit_audit_protocol import EmitAuditProtocol
from .contract_extract_archive_protocol import ExtractArchiveProtocol
from .contract_redact_sensitive_protocol import RedactSensitiveProtocol
from .contract_security_operate_aggregate import ISecurityOperateAggregate
from .contract_validate_code_protocol import ValidateCodeProtocol
from .contract_validate_path_protocol import ValidatePathProtocol

__all__ = [
    "EmitAuditProtocol",
    "ExtractArchiveProtocol",
    "RedactSensitiveProtocol",
    "ISecurityOperateAggregate",
    "ValidateCodeProtocol",
    "ValidatePathProtocol",
    "taxonomy_security_constant",
    "taxonomy_security_vo",
]

# If taxonomy_security_error.py and taxonomy_security_event.py are required,
# create them before adding:
#
# from . import (
#     taxonomy_security_error,
#     taxonomy_security_event,
# )
```

### `modules/shared/src/security/taxonomy_security_vo.py`

```python
from .taxonomy_security_constant import (
    SECURITY_DEFAULT_ARCHIVE_MAX_DEPTH,
    SECURITY_DEFAULT_ARCHIVE_MAX_ENTRY_COUNT,
    SECURITY_DEFAULT_ARCHIVE_MAX_ENTRY_SIZE,
    SECURITY_DEFAULT_ARCHIVE_MAX_TOTAL_SIZE,
    SECURITY_DEFAULT_MAX_CODE_SIZE,
    SECURITY_POLICY_STRICT,
)


@dataclass(frozen=True)
class ArchiveExtractionOptionsVO:
    max_depth: int = SECURITY_DEFAULT_ARCHIVE_MAX_DEPTH
    max_total_size: int = SECURITY_DEFAULT_ARCHIVE_MAX_TOTAL_SIZE
    max_entry_size: int = SECURITY_DEFAULT_ARCHIVE_MAX_ENTRY_SIZE
    max_entry_count: int = SECURITY_DEFAULT_ARCHIVE_MAX_ENTRY_COUNT
    allow_symbolic_links: bool = False
    allow_hard_links: bool = False


@dataclass(frozen=True)
class CodeValidationVO:
    code_text: str = ""
    max_code_size: int = SECURITY_DEFAULT_MAX_CODE_SIZE
    strict_mode: bool = True
    execution_context: str | None = None

    allowed: bool = False
    violations: tuple[CodeViolationVO, ...] = dc_field(default_factory=tuple)
    redacted_metadata: dict = dc_field(default_factory=dict)
    audit_metadata: dict = dc_field(default_factory=dict)


@dataclass(frozen=True)
class SecurityPolicyVO:
    allowed_directories: tuple[str, ...] = ()
    archive_max_depth: int = SECURITY_DEFAULT_ARCHIVE_MAX_DEPTH
    archive_max_total_size: int = SECURITY_DEFAULT_ARCHIVE_MAX_TOTAL_SIZE
    archive_max_entry_count: int = SECURITY_DEFAULT_ARCHIVE_MAX_ENTRY_COUNT
    archive_allow_symbolic_links: bool = False
    code_validation_enabled: bool = True
    blocked_code_constructs: tuple[str, ...] = dc_field(default_factory=tuple)
    max_code_size: int = SECURITY_DEFAULT_MAX_CODE_SIZE
    redaction_patterns: tuple[str, ...] = dc_field(default_factory=tuple)
    redaction_key_names: tuple[str, ...] = dc_field(default_factory=tuple)
    redaction_debug_mode: bool = False
    security_policy_mode: str = SECURITY_POLICY_STRICT
```

```

```
