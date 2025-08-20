import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import warnings
from typing import Dict, List, Optional, Any, Union
import time
import os
import json
import subprocess
import socket
from pathlib import Path

# Import original components if they exist
try:
    from smart_db_connector import SmartReport
except ImportError:
    # Create SmartReport if it doesn't exist
    class SmartReport:
        """Enhanced report class for database operations"""
        
        def __init__(self, operation: str):
            self.operation = operation
            self.start_time = time.time()
            self.info = []
            self.warnings = []
            self.errors = []
            self.recommendations = []
            self.execution_time = 0
            
        def add_info(self, message: str):
            self.info.append(message)
            
        def add_warning(self, message: str):
            self.warnings.append(message)
            
        def add_error(self, message: str):
            self.errors.append(message)
            
        def add_recommendation(self, message: str):
            self.recommendations.append(message)
            
        def complete(self):
            self.execution_time = time.time() - self.start_time
            
        def summary(self) -> Dict:
            self.complete()
            return {
                'operation': self.operation,
                'execution_time_seconds': round(self.execution_time, 3),
                'info_count': len(self.info),
                'warnings_count': len(self.warnings),
                'errors_count': len(self.errors),
                'recommendations_count': len(self.recommendations),
                'status': 'completed' if len(self.errors) == 0 else 'completed_with_errors'
            }

