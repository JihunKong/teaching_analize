FROM python:3.11-slim

WORKDIR /app

# Install only essential dependencies
RUN pip install --no-cache-dir fastapi==0.104.1 uvicorn[standard]==0.24.0

# Copy only the main.py file
COPY main.py .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose port (Railway will override)
EXPOSE 8000

# Run the application directly with uvicorn
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}