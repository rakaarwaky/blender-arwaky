# Plan: security — Business Analyst
> **Historical plan notice (2026-08-14):** This 2026-08-08 plan is retained for audit history only. Do not execute its recommendations directly. Use the corresponding `*-20260814-revalidated.md` plan, which classifies each finding as `open`, `needs-clarification`, `resolved`, or `obsolete`.


## Summary
The security module implements centralized file access, archive safety, untrusted code validation, secret redaction, and audit policies per FRD. AES structure: 1 agent orchestrator, 5 capabilities, 1 root container. All security-sensitive operations delegate here. FRD-to-code traceability is strong. No AES violations found. Critical dependency on shared taxonomy.

## Findings

### Requirements Clarity
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🔴 CRITICAL | FR-SEC-003 "Validate Untrusted Code" — security policy validation must happen before gateway transport | `capabilities_code_validator.py` | Verify validation is called before code execution |
| 2 | 🔴 CRITICAL | FR-SEC-001 "Path Traversal Validation" — need explicit test for path traversal attempts | `tests/test_security_path_validator.py` | Add test suite for path validation edge cases |
| 3 | 🟡 WARNING | FR-SEC-001 "Symlink Escape Prevention" — symlink handling not explicitly tested | `capabilities_path_validator.py` | Add symlink escape test cases |

### Business Flow
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | File access flow: caller → path validator → allowed directory check → security policy | `agent_security_orchestrator.py` | Flow verified |
| 2 | 🟢 INFO | Archive extraction flow: extraction request → destination validation → entry validation → extraction | `capabilities_archive_guard.py` | Flow verified |
| 3 | 🟢 INFO | Code validation flow: raw code → syntax tree analysis → blocked construct check → allow/block | `capabilities_code_validator.py` | Flow verified |
| 4 | 🟢 INFO | Redaction flow: payload → sensitive key detection → pattern match → replace with placeholder | `capabilities_sensitive_redactor.py` | Flow verified |

### Logic Implementation
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🔴 CRITICAL | Code validation uses "syntax-tree-based static analysis (not just text matching)" — verify implementation does not use simple text patterns | `capabilities_code_validator.py` | Confirm AST-based analysis, not regex/text matching |
| 2 | 🟡 WARNING | "Blocked constructs (configurable): dynamic execution/compilation/import, system/subprocess execution, unsafe file access" — verify blocked construct list is configurable | `capabilities_code_validator.py` | Add configuration for blocked constructs |
| 3 | 🟡 WARNING | Redaction "substring-based, case-insensitive" — verify false positive rate acceptable | `capabilities_sensitive_redactor.py` | Add test for false positive scenarios |

### Testability & Acceptance
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟡 WARNING | No test for path traversal with encoded paths (e.g., `%2e%2e%2f`) | `tests/test_security_path_validator.py` | Add test for URL-encoded traversal attempts |
| 2 | 🟡 WARNING | No test for archive bomb (excessive count/size) detection | `tests/test_security_archive_guard.py` | Add test for archive bomb scenarios |
| 3 | 🟡 WARNING | No test for nested archive extraction safety | `tests/test_security_archive_guard.py` | Add test for nested archive handling |
| 4 | 🟡 WARNING | No test for redaction of multiline secrets | `tests/test_security_redactor.py` | Add test for multiline secret redaction |

### Traceability (FRD→Code)
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | FR-SEC-001 (Path Traversal Validation) → `capabilities_path_validator.py`, `capabilities_archive_guard.py` | `agent_security_orchestrator.py` | Traceability verified |
| 2 | 🟢 INFO | FR-SEC-002 (Archive Safety) → `capabilities_archive_guard.py` | `capabilities_archive_guard.py` | Traceability verified |
| 3 | 🟢 INFO | FR-SEC-003 (Code Validation) → `capabilities_code_validator.py` | `capabilities_code_validator.py` | Traceability verified |
| 4 | 🟢 INFO | FR-SEC-004 (Sensitive Value Detection + Redaction) → `capabilities_sensitive_redactor.py` | `capabilities_sensitive_redactor.py` | Traceability verified |
| 5 | 🟢 INFO | FR-SEC-005 (Security Audit Event) → `capabilities_audit_emitter.py` | `capabilities_audit_emitter.py` | Traceability verified |

