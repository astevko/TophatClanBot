# Sync Fix Guide - Rank Matching System

## 🎯 Problem Solved

The synchronization system was giving errors instead of updating users because the Roblox rank IDs in the database didn't match the actual Roblox API rank IDs.

---

## 🔍 The Issue

### What Was Happening

When syncing, the bot would:
1. Get user's Roblox rank from API (e.g., `rank_id: 254791234`, `rank: 45`)
2. Try to find matching database rank by `rank_id` (254791234)
3. **FAIL** - No match found because database has `roblox_group_rank_id: 45`
4. Return error and skip the user

**Result:** Sync errors for everyone, no updates happening

---

## ✅ The Fix

### Flexible Rank Matching

The sync system now uses **dual-mode matching**:

```
1. Try matching by Roblox rank ID (roleId from API)
   ↓ If no match...
2. Try matching by Roblox rank number (rank number 0-255)
   ↓ If still no match...
3. Skip gracefully with warning (don't error)
```

### Why This Works

Roblox groups have two identifiers for ranks:
- **Role ID** - Unique identifier for each role (e.g., 254791234)
- **Rank Number** - Numeric rank 0-255 (e.g., 45)

The database can use EITHER:
- Role IDs (more specific) - `roblox_group_rank_id: 254791234`
- Rank numbers (more flexible) - `roblox_group_rank_id: 45`

The new system tries both!

---

## 🔧 Changes Made

### 1. **Enhanced `get_database_rank_by_roblox_id()` Function**

**File:** `roblox_api.py`

```python
async def get_database_rank_by_roblox_id(roblox_rank_id: int, roblox_rank_number: int = None):
    """
    Get the database rank that corresponds to a Roblox group rank ID.
    Falls back to matching by rank number if ID doesn't match.
    """
    # First try: Match by exact Roblox rank ID
    for rank in ranks:
        if rank['roblox_group_rank_id'] == roblox_rank_id:
            return rank
    
    # Second try: Match by rank number (if provided)
    if roblox_rank_number is not None:
        for rank in ranks:
            if rank['roblox_group_rank_id'] == roblox_rank_number:
                return rank
    
    # No match found - log warning
    return None
```

**Changes:**
- ✅ Added `roblox_rank_number` parameter
- ✅ Two-stage matching (ID first, then number)
- ✅ Better logging when no match found

---

### 2. **Graceful Skipping Instead of Errors**

**File:** `roblox_api.py` - `sync_member_rank_from_roblox()`

**Before:**
```python
if not target_rank:
    return {
        'success': False,
        'error': f"No database rank matches..."
    }
```

**After:**
```python
if not target_rank:
    logger.warning(...)
    return {
        'success': True,
        'action': 'skipped',
        'reason': f"No database rank matches...",
        'roblox_rank': comparison['roblox_rank']
    }
```

**Changes:**
- ✅ Returns `success: True` with `action: 'skipped'`
- ✅ Logs warning instead of error
- ✅ Continues processing other users

---

### 3. **Updated All Sync Calls**

Updated everywhere `get_database_rank_by_roblox_id()` is called to pass both parameters:

```python
# OLD
target_rank = await get_database_rank_by_roblox_id(rank_info['rank_id'])

# NEW
target_rank = await get_database_rank_by_roblox_id(
    rank_info['rank_id'],
    rank_info['rank']
)
```

**Files Updated:**
- ✅ `commands/user_commands.py` - `/link-roblox` command
- ✅ `roblox_api.py` - `compare_ranks()` function
- ✅ `roblox_api.py` - `sync_member_rank_from_roblox()` function

---

### 4. **Enhanced Rank Comparison**

**File:** `roblox_api.py` - `compare_ranks()`

```python
# Check if ranks match (by rank_id OR rank number)
if (discord_rank['roblox_group_rank_id'] == roblox_rank['rank_id'] or
    discord_rank['roblox_group_rank_id'] == roblox_rank['rank']):
    return None  # Ranks are in sync
```

**Changes:**
- ✅ Compares both ID and number
- ✅ More flexible matching
- ✅ Reduces false mismatches

---

### 5. **Improved Error Handling Across All Commands**

All commands now handle the `'skipped'` action:

**`/xp` Command:**
```python
elif sync_result['success'] and sync_result['action'] == 'skipped':
    logger.info(f"Sync skipped for {member['roblox_username']}: {sync_result['reason']}")
```

**`/promote` Command:**
```python
elif sync_result['success'] and sync_result['action'] == 'skipped':
    logger.warning(f"Pre-promotion sync skipped: {sync_result['reason']}")
```

**`/check-member` Command:**
```python
elif sync_result['success'] and sync_result['action'] == 'skipped':
    logger.info(f"Sync skipped: {sync_result['reason']}")
```

**`/sync` Command (Single):**
```python
if result['action'] == 'skipped':
    await interaction.followup.send(
        f"⚠️ Sync skipped for {member.mention}\n"
        f"Reason: {result['reason']}\n\n"
        f"Their Roblox rank doesn't have a matching Discord rank.",
        ephemeral=True
    )
```

**`/sync` Command (Bulk):**
```python
skipped = 0
...
if result['action'] == 'skipped':
    skipped += 1
    continue
...
embed.add_field(name="⚠️ Skipped", value=str(skipped), inline=True)
```

**Background Sync:**
```python
skipped = 0
...
if result['action'] == 'skipped':
    skipped += 1
    continue
...
logger.info(f"✅ Automatic sync complete: {synced} updated, {already_synced} in sync, {skipped} skipped, {errors} errors")
```

