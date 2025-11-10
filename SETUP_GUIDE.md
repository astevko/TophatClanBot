# TophatC Clan Bot - Setup Guide

## Step 1: Create/Configure Discord Bot

### Get Your Bot Token

1. Go to https://discord.com/developers/applications
2. Click your application (or create new one: "New Application")
3. Go to "Bot" section in left sidebar
4. Click "Reset Token" (or "Copy" if this is a new bot)
5. **IMPORTANT**: Copy the token immediately - you can only see it once!

### Enable Required Intents

In the same Bot section:
1. Scroll down to "Privileged Gateway Intents"
2. Enable:
   - ✅ Server Members Intent
   - ✅ Message Content Intent
3. Click "Save Changes"

### Get Bot Invite URL

1. Go to "OAuth2" → "URL Generator" in left sidebar
2. Select scopes:
   - ✅ bot
   - ✅ applications.commands
3. Select bot permissions:
   - ✅ Manage Roles
   - ✅ Send Messages
   - ✅ Embed Links
   - ✅ Attach Files
   - ✅ Read Message History
   - ✅ Use Slash Commands
4. Copy the generated URL at the bottom
5. Open it in browser to invite bot to your server

---

## Step 2: Get Your Discord Server (Guild) ID

1. Open Discord
2. Go to Settings → Advanced → Enable "Developer Mode"
3. Right-click your server icon → "Copy Server ID"
4. Save this ID

---

## Step 3: Get Roblox Group Information

### Find Your Group ID

1. Go to your Roblox group page
2. Look at the URL: `https://www.roblox.com/groups/[GROUP_ID]/...`
3. The number is your GROUP_ID

### Get Roblox API Key (Recommended Method)

1. Go to https://create.roblox.com/dashboard/credentials
2. Click "Create API Key"
3. Name it: "TophatC Clan Bot"
4. Add permissions:
   - ✅ `group.membership:write`
   - ✅ `group.membership:read`
5. Select your group
6. Click "Create"
7. **IMPORTANT**: Copy the API key immediately!

### Get Group Rank IDs

1. Go to your group page on Roblox
2. Click "Configure Group" (you must be group owner/admin)
3. Go to "Roles" section
4. Note the rank numbers for each role (1, 2, 3, etc.)
5. These will map to the ranks in the bot

**Default Mapping:**
- Private = Rank 1
- Corporal = Rank 2
- Sergeant = Rank 3
- Staff Sergeant = Rank 4
- Lieutenant = Rank 5
- Captain = Rank 6
- Major = Rank 7
- Colonel = Rank 8
- General = Rank 9

You can customize these in `database.py` later.

---

## Step 4: Configure Your .env File

```bash
cd /Users/andrewstevko/work/TophatClanBot

# Edit the .env file
nano .env
```

Fill in ALL values:

```bash
# Discord Bot Configuration
DISCORD_BOT_TOKEN=MTQyNDE2MDQxNDI1NzkwNTczOA.GFFAsm.iToqz3kLF5zj3nYX0ugJFdsRAvMpHUfMFn7IkQ
GUILD_ID=1234567890123456789

# Admin Channel Configuration
# You can set this later with /set-admin-channel command
ADMIN_CHANNEL_ID=

# Roblox Configuration
ROBLOX_GROUP_ID=12345678
ROBLOX_API_KEY=your_api_key_here

# Admin Role Configuration
ADMIN_ROLE_NAME=Admin
```

**Press:**
- `Ctrl+X` to exit
- `Y` to save
- `Enter` to confirm

---

## Step 5: Run the Bot

```bash
# Make sure you're in the project directory
cd /Users/andrewstevko/work/TophatClanBot

# Run the bot
make run

# Or use the shell script
./run.sh

# Or manually
uv run bot.py
```

---

## Step 6: Verify Bot is Working

When the bot starts successfully, you should see:

```
2024-11-10 - INFO - Setting up bot...
2024-11-10 - INFO - Database initialized successfully
2024-11-10 - INFO - Synced commands to guild 1234567890
2024-11-10 - INFO - Bot setup complete
2024-11-10 - INFO - Logged in as YourBotName (ID: 1234567890)
2024-11-10 - INFO - Connected to 1 guild(s)
2024-11-10 - INFO - Bot is ready!
```

In Discord, your bot should show as **Online** (green dot).

---

## Step 7: Initial Setup Commands

### In Discord (as Admin):

1. **Set Admin Channel** (where raid submissions will appear):
   ```
   /set-admin-channel #raid-approvals
   ```

2. **Create an Admin Channel** (if you don't have one):
   - Right-click server → Create Channel
   - Name it: `raid-approvals`
   - Make it private to admins only

3. **Test User Commands**:
   ```
   /link-roblox YourRobloxUsername
   /xp
   /leaderboard
   ```

---

## Step 8: First Raid Submission Test

### As a Regular Member:

1. Take a screenshot/image
2. Run command: `/submit-raid` and attach the image
3. Fill in the modal:
   - Participants: `@user1 @user2`
   - Start time: `2024-11-10 14:00`
   - End time: `2024-11-10 16:00`
4. Submit

### As Admin:

1. Check the raid-approvals channel
2. You should see the submission with [Approve] [Decline] buttons
3. Click [Approve]
4. Enter points: `5`
5. All participants should receive 5 points

### Verify:

Members can check progress with `/xp`

---

## Troubleshooting

### Bot doesn't connect
- ✅ Check token is correct in `.env`
- ✅ Check bot is invited to server
- ✅ Check intents are enabled

### Commands don't show up
- ✅ Wait 1-5 minutes for Discord to sync
- ✅ Verify GUILD_ID is correct
- ✅ Try typing `/` to see commands

### Roblox sync fails
- ✅ Check API key has correct permissions
- ✅ Verify group ID is correct
- ✅ Ensure bot account has group admin access

### "Permission Denied" errors
- ✅ Ensure bot role is above rank roles
- ✅ Give bot "Manage Roles" permission
- ✅ Bot needs admin access to create roles

---

## What's Next?

Once the bot is running:

1. **Invite members** to use `/link-roblox`
2. **Start submitting raids** for approval
3. **Award points** and promote members
4. **Deploy to cloud** (Railway/Render) for 24/7 uptime
5. **Customize ranks** in `database.py` if needed

---

## Need Help?

Check the logs:
```bash
tail -f bot.log
```

Common issues are in the main README.md troubleshooting section.

