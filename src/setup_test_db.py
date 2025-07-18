#!/usr/bin/env python3
"""
Docker test script for ERD Plus
Sets up test database and runs ERD generation
"""

import mysql.connector
from mysql.connector import Error
import time
import os
import sys
import json

def load_config(config_path="/data/definition.json"):
    """Load database configuration from JSON file"""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"Error: Configuration file {config_path} not found")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {config_path}")
        sys.exit(1)

def wait_for_mysql(host, user, password, port=3306, max_retries=30):
    """Wait for MySQL to be ready"""
    log_file = "/data/output/setup_log.txt"
    
    print(f"🔍 Waiting for MySQL at {host}:{port}...")
    with open(log_file, "a") as f:
        f.write(f"🔍 Waiting for MySQL at {host}:{port}...\n")
        f.flush()
    
    for i in range(max_retries):
        try:
            print(f"⏳ Connection attempt {i+1}/{max_retries} to {host}:{port} with user '{user}'")
            with open(log_file, "a") as f:
                f.write(f"⏳ Connection attempt {i+1}/{max_retries} to {host}:{port} with user '{user}'\n")
                f.flush()
                
            connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                port=int(port),
                connect_timeout=10,
                autocommit=True
            )
            if connection.is_connected():
                db_info = connection.get_server_info()
                print(f"✅ MySQL is ready! Server version: {db_info}")
                with open(log_file, "a") as f:
                    f.write(f"✅ MySQL is ready! Server version: {db_info}\n")
                    f.flush()
                connection.close()
                return True
        except Error as e:
            error_msg = f"⏳ Waiting for MySQL... ({i+1}/{max_retries}) - Error: {e}"
            print(error_msg)
            with open(log_file, "a") as f:
                f.write(error_msg + "\n")
                f.flush()
            time.sleep(2)
        except Exception as e:
            error_msg = f"⏳ Unexpected error during connection attempt {i+1}: {e}"
            print(error_msg)
            with open(log_file, "a") as f:
                f.write(error_msg + "\n")
                f.flush()
            time.sleep(2)
    
    error_msg = "❌ Failed to connect to MySQL after maximum retries"
    print(error_msg)
    with open(log_file, "a") as f:
        f.write(error_msg + "\n")
        f.flush()
    return False

