FROM python:3.9-slim

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Create non-root user with specific UID/GID for volume permissions
RUN groupadd -r appuser --gid=1000 && useradd -r -g appuser --uid=1000 appuser

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for mounted volumes with proper permissions
RUN mkdir -p /app/config /app/logs && \
    chown -R appuser:appuser /app

# Ensure configuration directory has proper permissions for mounting
RUN chmod 755 /app/config && \
    chmod 755 /app/logs

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run Streamlit with configuration path validation
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true", "--server.fileWatcherType=none"]
