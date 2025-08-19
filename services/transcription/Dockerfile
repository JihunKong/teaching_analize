# Browser-enabled YouTube Transcript Service Dockerfile
FROM python:3.11-slim

# Install system dependencies for Chrome, Selenium and ffmpeg
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    ffmpeg \
    xvfb \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libxss1 \
    libxtst6 \
    && rm -rf /var/lib/apt/lists/*

# Install Chromium (ARM64 compatible)
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Set up Chromium environment
ENV CHROME_BIN=/usr/bin/chromium
ENV DISPLAY=:99

# Set working directory
WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user for security (after pip install to avoid permission issues)
RUN useradd --create-home --shell /bin/bash aiboa

# Copy application code
COPY . .

# Create data directory with proper permissions
RUN mkdir -p /app/data/uploads /app/data/transcripts /app/logs && chown -R aiboa:aiboa /app

# Switch to non-root user
USER aiboa

# Create health check script
RUN echo '#!/bin/bash\ncurl -f http://localhost:8000/health || exit 1' > /app/healthcheck.sh && chmod +x /app/healthcheck.sh

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD /app/healthcheck.sh

# Environment variables for browser scraping
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production

# Run the application with virtual display for headless Chrome
CMD ["sh", "-c", "Xvfb :99 -screen 0 1920x1080x24 & uvicorn main_working:app --host 0.0.0.0 --port 8000 --workers 1"]