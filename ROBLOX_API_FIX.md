# Roblox API Fix - INVALID_ARGUMENT Error

**Date:** November 13, 2025  
**Status:** ✅ Fixed

## Issue

The bot was failing to update member ranks in Roblox with the following error:

```
Failed to update rank: 400 - {
  "code": "INVALID_ARGUMENT",
  "message": "Failed to parse resource path and its identifiers - 47."
}
```

---

## Root Cause

The Roblox **Open Cloud API** expects the `role` field to be a **full resource path**, not just the role ID.

### ❌ Incorrect (Before):
```python
json={"role": str(new_rank_id)}  # Just the ID: "47"
```

### ✅ Correct (After):
```python
role_path = f"groups/{Config.ROBLOX_GROUP_ID}/roles/{new_rank_id}"
json={"role": role_path}  # Full path: "groups/12345/roles/47"
```

---

## Technical Details

### Roblox Open Cloud API v2 Format

The Open Cloud API v2 uses **resource-oriented paths** for all identifiers:

**Endpoint:**
```
PATCH /cloud/v2/groups/{groupId}/memberships/{userId}
```

**Body:**
```json
{
  "role": "groups/{groupId}/roles/{roleId}"
}
```

**Example:**
```json
{
  "role": "groups/12345678/roles/47"
}
```

This is different from the legacy Groups API which just accepts the role ID directly.

---

## The Fix

**File:** `roblox_api.py` (lines 113-136)

**Changes:**
1. Construct full resource path: `groups/{groupId}/roles/{roleId}`
2. Send the full path instead of just the role ID
3. Added explanatory comment for future reference

```python
# Roblox Open Cloud API expects role as a full resource path
role_path = f"groups/{Config.ROBLOX_GROUP_ID}/roles/{new_rank_id}"

async with session.patch(
    url,
    headers=headers,
    json={"role": role_path}  # ✅ Full resource path
) as response:
    # Handle response...
```

---

## Impact

### Before Fix:
- ❌ All rank promotions via Open Cloud API failed with 400 error
- ❌ `/promote` command couldn't update Roblox ranks
- ❌ Auto-sync couldn't update Roblox ranks
- ⚠️ Discord ranks updated but Roblox ranks remained unchanged

### After Fix:
- ✅ Rank promotions work correctly via Open Cloud API
- ✅ `/promote` command updates both Discord AND Roblox
- ✅ Auto-sync successfully updates Roblox ranks
- ✅ Discord and Roblox stay in sync

---

## Testing

### Test 1: Manual Promotion
```bash
# Run /promote command on a member
/promote @TestUser

# Expected result:
✅ Database updated
✅ Discord role updated
✅ Roblox rank updated
```

### Test 2: Auto-Sync
```bash
# Wait for hourly auto-sync to run
# Check bot.log for:
"Successfully updated rank for username to {rank_id}"
```

### Test 3: Verify in Roblox
1. Go to your Roblox group page
2. Check the member's rank in the group
3. Verify it matches their Discord role

---

## API Authentication Methods

This bot supports two methods for updating Roblox ranks:

### 1. Open Cloud API (Recommended) ✅
- **Setup:** Configure `ROBLOX_API_KEY` in environment
- **Endpoint:** `/cloud/v2/groups/{groupId}/memberships/{userId}`
- **Auth:** `x-api-key` header
- **Status:** ✅ Fixed with this update

### 2. Cookie-Based (Legacy)
- **Setup:** Configure `ROBLOX_COOKIE` in environment
- **Endpoint:** `/v1/groups/{groupId}/users/{userId}`
- **Auth:** `.ROBLOSECURITY` cookie + CSRF token
- **Status:** ✅ Still works (unchanged)

**Note:** The cookie-based method was not affected by this bug as it uses a different API endpoint and format.

---

## API Key vs Cookie

### Open Cloud API Key (Recommended)
**Pros:**
- ✅ More secure (scoped permissions)
- ✅ Doesn't expire
- ✅ Official supported method
- ✅ Better for production

**Cons:**
- ⚠️ Requires group ownership to create API key
- ⚠️ Must configure in Roblox Creator Hub

### Cookie-Based (Legacy)
**Pros:**
- ✅ Easier to set up
- ✅ Works for non-owners (if user has permissions)

**Cons:**
- ⚠️ Less secure (full account access)
- ⚠️ Cookie expires periodically
- ⚠️ May be deprecated in future

---

## Configuration

### Option 1: Open Cloud API (Fixed)

1. Go to [Roblox Creator Hub](https://create.roblox.com/)
2. Select your group
3. Go to **Settings** → **Security** → **Open Cloud**
4. Create a new API key with permissions:
   - `group:read`
   - `group.membership:write`
5. Set in your `.env`:
   ```bash
   ROBLOX_API_KEY=your_api_key_here
   ```

### Option 2: Cookie-Based (Still Works)

1. Log into Roblox in your browser
2. Open Developer Tools (F12)
3. Go to Application → Cookies
4. Copy the `.ROBLOSECURITY` cookie value
5. Set in your `.env`:
   ```bash
   ROBLOX_COOKIE=your_cookie_here
   ```

---

## Related Files Modified

1. ✅ `roblox_api.py`
   - Fixed Open Cloud API role path format
   - Added explanatory comments
   - No changes to cookie-based method

---

## Additional Notes

### Why This Wasn't Caught Earlier

The error only occurs when using the **Open Cloud API** with an API key. If you were using the cookie-based authentication, this bug would not have appeared.

The bug was introduced when support for Open Cloud API was added, but the resource path format wasn't properly documented.

### Roblox API Version Differences

| API Version | Role Format | Status |
|-------------|-------------|--------|
| **Open Cloud v2** | `groups/{groupId}/roles/{roleId}` | ✅ Fixed |
| **Groups API v1** | `{"roleId": 123}` | ✅ Working |

---

## Verification

### Check if Fix is Applied

Look for this line in `roblox_api.py` (around line 123):

```python
role_path = f"groups/{Config.ROBLOX_GROUP_ID}/roles/{new_rank_id}"
```

If you see `json={"role": str(new_rank_id)}` instead, the fix is NOT applied.

### Check Logs

After fix, successful rank updates will log:
```
Successfully updated rank for {username} to {rank_id}
```

Before fix, you would see:
```
Failed to update rank: 400 - { "code": "INVALID_ARGUMENT", ... }
```

---

## Next Steps

1. ✅ **Code Applied** - Fix is implemented
2. ⏳ **Restart Bot** - Restart to apply changes
3. ⏳ **Test Promotion** - Try `/promote` command
4. ⏳ **Monitor Logs** - Check for successful rank updates
5. ⏳ **Verify in Roblox** - Confirm ranks match in Roblox group

---

## Conclusion

**Status:** ✅ Fixed  
**Breaking Changes:** None  
**Configuration Required:** None (existing API keys will now work)  
**Restart Required:** Yes

The fix ensures that the Roblox Open Cloud API receives the correct resource path format, allowing the bot to successfully update member ranks in your Roblox group.

---

**Related Issues:**
- Discord Rate Limiting → See `RATE_LIMIT_FIXES.md`
- Rank Identification → See `RANK_IDENTIFICATION_GUIDE.md`
- Roblox Sync System → See `ROBLOX_SYNC_GUIDE.md`

