# Database Initialization Fix Guide

## Problem
The bot is failing with error: `sqlite3.OperationalError: no such table: members`

This means the database is not properly initialized.

## Quick Fix (On the Server)

### Step 1: SSH into your server
```bash
ssh opc@tophatclan-bot-server
```

### Step 2: Navigate to the bot directory
```bash
cd ~/TophatClanBot
```

### Step 3: Activate the virtual environment
```bash
source .venv/bin/activate
```

### Step 4: Run the diagnostic tool
```bash
python diagnose_database.py
```

This will:
- Check which database type is configured (Oracle/PostgreSQL/SQLite)
- Test the connection
- Initialize the database if it's SQLite
- Provide specific recommendations

### Step 5: Review the output

#### If using SQLite (local development):
The script will automatically initialize the database with all required tables.

#### If using Oracle (intended for production):
Check that your `.env` file has:
```bash
ORACLE_USER=your_username
ORACLE_PASSWORD=your_password
ORACLE_DSN=your_dsn_string
ORACLE_CONFIG_DIR=/path/to/wallet
```

If these are missing or incorrect, the bot falls back to SQLite, which won't have your production data.

#### If using PostgreSQL:
Check that your `.env` file has:
```bash
DATABASE_URL=postgresql://user:password@host:port/database
```

### Step 6: Restart the bot
```bash
# If using systemd
sudo systemctl restart tophat-bot

# Or if running manually
# Stop the current process (Ctrl+C) and run:
python bot.py
```

## Root Cause Analysis

The bot selects a database in this priority order:
1. **Oracle** (if `ORACLE_USER`, `ORACLE_PASSWORD`, and `ORACLE_DSN` are all set)
2. **PostgreSQL** (if `DATABASE_URL` is set and Oracle is not configured)
3. **SQLite** (fallback for local development - uses `tophat_clan.db` file)

The error indicates the bot is using SQLite, but the database file either:
- Doesn't exist
- Is corrupted/empty
- Was deleted

## Prevention

To avoid this issue in the future:

1. **Always set the correct database credentials** in your `.env` file
2. **Back up your database regularly** (use the provided backup scripts)
3. **Monitor the bot logs** for initialization messages:
   - "Using Oracle database (production)"
   - "Using PostgreSQL database (production)"
   - "Using SQLite database (local development)"

## Manual Database Initialization (Alternative)

If the diagnostic script doesn't work, you can manually initialize the database:

```bash
cd ~/TophatClanBot
source .venv/bin/activate
python -c "import asyncio; import database; asyncio.run(database.init_database())"
```

For Oracle:
```bash
python -c "import asyncio; import database_oracle; asyncio.run(database_oracle.init_database())"
```

For PostgreSQL:
```bash
python -c "import asyncio; import database_postgres; asyncio.run(database_postgres.init_database())"
```

## Need Help?

If the issue persists:
1. Check the bot logs: `tail -f bot.log`
2. Check systemd logs: `sudo journalctl -u tophat-bot -f`
3. Verify environment variables: `cat .env | grep -E "ORACLE|DATABASE"`
4. Test database connectivity manually using `test_oracle_connection.py`

