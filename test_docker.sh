#!/bin/bash
# Docker test script for ERD Plus

echo "🚀 Starting ERD Plus Test with Graphviz..."

# Build and start services
echo "📦 Building Docker images..."
docker-compose build --no-cache

echo "🐬 Starting MySQL..."
docker-compose up -d mysql

# Wait for MySQL to be ready
echo "⏳ Waiting for MySQL to be ready..."
sleep 15

# Setup test database
echo "🗄️ Setting up test database..."
docker-compose run --rm erd-plus python src/setup_test_db.py

# Run ERD generation
echo "🎨 Generating ERD..."
docker-compose run --rm erd-plus

echo "✅ Test completed! Check data/output/ for results."

# Show generated files
echo "📁 Generated files:"
ls -la data/output/ || echo "No output directory found"

# Show content if available
if [ -f "data/output/schema.er" ]; then
    echo "📄 Generated ERD file content:"
    head -20 data/output/schema.er
fi

# Cleanup
echo "🧹 Cleaning up..."
docker-compose down -v
