"""
Public API for the Smart DB Connector package.

Provides:
- SmartDBConnector (aliased from db_connector)
- SmartReport for reporting
- Utility functions for creating connectors and running demos
"""

from .smart_db_connector import (
    db_connector as SmartDBConnector,
    db_connector,
    SmartReport,
    create_sample_connector,
    run_comprehensive_demo,
)

__all__ = [
    "SmartDBConnector",
    "db_connector",
    "SmartReport",
    "create_sample_connector",
    "run_comprehensive_demo",
]
