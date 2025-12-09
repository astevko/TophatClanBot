# Slash Commands Guide

Complete reference for all TophatC Clan Bot slash commands.

---

## Table of Contents

- [User Commands](#user-commands) - Available to all members
- [Admin Commands](#admin-commands) - Admin-only commands
- [Command Tips](#command-tips)
- [Troubleshooting](#troubleshooting)

---

## User Commands

Commands available to all clan members.

### `/xp`

**Check your current rank and points progress**

**Usage:**
```
/xp
```

**What it shows:**
- Current rank (with ⚡ if admin-granted or 📊 if point-based)
- Total points earned
- Rank type
- Next point-based rank
- Progress bar toward next rank
- Points needed for next rank

**Example Output:**
```
📊 YourName's Progress

Current Rank: Sergeant 📊
Total Points: 75
Rank Type: Point-Based

Next Point-Based Rank: Staff Sergeant
Progress to Next Rank: [███████░░░] 75/100 (25 points needed)

Roblox: YourRobloxName
```

**With Admin-Only Rank:**
```
📊 YourName's Progress

Current Rank: Commander ⚡
Total Points: 150
Rank Type: Admin-Granted

Next Point-Based Rank: Lieutenant
Progress to Next Rank: [██████████] 150/150 (0 points needed)

ℹ️ Note: You have an admin-granted rank. Points still count toward point-based ranks!

Roblox: YourRobloxName
```

**Tips:**
- Check this regularly to track your progress
- Points accumulate even if you have an admin-granted rank
- Use this to see how close you are to promotion

---

### `/leaderboard`

**View the top clan members by points**

**Usage:**
```
/leaderboard
```

**What it shows:**
- Top 10 members by total points
- Their current rank
- Point totals
- Rankings with medals (🥇🥈🥉)

**Example Output:**
```
🏆 TophatC Clan Leaderboard
Top 10 members by activity points

🥇 @Player1 - General (520 pts)
🥈 @Player2 - Colonel (380 pts)
🥉 @Player3 - Major (290 pts)
4. @Player4 - Captain (220 pts)
5. @Player5 - Lieutenant (165 pts)
...

Keep raiding to climb the ranks!
```

**Tips:**
- See how you compare to other members
- Motivates competition and activity
- Resets are never done - points are permanent

---

### `/link-roblox <username>`

**Link your Discord account to your Roblox username**

**Usage:**
```
/link-roblox RobloxUsername
```

**Parameters:**
- `username` - Your Roblox username (case-sensitive)

**What it does:**
- Registers you in the bot's database
- Assigns you "Private" rank
- Creates your Discord role
- Allows you to earn points

**Example:**
```
/link-roblox JohnDoe123
```

**Output:**
```
✅ Successfully linked your account to JohnDoe123!
You've been assigned the Private rank. Use /xp to check your progress.
```

**Important:**
- You can only link ONE Roblox account
- To change, use the command again with new username
- Must link before submitting raids or earning points

**Tips:**
- Use your EXACT Roblox username
- Do this first thing after joining the server
- Admin can verify your Roblox account is in the group

---

### `/submit-raid <proof_image>`

**Submit a raid event for admin approval**

**Usage:**
```
/submit-raid
[Attach image as proof]
```

**Parameters:**
- `proof_image` - Screenshot/image showing the raid (required)

**What happens:**
1. You attach an image of the raid
2. Bot opens a form asking for:
   - **Participants**: @mention everyone who participated
   - **Start Time**: When the raid started (e.g., "2:30 PM" or "2024-11-10 14:30")
   - **End Time**: When the raid ended
3. Bot posts to admin channel for review
4. Admin approves/declines and awards points

**Example:**
```
/submit-raid [attach screenshot]

Form appears:
Participants: @User1 @User2 @User3 @User4
Start Time: 2024-11-10 14:00
End Time: 2024-11-10 16:30

Submit → Sent to admin channel
```

**Tips:**
- Take group selfie as proof
- Include ALL participants in the mentions
- Be accurate with times
- Wait for admin approval before submitting another

**What NOT to do:**
- Don't submit fake/old screenshots
- Don't mention non-participants
- Don't spam multiple submissions

---

## Admin Commands

Commands restricted to administrators and users with admin permissions.

### `/promote @user`

**Promote a member to the next rank**

**Usage:**
```
/promote @member
```

**Parameters:**
- `member` - The Discord user to promote

**What it does:**
- Gets member's current rank
- Finds next rank (includes admin-only ranks)
- Checks points requirement (for point-based ranks only)
- Updates rank in database
- Updates Discord role
- Syncs to Roblox group
- Notifies member

**Point-Based Rank Example:**
```
/promote @JohnDoe

Checking: JohnDoe has 75 points, needs 100 for Staff Sergeant
❌ @JohnDoe needs 25 more points to be promoted to Staff Sergeant.
Current: 75/100 points
```

After earning more points:
```
/promote @JohnDoe

✅ Promotion Successful
@JohnDoe has been promoted!

Previous Rank: Sergeant
New Rank: Staff Sergeant
Total Points: 105
Rank Type: 📊 Point-Based Rank
Roblox Sync: ✅ Roblox rank updated
```

**Admin-Only Rank Example:**
```
/promote @JohnDoe

✅ Promotion Successful
@JohnDoe has been promoted!

Previous Rank: Sergeant
New Rank: Commander
Total Points: 75
Rank Type: ⚡ Admin-Only Rank (Manual Promotion)
Roblox Sync: ✅ Roblox rank updated
```

**Tips:**
- Check `/check-member` first to verify eligibility
- Admin-only ranks skip point requirements
- Member receives DM notification
- Roblox rank syncs automatically (if API configured)

**Security:**
- ❌ You cannot promote yourself
- ✅ Ask another admin to promote you
- 🔒 All self-promotion attempts are logged

---

### `/add-points @user <amount>`

**Manually add or remove points from a member**

**Usage:**
```
/add-points @member 10
/add-points @member -5
```

**Parameters:**
- `member` - The Discord user
- `amount` - Points to add (positive) or remove (negative)

**What it does:**
- Adjusts member's point total
- Validates member exists
- Prevents negative totals
- Notifies member

**Example:**
```
/add-points @JohnDoe 10

✅ Points Updated
10 points added to @JohnDoe

Previous Points: 50
Change: +10
New Points: 60
```

**Removing Points:**
```
/add-points @JohnDoe -5

✅ Points Updated
5 points removed from @JohnDoe

Previous Points: 60
Change: -5
New Points: 55
```

**Use Cases:**
- Bonus points for special achievements
- Correction if wrong amount was awarded
- Penalty for rule violations
- Manual adjustment needed

**Tips:**
- Use sparingly - most points come from raids
- Always document why you adjusted points
- Member receives notification

**Security:**
- ❌ You cannot add points to yourself
- ✅ Ask another admin to adjust your points
- 🔒 All self-point attempts are logged

---

### `/set-admin-channel <channel>`

**Configure the channel where raid submissions appear**

**Usage:**
```
/set-admin-channel #raid-approvals
```

**Parameters:**
- `channel` - The text channel for submissions

**What it does:**
- Sets designated channel for all raid submissions
- Saves to database
- All future `/submit-raid` go there

**Example:**
```
/set-admin-channel #raid-approvals

✅ Admin channel set to #raid-approvals. 
All raid submissions will be posted there.
```

**Tips:**
- Create a private admin-only channel
- Name it clearly (e.g., #raid-approvals, #event-review)
- Only admins should see this channel
- Set once and forget

---

### `/view-pending`

**See all pending raid submissions**

**Usage:**
```
/view-pending
```

**What it shows:**
- List of all pending (unapproved) submissions
- Submission ID
- Submitter
- Participants
- Raid times

**Example Output:**
```
📋 Pending Raid Submissions
There are 3 pending submission(s)

Submission #42
Submitter: @Player1
Start: 2024-11-10 14:00
End: 2024-11-10 16:00
Participants: @Player1 @Player2 @Player3...

Submission #43
Submitter: @Player2
...

Showing 3 of 3 submissions
```

**Tips:**
- Check this regularly so members don't wait long
- Each submission should be in the admin channel
- Process in order (FIFO - first in, first out)

---

### `/check-member @user`

**View detailed stats and promotion eligibility for a member**

**Usage:**
```
/check-member @member
```

**Parameters:**
- `member` - The Discord user to check

**What it shows:**
- Discord tag and Roblox username
- Current rank and rank type
- Total points earned
- Next point-based rank
- Promotion eligibility
- Points needed (if any)

**Example Output (Point-Based Rank):**
```
📊 Member Stats: @JohnDoe

Discord: @JohnDoe
Roblox: JohnDoe123
Member Since: 2024-11-01

Current Rank: Sergeant
Total Points: 75
Rank Type: 📊 Point-Based

Next Point-Based Rank: Staff Sergeant
Auto-Promotion Status: ❌ Needs 25 more points
(75/100 points)
```

**Example Output (Admin-Only Rank):**
```
📊 Member Stats: @JohnDoe

Discord: @JohnDoe
Roblox: JohnDoe123
Member Since: 2024-11-01

Current Rank: Commander
Total Points: 150
Rank Type: ⚡ Admin-Only

Next Point-Based Rank: Captain
Auto-Promotion Status: ✅ Eligible for Promotion
(150/210 points)

ℹ️ Note: This member has an admin-granted rank. 
Use /promote to change ranks manually.
```

**Tips:**
- Use before promoting to verify eligibility
- See if someone is close to ranking up
- Track member progress over time

---

### `/list-ranks`

**View all rank requirements and categories**

**Usage:**
```
/list-ranks
```

**What it shows:**
- All point-based ranks with requirements
- All admin-only ranks by category
- Complete rank structure

**Example Output:**
```
🎖️ Clan Rank System
Complete overview of all ranks

📊 Point-Based Ranks (Earn through raids)
1. Private - 0 pts
2. Corporal - 30 pts
3. Sergeant - 60 pts
4. Staff Sergeant - 100 pts
5. Lieutenant - 150 pts
6. Captain - 210 pts
7. Major - 280 pts
8. Colonel - 360 pts
9. General - 450 pts

⚡ Leadership Ranks (Admin-granted)
10. Officer Cadet
11. Junior Officer
12. Senior Officer
13. Commander
14. High Commander

🏆 Honorary Ranks (Admin-granted)
15. Veteran
16. Elite Guard
17. Legend
18. Hall of Fame

🔰 Trial/Probation (Admin-granted)
19. Recruit
20. Probation

Use /promote to assign any rank manually | /check-member to see eligibility
```

**Tips:**
- Reference this when explaining rank system to members
- Shows complete progression path
- Helps plan point requirements

---

### `/set-discord-log-level`

**Control which log levels are sent to Discord logging channel**

**Usage:**
```
/set-discord-log-level level: [choice]
```

**Parameters:**
- `level` - Choose from:
  - **Critical Only** - Only CRITICAL logs (most severe issues)
  - **Error and Critical** - ERROR and CRITICAL logs only
  - **Warning, Error, and Critical** - All warnings and errors (default)
  - **None (Disable)** - Disable Discord logging completely

**What it does:**
- Changes which log messages are sent to Discord logging channel
- Takes effect immediately (no restart needed)
- All logs still saved to `bot.log` file regardless of setting

**Example Output:**
```
✅ Discord Log Level Updated

Discord logging channel will now show: ERROR and CRITICAL logs only

Previous Level: WARNING
New Level: ERROR

ℹ️ Note
This change is immediate. All logs still go to bot.log file.
```

**Use Cases:**
- **Error and Critical** - Reduce noise, only show actual errors
- **Critical Only** - Production monitoring, only critical issues
- **None** - Temporarily disable during bulk operations or maintenance
- **Warning, Error, Critical** - Default, show all important messages

**Tips:**
- Change resets to WARNING on bot restart
- Useful for reducing Discord channel clutter
- All logs always saved to bot.log regardless
- Can be changed anytime without affecting bot operation

---

## Command Tips

### General Tips

**For All Users:**
- Commands are slash commands - type `/` to see available commands
- Most commands show results privately (ephemeral)
- Bot must be online for commands to work
- If command doesn't appear, wait a few minutes (Discord sync)

**For Admins:**
- Test commands in a private channel first
- Document major point adjustments
- Process raid submissions promptly
- Check `/view-pending` regularly

### Command Etiquette

**DO:**
- ✅ Use `/xp` to check your own progress
- ✅ Submit raids with accurate info
- ✅ Include all participants
- ✅ Be patient waiting for approval

**DON'T:**
- ❌ Spam commands
- ❌ Submit fake raids
- ❌ Abuse `/xp` or `/leaderboard`
- ❌ Harass admins about approvals

### Keyboard Shortcuts

- Type `/` - Shows all available commands
- Tab - Auto-complete command names
- Escape - Cancel command/form
- Enter - Submit form/command

---

## Troubleshooting

### "You don't have permission to use this command"

**Problem:** Trying to use admin command without permissions

**Solution:**
- Admin commands require Administrator permission OR Admin role
- Ask an admin to grant you permissions
- Check with server owner about role assignment

---

### "You're not registered yet"

**Problem:** Haven't linked Roblox account

**Solution:**
```
/link-roblox YourRobloxUsername
```

---

### "Commands don't appear when I type /"

**Problem:** Discord hasn't synced commands yet

**Solutions:**
1. Wait 1-5 minutes after bot starts
2. Check bot is online (green status)
3. Verify bot has "Use Application Commands" permission
4. Try leaving and rejoining the server
5. Ask admin to restart bot

---

### "Bot doesn't respond to commands"

**Problem:** Bot offline or misconfigured

**Solutions:**
1. Check bot status (should be green/online)
2. Verify bot has proper permissions
3. Check bot is in the server
4. Ask admin to check bot logs
5. Try again in a few minutes

---

### "Raid submission failed"

**Problem:** Image not attached or invalid

**Solutions:**
- Attach image BEFORE opening form
- Use valid image format (PNG, JPG, WEBP)
- Check image uploaded successfully
- File size under 8MB

---

### "Admin channel not configured"

**Problem:** No admin channel set for submissions

**Solution (Admin):**
```
/set-admin-channel #your-admin-channel
```

---

### "You cannot promote yourself"

**Problem:** Trying to use `/promote @yourself`

**Solution:**
- This is intentional - prevents abuse
- Ask another admin to promote you
- All self-promotion attempts are logged

---

### "You cannot add points to yourself"

**Problem:** Trying to use `/add-points @yourself`

**Solution:**
- This is intentional - prevents abuse
- Ask another admin to adjust your points
- All self-point attempts are logged

---

### "Roblox rank update failed"

**Problem:** Bot can't sync to Roblox

**Causes:**
- Invalid Roblox API key
- Bot doesn't have group permissions
- Wrong Roblox group ID
- Roblox API temporarily down

**Solution (Admin):**
- Check bot configuration
- Verify Roblox API key
- Check bot logs for errors
- Contact bot developer if persistent

---

## Quick Reference Card

### User Commands Summary

| Command | Purpose | Example |
|---------|---------|---------|
| `/xp` | Check rank/points | `/xp` |
| `/leaderboard` | View top 10 | `/leaderboard` |
| `/link-roblox` | Register account | `/link-roblox JohnDoe` |
| `/submit-raid` | Submit event | `/submit-raid [image]` |

### Admin Commands Summary

| Command | Purpose | Example |
|---------|---------|---------|
| `/promote` | Promote member | `/promote @user` |
| `/add-points` | Adjust points | `/add-points @user 10` |
| `/set-admin-channel` | Config channel | `/set-admin-channel #channel` |
| `/view-pending` | See submissions | `/view-pending` |
| `/check-member` | View stats | `/check-member @user` |
| `/list-ranks` | Show all ranks | `/list-ranks` |
| `/set-discord-log-level` | Control Discord logs | `/set-discord-log-level ERROR` |

---

## Examples by Scenario

### Scenario 1: New Member Joins

**Member Actions:**
```
1. /link-roblox MyRobloxName
2. /xp (to see they're Private with 0 points)
3. /leaderboard (to see clan rankings)
```

**Admin Actions:**
```
1. /check-member @newmember (verify registration)
2. Optional: /promote @newmember (to Recruit for trial)
```

---

### Scenario 2: Raid Completion

**Member Actions:**
```
1. Take group screenshot
2. /submit-raid [attach screenshot]
3. Fill form with participants and times
4. Wait for admin approval
```

**Admin Actions:**
```
1. Check #raid-approvals channel
2. Click [Approve] button
3. Enter points (1-30)
4. Points automatically distributed
```

---

### Scenario 3: Promotion Time

**Admin Actions:**
```
1. /check-member @player (verify eligibility)
2. /promote @player (if eligible)
3. Member receives notification
4. Roblox rank auto-syncs
```

---

### Scenario 4: Special Recognition

**Admin Actions:**
```
1. /add-points @player 25 (bonus for achievement)
2. /promote @player (to honorary rank like "Veteran")
3. Announce in server
```

---

## Advanced Tips

### For Power Users

**Tracking Progress:**
- Check `/xp` after each raid
- Compare with `/leaderboard` monthly
- Set personal point goals

**Maximizing Activity:**
- Participate in all raids
- Help organize events
- Submit promptly after raids
- Include all participants

### For Admins

**Efficient Management:**
- Process submissions daily
- Use `/view-pending` to track backlog
- Document point adjustments
- Be consistent with point awards

**Best Practices:**
- Award 1-3 pts for small raids
- Award 4-6 pts for medium raids
- Award 7-8 pts for large/special events
- Use admin-only ranks strategically

---

## Need More Help?

- **Admin-Only Ranks:** See `ADMIN_RANKS_GUIDE.md`
- **Rank Customization:** See `RANK_CUSTOMIZATION.md`
- **Setup:** See `SETUP_GUIDE.md`
- **Deployment:** See `RAILWAY_DEPLOYMENT.md`
- **Security:** See `SECURITY.md`

---

## Command Changelog

**Current Version:** 1.0

### v1.0 - Initial Release
- All user commands implemented
- All admin commands implemented
- Admin-only ranks system
- Raid submission workflow
- Roblox integration

---

**Happy raiding! 🎯**

