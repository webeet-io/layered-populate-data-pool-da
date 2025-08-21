#!/usr/bin/env python3
"""
Check what tables actually exist
"""

import pandas as pd
import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from smart_db_connector_enhanced_V3 import db_connector

def check_actual_tables():
    """Check what tables actually exist"""
    print("📋 CHECKING ACTUAL TABLES")
    print("=" * 50)
    
    db = db_connector()
    
    # List all tables in test_berlin_data schema
    print("\n1. All tables in test_berlin_data schema:")
    tables_query = """
    SELECT table_name, table_type
    FROM information_schema.tables
    WHERE table_schema = 'test_berlin_data'
    ORDER BY table_name
    """
    
    all_tables = db.query(tables_query, show_info=False)
    print(f"   Found {len(all_tables)} tables:")
    
    # Check for our test table specifically
    test_tables = all_tables[all_tables['table_name'].str.contains('v3_test_table', case=False)]
    print(f"\n2. Tables matching 'v3_test_table':")
    if len(test_tables) > 0:
        for _, row in test_tables.iterrows():
            print(f"   - {row['table_name']} ({row['table_type']})")
    else:
        print("   None found")
    
    # Try to drop with different approaches
    print(f"\n3. Attempting different drop approaches:")
    
    # Approach 1: Simple drop
    try:
        db.query("DROP TABLE IF EXISTS v3_test_table", show_info=False)
        print("   ✅ Simple DROP succeeded")
    except Exception as e:
        print(f"   ❌ Simple DROP failed: {e}")
    
    # Approach 2: Schema-qualified drop
    try:
        db.query("DROP TABLE IF EXISTS test_berlin_data.v3_test_table", show_info=False)
        print("   ✅ Schema-qualified DROP succeeded")
    except Exception as e:
        print(f"   ❌ Schema-qualified DROP failed: {e}")
    
    # Approach 3: Drop with CASCADE
    try:
        db.query("DROP TABLE IF EXISTS test_berlin_data.v3_test_table CASCADE", show_info=False)
        print("   ✅ CASCADE DROP succeeded")
    except Exception as e:
        print(f"   ❌ CASCADE DROP failed: {e}")
    
    # Check again after drops
    print(f"\n4. Checking again after drops:")
    final_check = db.query("""
    SELECT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'test_berlin_data' AND table_name = 'v3_test_table'
    )
    """, show_info=False).iloc[0, 0]
    print(f"   Table exists after drops: {final_check}")
    
    db.close()

if __name__ == "__main__":
    check_actual_tables()