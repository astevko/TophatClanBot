# Onboarding Guide: Adding a New Clan Bot Instance

This guide walks you through setting up a new clan bot instance alongside existing ones. Each clan runs as an independent bot instance with its own database schema and configuration.

## Prerequisites

- Access to the Oracle database server (for creating new schemas)
- Docker installed on the deployment server
- Discord bot application created
- Roblox group access for the new clan

---

## Step 1: Clone/Prepare Repository

If deploying on a new server, clone the repository:

```bash
git clone <repository-url>
cd TophatClanBot
```

If adding to an existing deployment server, the repository should already be available.

---

## Step 2: Create Oracle Schema

Each clan needs its own Oracle schema (user) to keep data isolated.

### 2.1 Connect to Oracle Database

Connect as a DBA or admin user:

```bash
sqlplus sys@your_database as sysdba
# or
sqlplus admin_user@your_database
```

### 2.2 Create New User/Schema

Replace `newclan_bot` and `password` with your clan's values:

```sql
-- Create user (schema) for the new clan
CREATE USER newclan_bot IDENTIFIED BY "secure_password_here";

-- Grant necessary permissions
GRANT CREATE SESSION, CREATE TABLE, UNLIMITED TABLESPACE TO newclan_bot;
```

### 2.3 Initialize Schema Tables

Connect as the new user and run the schema setup script:

```bash
sqlplus newclan_bot@your_database
```

```sql
-- Run the schema setup script
@scripts/setup_oracle_schema.sql
```

Or copy the contents of `scripts/setup_oracle_schema.sql` and run it directly.

---

## Step 3: Create Clan Configuration Directory

Create a configuration directory for your clan's ranks:

```bash
mkdir -p configs/newclan
```

Create `configs/newclan/ranks.json` with your clan's rank structure. See `configs/tophat/ranks.json` or `configs/graves_family/ranks.json` for examples.

Example format:

```json
[
  {
    "rank_order": 1,
    "rank_name": "Private",
    "points_required": 0,
    "roblox_group_rank_id": 1,
    "admin_only": false
  },
  {
    "rank_order": 2,
    "rank_name": "Corporal",
    "points_required": 30,
    "roblox_group_rank_id": 2,
    "admin_only": false
  }
]
```

**Fields:**
- `rank_order`: Position in hierarchy (1, 2, 3, etc.)
- `rank_name`: Display name in Discord
- `points_required`: Minimum points needed (0 for admin-only ranks)
- `roblox_group_rank_id`: Corresponding Roblox group rank number
- `admin_only`: `true` for admin-granted ranks, `false` for point-based ranks

---

## Step 4: Create Deployment Directory

Create a deployment directory for your clan:

```bash
mkdir -p deployments/newclan
cd deployments/newclan
```

Copy the docker-compose template:

```bash
cp ../tophat/docker-compose.yml ./docker-compose.yml
```

Edit `docker-compose.yml` and update:
- `container_name`: e.g., `newclan-bot`
- `CLAN_NAME`: Your clan's display name
- `CLAN_CONFIG_DIR`: Directory name in `configs/` (e.g., `newclan`)
- `DATABASE_SCHEMA`: Oracle schema name (optional, defaults to ORACLE_USER)

---

## Step 5: Configure Environment Variables

Create a `.env` file in your deployment directory:

```bash
cd deployments/newclan
cp ../../setup_example.env .env
```

Edit `.env` and configure:

### Required Configuration

```bash
# Clan Identity (also set in docker-compose.yml)
CLAN_NAME=New Clan Name
CLAN_CONFIG_DIR=newclan

# Discord Configuration
DISCORD_BOT_TOKEN=your_discord_bot_token
GUILD_ID=your_discord_server_id
LOG_CHANNEL_ID=your_log_channel_id

# Roblox Configuration
ROBLOX_GROUP_ID=your_roblox_group_id
ROBLOX_API_KEY=your_roblox_api_key
# OR ROBLOX_COOKIE=your_roblox_cookie

# Oracle Database Configuration
ORACLE_USER=newclan_bot
ORACLE_PASSWORD=your_oracle_password
ORACLE_DSN=your_oracle_dsn
# DATABASE_SCHEMA=newclan_schema  # Optional, defaults to ORACLE_USER
```

