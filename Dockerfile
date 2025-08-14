FROM python:3.11-slim

WORKDIR /app

# Install dependencies based on SERVICE environment variable
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy everything
COPY . .

# Install Python dependencies for transcription service (default)
RUN pip install fastapi==0.104.1 uvicorn[standard]==0.24.0 python-dotenv==1.0.0 \
    openai==1.3.5 httpx==0.25.1 aiofiles==23.2.1 pydantic==2.5.0 \
    pydantic-settings==2.1.0 sqlalchemy==2.0.23 psycopg2-binary==2.9.9

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Default to transcription service
CMD uvicorn services.transcription.app.main:app --host 0.0.0.0 --port ${PORT:-8000}