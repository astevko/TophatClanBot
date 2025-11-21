# Critical Database Import Fix

## Date: November 17, 2025

## Problem Identified

The bot was experiencing a critical bug where:
- **Startup**: Bot correctly connected to Oracle database ✅
- **Runtime**: Commands tried to use SQLite database ❌

### Error Message
```
sqlite3.OperationalError: no such table: members
```

### Root Cause

The command files had **hardcoded imports** that bypassed the database selection logic:

**bot.py** (correct):
```python
# Conditional import based on configuration
if Config.USE_ORACLE:
    import database_oracle as database
elif Config.USE_SQLITE:
    import database
else:
    import database_postgres as database
```

**commands/admin_commands.py** (incorrect):
```python
import database  # Always imports SQLite module!
```

**commands/user_commands.py** (incorrect):
```python
import database  # Always imports SQLite module!
```

**roblox_api.py** (incorrect):
```python
import database  # Always imports SQLite module! (3 lazy imports)
```

This caused a **split-brain scenario**:
- Bot initialization used `database_oracle` ✅
- All commands used `database` (SQLite) ❌

## Fix Applied

Updated all command and API files to use the same conditional import logic:

### Changes Made

1. **commands/admin_commands.py** (lines 13-22)
2. **commands/user_commands.py** (lines 14-22)
3. **roblox_api.py** (lines 291-296, 334-339, 380-385 - three functions)

All now include:
```python
# Import appropriate database module based on configuration
if Config.USE_ORACLE:
    import database_oracle as database
elif Config.USE_SQLITE:
    import database
else:
    import database_postgres as database
```

## Deployment Instructions

### On Your Oracle Cloud Server:

```bash
# 1. SSH to server
ssh opc@perry.stevko.xyz

# 2. Go to bot directory
cd ~/TophatClanBot

# 3. Pull latest changes
git pull

# 4. Restart the bot
sudo systemctl restart tophat-bot

# 5. Verify it's working
sudo journalctl -u tophat-bot -n 50 | grep -i database
```

You should see:
```
Using Oracle database (production)
Oracle connection pool created
Oracle database initialized successfully
```

### Testing

After restarting, test with Discord commands:
- `/check-member` - Should work now ✅
- `/xp` - Should show member data from Oracle ✅
- Any other command - Should access Oracle database ✅

## Impact

**Before Fix**:
- ❌ All Discord commands failed with "no such table" errors
- ❌ Bot couldn't access member data
- ❌ All database operations in commands failed

**After Fix**:
- ✅ All commands now use the correct database
- ✅ Bot consistently uses Oracle throughout
- ✅ Member data accessible from commands

## Prevention

This issue highlights the importance of:
1. **Centralized configuration** - All modules should respect the database selection logic
2. **Testing commands** after deployment, not just bot startup
3. **Code review** - Catch hardcoded imports that bypass configuration

## Technical Details

### Module Resolution

Python's `import database` statement:
- Looks for `database.py` in the current directory or Python path
- Does NOT respect the conditional import logic in other files
- Each Python file has its own import namespace

### Why It Appeared to Work at First

The bot **startup code** (`bot.py`) correctly used Oracle:
- Created connection pool ✅
- Initialized tables ✅
- Verified connection ✅

But **command execution** happened in a different import context:
- Commands loaded their own imports
- Used `database.py` (SQLite) directly
- Never saw the Oracle configuration

### Proper Solution

All files that need database access must either:
1. Use the same conditional import logic (current fix)
2. Import from a common database wrapper module
3. Receive database as a dependency injection

We chose option 1 for consistency with `bot.py`.

## Files Changed

- `commands/admin_commands.py` - Updated database import logic
- `commands/user_commands.py` - Updated database import logic
- `roblox_api.py` - Updated database import logic (3 lazy imports fixed)

## Verification

Logs showing the problem (before fix):
```
2025-11-17 05:04:48,065 - database_oracle - INFO - Oracle connection pool created
[...startup uses Oracle...]

2025-11-17 05:06:11,948 - aiosqlite - DEBUG - executing functools.partial(<built-in method close of sqlite3.Connection...
[...commands use SQLite...]
```

After fix, both startup AND commands should show Oracle operations only.

## Related Documents

- `QUICK_FIX.md` - General database troubleshooting (kept for reference)
- `SYSTEMD_DATABASE_FIX.md` - Systemd-specific issues (kept for reference)
- `TROUBLESHOOTING.md` - Comprehensive troubleshooting guide

Note: The diagnostic tools created earlier are still useful for verifying database configuration.

---

**Status**: ✅ FIXED
**Deployed**: Pending (needs git pull on server)
**Verified**: Pending (test after deployment)

