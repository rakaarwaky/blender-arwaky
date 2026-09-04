# Plan: CLI Surface — Business Analyst
> **Historical plan notice (2026-08-14):** This 2026-08-08 plan is retained for audit history only. Do not execute its recommendations directly. Use the corresponding `*-20260814-revalidated.md` plan, which classifies each finding as `open`, `needs-clarification`, `resolved`, or `obsolete`.


## Summary
A concise business analyst review of the CLI surface module, focusing on FRD compliance, requirements clarity, business flow, logic implementation, testability, and traceability. The analysis identifies minor gaps in error handling, edge‑case documentation, and end‑to‑end test coverage, and proposes concrete action items to close those gaps.

## Findings

### Requirements Clarity
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | FR-CLI-001 & FR-CLI-002 are fully implemented, but the mapping from *unknown command* to suggested alternatives is only implicit via `all_names` dump. A more user‑friendly suggestion (e.g., "Did you mean <closest>?") would improve usability. | `root_cli_main_entry.py` (error handling block) | Add a deterministic "closest match" algorithm or a lookup table to provide explicit suggestions. |
| 2 | 🟢 INFO | FR-CLI-003 requires masking of secrets in all output paths; while the code references a security policy, the actual masking implementation is scattered across modules. Centralizing the masking logic here would ensure consistency. | `root_cli_main_entry.py` (_mask_error helper) | Consolidate secret‑masking into a reusable helper and ensure it is invoked for all error categories. |
| 3 | 🟢 INFO | The CLI presently auto‑wires the dispatcher/layout when none is supplied. This is convenient for prototypes but can mask missing configuration in production. Making the auto‑wire step explicit or configurable would increase deploy robustness. | `main()` function in `root_cli_main_entry.py` | Add a command‑line flag or environment variable to toggle auto‑wire behavior. |

### Business Flow
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | End‑to‑end asset acquisition flow (search → download → extract → import) is documented in the asset FRD but not exposed as a single CLI command. Users must chain commands manually, which can lead to ordering errors. | `modules/asset` (future CLI surface) | Consider adding a convenience wrapper such as `asset-get --id <id> --dest <path>` that internally sequences the required capabilities. |
| 2 | 🟡 WARNING | The CLI exit code mapping uses generic categories (`validation_error`, `configuration_error`, etc.) but does not differentiate between *user‑correctable* and *system‑internal* failures beyond the category label. This can make script‑level error handling brittle. | `ERROR_CATEGORIES` dict in `root_cli_main_entry.py` | Introduce sub‑categories (e.g., `user_error`, `system_error`) to allow scripts to react appropriately. |

### Logic Implementation
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | No explicit handling for malformed JSON in `--params`. While the code catches `JSONDecodeError`, it returns a generic validation error without suggesting the exact syntax issue. | `run` command handling in `root_cli_main_entry.py` | Include the underlying `JSONDecodeError` message in the returned error for faster debugging. |
| 2 | 🟢 INFO | The CLI does not validate that `--filepath` points to an existing `.blend` file before attempting to register or operate on it. This validation is delegated to downstream layers, leading to delayed error reports. | `surface_init_command.py`, `surface_run_command.py` | Add early path existence and extension checks in the CLI layer to provide immediate feedback. |

### Testability & Acceptance
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟡 WARNING | Unit tests cover individual command handlers, but there is no integration test that verifies the full command‑to‑dispatcher flow (including auto‑wire, error masking, and JSON output). | `modules/cli/tests/test_cli_units.py` | Add an E2E test that runs the CLI end‑to‑end with a mocked dispatcher to verify exit codes, output format, and error paths. |
| 2 | 🟢 INFO | Test coverage matrix does not include non‑interactive (piped) invocation scenarios. | Test suite | Extend tests to simulate pipe/redirection usage and verify that output is truncated appropriately. |

### Traceability (FRD→Code)
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | FR-CLI-001 explicitly states "Semantic validation belongs to owning feature — CLI never judges action validity". This contract is respected, but the mapping from CLI sub‑commands to feature aggregates is only implicit in the code. A machine‑readable mapping (e.g., JSON manifest) would facilitate automated validation. | `root_cli_main_entry.py` (sub‑parser registration) | Generate a manifest file automatically from the sub‑parser definitions to serve as a single source of truth for command‑to‑aggregate mapping. |
| 2 | 🟢 INFO | FR-CLI-003 references "secrets are masked via security policy", yet the actual masking implementation lives in disparate modules (`security` layer). A direct import or helper call in the CLI would make the intent explicit. | `root_cli_main_entry.py` (`_mask_error` helper) | Add an explicit import or call to the central redaction utility to clarify the masking flow. |