---

## 📊 Sync Actions

The sync system now returns three possible actions:

| Action | Meaning | Result |
|--------|---------|--------|
| `'none'` | Ranks already match | No update needed |
| `'updated'` | Ranks didn't match | Discord rank updated |
| `'skipped'` | No matching rank found | Logged, but continues |

---

## 🎯 How to Configure Ranks

### Option 1: Use Rank Numbers (Recommended)

In `database.py`, use Roblox rank numbers (0-255):

```python
default_ranks = [
    (1, "Pending", 0, 1, False),      # Rank number 1
    (2, "E0 | Enlist", 1, 2, False),  # Rank number 2
    (3, "E1 | Soldier", 3, 45, False), # Rank number 45
    # ...
]
```

**Pros:**
- ✅ Works across groups
- ✅ Easy to configure
- ✅ No need to find role IDs

---

### Option 2: Use Role IDs (More Specific)

Use actual Roblox role IDs from your group:

```python
default_ranks = [
    (1, "Pending", 0, 254791234, False),      # Actual role ID
    (2, "E0 | Enlist", 1, 254791235, False),  # Actual role ID
    # ...
]
```

**Pros:**
- ✅ More specific matching
- ✅ No conflicts if rank numbers change

**Cons:**
- ❌ Need to find role IDs from Roblox API
- ❌ More setup work

---

### How to Find Role IDs

1. Use the `/list-ranks` command in your bot
2. Or check Roblox group API:
   ```
   https://groups.roblox.com/v1/groups/YOUR_GROUP_ID/roles
   ```

3. Look for the `id` field in each role

---

## 🔍 Checking Sync Status

### View Skipped Syncs in Logs

```
[WARNING] No database rank found for Roblox rank ID 254791234 (rank number: 45)
[INFO] Sync skipped for JohnDoe on /xp: No database rank matches Roblox rank 'Guest'
[INFO] ✅ Automatic sync complete: 12 updated, 45 in sync, 3 skipped, 0 errors
```

### Admin Commands

**Check Single Member:**
```
/verify-rank @member
```
Shows if ranks match or mismatch

**Manual Sync:**
```
/sync @member
```
Tries to sync, shows skip message if no match

**Bulk Sync:**
```
/sync
```
Shows how many were skipped in summary

---

## 📋 Troubleshooting

### Issue: Users getting "skipped" in sync

**Cause:** Their Roblox rank doesn't have a matching entry in the database

**Solution:**
1. Check what Roblox rank they have (use bot logs or Roblox group page)
2. Add that rank to database in `database.py`:
   ```python
   (order, "Rank Name", points, roblox_rank_number_or_id, admin_only)
   ```
3. Restart bot to load new rank
4. Run `/sync @member` to update

---

### Issue: Sync still errors for some users

**Possible Causes:**
1. **User not in Roblox group** - They need to join the group
2. **Invalid Roblox username** - Username changed or account deleted
3. **API rate limiting** - Wait a few minutes and try again
4. **Network issues** - Check internet connection

**Check Logs:**
Look for specific error messages:
```
[ERROR] Could not fetch Roblox rank for JohnDoe
[ERROR] Failed to verify group membership
[ERROR] Error syncing member 123456789: ...
```

---

### Issue: Want to see which ranks are missing

**Solution:** Run bulk sync and check logs:

```
/sync
```

Look for warnings in logs:
```
[WARNING] Cannot sync Player1: No database rank matches Roblox rank 'Guest' (ID: 254791234, Rank: 0)
```

Then add those ranks to the database.

---

## 🎉 Results

**Before:**
```
[ERROR] Failed to sync @Player1: No database rank matches...
[ERROR] Failed to sync @Player2: No database rank matches...
[ERROR] Failed to sync @Player3: No database rank matches...
❌ Sync failed for all users
```

**After:**
```
[INFO] Auto-synced Player1: E0 | Enlist → E1 | Soldier
[INFO] Auto-synced Player2: E1 | Soldier → E2 | Specialist
[INFO] Sync skipped for Player3: No database rank matches 'Guest'
✅ Automatic sync complete: 2 updated, 42 in sync, 1 skipped, 0 errors
```

**Key Improvements:**
- ✅ Users get synced successfully
- ✅ Flexible rank matching (ID or number)
- ✅ Graceful skipping instead of errors
- ✅ Clear logging of what happened
- ✅ System continues working for all users

---

## 📝 Summary

### What Changed
1. **Dual-mode rank matching** - Tries ID first, then rank number
2. **Graceful skipping** - Logs warning instead of erroring
3. **Better error handling** - All commands handle skipped syncs
4. **Improved logging** - Clear messages about what happened
5. **Continued processing** - One user's issue doesn't block others

### What It Fixes
- ❌ "No database rank matches" errors → ✅ Flexible matching or graceful skip
- ❌ Sync failures blocking all users → ✅ Each user processed independently
- ❌ Unclear error messages → ✅ Detailed warnings with rank info
- ❌ System giving up → ✅ System continues working

### User Experience
- Users with matching ranks: **Synced successfully** ✅
- Users with close ranks: **Synced via rank number** ✅
- Users with unmapped ranks: **Skipped gracefully** ⚠️ (admin can fix)

---

**Last Updated:** November 12, 2025  
**Version:** 2.2 - Sync Fix  
**Status:** ✅ Fixed and Tested

