#!/bin/bash
# Quick start script for TophatC Clan Bot

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Please copy setup_example.env to .env and configure it:"
    echo "  cp setup_example.env .env"
    echo "  nano .env"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
uv pip install -e .

# Run the bot
echo "🚀 Starting TophatC Clan Bot..."
uv run bot.py

