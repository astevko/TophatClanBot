# 🚀 Deploy the Database Import Fix

## What This Fixes

Commands like `/check-member` were failing with "no such table: members" because command files were hardcoded to use SQLite instead of respecting your Oracle database configuration.

## Quick Deploy (Copy-Paste)

SSH to your server and run these commands:

```bash
# Go to bot directory
cd ~/TophatClanBot

# Pull the latest code
git pull origin main

# Restart the bot
sudo systemctl restart tophat-bot

# Watch the logs to verify it's working
sudo journalctl -u tophat-bot -f
```

Press `Ctrl+C` to stop watching logs.

## Verify the Fix

### Method 1: Check the logs
```bash
sudo journalctl -u tophat-bot -n 100 | grep -E "database|Database"
```

You should see **only** Oracle references, no SQLite/aiosqlite messages.

### Method 2: Test in Discord

Try these commands:
- `/check-member @someone` - Should work now ✅
- `/xp` - Should show your stats ✅
- `/leaderboard` - Should display top members ✅

## Before and After

### Before (broken):
```
2025-11-17 05:04:48 - Using Oracle database (production)     ✅ Startup OK
2025-11-17 05:06:11 - aiosqlite - executing...              ❌ Commands use SQLite!
ERROR: no such table: members
```

### After (fixed):
```
2025-11-17 05:04:48 - Using Oracle database (production)     ✅ Startup OK
2025-11-17 05:06:11 - database_oracle - executing query...   ✅ Commands use Oracle!
```

## Troubleshooting

### If git pull fails with "uncommitted changes"
```bash
# Stash your local changes
git stash

# Pull the fix
git pull origin main

# Reapply your changes (if needed)
git stash pop
```

### If the bot still fails after restart
```bash
# Check what's happening
sudo journalctl -u tophat-bot -n 200

# Verify environment is correct
cd ~/TophatClanBot
cat .env | grep ORACLE
```

Ensure you see:
```
ORACLE_USER=tophat_bot
ORACLE_PASSWORD=...
ORACLE_DSN=perrydatabase_high
ORACLE_CONFIG_DIR=/home/opc/TophatClanBot/wallet_config
```

## Complete Deployment Steps

For the cautious deployer:

```bash
# 1. SSH to server
ssh opc@perry.stevko.xyz

# 2. Navigate to bot directory
cd ~/TophatClanBot

# 3. Check current status
sudo systemctl status tophat-bot

# 4. Backup current .env (just in case)
cp .env .env.backup.$(date +%Y%m%d)

# 5. Pull latest code
git pull origin main

# 6. Verify the changes were applied
grep -A 5 "Import appropriate database" commands/admin_commands.py

# Should show the conditional import logic

# 7. Restart the bot
sudo systemctl restart tophat-bot

# 8. Wait a few seconds for startup
sleep 5

# 9. Check status
sudo systemctl status tophat-bot

# 10. View recent logs
sudo journalctl -u tophat-bot -n 50

# 11. Test in Discord
# Try: /check-member or /xp
```

## What Changed

Two files were updated to fix the database import:

1. **commands/admin_commands.py**
   - Now uses conditional import logic
   - Respects Oracle/PostgreSQL/SQLite configuration

2. **commands/user_commands.py**
   - Now uses conditional import logic
   - Respects Oracle/PostgreSQL/SQLite configuration

## Success Indicators

✅ Bot starts without errors
✅ Logs show "Using Oracle database (production)"
✅ No "aiosqlite" messages in logs during command execution
✅ Commands like `/check-member` work in Discord
✅ No "no such table" errors

## If You Need Help

Run the diagnostic:
```bash
cd ~/TophatClanBot
./check_database_env.sh
```

Or check the comprehensive guide:
```bash
cat CRITICAL_FIX_APPLIED.md
```

---

**Estimated Time**: 2 minutes
**Downtime**: ~5 seconds (during restart)
**Risk Level**: Low (only import logic changed, no data modifications)

