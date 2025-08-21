"""
Public API for the Smart DB Connector V3 package.

This module exposes the main connector class, utility functions, and custom exceptions
for easy access when the package is imported.
"""

from .smart_db_connector_enhanced_V3 import (
    # The main class for database connections
    SmartDbConnectorV3,
    
    # A convenient alias for the main class
    db_connector,
    
    # A quick-start function to get a connector instance
    quick_connect,
    
    # Custom exception for connection-related errors
    DatabaseConnectionError,
    
    # Custom exception for schema-related errors
    SchemaError,

    # Standalone class for generating operation reports
    SmartReport,

    # A function to demonstrate the connector's usage
    demo_usage
)

# The __all__ list defines the public API of the package.
# Only these names will be imported when a user does 'from your_package import *'
__all__ = [
    "SmartDbConnectorV3",
    "db_connector",
    "quick_connect",
    "DatabaseConnectionError",
    "SchemaError",
    "SmartReport",
    "demo_usage"
]
