# ERD Plus Makefile
# MySQL Schema to ERD Generation System

.PHONY: help setup up down run clean logs status test example

# デフォルトターゲット
help:
	@echo "ERD Plus - MySQL Schema to ERD Generation System"
	@echo ""
	@echo "Available commands:"
	@echo "  setup     - 初期セットアップ（definition.json作成）"
	@echo "  up        - Docker環境起動"
	@echo "  down      - Docker環境停止"
	@echo "  run       - ERD生成実行"
	@echo "  all       - Docker起動からERD生成まで一括実行"
	@echo "  test      - データベース接続テスト"
	@echo "  clean     - 生成物とDocker環境をクリーンアップ"
	@echo "  logs      - Dockerコンテナのログ表示"
	@echo "  status    - Docker環境の状態確認"
	@echo "  example   - サンプル設定ファイル表示"
	@echo ""

# 初期セットアップ
setup:
	@echo "🔧 ERD Plus 初期セットアップ"
	@if [ ! -f src/.env ]; then \
		echo "📝 .envファイルを作成します..."; \
		cp src/.env.example src/.env; \
		echo "✅ src/.env を作成しました"; \
		echo "⚠️  データベース接続情報を編集してください"; \
	else \
		echo "✅ .env は既に存在します"; \
	fi
	@echo "🐳 Dockerイメージをビルドします..."
	@docker compose build
	@echo "✅ セットアップ完了！"

# Docker環境起動
up:
	@echo "🐳 Docker環境を起動します..."
	@docker compose up -d
	@echo "⏳ MySQL起動を待機中..."
	@sleep 10
	@echo "✅ Docker環境が起動しました"

# Docker環境停止
down:
	@echo "🛑 Docker環境を停止します..."
	@docker compose down
	@echo "✅ Docker環境を停止しました"

# ERD生成実行
run:
	@echo "🚀 ERD生成を開始します..."
	@docker compose exec erd-plus python /app/src/main.py
	@echo "✅ ERD生成が完了しました！"
	@echo "📁 生成物は data/output/ ディレクトリを確認してください"

# 一括実行（Docker起動 → ERD生成）
all: up
	@sleep 5
	@$(MAKE) run

# データベース接続テスト
test:
	@echo "🔍 データベース接続テストを実行します..."
	@docker compose exec erd-plus python /app/src/test_simple.py

# クリーンアップ
clean:
	@echo "🧹 クリーンアップを開始します..."
	@echo "🗑️  生成物を削除中..."
	@rm -rf data/output/*
	@echo "🐳 Docker環境をクリーンアップ中..."
	@docker compose down --volumes --remove-orphans
	@docker system prune -f
	@echo "✅ クリーンアップが完了しました"

# Dockerログ表示
logs:
	@echo "📋 Dockerコンテナのログを表示します..."
	@docker compose logs -f

# Docker環境状態確認
status:
	@echo "📊 Docker環境の状態:"
	@docker compose ps
	@echo ""
	@echo "🗂️  生成物の状態:"
	@if [ -d "data/output" ]; then \
		find data/output -name "*.er" -o -name "*.pdf" -o -name "*.md" | head -10; \
	else \
		echo "生成物はまだありません"; \
	fi

# サンプル設定表示
example:
	@echo "📋 .env サンプル設定:"
	@echo ""
	@cat src/.env.example
	@echo ""
	@echo "💡 この設定を src/.env にコピーして編集してください"

# 開発用：ソースコード変更後の再起動
restart:
	@echo "🔄 ERD Plusコンテナを再起動します..."
	@docker compose restart erd-plus
	@echo "✅ 再起動完了"

# 開発用：コンテナ内でbashを起動
shell:
	@echo "🖥️  ERD Plusコンテナに接続します..."
	@docker compose exec erd-plus bash

# 生成物の確認
show:
	@echo "📁 最新の生成物:"
	@find data/output -type f \( -name "*.er" -o -name "*.pdf" -o -name "*.md" \) -exec ls -la {} \; 2>/dev/null || echo "生成物がありません"
