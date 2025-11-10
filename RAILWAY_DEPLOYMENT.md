# Railway.app Deployment Guide

Complete guide to deploying your TophatC Clan Bot to Railway with PostgreSQL.

---

## Why PostgreSQL?

For cloud deployment, PostgreSQL is better than SQLite because:
- ✅ Persistent storage (SQLite files can be lost on restart)
- ✅ Better for concurrent access
- ✅ Automatic backups on Railway
- ✅ Scales better as your clan grows

**Good news:** The bot automatically detects and uses the right database!
- Local development → SQLite (easy, no setup)
- Railway/Cloud → PostgreSQL (production-ready)

---

## Step 1: Prepare Your Bot

### 1. Make sure your code is pushed to GitHub

```bash
cd /Users/andrewstevko/work/TophatClanBot

# Initialize git if you haven't
git init
git add .
git commit -m "Initial commit: TophatC Clan Bot"

# Create GitHub repo and push
git remote add origin https://github.com/yourusername/TophatClanBot.git
git branch -M main
git push -u origin main
```

---

## Step 2: Create Railway Project

### 1. Sign up for Railway

- Go to https://railway.app/
- Click "Start a New Project"
- Sign up with GitHub (recommended)

### 2. Create New Project

1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Connect your GitHub account
4. Select your `TophatClanBot` repository
5. Click "Deploy Now"

---

## Step 3: Add PostgreSQL Database

### 1. Add PostgreSQL to Your Project

1. In your Railway project dashboard
2. Click "New" → "Database" → "Add PostgreSQL"
3. Railway will automatically:
   - Create a PostgreSQL database
   - Set the `DATABASE_URL` environment variable
   - Connect it to your bot

### 2. Verify Database Connection

- Go to your PostgreSQL service
- Click "Connect" tab
- You'll see the `DATABASE_URL` is automatically available
- **The bot will automatically use this!**

---

## Step 4: Configure Environment Variables

### 1. Add Bot Configuration

In your Railway project:

1. Click on your bot service (not the database)
2. Go to "Variables" tab
3. Click "New Variable" and add:

```bash
# Discord Configuration
DISCORD_BOT_TOKEN=your_bot_token_here
GUILD_ID=your_discord_server_id

# Roblox Configuration
ROBLOX_GROUP_ID=your_roblox_group_id
ROBLOX_API_KEY=your_roblox_api_key

# Admin Configuration
ADMIN_USER_IDS=your_discord_user_id
ADMIN_ROLE_NAME=Admin

# Optional: Admin Channel (or set with /set-admin-channel later)
ADMIN_CHANNEL_ID=
```

**Important:** Don't add `DATABASE_URL` - Railway sets this automatically!

### 2. Save Variables

Click "Add" for each variable.

---

## Step 5: Configure Build Settings

Railway should auto-detect Python, but verify:

1. Go to "Settings" tab
2. Check "Build Command":
   ```bash
   pip install uv && uv pip install --system -e .
   ```

3. Check "Start Command":
   ```bash
   python bot.py
   ```

4. If not set, click "Edit" and add them

---

## Step 6: Deploy

### Automatic Deployment

Railway automatically deploys when you push to GitHub!

```bash
# Make any changes
git add .
git commit -m "Update bot"
git push

# Railway will automatically redeploy
```

### Manual Deployment

1. Go to "Deployments" tab
2. Click "Redeploy" on any deployment
3. Or click "Deploy" to trigger new deployment

---

## Step 7: Monitor Your Bot

### Check Logs

1. Go to your bot service
2. Click "Logs" tab
3. You should see:

```
INFO - Using PostgreSQL database (production)
INFO - Database initialized successfully
INFO - Bot setup complete
INFO - Logged in as YourBot
INFO - Bot is ready!
```

### Check Database

1. Click on PostgreSQL service
2. Go to "Data" tab (or use "Connect" to get connection string)
3. You can view tables: `members`, `rank_requirements`, `raid_submissions`, `config`

---

## Step 8: Verify Bot Works

### In Discord:

1. Bot should show as **Online** (green)
2. Type `/` - commands should appear
3. Test commands:
   ```
   /link-roblox YourUsername
   /xp
   /leaderboard
   ```

### As Admin:

```
/set-admin-channel #raid-approvals
/list-ranks
/check-member @someone
```

---

## Troubleshooting

### Bot doesn't start

**Check logs for errors:**
- `Configuration errors` → Missing environment variables
- `Improper token` → Wrong DISCORD_BOT_TOKEN
- `Database connection failed` → PostgreSQL issue

**Solutions:**
1. Verify all environment variables are set
2. Check DATABASE_URL exists (Railway sets this automatically)
3. Restart deployment

### Database connection errors

**Check:**
- PostgreSQL service is running
- DATABASE_URL variable exists
- Bot service can access PostgreSQL

**Fix:**
1. Go to PostgreSQL service
2. Make sure it's running
3. Railway should auto-link services

### Bot connects but commands don't work

