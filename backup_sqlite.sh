#!/bin/bash
# SQLite Database Backup Script
# Creates timestamped backups of the local SQLite database

set -e  # Exit on error

# Configuration
DB_FILE="tophat_clan.db"
BACKUP_DIR="backups"
RETENTION_DAYS=30
MAX_BACKUPS=50

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "================================================"
echo "SQLite Database Backup Script"
echo "================================================"

# Check if database exists
if [ ! -f "$DB_FILE" ]; then
    echo -e "${RED}❌ Error: Database file '$DB_FILE' not found!${NC}"
    exit 1
fi

# Create backup directory
mkdir -p "$BACKUP_DIR"
echo -e "${GREEN}✅ Backup directory ready: $BACKUP_DIR${NC}"

# Create timestamped backup
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/tophat_clan_${TIMESTAMP}.db"

# Copy database
echo "📦 Creating backup..."
cp "$DB_FILE" "$BACKUP_FILE"

# Verify backup
if [ -f "$BACKUP_FILE" ]; then
    # Compress backup
    echo "🗜️  Compressing backup..."
    gzip "$BACKUP_FILE"
    COMPRESSED_FILE="${BACKUP_FILE}.gz"
    
    # Calculate size
    SIZE=$(du -h "$COMPRESSED_FILE" | cut -f1)
    echo -e "${GREEN}✅ Backup created: ${BACKUP_FILE}.gz${NC}"
    echo -e "${GREEN}📦 Backup size: $SIZE${NC}"
    
    # Verify integrity of compressed backup
    if gunzip -t "$COMPRESSED_FILE" 2>/dev/null; then
        echo -e "${GREEN}✅ Backup integrity verified${NC}"
    else
        echo -e "${RED}❌ Warning: Backup may be corrupted!${NC}"
    fi
else
    echo -e "${RED}❌ Error: Backup creation failed!${NC}"
    exit 1
fi

# Count existing backups
BACKUP_COUNT=$(find "$BACKUP_DIR" -name "tophat_clan_*.db.gz" -type f | wc -l)
echo "📊 Total backups: $BACKUP_COUNT"

# Delete old backups (older than retention period)
echo "🧹 Cleaning up old backups (older than ${RETENTION_DAYS} days)..."
DELETED=$(find "$BACKUP_DIR" -name "tophat_clan_*.db.gz" -mtime +$RETENTION_DAYS -delete -print | wc -l)

if [ $DELETED -gt 0 ]; then
    echo -e "${YELLOW}🗑️  Deleted $DELETED old backup(s)${NC}"
fi

# Limit total number of backups
CURRENT_COUNT=$(find "$BACKUP_DIR" -name "tophat_clan_*.db.gz" -type f | wc -l)
if [ $CURRENT_COUNT -gt $MAX_BACKUPS ]; then
    echo "🗑️  Too many backups ($CURRENT_COUNT), keeping only $MAX_BACKUPS most recent..."
    find "$BACKUP_DIR" -name "tophat_clan_*.db.gz" -type f -printf '%T@ %p\n' | \
        sort -rn | \
        tail -n +$((MAX_BACKUPS + 1)) | \
        cut -d' ' -f2- | \
        xargs rm -f
    echo -e "${GREEN}✅ Cleanup complete${NC}"
fi

# Show latest backups
echo ""
echo "📋 Latest 5 backups:"
find "$BACKUP_DIR" -name "tophat_clan_*.db.gz" -type f -printf '%T@ %p %s\n' | \
    sort -rn | \
    head -5 | \
    while read -r timestamp path size; do
        date_str=$(date -r "${path}" "+%Y-%m-%d %H:%M:%S")
        size_human=$(numfmt --to=iec-i --suffix=B "$size" 2>/dev/null || echo "${size}B")
        basename_path=$(basename "$path")
        echo "  📦 $basename_path - $size_human - $date_str"
    done

echo ""
echo "================================================"
echo -e "${GREEN}✅ Backup completed successfully!${NC}"
echo "================================================"

