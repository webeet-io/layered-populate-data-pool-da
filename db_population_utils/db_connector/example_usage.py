"""
Example usage of Interactive Smart DB Connector
"""

from smart_db_connector_enhanced import InteractiveDbConnector

def main():
    """Example of how to use the interactive connector"""
    
    print("🚀 INTERACTIVE DB CONNECTOR EXAMPLE")
    print("=" * 40)
    
    # Method 1: Simple connection (prompts for credentials if needed)
    db = InteractiveDbConnector()
    
    if db.engine:
        print("\n✅ Successfully connected!")
        
        # Show available schemas
        print(f"Available schemas: {db.schemas}")
        
        # Switch to a specific schema if available
        if db.schemas:
            target_schema = 'test_berlin_data' if 'test_berlin_data' in db.schemas else db.schemas[0]
            db.use(target_schema)
            
            # Show tables in current schema
            print(f"Tables in {target_schema}: {len(db.tables)} tables")
            
            # Example query
            try:
                result = db.query("SELECT current_schema() as schema, current_user as user")
                print("\nConnection info:")
                print(result)
            except Exception as e:
                print(f"Query error: {e}")
        
        # Clean up
        db.close()
        
    else:
        print("❌ Failed to connect to database")

if __name__ == "__main__":
    main()