def create_test_database():
    """Create a test database with sample tables"""
    # Load configuration from definition.json
    config = load_config()
    
    host = config.get('host', 'mysql')
    password = config.get('password', 'testpassword')
    port = config.get('port', 3306)
    database = config.get('database', 'test_erd_plus')
    username = config.get('username', 'root')
    
    log_file = "/data/output/setup_log.txt"
    
    # 詳細な接続情報をログ出力
    connection_info = f"""
=== MySQL接続情報 (from definition.json) ===
host: {host}
port: {port}
database: {database}
username: {username}
password: {password}

=== definition.json 全設定 ===
"""
    
    # definition.jsonの全設定をログ出力
    for key, value in config.items():
        connection_info += f"{key}: {value}\n"
    
    print(connection_info)
    with open(log_file, "a") as f:
        f.write(connection_info + "\n")
        f.flush()
    
    print(f"Connecting to MySQL at {host}:{port} with user '{username}' and password '{password}'")
    
    if not wait_for_mysql(host, username, password, port):
        error_msg = "Failed to connect to MySQL after all retries"
        print(error_msg)
        with open(log_file, "a") as f:
            f.write(f"❌ {error_msg}\n")
            f.flush()
        sys.exit(1)
    
    try:
        print("Establishing main database connection...")
        with open(log_file, "a") as f:
            f.write("Establishing main database connection...\n")
            f.flush()
            
        connection = mysql.connector.connect(
            host=host,
            user=username,
            password=password,
            port=int(port),
            connect_timeout=30,
            autocommit=True
        )
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            connection_id = connection.connection_id
            print(f"✅ Connected to MySQL Server version {db_info} (Connection ID: {connection_id})")
            with open(log_file, "a") as f:
                f.write(f"✅ Connected to MySQL Server version {db_info} (Connection ID: {connection_id})\n")
                f.flush()
        
        cursor = connection.cursor()
        
        print("Creating and using test database...")
        with open(log_file, "a") as f:
            f.write("Creating and using test database...\n")
            f.flush()
            
        # Create test database
        cursor.execute(f"DROP DATABASE IF EXISTS {database}")
        print(f"✓ Dropped existing {database} database (if existed)")
        with open(log_file, "a") as f:
            f.write(f"✓ Dropped existing {database} database (if existed)\n")
            f.flush()
            
        cursor.execute(f"CREATE DATABASE {database}")
        print(f"✓ Created {database} database")
        with open(log_file, "a") as f:
            f.write(f"✓ Created {database} database\n")
            f.flush()
            
        cursor.execute(f"USE {database}")
        print(f"✓ Switched to {database} database")
        with open(log_file, "a") as f:
            f.write(f"✓ Switched to {database} database\n")
            f.flush()
        
        print("Creating tables with Japanese comments...")
        # Create sample tables
        tables = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ユーザーID',
                username VARCHAR(50) NOT NULL UNIQUE COMMENT 'ユーザー名',
                email VARCHAR(100) NOT NULL COMMENT 'メールアドレス',
                first_name VARCHAR(50) COMMENT '名前',
                last_name VARCHAR(50) COMMENT '姓',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '作成日時',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日時'
            ) COMMENT='ユーザー情報テーブル'
            """,
            """
            CREATE TABLE IF NOT EXISTS categories (
                id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'カテゴリID',
                name VARCHAR(50) NOT NULL COMMENT 'カテゴリ名',
                description TEXT COMMENT 'カテゴリの説明',
                parent_category_id INT COMMENT '親カテゴリID',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '作成日時',
                FOREIGN KEY (parent_category_id) REFERENCES categories(id) ON DELETE SET NULL
            ) COMMENT='カテゴリ情報テーブル'
            """,
            """
            CREATE TABLE IF NOT EXISTS posts (
                id INT AUTO_INCREMENT PRIMARY KEY COMMENT '投稿ID',
                title VARCHAR(200) NOT NULL COMMENT '投稿タイトル',
                content TEXT COMMENT '投稿内容',
                user_id INT NOT NULL COMMENT '投稿者ID',
                category_id INT COMMENT 'カテゴリID',
                published BOOLEAN DEFAULT FALSE COMMENT '公開フラグ',
                view_count INT DEFAULT 0 COMMENT '閲覧数',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '作成日時',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日時',
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
            ) COMMENT='投稿情報テーブル'
            """,
            """
            CREATE TABLE IF NOT EXISTS comments (
                id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'コメントID',
                content TEXT NOT NULL COMMENT 'コメント内容',
                post_id INT NOT NULL COMMENT '投稿ID',
                user_id INT NOT NULL COMMENT 'コメント投稿者ID',
                parent_comment_id INT COMMENT '親コメントID',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '作成日時',
                FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (parent_comment_id) REFERENCES comments(id) ON DELETE CASCADE
            ) COMMENT='コメント情報テーブル'
            """,
            """
            CREATE TABLE IF NOT EXISTS tags (
                id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'タグID',
                name VARCHAR(30) NOT NULL UNIQUE COMMENT 'タグ名',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '作成日時'
            ) COMMENT='タグ情報テーブル'
            """,
            """
            CREATE TABLE IF NOT EXISTS post_tags (
                post_id INT COMMENT '投稿ID',
                tag_id INT COMMENT 'タグID',
                PRIMARY KEY (post_id, tag_id),
                FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
            ) COMMENT='投稿とタグの関連テーブル'
            """
        ]
        
        for i, table_sql in enumerate(tables, 1):
            table_name = ["users", "categories", "posts", "comments", "tags", "post_tags"][i-1]
            print(f"Creating table {i}/{len(tables)}: {table_name}...")
            with open(log_file, "a") as f:
                f.write(f"Creating table {i}/{len(tables)}: {table_name}...\n")
                f.write(f"SQL: {table_sql[:100]}...\n")
                f.flush()
            try:
                cursor.execute(table_sql)
                print(f"✓ Table {table_name} created successfully")
                with open(log_file, "a") as f:
                    f.write(f"✓ Table {table_name} created successfully\n")
                    f.flush()
            except Error as table_error:
                error_msg = f"❌ Failed to create table {table_name}: {table_error}"
                print(error_msg)
                with open(log_file, "a") as f:
                    f.write(error_msg + "\n")
                    f.flush()
                raise table_error
        
        connection.commit()
        print(f"✅ Test database '{database}' created successfully!")
        print("Created tables:")
        print("- users (with user information) - ユーザー情報")
        print("- categories (with self-referencing parent relationship) - カテゴリ情報")
        print("- posts (related to users and categories) - 投稿情報")
        print("- comments (related to posts and users, with self-referencing parent) - コメント情報")
        print("- tags (for tagging system) - タグ情報")
        print("- post_tags (many-to-many relationship between posts and tags) - 投稿タグ関連")
        
        # Verify tables were created
        cursor.execute("SHOW TABLES")
        tables_list = cursor.fetchall()
        print(f"\n📋 Verified {len(tables_list)} tables created:")
        for table in tables_list:
            print(f"  - {table[0]}")
        
    except Error as e:
        error_msg = f"❌ Error creating test database: {e}"
        print(error_msg)
        with open(log_file, "a") as f:
            f.write(error_msg + "\n")
            f.flush()
        import traceback
        traceback_str = traceback.format_exc()
        print(traceback_str)
        with open(log_file, "a") as f:
            f.write(traceback_str + "\n")
            f.flush()
        sys.exit(1)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("🔌 Database connection closed")
            with open(log_file, "a") as f:
                f.write("🔌 Database connection closed\n")
                f.flush()

if __name__ == "__main__":
    print("DEBUG: Starting script execution...")
    
    # Create log file
    log_file = "/data/output/setup_log.txt"
    os.makedirs("/data/output", exist_ok=True)
    
    print("DEBUG: Created output directory and log file path")
    
    with open(log_file, "w") as f:
        f.write("🚀 Starting ERD Plus Database Setup\n")
        f.write("=" * 50 + "\n")
        f.flush()
    
    print("DEBUG: Initialized log file")
    
    try:
        print("🚀 Starting ERD Plus Database Setup")
        
        # ネットワーク診断情報を記録
        import subprocess
        network_info = """
