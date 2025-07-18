#!/usr/bin/env python3
"""
Connection test utility for MySQL database
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

def load_config():
    """Load database configuration from .env file"""
    # Load .env file from the same directory as this script
    env_path = Path(__file__).parent / '.env'
    
    if not env_path.exists():
        print(f"Error: Configuration file {env_path} not found")
        return None
    
    load_dotenv(env_path)
    
    config = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT', '3306')),
        'database': os.getenv('DB_DATABASE'),
        'username': os.getenv('DB_USERNAME'),
        'password': os.getenv('DB_PASSWORD', ''),
        'schema': os.getenv('DB_SCHEMA')
    }
    
    return config

def test_mysql_connection(config=None, verbose=False):
    """
    Test MySQL connection with the given configuration
    Returns True if connection successful, False otherwise
    """
    if config is None:
        config = load_config()
        if config is None:
            return False
    
    if verbose:
        print("=== MySQL Connection Test ===")
        print(f"Host: {config.get('host')}")
        print(f"Port: {config.get('port')}")
        print(f"Database: {config.get('database')}")
        print(f"Username: {config.get('username')}")
    
    try:
        # Try to import mysql.connector
        import mysql.connector
        if verbose:
            print("✅ MySQL connector imported successfully")
    except ImportError as e:
        if verbose:
            print(f"❌ Failed to import MySQL connector: {e}")
        return False
    
    # Try to connect
    try:
        if verbose:
            print("Attempting to connect...")
            
        connection = mysql.connector.connect(
            host=config.get('host'),
            port=config.get('port'),
            user=config.get('username'),
            password=config.get('password'),
            connect_timeout=10
        )
        
        if connection.is_connected():
            if verbose:
                print("✅ Connected successfully!")
                cursor = connection.cursor()
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()
                print(f"MySQL version: {version[0]}")
            connection.close()
            return True
    
    except Exception as e:
        if verbose:
            print(f"❌ Connection failed: {e}")
        return False
    
    return False

def main():
    """Standalone test when run directly"""
    config = load_config()
    if config is None:
        sys.exit(1)
    
    success = test_mysql_connection(config, verbose=True)
    if success:
        print("Connection test completed successfully!")
        sys.exit(0)
    else:
        print("Connection test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
