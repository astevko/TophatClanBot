# Docker & CI/CD Setup Guide

This document provides a quick reference for the Docker and CI/CD features of the TophatC Clan Bot.

## 📦 What's Included

### Docker Files
- **`Dockerfile`** - Production-ready container image with security best practices
- **`docker-compose.yml`** - Production deployment with PostgreSQL database
- **`docker-compose.dev.yml`** - Development override with hot-reload and pgAdmin
- **`.dockerignore`** - Optimizes build by excluding unnecessary files

### GitHub Actions Workflows
- **`.github/workflows/ci.yml`** - Continuous Integration (testing, linting, security scans)
- **`.github/workflows/docker-build.yml`** - Builds and pushes Docker images to GHCR
- **`.github/workflows/deploy.yml`** - Deployment workflow template

### Documentation
- **`DOCKER_DEPLOYMENT.md`** - Comprehensive deployment guide
- **`.github/PULL_REQUEST_TEMPLATE.md`** - PR template for contributions

## 🚀 Quick Start

### Local Development (No Docker)

```bash
# Setup
make setup
# Edit .env file with your credentials

# Run
make run
```

### Docker Compose (Recommended)

```bash
# Setup environment
cp setup_example.env .env
# Edit .env and add POSTGRES_PASSWORD

# Start services (production mode)
make docker-up

# View logs
make docker-logs

# Stop services
make docker-down
```

### Docker Compose Development Mode

```bash
# Starts with hot-reload and pgAdmin
make docker-dev
```

Access pgAdmin at http://localhost:5050:
- Email: `admin@tophatclan.local`
- Password: `admin`

## 🐳 Docker Architecture

```
┌─────────────────────────────────────────┐
│        Docker Compose Stack             │
├─────────────────────────────────────────┤
│                                          │
│  ┌──────────────┐    ┌──────────────┐   │
│  │              │    │              │   │
│  │  Discord Bot │◄───┤  PostgreSQL  │   │
│  │              │    │   Database   │   │
│  └──────────────┘    └──────────────┘   │
│         │                    │           │
│         │              ┌─────▼─────┐     │
│         │              │  Volume   │     │
│         │              │ postgres_ │     │
│         │              │   data    │     │
│         │              └───────────┘     │
│    ┌────▼─────┐                          │
│    │  Logs    │                          │
│    │  Volume  │                          │
│    └──────────┘                          │
│                                          │
└─────────────────────────────────────────┘
```

## 🎯 Make Commands Reference

### Development
```bash
make install        # Install dependencies using uv
make run            # Run the bot locally
make clean          # Clean up database and logs
make setup          # First-time setup helper
```

### Docker (Single Container)
```bash
make docker-build   # Build Docker image
make docker-run     # Run bot in Docker
```

### Docker Compose (Production)
```bash
make docker-up      # Start all services
make docker-dev     # Start in development mode
make docker-down    # Stop all services
make docker-logs    # View logs
make docker-restart # Restart all services
make docker-clean   # Clean up everything
```

### Database Management
```bash
make db-backup      # Backup database to backups/
make db-restore     # Restore from backup
make db-shell       # Open PostgreSQL shell
```

## 🔄 CI/CD Pipeline

### On Every Push/PR
1. **Lint** - Code quality checks with ruff
2. **Test** - Syntax validation across Python 3.9-3.12
3. **Security** - Bandit and safety scans

### On Push to Main
1. **Build** - Docker image built for multiple architectures
2. **Scan** - Docker Scout security scan
3. **Push** - Image pushed to GitHub Container Registry

### On Version Tags (v*)
1. All of the above
2. **Deploy** - Automatic deployment (configure in deploy.yml)

## 🏷️ Docker Images

Images are automatically built and published to GitHub Container Registry:

```bash
# Pull latest image
docker pull ghcr.io/YOUR_USERNAME/tophatclanbot:latest

# Pull specific version
docker pull ghcr.io/YOUR_USERNAME/tophatclanbot:v1.0.0

# Use in docker-compose.yml
services:
  bot:
    image: ghcr.io/YOUR_USERNAME/tophatclanbot:latest
```

## Oracle Container Registry (OCIR)

For private deployments to Oracle Cloud, images are also pushed to Oracle Container Registry.

### Required GitHub Secrets for OCIR

Add these secrets in your GitHub repository (Settings > Secrets and variables > Actions):