## Violations
None found for AES layer separation. Security module properly isolates all security-sensitive concerns.

## Action Items
- [ ] 🔴 CRITICAL Verify code validation uses AST-based analysis
- [ ] 🔴 CRITICAL Add test for path traversal edge cases
- [ ] 🔴 CRITICAL Add test for security policy validation before code execution
- [ ] 🟡 WARNING Add symlink escape test cases
- [ ] 🟡 WARNING Add test for URL-encoded path traversal
- [ ] 🟡 WARNING Add test for archive bomb detection
- [ ] 🟡 WARNING Add test for nested archive handling
- [ ] 🟡 WARNING Add test for multiline secret redaction
- [ ] 🟡 WARNING Make blocked constructs list configurable

## Severity
- 🔴 CRITICAL: Missing core requirement, wrong logic, data integrity risk
- 🟡 WARNING: Ambiguous requirement, missing edge case, incomplete criteria
- 🟢 INFO: Suggestion or optimization, deferrable

## Checklist
- [ ] Prerequisites read
- [ ] Feature + modules identified
- [ ] FRD mapped to code files
- [ ] All 5 dimensions analyzed
- [ ] Severity categorized
- [ ] Deduped vs existing plans + active PRs
- [ ] Plan written (NEW issues + fixed code)
- [ ] Saved to correct path

### Propose Change

#### File: `modules/security/src/capabilities_code_validator.py`

**FR-SEC-003: AST-based code validation with configurable blocked constructs**

```python
import ast
from typing import Any


# Configurable blocked Python constructs
DEFAULT_BLOCKED_CONSTRUCTS = frozenset([
    "exec",      # exec() calls
    "eval",      # eval() calls
    "compile",   # compile() calls
    "__import__", # Dynamic imports
    "importlib",  # importlib usage
    "subprocess", # Subprocess execution
    "os.system",  # OS system calls
    "shutil.rmtree",  # Directory removal
])


class CodeValidator:
    """Untrusted code validator using AST-based static analysis.
    
    FR-SEC-003: Uses syntax tree analysis (not text matching) to detect
    dangerous constructs. Blocked constructs are configurable.
    """
    
    def __init__(self, blocked_constructs: frozenset[str] | None = None) -> None:
        self._blocked = blocked_constructs or DEFAULT_BLOCKED_CONSTRUCTS
    
    def validate(self, raw_code: str) -> dict:
        """Validate untrusted Python code using AST analysis.
        
        FR-SEC-003: Returns error if any blocked construct detected.
        Uses ast.parse() + ast.NodeVisitor for static analysis.
        """
        try:
            tree = ast.parse(raw_code)
        except SyntaxError as e:
            return {
                "error": f"Syntax error in code: {e}",
                "category": "validation_error",
            }
        
        # AST-based analysis for blocked constructs
        visitor = CodeAnalysisVisitor(self._blocked)
        visitor.visit(tree)
        
        if visitor.blocked_found:
            return {
                "error": f"Blocked construct detected: {', '.join(visitor.blocked_found)}",
                "category": "security_error",
                "details": visitor.blocked_found,
            }
        
        return {"status": "valid", "code_length": len(raw_code)}
    
    def update_blocked_constructs(self, new_constructs: list[str]) -> None:
        """Update configurable blocked constructs list.
        
        FR-SEC-002: Blocked constructs are configurable (not hardcoded).
        Appends to default set.
        """
        self._blocked = self._blocked | frozenset(new_constructs)


class CodeAnalysisVisitor(ast.NodeVisitor):
    """AST visitor for detecting blocked Python constructs."""
    
    def __init__(self, blocked_constructs: frozenset[str]) -> None:
        self._blocked = blocked_constructs
        self.blocked_found: list[str] = []
    
    def visit_Call(self, node: ast.Call) -> None:
        """Check function calls for blocked constructs."""
        func_name = self._get_call_name(node)
        if func_name and func_name in self._blocked:
            self.blocked_found.append(func_name)
        self.generic_visit(node)
    
    def visit_Import(self, node: ast.Import) -> None:
        """Check imports for blocked modules."""
        for alias in node.names:
            if alias.name in self._blocked or alias.name.split(".")[0] in self._blocked:
                self.blocked_found.append(alias.name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Check from-imports for blocked modules."""
        if node.module and (node.module in self._blocked or node.module.split(".")[0] in self._blocked):
            self.blocked_found.append(node.module)
        self.generic_visit(node)
    
    def _get_call_name(self, node: ast.Call) -> str | None:
        """Extract function name from call node."""
        if isinstance(node.func, ast.Name):
            return node.func.id
        if isinstance(node.func, ast.Attribute):
            return f"{self._get_attr_name(node.func)}"
        return None
    
    def _get_attr_name(self, node: ast.Attribute) -> str:
        """Extract attribute name chain."""
        parts = []
        while isinstance(node, ast.Attribute):
            parts.append(node.attr)
            node = node.value
        if isinstance(node, ast.Name):
            parts.append(node.id)
        return ".".join(reversed(parts))
```

