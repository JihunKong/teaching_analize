FROM python:3.11-slim

WORKDIR /app

# Install only essential dependencies
RUN pip install --no-cache-dir fastapi==0.104.1 uvicorn[standard]==0.24.0

# Copy application files
COPY main.py start.sh ./

# Make start script executable
RUN chmod +x start.sh

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application using start script
CMD ["./start.sh"]