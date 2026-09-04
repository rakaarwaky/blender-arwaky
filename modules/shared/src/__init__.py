"""Shared domain package.

Shared contracts, taxonomy, and utilities are imported from their canonical
feature modules, for example ``modules.shared.src.common.taxonomy_core_vo``.
The former root-level re-export surface is intentionally removed; new code must
use explicit domain imports.
"""

__all__: list[str] = []
