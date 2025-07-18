FROM python:3.11-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    graphviz \
    default-mysql-client \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Download pre-built ERD binary (if available) or use alternative approach
# For now, we'll create a mock ERD implementation for testing
RUN mkdir -p /usr/local/bin

# Set working directory
WORKDIR /app

# Copy Python requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Create data directory
RUN mkdir -p /data/output

# Default command - keep container running
CMD ["sleep", "infinity"]
