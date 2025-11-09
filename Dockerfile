FROM python:3.11-slim

WORKDIR /app

# Install uv for faster dependency installation
RUN pip install uv

# Copy project files
COPY pyproject.toml .
COPY requirements.txt .
COPY bot.py .
COPY config.py .
COPY database.py .
COPY roblox_api.py .
COPY commands/ commands/

# Install dependencies using uv
RUN uv pip install --system -e .

# Create directory for database
RUN mkdir -p /data

# Run the bot
CMD ["python", "bot.py"]

