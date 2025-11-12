# Roblox Synchronization Guide

This guide explains the comprehensive Roblox synchronization system implemented in TophatC Clan Bot.

## 🎯 Overview

The bot now features a **bidirectional synchronization system** that keeps Discord ranks, the database, and Roblox group ranks in sync. The system includes automatic verification, manual sync commands, and robust error handling to prevent desynchronization.

---

## ✨ Features Implemented

### 1. **Group Membership Verification** ✅
**Location:** `commands/user_commands.py` - `/link-roblox` command

When users link their Roblox account, the bot now:
- ✅ Verifies the Roblox username exists
- ✅ Confirms they're a member of the configured Roblox group
- ✅ Retrieves their current Roblox rank
- ✅ Displays their Roblox rank information

**User Experience:**
```
/link-roblox username:JohnDoe

✅ Successfully linked your account to JohnDoe!
📊 Your current Roblox rank: E1 | Soldier (Rank 3)
💡 Your Discord rank will be synced with your Roblox rank automatically.
```

**Error Handling:**
- Username doesn't exist → Clear error message
- Not in group → Prompts user to join the group first
- Can't fetch rank → Asks user to try again later

---

### 2. **Manual Rank Verification Command** ✅
**Location:** `commands/admin_commands.py` - `/verify-rank` command

**Usage:** `/verify-rank @member`

Admins can check if a member's Discord rank matches their Roblox rank.

**When Ranks Match:**
```
✅ Ranks In Sync
@JohnDoe's Discord and Roblox ranks match!

Current Rank: E1 | Soldier
Roblox Username: JohnDoe
```

**When Ranks Don't Match:**
```
⚠️ Rank Mismatch Detected
@JohnDoe's Discord and Roblox ranks don't match!

Discord Rank: E0 | Enlist (Order: 2)
Roblox Rank: E1 | Soldier (Rank 3)

Suggested Action:
Update Discord rank to E1 | Soldier
Use /sync @JohnDoe to sync
```

---

### 3. **Manual Sync Command** ✅
**Location:** `commands/admin_commands.py` - `/sync` command

**Usage:** 
- `/sync @member` - Sync a specific member
- `/sync` - Sync ALL members (bulk operation)

#### Single Member Sync
Updates a member's Discord rank to match their current Roblox rank.

**Success Response:**
```
✅ Rank Synced
Successfully synced @JohnDoe's rank from Roblox!

Old Discord Rank: E0 | Enlist
New Discord Rank: E1 | Soldier
Roblox Rank: E1 | Soldier (Rank 3)
```

#### Bulk Sync (All Members)
Syncs all registered members in one operation.

**Response:**
```
✅ Bulk Sync Complete
Synchronized ranks for all registered members

✅ Synced: 12
✓ Already In Sync: 45
❌ Errors: 2

Updates Made:
• Player1: E0 | Enlist → E1 | Soldier
• Player2: E1 | Soldier → E2 | Specialist
• Player3: E3 | Lance Corporal → E4 | Corporal
... and 9 more
```

---

### 4. **Automatic Background Synchronization** ✅
**Location:** `bot.py` - Background task

The bot automatically syncs all members' ranks **every 6 hours**.

**Features:**
- ⏰ Runs automatically in the background
- 🔄 Syncs all registered members
- 📊 Logs sync results
- 🛡️ Error handling prevents crashes

**Configuration:**
You can adjust the sync interval in `bot.py`:
```python
@tasks.loop(hours=6)  # Change this to adjust frequency
async def auto_sync_ranks(self):
```

**Logs:**
```
[INFO] 🔄 Starting automatic rank synchronization...
[INFO] Auto-synced Player1: E0 | Enlist -> E1 | Soldier
[INFO] ✅ Automatic sync complete: 8 updated, 42 in sync, 0 errors
```

---

### 5. **Startup Credential Verification** ✅
**Location:** `bot.py` - `setup_hook()` method

When the bot starts, it automatically verifies Roblox credentials.

**Startup Sequence:**
```
[INFO] Setting up bot...
[INFO] Verifying Roblox API credentials...
[INFO] ✅ Connected to Roblox group: TophatC Clan
[INFO] ✅ Retrieved 23 group roles
[INFO] ✅ Roblox authentication credentials configured
[INFO] ✅ Roblox API credentials verified successfully
[INFO] ✅ Started automatic rank synchronization task
[INFO] Bot setup complete
```

