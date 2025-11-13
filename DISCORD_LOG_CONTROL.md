# Discord Log Level Control Command

**Date:** November 13, 2025  
**Status:** ✅ Implemented  
**Command:** `/set-discord-log-level`  
**Permission:** Admin only

---

## Overview

This command allows administrators to dynamically control which log levels are sent to the Discord logging channel **without restarting the bot**. This is useful for reducing noise, troubleshooting, or temporarily disabling Discord logging.

---

## Command Usage

### Command
```
/set-discord-log-level
```

### Options

The command provides four choices:

| Option | Value | What Gets Logged to Discord |
|--------|-------|----------------------------|
| **Critical Only** | `CRITICAL` | Only CRITICAL logs (most severe) |
| **Error and Critical** | `ERROR` | ERROR and CRITICAL logs only |
| **Warning, Error, and Critical** | `WARNING` | WARNING, ERROR, and CRITICAL (default) |
| **None (Disable)** | `NONE` | Nothing - Discord logging disabled |

---

## Examples

### Example 1: Show Only Errors (Your Request!)

To stop all logs except ERROR and CRITICAL:

```
/set-discord-log-level level: Error and Critical
```

**Result:**
- ✅ ERROR messages shown in Discord
- ✅ CRITICAL messages shown in Discord
- ❌ WARNING messages excluded
- ❌ INFO messages excluded (already excluded by default)

### Example 2: Disable Discord Logging Completely

During maintenance or to reduce rate limiting:

```
/set-discord-log-level level: None (Disable Discord Logging)
```

**Result:**
- ❌ No logs sent to Discord
- ✅ All logs still saved to `bot.log` file
- Useful during bulk operations or debugging

### Example 3: Only Show Critical Issues

Show only the most severe problems:

```
/set-discord-log-level level: Critical Only
```

**Result:**
- ✅ CRITICAL logs only
- ❌ ERROR, WARNING, INFO excluded

### Example 4: Restore Default

Return to normal logging:

```
/set-discord-log-level level: Warning, Error, and Critical
```

**Result:**
- ✅ WARNING, ERROR, and CRITICAL logs
- This is the default setting

---

## How It Works

### Technical Implementation

**1. Class Variable in DiscordHandler**
```python
class DiscordHandler(logging.Handler):
    # Class variable to control minimum log level sent to Discord
    min_discord_level = 'WARNING'  # Default
```

**2. Dynamic Filtering**
```python
# Filter based on minimum log level setting
allowed_levels = {
    'CRITICAL': ['CRITICAL'],
    'ERROR': ['ERROR', 'CRITICAL'],
    'WARNING': ['WARNING', 'ERROR', 'CRITICAL'],
}

if level not in allowed_levels.get(DiscordHandler.min_discord_level, []):
    return  # Skip sending to Discord
```

**3. Command Updates Class Variable**
```python
# Change takes effect immediately
DiscordHandler.min_discord_level = 'ERROR'
```

---

## Command Response

When you run the command, you'll see a response like this:

```
✅ Discord Log Level Updated

Discord logging channel will now show: ERROR and CRITICAL logs only

Previous Level: WARNING
New Level: ERROR

ℹ️ Note
This change is immediate. All logs still go to bot.log file.
```

---

## Use Cases

### Use Case 1: Reduce Noise (Your Scenario!)

**Problem:** Too many WARNING messages cluttering Discord channel

**Solution:**
```
/set-discord-log-level level: Error and Critical
```

**Result:** Discord shows only actual errors and critical issues

---

### Use Case 2: Troubleshooting

**Problem:** Need to see all warnings temporarily for debugging

**Solution:**
```
/set-discord-log-level level: Warning, Error, and Critical
```

**Result:** Full visibility of issues

---

### Use Case 3: Bulk Operations

**Problem:** Running bulk sync that generates many logs

**Solution:**
```
/set-discord-log-level level: None
# Run bulk sync operation
/set-discord-log-level level: Error and Critical
```

**Result:** Discord channel stays clean during bulk operations

---

### Use Case 4: Production Stability

**Problem:** Only want to know about serious issues in production

**Solution:**
```
/set-discord-log-level level: Error and Critical
```

**Result:** Only errors and critical issues alert you

---

## Important Notes

### 1. All Logs Still Saved
**No matter the Discord log level**, all logs (including DEBUG and INFO) are **always saved** to `bot.log` file.

- Discord logging affects **Discord channel only**
- File logging remains unchanged
- You can always review full logs in `bot.log`

### 2. Change is Immediate
- No bot restart required
- Takes effect for next log message
- Temporary (resets on bot restart to default)

### 3. Resets on Restart
- Bot restart resets to default (`WARNING`)
- To make permanent, would need config file change
- Current implementation is session-based

