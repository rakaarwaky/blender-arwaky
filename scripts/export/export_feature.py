#!/usr/bin/env python3
"""Export a selected module into a single consolidated Markdown file.

The output includes the module's own source files, pyproject.toml (or setup.cfg),
and any shared module transitively reachable through ``from modules.shared``
or ``import modules.shared`` import paths.

Usage:
    # Interactive mode (prompts for selection):
    python3 scripts/export/export_feature.py

    # CLI mode (non-interactive):
    python3 scripts/export/export_feature.py --module server
    python3 scripts/export/export_feature.py --module telemetry --output /tmp/out.md
"""

import argparse
import re
import sys
from pathlib import Path

# Sanitize version strings to a safe filename fragment (CWE-22 mitigation).
SAFE_VERSION_CHARS = re.compile(r"[^0-9A-Za-z.\-]")


def resolve_workspace() -> tuple[Path, Path]:
    """Return (workspace_root, modules_dir). Exit on missing modules/."""
    workspace_root = Path(__file__).resolve().parent.parent.parent
    modules_dir = workspace_root / "modules"

    if not modules_dir.exists():
        print(f"Error: 'modules' directory not found at {modules_dir}", file=sys.stderr)
        sys.exit(1)
    return workspace_root, modules_dir


def list_modules(modules_dir: Path) -> list[str]:
    """Sorted list of module directory names that contain a Python package."""
    modules: list[str] = []
    for entry in modules_dir.iterdir():
        if entry.is_dir() and (entry / "__init__.py").exists():
            modules.append(entry.name)
    return sorted(modules)


def prompt_module(modules: list[str]) -> str:
    """Show numbered list, prompt for selection, return the chosen module name."""
    print("Available modules:")
    for i, name in enumerate(modules, 1):
        print(f"{i:2d}) {name}")
    print()

    while True:
        try:
            choice = input(
                f"Select a module (1-{len(modules)}) or 'q' to quit: "
            ).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            sys.exit(0)

        if choice.lower() == "q":
            print("Exiting.")
            sys.exit(0)

        try:
            idx = int(choice) - 1
        except ValueError:
            print("Error: Invalid input. Please enter a valid number or 'q'.")
            continue

        if 0 <= idx < len(modules):
            return modules[idx]
        print(f"Error: Please choose a number between 1 and {len(modules)}.")


def read_version(workspace_root: Path, fallback: str = "0.1.0") -> str:
    """Read version from pyproject.toml package section."""
    pyproject = workspace_root / "pyproject.toml"
    if not pyproject.exists():
        return fallback

    try:
        content = pyproject.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        print(
            f"Warning: Could not read {pyproject} ({e}). Defaulting to {fallback}."
        )
        return fallback

    # Look for version = "x.y.z" in [project] section
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith('version = "') or stripped.startswith("version = '"):
            match = re.match(r'^version\s*=\s*"([^"]+)"', stripped)
            if match:
                return match.group(1)

    return fallback


def sanitize_version(version: str) -> str:
    """CWE-22: strip any character that could escape the .agents/finding directory."""
    safe = SAFE_VERSION_CHARS.sub("_", version)
    return safe or "0.0.0"


def index_shared_module(
    shared_src_dir: Path,
) -> tuple[dict[str, list[Path]], dict[str, list[Path]]]:
    """Index shared module files for resolving transitive dependencies.

    Returns (module_to_files, symbol_to_files) dicts mapping module names
    and symbols (classes, functions) to their source files.
    """
    module_to_files: dict[str, list[Path]] = {}
    symbol_to_files: dict[str, list[Path]] = {}

    if not shared_src_dir.exists():
        print(
            "Warning: 'modules/shared/src' directory not found. Shared dependencies cannot be resolved."
        )
        return module_to_files, symbol_to_files

    print("Indexing shared module for resolving dependencies...")

    # Regex to match Python class/function/type definitions
    DECL_PATTERN = re.compile(
        r"\b(?:def|class)\s+(\w+)"
    )

    for f in shared_src_dir.rglob("*.py"):
        if f.name == "__init__.py":
            continue

        mod_name = f.stem.replace("-", "_")
        module_to_files.setdefault(mod_name, []).append(f)

        try:
            content = f.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            print(f"Warning: Failed to index file {f} ({e})")
            continue

        for match in DECL_PATTERN.finditer(content):
            symbol_name = match.group(1)
            symbol_to_files.setdefault(symbol_name, []).append(f)

    return module_to_files, symbol_to_files


