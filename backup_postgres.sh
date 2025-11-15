#!/bin/bash
# PostgreSQL Database Backup Script for OCI
# Creates timestamped backups of the PostgreSQL database

set -e  # Exit on error

# Configuration
DB_NAME="tophatclan"
DB_USER="botuser"
DB_HOST="localhost"
DB_PORT="5432"
BACKUP_DIR="db_backups"
RETENTION_DAYS=30
MAX_BACKUPS=50

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "================================================"
echo "PostgreSQL Database Backup Script"
echo "================================================"

# Check if PostgreSQL tools are available
if ! command -v pg_dump &> /dev/null; then
    echo -e "${RED}❌ Error: pg_dump not found. Install PostgreSQL client tools.${NC}"
    exit 1
fi

# Get password from environment or .env file
if [ -z "$DB_PASSWORD" ]; then
    if [ -f ".env" ]; then
        export $(grep -v '^#' .env | grep 'POSTGRES_PASSWORD' | xargs)
        DB_PASSWORD="$POSTGRES_PASSWORD"
    fi
    
    if [ -z "$DB_PASSWORD" ]; then
        echo -e "${RED}❌ Error: Database password not set!${NC}"
        echo "Set DB_PASSWORD environment variable or POSTGRES_PASSWORD in .env file"
        exit 1
    fi
fi

# Create backup directory
mkdir -p "$BACKUP_DIR"
echo -e "${GREEN}✅ Backup directory ready: $BACKUP_DIR${NC}"

# Set password for non-interactive backup
export PGPASSWORD="$DB_PASSWORD"

# Test database connection
echo "🔗 Testing database connection..."
if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Database connection successful${NC}"
else
    echo -e "${RED}❌ Error: Cannot connect to database!${NC}"
    echo "Check:"
    echo "  - PostgreSQL is running: sudo systemctl status postgresql"
    echo "  - Database exists: psql -l"
    echo "  - Credentials are correct"
    unset PGPASSWORD
    exit 1
fi

# Create timestamped backup
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/tophatclan_${TIMESTAMP}.sql"

# Dump database
echo "📦 Creating database dump..."
if pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" > "$BACKUP_FILE"; then
    echo -e "${GREEN}✅ Database dump created${NC}"
else
    echo -e "${RED}❌ Error: Database dump failed!${NC}"
    unset PGPASSWORD
    exit 1
fi

# Unset password
unset PGPASSWORD

# Verify backup file exists and has content
if [ -s "$BACKUP_FILE" ]; then
    # Compress backup
    echo "🗜️  Compressing backup..."
    gzip "$BACKUP_FILE"
    COMPRESSED_FILE="${BACKUP_FILE}.gz"
    
    # Calculate size
    SIZE=$(du -h "$COMPRESSED_FILE" | cut -f1)
    echo -e "${GREEN}✅ Backup created: ${COMPRESSED_FILE}${NC}"
    echo -e "${GREEN}📦 Backup size: $SIZE${NC}"
    
    # Verify compression
    if gunzip -t "$COMPRESSED_FILE" 2>/dev/null; then
        echo -e "${GREEN}✅ Backup integrity verified${NC}"
    else
        echo -e "${RED}❌ Warning: Backup may be corrupted!${NC}"
    fi
else
    echo -e "${RED}❌ Error: Backup file is empty!${NC}"
    rm -f "$BACKUP_FILE"
    exit 1
fi

# Count existing backups
BACKUP_COUNT=$(find "$BACKUP_DIR" -name "tophatclan_*.sql.gz" -type f | wc -l)
echo "📊 Total backups: $BACKUP_COUNT"

# Delete old backups (older than retention period)
echo "🧹 Cleaning up old backups (older than ${RETENTION_DAYS} days)..."
DELETED=$(find "$BACKUP_DIR" -name "tophatclan_*.sql.gz" -mtime +$RETENTION_DAYS -type f -delete -print | wc -l)

if [ $DELETED -gt 0 ]; then
    echo -e "${YELLOW}🗑️  Deleted $DELETED old backup(s)${NC}"
fi

# Limit total number of backups
CURRENT_COUNT=$(find "$BACKUP_DIR" -name "tophatclan_*.sql.gz" -type f | wc -l)
if [ $CURRENT_COUNT -gt $MAX_BACKUPS ]; then
    echo "🗑️  Too many backups ($CURRENT_COUNT), keeping only $MAX_BACKUPS most recent..."
    find "$BACKUP_DIR" -name "tophatclan_*.sql.gz" -type f -printf '%T@ %p\n' | \
        sort -rn | \
        tail -n +$((MAX_BACKUPS + 1)) | \
        cut -d' ' -f2- | \
        xargs rm -f
    echo -e "${GREEN}✅ Cleanup complete${NC}"
fi

# Show latest backups
echo ""
echo "📋 Latest 5 backups:"
find "$BACKUP_DIR" -name "tophatclan_*.sql.gz" -type f -printf '%T@ %p %s\n' | \
    sort -rn | \
    head -5 | \
    while read -r timestamp path size; do
        date_str=$(date -r "${path}" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || date -d "@${timestamp}" "+%Y-%m-%d %H:%M:%S")
        size_human=$(numfmt --to=iec-i --suffix=B "$size" 2>/dev/null || echo "${size}B")
        basename_path=$(basename "$path")
        echo "  📦 $basename_path - $size_human - $date_str"
    done

echo ""
echo "================================================"
echo -e "${GREEN}✅ Backup completed successfully!${NC}"
echo "================================================"
echo ""
echo "💡 To restore this backup:"
echo "   gunzip -c ${COMPRESSED_FILE} | psql -h $DB_HOST -U $DB_USER -d $DB_NAME"

