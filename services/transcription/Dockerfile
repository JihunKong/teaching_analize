FROM python:3.11-slim-bookworm

# Set working directory
WORKDIR /app

# Install system dependencies for Selenium browser automation only
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg \
    ca-certificates \
    git \
    build-essential \
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
    libxcursor1 \
    libxi6 \
    libxtst6 \
    unzip \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Set display for headless browser (Xvfb)
ENV DISPLAY=:99

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Chromium and ChromeDriver are already installed via apt (Selenium only)

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/data

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Copy and set up startup script for Xvfb
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Start the application with Xvfb support
CMD ["/app/start.sh", "python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]