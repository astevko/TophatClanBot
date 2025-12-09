# TophatC Clan Discord Bot

A Discord bot for managing the TophatC Clan, tracking member ranks and activity points, with full Roblox group integration.

## Quick Start

```bash
# Install uv (fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone <your-repo-url>
cd TophatClanBot

# Configure
cp setup_example.env .env
nano .env  # Add your Discord token, Guild ID, and Roblox credentials

# Run
./run.sh   # Linux/macOS
run.bat    # Windows
```

## Features

- 🎯 **Raid Submission System**: Members submit raid events with proof images for admin approval
- 📊 **Rank & XP Tracking**: Track member progress through military hierarchy ranks
- 🏆 **Leaderboard**: View top members by activity points
- 🔗 **Roblox Integration**: Automatically sync ranks between Discord and Roblox group
- ⚡ **Admin Tools**: Promote members, manage points, and approve events
- 🎨 **Beautiful Embeds**: Rich Discord embeds for all interactions

## Commands

### Quick Reference

**User Commands:**
- `/xp` - Check your rank and points progress
- `/leaderboard` - View top 10 members by points
- `/link-roblox <username>` - Link Discord to Roblox account
- `/submit-raid <proof_image>` - Submit raid for approval

**Admin Commands:**
- `/promote @user` - Promote member to next rank
- `/add-points @user <amount>` - Adjust member points
- `/set-admin-channel <channel>` - Set submission channel
- `/view-pending` - View pending submissions
- `/check-member @user` - Check member stats
- `/list-ranks` - View all ranks

📖 **For detailed command usage, examples, and troubleshooting, see [COMMANDS_GUIDE.md](COMMANDS_GUIDE.md)**

## Rank System

Default military hierarchy with point requirements:

1. **Private** - 0 points
2. **Corporal** - 30 points
3. **Sergeant** - 60 points
4. **Staff Sergeant** - 100 points
5. **Lieutenant** - 150 points
6. **Captain** - 210 points
7. **Major** - 280 points
8. **Colonel** - 360 points
9. **General** - 450 points

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer (recommended)
- A Discord account with permission to create bots
- A Roblox group with appropriate permissions
- Roblox Open Cloud API key or group owner/admin credentials

### 1. Discord Bot Setup

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" section and click "Add Bot"
4. Enable the following **Privileged Gateway Intents**:
   - Server Members Intent
   - Message Content Intent
