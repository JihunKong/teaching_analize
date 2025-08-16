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

# Copy application code and configuration
COPY --chown=aiboa:aiboa . .

# Copy Streamlit configuration if it exists
COPY --chown=aiboa:aiboa .streamlit/ .streamlit/

# Switch to non-root user
USER aiboa

# Ensure Python packages are in PATH
ENV PATH=/home/aiboa/.local/bin:$PATH

# Set Streamlit configuration
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Create health check script
RUN echo '#!/bin/bash\ncurl -f http://localhost:8501/health || curl -f http://localhost:8501/_stcore/health || exit 1' > /app/healthcheck.sh && chmod +x /app/healthcheck.sh

# Expose port (Streamlit default port)
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD /app/healthcheck.sh

# Run the Streamlit application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true", "--browser.gatherUsageStats=false"]