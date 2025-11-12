# Rank Identification Guide

## 🎯 Overview

New admin commands to help you identify, configure, and troubleshoot Roblox rank mappings in your Discord bot.

---

## 🆕 New Commands

### 1. `/list-roblox-ranks`

**Purpose:** Fetch and display all ranks from your Roblox group with their IDs.

**Usage:**
```
/list-roblox-ranks
```

**What It Shows:**
- All ranks from your Roblox group
- Rank number (0-255)
- Role ID (unique identifier)
- Member count per rank

**Example Output:**
```
🎮 Roblox Group Ranks: TophatC Clan

Ranks 1-10
──────────
Guest
  • Rank #: 0
  • Role ID: 254791234
  • Members: 5

Private
  • Rank #: 1
  • Role ID: 254791235
  • Members: 12

E0 | Enlist
  • Rank #: 2
  • Role ID: 254791236
  • Members: 34

E1 | Soldier
  • Rank #: 45
  • Role ID: 254791237
  • Members: 28

[...more ranks...]

💡 How to Use
──────────
To configure database ranks:
1. Choose either Rank # or Role ID for each rank
2. Update database.py in insert_default_ranks()
3. Use the format: (order, 'Name', points, rank_or_id, admin_only)

Recommendation: Use Rank # for simplicity
Use Role ID for precision
```

**When to Use:**
- Setting up the bot for the first time
- Adding new ranks to your database
- Troubleshooting rank sync issues
- Checking current Roblox group structure

---

### 2. `/compare-ranks`

**Purpose:** Compare your configured database ranks with actual Roblox group ranks.

**Usage:**
```
/compare-ranks
```

**What It Shows:**
- ✅ **Mapped ranks** - Database ranks that match Roblox ranks
- ⚠️ **Unmapped ranks** - Database ranks with no Roblox match
- 💡 **Missing ranks** - Roblox ranks not in your database
- 📊 **Summary statistics**

**Example Output:**
```
🔄 Rank Mapping Comparison

✅ Mapped Ranks (18)
──────────────────
🔢 Pending
  → Roblox: Guest (Rank #0)

🔢 E0 | Enlist
  → Roblox: Private (Rank #1)

🔗 E1 | Soldier
  → Roblox: E1 | Soldier (Rank #45)

[...more mapped ranks...]

⚠️ Unmapped Ranks (3)
───────────────────
❌ Old Rank Name
  Looking for: ID/Rank# 999

❌ Removed Rank
  Looking for: ID/Rank# 254799999

🔧 Fix Unmapped Ranks
──────────────────
1. Run /list-roblox-ranks to see available Roblox ranks
2. Update database.py with correct rank IDs or numbers
3. Restart the bot to apply changes

💡 Roblox Ranks Not in Database (2)
─────────────────────────────────
➕ New Rank Added
  Rank #: 100 | Role ID: 254791240

➕ Special Rank
  Rank #: 200 | Role ID: 254791241

📊 Summary
─────────
✅ Mapped: 18
⚠️ Unmapped: 3
💡 Missing: 2
🎮 Total Roblox Ranks: 20
💾 Total Database Ranks: 21

🔗 = Matched by Role ID | 🔢 = Matched by Rank Number
```

**When to Use:**
- After making changes to Roblox group ranks
- Diagnosing sync issues
- Verifying database configuration
- Regular maintenance checks

---

### 3. `/list-ranks` (Existing)

**Purpose:** View all configured Discord/database ranks.

**Usage:**
```
/list-ranks
```

**What It Shows:**
- Point-based ranks with requirements
- Admin-only ranks
- Rank hierarchy

---

## 🔧 How to Configure Ranks

### Step 1: Get Roblox Rank Information

Run the command:
```
/list-roblox-ranks
```

This shows you all ranks from your Roblox group with their identifiers.

---

### Step 2: Choose Your Mapping Strategy

You have two options:

#### **Option A: Use Rank Numbers (Recommended)**

