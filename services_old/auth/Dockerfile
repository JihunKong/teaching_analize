# Multi-stage build for AIBOA Authentication Service
FROM python:3.11-slim as builder

# Install system dependencies for compilation
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create and set working directory
WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

# Install runtime system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash aiboa

# Set working directory
WORKDIR /app

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/aiboa/.local

# Create data and log directories with proper permissions
RUN mkdir -p /app/data /var/log/aiboa && \
    chown -R aiboa:aiboa /app /var/log/aiboa

# Copy application code
COPY --chown=aiboa:aiboa . .

# Switch to non-root user
USER aiboa

# Ensure Python packages are in PATH
ENV PATH=/home/aiboa/.local/bin:$PATH

# Create health check script
RUN echo '#!/bin/bash\ncurl -f http://localhost:8002/health || exit 1' > /app/healthcheck.sh && chmod +x /app/healthcheck.sh

# Expose port
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD /app/healthcheck.sh

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002", "--workers", "1"]