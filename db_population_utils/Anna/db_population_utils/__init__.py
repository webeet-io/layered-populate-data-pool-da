# db_population_utils/__init__.py
"""
Top-level public API for db_population_utils.

This re-exports the orchestrator and core cleaning/validation utilities,
so users can simply do:

    from db_population_utils import DataProcessor
"""

from .data_processor.data_processor import DataProcessor
from .data_processor.column_standardizer import ColumnStandardizer
from .data_processor.webscraping_cleaner import WebscrapingDataCleaner
from .data_processor.ml_data_preparer import MLDataPreparer

# Optional / validation helpers
try:
    from .data_processor.basic_geo_validator import BasicGeoValidator, GeoBounds
except Exception:  # pragma: no cover
    BasicGeoValidator = None  # type: ignore
    GeoBounds = None  # type: ignore

try:
    from .data_processor.berlin_data_validator import BerlinDataValidator
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