5. Copy the bot token (you'll need this later)
6. Go to "OAuth2" → "URL Generator"
7. Select scopes: `bot` and `applications.commands`
8. Select bot permissions:
   - Manage Roles
   - Send Messages
   - Embed Links
   - Attach Files
   - Read Message History
   - Use Slash Commands
9. Copy the generated URL and open it in your browser to invite the bot to your server

### 2. Get Your Discord Server (Guild) ID

1. Enable Developer Mode in Discord (Settings → Advanced → Developer Mode)
2. Right-click your server icon and select "Copy ID"

### 3. Roblox API Setup

#### Option A: Open Cloud API (Recommended)

1. Go to [Roblox Creator Hub](https://create.roblox.com/dashboard/credentials)
2. Click "Create API Key"
3. Give it a name (e.g., "TophatC Clan Bot")
4. Add the following permissions:
   - `group.membership:write` - To update member ranks
   - `group.membership:read` - To read member information
5. Select your group
6. Copy the API key (you'll only see it once!)

#### Option B: Cookie Authentication (Legacy)

⚠️ **Warning**: This method is less secure and not recommended.

1. Log into Roblox in your browser
2. Open browser developer tools (F12)
3. Go to Application/Storage → Cookies → roblox.com
4. Find the `.ROBLOSECURITY` cookie and copy its value

### 4. Configure the Bot

1. Clone this repository:
```bash
git clone https://github.com/yourusername/TophatClanBot.git
cd TophatClanBot
```

2. Install `uv` (if you haven't already):
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv
```

3. Create a `.env` file in the project root:
```bash
# Discord Bot Configuration
DISCORD_BOT_TOKEN=your_discord_bot_token_here
GUILD_ID=your_discord_server_id_here

# Admin Channel Configuration (optional - can set via /set-admin-channel)
ADMIN_CHANNEL_ID=your_admin_channel_id_here

# Roblox Configuration
ROBLOX_GROUP_ID=your_roblox_group_id_here
ROBLOX_API_KEY=your_roblox_api_key_here

# Admin Role Configuration (optional)
ADMIN_ROLE_NAME=Admin
```

4. Install dependencies:
```bash
# Using uv (recommended - much faster!)
uv pip install -e .

# Or using traditional pip
pip install -r requirements.txt
```

### 5. Run the Bot Locally

```bash
# Quick start with provided script (recommended)
./run.sh           # Linux/macOS
run.bat            # Windows

# Or manually with uv
uv run bot.py

# Or with standard Python
python bot.py
```

The bot will:
- Initialize the database with default ranks
- Connect to Discord
- Sync slash commands
- Be ready to use!

## Deployment Options

### 🐳 Docker Deployment (Recommended)

The easiest way to deploy is using Docker and Docker Compose with PostgreSQL:

```bash
# Quick start
cp setup_example.env .env
# Edit .env with your credentials + POSTGRES_PASSWORD

# Start services (bot + database)
make docker-up

# View logs
make docker-logs

# Stop services
make docker-down
```

**Features:**
- ✅ Production-ready PostgreSQL database
- ✅ Automatic restarts
- ✅ Resource isolation
- ✅ Easy backup/restore
- ✅ Development mode with hot-reload

📖 **See [README_DOCKER.md](README_DOCKER.md) and [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) for complete Docker setup guide**

### ☁️ Cloud Deployment

#### Option 1: Deploy to Oracle Cloud (OCI) Free Tier (Recommended) ⭐

Oracle Cloud's Always Free tier provides generous resources perfect for Discord bots:
- ✅ **4 ARM CPUs + 24 GB RAM** (always free!)
- ✅ **PostgreSQL Database** (20 GB, always free!)
- ✅ **200 GB Storage** (always free!)
- ✅ **No credit card charges** after trial

**Quick Start:**
```bash
# 30-minute setup - see detailed guide
# 1. Create OCI account
# 2. Launch VM (4 ARM CPUs, 24 GB RAM)
# 3. Install Docker & PostgreSQL
# 4. Deploy bot with Docker Compose
```

📖 **See [OCI_DEPLOYMENT_GUIDE.md](OCI_DEPLOYMENT_GUIDE.md) for complete step-by-step instructions**  
📖 **See [QUICK_START_OCI.md](QUICK_START_OCI.md) for fast-track deployment (30 min)**  
📖 **See [BACKUP_RESTORE_GUIDE.md](BACKUP_RESTORE_GUIDE.md) for database migration**

#### Option 2: Deploy to Railway.app (Free Tier)

1. Create account at [Railway.app](https://railway.app/)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select this repository
4. Configure build settings:
   - **Build Command**: `pip install uv && uv pip install --system -e .`
   - **Start Command**: `python bot.py`
5. Add environment variables:
   - Go to your project → Variables
   - Add all variables from your `.env` file
6. Railway will automatically deploy your bot
7. Your bot will run 24/7 with $5 free credit per month

#### Option 3: Deploy to Render.com (Free Tier)

1. Create account at [Render.com](https://render.com/)
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: tophatc-clan-bot
   - **Environment**: Python
   - **Build Command**: `pip install uv && uv pip install --system -e .`
   - **Start Command**: `python bot.py`
5. Add environment variables (same as `.env` file)
6. Click "Create Web Service"
7. Your bot will run on the free tier (750 hours/month)

#### Option 4: Deploy with Docker to Any VPS

1. Setup VPS with Docker and Docker Compose installed
2. Clone repository and configure `.env`
3. Run `docker-compose up -d`
4. Bot runs 24/7 with PostgreSQL database

See [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) for detailed instructions.

#### Option 5: GitHub Container Registry + Cloud Run

The project includes GitHub Actions that automatically build and push Docker images:

1. Push to main branch → Image builds automatically
2. Pull from `ghcr.io/your-username/tophatclanbot:latest`
3. Deploy to Google Cloud Run, AWS ECS, Azure Container Instances, etc.

See `.github/workflows/docker-build.yml` for CI/CD configuration.

## Usage Workflow

### For Members

1. **Join & Link Account**
   - Use `/link-roblox <username>` to register
   - Receive "Private" rank automatically

2. **Participate in Raids**
   - Take group selfie as proof
   - Use `/submit-raid` with the image
   - Fill in participant details, start/end time

3. **Track Progress**
   - Use `/xp` to check rank progress
   - Use `/leaderboard` to see rankings

### For Admins

1. **Review Submissions**
   - Check admin channel for raid submissions
   - Click "Approve" or "Decline"
   - If approving, enter points (1-30)

2. **Manage Members**
   - Use `/check-member @user` to see stats
   - Use `/promote @user` when eligible
   - Use `/add-points @user <amount>` for manual adjustments

3. **Configuration**
   - Use `/set-admin-channel #channel` to set review channel
   - Use `/list-ranks` to see all rank requirements

## Database

The bot supports three database backends for different deployment scenarios:

### SQLite (Local Development)
- **Database file**: `tophat_clan.db`
- **Used when**: Neither `DATABASE_URL` nor Oracle credentials are set
- **Best for**: Local development and testing

### PostgreSQL (Production)
- **Used when**: `DATABASE_URL` environment variable is set
- **Best for**: Production deployments (Railway, Render, Docker)
- **Connection format**: `postgresql://user:password@host:port/database`

### Oracle Autonomous Database (Cloud Production) ⭐ NEW
- **Used when**: `ORACLE_USER`, `ORACLE_PASSWORD`, and `ORACLE_DSN` are set
- **Best for**: Enterprise deployments on Oracle Cloud Infrastructure
- **Features**:
  - Fully managed cloud database
  - Automatic backups and scaling
  - Always-free tier available (20 GB storage)
  - High availability and security

📖 **See [ORACLE_DEPLOYMENT_GUIDE.md](ORACLE_DEPLOYMENT_GUIDE.md) for complete Oracle setup instructions**

### Database Priority

The bot selects the database in this priority order:
1. **Oracle** (if Oracle credentials are configured)
2. **PostgreSQL** (if `DATABASE_URL` is configured)
3. **SQLite** (default fallback for local development)

### Database Schema
All databases use the same schema with four main tables:
- **members**: Discord ID, Roblox username, rank, points
- **raid_submissions**: Submitted events with approval status
- **rank_requirements**: Rank hierarchy and point thresholds
- **config**: Bot configuration settings

The database is created automatically on first run.

### Backup & Migration
The project includes automated backup and migration tools:

```bash
# Backup SQLite (local)
./backup_sqlite.sh

# Backup PostgreSQL (production)
./backup_postgres.sh

# Migrate SQLite to PostgreSQL
python migrate_to_postgres.py postgresql://user:pass@host:5432/db

# Migrate PostgreSQL to Oracle
python migrate_postgres_to_oracle.py

# Test Oracle connection
python test_oracle_connection.py
```

📖 **See [BACKUP_RESTORE_GUIDE.md](BACKUP_RESTORE_GUIDE.md) for complete backup/restore instructions**

## Troubleshooting

### Bot doesn't respond to commands

- Make sure bot has "Use Application Commands" permission
- Verify bot is online (check for green status)
- Try kicking and re-inviting the bot with the OAuth2 URL

### Roblox rank updates fail

- Verify your API key has correct permissions
- Check that the bot account has group admin permissions
- Ensure `ROBLOX_GROUP_ID` is correct
- Check logs for specific error messages

### Commands not showing up

- Wait a few minutes after bot starts (Discord needs to sync)
- Try typing `/` to see if commands appear
- Verify `GUILD_ID` is correct in `.env`

### Permission errors

- Ensure bot role is above the rank roles in server settings
- Give bot "Manage Roles" permission
- Check that bot can access admin channel

## CI/CD Pipeline

The project includes GitHub Actions workflows for automated testing and deployment:

### Continuous Integration (`.github/workflows/ci.yml`)
- Runs on every push and PR
- Tests across Python 3.9, 3.10, 3.11, 3.12
- Linting with ruff
- Security scanning with Bandit and Safety

### Docker Build (`.github/workflows/docker-build.yml`)
- Builds multi-architecture Docker images (amd64, arm64)
- Pushes to GitHub Container Registry
- Security scanning with Docker Scout
- Automatic on push to main or version tags

### Deployment (`.github/workflows/deploy.yml`)
- Template for automated deployment
- Supports Railway, VPS, AWS ECS, and more
- Manual trigger or automatic on version tags

## Development

### Project Structure

```
TophatClanBot/
├── bot.py                      # Main bot entry point
├── database.py                 # SQLite database operations
├── database_postgres.py        # PostgreSQL database operations
├── database_oracle.py          # Oracle database operations
├── roblox_api.py               # Roblox API integration
├── config.py                   # Configuration management
├── security_utils.py           # Security utilities and logging
├── commands/
│   ├── user_commands.py        # User-facing commands
│   └── admin_commands.py       # Admin-only commands
├── pyproject.toml              # Project metadata and dependencies
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Production Docker image
├── docker-compose.yml          # Production orchestration
├── docker-compose.dev.yml      # Development orchestration
├── .dockerignore               # Docker build optimization
├── Makefile                    # Build automation
├── run.sh / run.bat            # Quick start scripts
├── setup_example.env           # Environment template
├── .env                        # Environment variables (not in git)
├── .gitignore                  # Git ignore rules
├── .github/
│   ├── workflows/
│   │   ├── ci.yml              # Continuous Integration
│   │   ├── docker-build.yml    # Docker image builds
│   │   └── deploy.yml          # Deployment automation
│   └── PULL_REQUEST_TEMPLATE.md
├── README.md                   # This file
├── README_DOCKER.md            # Docker quick reference
├── DOCKER_DEPLOYMENT.md        # Comprehensive Docker guide
├── ORACLE_DEPLOYMENT_GUIDE.md  # Oracle database setup guide
├── OCI_DEPLOYMENT_GUIDE.md     # Oracle Cloud deployment
├── migrate_postgres_to_oracle.py  # PostgreSQL to Oracle migration
├── test_oracle_connection.py   # Test Oracle connectivity
└── [Other documentation files]
```

### Using uv for Development

```bash
# Install dependencies
uv pip install -e .

# Install with dev dependencies
uv pip install -e ".[dev]"

# Run the bot
uv run bot.py

# Update dependencies
uv pip install --upgrade discord.py

# Create virtual environment with uv
uv venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

### Using Makefile (Linux/macOS)

```bash
# See all available commands
make help

# First-time setup
make setup

# Local development
make install           # Install dependencies
make run               # Run the bot

# Docker development
make docker-dev        # Start with hot-reload + pgAdmin
make docker-up         # Start production stack
make docker-down       # Stop all services
make docker-logs       # View logs

# Database management
make db-backup         # Backup PostgreSQL database
make db-restore        # Restore from backup
make db-shell          # Open database shell

# Cleanup
make clean             # Clean local files
make docker-clean      # Clean Docker resources
```

### Adding New Ranks

Edit the `default_ranks` list in `database.py` (line ~61) before first run:

```python
default_ranks = [
    (1, "Private", 0, 1),
    (2, "Corporal", 30, 2),
    # Add more ranks here...
]
```

Each tuple is: `(rank_order, rank_name, points_required, roblox_group_rank_id)`

### Customization

- **Point Range**: Change validation in `PointsInputModal` (user_commands.py)
- **Rank Colors**: Modify role creation in command files
- **Announcement Channel**: Uncomment lines in `promote` command (admin_commands.py)

## Security Notes

- **Never commit `.env` file** - Contains sensitive tokens
- **Use API key over cookie** - More secure and granular permissions
- **Restrict admin commands** - Only trusted members should have Admin role
- **Regular backups** - Backup `tophat_clan.db` regularly

## Support

For issues or questions:
1. Check the logs (`bot.log` file)
2. Review Discord and Roblox API status pages
3. Open an issue on GitHub

## License

See LICENSE file for details.

## Credits

Built for the TophatC Clan community.

