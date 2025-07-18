#!/usr/bin/env python3
"""
Test script for ERD Plus
Creates a sample MySQL database and runs the ERD generation process
"""

import mysql.connector
from mysql.connector import Error
import json
import os

def create_test_database():
    """Create a test database with sample tables"""
    try:
        # Connect to MySQL server (without specifying database)
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='password'  # Change this to your MySQL root password
        )
        
        cursor = connection.cursor()
        
        # Create test database
        cursor.execute("CREATE DATABASE IF NOT EXISTS test_erd_plus")
        cursor.execute("USE test_erd_plus")
        
        # Create sample tables
        tables = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                email VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS categories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS posts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                content TEXT,
                user_id INT NOT NULL,
                category_id INT,
                published BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS comments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                content TEXT NOT NULL,
                post_id INT NOT NULL,
                user_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        ]
        
        for table_sql in tables:
            cursor.execute(table_sql)
        
        connection.commit()
        print("Test database 'test_erd_plus' created successfully!")
        
        # Create test configuration file
        config = {
            "host": "localhost",
            "port": 3306,
            "database": "test_erd_plus",
            "username": "root",
            "password": "password",  # Change this to your MySQL root password
            "schema": "test_erd_plus"
        }
        
        with open('/tmp/test_definition.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print("Test configuration saved to /tmp/test_definition.json")
        
    except Error as e:
        print(f"Error creating test database: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    create_test_database()