### 4. Admin Only
- Only administrators can use this command
- Changes affect all users
- Logged to bot.log for audit trail

---

## Log Level Hierarchy

From least to most severe:

```
DEBUG < INFO < WARNING < ERROR < CRITICAL
```

**Current Filtering:**
- DEBUG: Never sent to Discord
- INFO: Never sent to Discord
- WARNING: Sent if level is WARNING or lower
- ERROR: Sent if level is ERROR or lower
- CRITICAL: Always sent (unless NONE)

---

## Monitoring

### Check Current Setting

The current log level is stored in the class variable and can be checked:

```python
from bot import DiscordHandler
print(DiscordHandler.min_discord_level)
```

### View Changes in Logs

All changes are logged:

```bash
grep "changed Discord log level" bot.log
```

Example output:
```
2025-11-13 12:00:00 - AdminCommands - INFO - JohnDoe changed Discord log level from WARNING to ERROR
```

---

## Recommended Settings

### By Server Size

| Server Size | Recommended Level | Reasoning |
|-------------|------------------|-----------|
| Small (< 100) | WARNING | See all issues |
| Medium (100-1000) | ERROR | Reduce noise |
| Large (1000+) | ERROR or CRITICAL | Only serious issues |

### By Environment

| Environment | Recommended Level | Reasoning |
|-------------|------------------|-----------|
| Development | WARNING | Full visibility |
| Staging | WARNING or ERROR | Testing alerts |
| Production | ERROR | Stable, only errors |

---

## Troubleshooting

### Not Seeing Expected Logs?

**Check:**
1. Current log level setting
2. Log message level (is it WARNING when level is ERROR?)
3. Discord channel permissions
4. Bot.log file (logs should be there)

### Too Many Logs Still?

**Solution:**
1. Set to ERROR or CRITICAL
2. Check if actual errors need fixing
3. Consider disabling temporarily with NONE

### Forgot Current Setting?

**Check bot.log:**
```bash
grep "changed Discord log level" bot.log | tail -1
```

Or restart bot (resets to WARNING)

---

## Code Changes

### Files Modified

**1. `bot.py`** - DiscordHandler class
```python
# Added class variable
min_discord_level = 'WARNING'

# Added dynamic filtering logic
allowed_levels = {
    'CRITICAL': ['CRITICAL'],
    'ERROR': ['ERROR', 'CRITICAL'],
    'WARNING': ['WARNING', 'ERROR', 'CRITICAL'],
}
```

**2. `commands/admin_commands.py`** - New command
```python
@app_commands.command(name="set-discord-log-level", ...)
async def set_discord_log_level(self, interaction, level):
    DiscordHandler.min_discord_level = level
```

---

## Testing

### Test Plan

**1. Test Each Level:**
```
/set-discord-log-level level: Error and Critical
# Trigger a WARNING - should not appear in Discord
# Trigger an ERROR - should appear in Discord
```

**2. Test NONE:**
```
/set-discord-log-level level: None
# Trigger any log - should not appear in Discord
# Check bot.log - should still have all logs
```

**3. Test Level Changes:**
```
/set-discord-log-level level: Critical Only
/set-discord-log-level level: Error and Critical
# Verify each change takes effect immediately
```

**4. Test Persistence:**
```
/set-discord-log-level level: Error and Critical
# Restart bot
# Check default is WARNING again
```

---

## Future Enhancements

### Possible Improvements

1. **Persist Setting Across Restarts**
   - Store in database or config file
   - Auto-restore on startup

2. **Per-Channel Log Levels**
   - Different levels for different channels
   - Admin channel vs general logs

3. **Scheduled Log Levels**
   - Lower verbosity during peak hours
   - Higher verbosity during maintenance

4. **View Current Setting Command**
   - `/get-discord-log-level`
   - Show current configuration

---

## Comparison Table

### Before vs After

| Feature | Before | After |
|---------|--------|-------|
| **Control** | Hardcoded in code | Dynamic via command |
| **Change Method** | Edit code + restart | Run command (instant) |
| **Flexibility** | None | 4 levels + disable |
| **Access** | Developer only | Admin via Discord |
| **Restart Required** | Yes | No |

---

## Summary

### Quick Reference

**To show only ERROR and CRITICAL in Discord:**
```
/set-discord-log-level level: Error and Critical
```

**To disable Discord logging:**
```
/set-discord-log-level level: None
```

**To restore default:**
```
/set-discord-log-level level: Warning, Error, and Critical
```

**Remember:**
- ✅ Changes are immediate
- ✅ All logs still saved to bot.log
- ✅ Resets to WARNING on bot restart
- ✅ Admin only command

---

**Status:** Ready for use  
**Breaking Changes:** None  
**Configuration Required:** None  
**Restart Required:** No (command works immediately)

