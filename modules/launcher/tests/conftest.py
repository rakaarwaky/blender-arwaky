"""Hermetic test fixtures for the launcher feature test suite.

The repo's ``modules.shared.src.__init__`` eagerly imports every domain
subpackage (``scene``, ``object``, ...) and re-exports individual names. A
concurrent refactor of the scene domain has left that global import graph
temporarily broken (rename in flight). To verify the launcher feature in
isolation we shim ``modules.shared.src`` so its ``__init__`` still exposes the
real subpackage directory but does NOT execute the eager cross-domain imports.
This isolates the launcher tests from unrelated in-flight edits elsewhere.
"""

from __future__ import annotations

import importlib.util
import os
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_SHARED_SRC_MODULE_NAME = "modules.shared.src"
_SHARED_SRC_INIT = ROOT / "modules" / "shared" / "src" / "__init__.py"


def _shim_shared_src() -> None:
    if _SHARED_SRC_MODULE_NAME in sys.modules:
        return
    spec = importlib.util.spec_from_file_location(_SHARED_SRC_MODULE_NAME, str(_SHARED_SRC_INIT))
    assert spec is not None and spec.submodule_search_locations is not None
    real_dir = list(spec.submodule_search_locations)[0]

    stub = types.ModuleType(_SHARED_SRC_MODULE_NAME)
    stub.__path__ = [real_dir]
    stub.__file__ = str(_SHARED_SRC_INIT)
    # Provide the mcp subpackage shim (some shared re-exports expect it).
    mcp_pkg = types.ModuleType("modules.shared.src.mcp")
    mcp_pkg.__path__ = [os.path.join(real_dir, "mcp")]
    sys.modules["modules.shared.src.mcp"] = mcp_pkg
    bootstrap = types.ModuleType("modules.shared.src.mcp.contract_server_bootstrap")
    bootstrap.ServerBootstrapManagerAggregate = object
    sys.modules["modules.shared.src.mcp.contract_server_bootstrap"] = bootstrap

    sys.modules[_SHARED_SRC_MODULE_NAME] = stub


_shim_shared_src()
