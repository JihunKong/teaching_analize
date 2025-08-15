FROM python:3.11-slim

WORKDIR /app

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY main.py .

# Run the application
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}