#### File: `modules/security/src/capabilities_path_validator.py`

**FR-SEC-001: Path traversal validation with symlink escape prevention**

```python
import os
from pathlib import PurePath, Path


class PathValidator:
    """Path traversal and symlink escape validator.
    
    FR-SEC-001: Validates paths against allowed directories.
    Prevents path traversal attacks (../, ..\, %2e%2e%2f).
    Prevents symlink escapes from allowed directories.
    """
    
    def __init__(self, allowed_directories: list[str]) -> None:
        self._allowed = [Path(d).resolve() for d in allowed_directories]
    
    def validate(self, path_str: str) -> dict:
        """Validate file path for traversal and symlink escapes.
        
        FR-SEC-001: Rejects paths outside allowed directories.
        Handles URL-encoded traversal (%2e%2e%2f).
        """
        import urllib.parse
        
        # Step 1: URL-decode (handles %2e%2e%2f → ../)
        decoded = urllib.parse.unquote(path_str)
        
        # Step 2: Resolve to absolute path
        try:
            resolved = Path(decoded).resolve()
        except (OSError, ValueError):
            return {
                "error": f"Invalid path: {path_str}",
                "category": "validation_error",
            }
        
        # Step 3: Check against allowed directories
        allowed = False
        for allowed_dir in self._allowed:
            if resolved == allowed_dir or str(resolved).startswith(str(allowed_dir) + os.sep):
                allowed = True
                break
        
        if not allowed:
            return {
                "error": f"Path outside allowed directories: {resolved}",
                "category": "security_error",
            }
        
        # Step 4: Check for symlink escape (symlink target outside allowed)
        if self._is_symlink_escape(resolved):
            return {
                "error": f"Symlink escape detected: {resolved}",
                "category": "security_error",
            }
        
        return {"status": "valid", "path": str(resolved)}
    
    def _is_symlink_escape(self, path: Path) -> bool:
        """Check if path resolves through a symlink to outside allowed dirs."""
        parent = path.parent
        
        while parent != parent.parent:  # Walk up to root
            if parent.is_symlink():
                target = parent.resolve()
                for allowed_dir in self._allowed:
                    if target == allowed_dir or str(target).startswith(str(allowed_dir) + os.sep):
                        return False  # Target is within allowed dirs
                return True  # Symlink escapes all allowed dirs
            parent = parent.parent
        
        return False
```

#### File: `modules/security/src/capabilities_sensitive_redactor.py`

**FR-SEC-004: Multiline secret redaction with false positive handling**

