# Use the official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8080

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# 静的ファイルの存在確認
RUN echo "=== 静的ファイル確認 ===" && \
    ls -la /app/src/ && \
    echo "=== imgディレクトリ確認 ===" && \
    ls -la /app/src/img/ && \
    echo "=== PNGファイル確認 ===" && \
    find /app/src/img -name "*.png" -type f

# Ensure service account key is properly placed
RUN if [ -f "service-account-key.json" ]; then \
        echo "Service account key found and placed correctly"; \
    else \
        echo "Warning: service-account-key.json not found"; \
    fi

# Expose the port
EXPOSE 8080

# Start the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]