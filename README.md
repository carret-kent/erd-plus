# ERD Plus
このプロジェクトは、MySQLデータベースにアクセスし、指定されたスキーマ情報を自動取得してHaskell ERDを使用したER図を自動生成することを目的としています。
また、作成した中間ファイルの.erファイルをMarkdown形式に変換することでLLMの取り込みも簡易的に行えるようにしています。

# About ERD?
https://hackage.haskell.org/package/erd
https://github.com/BurntSushi/erd

上記サイトで掲載されているERDを使いER図を自動生成することを目的としています。

```
[Person]
*name {label: "varchar(50), unique, not null"}
height {label: "int(11)"}
weight {label: "decimal(5,2)"}
+birth_location_id {label: "int(11), not null, foreign key"}

[Location]
*id {label: "int(11), auto_increment, primary key"}
city {label: "varchar(100), not null"}
state {label: "varchar(50)"}
country {label: "varchar(50), not null"}

# Each relationship must be between exactly two entities, which
# need not be distinct. Each entity in the relationship has
# exactly one of four possible cardinalities:
#
# Cardinality    Syntax
# 0 or 1         0
# exactly 1      1
# 0 or more      *
# 1 or more      +
Person *--1 Location
```

# Step
1. MySQLデータベースから指定されたスキーマ情報を自動取得
2. 取得したスキーマ情報から、label属性付きのerファイルを作成する
3. erファイルから、HaskellのERDを実行し、pdf形式でER図を出力します
4. erファイルをMarkdown形式に変換し出力します

# Structure
1. データベース接続・スキーマ取得
- Pythonスクリプトを使用して、MySQLデータベースから指定されたスキーマのテーブル定義、カラム情報、リレーション情報を取得します。
2. erファイル作成
- 取得したスキーマ情報から、Pythonスクリプトを使用してlabel属性付きの.erファイルを作成します。
- label属性には、カラムの型(文字数制限)、unique制約、not null指定、コメントなどの詳細情報を含めます。
3. ER図生成
- HaskellのERDを使用して、.erファイルからPDF形式のER図を生成
4. Markdown変換
- Pythonスクリプトを使用して、.erファイルをMarkdown形式に変換します。

# How to use
1. Docker imgをビルドします。
```bash
docker build -t erd-plus .
```
2. データベース接続情報とスキーマ情報を`/data/definition.json`に配置します。(/data/definition.jsonの例は、`data/definition.json.example`を参照してください)
3. Dockerコンテナを起動します。
```bash
docker run --rm -v $(pwd)/data:/data erd-plus
```
4. `/data/output/`に生成されたER図（PDF）とMarkdownファイルが出力されます

# Configuration
`data/definition.json`には以下の情報を記載してください：
```json
{
  "host": "localhost",
  "port": 3306,
  "database": "your_database_name",
  "username": "your_username",
  "password": "your_password",
  "schema": "your_schema_name"
}
```

# Label Attribute Format
ERD Plusは、カラムの詳細情報をlabel属性として出力します。label属性の形式は以下の通りです：

```
column_name {label: "データ型(制限), 制約1, 制約2, コメント"}
```

## Label構成要素
- **データ型**: varchar(255), int(11), decimal(5,2) など
- **制約情報**: unique, not null, auto_increment, primary key, foreign key など
- **コメント**: カラムの説明（MySQLのCOMMENT属性から取得、日本語対応）
- **区切り文字**: 各要素は `,` (カンマ+スペース) で区切られます

## Label例
```
*id {label: "int(11), auto_increment, primary key"}
+username {label: "varchar(50), unique, not null, ユーザー名"}
email {label: "varchar(100), not null, メールアドレス"}
created_at {label: "timestamp, default current_timestamp, 作成日時"}
description {label: "text, 商品の詳細説明"}
```