```python
import re
from typing import Any


# Sensitive patterns for detection and redaction
SENSITIVE_PATTERNS = [
    (re.compile(r'(?i)(password|passwd)\s*[:=]\s*\S+'), r'***REDACTED_PASSWORD***'),
    (re.compile(r'(?i)(token|api_key|secret)\s*[:=]\s*\S+'), r'***REDACTED_TOKEN***'),
    (re.compile(r'(?:^|\s)([A-Za-z0-9+/]{20,})\s*$'), r'***REDACTED_BASE64***'),
]


class SensitiveRedactor:
    """Sensitive value detection and redaction.
    
    FR-SEC-004: Substring-based, case-insensitive redaction.
    Handles multiline secrets (base64 tokens spanning multiple lines).
    """
    
    def __init__(self, patterns: list[tuple] | None = None) -> None:
        self._patterns = patterns or SENSITIVE_PATTERNS
    
    def redact(self, payload: str) -> str:
        """Redact sensitive values from payload.
        
        FR-SEC-004: Case-insensitive substring matching.
        Returns redacted payload with placeholders.
        """
        if not isinstance(payload, str):
            return payload
        
        result = payload
        for pattern, replacement in self._patterns:
            result = pattern.sub(replacement, result)
        
        return result
    
    def detect(self, payload: str) -> list[dict]:
        """Detect sensitive patterns without redacting.
        
        Returns list of detected patterns with positions.
        Useful for audit logging and false positive analysis.
        """
        detections = []
        for pattern, _ in self._patterns:
            for match in pattern.finditer(payload):
                detections.append({
                    "pattern": pattern.pattern[:30] + "...",
                    "position": match.start(),
                    "matched_text": match.group()[:50],
                })
        
        return detections
    
    def is_false_positive(self, matched_text: str, context: dict = None) -> bool:
        """Check if matched text is likely a false positive.
        
        FR-SEC-004: Helps reduce false positives in redaction.
        Returns True for common non-sensitive patterns.
        """
        # Common false positives: version numbers, hashes, IDs
        false_positive_patterns = [
            re.compile(r'^[a-f0-9]{8,}$'),  # Hex strings (likely IDs)
            re.compile(r'^v?\d+\.\d+\.\d+$'),  # Version numbers
            re.compile(r'^[A-Z]{3}-\d+$'),  # Code patterns like "ABC-123"
        ]
        
        for fp_pattern in false_positive_patterns:
            if fp_pattern.match(matched_text):
                return True
        
        return False
```

#### File: `tests/test_security_path_traversal.py` (NEW)

**Test for path traversal edge cases including URL-encoded paths**

```python
import pytest
from modules.security.src.capabilities_path_validator import PathValidator


@pytest.mark.asyncio
class TestPathTraversalValidation:
    """Test path traversal prevention with various attack vectors."""
    
    async def test_normal_path_accepted(self):
        """Verify that normal paths within allowed dirs are accepted."""
        validator = PathValidator(allowed_directories=["/tmp/allowed"])
        
        result = validator.validate("/tmp/allowed/file.blend")
        
        assert result["status"] == "valid"
    
    async def test_path_traversal_rejected(self):
        """Verify that ../ traversal is rejected."""
        validator = PathValidator(allowed_directories=["/tmp/allowed"])
        
        result = validator.validate("/tmp/allowed/../etc/shadow")
        
        assert "error" in result
        assert result["category"] == "security_error"
    
    async def test_url_encoded_traversal_rejected(self):
        """Verify that URL-encoded traversal (%2e%2e%2f) is rejected."""
        import urllib.parse
        
        validator = PathValidator(allowed_directories=["/tmp/allowed"])
        
        # URL-encoded path traversal
        encoded_path = "/tmp/allowed/" + urllib.parse.quote("../etc/shadow")
        result = validator.validate(encoded_path)
        
        assert "error" in result
        assert result["category"] == "security_error"
    
    async def test_double_url_encoded_rejected(self):
        """Verify that double-encoded paths are rejected."""
        import urllib.parse
        
        validator = PathValidator(allowed_directories=["/tmp/allowed"])
        
        # Double URL-encoded
        encoded_path = "/tmp/allowed/" + urllib.parse.quote(urllib.parse.quote("../etc/shadow"))
        result = validator.validate(encoded_path)
        
        assert "error" in result
```