**If Credentials Fail:**
```
[ERROR] Failed to retrieve group info - check ROBLOX_GROUP_ID
[WARNING] ⚠️ Roblox API verification failed - some features may not work
```

---

### 6. **Enhanced Error Handling** ✅
**Location:** `commands/admin_commands.py` - `/promote` command

The promotion system now tracks each operation separately and provides detailed feedback.

**Full Success:**
```
✅ Promotion Successful
@JohnDoe has been promoted!

Previous Rank: E1 | Soldier
New Rank: E2 | Specialist
Total Points: 5

Database: ✅ Database updated
Discord Role: ✅ Discord role updated
Roblox Sync: ✅ Roblox rank updated
Notification: ✅ DM sent
```

**Partial Success (Roblox Sync Failed):**
```
⚠️ Promotion Complete (Roblox Sync Failed)
@JohnDoe has been promoted!

Previous Rank: E1 | Soldier
New Rank: E2 | Specialist
Total Points: 5

Database: ✅ Database updated
Discord Role: ✅ Discord role updated
Roblox Sync: ❌ Roblox sync failed
Notification: ✅ DM sent

⚠️ Action Required
⚠️ Manual Action Required
The member's rank was updated in Discord/Database but NOT in Roblox.
• Use /sync @JohnDoe to retry syncing to Roblox
• Or manually update their rank in the Roblox group
• Error: API returned False - check permissions or rate limits
```

**Logging:**
```
[WARNING] DESYNC: JohnDoe promoted to E2 | Specialist in Discord but Roblox update failed.
          Error: API returned False - check permissions or rate limits
```

---

## 🔧 Technical Details

### New Helper Functions in `roblox_api.py`

1. **`verify_roblox_credentials()`**
   - Verifies API access on startup
   - Tests group info retrieval
   - Checks authentication credentials

2. **`get_database_rank_by_roblox_id(roblox_rank_id)`**
   - Finds the database rank matching a Roblox rank ID
   - Used for rank comparison and syncing

3. **`compare_ranks(discord_member_data)`**
   - Compares Discord and Roblox ranks
   - Returns mismatch details if ranks don't match
   - Returns `None` if ranks are in sync

4. **`sync_member_rank_from_roblox(discord_id)`**
   - Syncs a single member's Discord rank from Roblox
   - Updates database with new rank
   - Returns detailed sync results

### Database Operations

The system uses existing database functions:
- `get_member(discord_id)` - Fetch member data
- `get_rank_by_order(rank_order)` - Get rank details
- `set_member_rank(discord_id, rank_order)` - Update rank
- `get_all_ranks()` - Get all ranks for mapping

---

## 📋 Admin Command Reference

| Command | Description | Usage |
|---------|-------------|-------|
| `/verify-rank @member` | Check if ranks match | `/verify-rank @JohnDoe` |
| `/sync @member` | Sync one member | `/sync @JohnDoe` |
| `/sync` | Sync all members | `/sync` |
| `/promote @member` | Promote (with enhanced error handling) | `/promote @JohnDoe` |

---

## 🔄 Sync Flow Diagram

### User Links Account (`/link-roblox`)
```
User → /link-roblox username
  ↓
Bot verifies username exists
  ↓
Bot checks group membership
  ↓
Bot retrieves Roblox rank
  ↓
Account linked ✅
```

### Promotion with Sync (`/promote`)
```
Admin → /promote @member
  ↓
Update Database ✅
  ↓
Update Discord Role (✅/⚠️)
  ↓
Update Roblox Rank (✅/❌)
  ↓
Send DM notification (✅/⚠️)
  ↓
Send detailed status report
```

### Automatic Sync (Every 6 Hours)
```
Background Task Triggered
  ↓
Fetch all members from database
  ↓
For each member:
  - Get current Roblox rank
  - Compare with Discord rank
  - Update if mismatch found
  - Update Discord role
  ↓
Log results
```

---

## ⚙️ Configuration

### Environment Variables Required

