# Linter Source Code Analysis Report

## Files Analyzed

1. `lint-arwaky/crates/orphan-detector/src/capabilities_orphan_surfaces_analyzer.rs` - AES506
2. `lint-arwaky/crates/orphan-detector/src/capabilities_orphan_graph_resolver.rs` - Import graph + entry points
3. `lint-arwaky/crates/orphan-detector/src/agent_orphan_orchestrator.rs` - Reachability tracing
4. `lint-arwaky/crates/import-rules/src/capabilities_dummy_import_checker.rs` - AES204
5. `lint-arwaky/crates/import-rules/src/capabilities_import_unused_checker.rs` - AES203
6. `lint-arwaky/crates/shared/src/import-rules/utility_import_resolver.rs` - Barrel file detection

## Key Findings

### 1. AES506 Surface Orphan Detection Flow

The AES506 checker works like this:
1. `scan_orphans()` collects all files from target directory
2. `_expand_workspace_files()` adds ALL workspace files (cross-module)
3. Import graph is built from ALL files (including cross-module imports)
4. Entry points are identified via pattern matching
5. `_trace_reachability()` BFS through import graph from entry points
6. Each file is checked: if it's in the "reachable" set, it's NOT orphaned
7. Surface files NOT in the reachable set → flagged AES506

### 2. Entry Point Detection (TWO implementations)

**Implementation A** - `get_orphan_entry_points()` in `agent_orphan_orchestrator.rs`:
```rust
vec!["_container.rs", "_container.py", ..., "main.py", "lib.rs", "index.ts"]
```
Does NOT include `root_*` prefix pattern!

**Implementation B** - `identify_entry_points()` in `capabilities_orphan_graph_resolver.rs`:
```rust
// DEFAULT (no configured patterns):
basename.starts_with("root_")  // HAS root_*
|| basename.ends_with("_entry.py")
|| ...

// CONFIGURED (with patterns from get_orphan_entry_points()):
basename.ends_with(pattern)  // _entry.py matches root_cli_main_entry.py
|| file_stem(basename).contains(pattern)
```

**Conclusion: Entry points ARE correctly identified** because `root_cli_main_entry.py` matches `_entry.py` pattern via `ends_with`. But `__init__.py` is NOT an entry point (no matching pattern).

### 3. `__init__.py` EXCLUDED from Orphan Checking

In `_evaluate_layer()` (`agent_orphan_orchestrator.rs` line ~320):
```rust
if f.ends_with("__init__.py") || f.ends_with("/mod.rs") || ... {
    return OrphanIndicatorResult::new(false, String::new(), Severity::HIGH);
}
```

This means `__init__.py` is:
- NOT flagged as orphan (correct)
- NOT evaluated for AES506 at all (correct for barrel files)
- But its IMPORTED SURFACES should still be traced through the import graph

### 4. Root Cause of AES506 False Positives

The **Python relative import resolution** in `build_graph_context_inner()` (Pass 3b) handles:
```python
from . import (surface_close_command, ...)
```

The regex and code SHOULD resolve these correctly. The import edge from `__init__.py` → `surface_close_command.py` should be added to the graph.

The **Python absolute import resolution** in the BUGFIX section (Pass 3) handles:
```python
from modules.cli.src import (surface_close_command, ...)
```

This also SHOULD work, extracting `surface_close_command` and resolving it via `module_to_file`.

**Likely Bug:** Path format mismatch. The import graph uses RELATIVE paths (e.g., `modules/cli/src/__init__.py`), but `_trace_reachability()` uses paths from `identify_entry_points()` which might use ABSOLUTE paths if the entry point was identified from original file paths.

OR: The `__init__.py` file path stored in the graph differs from the entry point path. For example, when `root_cli_main_entry.py` imports `from modules.cli.src import (...)`, the resolved import points to the `__init__.py` barrel file. But the graph might store this as `modules/cli/src/__init__.py` (relative), while entry points use absolute paths like `/home/raka/.../modules/root_cli_main_entry.py`.

### 5. AES204 False Positive for `__all__` Re-exports

The AES204 checker (`capabilities_dummy_import_checker.rs`) skips barrel files:
```rust
// In DummyFileContext::compute():
if utility_import_resolver::is_barrel_file(basename) {
    return None;  // Skip barrel files
}
```

Where `is_barrel_file()` checks:
```rust
matches!(filename, "__init__.py" | "mod.rs" | "lib.rs" | ...)
```

So `__init__.py` is skipped from AES204. But a non-barrel file like `root_cli_surfaces.py` or `cli_surface_router.py` is NOT skipped, and its imports are checked for real usage.

### 6. AES204 `symbol_used_real` Function

For a non-barrel file, AES204 checks if imported symbols are actually used:
```rust
if utility_dummy_detector::symbol_used_real(
    &lines, &symbol_str, &ctx.dummy_ranges, &ctx.dummy_impl_traits,
) { continue; }  // Symbol IS used → no violation
```

The `symbol_used_real` function checks:
1. Is the symbol used OUTSIDE dummy function ranges?
2. If the symbol appears only in `__all__`, it counts as "used in dummy" → violation

So `__all__` re-exports DON'T count as real usage for AES204. This is why `root_cli_surfaces.py`:

```python
from .surface_close_command import handle as close_handle

__all__ = ["close_handle", ...]
```

Triggers AES204: `close_handle` is imported but only appears in `__all__`, not in real function calls.

## Summary of Bugs Found

| Bug | Location | Description |
|-----|----------|-------------|
| B1 | `orphan-detector/src/` | Import graph path format may mismatch with entry point path format, causing BFS reachability to fail |
| B2 | `shared/src/import-rules/utility_import_resolver.rs` | `is_barrel_file()` correctly identifies `__init__.py`, but the import graph resolution via `from X import (Y,Z)` might not correctly add barrel-file→surface edges |
| B3 | `orphan-detector/src/agent_orphan_orchestrator.rs` | `_evaluate_layer()` skips `__init__.py` entirely - this is correct behavior but means surfaces only reachable through `__init__.py` won't be detected if the import graph edge is missing |
| B4 | `import-rules/src/capabilities_dummy_import_checker.rs` | Direct re-export in `__all__` doesn't count as "real usage" for AES204 - this is intentional behavior, not a bug, but makes it impossible to create non-barrel re-export files |