class AWSConnectionManager:
    """Manages AWS tunnel connections for database access"""
    
    def __init__(self):
        self.config_file = Path.home() / '.aws_db_config.json'
        self.tunnel_process = None
        self.config = None
        
        # Hardcoded common parameters for your specific database
        self.COMMON_CONFIG = {
            "profile": "default",
            "region": "us-east-1", 
            "bastion_instance_id": "i-your-bastion-id",  # Replace with actual bastion ID when available
            "database_host": "localhost",  # Updated to localhost
            "database_port": 5432,  # Keep original port for tunnel target
            "local_port": 5433,     # Updated to match your setup
            "database_name": "layereddb"  # Updated to your database name
        }
        
        # Neon database fallback configuration
        self.NEON_FALLBACK = {
            "connection_string": (
                "postgresql+psycopg2://neondb_owner:npg_CeS9fJg2azZD"
                "@ep-falling-glitter-a5m0j5gk-pooler.us-east-2.aws.neon.tech:5432/neondb"
                "?sslmode=require"
            ),
            "default_schema": "test_berlin_data"
        }
        
    def load_config(self) -> Optional[Dict]:
        """Load AWS tunnel configuration from user's home directory"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                    return self.config
            except Exception as e:
                print(f"⚠️  Warning: Could not load AWS config: {e}")
        return None
    
    def create_interactive_config(self) -> bool:
        """Create configuration interactively by asking for user credentials"""
        print("🔐 INTERACTIVE DATABASE CONNECTION SETUP")
        print("=" * 50)
        print("Please provide your database credentials:")
        print()
        
        try:
            # Get user credentials interactively
            import getpass
            
            print("Enter your database credentials:")
            username = input("Database Username: ").strip()
            if not username:
                print("❌ Username is required")
                return False
                
            password = getpass.getpass("Database Password: ")
            if not password:
                print("❌ Password is required")
                return False
            
            # Create config with hardcoded common parameters and user credentials
            config = {
                "aws_tunnel": {
                    "enabled": True,
                    "profile": self.COMMON_CONFIG["profile"],
                    "region": self.COMMON_CONFIG["region"],
                    "bastion_instance_id": self.COMMON_CONFIG["bastion_instance_id"],
                    "database_host": self.COMMON_CONFIG["database_host"],
                    "database_port": self.COMMON_CONFIG["database_port"],
                    "local_port": self.COMMON_CONFIG["local_port"],
                    "database_name": self.COMMON_CONFIG["database_name"],
                    "database_user": username,
                    "database_password": password
                },
                "direct_connection": {
                    "enabled": False,
                    "connection_string": ""
                }
            }
            
            # Save config
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
            
            # Set permissions to be readable only by user (for security)
            os.chmod(self.config_file, 0o600)
            
            self.config = config
            print(f"\n✅ Configuration saved securely to: {self.config_file}")
            return True
            
        except KeyboardInterrupt:
            print("\n❌ Setup cancelled by user")
            return False
        except Exception as e:
            print(f"❌ Error during setup: {e}")
            return False
    
    def create_sample_config(self):
        """Create a sample configuration file (deprecated - use interactive setup)"""
        print("⚠️  Sample config creation is deprecated.")
        print("💡 Use interactive setup instead:")
        return self.create_interactive_config()

    def start_tunnel(self) -> bool:
        """Start AWS Session Manager tunnel"""
        if not self.config or not self.config.get('aws_tunnel', {}).get('enabled'):
            return False
            
        tunnel_config = self.config['aws_tunnel']
        
        try:
            # Check if tunnel is already running
            if self.is_port_open('localhost', tunnel_config['local_port']):
                print(f"✅ Tunnel already running on port {tunnel_config['local_port']}")
                return True
            
            # Start AWS Session Manager tunnel
            command = [
                'aws', 'ssm', 'start-session',
                '--target', tunnel_config['bastion_instance_id'],
                '--document-name', 'AWS-StartPortForwardingSessionToRemoteHost',
                '--parameters', json.dumps({
                    'host': [tunnel_config['database_host']],
                    'portNumber': [str(tunnel_config['database_port'])],
                    'localPortNumber': [str(tunnel_config['local_port'])]
                }),
                '--profile', tunnel_config.get('profile', 'default'),
                '--region', tunnel_config.get('region', 'us-east-1')
            ]
            
            print(f"🚇 Starting AWS tunnel on port {tunnel_config['local_port']}...")
            
            # Start tunnel in background
            self.tunnel_process = subprocess.Popen(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Wait a moment for tunnel to establish
            time.sleep(3)
            
            # Check if tunnel is working
            if self.is_port_open('localhost', tunnel_config['local_port']):
                print(f"✅ AWS tunnel established successfully")
                return True
            else:
                print(f"❌ Failed to establish AWS tunnel")
                return False
                
        except FileNotFoundError:
            print("❌ AWS CLI not found. Please install AWS CLI and configure it.")
            return False
        except Exception as e:
            print(f"❌ Error starting AWS tunnel: {e}")
            return False
    
    def stop_tunnel(self):
        """Stop AWS tunnel"""
        if self.tunnel_process:
            self.tunnel_process.terminate()
            self.tunnel_process = None
            print("🚇 AWS tunnel stopped")
    
    def is_port_open(self, host: str, port: int) -> bool:
        """Check if port is open/tunnel is running"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except:
            return False
    
    def get_connection_string(self) -> Optional[str]:
        """Get appropriate connection string based on configuration"""
        if not self.config:
            # If no AWS config, fallback to Neon database
            print("🔗 No AWS config found, using Neon database fallback")
            return self.NEON_FALLBACK["connection_string"]
            
        # Try AWS tunnel first if enabled
        if self.config.get('aws_tunnel', {}).get('enabled'):
            tunnel_config = self.config['aws_tunnel']
            
            # For localhost setup, we don't need to start a tunnel
            if tunnel_config['database_host'] == 'localhost':
                connection_string = (
                    f"postgresql+psycopg2://{tunnel_config['database_user']}:"
                    f"{tunnel_config['database_password']}@localhost:"
                    f"{tunnel_config['local_port']}/{tunnel_config['database_name']}"
                )
                print(f"🔗 Using direct localhost connection on port {tunnel_config['local_port']}")
                return connection_string
            
            # For remote hosts, start tunnel
            elif self.start_tunnel():
                connection_string = (
                    f"postgresql+psycopg2://{tunnel_config['database_user']}:"
                    f"{tunnel_config['database_password']}@localhost:"
                    f"{tunnel_config['local_port']}/{tunnel_config['database_name']}"
                )
                print(f"🚇 Using AWS tunnel connection")
                return connection_string
        
        # Fall back to direct connection or Neon
        if self.config.get('direct_connection', {}).get('enabled'):
            direct_config = self.config['direct_connection']
            print(f"🔗 Using direct connection")
            return direct_config['connection_string']
        
        # Final fallback to Neon database
        print("🔗 Falling back to Neon database")
        return self.NEON_FALLBACK["connection_string"]