=== ネットワーク診断情報 ===
"""
        
        # ホスト名解決テスト
        try:
            ping_result = subprocess.run(['ping', '-c', '1', 'mysql'], 
                                       capture_output=True, text=True, timeout=5)
            network_info += f"ping mysql: {ping_result.returncode} (0=success)\n"
            if ping_result.stdout:
                network_info += f"ping stdout: {ping_result.stdout}\n"
            if ping_result.stderr:
                network_info += f"ping stderr: {ping_result.stderr}\n"
        except Exception as e:
            network_info += f"ping mysql failed: {e}\n"
        
        # nslookupテスト
        try:
            nslookup_result = subprocess.run(['nslookup', 'mysql'], 
                                           capture_output=True, text=True, timeout=5)
            network_info += f"nslookup mysql: {nslookup_result.returncode}\n"
            if nslookup_result.stdout:
                network_info += f"nslookup stdout: {nslookup_result.stdout}\n"
        except Exception as e:
            network_info += f"nslookup mysql failed: {e}\n"
        
        # Dockerネットワーク情報
        try:
            netstat_result = subprocess.run(['netstat', '-rn'], 
                                          capture_output=True, text=True, timeout=5)
            network_info += f"netstat -rn:\n{netstat_result.stdout}\n"
        except Exception as e:
            network_info += f"netstat failed: {e}\n"
        
        print(network_info)
        with open(log_file, "a") as f:
            f.write(network_info + "\n")
            f.write(f"Python version: {sys.version}\n")
            f.write(f"Current working directory: {os.getcwd()}\n")
            f.flush()
        
        # Test MySQL connector
        try:
            import mysql.connector
            print("✅ MySQL connector imported successfully")
            with open(log_file, "a") as f:
                f.write("✅ MySQL connector imported successfully\n")
                f.flush()
        except ImportError as e:
            error_msg = f"❌ Failed to import MySQL connector: {e}"
            print(error_msg)
            with open(log_file, "a") as f:
                f.write(error_msg + "\n")
                f.flush()
            sys.exit(1)
        
        create_test_database()
        
    except Exception as e:
        error_msg = f"❌ Unexpected error: {e}"
        print(error_msg)
        import traceback
        traceback_str = traceback.format_exc()
        print(traceback_str)
        
        with open(log_file, "a") as f:
            f.write(error_msg + "\n")
            f.write(traceback_str + "\n")
            f.flush()
        sys.exit(1)
