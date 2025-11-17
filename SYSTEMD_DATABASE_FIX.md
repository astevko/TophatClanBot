# Systemd Database Fix Guide

## Problem
The bot is running as a systemd service but trying to use SQLite instead of Oracle, resulting in:
```
sqlite3.OperationalError: no such table: members
```

## Root Cause
The systemd service is not loading the Oracle database credentials from the `.env` file, so the bot falls back to SQLite (local development mode).

## Quick Fix (On Oracle Cloud Server)

### Step 1: SSH into your server
```bash
ssh opc@perry.stevko.xyz
# or
ssh opc@<your-server-ip>
```

### Step 2: Navigate to bot directory
```bash
cd ~/TophatClanBot
```

### Step 3: Check your .env file has Oracle credentials
```bash
cat .env | grep ORACLE
```

You should see:
```bash
ORACLE_USER=tophat_bot
ORACLE_PASSWORD=YourPassword
ORACLE_DSN=perrydatabase_high
ORACLE_CONFIG_DIR=/home/opc/TophatClanBot/wallet_config
```

**If these are missing or commented out**, add them:
```bash
nano .env
```

Add these lines (use your actual credentials):
```bash
# Oracle Database Configuration
ORACLE_USER=tophat_bot
ORACLE_PASSWORD=YourSecurePassword123!
ORACLE_DSN=perrydatabase_high
ORACLE_CONFIG_DIR=/home/opc/TophatClanBot/wallet_config
```

Save and exit (Ctrl+X, Y, Enter)

### Step 4: Verify wallet is in place
```bash
ls -la /home/opc/TophatClanBot/wallet_config/
```

Should show:
- `cwallet.sso`
- `tnsnames.ora`
- `sqlnet.ora`
- Other wallet files

### Step 5: Test database connection
```bash
cd ~/TophatClanBot
source .venv/bin/activate  # If using venv
# OR just use uv:
uv run python test_oracle_connection.py
```

If successful, you'll see:
```
✅ Connected successfully! Query result: 1
✅ Oracle version: 23.x.x.x
```

### Step 6: Initialize Oracle database
```bash
uv run python init_database.py
```

This will create all required tables in your Oracle database.

### Step 7: Restart the systemd service
```bash
sudo systemctl restart tophat-bot
```

### Step 8: Verify the bot is working
```bash
# Check service status
sudo systemctl status tophat-bot

# Watch logs in real-time
sudo journalctl -u tophat-bot -f
```

Look for this line in the logs:
```
Using Oracle database (production)
```

If you see "Using SQLite database", the `.env` file still isn't being loaded correctly.

## Advanced Troubleshooting

### Issue 1: Systemd not loading .env file

If the `.env` file exists but systemd isn't loading it, try this alternative:

**Option A: Specify environment variables directly in service file**

```bash
sudo nano /etc/systemd/system/tophat-bot.service
```

Replace `EnvironmentFile=/home/opc/TophatClanBot/.env` with direct environment variables:

```ini
[Unit]
Description=TophatC Clan Discord Bot
After=network.target

[Service]
Type=simple
User=opc
WorkingDirectory=/home/opc/TophatClanBot
Environment="ORACLE_USER=tophat_bot"
Environment="ORACLE_PASSWORD=YourSecurePassword123!"
Environment="ORACLE_DSN=perrydatabase_high"
Environment="ORACLE_CONFIG_DIR=/home/opc/TophatClanBot/wallet_config"
# Add other environment variables as needed
Environment="DISCORD_BOT_TOKEN=your_token_here"
Environment="GUILD_ID=your_guild_id"
Environment="ROBLOX_GROUP_ID=your_group_id"
Environment="ROBLOX_API_KEY=your_api_key"
Environment="LOG_CHANNEL_ID=your_log_channel_id"
ExecStart=/home/opc/.local/bin/uv run bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Option B: Use a wrapper script**

Create a wrapper script that loads the environment:

```bash
nano /home/opc/TophatClanBot/start-bot.sh
```

Add:
```bash
#!/bin/bash
set -a
source /home/opc/TophatClanBot/.env
set +a
exec /home/opc/.local/bin/uv run bot.py
```

Make it executable:
```bash
chmod +x /home/opc/TophatClanBot/start-bot.sh
```

Update service file:
```bash
sudo nano /etc/systemd/system/tophat-bot.service
```

Change `ExecStart` line:
```ini
ExecStart=/home/opc/TophatClanBot/start-bot.sh
```

After changing the service file:
```bash
sudo systemctl daemon-reload
sudo systemctl restart tophat-bot
```

### Issue 2: Permission issues with .env file

```bash
# Check permissions
ls -la /home/opc/TophatClanBot/.env

