# 🚨 QUICK FIX: "no such table: members" Error

## The Problem
Your bot is running on Oracle Cloud with a systemd service, but it's trying to use SQLite instead of the Oracle database, causing the error:
```
sqlite3.OperationalError: no such table: members
```

## The Fix (5 Minutes)

### 1️⃣ SSH to your server
```bash
ssh opc@perry.stevko.xyz
```

### 2️⃣ Go to bot directory
```bash
cd ~/TophatClanBot
```

### 3️⃣ Check if Oracle credentials are in .env
```bash
./check_database_env.sh
```

If you see "⚠️ Bot is configured to use SQLite", continue to next step.

### 4️⃣ Edit .env file and add Oracle credentials
```bash
nano .env
```

Add these lines (use your actual password):
```bash
# Oracle Database Configuration
ORACLE_USER=tophat_bot
ORACLE_PASSWORD=YourActualPasswordHere
ORACLE_DSN=perrydatabase_high
ORACLE_CONFIG_DIR=/home/opc/TophatClanBot/wallet_config
```

Save: `Ctrl+X`, then `Y`, then `Enter`

### 5️⃣ Initialize the Oracle database
```bash
uv run python init_database.py
```

You should see: "✅ Database initialized successfully!"

### 6️⃣ Restart the bot
```bash
sudo systemctl restart tophat-bot
```

### 7️⃣ Verify it's working
```bash
sudo journalctl -u tophat-bot -n 20 | grep database
```

You should see: **"Using Oracle database (production)"**

If you see "Using SQLite database", see [Advanced Fix](#advanced-fix) below.

---

## ✅ Test the Bot

In Discord, try a command like `/check-member` - it should work now!

---

## Advanced Fix

If the bot is still using SQLite after step 7, the systemd service isn't loading the `.env` file correctly.

### Option 1: Use the wrapper script
```bash
# Make start script executable
chmod +x /home/opc/TophatClanBot/start-bot.sh

# Edit systemd service
sudo nano /etc/systemd/system/tophat-bot.service
```

Change the `ExecStart` line to:
```ini
ExecStart=/home/opc/TophatClanBot/start-bot.sh
```

Save, then:
```bash
sudo systemctl daemon-reload
sudo systemctl restart tophat-bot
sudo journalctl -u tophat-bot -f
```

Look for: "Using Oracle database (production)"

### Option 2: Check .env file permissions
```bash
# Ensure bot can read .env
ls -la .env
chmod 600 .env
chown opc:opc .env
```

---

## Quick Commands Reference

| Command | Purpose |
|---------|---------|
| `./check_database_env.sh` | Check which database is configured |
| `uv run python test_oracle_connection.py` | Test Oracle connection |
| `uv run python init_database.py` | Initialize database tables |
| `sudo systemctl status tophat-bot` | Check bot service status |
| `sudo systemctl restart tophat-bot` | Restart the bot |
| `sudo journalctl -u tophat-bot -f` | Watch bot logs live |
| `sudo journalctl -u tophat-bot -n 50` | Show last 50 log lines |

---

## Still Not Working?

Run the comprehensive diagnostic:
```bash
uv run python diagnose_database.py
```

Or check the detailed guide:
```bash
cat SYSTEMD_DATABASE_FIX.md
```

---

## What Happened?

The bot has 3 database options:
1. **Oracle** (production) - requires `ORACLE_USER`, `ORACLE_PASSWORD`, `ORACLE_DSN`
2. **PostgreSQL** (production) - requires `DATABASE_URL`  
3. **SQLite** (local dev) - fallback if neither above is configured

Your systemd service wasn't loading the Oracle credentials from `.env`, so it defaulted to SQLite. SQLite creates an empty database file, which doesn't have your member data.

By adding the Oracle credentials to `.env` and restarting, the bot will now connect to your Oracle database where your actual data lives!

---

**Need Help?** Check `SYSTEMD_DATABASE_FIX.md` for detailed troubleshooting.

