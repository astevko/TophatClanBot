# Role Permissions Guide

This guide explains how to configure and use role-based permissions for your Discord bot commands.

## Configuration

### Step 1: Edit Your .env File

Add or modify these lines in your `.env` file:

```bash
# Role Configuration (Names) - Fallback if IDs not provided
ADMIN_ROLE_NAME=Admin
MODERATOR_ROLE_NAME=Moderator
OFFICER_ROLE_NAME=Officer
ELITE_ROLE_NAME=Elite
MEMBER_ROLE_NAME=Member

# Role Configuration (IDs) - More reliable! (Recommended)
ADMIN_ROLE_ID=1234567890123456
MODERATOR_ROLE_ID=1234567890123457
OFFICER_ROLE_ID=1234567890123458
ELITE_ROLE_ID=1234567890123459
MEMBER_ROLE_ID=1234567890123460
```

**How to get Role IDs:**
1. Enable Developer Mode: Discord Settings → Advanced → Developer Mode ✅
2. Go to Server Settings → Roles
3. Right-click on a role → Copy ID
4. Paste the ID into your `.env` file

**Why use Role IDs?**
- ✅ Never change, even if role is renamed
- ✅ No case-sensitivity issues
- ✅ More reliable than names
- ✅ Recommended for production bots

### Step 2: Create Roles in Discord

1. Server Settings → Roles
2. Create roles with the exact names you specified in `.env`
3. Assign roles to your members

---

## Available Role Checks

### 1. `@is_admin()` - High Command Only
**Who can access:** Users with Admin role, Discord Administrators, or whitelisted User IDs

```python
@app_commands.command(name="promote", description="[HICOM] Promote a member")
@is_admin()
async def promote(self, interaction: discord.Interaction, member: discord.Member):
    # Only admins can use this
```

**Current commands using this:**
- `/promote`
- `/add-points`
- `/points-remove`
- `/check-member`
- `/list-ranks`
- `/set-admin-channel`
- `/view-pending`

---

### 2. `@is_moderator()` - Moderator or Higher
**Who can access:** Admins + Moderators

```python
@app_commands.command(name="warn", description="[MOD] Warn a member")
@is_moderator()
async def warn(self, interaction: discord.Interaction, member: discord.Member):
    # Mods and admins can use this
```

**Hierarchy:**
- ✅ Admin role
- ✅ Moderator role
- ❌ Everyone else

---

### 3. `@is_officer()` - Officer or Higher
**Who can access:** Admins + Moderators + Officers

```python
@app_commands.command(name="officer-task", description="[OFFICER] Officer task")
@is_officer()
async def officer_task(self, interaction: discord.Interaction):
    # Officers, mods, and admins can use this
```

**Hierarchy:**
- ✅ Admin role
- ✅ Moderator role
- ✅ Officer role
- ❌ Everyone else

---

### 4. `@has_role(role_name, role_id)` - Specific Role Only
**Who can access:** Only users with the exact role (by name or ID)

```python
# By role name
@app_commands.command(name="elite-bonus", description="[ELITE] Elite member bonus")
@has_role(role_name="Elite")
async def elite_bonus(self, interaction: discord.Interaction):
    # ONLY Elite members can use this (not even admins!)

# By role ID (more reliable)
@app_commands.command(name="vip-access", description="[VIP] VIP member access")
@has_role(role_id=1234567890)
async def vip_access(self, interaction: discord.Interaction):
    # ONLY users with this specific role ID
```

---

### 5. `@has_any_role(*role_names, role_ids)` - Any of Multiple Roles
**Who can access:** Users with ANY of the specified roles (by name or ID)

```python
# By role names
@app_commands.command(name="staff-meeting", description="[STAFF] Staff meeting command")
@has_any_role("Admin", "Moderator", "Officer")
async def staff_meeting(self, interaction: discord.Interaction):
    # Anyone with Admin, Mod, OR Officer role can use this

# By role IDs (more reliable)
@app_commands.command(name="team-access", description="[TEAM] Team access")
@has_any_role(role_ids=[1234567890, 1234567891, 1234567892])
async def team_access(self, interaction: discord.Interaction):
    # Anyone with any of these role IDs
```

---

### 6. `@has_all_roles(*role_names, role_ids)` - All Roles Required
**Who can access:** Users with ALL of the specified roles (by name or ID)

```python
# By role names
@app_commands.command(name="special-access", description="Requires multiple roles")
@has_all_roles("Verified", "Member", "Active")
async def special_access(self, interaction: discord.Interaction):
    # Must have Verified AND Member AND Active roles

# By role IDs
@app_commands.command(name="exclusive", description="Requires multiple role IDs")
@has_all_roles(role_ids=[1234567890, 1234567891])
async def exclusive(self, interaction: discord.Interaction):
    # Must have both of these roles
```

