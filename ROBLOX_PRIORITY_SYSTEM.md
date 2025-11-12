# Roblox Priority System - Source of Truth

## 🎯 Overview

The bot now treats **Roblox group ranks as the authoritative source of truth**. Discord ranks and database ranks automatically sync FROM Roblox, ensuring your Roblox group is always the primary system.

---

## 🔄 How It Works

### Priority Hierarchy
```
Roblox Group Rank (Source of Truth)
         ↓
    [Auto-Sync]
         ↓
Discord/Database Rank (Updated Automatically)
```

**Key Principle:** Whenever there's a mismatch, Roblox wins and Discord is updated to match.

---

## ✨ Automatic Sync Points

The system automatically syncs FROM Roblox in these scenarios:

### 1. **When Linking Account** (`/link-roblox`)
```
User runs: /link-roblox JohnDoe
  ↓
Bot verifies user in Roblox group
  ↓
Bot fetches current Roblox rank
  ↓
Bot sets Discord rank to match Roblox
  ↓
✅ Account linked with correct rank from Roblox
```

**User Experience:**
```
✅ Successfully linked your account to JohnDoe!
📊 Your current Roblox rank: E2 | Specialist (Rank 4)
🎖️ Discord rank set to: E2 | Specialist
💡 Your ranks will stay synced automatically.
```

If updating an existing link and rank changed:
```
✅ Updated your Roblox username to JohnDoe!
📊 Your current Roblox rank: E3 | Lance Corporal (Rank 5)
🔄 Discord rank synced: E2 | Specialist → E3 | Lance Corporal
```

---

### 2. **When Checking XP** (`/xp`)
```
User runs: /xp
  ↓
Bot syncs rank from Roblox FIRST
  ↓
Bot displays current stats
  ↓
Shows notification if rank was synced
```

**User Experience (No Change):**
```
📊 YourName's Progress
Current Rank: E2 | Specialist
Total Points: 5
Next Rank: E3 | Lance Corporal
Progress: 5/35 (30 points needed)
```

**User Experience (Rank Synced):**
```
📊 YourName's Progress
Current Rank: E3 | Lance Corporal
Total Points: 5

🔄 Auto-Synced
Your rank was updated from Roblox: E2 | Specialist → E3 | Lance Corporal
```

---

### 3. **Before Promotion** (`/promote`)
```
Admin runs: /promote @JohnDoe
  ↓
Bot syncs rank from Roblox FIRST
  ↓
Bot proceeds with promotion from current Roblox rank
```

**Admin Experience (Rank Synced First):**
```
🔄 Rank Synced from Roblox First
@JohnDoe's rank was updated from Roblox: E1 | Soldier → E2 | Specialist

Proceeding with promotion...

✅ Promotion Successful
@JohnDoe has been promoted!
Previous Rank: E2 | Specialist
New Rank: E3 | Lance Corporal
```

This ensures promotions are always based on the member's TRUE current rank in Roblox.

---

### 4. **When Checking Member Stats** (`/check-member`)
```
Admin runs: /check-member @JohnDoe
  ↓
Bot syncs rank from Roblox FIRST
  ↓
Bot displays accurate current stats
```

**Admin Experience:**
```
📊 Member Stats: JohnDoe

Discord: @JohnDoe
Roblox: JohnDoe123
Current Rank: E3 | Lance Corporal
Total Points: 15

🔄 Auto-Synced
Rank was updated from Roblox: E2 | Specialist → E3 | Lance Corporal
```

---

### 5. **Background Sync** (Every Hour)
```
Every 1 hour automatically:
  ↓
Bot syncs ALL members from Roblox
  ↓
Updates Discord ranks/roles as needed
  ↓
Logs all changes
```

**Frequency:** Every **1 hour** (changed from 6 hours)

**Logs:**
```
[INFO] 🔄 Starting automatic rank synchronization...
[INFO] Auto-synced Player1: E0 | Enlist -> E1 | Soldier
[INFO] Auto-synced Player2: E2 | Specialist -> E3 | Lance Corporal
[INFO] ✅ Automatic sync complete: 8 updated, 42 in sync, 0 errors
```

---

## 📋 Manual Sync Commands

Admins can still manually trigger syncs:

### `/verify-rank @member`
Check if a member's ranks match (Discord vs Roblox)

### `/sync @member`
Force sync a specific member from Roblox

### `/sync`
Bulk sync ALL members from Roblox

---

## 🔍 What Changed from Previous Version

### Before (v2.0)
- Manual sync only
- 6-hour background sync
- Roblox and Discord could desync
- Syncing required admin action

### After (v2.1 - Current)
- **Auto-sync on every user interaction** ✨
- **1-hour background sync** ⚡
- **Roblox is always source of truth** 🎯
- **Ranks stay synced without admin intervention** 🚀

---

## 💡 Use Cases

### Scenario 1: Promoted in Roblox
```
1. Admin promotes user in Roblox group: Private → Soldier
2. User checks /xp in Discord
3. Bot detects mismatch, syncs from Roblox
4. User sees updated rank in Discord automatically
```

### Scenario 2: New Member Joins
```
1. New member already has rank in Roblox: Specialist
2. Member links account: /link-roblox Username
3. Bot sets Discord rank to match Roblox: Specialist
4. Member starts with correct rank immediately
```