**Pros:**
- ✅ Simple and easy to configure
- ✅ Works if you recreate roles in Roblox
- ✅ Portable across different groups
- ✅ Easy to remember (0-255)

**Cons:**
- ⚠️ Could conflict if rank numbers change

**Example:**
```python
# database.py
default_ranks = [
    (1, "Pending", 0, 0, False),      # Rank number 0
    (2, "E0 | Enlist", 1, 1, False),  # Rank number 1
    (3, "E1 | Soldier", 3, 45, False), # Rank number 45
]
```

---

#### **Option B: Use Role IDs (More Precise)**

**Pros:**
- ✅ Extremely specific to each role
- ✅ No conflicts with other roles
- ✅ Won't break if rank numbers change

**Cons:**
- ⚠️ Need to look up IDs from Roblox
- ⚠️ Different IDs for each group
- ⚠️ Must update if roles are recreated

**Example:**
```python
# database.py
default_ranks = [
    (1, "Pending", 0, 254791234, False),     # Role ID
    (2, "E0 | Enlist", 1, 254791235, False), # Role ID
    (3, "E1 | Soldier", 3, 254791236, False), # Role ID
]
```

---

### Step 3: Update Database Configuration

Edit `database.py` in the `insert_default_ranks()` function:

```python
async def insert_default_ranks(db):
    """Insert default military ranks into the database."""
    default_ranks = [
        # Format: (rank_order, rank_name, points_required, roblox_id_or_number, admin_only)
        
        # Point-Based Ranks
        (1, "Pending", 0, 0, False),
        (2, "E0 | Enlist", 1, 1, False),
        (3, "E1 | Soldier", 3, 45, False),
        (4, "E2 | Specialist", 5, 46, False),
        # ... add more ranks ...
        
        # Admin-Only Ranks
        (17, "Commander", 0, 150, True),
        (18, "Leader", 0, 255, True),
    ]
    
    for rank_order, rank_name, points_required, roblox_rank_id, admin_only in default_ranks:
        await db.execute("""
            INSERT OR IGNORE INTO rank_requirements 
            (rank_order, rank_name, points_required, roblox_group_rank_id, admin_only)
            VALUES (?, ?, ?, ?, ?)
        """, (rank_order, rank_name, points_required, roblox_rank_id, admin_only))
    
    await db.commit()
```

---

### Step 4: Verify Configuration

Run the comparison command:
```
/compare-ranks
```

This will show:
- ✅ Which ranks are correctly mapped
- ⚠️ Which ranks need fixing
- 💡 Which Roblox ranks aren't in your database

---

### Step 5: Fix Issues

If you see unmapped ranks:

1. Check the Roblox rank ID/number it's looking for
2. Run `/list-roblox-ranks` to find the correct value
3. Update `database.py` with the correct ID/number
4. Restart the bot
5. Run `/compare-ranks` again to verify

---

## 📋 Configuration Examples

### Example 1: Small Group (Use Rank Numbers)

```python
default_ranks = [
    # Basic ranks using rank numbers 0-10
    (1, "Guest", 0, 0, False),
    (2, "Member", 10, 1, False),
    (3, "Regular", 25, 2, False),
    (4, "Veteran", 50, 3, False),
    (5, "Elite", 100, 4, False),
    (6, "Admin", 0, 10, True),
]
```

---

### Example 2: Military Group (Use Role IDs)

```python
default_ranks = [
    # Using specific role IDs from Roblox
    (1, "Recruit", 0, 254791234, False),
    (2, "Private", 5, 254791235, False),
    (3, "Corporal", 15, 254791236, False),
    (4, "Sergeant", 30, 254791237, False),
    (5, "Lieutenant", 60, 254791238, False),
    (6, "Captain", 0, 254791239, True),
    (7, "General", 0, 254791240, True),
]
```

---

### Example 3: Mixed Strategy

