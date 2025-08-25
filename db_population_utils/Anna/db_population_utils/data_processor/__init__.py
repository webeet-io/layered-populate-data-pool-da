# db_population_utils/data_processor/__init__.py
"""
Public API for the data_processor subpackage.

Import from here in tests and user code, e.g.:
    from db_population_utils.data_processor import DataProcessor
"""

from .data_processor import DataProcessor
from .column_standardizer import ColumnStandardizer
from .webscraping_cleaner import WebscrapingDataCleaner
from .ml_data_preparer import MLDataPreparer

# Geo / validation helpers (export whichever validators you keep)
try:
    from .basic_geo_validator import BasicGeoValidator, GeoBounds  # preferred lightweight validator
except Exception:  # pragma: no cover
    BasicGeoValidator = None  # type: ignore
    GeoBounds = None  # type: ignore

# Optional: if you keep a Berlin-specific validator module, re-export it too.
try:
    from .berlin_data_validator import BerlinDataValidator  # noqa: F401
except Exception:  # pragma: no cover
    BerlinDataValidator = None  # type: ignore

__all__ = [
    "DataProcessor",
    "ColumnStandardizer",
    "WebscrapingDataCleaner",
    "MLDataPreparer",
    "BasicGeoValidator",
    "GeoBounds",
    "BerlinDataValidator",
]


