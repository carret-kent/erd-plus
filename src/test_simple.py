#!/usr/bin/env python3
"""
Simple test script to check MySQL connection using definition.json
"""

import json
import sys
import os

def load_config(config_path="/data/definition.json"):
    """Load database configuration from JSON file"""
    print(f"Loading config from: {config_path}")
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        print(f"Config loaded successfully: {config}")
        return config
    except FileNotFoundError:
        print(f"Error: Configuration file {config_path} not found")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {config_path}")
        sys.exit(1)

def main():
    # Create log file to debug output issues
    log_file = "/data/output/test_log.txt"
    os.makedirs("/data/output", exist_ok=True)
    
    with open(log_file, "w") as f:
        f.write("=== Simple MySQL Connection Test ===\n")
        f.flush()
    
    print("=== Simple MySQL Connection Test ===")
    
    try:
        # Check if we can load config
        config = load_config()
        
        info = f"MySQL Host: {config.get('host')}\n"
        info += f"MySQL Port: {config.get('port')}\n"
        info += f"MySQL Database: {config.get('database')}\n"
        info += f"MySQL Username: {config.get('username')}\n"
        
        print(info)
        with open(log_file, "a") as f:
            f.write(info)
            f.flush()
        
        # Try to import mysql.connector
        try:
            import mysql.connector
            msg = "✅ MySQL connector imported successfully\n"
            print(msg)
            with open(log_file, "a") as f:
                f.write(msg)
                f.flush()
        except ImportError as e:
            error_msg = f"❌ Failed to import MySQL connector: {e}\n"
            print(error_msg)
            with open(log_file, "a") as f:
                f.write(error_msg)
                f.flush()
            return
        
        # Try to connect
        try:
            msg = "Attempting to connect...\n"
            print(msg)
            with open(log_file, "a") as f:
                f.write(msg)
                f.flush()
                
            connection = mysql.connector.connect(
                host=config.get('host'),
                port=config.get('port'),
                user=config.get('username'),
                password=config.get('password'),
                connect_timeout=10
            )
            
            if connection.is_connected():
                msg = "✅ Connected successfully!\n"
                print(msg)
                with open(log_file, "a") as f:
                    f.write(msg)
                    f.flush()
                    
                cursor = connection.cursor()
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()
                version_msg = f"MySQL version: {version[0]}\n"
                print(version_msg)
                with open(log_file, "a") as f:
                    f.write(version_msg)
                    f.flush()
                connection.close()
            
        except Exception as e:
            error_msg = f"❌ Connection failed: {e}\n"
            print(error_msg)
            with open(log_file, "a") as f:
                f.write(error_msg)
                f.flush()
    
    except Exception as e:
        error_msg = f"❌ Unexpected error: {e}\n"
        print(error_msg)
        with open(log_file, "a") as f:
            f.write(error_msg)
            f.flush()

if __name__ == "__main__":
    main()
