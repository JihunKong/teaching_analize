FROM python:3.11-slim

WORKDIR /app

# Copy minimal requirements
COPY requirements.minimal.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy minimal app
COPY main_minimal.py main.py

# Use PORT from Railway
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}