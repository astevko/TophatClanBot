# Database Backup & Restore Guide

This guide covers backing up your local SQLite database and restoring it to Oracle Cloud Infrastructure (OCI) PostgreSQL.

## Table of Contents
1. [Understanding Your Databases](#1-understanding-your-databases)
2. [Backup Local SQLite Database](#2-backup-local-sqlite-database)
3. [Export Data from SQLite](#3-export-data-from-sqlite)
4. [Migrate to PostgreSQL on OCI](#4-migrate-to-postgresql-on-oci)
5. [Automated Backup Scripts](#5-automated-backup-scripts)
6. [Restore from Backup](#6-restore-from-backup)
7. [Disaster Recovery](#7-disaster-recovery)

---

## 1. Understanding Your Databases

### Local Development (SQLite)
- **Database file:** `tophat_clan.db`
- **Location:** Project root directory
- **Driver:** `aiosqlite`
- **Used when:** `DATABASE_URL` environment variable is NOT set

### Production (PostgreSQL)
- **Location:** OCI server or Autonomous Database
- **Driver:** `asyncpg`
- **Used when:** `DATABASE_URL` environment variable is set
- **Format:** `postgresql://user:password@host:port/database`

### Database Schema
Both databases use the same schema:
- `members` - Discord users linked to Roblox accounts
- `raid_submissions` - Event submissions for approval
- `rank_requirements` - Rank definitions and requirements
- `config` - Bot configuration settings

---

## 2. Backup Local SQLite Database

### Method 1: Simple File Copy (Safest)

```bash
# Navigate to your bot directory
cd /Users/andrewstevko/work/TophatClanBot

# Create backups directory
mkdir -p backups

# Copy database file with timestamp
cp tophat_clan.db "backups/tophat_clan_$(date +%Y%m%d_%H%M%S).db"

# Verify backup
ls -lh backups/
```

### Method 2: Using SQLite CLI

```bash
# Install SQLite (if not already installed)
# macOS:
brew install sqlite

# Create backup with SQLite
sqlite3 tophat_clan.db ".backup backups/tophat_clan_backup.db"

# Verify backup integrity
sqlite3 backups/tophat_clan_backup.db "PRAGMA integrity_check;"
```

### Method 3: Automated Daily Backup Script

Create a backup script:

```bash
# Create backup script
cat > backup_sqlite.sh << 'EOF'
#!/bin/bash
# SQLite Database Backup Script

# Configuration
DB_FILE="tophat_clan.db"
BACKUP_DIR="backups"
RETENTION_DAYS=30

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Create timestamped backup
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/tophat_clan_${TIMESTAMP}.db"

# Copy database
cp "$DB_FILE" "$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_FILE"

echo "✅ Backup created: ${BACKUP_FILE}.gz"

# Delete old backups (older than retention period)
find "$BACKUP_DIR" -name "tophat_clan_*.db.gz" -mtime +$RETENTION_DAYS -delete

echo "✅ Old backups cleaned up (kept last ${RETENTION_DAYS} days)"
EOF

# Make executable
chmod +x backup_sqlite.sh

# Run backup
./backup_sqlite.sh
```

### Schedule Automatic Backups (macOS)

```bash
# Create launchd plist for daily backups at 2 AM
cat > ~/Library/LaunchAgents/com.tophatbot.backup.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.tophatbot.backup</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>/Users/andrewstevko/work/TophatClanBot/backup_sqlite.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>2</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardErrorPath</key>
    <string>/Users/andrewstevko/work/TophatClanBot/logs/backup_error.log</string>
    <key>StandardOutPath</key>
    <string>/Users/andrewstevko/work/TophatClanBot/logs/backup.log</string>
</dict>
</plist>
EOF

# Load the scheduled task
launchctl load ~/Library/LaunchAgents/com.tophatbot.backup.plist

# Check if it's loaded
launchctl list | grep tophatbot
```

---

## 3. Export Data from SQLite

### Export to SQL Dump

```bash
# Export entire database to SQL file
sqlite3 tophat_clan.db .dump > tophat_clan_export.sql

# Export specific table
sqlite3 tophat_clan.db "SELECT * FROM members;" > members_export.csv

# Export all tables as CSV
sqlite3 tophat_clan.db <<EOF
.headers on
.mode csv
.output members.csv
SELECT * FROM members;
.output raid_submissions.csv
SELECT * FROM raid_submissions;
.output rank_requirements.csv
SELECT * FROM rank_requirements;
.output config.csv
SELECT * FROM config;
.quit
EOF
```

### Export to JSON (Using Python)

Create an export script:

```python
# export_sqlite_to_json.py
import sqlite3
import json
from datetime import datetime

def export_to_json(db_path='tophat_clan.db', output_file='backup.json'):
    """Export SQLite database to JSON format."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    data = {
        'export_date': datetime.utcnow().isoformat(),
        'tables': {}
    }
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
    # Export each table
    for table in tables:
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        data['tables'][table] = [dict(row) for row in rows]
        print(f"✅ Exported {len(rows)} rows from {table}")
    
    # Write to file
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    conn.close()
    print(f"\n✅ Export complete: {output_file}")

if __name__ == '__main__':
    export_to_json()
```

Run the export:

```bash
python export_sqlite_to_json.py
```

---

## 4. Migrate to PostgreSQL on OCI

### Method 1: Automated Migration Script (Recommended)

Create a migration script:

```python
# migrate_sqlite_to_postgres.py
import asyncio
import sqlite3
import asyncpg
import sys

# Configuration
SQLITE_DB = 'tophat_clan.db'
# Update this with your OCI PostgreSQL URL
POSTGRES_URL = 'postgresql://botuser:password@your-oci-ip:5432/tophatclan'

async def migrate():
    """Migrate data from SQLite to PostgreSQL."""
    print("🔄 Starting migration from SQLite to PostgreSQL...")
    
    # Connect to SQLite
    sqlite_conn = sqlite3.connect(SQLITE_DB)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()
    
    # Connect to PostgreSQL
    pg_conn = await asyncpg.connect(POSTGRES_URL)
    
    try:
        # Migrate rank_requirements (must be first due to foreign keys)
        print("\n📋 Migrating rank_requirements...")
        sqlite_cursor.execute("SELECT * FROM rank_requirements")
        ranks = sqlite_cursor.fetchall()
        
        for rank in ranks:
            await pg_conn.execute("""
                INSERT INTO rank_requirements 
                (rank_order, rank_name, points_required, roblox_group_rank_id, admin_only)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (rank_order) DO UPDATE SET
                    rank_name = EXCLUDED.rank_name,
                    points_required = EXCLUDED.points_required,
                    roblox_group_rank_id = EXCLUDED.roblox_group_rank_id,
                    admin_only = EXCLUDED.admin_only
            """, rank['rank_order'], rank['rank_name'], rank['points_required'], 
                 rank['roblox_group_rank_id'], bool(rank['admin_only']))
        
        print(f"✅ Migrated {len(ranks)} ranks")
        
        # Migrate members
        print("\n👥 Migrating members...")
        sqlite_cursor.execute("SELECT * FROM members")
        members = sqlite_cursor.fetchall()
        
        for member in members:
            await pg_conn.execute("""
                INSERT INTO members 
                (discord_id, roblox_username, current_rank, points, created_at)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (discord_id) DO UPDATE SET
                    roblox_username = EXCLUDED.roblox_username,
                    current_rank = EXCLUDED.current_rank,
                    points = EXCLUDED.points
            """, member['discord_id'], member['roblox_username'], 
                 member['current_rank'], member['points'], member['created_at'])
        
        print(f"✅ Migrated {len(members)} members")
        
        # Migrate raid_submissions
        print("\n⚔️ Migrating raid_submissions...")
        sqlite_cursor.execute("SELECT * FROM raid_submissions")
        submissions = sqlite_cursor.fetchall()
        
        for sub in submissions:
            await pg_conn.execute("""
                INSERT INTO raid_submissions 
                (submission_id, submitter_id, event_type, participants, start_time, 
                 end_time, image_url, status, points_awarded, admin_id, timestamp)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                ON CONFLICT (submission_id) DO UPDATE SET
                    status = EXCLUDED.status,
                    points_awarded = EXCLUDED.points_awarded,
                    admin_id = EXCLUDED.admin_id
            """, sub['submission_id'], sub['submitter_id'], 
                 sub.get('event_type', 'raid'),  # Default if column doesn't exist
                 sub['participants'], sub['start_time'], sub['end_time'], 
                 sub['image_url'], sub['status'], sub['points_awarded'], 
                 sub['admin_id'], sub['timestamp'])
        
        print(f"✅ Migrated {len(submissions)} raid submissions")
        
        # Migrate config
        print("\n⚙️ Migrating config...")
        sqlite_cursor.execute("SELECT * FROM config")
        configs = sqlite_cursor.fetchall()
        
        for config in configs:
            await pg_conn.execute("""
                INSERT INTO config (key, value)
                VALUES ($1, $2)
                ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
            """, config['key'], config['value'])
        
        print(f"✅ Migrated {len(configs)} config entries")
        
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}", file=sys.stderr)
        raise
    finally:
        sqlite_conn.close()
        await pg_conn.close()

if __name__ == '__main__':
    # Update POSTGRES_URL above before running
    if POSTGRES_URL == 'postgresql://botuser:password@your-oci-ip:5432/tophatclan':
        print("❌ Error: Please update POSTGRES_URL in the script first!")
        sys.exit(1)
    
    asyncio.run(migrate())
```

Run the migration:

```bash
# Install required package if not already installed
pip install asyncpg

# Edit the script to add your PostgreSQL URL
vim migrate_sqlite_to_postgres.py

# Run migration
python migrate_sqlite_to_postgres.py
```

### Method 2: Manual SQL Import

```bash
# Step 1: Export SQLite to SQL dump
sqlite3 tophat_clan.db .dump > sqlite_dump.sql

# Step 2: Clean up SQLite-specific syntax for PostgreSQL
# Create a cleaned version
cat sqlite_dump.sql | \
  sed 's/AUTOINCREMENT/SERIAL/g' | \
  sed 's/INTEGER PRIMARY KEY/BIGSERIAL PRIMARY KEY/g' | \
  sed 's/TEXT NOT NULL,/TEXT NOT NULL,/g' \
  > postgres_import.sql

# Step 3: Copy to OCI server
scp -i /path/to/key postgres_import.sql ubuntu@YOUR_OCI_IP:~/

# Step 4: SSH to OCI and import
ssh -i /path/to/key ubuntu@YOUR_OCI_IP

# Import to PostgreSQL
psql -h localhost -U botuser -d tophatclan -f postgres_import.sql
```

### Method 3: Using pgloader (Advanced)

```bash
# Install pgloader on your local machine
# macOS:
brew install pgloader

# Create pgloader config
cat > migrate.load << EOF
LOAD DATABASE
     FROM sqlite://tophat_clan.db
     INTO postgresql://botuser:password@YOUR_OCI_IP:5432/tophatclan
     WITH include drop, create tables, create indexes, reset sequences
     CAST type INTEGER to BIGINT drop typemod
     CAST type TEXT to TEXT drop typemod;
EOF

# Run migration
pgloader migrate.load
```

---

## 5. Automated Backup Scripts

### PostgreSQL Backup on OCI

Create a backup script on your OCI server:

```bash
# SSH to OCI
ssh -i /path/to/key ubuntu@YOUR_OCI_IP

# Create backup script
cat > ~/backup_postgres.sh << 'EOF'
#!/bin/bash
# PostgreSQL Database Backup Script for OCI

# Configuration
DB_NAME="tophatclan"
DB_USER="botuser"
DB_PASSWORD="YOUR_DB_PASSWORD"
BACKUP_DIR="/home/ubuntu/db_backups"
RETENTION_DAYS=30

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Set password for non-interactive backup
export PGPASSWORD="$DB_PASSWORD"

# Create timestamped backup
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/tophatclan_${TIMESTAMP}.sql"

# Dump database
pg_dump -h localhost -U "$DB_USER" -d "$DB_NAME" > "$BACKUP_FILE"

# Check if backup was successful
if [ $? -eq 0 ]; then
    # Compress backup
    gzip "$BACKUP_FILE"
    echo "✅ Backup created: ${BACKUP_FILE}.gz"
    
    # Calculate size
    SIZE=$(du -h "${BACKUP_FILE}.gz" | cut -f1)
    echo "📦 Backup size: $SIZE"
else
    echo "❌ Backup failed!"
    exit 1
fi

# Delete old backups
find "$BACKUP_DIR" -name "tophatclan_*.sql.gz" -mtime +$RETENTION_DAYS -delete
echo "✅ Cleaned up backups older than ${RETENTION_DAYS} days"

# Unset password
unset PGPASSWORD
EOF

# Make executable
chmod +x ~/backup_postgres.sh

# Test backup
./backup_postgres.sh
```

### Schedule Automated Backups with Cron

```bash
# Edit crontab
crontab -e

# Add this line for daily backups at 2 AM
0 2 * * * /home/ubuntu/backup_postgres.sh >> /home/ubuntu/backup.log 2>&1

# Save and exit

# Verify cron job
crontab -l
```

### Copy Backups to Local Machine

```bash
# From your local machine, sync backups
rsync -avz -e "ssh -i /path/to/key" \
  ubuntu@YOUR_OCI_IP:~/db_backups/ \
  ~/TophatClanBot/oci_backups/
```

---

## 6. Restore from Backup

### Restore SQLite from Backup

```bash
# Stop the bot first
# If running locally:
# Press Ctrl+C or kill the process

# Restore from backup
cp backups/tophat_clan_YYYYMMDD_HHMMSS.db tophat_clan.db

# Or from compressed backup
gunzip -c backups/tophat_clan_YYYYMMDD_HHMMSS.db.gz > tophat_clan.db

# Verify integrity
sqlite3 tophat_clan.db "PRAGMA integrity_check;"

# Restart bot
python bot.py
```

### Restore PostgreSQL from Backup

```bash
# SSH to OCI
ssh -i /path/to/key ubuntu@YOUR_OCI_IP

# Stop the bot (if running)
cd ~/TophatClanBot
docker compose down

# Uncompress backup
gunzip -k db_backups/tophatclan_YYYYMMDD_HHMMSS.sql.gz

# Drop and recreate database (WARNING: deletes all data)
sudo -u postgres psql << EOF
DROP DATABASE tophatclan;
CREATE DATABASE tophatclan;
GRANT ALL PRIVILEGES ON DATABASE tophatclan TO botuser;
EOF

# Restore from backup
export PGPASSWORD="YOUR_DB_PASSWORD"
psql -h localhost -U botuser -d tophatclan < db_backups/tophatclan_YYYYMMDD_HHMMSS.sql
unset PGPASSWORD

# Restart bot
docker compose up -d

# Check logs
docker compose logs -f bot
```

### Restore Specific Tables Only

```bash
# Extract specific table from backup
pg_restore -h localhost -U botuser -d tophatclan \
  --table=members \
  db_backups/tophatclan_YYYYMMDD_HHMMSS.sql
```

---

## 7. Disaster Recovery

### Complete Disaster Recovery Plan

#### Scenario 1: OCI Instance Failure

1. **Create new OCI instance** (follow OCI_DEPLOYMENT_GUIDE.md)
2. **Restore latest database backup:**
   ```bash
   # Copy backup to new instance
   scp -i /path/to/key backups/latest.sql.gz ubuntu@NEW_OCI_IP:~/
   
   # SSH to new instance
   ssh -i /path/to/key ubuntu@NEW_OCI_IP
   
   # Restore database
   gunzip -c latest.sql.gz | psql -h localhost -U botuser -d tophatclan
   ```
3. **Deploy bot** (follow deployment steps)
4. **Update DNS/IP** if applicable

#### Scenario 2: Database Corruption

1. **Stop bot immediately:**
   ```bash
   docker compose down
   ```
2. **Check database integrity:**
   ```bash
   # PostgreSQL
   psql -h localhost -U botuser -d tophatclan -c "SELECT pg_database.datname, pg_size_pretty(pg_database_size(pg_database.datname)) AS size FROM pg_database;"
   ```
3. **Restore from most recent backup**
4. **Restart bot**

#### Scenario 3: Accidental Data Deletion

1. **DO NOT restart bot** - prevents further writes
2. **Immediately create backup of current state:**
   ```bash
   pg_dump -h localhost -U botuser -d tophatclan > emergency_backup.sql
   ```
3. **Restore from backup before deletion occurred**
4. **Compare with emergency backup to recover any new data**

### Off-site Backup Strategy

```bash
# Option 1: Sync to cloud storage (AWS S3, Google Cloud, etc.)
# Install AWS CLI
sudo apt install awscli

# Configure AWS
aws configure

# Sync backups to S3
aws s3 sync ~/db_backups/ s3://your-bucket/tophat-backups/

# Option 2: Sync to GitHub (private repo)
cd ~/db_backups
git init
echo "*.sql" >> .gitignore  # Don't commit uncompressed files
git add *.sql.gz
git commit -m "Database backup $(date +%Y%m%d)"
git push origin main
```

---

## Backup Best Practices

1. **3-2-1 Rule:**
   - 3 copies of data
   - 2 different media types
   - 1 off-site backup

2. **Regular Testing:**
   - Test restores monthly
   - Verify backup integrity

3. **Automation:**
   - Schedule automated backups
   - Monitor backup success/failure

4. **Security:**
   - Encrypt backups (especially off-site)
   - Secure backup storage
   - Rotate credentials

5. **Documentation:**
   - Keep this guide updated
   - Document any custom procedures

---

## Quick Reference Commands

```bash
# Backup SQLite
cp tophat_clan.db backups/backup_$(date +%Y%m%d).db

# Backup PostgreSQL
pg_dump -h localhost -U botuser tophatclan | gzip > backup_$(date +%Y%m%d).sql.gz

# Restore SQLite
cp backups/backup.db tophat_clan.db

# Restore PostgreSQL
gunzip -c backup.sql.gz | psql -h localhost -U botuser -d tophatclan

# Sync backups from OCI
rsync -avz -e "ssh -i key.pem" ubuntu@OCI_IP:~/db_backups/ ./local_backups/
```

---

## Monitoring Backup Health

### Create Backup Monitor Script

```bash
cat > check_backups.sh << 'EOF'
#!/bin/bash
# Check backup health

BACKUP_DIR="db_backups"
MAX_AGE_HOURS=48

# Find latest backup
LATEST=$(find "$BACKUP_DIR" -name "*.sql.gz" -type f -printf '%T@ %p\n' | sort -rn | head -1 | cut -d' ' -f2)

if [ -z "$LATEST" ]; then
    echo "❌ No backups found!"
    exit 1
fi

# Get backup age in hours
AGE_SECONDS=$(( $(date +%s) - $(stat -c %Y "$LATEST") ))
AGE_HOURS=$(( AGE_SECONDS / 3600 ))

echo "📦 Latest backup: $LATEST"
echo "🕐 Age: $AGE_HOURS hours"

if [ $AGE_HOURS -gt $MAX_AGE_HOURS ]; then
    echo "⚠️ WARNING: Backup is too old!"
    exit 1
else
    echo "✅ Backup is fresh"
fi
EOF

chmod +x check_backups.sh
```

---

**Your data is now protected! 💾**

