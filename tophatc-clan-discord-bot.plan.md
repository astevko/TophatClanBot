<!-- 733759b5-1867-44dc-86f7-086476bb9f37 9addd247-46d3-4d53-a893-64e16c24c097 -->
# TophatC Clan Discord Bot Implementation Plan

## Overview

Build a Discord bot in Python using discord.py that tracks clan member ranks, activity points, and integrates with Roblox API to automatically sync ranks between Discord and Roblox group.

## Core Components

### 1. Bot Setup & Configuration

- Create Python Discord bot using discord.py library
- Set up SQLite database with tables:
  - `members` (discord_id, roblox_username, current_rank, points, created_at)
  - `raid_submissions` (submission_id, submitter_id, participants, start_time, end_time, image_url, status, points_awarded, admin_id, timestamp)
  - `rank_requirements` (rank_name, points_required, roblox_group_rank_id)
- Configuration file for Discord bot token, Roblox API credentials, admin channel ID, rank definitions

### 2. Rank System

Military hierarchy with point thresholds:

- Define ranks (Private, Corporal, Sergeant, etc.) with point requirements (e.g., Private 0-30, Corporal 31-60)
- Discord roles automatically assigned based on current rank
- Points accumulate toward next rank promotion

### 3. Raid Submission System

**User Flow** (`/submit-raid`):

- User runs `/submit-raid` command with image attachment
- Modal form prompts for:
  - Participant mentions (@user1 @user2 @user3)
  - Raid start date/time
  - Raid end date/time
- Bot posts formatted embed to admin channel with all details + proof image
- Embed includes two buttons: [Approve] [Decline]

**Admin Approval Flow**:

- Admin clicks [Approve] → Modal asks for points (1-8)
- Bot awards points to all participants
- Updates database and notifies participants
- Admin clicks [Decline] → Submission rejected, submitter notified

### 4. User Commands

- `/xp` - View current rank and progress (e.g., "Private 10/30")
- `/leaderboard` - Show top members by points
- `/link-roblox <username>` - Link Discord account to Roblox username

### 5. Admin Commands

- `/promote @user` - Manually promote user after approval (updates Discord role + Roblox group rank)
- `/add-points @user <amount>` - Manually adjust points
- `/set-admin-channel` - Configure where raid submissions appear
- `/view-pending` - See all pending raid submissions

### 6. Roblox Integration

- Use Roblox Open Cloud API or Group API
- Authenticate with API key or cookie
- Functions:
  - Verify user is in Roblox group
  - Read current Roblox group rank
  - Update Roblox group rank when promoted (requires group permissions)
- Sync happens when admin approves promotion

### 7. Deployment Setup

- Create `requirements.txt` with dependencies (discord.py, aiohttp, etc.)
- Create `.env.example` for configuration template
- Setup instructions for Railway.app or Render.com free hosting
- Include README with:
  - Installation steps
  - Discord bot creation & token setup
  - Roblox API setup
  - Deployment guide

## File Structure

```
TophatClanBot/
├── bot.py                 # Main bot entry point
├── database.py            # SQLite database functions
├── roblox_api.py          # Roblox API integration
├── commands/
│   ├── user_commands.py   # /xp, /submit-raid, /link-roblox
│   └── admin_commands.py  # /promote, /add-points, admin tools
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
└── README.md             # Setup and deployment guide
```

## Key Technical Details

**Discord Components**:

- Slash commands (app_commands)
- Modal forms for user input
- Button interactions for admin approval
- Embeds for rich raid submission display
- Role management for rank assignment

**Database Schema**:

- Track points and rank per Discord user ID
- Store raid submissions with participant lists
- Historical record of approvals and point awards

**Roblox API Integration**:

- OAuth2 or API key authentication
- Group rank update endpoint
- Error handling for API rate limits

**Security**:

- Admin-only commands restricted by Discord role/permissions
- Environment variables for sensitive tokens
- Input validation on point values (1-8) and user mentions

### To-dos

- [ ] Initialize project structure with directories, requirements.txt, .env.example, and README.md
- [ ] Create database.py with SQLite schema (members, raid_submissions, rank_requirements) and CRUD functions
- [ ] Build bot.py with Discord client setup, event handlers, and configuration loading
- [ ] Implement /submit-raid command with modal form, admin channel posting, and button interactions
- [ ] Build approval/decline button handlers with points modal and participant point awarding logic
- [ ] Create /xp, /leaderboard, and /link-roblox commands in user_commands.py
- [ ] Implement /promote, /add-points, /set-admin-channel in admin_commands.py
- [ ] Build roblox_api.py with group rank verification and update functions using Roblox API
- [ ] Implement rank progression logic with Discord role assignment and promotion approval workflow
- [ ] Write comprehensive README with setup instructions for Discord bot, Roblox API, and Railway/Render deployment