### Optional Configuration

```bash
# Role Configuration
ADMIN_ROLE_NAME=Admin
MODERATOR_ROLE_NAME=Moderator
# ... etc

# Admin User IDs (comma-separated Discord user IDs)
ADMIN_USER_IDS=123456789012345678,987654321098765432

# Logging
LOG_LEVEL=INFO
```

---

## Step 6: Configure Discord Bot Application

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application or use an existing one
3. Go to "Bot" section and create a bot
4. Copy the bot token to your `.env` file
5. Enable required intents:
   - Message Content Intent
   - Server Members Intent
6. Go to "OAuth2" > "URL Generator"
   - Select scopes: `bot`, `applications.commands`
   - Select permissions: Administrator (or specific permissions)
7. Invite bot to your Discord server using the generated URL

---

## Step 7: Configure Roblox Group Integration

1. Go to your Roblox group's settings
2. Navigate to "Configure Group" > "Revenue"
3. Create an API key or use cookie authentication
4. Note your Roblox group ID
5. Add these to your `.env` file

---

## Step 8: Deploy and Initialize

### 8.1 Build and Start Container

From your deployment directory:

```bash
cd deployments/newclan
docker-compose up -d --build
```

### 8.2 Check Logs

```bash
docker-compose logs -f bot
```

The bot should:
- Connect to Oracle database
- Initialize tables (if first run)
- Load ranks from `configs/newclan/ranks.json`
- Connect to Discord
- Sync slash commands

### 8.3 Verify Setup

1. Check Discord - bot should be online
2. Run `/xp` command to test bot response
3. Check database - ranks should be loaded
4. Verify logs show no errors

---

## Step 9: Ongoing Management

### View Logs

```bash
cd deployments/newclan
docker-compose logs -f bot
```

### Restart Bot

```bash
docker-compose restart bot
```

### Update Bot

```bash
# Pull latest changes
cd ../..
git pull

# Rebuild and restart
cd deployments/newclan
docker-compose up -d --build
```

### Stop Bot

```bash
docker-compose down
```

---

## Troubleshooting

### Bot Won't Start

- Check `.env` file has all required variables
- Verify Oracle credentials are correct
- Check Docker logs: `docker-compose logs bot`

### Ranks Not Loading

- Verify `configs/newclan/ranks.json` exists and is valid JSON
- Check `CLAN_CONFIG_DIR` matches directory name
- Review logs for JSON parsing errors

### Database Connection Errors

- Verify Oracle user exists and has correct permissions
- Check `ORACLE_DSN` is correct
- Test connection manually: `sqlplus newclan_bot@your_dsn`

### Discord Connection Issues

- Verify bot token is correct
- Check bot has necessary permissions in Discord server
- Ensure bot is invited to the server
- Verify required intents are enabled

---

## Example: Adding "Graves Family" Clan

1. **Create Oracle schema:**
   ```sql
   CREATE USER graves_bot IDENTIFIED BY "secure_password";
   GRANT CREATE SESSION, CREATE TABLE, UNLIMITED TABLESPACE TO graves_bot;
   ```

2. **Create config directory:**
   ```bash
   mkdir -p configs/graves_family
   # Create configs/graves_family/ranks.json
   ```

3. **Create deployment:**
   ```bash
   mkdir -p deployments/graves_family
   # Copy and edit docker-compose.yml
   # Create .env file
   ```

4. **Deploy:**
   ```bash
   cd deployments/graves_family
   docker-compose up -d --build
   ```

---

## Architecture Overview

```
Oracle Database
├── tophat_schema (TophatC clan data)
├── graves_schema (Graves Family clan data)
└── newclan_schema (New clan data)

Docker Host
├── tophat-bot (container)
├── graves-family-bot (container)
└── newclan-bot (container)

Each bot instance:
- Uses same codebase (shared Docker image)
- Has separate .env configuration
- Connects to own Oracle schema
- Loads ranks from own config directory
```

---

## Additional Resources

- `setup_example.env` - Complete environment variable template
- `scripts/setup_oracle_schema.sql` - Oracle schema setup script
- `configs/tophat/ranks.json` - Example rank configuration
- `deployments/tophat/` - Example deployment configuration

