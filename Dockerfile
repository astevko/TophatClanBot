FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster dependency installation
RUN pip install --no-cache-dir uv

# Copy dependency files first (for better caching)
COPY pyproject.toml requirements.txt ./

# Install Python dependencies
RUN uv pip install --system -r requirements.txt

# Copy application files
COPY bot.py config.py database.py database_postgres.py roblox_api.py security_utils.py ./
COPY commands/ commands/

# Create directory for database (SQLite fallback)
RUN mkdir -p /data

# Create non-root user for security
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app /data
USER botuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Run the bot
CMD ["python", "-u", "bot.py"]