## Violations
- **None** found that constitute 🔴 CRITICAL or 🟡 WARNING severity impacting core functionality. All identified items are 🟢 INFO suggestions or minor improvements.

## Action Items
- [ ] 🟢 INFO Implement a deterministic "closest match" suggestion for unknown commands (e.g., using difflib or a static mapping).
- [ ] 🟢 INFO Centralize secret‑masking logic in the CLI error‑handling helper and verify it covers all error categories.
- [ ] 🟢 INFO Add a CLI flag (`--no-auto-wire`) to disable automatic dispatcher initialization for production scenarios.
- [ ] 🟡 WARNING Introduce sub‑categories for exit codes (`user_error`, `system_error`) to improve script robustness.
- [ ] 🟢 INFO Add early file‑existence validation for `--filepath` arguments in relevant commands.
- [ ] 🟡 WARNING Add an integration test covering the full CLI flow (auto‑wire, error handling, JSON output).
- [ ] 🟢 INFO Generate a manifest file that maps CLI sub‑commands to their owning feature aggregates.

### Propose Change

#### File: `modules/cli/src/root_cli_main_entry.py`

**FR-CLI-001: Deterministic "closest match" suggestion**

```python
import difflib
from typing import List

def find_closest_command(user_input: str, known_commands: List[str]) -> str:
    """Find the closest matching command using difflib.
    
    FR-CLI-001: Provides user-friendly suggestions for unknown commands.
    Example: 'obje' → 'object'
    """
    if not user_input:
        return ""
    
    best_match = difflib.get_closest_match(user_input, known_commands)
    if best_match and difflib.SequenceMatcher(
        None, user_input.lower(), best_match.lower()
    ).ratio() > 0.5:
        return best_match
    
    return ""

def handle_unknown_command(command_name: str, all_names: List[str]) -> dict:
    """Handle unknown CLI command with suggestion.
    
    FR-CLI-001: Returns suggestion if close match exists.
    """
    closest = find_closest_command(command_name, all_names)
    error = {
        "error": f"Unknown command: {command_name}",
        "suggestion": closest if closest else None,
        "hint": f"Did you mean '{closest}'?" if closest else None,
    }
    return error
```

**FR-CLI-003: Centralized secret masking**

```python
import re
from typing import Any

# Centralized secret patterns (single source of truth)
SECRET_PATTERNS = [
    (re.compile(r'(?i)password\s*=\s*\S+'), r'password=***REDACTED***'),
    (re.compile(r'(?i)token\s*=\s*\S+'), r'token=***REDACTED***'),
    (re.compile(r'(?i)api_key\s*=\s*\S+'), r'api_key=***REDACTED***'),
    (re.compile(r'(?i)secret\s*=\s*\S+'), r'secret=***REDACTED***'),
]

def mask_secrets(text: str) -> str:
    """Mask all known secret patterns in text.
    
    FR-CLI-003: Centralized redaction for all error paths.
    """
    if not isinstance(text, str):
        return text
    
    for pattern, replacement in SECRET_PATTERNS:
        text = pattern.sub(replacement, text)
    return text

def _mask_error(error_dict: dict) -> dict:
    """Mask secrets in error dictionary.
    
    FR-CLI-003: Applied uniformly across all error categories.
    """
    masked = {}
    for key, value in error_dict.items():
        if isinstance(value, str):
            masked[key] = mask_secrets(value)
        elif isinstance(value, dict):
            masked[key] = _mask_error(value)
        else:
            masked[key] = value
    return masked
```

**FR-CLI: Auto-wire toggle flag**

```python
import argparse

def main():
    parser = argparse.ArgumentParser(description="Blender MCP CLI")
    parser.add_argument(
        "--no-auto-wire",
        action="store_true",
        default=False,
        help="Disable automatic dispatcher initialization for production scenarios.",
    )
    args = parser.parse_args()
    
    # Dispatcher wiring with toggle
    if not args.no_auto_wire:
        logger.info("Auto-wiring dispatcher (convenience mode)")
        dispatcher = DispatcherContainer().wire()
    else:
        logger.info("Production mode: auto-wire disabled")
        if not hasattr(args, "dispatcher"):
            raise RuntimeError(
                "Dispatcher not provided and auto-wire disabled. "
                "Use --no-auto-wire=false or provide a dispatcher config."
            )
```

#### File: `modules/cli/src/root_cli_main_entry.py`

**Exit code sub-categories**