| Secret | Description | Example |
|--------|-------------|---------|
| `OCIR_REGION` | OCIR regional endpoint | `iad.ocir.io` (Ashburn), `phx.ocir.io` (Phoenix) |
| `OCIR_TENANCY` | Your OCI tenancy namespace | Found in OCI Console > Tenancy Details |
| `OCIR_USERNAME` | OCIR login username | `<tenancy>/<username>` or `<tenancy>/oracleidentitycloudservice/<email>` |
| `OCIR_TOKEN` | Auth token for OCIR | Generate in OCI Console > User Settings > Auth Tokens |

### Pull from OCIR on Oracle Instances

```bash
# Authenticate with OCIR (one-time setup)
docker login <region>.ocir.io -u '<tenancy>/<username>' -p '<auth-token>'

# Pull the image
docker pull <region>.ocir.io/<tenancy>/clanbot:latest
```

## 🔒 Security Features

### Dockerfile Security
- ✅ Non-root user (UID 1000)
- ✅ Minimal base image (python:3.11-slim)
- ✅ No cache for pip installations
- ✅ Multi-stage consideration
- ✅ Health checks

### Docker Compose Security
- ✅ Isolated network
- ✅ Environment variable secrets
- ✅ Volume isolation
- ✅ Log rotation

### CI/CD Security
- ✅ Dependency vulnerability scanning
- ✅ Static code analysis (Bandit)
- ✅ Container image scanning (Docker Scout)
- ✅ Only pushes on main branch

## 📊 Monitoring & Logs

### View Logs
```bash
# All services
docker-compose logs -f

# Just the bot
docker-compose logs -f bot

# Just the database
docker-compose logs -f postgres

# Last 100 lines
docker-compose logs --tail=100 bot
```

### Check Status
```bash
# Container status
docker-compose ps

# Resource usage
docker stats tophat-bot tophat-postgres
```

## 🐛 Troubleshooting

### Bot Won't Start
```bash
# Check configuration
docker-compose config

# Check logs
docker-compose logs bot

# Verify database
docker-compose exec postgres psql -U botuser -d tophatclan -c "SELECT 1;"
```

### Database Issues
```bash
# Check database health
docker-compose ps postgres

# View database logs
docker-compose logs postgres

# Connect to database
make db-shell
```

### Permission Errors
```bash
# Fix log directory ownership
sudo chown -R 1000:1000 ./logs
```

### Reset Everything
```bash
# Nuclear option - removes all data
make docker-clean
make docker-up
```

## 🌐 Deployment Options

### Option 1: Railway
1. Fork repository
2. Connect to Railway
3. Set environment variables
4. Deploy automatically

### Option 2: VPS with Docker
1. Install Docker and Docker Compose
2. Clone repository
3. Create `.env` file
4. Run `make docker-up`

### Option 3: GitHub Container Registry + Your Host
1. Images auto-build on push
2. Pull from GHCR
3. Run with your orchestration

### Option 4: Cloud Platforms
- AWS ECS
- Google Cloud Run
- Azure Container Instances
- DigitalOcean App Platform

## 📝 Environment Variables

See `setup_example.env` for all available variables.

**Required for Docker:**
- `POSTGRES_PASSWORD` - Database password
- `DISCORD_BOT_TOKEN` - Bot token
- `GUILD_ID` - Server ID
- `LOG_CHANNEL_ID` - Log channel ID
- `ROBLOX_GROUP_ID` - Roblox group ID
- `ROBLOX_API_KEY` or `ROBLOX_COOKIE` - Roblox auth

## 🔗 Useful Links

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Full Deployment Guide](DOCKER_DEPLOYMENT.md)

## 💡 Tips

1. **Use development mode** (`make docker-dev`) when coding
2. **Backup regularly** with `make db-backup`
3. **Monitor logs** for errors and rate limits
4. **Update images** regularly for security patches
5. **Use GitHub Actions** for automated testing

## 📚 Additional Documentation

- [`DOCKER_DEPLOYMENT.md`](DOCKER_DEPLOYMENT.md) - Full deployment guide
- [`SETUP_GUIDE.md`](SETUP_GUIDE.md) - General setup instructions
- [`COMMANDS_GUIDE.md`](COMMANDS_GUIDE.md) - Bot commands reference

---

**Need help?** Check the logs first with `make docker-logs` or review the full deployment guide in `DOCKER_DEPLOYMENT.md`.

