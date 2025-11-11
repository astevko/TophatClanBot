# Security Configuration Guide

## Admin Access Control

The bot has **three levels** of admin permission checks. A user only needs to pass **ONE** of these to access admin commands:

### 1. Admin User ID Whitelist (Most Secure) ⭐ Recommended

Explicitly list Discord user IDs who can use admin commands.

**Setup:**

1. **Enable Developer Mode** in Discord:
   - Settings → Advanced → Developer Mode (toggle ON)

2. **Get Your Discord User ID:**
   - Right-click your username anywhere in Discord
   - Click "Copy User ID"
   - You'll get something like: `123456789012345678`

3. **Add to `.env` file:**
   ```bash
   # Single admin
   ADMIN_USER_IDS=123456789012345678
   
   # Multiple admins (comma-separated)
   ADMIN_USER_IDS=123456789012345678,987654321098765432,456789012345678901
   ```

**Pros:**
- ✅ Most secure - explicit whitelist
- ✅ Works even if user doesn't have Discord permissions
- ✅ Easy to add/remove specific people
- ✅ Survives role changes

**Use when:** You want absolute control over who is admin

---

### 2. Discord Administrator Permission

Uses Discord's built-in "Administrator" permission.

**Setup:**

1. In Discord Server Settings → Roles
2. Create or edit a role
3. Enable "Administrator" permission
4. Assign role to trusted users

**Pros:**
- ✅ Uses Discord's native permission system
- ✅ Familiar for Discord admins
- ✅ Syncs with other bot permissions

**Use when:** You want admins to have full Discord server control

---

### 3. Custom Admin Role Name

Check for a specific role by name.

**Setup:**

1. Create a role in Discord (e.g., "ClanAdmin", "BotManager")
2. Set the role name in `.env`:
   ```bash
   ADMIN_ROLE_NAME=ClanAdmin
   ```
3. Assign this role to users

**Pros:**
- ✅ Flexible - separate from server admin
- ✅ Can have "bot admins" without full server control
- ✅ Easy to visualize in Discord

**Use when:** You want bot-specific admins who aren't server administrators

---

## Recommended Setup

### For Small Clans (5-20 members):

```bash
# Use User ID whitelist
ADMIN_USER_IDS=123456789012345678,987654321098765432
ADMIN_ROLE_NAME=Admin
```

### For Large Clans (20+ members):

```bash
# Use role-based system
ADMIN_ROLE_NAME=ClanOfficer
# Keep whitelist for owner as backup
ADMIN_USER_IDS=123456789012345678
```

---

## Testing Admin Access

### As Admin:

Try running:
```
/promote @member
/add-points @member 5
/check-member @member
```

You should see: ✅ Command works

Check logs:
```bash
tail -f bot.log
```

You'll see:
```
✅ Admin access granted to YourName (ID: 123...) via ADMIN_USER_IDS whitelist
```

### As Non-Admin:

Commands won't appear in the slash command list, or you'll get:
```
❌ You don't have permission to use this command
```

Logs will show:
```
❌ Admin access DENIED to Username (ID: 456...) - attempted to use /promote
```

---

## Command-by-Command Access

### Admin-Only Commands:
- `/promote` - Promote members
- `/add-points` - Manually adjust points
- `/set-admin-channel` - Configure bot
- `/view-pending` - See pending submissions
- `/check-member` - View member details
- `/list-ranks` - View all ranks

### User Commands (Everyone):
- `/xp` - Check own progress
- `/leaderboard` - View rankings
- `/link-roblox` - Link account
- `/submit-raid` - Submit events

---

## Unauthorized Access Attempts

All failed admin access attempts are logged:

```
⚠️ Admin access DENIED to BadActor (ID: 999...) - attempted to use /promote
```

Monitor your logs regularly:
```bash
grep "DENIED" bot.log
```

---

## Security Best Practices

### ✅ DO:
- Use User ID whitelist for maximum security
- Keep your `.env` file private (never commit to git)
- Regularly review admin access logs
- Remove admins when they leave the clan
- Use different roles for different permission levels
- Have multiple admins to prevent self-promotion abuse

### ❌ DON'T:
- Share your Discord bot token
- Give everyone the admin role
- Use predictable role names like "admin" or "mod"
- Leave the `ADMIN_USER_IDS` empty in production
- Trust users just because they ask

### 🔒 Built-in Protections

The bot includes these security measures:

**Self-Action Prevention:**
- ❌ Admins cannot promote themselves
- ❌ Admins cannot add points to themselves
- ✅ All attempts are logged
- ✅ Must ask another admin for changes

**Audit Trail:**
- All admin actions logged with user ID
- Failed admin access attempts logged
- Self-promotion attempts logged

---

## Emergency: Compromised Admin Access

If an unauthorized user gains admin access:

1. **Immediately change in `.env`:**
   ```bash
   ADMIN_USER_IDS=your_id_only
   ADMIN_ROLE_NAME=NewSecureRoleName
   ```

2. **Restart the bot:**
   ```bash
   make run
   ```

3. **Check logs for damage:**
   ```bash
   grep "Admin access granted" bot.log | tail -20
   ```

4. **Review database:**
   - Check for unauthorized promotions
   - Look for point manipulation
   - Verify raid submissions

5. **Audit Discord:**
   - Remove compromised roles
   - Change role names
   - Review member permissions

---

## Getting Your Admin IDs

### Quick Script:

Run this in your server to get all admin IDs:

```bash
# In Discord, enable Developer Mode
# Right-click each admin → Copy User ID
# Or use this command (requires Discord.js bot with permissions):

/eval interaction.guild.members.cache
  .filter(m => m.permissions.has('Administrator'))
  .map(m => `${m.user.tag}: ${m.id}`)
  .join('\n')
```

Or create a temporary command to list them:

```python
@app_commands.command(name="show-my-id")
async def show_my_id(interaction: discord.Interaction):
    """Show your Discord user ID"""
    await interaction.response.send_message(
        f"Your Discord User ID: `{interaction.user.id}`\n"
        f"Copy this for ADMIN_USER_IDS configuration.",
        ephemeral=True
    )
```

---

## Questions?

- **Q: Can I use all three methods at once?**
  - A: Yes! A user who passes ANY check gets access.

- **Q: What if I lock myself out?**
  - A: Edit `.env` locally and add your ID to `ADMIN_USER_IDS`

- **Q: Do members see admin commands?**
  - A: No, Discord hides commands they can't use.

- **Q: How do I audit who used what command?**
  - A: Check `bot.log` - all access is logged with timestamps.

