FROM python:3.11-slim

# Install Haskell and ERD
RUN apt-get update && apt-get install -y \
    curl \
    ghc \
    cabal-install \
    graphviz \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

# Install ERD
RUN cabal update && cabal install --global erd

# Set working directory
WORKDIR /app

# Copy Python requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and test files
COPY src/ ./src/
COPY test_setup.py ./

# Create data directory
RUN mkdir -p /data/output

# Default entrypoint
ENTRYPOINT ["python", "src/main.py"]
