# ⚠️ Bot Restart Required

## New Commands Added

The following new commands have been added but are **not yet registered with Discord**:

- `/list-roblox-ranks` - View all Roblox group ranks with IDs
- `/compare-ranks` - Compare Roblox ranks with database configuration

## 🔄 How to Register New Commands

### Step 1: Stop the Bot
```bash
# Press Ctrl+C to stop the bot
# Or kill the process if running in background
```

### Step 2: Restart the Bot
```bash
# On Linux/Mac:
./run.sh

# On Windows:
run.bat

# Or with Python directly:
python bot.py
```

### Step 3: Verify Commands Are Synced

Check the bot logs for:
```
[INFO] Synced commands to guild XXXXXX
```

Or:
```
[INFO] Synced commands globally
```

### Step 4: Test the Commands

In Discord, type `/` and you should see:
- `/list-roblox-ranks`
- `/compare-ranks`
- `/list-ranks` (existing)
- All other commands

## 🐛 If Commands Still Don't Appear

### Option 1: Force Command Sync

Add this temporary code to `bot.py` in the `setup_hook` method:

```python
# Force sync (temporary - remove after first run)
await self.tree.sync(guild=guild)
logger.info("Force synced commands")
```

### Option 2: Clear Command Cache (Discord Client)

1. Close Discord completely
2. Clear Discord cache:
   - **Windows:** `%appdata%/discord/Cache`
   - **Mac:** `~/Library/Application Support/discord/Cache`
   - **Linux:** `~/.config/discord/Cache`
3. Restart Discord
4. Commands should now appear

### Option 3: Wait for Discord

Sometimes Discord takes a few minutes to register new commands globally.
- **Guild commands:** Usually instant
- **Global commands:** Can take up to 1 hour

## 📊 Current Command Status

After restart, you should have these admin commands:

### Rank Management
- `/promote` - Promote a member
- `/add-points` - Add/remove points
- `/points-remove` - Remove points
- `/check-member` - Check member stats

### Sync Commands
- `/sync` - Sync ranks (single or bulk)
- `/verify-rank` - Check rank mismatch

### Rank Configuration (NEW)
- `/list-roblox-ranks` ⭐ - View Roblox group ranks with IDs
- `/compare-ranks` ⭐ - Compare Roblox with database
- `/list-ranks` - View configured Discord ranks

### Other
- `/set-admin-channel` - Configure admin channel
- `/view-pending` - View pending submissions

## ✅ Verification Checklist

After restart:

- [ ] Bot starts without errors
- [ ] Logs show "Synced commands to guild"
- [ ] Commands appear in Discord when typing `/`
- [ ] `/list-roblox-ranks` works
- [ ] `/compare-ranks` works
- [ ] No "CommandNotFound" errors in logs

## 🔍 Still Having Issues?

### Check Bot Logs

Look for these errors:
```
[ERROR] Failed to sync commands
[ERROR] Command registration failed
```

### Verify Bot Permissions

The bot needs:
- `applications.commands` scope
- `Use Slash Commands` permission

### Check Discord Developer Portal

1. Go to https://discord.com/developers/applications
2. Select your bot
3. Go to "OAuth2" → "URL Generator"
4. Verify `applications.commands` is checked

## 📝 Technical Details

### Why This Happens

Discord slash commands need to be registered with Discord's API. When you add new commands to the code:

1. Bot needs to restart to load new code
2. On startup, `setup_hook()` syncs commands
3. Discord registers the new commands
4. Commands become available

### Command Sync Code (bot.py)

```python
async def setup_hook(self):
    """Called when the bot is starting up."""
    # ... other setup ...
    
    # Sync commands with Discord
    if self.guild_id:
        guild = discord.Object(id=self.guild_id)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)  # ← This registers commands
        logger.info(f"Synced commands to guild {self.guild_id}")
```

---

**Last Updated:** November 12, 2025  
**Issue:** New commands not synced  
**Solution:** Restart bot  
**Status:** ⚠️ Action Required

