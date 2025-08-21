#!/usr/bin/env python3
"""
Manual cleanup and fresh V3 test
"""

import pandas as pd
import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from smart_db_connector_enhanced_V3 import db_connector

def manual_cleanup_and_test():
    """Manually clean up and test V3 functionality"""
    print("🧪 MANUAL CLEANUP AND V3 TEST")
    print("=" * 50)
    
    # Connect and drop table
    db = db_connector()
    print(f"\n1. Cleaning up table...")
    try:
        db.query("DROP TABLE IF EXISTS test_berlin_data.v3_test_table CASCADE", show_info=False)
        print("   ✅ Table dropped")
    except Exception as e:
        print(f"   ⚠️ Drop failed: {e}")
    
    # Check if table still exists
    tables_before = db.tables
    print(f"   Tables before: {'v3_test_table' in tables_before}")
    
    # Create test data
    print(f"\n2. Creating test data...")
    test_data = pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['Test 1', 'Test 2', 'Test 3'],
        'value': [10.5, 20.3, 30.7]
    })
    
    # Test upsert with table creation
    print(f"\n3. Testing upsert with fresh table creation...")
    result = db.populate(
        df=test_data,
        table_name='v3_test_table',
        schema='test_berlin_data',
        mode='upsert',
        primary_key=['id'],
        create_table=True,
        show_report=False
    )
    
    print(f"   Result: {result}")
    
    # Check table structure
    print(f"\n4. Checking table structure...")
    try:
        table_info = db.query("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = 'test_berlin_data' AND table_name = 'v3_test_table'
            ORDER BY ordinal_position
        """, show_info=False)
        print(f"   Columns: {len(table_info)}")
        for _, row in table_info.iterrows():
            print(f"     {row['column_name']}: {row['data_type']}")
        
        # Check constraints
        constraints = db.query("""
            SELECT constraint_name, constraint_type
            FROM information_schema.table_constraints
            WHERE table_schema = 'test_berlin_data' AND table_name = 'v3_test_table'
        """, show_info=False)
        print(f"   Constraints: {len(constraints)}")
        for _, row in constraints.iterrows():
            print(f"     {row['constraint_name']}: {row['constraint_type']}")
            
    except Exception as e:
        print(f"   ❌ Error checking structure: {e}")
    
    # Clean up
    db.query("DROP TABLE IF EXISTS test_berlin_data.v3_test_table CASCADE", show_info=False)
    db.close()

if __name__ == "__main__":
    manual_cleanup_and_test()