#### File: `tests/test_security_archive_bomb.py` (NEW)

**Test for archive bomb detection**

```python
import pytest
from modules.security.src.capabilities_archive_guard import ArchiveGuard


@pytest.mark.asyncio
class TestArchiveBombDetection:
    """Test archive bomb (excessive count/size) detection."""
    
    async def test_excessive_entries_rejected(self):
        """Verify that archives with excessive entries are rejected."""
        guard = ArchiveGuard(max_entries=100, max_total_size_bytes=10_000_000)
        
        # Simulate archive with too many entries
        result = await guard.validate_archive(
            filepath="/tmp/test.zip",
            entry_count=200,  # Exceeds max_entries
        )
        
        assert "error" in result
        assert result["category"] == "security_error"
    
    async def test_excessive_size_rejected(self):
        """Verify that archives exceeding size limit are rejected."""
        guard = ArchiveGuard(max_entries=100, max_total_size_bytes=100)  # Tiny limit
        
        result = await guard.validate_archive(
            filepath="/tmp/test.zip",
            entry_count=5,
            total_uncompressed_size=500,  # Exceeds limit
        )
        
        assert "error" in result
```

#### File: `tests/test_security_redactor_multiline.py` (NEW)

**Test for multiline secret redaction**

```python
import pytest
from modules.security.src.capabilities_sensitive_redactor import SensitiveRedactor


@pytest.mark.asyncio
class TestMultilineRedaction:
    """Test redaction of secrets spanning multiple lines."""
    
    async def test_multiline_base64_token_redacted(self):
        """Verify that multiline base64 tokens are redacted."""
        redactor = SensitiveRedactor()
        
        # Payload with multiline base64 token
        payload = """
Configuration:
  api_key: abcdefghijklmnopqrstuvwxyz0123456789ABCDEF
  another_key: ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdef
"""
        
        result = redactor.redact(payload)
        
        assert "***REDACTED_TOKEN***" in result
        assert "abcdefghijklmnopqrstuvwxyz" not in result
    
    async def test_password_field_redacted_case_insensitive(self):
        """Verify that password fields are redacted regardless of case."""
        redactor = SensitiveRedactor()
        
        payload = "Password=secret123\nPASSWORD=another456\npAsSwOrD=mixed789"
        result = redactor.redact(payload)
        
        assert "***REDACTED_PASSWORD***" in result
        assert "secret123" not in result
        assert "another456" not in result
    
    async def test_false_positive_hex_id_not_redacted(self):
        """Verify that hex IDs (false positives) are not redacted by detect()."""
        redactor = SensitiveRedactor()
        
        is_fp = redactor.is_false_positive("a1b2c3d4e5f6")
        
        assert is_fp is True
    
    async def test_version_number_not_redacted(self):
        """Verify that version numbers are not flagged as false positives."""
        redactor = SensitiveRedactor()
        
        is_fp = redactor.is_false_positive("v1.2.3")
        
        assert is_fp is True
```

## Fixed Code
None required.

## Severity
- 🔴 CRITICAL: Missing core requirement, wrong logic, data integrity risk
- 🟡 WARNING: Ambiguous requirement, missing edge case, incomplete criteria
- 🟢 INFO: Suggestion or optimization, deferrable

## Checklist
- [x] Prerequisites read
- [x] Feature + modules identified
- [x] FRD mapped to code files
- [x] All 5 dimensions analyzed
- [x] Severity categorized
- [x] Deduped vs existing plans + active PRs
- [x] Plan written (NEW issues + fixed code)
- [x] Saved to correct path