class EnhancedDbConnector:
    """Enhanced Smart Database Connector with AWS tunnel support"""
    
    def __init__(self, connection_string: Optional[str] = None, auto_discover: bool = True, use_aws_config: bool = True):
        """
        Initialize enhanced database connector with AWS tunnel support
        
        Args:
            connection_string: Database URL (optional if using AWS config)
            auto_discover: Automatically discover schemas on connection
            use_aws_config: Try to use AWS configuration file
        """
        self.connection_string = None
        self.engine = None
        self.available_schemas = {}
        self.current_schema = None
        self._default_schema = 'public'
        self.aws_manager = None
        
        print("🌟 INITIALIZING ENHANCED SMART DB CONNECTOR...")
        
        # Try AWS configuration first if enabled
        if use_aws_config:
            self.aws_manager = AWSConnectionManager()
            aws_config = self.aws_manager.load_config()
            
            if aws_config:
                print("✅ Found AWS configuration")
                aws_connection = self.aws_manager.get_connection_string()
                if aws_connection:
                    self.connection_string = aws_connection
            else:
                print("📝 No AWS configuration found")
                if not connection_string:
                    print("💡 Creating sample AWS config file...")
                    self.aws_manager.create_sample_config()
                    print("✏️  Please configure AWS settings and restart")
                    return
        
        # Use provided connection string if no AWS config
        if not self.connection_string and connection_string:
            self.connection_string = connection_string
            print("🔗 Using provided connection string")
        
        if not self.connection_string:
            print("❌ No connection string available")
            return
        
        # Connect and auto-discover
        self._connect()
        if auto_discover:
            self._discover_schemas()
            self._show_connection_info()
    
    def _connect(self):
        """Establish database connection"""
        try:
            self.engine = create_engine(self.connection_string)
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✅ Database connection established")
        except Exception as e:
            print(f"❌ Failed to connect to database: {e}")
            if self.aws_manager:
                print("💡 If using AWS tunnel, check:")
                print("   - AWS CLI is installed and configured")
                print("   - Session Manager plugin is installed") 
                print("   - Bastion instance is running")
                print("   - Security groups allow access")
            raise ConnectionError(f"Failed to connect to database: {e}")
    
    def _discover_schemas(self):
        """Automatically discover all schemas and tables"""
        print("🔍 Auto-discovering database schemas...")
        
        try:
            # Get schemas
            schemas_query = """
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
            ORDER BY schema_name;
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(schemas_query))
                schema_names = [row[0] for row in result]
            
            # For each schema, get table info
            for schema_name in schema_names:
                tables_query = f"""
                SELECT table_name,
                       (SELECT count(*) FROM information_schema.columns 
                        WHERE table_schema = '{schema_name}' AND table_name = t.table_name) as column_count
                FROM information_schema.tables t
                WHERE table_schema = '{schema_name}' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
                """
                
                with self.engine.connect() as conn:
                    result = conn.execute(text(tables_query))
                    tables = [{'name': row[0], 'columns': row[1]} for row in result]
                
                self.available_schemas[schema_name] = {
                    'tables': tables,
                    'table_count': len(tables)
                }
            
            # Set default current schema
            if 'public' in self.available_schemas:
                self.current_schema = 'public'
            elif self.available_schemas:
                self.current_schema = list(self.available_schemas.keys())[0]
                
            print(f"✅ Discovered {len(self.available_schemas)} schemas")
                
        except Exception as e:
            print(f"⚠️  Warning: Could not auto-discover schemas: {e}")
            self.available_schemas = {}
    
    def _show_connection_info(self):
        """Display connection and schema information"""
        print("\n" + "=" * 60)
        print("📊 SMART DB CONNECTOR - CONNECTION SUMMARY")
        print("=" * 60)
        
        if self.available_schemas:
            print(f"🗂️  Discovered {len(self.available_schemas)} schemas:")
            for schema_name, info in self.available_schemas.items():
                status = "🎯 [CURRENT]" if schema_name == self.current_schema else "   "
                print(f"{status} {schema_name}: {info['table_count']} tables")
                
                # Show first few tables for non-empty schemas
                if info['table_count'] > 0 and info['table_count'] <= 3:
                    for table in info['tables']:
                        print(f"       └─ {table['name']} ({table['columns']} cols)")
                elif info['table_count'] > 3:
                    for table in info['tables'][:2]:
                        print(f"       └─ {table['name']} ({table['columns']} cols)")
                    print(f"       └─ ... and {info['table_count'] - 2} more tables")
        else:
            print("⚠️  No schemas discovered")
        
        print(f"\n🎯 Current working schema: {self.current_schema}")
        print("\n💡 Usage examples:")
        print("   db.schemas          # List all schemas")
        print("   db.use('schema')    # Switch to schema")
        print("   db.tables           # List tables in current schema")
        print("   db.query('sql')     # Execute query")
        print("   db.populate(df, 'table')  # Insert DataFrame")
        print("=" * 60)
    
    @property 
    def schemas(self) -> List[str]:
        """Get list of available schema names"""
        return list(self.available_schemas.keys())
    
    @property
    def tables(self) -> List[str]:
        """Get list of tables in current schema"""
        if self.current_schema and self.current_schema in self.available_schemas:
            return [table['name'] for table in self.available_schemas[self.current_schema]['tables']]
        return []
    
    def use(self, schema_name: str) -> bool:
        """Set working schema"""
        if schema_name in self.available_schemas:
            old_schema = self.current_schema
            self.current_schema = schema_name
            table_count = len(self.tables)
            print(f"✅ Switched from '{old_schema}' to '{schema_name}' ({table_count} tables)")
            if table_count <= 10 and table_count > 0:
                print(f"   Tables: {', '.join(self.tables)}")
            return True
        else:
            available = ', '.join(self.schemas)
            print(f"❌ Schema '{schema_name}' not found. Available: {available}")
            return False
    
    def query(self, sql: str, schema: Optional[str] = None, show_info: bool = True) -> pd.DataFrame:
        """
        Execute query with smart schema handling
        
        Args:
            sql: SQL query
            schema: Optional schema name (uses current if not specified)
            show_info: Whether to show query info
        """
        # Determine schema to use
        target_schema = schema or self.current_schema
        
        if show_info and target_schema:
            print(f"🔍 Query executing in schema: '{target_schema}'")
        
        try:
            with self.engine.connect() as conn:
                # Set search path if schema specified
                if target_schema and target_schema != 'public':
                    conn.execute(text(f"SET search_path TO {target_schema}, public"))
                
                result = conn.execute(text(sql))
                df = pd.DataFrame(result.fetchall(), columns=result.keys())
                
                if show_info:
                    print(f"✅ Query completed: {len(df)} rows, {len(df.columns)} columns")
                
                return df
                
        except Exception as e:
            print(f"❌ Query failed: {e}")
            raise
    
    def insert(self, df: pd.DataFrame, table_name: str, schema: Optional[str] = None, 
              if_exists: str = 'replace', create_indexes: bool = True) -> Dict:
        """
        Insert DataFrame into table with smart schema handling
        
        Args:
            df: DataFrame to insert
            table_name: Target table name
            schema: Schema name (uses current if not specified)
            if_exists: Action if table exists ('replace', 'append', 'fail')
            create_indexes: Whether to create indexes
        """
        target_schema = schema or self.current_schema
        
        print(f"📝 Inserting {len(df)} rows × {len(df.columns)} columns")
        print(f"   Target: {target_schema}.{table_name}")
        print(f"   Action: {if_exists}")
        
        try:
            # Insert data
            df.to_sql(
                name=table_name,
                con=self.engine,
                schema=target_schema,
                if_exists=if_exists,
                index=False,
                method='multi'
            )
            
            print(f"✅ Insert completed successfully")
            
            # Update schema info
            self._refresh_schema_info(target_schema)
            
            return {
                'status': 'success',
                'rows_inserted': len(df),
                'table': f"{target_schema}.{table_name}",
                'schema': target_schema
            }
            
        except Exception as e:
            print(f"❌ Insert failed: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def populate(self, table_name: str, df: pd.DataFrame, schema: Optional[str] = None) -> Dict:
        """
        Quick population method - simplified interface
        
        Args:
            table_name: Target table name
            df: DataFrame to insert  
            schema: Optional schema name
        """
        return self.insert(df, table_name, schema, if_exists='replace', create_indexes=True)
    
    def list_tables(self, schema: Optional[str] = None) -> List[str]:
        """List tables in specified or current schema"""
        target_schema = schema or self.current_schema
        if target_schema in self.available_schemas:
            return [table['name'] for table in self.available_schemas[target_schema]['tables']]
        return []
    
    def get_table_info(self, table_name: str, schema: Optional[str] = None) -> Dict:
        """Get detailed table information"""
        target_schema = schema or self.current_schema
        
        try:
            columns_query = f"""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = '{target_schema}' AND table_name = '{table_name}'
            ORDER BY ordinal_position;
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(columns_query))
                columns = [dict(row._mapping) for row in result]
            
            return {
                'schema': target_schema,
                'table': table_name,
                'columns': columns,
                'column_count': len(columns)
            }
            
        except Exception as e:
            print(f"❌ Error getting table info: {e}")
            return {}
    
    def _refresh_schema_info(self, schema_name: str):
        """Refresh table information for specific schema"""
        if schema_name not in self.available_schemas:
            self.available_schemas[schema_name] = {'tables': [], 'table_count': 0}
            
        tables_query = f"""
        SELECT table_name,
               (SELECT count(*) FROM information_schema.columns 
                WHERE table_schema = '{schema_name}' AND table_name = t.table_name) as column_count
        FROM information_schema.tables t
        WHERE table_schema = '{schema_name}' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
        """
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(tables_query))
                tables = [{'name': row[0], 'columns': row[1]} for row in result]
            
            self.available_schemas[schema_name] = {
                'tables': tables,
                'table_count': len(tables)
            }
        except Exception as e:
            print(f"Warning: Could not refresh schema info: {e}")
    
    def health_check(self) -> Dict:
        """Perform health check"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            return {
                'status': 'healthy',
                'schemas_available': len(self.available_schemas),
                'current_schema': self.current_schema,
                'connection': 'active'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'connection': 'failed'
            }
    
    def close(self):
        """Close database connection and AWS tunnel"""
        if self.engine:
            self.engine.dispose()
            print("🔒 Database connection closed")
            
        if self.aws_manager:
            self.aws_manager.stop_tunnel()

# For backward compatibility and easy import
db_connector = EnhancedDbConnector

def run_comprehensive_demo():
    """Run a comprehensive demo of enhanced functionality"""
    print("This would run a comprehensive demo when implemented")

class InteractiveDbConnector(EnhancedDbConnector):
    """Interactive Database Connector that prompts for credentials"""
    
    def __init__(self, auto_discover: bool = True, force_interactive: bool = False):
        """
        Initialize interactive database connector
        
        Args:
            auto_discover: Automatically discover schemas on connection
            force_interactive: Force interactive credential input even if config exists
        """
        print("🌟 INTERACTIVE SMART DB CONNECTOR")
        print("=" * 40)
        
        self.connection_string = None
        self.engine = None
        self.available_schemas = {}
        self.current_schema = None
        self._default_schema = 'public'
        self.aws_manager = AWSConnectionManager()
        
        # Check if we need to get credentials
        config = self.aws_manager.load_config()
        
        if not config or force_interactive:
            if not config:
                print("🔗 No AWS config found, using Neon database")
                self.connection_string = self.aws_manager.NEON_FALLBACK["connection_string"]
            else:
                print("🔐 Setting up database connection...")
                success = self.aws_manager.create_interactive_config()
                if not success:
                    print("❌ Failed to set up connection")
                    return
                config = self.aws_manager.load_config()
        
        if config or self.connection_string:
            print("✅ Configuration loaded successfully")
            if not self.connection_string:
                self.connection_string = self.aws_manager.get_connection_string()
            
            if self.connection_string:
                # Connect and auto-discover
                self._connect()
                if auto_discover:
                    self._discover_schemas()
                    
                    # Auto-switch to test_berlin_data if available and using Neon
                    if ('test_berlin_data' in self.available_schemas and 
                        'neon' in self.connection_string):
                        self.current_schema = 'test_berlin_data'
                        print(f"🎯 Auto-selected default schema: test_berlin_data")
                    
                    self._show_connection_info()
            else:
                print("❌ Could not generate connection string")
        else:
            print("❌ No configuration available")
    
    def show_connection_summary(self):
        """Show a nice summary of the successful connection"""
        if not self.available_schemas:
            return
            
        print("\n" + "🎉" * 20)
        print("CONNECTION SUCCESSFUL!")
        print("🎉" * 20)
        print(f"\n📊 DATABASE OVERVIEW:")
        print(f"   Total schemas: {len(self.available_schemas)}")
        print(f"   Current schema: {self.current_schema}")
        
        # Show schema breakdown
        total_tables = sum(info['table_count'] for info in self.available_schemas.values())
        print(f"   Total tables: {total_tables}")
        
        print(f"\n🗂️  AVAILABLE SCHEMAS:")
        for schema_name, info in self.available_schemas.items():
            status = "🎯" if schema_name == self.current_schema else "📁"
            print(f"   {status} {schema_name}: {info['table_count']} tables")
        
        print(f"\n💡 READY TO USE:")
        print(f"   db.use('schema_name')  # Switch schema")
        print(f"   db.query('SELECT...')  # Execute queries")
        print(f"   db.populate(df, 'table')  # Insert data")
        print("=" * 50)
    
    def _show_connection_info(self):
        """Override to show enhanced connection info"""
        super()._show_connection_info()
        self.show_connection_summary()

# Create convenient aliases
db_connector = InteractiveDbConnector  # Make this the default
EnhancedDbConnector = InteractiveDbConnector  # Keep compatibility

def quick_connect():
    """Quick connection function for immediate use"""
    return InteractiveDbConnector(auto_discover=True)