```python
default_ranks = [
    # Common ranks using rank numbers (easier)
    (1, "Pending", 0, 0, False),
    (2, "Member", 5, 1, False),
    (3, "Active", 15, 2, False),
    
    # Important ranks using role IDs (more precise)
    (4, "VIP", 0, 254791250, True),
    (5, "Moderator", 0, 254791251, True),
    (6, "Admin", 0, 254791252, True),
]
```

---

## 🔍 Troubleshooting

### Issue: "No database rank found for Roblox rank"

**Cause:** A Roblox rank doesn't have a matching database entry.

**Solution:**
1. Run `/list-roblox-ranks` to see the rank's ID/number
2. Run `/compare-ranks` to see what's missing
3. Add the rank to `database.py`
4. Restart bot

---

### Issue: "Sync skipped" for multiple users

**Cause:** Multiple Roblox ranks aren't in your database.

**Solution:**
1. Run `/compare-ranks`
2. Check "Roblox Ranks Not in Database" section
3. Add all missing ranks to `database.py`
4. Restart bot
5. Run `/sync` to bulk update everyone

---

### Issue: Ranks are mapped but sync doesn't work

**Possible Causes:**
- Network issues with Roblox API
- User not in Roblox group
- Invalid Roblox username
- Roblox API rate limiting

**Solution:**
1. Check bot logs for specific errors
2. Verify user is in Roblox group
3. Run `/verify-rank @user` to check specific member
4. Wait a few minutes and try again (rate limiting)

---

### Issue: Role IDs changed after recreating roles

**Cause:** Deleting and recreating Roblox roles gives them new IDs.

**Solution:**
1. Run `/list-roblox-ranks` to get new IDs
2. Update all affected ranks in `database.py`
3. Restart bot
4. Run `/sync` to update all members

**Prevention:** Use rank numbers instead of role IDs!

---

## 📊 Command Comparison

| Command | What It Shows | When to Use |
|---------|---------------|-------------|
| `/list-roblox-ranks` | All Roblox group ranks with IDs | Initial setup, adding ranks |
| `/compare-ranks` | Mapping status between Roblox & DB | Verify config, troubleshoot |
| `/list-ranks` | Configured Discord ranks | Check current setup |
| `/verify-rank @user` | Single user's rank status | Check specific member |
| `/sync @user` | Try syncing single user | Fix individual sync issues |
| `/sync` | Bulk sync all members | Update everyone at once |

---

## 💡 Best Practices

### 1. **Regular Checks**
Run `/compare-ranks` monthly to ensure everything is in sync.

### 2. **Document Your Ranks**
Keep a reference of your rank structure:
```
Rank #0 → Guest (new members)
Rank #1 → Member (basic rank)
Rank #45 → Soldier (earned rank)
...
```

### 3. **Use Rank Numbers for Flexibility**
Unless you need extreme precision, rank numbers are easier to maintain.

### 4. **Test After Changes**
After updating `database.py`:
1. Restart bot
2. Run `/compare-ranks`
3. Test with `/sync` on a few users
4. Check bot logs

### 5. **Handle Missing Ranks**
If users have Roblox ranks not in your database:
- Decide if you want to add them
- Or leave them as "skipped" (won't break sync)

---

## 🎉 Benefits

✅ **Easy Setup** - See exactly what ranks to configure

✅ **Clear Visibility** - Know what's mapped and what's not

✅ **Quick Troubleshooting** - Identify issues immediately

✅ **Confidence** - Verify changes before they affect users

✅ **No Guessing** - Get exact IDs and numbers from Roblox

---

## 📝 Quick Reference

```bash
# View Roblox ranks with IDs
/list-roblox-ranks

# Compare Roblox with database
/compare-ranks

# View configured Discord ranks
/list-ranks

# Check specific user
/verify-rank @user

# Sync user manually
/sync @user

# Bulk sync everyone
/sync
```

---

**Last Updated:** November 12, 2025  
**Version:** 2.3 - Rank Identification  
**Status:** ✅ Implemented