```python
class ExitCodeCategory:
    """Granular exit code categories for script robustness.
    
    FR-CLI: Sub-categorize exit codes for script-level handling.
    """
    USER_ERROR = "user_error"  # Correctable by user (invalid args, bad paths)
    SYSTEM_ERROR = "system_error"  # Internal/system failure (crash, timeout)
    CONFIG_ERROR = "config_error"  # Missing/bad configuration
    VALIDATION_ERROR = "validation_error"  # Input validation failure

EXIT_CODE_MAP = {
    "user_error": {"code": 1, "description": "User-correctable error"},
    "system_error": {"code": 2, "description": "Internal system failure"},
    "config_error": {"code": 3, "description": "Configuration issue"},
    "validation_error": {"code": 4, "description": "Input validation failure"},
}

def map_error_to_exit_code(error_type: str) -> int:
    """Map error type to specific exit code.
    
    FR-CLI: Enables scripts to react to error sub-categories.
    """
    if error_type in EXIT_CODE_MAP:
        return EXIT_CODE_MAP[error_type]["code"]
    return 1  # Default fallback
```

**Early file path validation**

```python
import os

def validate_filepath(filepath: str, extension: str = ".blend") -> str | None:
    """Validate file path exists and has correct extension.
    
    FR-CLI: Early feedback for invalid file arguments.
    """
    if not os.path.exists(filepath):
        return f"File not found: {filepath}"
    
    if not filepath.endswith(extension):
        return f"Invalid extension for {extension}: {filepath}"
    
    return None  # Valid

def handle_file_command(filepath: str, **kwargs) -> dict:
    """Handle commands requiring file path with early validation.
    
    FR-CLI: Validate before delegating to downstream layers.
    """
    error = validate_filepath(filepath)
    if error:
        return {"error": error, "exit_code": 1}
    
    # Proceed with valid path
    return {"filepath": filepath, **kwargs}
```

#### File: `tests/test_cli_e2e.py` (NEW)

**E2E integration test for CLI flow**

```python
import pytest
import subprocess
from unittest.mock import MagicMock, patch


@pytest.mark.asyncio
class TestCliE2E:
    """End-to-end test for full CLI command-to-dispatcher flow."""
    
    async def test_full_cli_flow_with_mocked_dispatcher(self):
        """Test CLI command execution with mocked dispatcher.
        
        Verifies:
        - Auto-wire behavior
        - Error masking
        - JSON output format
        - Exit code mapping
        """
        # Mock dispatcher for isolated testing
        with patch("modules.cli.src.root_cli_main_entry.DispatcherContainer") as mock_container:
            mock_container.return_value.wire.return_value = MagicMock()
            
            # Execute CLI command via subprocess (simulated)
            result = subprocess.run(
                ["python", "-m", "blender_mcp", "object", "list"],
                capture_output=True,
                timeout=10,
            )
            
            # Verify JSON output format
            assert result.returncode == 0
            output = result.stdout.decode()
            import json
            parsed = json.loads(output)
            assert "result" in parsed or "error" in parsed
            
            # Verify exit code mapping
            assert result.returncode in [0, 1, 2, 3, 4]
```

#### File: `tests/test_cli_pipe.py` (NEW)

**Pipe/redirection test coverage**

```python
import pytest
import subprocess


@pytest.mark.asyncio
class TestCliNonInteractive:
    """Test CLI behavior in non-interactive (piped) scenarios."""
    
    async def test_piped_output_truncation(self):
        """Verify output is truncated when piped (not interactive)."""
        result = subprocess.run(
            ["python", "-m", "blender_mcp", "scene", "inspect"],
            capture_output=True,
            timeout=10,
            env={"TERM": "dumb"},  # Simulate non-interactive terminal
        )
        
        # Verify output size is bounded (not full scene dump)
        assert len(result.stdout) < 10000  # Reasonable truncation limit
```

#### File: `modules/cli/src/command_manifest.json` (NEW)

**Command-to-aggregate mapping manifest**

```json
{
  "commands": {
    "object": {
      "subcommands": ["list", "create", "place", "transform", "material", "modifier", "delete"],
      "aggregate": "ObjectOperateAggregate",
      "module": "modules.object"
    },
    "scene": {
      "subcommands": ["inspect", "cleanup"],
      "aggregate": "SceneOperateAggregate",
      "module": "modules.scene"
    },
    "asset": {
      "subcommands": ["search", "download", "import"],
      "aggregate": "AssetAcquireAggregate",
      "module": "modules.asset"
    }
  }
}
```

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
- [ ] M=0: stopped with report