**Check:**
- GUILD_ID is correct
- Bot has proper Discord permissions
- Intents are enabled in Discord Developer Portal

---

## Environment Variables Reference

### Required Variables

```bash
DISCORD_BOT_TOKEN=MTQyNDE2...          # From Discord Developer Portal
GUILD_ID=1234567890123456789           # Your Discord server ID
ROBLOX_GROUP_ID=12345678               # Your Roblox group ID
ROBLOX_API_KEY=your_api_key_here       # From Roblox Creator Hub
```

### Admin Configuration

```bash
ADMIN_USER_IDS=123,456,789             # Comma-separated Discord user IDs
ADMIN_ROLE_NAME=Admin                  # Role name for admins
```

### Optional

```bash
ADMIN_CHANNEL_ID=123456789             # Can set via /set-admin-channel
```

### Automatic (Set by Railway)

```bash
DATABASE_URL=postgres://user:pass@...  # Automatically set by Railway
PORT=8080                              # Set by Railway (if needed)
```

---

## Costs & Free Tier

### Railway Free Tier (2024)

- **$5 free credit per month**
- Enough for small-medium Discord bots
- Includes PostgreSQL database
- Automatic backups

### Typical Usage

- **Bot**: ~$3-4/month
- **PostgreSQL**: ~$1-2/month
- **Total**: Within free $5 credit for most clans

### If You Exceed Free Tier

- Add payment method
- Railway charges only for what you use
- Monitor usage in dashboard

---

## Updating Your Bot

### Method 1: Git Push (Recommended)

```bash
# Make changes to code
nano database.py

# Commit and push
git add .
git commit -m "Updated ranks"
git push

# Railway automatically redeploys
```

### Method 2: Manual Redeploy

1. Go to Railway dashboard
2. Click "Deployments"
3. Click "Redeploy" on latest deployment

---

## Database Management

### Backup Database

Railway automatically backs up your PostgreSQL database!

Manual backup:
```bash
# Get connection string from Railway
pg_dump $DATABASE_URL > backup.sql
```

### View Database

1. In Railway, click PostgreSQL service
2. Go to "Data" tab
3. Browse tables

Or use a SQL client:
```bash
# Get DATABASE_URL from Railway
psql $DATABASE_URL
```

### Reset Database

⚠️ **This deletes all data!**

```sql
-- Connect to database
psql $DATABASE_URL

-- Drop all tables
DROP TABLE IF EXISTS members, raid_submissions, rank_requirements, config;

-- Restart bot to recreate tables
```

---

## Monitoring & Alerts

### Check Bot Health

1. Dashboard → Your bot service
2. Check:
   - CPU usage
   - Memory usage
   - Logs for errors

### Set Up Alerts

1. Go to "Settings"
2. Add "Webhooks" for Discord notifications
3. Get notified when bot goes down

---

## Security Best Practices

### ✅ DO:

- Keep environment variables in Railway only
- Never commit `.env` to git
- Use `ADMIN_USER_IDS` whitelist
- Regularly check logs for unauthorized access
- Enable 2FA on Railway account

### ❌ DON'T:

- Share your Discord bot token
- Commit secrets to GitHub
- Use weak admin passwords
- Leave database publicly accessible

---

## Alternative: Use SQLite on Railway

If you really want to use SQLite on Railway:

1. Add volume mount in Railway settings
2. Set DATABASE_URL to empty:
   ```bash
   # Don't set DATABASE_URL - bot will use SQLite
   ```

**⚠️ Warning:** SQLite files can be lost on restart. Use PostgreSQL for production!

---

## Switching from SQLite to PostgreSQL

If you have local SQLite data you want to migrate:

### Export SQLite Data

```bash
# Dump SQLite to SQL
sqlite3 tophat_clan.db .dump > export.sql
```

### Import to PostgreSQL

```bash
# Get DATABASE_URL from Railway
# Clean up syntax (SQLite vs PostgreSQL differences)
# Then import
psql $DATABASE_URL < export_cleaned.sql
```

Or use a migration tool:
- pgloader
- railway-sqlite-to-postgres scripts

---

## Getting Help

### Check Logs First

```
Railway Dashboard → Bot Service → Logs
```

### Common Issues

1. **"Configuration errors"**
   - Missing environment variables
   - Check Variables tab

2. **"Database connection failed"**
   - PostgreSQL not running
   - DATABASE_URL not set (should be automatic)

3. **"Bot not responding"**
   - Check bot is running in Logs
   - Verify Discord token
   - Check GUILD_ID

### Railway Support

- Discord: https://discord.gg/railway
- Docs: https://docs.railway.app/
- Status: https://status.railway.app/

---

## Next Steps

✅ Bot deployed to Railway
✅ PostgreSQL database connected
✅ Environment variables configured

**Now:**

1. Test all commands in Discord
2. Invite members to use `/link-roblox`
3. Start approving raids
4. Monitor logs for any issues
5. Set up webhooks for alerts (optional)

**Enjoy your 24/7 clan bot! 🎉**

