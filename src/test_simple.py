#!/usr/bin/env python3
"""
Connection test utility for MySQL database
"""

import json
import sys
import os

def load_config(config_path="/data/definition.json"):
    """Load database configuration from JSON file"""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"Error: Configuration file {config_path} not found")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {config_path}")
        return None

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
