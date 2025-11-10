# Rank Customization Guide

## Where to Edit Ranks

File: **`database.py`** (lines 75-85)

Function: `insert_default_ranks()`

---

## Understanding the Rank Format

Each rank is defined as a tuple with 4 values:

```python
(rank_order, "Rank Name", points_required, roblox_group_rank_id)
```

**Fields:**
1. **rank_order** - Position in hierarchy (1, 2, 3, etc.)
2. **rank_name** - Display name in Discord
3. **points_required** - Minimum points needed to achieve this rank
4. **roblox_group_rank_id** - Corresponding Roblox group rank number

---

## Example Customizations

### Example 1: Easier Progression (Lower Points)

```python
default_ranks = [
    (1, "Private", 0, 1),
    (2, "Corporal", 20, 2),        # Was 30
    (3, "Sergeant", 40, 3),         # Was 60
    (4, "Staff Sergeant", 65, 4),   # Was 100
    (5, "Lieutenant", 95, 5),       # Was 150
    (6, "Captain", 130, 6),         # Was 210
    (7, "Major", 170, 7),           # Was 280
    (8, "Colonel", 215, 8),         # Was 360
    (9, "General", 270, 9),         # Was 450
]
```

### Example 2: Harder Progression (Higher Points)

```python
default_ranks = [
    (1, "Private", 0, 1),
    (2, "Corporal", 50, 2),         # Was 30
    (3, "Sergeant", 120, 3),        # Was 60
    (4, "Staff Sergeant", 200, 4),  # Was 100
    (5, "Lieutenant", 300, 5),      # Was 150
    (6, "Captain", 450, 6),         # Was 210
    (7, "Major", 650, 7),           # Was 280
    (8, "Colonel", 900, 8),         # Was 360
    (9, "General", 1200, 9),        # Was 450
]
```

### Example 3: Different Rank Names (Custom Theme)

```python
default_ranks = [
    (1, "Recruit", 0, 1),
    (2, "Scout", 25, 2),
    (3, "Soldier", 50, 3),
    (4, "Elite", 100, 4),
    (5, "Commander", 175, 5),
    (6, "Champion", 275, 6),
    (7, "War Chief", 400, 7),
    (8, "Legend", 550, 8),
]
```

### Example 4: Fewer Ranks (Simple System)

```python
default_ranks = [
    (1, "Member", 0, 1),
    (2, "Veteran", 50, 2),
    (3, "Elite", 150, 3),
    (4, "Leader", 300, 4),
]
```

### Example 5: More Ranks (Detailed Progression)

```python
default_ranks = [
    (1, "Trainee", 0, 1),
    (2, "Private", 15, 2),
    (3, "Private First Class", 35, 3),
    (4, "Specialist", 60, 4),
    (5, "Corporal", 90, 5),
    (6, "Sergeant", 125, 6),
    (7, "Staff Sergeant", 165, 7),
    (8, "Sergeant First Class", 210, 8),
    (9, "Master Sergeant", 260, 9),
    (10, "Lieutenant", 315, 10),
    (11, "Captain", 375, 11),
    (12, "Major", 440, 12),
    (13, "Colonel", 510, 13),
    (14, "General", 600, 14),
]
```

---

## Matching Roblox Group Ranks

### Step 1: Check Your Roblox Group Ranks

1. Go to your Roblox group page
2. Click "Configure Group" (must be owner/admin)
3. Go to "Roles" section
4. Note the rank numbers (usually 1-255)

**Example:**
```
Rank 1: Guest (don't use this)
Rank 5: Member
Rank 10: Private
Rank 50: Corporal
Rank 100: Sergeant
Rank 200: Lieutenant
Rank 255: General
```

### Step 2: Map Discord Ranks to Roblox Ranks

```python
default_ranks = [
    # (order, name, points, roblox_rank_number)
    (1, "Private", 0, 10),          # Roblox rank 10
    (2, "Corporal", 30, 50),        # Roblox rank 50
    (3, "Sergeant", 60, 100),       # Roblox rank 100
    (4, "Lieutenant", 150, 200),    # Roblox rank 200
    (5, "General", 300, 255),       # Roblox rank 255 (max)
]
```

**Important:** The `roblox_group_rank_id` must match the actual rank number in your Roblox group!

---

## How to Apply Changes

### ⚠️ IMPORTANT: Database Considerations

The ranks are only inserted on **first run** when the database is created.

#### Option A: Fresh Start (Recommended for Testing)

1. **Backup existing database** (if you have data):
   ```bash
   cp tophat_clan.db tophat_clan.db.backup
   ```

