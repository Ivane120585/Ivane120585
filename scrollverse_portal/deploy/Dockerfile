FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY scrollverse_portal/ ./scrollverse_portal/
COPY scrollcensus/ ./scrollcensus/
COPY scroll_phase_11/ ./scroll_phase_11/

# Create necessary directories
RUN mkdir -p /app/scrollverse_portal/db
RUN mkdir -p /app/logs

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "scrollverse_portal.backend.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 