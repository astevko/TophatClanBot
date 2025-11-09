.PHONY: install run clean test docker-build docker-run help

help:
	@echo "TophatC Clan Bot - Available Commands:"
	@echo ""
	@echo "  make install      - Install dependencies using uv"
	@echo "  make run          - Run the bot"
	@echo "  make clean        - Clean up database and logs"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-run   - Run bot in Docker"
	@echo "  make setup        - First-time setup helper"
	@echo ""

install:
	@echo "📦 Installing dependencies with uv..."
	uv pip install -e .

run:
	@echo "🚀 Starting TophatC Clan Bot..."
	uv run bot.py

clean:
	@echo "🧹 Cleaning up..."
	rm -f *.db *.sqlite *.sqlite3 *.log
	rm -rf __pycache__ commands/__pycache__
	@echo "✅ Cleaned!"

docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t tophatc-clan-bot .

docker-run:
	@echo "🐳 Running bot in Docker..."
	docker run --env-file .env tophatc-clan-bot

setup:
	@echo "🔧 First-time setup..."
	@if [ ! -f .env ]; then \
		cp setup_example.env .env; \
		echo "✅ Created .env file from template"; \
		echo "⚠️  Please edit .env with your configuration:"; \
		echo "   - DISCORD_BOT_TOKEN"; \
		echo "   - GUILD_ID"; \
		echo "   - ROBLOX_GROUP_ID"; \
		echo "   - ROBLOX_API_KEY"; \
	else \
		echo "✅ .env already exists"; \
	fi
	@make install
	@echo ""
	@echo "🎉 Setup complete! Edit .env then run: make run"

