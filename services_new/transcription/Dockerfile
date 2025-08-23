FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for browser automation and audio processing
# This matches the proven method from TRANSCRIPT_METHOD.md
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg \
    ca-certificates \
    xvfb \
    libasound2 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libxss1 \
    libnss3 \
    libnspr4 \
    libatspi2.0-0 \
    libgtk-3-0 \
    libgdk-pixbuf-xlib-2.0-0 \
    libxcomposite1 \
    libxcursor1 \
    libxi6 \
    libxtst6 \
    libasound2 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set display for headless browser (Xvfb)
ENV DISPLAY=:99

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (for browser automation fallback)
RUN playwright install chromium
# Skip playwright install-deps as it has compatibility issues with Debian Trixie
# We've already installed the essential system dependencies above

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/data

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Create startup script that includes Xvfb for headless browser automation
RUN echo '#!/bin/bash\n\
Xvfb :99 -screen 0 1920x1080x24 &\n\
export DISPLAY=:99\n\
sleep 2\n\
exec "$@"' > /app/start.sh && \
chmod +x /app/start.sh

# Start the application with Xvfb support
CMD ["/app/start.sh", "python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]