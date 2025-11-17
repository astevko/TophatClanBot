# Troubleshooting Guide

Common issues and solutions for the TophatC Clan Discord Bot.

## Table of Contents

1. [Database Issues](#database-issues)
2. [Systemd Service Issues](#systemd-service-issues)
3. [Discord Command Issues](#discord-command-issues)
4. [Roblox API Issues](#roblox-api-issues)
5. [Permission Issues](#permission-issues)

---

## Database Issues

### Error: "no such table: members"

**Symptom**: Bot crashes with `sqlite3.OperationalError: no such table: members`

**Cause**: Bot is using SQLite fallback instead of configured database (Oracle/PostgreSQL), and the SQLite database isn't initialized.

**Quick Fix**:
```bash
cd ~/TophatClanBot
./check_database_env.sh  # Check which database is configured
```

If using Oracle, ensure `.env` has:
```bash
ORACLE_USER=tophat_bot
ORACLE_PASSWORD=your_password
ORACLE_DSN=perrydatabase_high
ORACLE_CONFIG_DIR=/home/opc/TophatClanBot/wallet_config
```

Then initialize:
```bash
uv run python init_database.py
sudo systemctl restart tophat-bot
```

**Detailed Guide**: See `QUICK_FIX.md` and `SYSTEMD_DATABASE_FIX.md`

### Error: "ORA-12541: TNS:no listener"

**Symptom**: Cannot connect to Oracle database

**Solutions**:
1. Verify `ORACLE_DSN` is correct in `.env`
2. Check network connectivity to Oracle Cloud
3. Verify Oracle database is running in OCI Console
4. Check firewall rules allow port 1522

### Error: "Could not open wallet"

**Symptom**: Oracle connection fails with wallet error

**Solutions**:
```bash
# Verify wallet exists
ls -la /home/opc/TophatClanBot/wallet_config/

# Fix permissions
chmod 700 /home/opc/TophatClanBot/wallet_config
chmod 600 /home/opc/TophatClanBot/wallet_config/*
chown -R opc:opc /home/opc/TophatClanBot/wallet_config

# Verify ORACLE_CONFIG_DIR is set correctly
cat .env | grep ORACLE_CONFIG_DIR
```

### Database Connection Pool Exhausted

**Symptom**: Bot slows down or stops responding

**Solution**: Edit `database_oracle.py` and increase pool size:
```python
pool = oracledb.create_pool(
    min=5,
    max=20,  # Increase from default
    increment=2
)
```

---

## Systemd Service Issues

### Service won't start

**Check status**:
```bash
sudo systemctl status tophat-bot
```

**Check logs**:
```bash
sudo journalctl -u tophat-bot -n 50
```

**Common issues**:
1. **Missing .env file**: Ensure `/home/opc/TophatClanBot/.env` exists
2. **Wrong Python path**: Verify `ExecStart` path in service file
3. **Permission issues**: Check file ownership and permissions
4. **Missing dependencies**: Run `uv sync` or `pip install -r requirements.txt`

### Service starts but crashes immediately

**Watch logs**:
```bash
sudo journalctl -u tophat-bot -f
```

Look for error messages about:
- Missing environment variables
- Database connection failures
- Import errors (missing packages)
- Permission denied errors

### Environment variables not loading

**Symptom**: Bot uses wrong database or can't find configuration

**Solution 1**: Use wrapper script
```bash
chmod +x /home/opc/TophatClanBot/start-bot.sh
sudo nano /etc/systemd/system/tophat-bot.service
```

Change `ExecStart` to:
```ini
ExecStart=/home/opc/TophatClanBot/start-bot.sh
```

**Solution 2**: Set variables directly in service file
```ini
Environment="ORACLE_USER=tophat_bot"
Environment="ORACLE_PASSWORD=your_password"
Environment="ORACLE_DSN=perrydatabase_high"
# ... etc
```

After changes:
```bash
sudo systemctl daemon-reload
sudo systemctl restart tophat-bot
```

---

## Discord Command Issues

### Commands not showing up in Discord

**Symptom**: Slash commands don't appear in Discord

**Cause**: Commands not synced to Discord

**Solution**:
```bash
# Restart bot to trigger sync
sudo systemctl restart tophat-bot

# Check logs for sync confirmation
sudo journalctl -u tophat-bot | grep -i "sync"
```

Should see: "Synced commands to guild"

### Commands fail with "Missing Permissions"

**Symptom**: Commands work for some users but not others

**Cause**: Missing admin role or permissions

**Solution**:
1. Verify user has one of these:
   - Administrator permission
   - Role matching `ADMIN_ROLE_NAME` in `.env`
   - User ID in `ADMIN_USER_IDS` list

2. Check role configuration in `.env`:
```bash
cat .env | grep ROLE
```

### Command timeout

**Symptom**: Command takes too long and Discord shows error

**Cause**: Database query slow or Roblox API slow

**Solutions**:
1. Respond with "thinking" immediately:
```python
await interaction.response.defer(ephemeral=True)
# ... do work ...
await interaction.followup.send("Result")
```

2. Check database performance
3. Check Roblox API rate limits

---

## Roblox API Issues

### Error: "Failed to verify Roblox credentials"

**Symptom**: Bot starts but can't connect to Roblox

**Solution**:
```bash
# Check credentials in .env
cat .env | grep ROBLOX

# Test manually
uv run python -c "
import asyncio
import roblox_api
asyncio.run(roblox_api.verify_roblox_credentials())
"
```

Ensure one of these is set:
- `ROBLOX_API_KEY` (preferred)
- `ROBLOX_COOKIE` (alternative)

### Error: "Rate limit exceeded"

**Symptom**: Roblox commands fail intermittently

**Cause**: Too many API requests

**Solution**: Bot has built-in retry logic. If persistent:
1. Reduce frequency of rank syncs
2. Check for loops making excessive API calls
3. Consider caching Roblox data

### Group rank updates fail

**Symptom**: `/sync-rank` command doesn't update Roblox rank

**Cause**: Insufficient permissions or wrong group

**Solution**:
1. Verify bot account has group permissions to change ranks
2. Check `ROBLOX_GROUP_ID` is correct
3. Verify Roblox API key/cookie is for an account with group admin permissions

---

## Permission Issues

### Bot can't update Discord roles

**Symptom**: Rank promotions don't update Discord roles

**Cause**: Bot missing Discord permissions

**Solution**:
1. In Discord, go to Server Settings > Roles
2. Find bot's role
3. Ensure it has:
   - Manage Roles ✓
   - View Channels ✓
4. Ensure bot's role is ABOVE the roles it needs to assign

### Bot can't read/write files

**Symptom**: Permission denied errors for database or logs

**Solution**:
```bash
# Fix ownership
sudo chown -R opc:opc /home/opc/TophatClanBot

# Fix permissions
chmod 755 /home/opc/TophatClanBot
chmod 644 /home/opc/TophatClanBot/*.py
chmod 600 /home/opc/TophatClanBot/.env
chmod 644 /home/opc/TophatClanBot/tophat_clan.db  # if using SQLite
```

---

## Diagnostic Tools

### Quick health check
```bash
cd ~/TophatClanBot
./check_database_env.sh
```

### Test database connection
```bash
# Oracle
uv run python test_oracle_connection.py

# General
uv run python diagnose_database.py
```

### Initialize/reset database
```bash
uv run python init_database.py
```

### View logs
```bash
# Systemd logs (last 50 lines)
sudo journalctl -u tophat-bot -n 50

# Systemd logs (follow/live)
sudo journalctl -u tophat-bot -f

# Bot log file
tail -f bot.log
```

### Check bot status
```bash
# Service status
sudo systemctl status tophat-bot

# Is bot process running?
ps aux | grep bot.py

# Check resource usage
top -p $(pgrep -f bot.py)
```

---

## Getting Help

If you're still stuck after trying these solutions:

1. **Gather information**:
   ```bash
   # System info
   uname -a
   python --version
   
   # Bot status
   sudo systemctl status tophat-bot
   
   # Recent logs
   sudo journalctl -u tophat-bot -n 100 > bot_logs.txt
   
   # Environment check
   ./check_database_env.sh > env_check.txt
   ```

2. **Check existing documentation**:
   - `QUICK_FIX.md` - Common database issue
   - `SYSTEMD_DATABASE_FIX.md` - Detailed systemd troubleshooting
   - `ORACLE_DEPLOYMENT_GUIDE.md` - Oracle setup
   - `COMMANDS_GUIDE.md` - Command usage

3. **Report issue** with:
   - Error message (full traceback if available)
   - What you were trying to do
   - What you've already tried
   - Output from diagnostic tools

---

## Prevention Tips

### Regular maintenance
```bash
# Check bot health daily
./check_database_env.sh
sudo systemctl status tophat-bot

# Check logs for errors
sudo journalctl -u tophat-bot --since "1 hour ago" | grep -i error

# Monitor disk space
df -h

# Monitor database size (Oracle)
# Check in OCI Console > Autonomous Database > Metrics
```

### Backup regularly
```bash
# See BACKUP_RESTORE_GUIDE.md for detailed instructions

# Quick backup of config
cp .env .env.backup.$(date +%Y%m%d)
```

### Keep updated
```bash
cd ~/TophatClanBot
git pull
uv sync  # or: pip install -r requirements.txt
sudo systemctl restart tophat-bot
```

---

**Last Updated**: November 16, 2025