# Fix permissions if needed
chmod 600 /home/opc/TophatClanBot/.env
chown opc:opc /home/opc/TophatClanBot/.env
```

### Issue 3: Wallet permission issues

```bash
# Fix wallet permissions
chmod 700 /home/opc/TophatClanBot/wallet_config
chmod 600 /home/opc/TophatClanBot/wallet_config/*
chown -R opc:opc /home/opc/TophatClanBot/wallet_config
```

### Issue 4: Verify environment is loaded

Add a debug line to see what database is being used:

```bash
sudo journalctl -u tophat-bot -n 50 | grep -i database
```

You should see:
```
Using Oracle database (production)
```

If you see:
```
Using SQLite database (local development)
```

Then the Oracle environment variables are NOT being loaded.

## Manual Database Verification

Check what database the bot would use with current environment:

```bash
cd ~/TophatClanBot
uv run python -c "
from config import Config
print(f'USE_ORACLE: {Config.USE_ORACLE}')
print(f'USE_SQLITE: {Config.USE_SQLITE}')
print(f'ORACLE_USER: {Config.ORACLE_USER}')
print(f'ORACLE_DSN: {Config.ORACLE_DSN}')
"
```

Expected output for Oracle:
```
USE_ORACLE: True
USE_SQLITE: False
ORACLE_USER: tophat_bot
ORACLE_DSN: perrydatabase_high
```

If you get `USE_ORACLE: False`, the environment variables aren't loaded.

## Prevention

To prevent this issue in the future:

1. **Always verify .env file** before deploying:
   ```bash
   cat .env | grep ORACLE
   ```

2. **Test database connection** before starting service:
   ```bash
   uv run python test_oracle_connection.py
   ```

3. **Check logs** after starting service:
   ```bash
   sudo journalctl -u tophat-bot -f
   ```

4. **Create a health check script** (optional):
   ```bash
   #!/bin/bash
   # check-bot-health.sh
   
   if sudo journalctl -u tophat-bot -n 50 | grep -q "Using Oracle database"; then
       echo "✅ Bot is using Oracle database"
   elif sudo journalctl -u tophat-bot -n 50 | grep -q "Using SQLite database"; then
       echo "⚠️  WARNING: Bot is using SQLite instead of Oracle!"
       exit 1
   else
       echo "❓ Cannot determine which database is being used"
       exit 2
   fi
   ```

## Summary of Commands

Quick copy-paste for the most common fix:

```bash
# 1. SSH to server
ssh opc@perry.stevko.xyz

# 2. Go to bot directory
cd ~/TophatClanBot

# 3. Check Oracle credentials are in .env
cat .env | grep ORACLE

# 4. If missing, edit .env and add Oracle credentials
nano .env

# 5. Initialize Oracle database
uv run python init_database.py

# 6. Restart service
sudo systemctl restart tophat-bot

# 7. Watch logs
sudo journalctl -u tophat-bot -f
# Press Ctrl+C to stop watching

# 8. Check it's using Oracle
sudo journalctl -u tophat-bot -n 50 | grep "Using Oracle"
```

## Need More Help?

If the issue persists:
1. Share the output of: `cat .env | grep -E "ORACLE|DATABASE"`
2. Share the output of: `sudo journalctl -u tophat-bot -n 100`
3. Check if wallet files exist: `ls -la wallet_config/`
4. Test Oracle connection: `uv run python test_oracle_connection.py`

