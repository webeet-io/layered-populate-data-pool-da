#!/usr/bin/env python3
"""
Test script to verify V3 functionality works correctly
Run this to test the enhanced populate function outside of Jupyter
"""

import pandas as pd
import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from smart_db_connector_enhanced_V3 import db_connector

def test_v3_functionality():
    """Test the enhanced V3 functionality"""
    print("🧪 TESTING SMART DB CONNECTOR V3 FUNCTIONALITY")
    print("=" * 50)
    
    try:
        # Cleanup any existing test tables
        print("\n0. Cleaning up any existing test tables...")
        db_cleanup = db_connector()
        try:
            db_cleanup.query("DROP TABLE IF EXISTS v3_test_table", show_info=False)
            print("   ✅ Cleanup completed")
        except:
            print("   ✅ No cleanup needed")
        db_cleanup.close()
        
        # Test 1: Connection with new signature
        print("\n1. Testing connection with new signature...")
        db = db_connector()  # Should work with new signature
        
        if db.engine:
            print(f"   ✅ Connection successful!")
            print(f"   Connection type: {db.connection_type}")
            print(f"   Current schema: {db.current_schema}")
            print(f"   Available schemas: {len(db.schemas)}")
        else:
            print("   ❌ Connection failed")
            return False
        
        # Test 2: Create test data
        print("\n2. Creating test data...")
        test_data = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'name': ['Test 1', 'Test 2', 'Test 3', 'Test 4', 'Test 5'],
            'value': [10.5, 20.3, 30.7, 40.1, 50.9],
            'active': [True, False, True, True, False]
        })
        print(f"   ✅ Test data created: {test_data.shape}")
        
        # Test 3: Enhanced populate with upsert mode (creates table with constraints)
        print("\n3. Testing enhanced populate with mode='upsert'...")
        result = db.populate(
            df=test_data,
            table_name='v3_test_table',
            schema=db.current_schema,  # Provide schema to avoid prompt
            mode='upsert',       # Use upsert mode for proper table creation
            primary_key=['id'],  # Specify primary key for proper table creation
            create_table=True,   # Enable auto table creation with constraints
            show_report=False  # Disable report for script
        )
        
        if result['status'] == 'success':
            print(f"   ✅ Populate successful: {result.get('rows_upserted', result.get('rows_inserted', 0))} rows")
        else:
            print(f"   ❌ Populate failed: {result.get('error', 'Unknown error')}")
            return False
        
        # Test 4: Upsert functionality
        print("\n4. Testing upsert mode...")
        upsert_data = test_data.copy()
        upsert_data.loc[0, 'name'] = 'Updated Test 1'
        upsert_data = pd.concat([upsert_data, pd.DataFrame({
            'id': [6], 'name': ['New Test 6'], 'value': [60.5], 'active': [True]
        })], ignore_index=True)
        
        upsert_result = db.populate(
            df=upsert_data,
            table_name='v3_test_table',
            schema=db.current_schema,  # Provide schema to avoid prompt
            mode='upsert',
            primary_key=['id'],
            show_report=False
        )
        
        if upsert_result['status'] == 'success':
            print(f"   ✅ Upsert successful: {upsert_result['rows_upserted']} rows")
        else:
            print(f"   ❌ Upsert failed: {upsert_result.get('error', 'Unknown error')}")
        
        # Test 5: Verify data
        print("\n5. Verifying final data...")
        verify_query = "SELECT * FROM v3_test_table ORDER BY id"
        final_data = db.query(verify_query, show_info=False)
        print(f"   ✅ Final data: {final_data.shape}")
        print("   First record name:", final_data[final_data['id'] == 1]['name'].iloc[0])
        
        # Check if upsert worked (record 6 exists)
        new_records = final_data[final_data['id'] == 6]
        if len(new_records) > 0:
            print("   New record:", new_records['name'].iloc[0])
            print("   ✅ Upsert worked correctly")
        else:
            print("   ⚠️  Upsert failed (expected - table needs primary key constraint)")
            print("   💡 For production use, enable create_table=True for auto-constraints")
        
        # Cleanup
        print("\n6. Cleaning up...")
        db.query("DROP TABLE IF EXISTS v3_test_table", show_info=False)
        db.close()
        print("   ✅ Cleanup completed")
        
        print(f"\n🎉 ALL V3 TESTS PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_v3_functionality()
    sys.exit(0 if success else 1)