---

## Examples: Modifying Existing Commands

### Example 1: Make /points-remove Officer+ Only

```python
@app_commands.command(name="points-remove", description="[OFFICER] Remove points")
@is_officer()  # Changed from @is_admin()
async def points_remove(self, interaction: discord.Interaction, member: discord.Member, points: int):
    # Now Officers can also remove points
```

### Example 2: Make /view-pending Moderator+ Only

```python
@app_commands.command(name="view-pending", description="[MOD] View pending submissions")
@is_moderator()  # Changed from @is_admin()
async def view_pending(self, interaction: discord.Interaction):
    # Now Moderators can view pending submissions
```

### Example 3: Create Elite-Only Command

```python
@app_commands.command(name="elite-lounge", description="[ELITE] Access Elite lounge")
@has_role("Elite")  # Only Elite members
async def elite_lounge(self, interaction: discord.Interaction):
    await interaction.response.send_message("Welcome to the Elite lounge! 🌟", ephemeral=True)
```

---

## Permission Hierarchy

```
Discord Administrator
    ↓
Admin Role (from .env)
    ↓
Moderator Role (from .env)
    ↓
Officer Role (from .env)
    ↓
Elite Role (from .env)
    ↓
Member Role (from .env)
```

**Note:** 
- `@is_admin()` - Only top tier
- `@is_moderator()` - Admin + Moderator
- `@is_officer()` - Admin + Moderator + Officer
- `@has_role()` - Exact role only (no hierarchy)

---

## Using Config Values in Commands

You can reference role names and IDs from config:

```python
from config import Config

# Check by role ID (preferred)
if Config.ADMIN_ROLE_ID:
    admin_role = discord.utils.get(interaction.user.roles, id=Config.ADMIN_ROLE_ID)

# Check by role name (fallback)
admin_role = discord.utils.get(interaction.user.roles, name=Config.ADMIN_ROLE_NAME)

# Best practice: Check both
admin_role = None
if Config.ADMIN_ROLE_ID:
    admin_role = discord.utils.get(interaction.user.roles, id=Config.ADMIN_ROLE_ID)
if not admin_role:
    admin_role = discord.utils.get(interaction.user.roles, name=Config.ADMIN_ROLE_NAME)
```

---

## Testing Permissions

### Method 1: Test with Different Accounts
- Create test accounts
- Assign different roles
- Try commands to verify access

### Method 2: Check Logs
Commands log permission checks:
```bash
tail -f bot.log | grep "permission"
```

### Method 3: Error Messages
Users without permission will see:
```
❌ You don't have permission to use this command.
```

---

## Troubleshooting

### "Command not working for my role"
1. **Using Role IDs?** Double-check the ID is correct (right-click role → Copy ID)
2. **Using Role Names?** Check name matches `.env` exactly (case-sensitive)
3. Restart bot after changing `.env`
4. Make sure user has the role in Discord
5. Check bot logs for permission errors

### "Admin can't use Officer commands"
- Use `@is_officer()` instead of `@has_role("Officer")`
- The hierarchical checks include higher roles

### "Should I use Role IDs or Role Names?"
**Recommendation: Use Role IDs!**
- ✅ More reliable (never change)
- ✅ No typo issues
- ✅ No case-sensitivity problems
- ⚠️ Names: Only use for quick testing or if you can't get IDs

### "Want to combine role checks"
```python
# Custom check combining multiple conditions
from discord import app_commands

def custom_check():
    async def predicate(interaction: discord.Interaction) -> bool:
        # Must be admin OR have both Elite and Member roles
        if interaction.user.guild_permissions.administrator:
            return True
        
        has_elite = discord.utils.get(interaction.user.roles, name="Elite")
        has_member = discord.utils.get(interaction.user.roles, name="Member")
        
        return has_elite and has_member
    
    return app_commands.check(predicate)

@app_commands.command(name="custom", description="Custom permission check")
@custom_check()
async def custom_command(self, interaction: discord.Interaction):
    # Your code here
```

---

## Quick Reference Table

| Decorator | Admin | Mod | Officer | Elite | Member | None |
|-----------|-------|-----|---------|-------|--------|------|
| `@is_admin()` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `@is_moderator()` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| `@is_officer()` | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| `@has_role("Elite")` | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| `@has_any_role("Elite", "Member")` | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ |
| No decorator | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## Next Steps

1. **Configure your .env** with your role names
2. **Restart the bot** to load new config
3. **Test permissions** with different roles
4. **Customize commands** by changing decorators

For more help, check the main bot documentation or commands guide.

