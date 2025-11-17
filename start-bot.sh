#!/bin/bash
# Wrapper script to start the bot with environment variables loaded
# This ensures the .env file is properly loaded by systemd

# Load environment variables from .env file
set -a
source /home/opc/TophatClanBot/.env
set +a

# Start the bot
exec /home/opc/.local/bin/uv run bot.py

