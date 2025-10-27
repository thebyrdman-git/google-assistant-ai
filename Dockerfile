FROM python:3.11-slim

LABEL maintainer="Jimmy Byrd <jbyrd@example.com>"
LABEL description="Google Assistant AI Integration - Voice assistant powered by LiteLLM"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first (for Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn==21.2.0

# Copy application code
COPY app/ ./app/

# Create non-root user for security
RUN useradd -m -u 1000 assistant && \
    chown -R assistant:assistant /app

# Switch to non-root user
USER assistant

# Expose port
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5001/health || exit 1

# Run with Gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "2", "--timeout", "120", "app.main:app"]

