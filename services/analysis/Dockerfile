FROM python:3.11-slim

WORKDIR /app

# Install minimal dependencies
RUN pip install --no-cache-dir fastapi==0.104.1 uvicorn[standard]==0.24.0

# Copy simple test app
COPY simple_main.py main.py

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Create a simple start script that uses PORT as-is
RUN echo '#!/bin/sh\n\
echo "Starting server on PORT: $PORT"\n\
exec uvicorn main:app --host 0.0.0.0 --port $PORT' > start.sh && chmod +x start.sh

# Run using shell to properly expand PORT variable
CMD ["sh", "start.sh"]