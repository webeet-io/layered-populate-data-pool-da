# db_population_utils/__init__.py

"""
Database Population Utilities Package

This package provides comprehensive utilities for database connection management,
data processing, and population operations across multiple database environments.

Main Components:
- DBConnector: Advanced database connection management with pooling and monitoring
- DBSettings: Configuration management for database connections
- Custom exceptions for robust error handling

Usage:
    from db_population_utils import DBConnector, DBSettings
    
    # Basic usage
    settings = DBSettings.from_env("INGESTION_DB")
    connector = DBConnector(ingestion=settings)
    
    # Advanced usage with monitoring
    connector = DBConnector(
        config_file="config.yaml",
        echo=True,
        pool_size=10
    )
"""

from .db_connector import (
    # Core classes
    DBConnector,
    DBSettings,
    
    # Type definitions
    Target,
    
    # Custom exceptions
    DBConnectionError,
    DBConfigurationError,
    DBOperationError,
)

# Package metadata
__version__ = "0.1.0"
__author__ = "Your Team"
__description__ = "Comprehensive database population utilities"

# Public API - what gets imported with "from db_population_utils import *"
__all__ = [
    # Core classes
    "DBConnector",
    "DBSettings",
    
    # Type definitions
    "Target",
    
    # Exceptions
    "DBConnectionError",
    "DBConfigurationError", 
    "DBOperationError",
    
    # Package info
    "__version__",
]

# Convenience imports for common patterns
def create_connector_from_env(
    ingestion_prefix: str = "INGESTION_DB",
    app_prefix: str = "APP_DB",
    **kwargs
) -> DBConnector:
    """
    Convenience function to create DBConnector from environment variables.
    
    Args:
        ingestion_prefix: Environment variable prefix for ingestion DB
        app_prefix: Environment variable prefix for app DB
        **kwargs: Additional arguments passed to DBConnector
        
    Returns:
        Configured DBConnector instance
        
    Example:
        connector = create_connector_from_env(
            ingestion_prefix="PROD_INGESTION",
            app_prefix="PROD_APP",
            echo=True
        )
    """
    try:
        ingestion_settings = DBSettings.from_env(ingestion_prefix)
    except Exception:
        ingestion_settings = None
        
    try:
        app_settings = DBSettings.from_env(app_prefix)
    except Exception:
        app_settings = None
        
    return DBConnector(
        ingestion=ingestion_settings,
        app=app_settings,
        **kwargs
    )

def create_connector_from_config(
    config_path: str,
    **kwargs
) -> DBConnector:
    """
    Convenience function to create DBConnector from configuration file.
    
    Args:
        config_path: Path to configuration file (YAML/JSON)
        **kwargs: Additional arguments passed to DBConnector
        
    Returns:
        Configured DBConnector instance
        
    Example:
        connector = create_connector_from_config(
            "config/database.yaml",
            echo=True,
            pool_size=15
        )
    """
    return DBConnector(config_file=config_path, **kwargs)

# Add convenience functions to __all__
__all__.extend([
    "create_connector_from_env",
    "create_connector_from_config",
])

# Optional: Add logging configuration
import logging

# Set up package logger with null handler by default
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# Optional: Version check and compatibility warnings
import sys
import warnings

if sys.version_info < (3, 8):
    warnings.warn(
        "db_population_utils requires Python 3.8 or higher. "
        f"You are using Python {sys.version_info.major}.{sys.version_info.minor}.",
        UserWarning,
        stacklevel=2
    )

# Optional: Check for required dependencies
try:
    import sqlalchemy
    if tuple(map(int, sqlalchemy.__version__.split('.')[:2])) < (1, 4):
        warnings.warn(
            f"SQLAlchemy version {sqlalchemy.__version__} detected. "
            "db_population_utils works best with SQLAlchemy 1.4 or higher.",
            UserWarning,
            stacklevel=2
        )
except ImportError:
    warnings.warn(
        "SQLAlchemy not found. Please install it: pip install sqlalchemy",
        ImportWarning,
        stacklevel=2
    )

try:
    import pandas
except ImportError:
    warnings.warn(
        "Pandas not found. DataFrame operations will not be available. "
        "Install with: pip install pandas",
        ImportWarning,
        stacklevel=2
    )