2. **Delete the database**:
   ```bash
   rm tophat_clan.db
   ```

3. **Edit `database.py`** with your custom ranks

4. **Run the bot**:
   ```bash
   make run
   ```

5. New database will be created with your custom ranks

#### Option B: Update Existing Database

If you already have members and data:

```bash
# Create a SQL script to update ranks
sqlite3 tophat_clan.db
```

Then in SQLite:

```sql
-- Update existing ranks
UPDATE rank_requirements SET points_required = 20 WHERE rank_order = 2;
UPDATE rank_requirements SET points_required = 40 WHERE rank_order = 3;
-- etc...

-- Or delete and re-insert
DELETE FROM rank_requirements;
-- Then restart bot to re-insert

-- Check your changes
SELECT * FROM rank_requirements ORDER BY rank_order;

-- Exit
.quit
```

#### Option C: Manual SQL Update Script

Create `update_ranks.sql`:

```sql
-- Clear existing ranks
DELETE FROM rank_requirements;

-- Insert new ranks
INSERT INTO rank_requirements (rank_order, rank_name, points_required, roblox_group_rank_id) VALUES
(1, 'Recruit', 0, 1),
(2, 'Scout', 25, 2),
(3, 'Soldier', 50, 3),
(4, 'Elite', 100, 4);

-- Verify
SELECT * FROM rank_requirements ORDER BY rank_order;
```

Run it:
```bash
sqlite3 tophat_clan.db < update_ranks.sql
```

---

## Testing Your Changes

### 1. Check Ranks are Loaded

After starting the bot, check logs:
```bash
grep "Default ranks inserted" bot.log
```

### 2. View Ranks in Discord

As admin, run:
```
/list-ranks
```

You should see your custom ranks and point requirements.

### 3. Test Progression

1. Link a test account: `/link-roblox TestUser`
2. Add points: `/add-points @testuser 25`
3. Check progress: `/xp`
4. Promote when eligible: `/promote @testuser`

---

## Common Issues & Solutions

### Issue: Ranks didn't change after editing

**Solution:** Database already exists with old ranks.
- Delete `tophat_clan.db` and restart bot
- Or manually update with SQL

### Issue: Wrong Roblox ranks being set

**Solution:** Check your roblox_group_rank_id values match your actual Roblox group ranks.

### Issue: Members promoted too fast/slow

**Solution:** Adjust `points_required` values in `database.py`

### Issue: Can't delete database - data loss

**Solution:** Export data first:
```bash
sqlite3 tophat_clan.db .dump > backup.sql
# Edit ranks in database.py
rm tophat_clan.db
# Restart bot (new ranks)
# Re-import member data if needed
```

---

## Best Practices

### ✅ DO:
- Test with a fresh database first
- Backup your database before changes
- Use logical point progression (30, 60, 100 not 30, 35, 40)
- Match Discord rank names to Roblox ranks
- Document your custom system

### ❌ DON'T:
- Use negative points
- Skip rank_order numbers (1, 2, 4, 5 ❌)
- Use duplicate rank_order values
- Use Roblox rank 1 (usually "Guest")
- Change ranks while members are active

---

## Point Calculation Examples

### Average 5 points per raid:

| Ranks Needed | Total Points | Raids Needed |
|-------------|--------------|--------------|
| Private → Corporal | 30 | 6 raids |
| Private → Sergeant | 60 | 12 raids |
| Private → Lieutenant | 150 | 30 raids |
| Private → General | 450 | 90 raids |

### Want faster progression? Lower points:

| Ranks Needed | Total Points | Raids Needed |
|-------------|--------------|--------------|
| Private → Corporal | 20 | 4 raids |
| Private → Sergeant | 40 | 8 raids |
| Private → Lieutenant | 95 | 19 raids |
| Private → General | 270 | 54 raids |

---

## Need Help?

Can't figure out what points to use? Consider:

1. **How active is your clan?**
   - Very active (daily raids): Higher points OK
   - Casual (weekly): Lower points needed

2. **How long should max rank take?**
   - 3 months of active play: ~300-500 points
   - 6 months: ~500-800 points
   - 1 year: ~1000+ points

3. **Average points per event?**
   - Small events: 1-3 points
   - Medium events: 3-5 points
   - Large events: 5-8 points

**Formula:**
```
Total Points Needed = (Weeks to Max Rank) × (Events per Week) × (Avg Points per Event)
```

Example: 6 months (24 weeks) × 2 events/week × 4 points = 192 total points for max rank