def resolve_dependency_files(
    components: list[str],
    module_to_files: dict[str, list[Path]],
    symbol_to_files: dict[str, list[Path]],
) -> set[Path]:
    """Resolve a dotted import path (e.g., ['shared', 'server', 'ContractCommandProtocol']) to actual files."""
    resolved: set[Path] = set()
    for comp in components:
        if comp in module_to_files:
            files = module_to_files[comp]
            if len(files) == 1:
                resolved.add(files[0])
            else:
                # Score files by how well they match remaining components
                scored = _score_files(files, components)
                scored.sort(key=lambda item: item[0], reverse=True)
                if scored and scored[0][0] > 0:
                    best_score = scored[0][0]
                    resolved.update(f for score, f in scored if score == best_score)
                else:
                    resolved.add(files[0])

        if comp in symbol_to_files:
            files = symbol_to_files[comp]
            if len(files) == 1:
                resolved.add(files[0])
            else:
                scored = _score_files(files, components)
                scored.sort(key=lambda item: item[0], reverse=True)
                if scored and scored[0][0] > 0:
                    best_score = scored[0][0]
                    resolved.update(f for score, f in scored if score == best_score)
                else:
                    resolved.add(files[0])
    return resolved


def _score_files(files: list[Path], components: list[str]) -> list[tuple[int, Path]]:
    """Score files based on how many path components match."""
    scored: list[tuple[int, Path]] = []
    for f in files:
        f_parts = [p.replace("-", "_") for p in f.parts]
        score = 0
        for i, c in enumerate(components):
            if c in f_parts:
                score += len(components) - i
        scored.append((score, f))
    return scored


def collect_module_files(module_path: Path) -> set[Path]:
    """Collect all Python source files within the module directory."""
    files: set[Path] = set()

    # Include important config files at workspace root
    workspace_root = module_path.parent.parent
    important_files = {
        "pyproject.toml",
        "README.md",
        "FRD.md",
        "ARCHITECTURE.md",
    }

    for f in workspace_root.iterdir():
        if f.is_file() and f.name in important_files:
            files.add(f)

    # Collect all .py files in the module
    src_dir = module_path / "src"
    if src_dir.exists():
        for f in src_dir.rglob("*.py"):
            if f.is_file():
                files.add(f)
    else:
        # Module without src/ subdir — collect from module dir itself
        for f in module_path.rglob("*.py"):
            if f.is_file():
                files.add(f)

    return files


def scan_python_imports(
    files: set[Path],
    module_to_files: dict[str, list[Path]],
    symbol_to_files: dict[str, list[Path]],
) -> set[Path]:
    """Scan source files for modules.shared imports and resolve them."""
    print("Scanning source files for imported shared dependencies...")

    # Pattern: from modules.shared import ... or from modules.shared.xxx import ...
    SHARED_IMPORT_PATTERN = re.compile(
        r"\b(?:from|import)\s+modules\.shared(?:\.([a-zA-Z0-9_]+))?"
    )

    extra: set[Path] = set()
    scanned: set[Path] = set()

    for f in files:
        if f.suffix != ".py" or f in scanned:
            continue
        scanned.add(f)
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            print(f"Warning: Failed to read file {f} for dependency analysis ({e})")
            continue

        for match in SHARED_IMPORT_PATTERN.finditer(content):
            sub_module = match.group(1)
            if sub_module:
                components = sub_module.split(".")
                extra.update(
                    resolve_dependency_files(components, module_to_files, symbol_to_files)
                )
    return extra


