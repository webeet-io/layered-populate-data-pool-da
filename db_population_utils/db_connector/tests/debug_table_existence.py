#!/usr/bin/env python3
"""
Debug table existence check
"""

import pandas as pd
import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from smart_db_connector_enhanced_V3 import db_connector

def debug_table_existence():
    """Debug table existence checking"""
    print("🔍 DEBUGGING TABLE EXISTENCE CHECK")
    print("=" * 50)
    
    db = db_connector()
    
    # Drop table to ensure it doesn't exist
    print("\n1. Dropping table...")
    db.query("DROP TABLE IF EXISTS test_berlin_data.v3_test_table CASCADE", show_info=False)
    
    # Check via different methods
    print("\n2. Checking table existence via different methods:")
    
    # Method 1: Via self.tables (cached)
    cached_exists = 'v3_test_table' in db.tables
    print(f"   Cached check (self.tables): {cached_exists}")
    
    # Method 2: Via _table_exists method
    direct_exists = db._table_exists('v3_test_table', 'test_berlin_data')
    print(f"   Direct check (_table_exists): {direct_exists}")
    
    # Method 3: Direct SQL query
    check_sql = """
    SELECT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'test_berlin_data' AND table_name = 'v3_test_table'
    )
    """
    manual_check = db.query(check_sql, show_info=False).iloc[0, 0]
    print(f"   Manual SQL check: {manual_check}")
    
    # Refresh schema info
    print("\n3. Refreshing schema info...")
    db._refresh_schema_info('test_berlin_data')
    
    # Check again after refresh
    cached_exists_after = 'v3_test_table' in db.tables
    print(f"   Cached check after refresh: {cached_exists_after}")
    
    db.close()

if __name__ == "__main__":
    debug_table_existence()