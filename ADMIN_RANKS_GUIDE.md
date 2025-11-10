# Admin-Only Ranks Guide

Complete guide to using and managing the admin-only ranks system in TophatC Clan Bot.

---

## Overview

The bot now supports **two types of ranks**:

### 1. Point-Based Ranks (9 total)
- Private, Corporal, Sergeant, Staff Sergeant, Lieutenant, Captain, Major, Colonel, General
- Members earn these through raids and activity points
- Admins can promote when member has enough points
- **Icon**: 📊

### 2. Admin-Only Ranks (11 total)
- **Leadership**: Officer Cadet, Junior Officer, Senior Officer, Commander, High Commander
- **Honorary**: Veteran, Elite Guard, Legend, Hall of Fame
- **Trial**: Recruit, Probation
- Only admins can grant these ranks (no point requirement)
- **Icon**: ⚡

---

## How It Works

### For Members

**If you have a point-based rank:**
- Use `/xp` to see progress toward next rank
- Earn points through raids
- Admin promotes you when eligible

**If you have an admin-only rank:**
- `/xp` still shows your points
- Points count toward point-based ranks
- Admin can change your rank at any time

### For Admins

**Promoting to point-based ranks:**
- Member needs required points
- Bot checks eligibility
- Use `/promote @member`

**Promoting to admin-only ranks:**
- No point requirement
- Admin can grant immediately
- Use `/promote @member`

---

## Common Use Cases

### 1. New Member Trial Period

New members start in trial rank:

```
/link-roblox NewMember123
/promote @NewMember  → Select "Recruit" (rank 19)
```

Member is now in trial. After proving themselves:

```
/promote @NewMember → Select "Private" (rank 1)
```

Member begins normal point progression.

### 2. Officer Positions

Promote trusted member to leadership:

```
/promote @TrustedMember → Select "Junior Officer" (rank 11)
```

Member keeps their points and can be promoted to higher officer ranks or back to point-based ranks.

### 3. Honorary Recognition

Reward long-time member:

```
/promote @VeteranMember → Select "Veteran" (rank 15)
```

Member receives honorary rank while keeping all their points.

### 4. Probation/Discipline

Temporarily demote member:

```
/promote @MemberName → Select "Probation" (rank 20)
```

After improvement:

```
/promote @MemberName → Back to their earned rank
```

---

## Commands Reference

### `/xp` - Check Your Progress

**With point-based rank:**
```
📊 Your Progress
Current Rank: Sergeant 📊
Total Points: 75
Rank Type: Point-Based
Next Point-Based Rank: Staff Sergeant
Progress: [████░░░░░░] 75/100 (25 points needed)
```

**With admin-only rank:**
```
📊 Your Progress
Current Rank: Commander ⚡
Total Points: 150
Rank Type: Admin-Granted
Next Point-Based Rank: Lieutenant
Progress: [██████████] 150/150 (Eligible!)
ℹ️ Note: You have an admin-granted rank. Points still count toward point-based ranks!
```

### `/list-ranks` - View All Ranks (Admin)

```
🎖️ Clan Rank System

📊 Point-Based Ranks (Earn through raids)
1. Private - 0 pts
2. Corporal - 30 pts
3. Sergeant - 60 pts
...

⚡ Leadership Ranks (Admin-granted)
10. Officer Cadet
11. Junior Officer
...

🏆 Honorary Ranks (Admin-granted)
15. Veteran
16. Elite Guard
...

🔰 Trial/Probation (Admin-granted)
19. Recruit
20. Probation
```

### `/check-member @user` - Check Member Details (Admin)

```
📊 Member Stats: @UserName

Discord: @UserName
Roblox: RobloxName123
Member Since: 2024-11-01

Current Rank: Commander
Total Points: 250
Rank Type: ⚡ Admin-Only

Next Point-Based Rank: Captain
Auto-Promotion Status: ✅ Eligible for Promotion
(250/210 points)

ℹ️ Note: This member has an admin-granted rank. Use /promote to change ranks manually.
```

### `/promote @user` - Promote Member (Admin)

**Behavior changes based on target rank:**

Promoting to **point-based rank**:
- Bot checks if member has enough points
- If not enough: Shows error
- If enough: Promotes

Promoting to **admin-only rank**:
- No point check
- Immediate promotion
- Shows "⚡ Admin-Only Rank (Manual Promotion)"

