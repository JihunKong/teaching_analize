FROM python:3.11-slim

WORKDIR /app

# Install minimal dependencies
RUN pip install --no-cache-dir fastapi==0.104.1 uvicorn[standard]==0.24.0

# Copy simple test app
COPY simple_main.py main.py

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Create a start script that ignores PORT if it's 5432 (PostgreSQL port)
RUN echo '#!/bin/sh\n\
if [ "$PORT" = "5432" ]; then\n\
  echo "PORT is 5432 (PostgreSQL), using Railway default HTTP port"\n\
  exec uvicorn main:app --host 0.0.0.0 --port 8080\n\
else\n\
  echo "Starting on PORT: $PORT"\n\
  exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}\n\
fi' > start.sh && chmod +x start.sh

# Run using shell to properly expand PORT variable
CMD ["sh", "start.sh"]