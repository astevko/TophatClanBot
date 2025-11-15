.PHONY: install run clean test docker-build docker-run docker-up docker-down docker-logs docker-dev db-backup db-restore db-shell help

help:
	@echo "TophatC Clan Bot - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  make install        - Install dependencies using uv"
	@echo "  make run            - Run the bot locally"
	@echo "  make clean          - Clean up database and logs"
	@echo "  make setup          - First-time setup helper"
	@echo ""
	@echo "Docker (single container):"
	@echo "  make docker-build   - Build Docker image"
	@echo "  make docker-run     - Run bot in Docker"
	@echo ""
	@echo "Docker Compose (with PostgreSQL):"
	@echo "  make docker-up      - Start all services (production)"
	@echo "  make docker-dev     - Start all services (development mode)"
	@echo "  make docker-down    - Stop all services"
	@echo "  make docker-logs    - View logs from all services"
	@echo "  make docker-restart - Restart all services"
	@echo "  make docker-clean   - Stop and remove all containers and volumes"
	@echo ""
	@echo "Database:"
	@echo "  make db-backup      - Backup PostgreSQL database"
	@echo "  make db-restore     - Restore PostgreSQL database"
	@echo "  make db-shell       - Open PostgreSQL shell"
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

# Docker Compose commands
docker-up:
	@echo "🐳 Starting services with Docker Compose (production)..."
	docker-compose up -d
	@echo "✅ Services started! View logs with: make docker-logs"

docker-dev:
	@echo "🐳 Starting services with Docker Compose (development)..."
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

docker-down:
	@echo "🛑 Stopping Docker Compose services..."
	docker-compose down

docker-logs:
	@echo "📋 Viewing Docker Compose logs..."
	docker-compose logs -f

docker-restart:
	@echo "🔄 Restarting Docker Compose services..."
	docker-compose restart

docker-clean:
	@echo "🧹 Cleaning Docker resources..."
	docker-compose down -v
	docker system prune -f
	@echo "✅ Docker resources cleaned!"

# Database commands
db-backup:
	@echo "💾 Backing up database..."
	@mkdir -p backups
	@docker-compose exec -T postgres pg_dump -U botuser tophatclan > backups/backup-$$(date +%Y%m%d-%H%M%S).sql
	@echo "✅ Backup created in backups/"

db-restore:
	@echo "⚠️  This will restore the database from a backup file"
	@read -p "Enter backup file path: " backup_file; \
	cat $$backup_file | docker-compose exec -T postgres psql -U botuser tophatclan
	@echo "✅ Database restored!"

db-shell:
	@echo "🐘 Opening PostgreSQL shell..."
	docker-compose exec postgres psql -U botuser tophatclan

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
		echo "   - POSTGRES_PASSWORD (for Docker)"; \
	else \
		echo "✅ .env already exists"; \
	fi
	@make install
	@echo ""
	@echo "🎉 Setup complete! Edit .env then run:"
	@echo "   - Local: make run"
	@echo "   - Docker: make docker-up"