def write_markdown(
    output_path: Path,
    sorted_files: list[Path],
    workspace_root: Path,
    selected_module: str,
    safe_version: str,
) -> None:
    with open(output_path, "w", encoding="utf-8") as out:
        out.write(f"# Module: {selected_module} (v{safe_version})\n\n")
        out.write(
            f"This document contains the source code for module `{selected_module}` "
            f"along with its corresponding and imported definitions from the `shared` module.\n\n"
        )

        out.write("## File List\n\n")
        for f in sorted_files:
            rel = f.relative_to(workspace_root)
            out.write(f"- [{rel}]({f.as_uri()})\n")
        out.write("\n---\n\n")

        for f in sorted_files:
            rel = f.relative_to(workspace_root)
            out.write(f"## File: {rel}\n\n")
            lang = _language_for(f)
            out.write(f"```{lang}\n")
            try:
                content = f.read_text(encoding="utf-8", errors="replace")
                escaped = content.replace("```", "``` `")
                out.write(escaped)
                if not content.endswith("\n"):
                    out.write("\n")
            except OSError as e:
                out.write(f"/* Error reading file: {e} */\n")
            out.write("```\n\n---\n\n")


def _language_for(path: Path) -> str:
    """Pick a fenced-code-block language identifier based on file extension."""
    if path.name == "pyproject.toml":
        return "toml"
    if path.suffix == ".py":
        return "python"
    if path.suffix in (".js", ".ts"):
        return "javascript"
    return ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export a module into a single consolidated Markdown file."
    )
    parser.add_argument(
        "--module", "-m",
        help="Module name to export (non-interactive mode). Omit for interactive selection.",
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path (default: .agents/finding/<module>_v<ver>.md).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.module:
        # Non-interactive CLI mode
        workspace_root, modules_dir = resolve_workspace()

        modules = list_modules(modules_dir)
        if args.module not in modules:
            print(f"Error: Module '{args.module}' not found. Available: {', '.join(modules)}", file=sys.stderr)
            sys.exit(1)

        selected_module = args.module
        print(f"Processing module: {selected_module}...")

        module_path = modules_dir / selected_module
        version = read_version(workspace_root)
        safe_version = sanitize_version(version)
        print(f"Version resolved: {version} (filename-safe: {safe_version})")

        shared_src_dir = modules_dir / "shared" / "src"
        module_to_files, symbol_to_files = index_shared_module(shared_src_dir)

        files_to_export = collect_module_files(module_path)

        if args.output:
            output_path = Path(args.output)
        else:
            output_path = workspace_root / ".agents" / "finding" / f"{selected_module}_v{safe_version}.md"

        print(f"Writing export to {output_path}...")
        sorted_files = sorted(files_to_export)
        write_markdown(
            output_path,
            sorted_files,
            workspace_root,
            selected_module,
            safe_version,
        )

        print(f"\nSuccess! Consolidated markdown file created: {output_path}")
        return

    # Interactive mode
    while True:
        print("\n=== Blender MCP Module Exporter ===")

        workspace_root, modules_dir = resolve_workspace()

        modules = list_modules(modules_dir)
        if not modules:
            print("Error: No modules found in 'modules' directory.", file=sys.stderr)
            sys.exit(1)

        selected_module = prompt_module(modules)
        print(f"\nProcessing module: {selected_module}...")

        module_path = modules_dir / selected_module
        version = read_version(workspace_root)
        safe_version = sanitize_version(version)
        print(f"Version resolved: {version} (filename-safe: {safe_version})")

        shared_src_dir = modules_dir / "shared" / "src"
        module_to_files, symbol_to_files = index_shared_module(shared_src_dir)

        files_to_export = collect_module_files(module_path)

        output_path = workspace_root / ".agents" / "finding" / f"{selected_module}_v{safe_version}.md"

        print(f"Writing export to {output_path}...")
        sorted_files = sorted(files_to_export)
        write_markdown(
            output_path,
            sorted_files,
            workspace_root,
            selected_module,
            safe_version,
        )

        print(f"\nSuccess! Consolidated markdown file created: {output_path}")

        try:
            again = input("\nExport another module? (y/n): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        if again != "y":
            break

    print("Done.")


if __name__ == "__main__":
    main()
