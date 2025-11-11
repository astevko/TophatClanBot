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

## Deployment to Cloud

### Option 1: Deploy to Railway.app (Free Tier)

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

### Option 2: Deploy to Render.com (Free Tier)

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

### Option 3: Deploy to fly.io (Free Tier)

1. Install flyctl: https://fly.io/docs/hands-on/install-flyctl/
2. Create account: `flyctl auth signup`
3. Create `Dockerfile` in project root:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy project files
COPY . .

# Install dependencies using uv
RUN uv pip install --system -e .

# Run the bot
CMD ["python", "bot.py"]
```

4. Create `fly.toml` in project root:

```toml
app = "tophatc-clan-bot"

[build]
  dockerfile = "Dockerfile"
```

5. Deploy:
```bash
flyctl launch
flyctl secrets set DISCORD_BOT_TOKEN=your_token
flyctl secrets set GUILD_ID=your_guild_id
flyctl secrets set ROBLOX_GROUP_ID=your_group_id
flyctl secrets set ROBLOX_API_KEY=your_api_key
flyctl deploy
```

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
   - If approving, enter points (1-8)

2. **Manage Members**
   - Use `/check-member @user` to see stats
   - Use `/promote @user` when eligible
   - Use `/add-points @user <amount>` for manual adjustments

3. **Configuration**
   - Use `/set-admin-channel #channel` to set review channel
   - Use `/list-ranks` to see all rank requirements

## Database

The bot uses SQLite (`tophat_clan.db`) with three main tables:

- **members**: Discord ID, Roblox username, rank, points
- **raid_submissions**: Submitted events with approval status
- **rank_requirements**: Rank hierarchy and point thresholds

The database file is created automatically on first run.

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

## Development

### Project Structure

```
TophatClanBot/
├── bot.py                 # Main bot entry point
├── database.py            # SQLite database operations
├── roblox_api.py          # Roblox API integration
├── config.py              # Configuration management
├── commands/
│   ├── user_commands.py   # User-facing commands
│   └── admin_commands.py  # Admin-only commands
├── pyproject.toml         # Project metadata and dependencies (uv)
├── requirements.txt       # Python dependencies (fallback)
├── Dockerfile             # Docker container configuration
├── Makefile               # Build automation (Linux/macOS)
├── run.sh / run.bat       # Quick start scripts
├── setup_example.env      # Environment template
├── .env                   # Environment variables (not in git)
├── .gitignore            # Git ignore rules
└── README.md             # This file
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

# Install dependencies
make install

# Run the bot
make run

# Build Docker image
make docker-build

# Clean up database and logs
make clean
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