```env
# Roblox Configuration
ROBLOX_GROUP_ID=12345678        # Your Roblox group ID
ROBLOX_API_KEY=your_api_key     # Roblox Open Cloud API key (preferred)
# OR
ROBLOX_COOKIE=your_cookie       # Legacy authentication method
```

### Sync Frequency

Adjust in `bot.py`:
```python
@tasks.loop(hours=6)  # Change to hours=3 for more frequent syncing
```

---

## 🐛 Troubleshooting

### Issue: Roblox sync keeps failing
**Solutions:**
1. Check your `ROBLOX_API_KEY` or `ROBLOX_COOKIE` is valid
2. Verify the bot account has proper permissions in the Roblox group
3. Check for rate limiting (wait a few minutes and try again)
4. Review bot logs for specific error messages

### Issue: Some ranks aren't mapping correctly
**Solutions:**
1. Verify `roblox_group_rank_id` in database matches your actual Roblox group role IDs
2. Use `/verify-rank` to check specific members
3. Check database configuration with `/list-ranks`

### Issue: Background sync not running
**Solutions:**
1. Check bot logs for startup errors
2. Verify the task started: Look for "Started automatic rank synchronization task"
3. Check if bot has been running for at least 6 hours (first sync after 6h)

### Issue: Members getting the wrong rank
**Solutions:**
1. Run `/verify-rank @member` to see the mismatch details
2. Check if the member's Roblox rank ID exists in your database
3. Run `/sync @member` to force a resync
4. Verify rank mappings in database with `/list-ranks`

---

## 📊 Monitoring

### What to Watch in Logs

**Good Signs:**
```
[INFO] ✅ Roblox API credentials verified successfully
[INFO] ✅ Started automatic rank synchronization task
[INFO] Auto-synced Player1: E0 | Enlist -> E1 | Soldier
[INFO] ✅ Automatic sync complete: 8 updated, 42 in sync, 0 errors
```

**Warning Signs:**
```
[WARNING] DESYNC: Player1 promoted to E2 | Specialist in Discord but Roblox update failed
[WARNING] ⚠️ Roblox API verification failed - some features may not work
```

**Error Signs:**
```
[ERROR] Failed to retrieve group info - check ROBLOX_GROUP_ID
[ERROR] Failed to update Roblox rank for Player1: 401 Unauthorized
```

---

## 🎉 Benefits

1. **Automatic Synchronization** - Ranks stay in sync without manual intervention
2. **Error Recovery** - Failed syncs are logged and can be retried with `/sync`
3. **Transparency** - Detailed status reports show exactly what happened
4. **Verification** - Admins can check for mismatches anytime
5. **Bulk Operations** - Sync all members at once when needed
6. **Startup Validation** - Issues are caught when the bot starts
7. **Background Task** - Periodic syncing keeps everything current

---

## 🔐 Security Notes

- The bot requires proper Roblox group permissions to update ranks
- API keys should be kept secure in the `.env` file
- Only admins can run sync commands
- All sync operations are logged for audit purposes

---

## 📝 Change Log

### Version 2.0 - Roblox Sync System

**Added:**
- Group membership verification in `/link-roblox`
- `/verify-rank` command for checking rank mismatches
- `/sync` command for manual synchronization (single and bulk)
- Automatic background synchronization every 6 hours
- Startup credential verification
- Enhanced error handling in `/promote` command
- Detailed sync status reporting
- Desync detection and logging

**Improved:**
- Promotion command now tracks each operation separately
- Better error messages for failed operations
- Clear action items when manual intervention needed

---

## 🚀 Future Enhancements (Potential)

- [ ] Configurable sync frequency per server
- [ ] Sync status dashboard command
- [ ] Automatic retry logic for failed syncs
- [ ] Webhook notifications for critical sync failures
- [ ] Sync history tracking in database
- [ ] Role-based sync (only sync specific ranks)

---

## 📞 Support

If you encounter issues with the Roblox synchronization system:

1. Check the bot logs for error messages
2. Run `/verify-rank @member` to diagnose specific issues
3. Try `/sync @member` to manually force a sync
4. Review this guide's troubleshooting section
5. Verify your Roblox API credentials are configured correctly

---

**Last Updated:** November 12, 2025
**Version:** 2.0
**Status:** ✅ Fully Implemented

