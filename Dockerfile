FROM python:3.11-slim

WORKDIR /app

# Copy requirements first
COPY requirements.txt .

# Install only essential dependencies
RUN pip install --no-cache-dir fastapi==0.104.1 uvicorn[standard]==0.24.0

# Copy application
COPY main.py .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose port (Railway will override)
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]