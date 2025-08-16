# Multi-stage build for production optimization
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
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash aiboa

# Set working directory
WORKDIR /app

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/aiboa/.local

# Create data directory with proper permissions
RUN mkdir -p /app/data && chown -R aiboa:aiboa /app

# Copy application code
COPY --chown=aiboa:aiboa . .

# Switch to non-root user
USER aiboa

# Ensure Python packages are in PATH
ENV PATH=/home/aiboa/.local/bin:$PATH

# Create health check script
RUN echo '#!/bin/bash\ncurl -f http://localhost:8000/health || exit 1' > /app/healthcheck.sh && chmod +x /app/healthcheck.sh

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD /app/healthcheck.sh

# Run the application (use working implementation)
CMD ["uvicorn", "main_working:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]