FROM python:3.11-slim

WORKDIR /app

# Install complete system dependencies for production
RUN apt-get update && apt-get install -y \
    ffmpeg \
    gcc \
    g++ \
    python3-dev \
    libpq-dev \
    build-essential \
    libmagic1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install build tools
RUN pip install --upgrade pip wheel setuptools

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Create storage directories
RUN mkdir -p /data/uploads /data/transcripts /data/youtube

# Create start script that uses PORT as-is
RUN echo '#!/bin/sh\n\
echo "Starting Transcription Service on PORT: $PORT"\n\
exec uvicorn main:app --host 0.0.0.0 --port $PORT' > start.sh && chmod +x start.sh

# Run using shell to properly expand PORT variable
CMD ["sh", "start.sh"]