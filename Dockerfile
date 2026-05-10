FROM debian:trixie-slim

# Install Python 3.11
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .
RUN python3 -m pip install --break-system-packages -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Start server
CMD ["python3", "-m", "uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
