FROM python:3.11-slim

WORKDIR /app

# Install only essential system dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.minimal.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose port (Railway will override this)
EXPOSE 8001

# Start the application
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8001}