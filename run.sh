#!/bin/bash
# Build and run ERD Plus locally for testing

echo "Building ERD Plus Docker image..."
docker build -t erd-plus .

echo "Running ERD Plus..."
docker run --rm -v $(pwd)/data:/data erd-plus