---

## Workflows

### Workflow 1: Standard Member Progression

```
1. New member joins
   /link-roblox Username

2. Starts at Private (rank 1, 0 pts)
   Current: Private 📊

3. Participates in raids
   +5 pts per raid

4. Reaches 30 points
   /promote @member → Corporal

5. Continues earning points
   Eventually reaches General
```

### Workflow 2: Officer Track

```
1. Member is Sergeant (60 pts)
   Current: Sergeant 📊

2. Admin promotes to officer role
   /promote @member → Junior Officer

3. Now has officer rank
   Current: Junior Officer ⚡
   Points: 60 (saved)

4. Can be promoted within officers
   /promote @member → Senior Officer

5. Or return to point-based
   /promote @member → Staff Sergeant
   (if they have 100+ points)
```

### Workflow 3: Trial Member

```
1. New member joins
   /link-roblox NewMember

2. Put in trial
   /promote @NewMember → Recruit

3. Member proves themselves
   Participates in 3+ raids

4. Promote to Private
   /promote @NewMember → Private

5. Normal progression begins
   Can now earn point-based ranks
```

---

## Best Practices

### ✅ DO:

- **Use Recruit for all new members** - Trial period before full access
- **Use Probation sparingly** - For discipline/temporary demotion
- **Keep officer ranks for active leadership** - Not everyone needs it
- **Give honorary ranks as rewards** - Veteran, Legend, Hall of Fame
- **Document your decisions** - Note why you grant admin-only ranks

### ❌ DON'T:

- Grant admin-only ranks too freely - They're special
- Forget members still earn points - They can progress
- Mix up the categories - Keep leadership/honorary/trial separate
- Skip the trial period - New members should prove themselves
- Remove all point-based paths - Members need progression

---

## Customizing Admin-Only Ranks

### Change Rank Names

Edit `database.py` lines 88-103:

```python
# Change "Commander" to "Squad Leader"
(13, "Squad Leader", 0, 13, True),

# Change "Veteran" to "OG Member"  
(15, "OG Member", 0, 15, True),
```

### Add More Admin-Only Ranks

```python
# Add a new honorary rank
(21, "MVP", 0, 21, True),

# Add another leadership rank
(22, "Division Commander", 0, 22, True),
```

### Remove Admin-Only Ranks

Simply delete the ranks you don't want from the list.

**Note:** Make sure Roblox group rank IDs match!

---

## FAQs

**Q: Can a member have both types of ranks?**
A: No, members have ONE rank at a time. But they can switch between types.

**Q: Do points matter for admin-only ranks?**
A: No. Admin can grant them regardless of points. But members still accumulate points.

**Q: What happens to points when switching to admin-only rank?**
A: Points are saved! They still count toward point-based ranks.

**Q: Can I promote someone from Admin-Only rank to Point-Based rank?**
A: Yes! Use `/promote` as normal. Bot will check if they have enough points for point-based ranks.

**Q: How do I see who has admin-only ranks?**
A: Use `/check-member @user` - it shows rank type (⚡ Admin-Only or 📊 Point-Based)

**Q: Can members see admin-only ranks?**
A: Yes, in `/list-ranks` (everyone can see this). But only admins can grant them.

**Q: What if I want MORE than 11 admin-only ranks?**
A: Edit `database.py` and add more ranks with `admin_only=True`

---

## Migrating Existing Database

If you're upgrading from the old system:

```bash
# Run migration script
python migrate_add_admin_ranks.py

# Restart bot
make run
```

The migration:
- Adds `admin_only` column
- Inserts 11 new admin-only ranks
- Keeps all existing member data
- No data loss

---

## Troubleshooting

**Issue: Admin-only ranks don't appear**
- Run migration script
- Check database has `admin_only` column
- Restart bot

**Issue: Can't promote to admin-only rank**
- Verify you have admin permissions
- Check rank exists in database
- Try `/list-ranks` to see all ranks

**Issue: Member has admin-only rank but can't be promoted**
- This is normal for point-based ranks
- Member needs required points
- Or use admin-only rank for manual promotion

---

## Summary

The admin-only ranks system gives you flexibility:

- **Point-Based**: Automatic progression through activity
- **Admin-Only**: Manual grants for special situations

Use point-based for regular progression, admin-only for leadership, honorary recognition, and trials.

Members can switch between both types, and all points are preserved!