### Scenario 3: Demoted in Roblox
```
1. User demoted in Roblox: Corporal → Private
2. Background sync runs (every hour)
3. Bot detects mismatch, updates Discord
4. User's Discord rank changed to Private
```

### Scenario 4: Admin Promotes in Discord
```
1. Admin runs: /promote @member
2. Bot syncs from Roblox FIRST
3. Bot promotes from current Roblox rank
4. Bot updates BOTH Discord and Roblox
```

---

## ⚙️ Configuration

### Background Sync Frequency

Change in `bot.py` line 194:
```python
@tasks.loop(hours=1)  # Adjust this value
async def auto_sync_ranks(self):
```

Recommended values:
- `hours=1` - Hourly sync (current, recommended)
- `hours=2` - Every 2 hours (lighter load)
- `minutes=30` - Every 30 minutes (very frequent)

---

## 📊 Sync Statistics

The system tracks all syncs:

- ✅ **Successful syncs** - Logged with member name and rank change
- ⚠️ **Already in sync** - No action needed
- ❌ **Errors** - Logged with error details

**View in logs:**
```
[INFO] Auto-synced Player1 on /xp: E0 | Enlist → E1 | Soldier
[INFO] Auto-synced Player2 on check-member: E1 | Soldier → E2 | Specialist
[INFO] Pre-promotion sync for Player3: E2 | Specialist → E3 | Lance Corporal
```

---

## 🎯 Benefits

### 1. **Single Source of Truth**
- Roblox group is the authoritative system
- No more confusion about "real" ranks
- Easier to manage ranks in one place

### 2. **Automatic Consistency**
- Ranks stay in sync without manual work
- Users always see their current Roblox rank
- No manual sync commands needed

### 3. **Transparent Updates**
- Users see when their rank syncs
- Clear notifications on rank changes
- All syncs are logged

### 4. **Admin Friendly**
- Promote in Roblox OR Discord
- Both systems stay synced
- Can verify sync status anytime

### 5. **User Friendly**
- Always see current rank
- No need to wait for sync
- Instant feedback on rank changes

---

## 🔧 Technical Details

### Sync Process Flow
```python
async def auto_sync_process():
    1. Get current Roblox rank via API
    2. Get current Discord rank from database
    3. Compare Roblox rank ID vs Discord rank ID
    4. If mismatch:
       - Find matching database rank for Roblox rank ID
       - Update database with new rank
       - Update Discord role
       - Log the change
    5. Return sync result
```

### Key Functions

**`sync_member_rank_from_roblox(discord_id)`**
- Fetches Roblox rank
- Compares with Discord rank
- Updates if mismatch found
- Returns detailed result

**`compare_ranks(member_data)`**
- Compares Discord vs Roblox
- Returns mismatch details
- Returns `None` if in sync

**`get_database_rank_by_roblox_id(rank_id)`**
- Maps Roblox rank ID to database rank
- Handles rank matching

---

## 🚨 Important Notes

### Admin-Only Ranks
Admin-only ranks (like leadership roles) are **NOT automatically synced**.

**Why?**
- These are special Discord-only ranks
- Not based on Roblox group ranks
- Assigned manually by HICOM

**Example:**
```
Member promoted to "Gold Leader" in Discord
→ This is an admin-only rank
→ Won't be overwritten by Roblox sync
→ Stays until manually changed
```

### Point-Based vs Admin Ranks
- **Point-based ranks** sync from Roblox ✅
- **Admin-only ranks** stay in Discord unless manually changed ✅

---

## 📈 Performance

### API Call Optimization
- Only syncs when needed (checks mismatch first)
- Background sync spreads load over time
- API calls are rate-limited safe

### Discord Rate Limits
- Role updates use Discord API efficiently
- Syncs don't trigger rate limits
- Background task paces updates

---

## 🐛 Troubleshooting

### "My rank won't update"
1. Check if you're in the Roblox group
2. Verify your Roblox username is correct
3. Run `/xp` to trigger manual sync
4. Ask admin to run `/sync @you`

### "I was promoted in Roblox but Discord still shows old rank"
1. Run `/xp` to trigger immediate sync
2. Wait up to 1 hour for background sync
3. Ask admin to run `/verify-rank @you`

### "Admin rank got overwritten"
- This shouldn't happen! Admin-only ranks are protected
- If it does, report as a bug
- Admin can restore with `/promote`

---

## 📝 Version History

### v2.1 - Roblox Priority System
**Added:**
- Auto-sync on `/link-roblox`
- Auto-sync on `/xp`
- Auto-sync on `/check-member`
- Auto-sync before `/promote`
- Increased background sync to every hour
- Roblox as source of truth

**Changed:**
- Background sync: 6 hours → 1 hour
- Linking account now sets rank from Roblox
- All user commands trigger sync check

---

## 🎉 Summary

**Before:** Roblox and Discord could desync, requiring manual admin intervention.

**Now:** Roblox is the source of truth. Discord automatically stays in sync. Users and admins barely need to think about it.

**Result:** One less thing to manage, happier members, accurate ranks everywhere! 🚀

---

**Last Updated:** November 12, 2025  
**Version:** 2.1 - Roblox Priority System  
**Status:** ✅ Fully Implemented

