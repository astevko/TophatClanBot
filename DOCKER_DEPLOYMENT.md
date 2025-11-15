# Docker Deployment Guide

This guide explains how to deploy the TophatC Clan Discord Bot using Docker and Docker Compose.

## Prerequisites

- Docker Engine 20.10+ installed
- Docker Compose v2.0+ installed
- Basic understanding of Docker and environment variables

## Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd TophatClanBot
```

### 2. Create Environment File

Copy the example environment file and fill in your values:

```bash
cp .env.example .env
nano .env  # or use your preferred editor
```

**Required variables:**
- `POSTGRES_PASSWORD` - Secure password for PostgreSQL database
- `DISCORD_BOT_TOKEN` - Your Discord bot token
- `GUILD_ID` - Your Discord server ID
- `LOG_CHANNEL_ID` - Discord channel ID for bot logs
- `ROBLOX_GROUP_ID` - Your Roblox group ID
- `ROBLOX_API_KEY` or `ROBLOX_COOKIE` - Roblox API credentials

### 3. Start the Services

```bash
docker-compose up -d
```

This will:
- Pull the PostgreSQL image
- Build the bot Docker image
- Create a dedicated network for the services
- Start both the database and bot containers

### 4. View Logs

```bash
# View bot logs
docker-compose logs -f bot

# View database logs
docker-compose logs -f postgres

# View all logs
docker-compose logs -f
```

### 5. Stop the Services

```bash
docker-compose down
```

To also remove the database volume:

```bash
docker-compose down -v
```

## Architecture

The Docker Compose setup includes:

### Services

1. **PostgreSQL Database** (`postgres`)
   - Image: `postgres:16-alpine`
   - Port: `5432` (exposed for debugging)
   - Volume: `postgres_data` for persistent storage
   - Health check: Ensures database is ready before bot starts

2. **Discord Bot** (`bot`)
   - Built from local Dockerfile
   - Depends on PostgreSQL
   - Automatically restarts on failure
   - Runs as non-root user for security

### Networking

Both services communicate through a dedicated Docker network (`botnet`), isolating them from other containers.

### Volumes

- `postgres_data`: Persists database data across container restarts
- `./logs`: (Optional) Mounts local logs directory

## Configuration

### Environment Variables

All configuration is done through environment variables in the `.env` file:

#### Database Configuration
```env
POSTGRES_PASSWORD=your_secure_password
```

#### Discord Configuration
```env
DISCORD_BOT_TOKEN=your_token
GUILD_ID=123456789
LOG_CHANNEL_ID=123456789
ADMIN_CHANNEL_ID=123456789
```

#### Roblox Configuration
```env
ROBLOX_GROUP_ID=123456
ROBLOX_API_KEY=your_api_key
# OR use cookie authentication:
# ROBLOX_COOKIE=_|WARNING:-DO-NOT-SHARE...
```

#### Role Configuration
```env
# By Name (fallback)
ADMIN_ROLE_NAME=Admin
MODERATOR_ROLE_NAME=Moderator

# By ID (more reliable)
ADMIN_ROLE_ID=123456789
MODERATOR_ROLE_ID=987654321
```

#### Admin Whitelist
```env
ADMIN_USER_IDS=123456789012345678,987654321098765432
```

#### Rate Limiting
```env
MAX_RATE_LIMIT_RETRIES=3
RATE_LIMIT_RETRY_DELAY=1.0
```

## Management Commands

### Rebuild and Restart

After code changes:

```bash
docker-compose up -d --build
```

### View Container Status

```bash
docker-compose ps
```

### Execute Commands in Container

```bash
# Open shell in bot container
docker-compose exec bot /bin/bash

# Run Python command
docker-compose exec bot python -c "print('Hello')"
```

### Database Access

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U botuser -d tophatclan

# Backup database
docker-compose exec postgres pg_dump -U botuser tophatclan > backup.sql

# Restore database
cat backup.sql | docker-compose exec -T postgres psql -U botuser tophatclan
```

### View Resource Usage

```bash
docker stats tophat-bot tophat-postgres
```

## Production Deployment

### 1. Security Considerations

- **Never commit `.env` file** to version control
- Use strong passwords for `POSTGRES_PASSWORD`
- Rotate credentials regularly
- Consider using Docker secrets for sensitive data
- Run containers as non-root (already configured)

### 2. Resource Limits

Add resource limits to `docker-compose.yml`:

```yaml
services:
  bot:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

### 3. Monitoring

Consider adding monitoring services:

```yaml
services:
  # Add Prometheus, Grafana, or other monitoring tools
```

### 4. Backup Strategy

Set up automated backups:

```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="./backups"
mkdir -p $BACKUP_DIR
docker-compose exec -T postgres pg_dump -U botuser tophatclan | gzip > "$BACKUP_DIR/backup-$(date +%Y%m%d-%H%M%S).sql.gz"
# Keep only last 7 days
find $BACKUP_DIR -name "backup-*.sql.gz" -mtime +7 -delete
EOF

chmod +x backup.sh

# Add to crontab for daily backups
# 0 2 * * * /path/to/backup.sh
```

### 5. SSL/TLS

If exposing database externally, configure SSL:

```yaml
postgres:
  command: >
    postgres
    -c ssl=on
    -c ssl_cert_file=/etc/ssl/certs/server.crt
    -c ssl_key_file=/etc/ssl/private/server.key
```

## Troubleshooting

### Bot Won't Start

1. Check logs:
   ```bash
   docker-compose logs bot
   ```

2. Verify environment variables:
   ```bash
   docker-compose config
   ```

3. Check database connectivity:
   ```bash
   docker-compose exec bot ping postgres
   ```

### Database Connection Issues

1. Verify database is healthy:
   ```bash
   docker-compose ps
   ```

2. Check database logs:
   ```bash
   docker-compose logs postgres
   ```

3. Test connection manually:
   ```bash
   docker-compose exec postgres psql -U botuser -d tophatclan -c "SELECT 1;"
   ```

### Permission Issues

If you see permission errors:

```bash
# Fix ownership
sudo chown -R 1000:1000 ./logs
```

### Out of Memory

If containers are killed due to OOM:

1. Check resource usage:
   ```bash
   docker stats
   ```

2. Increase Docker memory limit in Docker Desktop settings
3. Add memory limits to `docker-compose.yml`

### Container Keeps Restarting

1. Check exit code and logs:
   ```bash
   docker-compose ps
   docker-compose logs bot --tail=100
   ```

2. Verify all required environment variables are set
3. Check database is accessible

## Updates and Maintenance

### Update Bot Code

```bash
git pull
docker-compose up -d --build
```

### Update Dependencies

```bash
# Update requirements.txt
docker-compose build --no-cache
docker-compose up -d
```

### Database Migrations

If schema changes are needed:

```bash
# Create migration script
docker-compose exec bot python migrate_script.py
```

## CI/CD Integration

The project includes GitHub Actions workflows for automated builds:

- **CI Workflow** (`.github/workflows/ci.yml`): Runs tests and linting
- **Docker Build** (`.github/workflows/docker-build.yml`): Builds and pushes images to GitHub Container Registry

### Using Pre-built Images

Instead of building locally, pull from registry:

```yaml
services:
  bot:
    image: ghcr.io/your-username/tophatclanbot:latest
    # Remove 'build:' section
```

## Support

For issues and questions:
- Check the logs first: `docker-compose logs`
- Review this guide and other documentation
- Check GitHub Issues
- Contact the development team

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)
- [Discord.py Documentation](https://discordpy.readthedocs.io/)

