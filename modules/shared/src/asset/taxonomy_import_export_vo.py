"""Import/Export operation request and response value objects.

Re-exports merged VOs from taxonomy_asset_vo.py for backward compatibility.
"""

from .taxonomy_asset_vo import ExportModelVO, ImportGlbVO

# Legacy aliases — prefer the merged VO names above
ImportGlbRequestVO = ImportGlbVO
ImportGlbResponseVO = ImportGlbVO
ExportModelRequestVO = ExportModelVO
ExportModelResponseVO = ExportModelVO

__all__ = [
    "ExportModelVO",
    "ImportGlbVO",
]
