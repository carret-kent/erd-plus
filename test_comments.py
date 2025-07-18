#!/usr/bin/env python3
"""
Test script to check Japanese comment extraction
"""

from src.db_connector import MySQLSchemaExtractor
from src.erd_generator import ERDGenerator
import json

def test_japanese_comments():
    config = {
        'host': 'mysql',
        'port': 3306,
        'database': 'test_erd_plus',
        'username': 'root',
        'password': 'testpassword',
        'schema': 'test_erd_plus'
    }
    
    print("🔍 Testing Japanese comment extraction...")
    
    # Extract schema
    extractor = MySQLSchemaExtractor(config)
    schema_data = extractor.extract_schema()
    
    print(f"📊 Found tables: {list(schema_data['tables'].keys())}")
    
    # Check users table columns
    if 'users' in schema_data['tables']:
        print("\n👤 Users table columns:")
        for col in schema_data['tables']['users']['columns']:
            comment = col.get('COLUMN_COMMENT', 'No comment')
            print(f"  - {col['COLUMN_NAME']}: {col['DATA_TYPE']} -> Comment: '{comment}'")
    
    # Test ERD generation
    print("\n🎨 Generating ERD with Japanese comments...")
    erd_generator = ERDGenerator(schema_data)
    
    # Test column formatting
    if 'users' in schema_data['tables']:
        print("\n📝 Formatted columns:")
        for col in schema_data['tables']['users']['columns']:
            formatted = erd_generator._format_column_name(col)
            print(f"  {formatted}")

if __name__ == "__main__":
    test_japanese_comments()
