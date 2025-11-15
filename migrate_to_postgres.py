#!/usr/bin/env python3
"""
SQLite to PostgreSQL Migration Script
Migrates data from local SQLite database to PostgreSQL on OCI.
"""

import asyncio
import sqlite3
import sys
from typing import List, Dict, Any

try:
    import asyncpg
except ImportError:
    print("❌ Error: asyncpg not installed")
    print("Install it with: pip install asyncpg")
    sys.exit(1)

# Configuration
SQLITE_DB = 'tophat_clan.db'
POSTGRES_URL = None  # Will be set from command line or environment


async def get_sqlite_data(table_name: str) -> List[Dict[str, Any]]:
    """Fetch all data from SQLite table."""
    conn = sqlite3.connect(SQLITE_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


async def migrate_rank_requirements(pg_conn: asyncpg.Connection):
    """Migrate rank requirements table."""
    print("\n📋 Migrating rank_requirements...")
    
    ranks = await get_sqlite_data('rank_requirements')
    
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
        """, 
        rank['rank_order'], 
        rank['rank_name'], 
        rank['points_required'], 
        rank['roblox_group_rank_id'], 
        bool(rank.get('admin_only', False)))
    
    print(f"✅ Migrated {len(ranks)} ranks")
    return len(ranks)


async def migrate_members(pg_conn: asyncpg.Connection):
    """Migrate members table."""
    print("\n👥 Migrating members...")
    
    members = await get_sqlite_data('members')
    
    for member in members:
        await pg_conn.execute("""
            INSERT INTO members 
            (discord_id, roblox_username, current_rank, points, created_at)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (discord_id) DO UPDATE SET
                roblox_username = EXCLUDED.roblox_username,
                current_rank = EXCLUDED.current_rank,
                points = EXCLUDED.points
        """, 
        member['discord_id'], 
        member['roblox_username'], 
        member['current_rank'], 
        member['points'], 
        member['created_at'])
    
    print(f"✅ Migrated {len(members)} members")
    return len(members)


async def migrate_raid_submissions(pg_conn: asyncpg.Connection):
    """Migrate raid submissions table."""
    print("\n⚔️  Migrating raid_submissions...")
    
    submissions = await get_sqlite_data('raid_submissions')
    
    migrated = 0
    for sub in submissions:
        # Handle optional event_type column (newer schema)
        event_type = sub.get('event_type', 'raid')
        
        await pg_conn.execute("""
            INSERT INTO raid_submissions 
            (submission_id, submitter_id, event_type, participants, start_time, 
             end_time, image_url, status, points_awarded, admin_id, timestamp)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            ON CONFLICT (submission_id) DO UPDATE SET
                status = EXCLUDED.status,
                points_awarded = EXCLUDED.points_awarded,
                admin_id = EXCLUDED.admin_id
        """, 
        sub['submission_id'], 
        sub['submitter_id'], 
        event_type,
        sub['participants'], 
        sub['start_time'], 
        sub['end_time'], 
        sub['image_url'], 
        sub['status'], 
        sub['points_awarded'], 
        sub['admin_id'], 
        sub['timestamp'])
        migrated += 1
    
    print(f"✅ Migrated {migrated} raid submissions")
    return migrated


async def migrate_config(pg_conn: asyncpg.Connection):
    """Migrate config table."""
    print("\n⚙️  Migrating config...")
    
    try:
        configs = await get_sqlite_data('config')
    except sqlite3.OperationalError:
        print("⚠️  Config table doesn't exist in SQLite, skipping...")
        return 0
    
    for config in configs:
        await pg_conn.execute("""
            INSERT INTO config (key, value)
            VALUES ($1, $2)
            ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
        """, 
        config['key'], 
        config['value'])
    
    print(f"✅ Migrated {len(configs)} config entries")
    return len(configs)


async def verify_migration(pg_conn: asyncpg.Connection):
    """Verify migration by counting rows in PostgreSQL."""
    print("\n🔍 Verifying migration...")
    
    tables = ['rank_requirements', 'members', 'raid_submissions', 'config']
    
    for table in tables:
        try:
            count = await pg_conn.fetchval(f"SELECT COUNT(*) FROM {table}")
            print(f"  ✅ {table}: {count} rows")
        except Exception as e:
            print(f"  ⚠️  {table}: Error - {e}")


async def migrate(postgres_url: str):
    """Main migration function."""
    print("=" * 60)
    print("SQLite to PostgreSQL Migration")
    print("=" * 60)
    
    # Check if SQLite database exists
    try:
        conn = sqlite3.connect(SQLITE_DB)
        conn.close()
        print(f"✅ Found SQLite database: {SQLITE_DB}")
    except Exception as e:
        print(f"❌ Error: Cannot open SQLite database: {e}")
        sys.exit(1)
    
    # Connect to PostgreSQL
    print(f"\n🔗 Connecting to PostgreSQL...")
    try:
        pg_conn = await asyncpg.connect(postgres_url)
        print("✅ Connected to PostgreSQL")
    except Exception as e:
        print(f"❌ Error: Cannot connect to PostgreSQL: {e}")
        print("\nTroubleshooting:")
        print("  1. Check PostgreSQL is running")
        print("  2. Verify connection string format:")
        print("     postgresql://user:password@host:port/database")
        print("  3. Ensure database exists and user has permissions")
        sys.exit(1)
    
    try:
        # Run migrations in order (ranks first due to foreign keys)
        total_ranks = await migrate_rank_requirements(pg_conn)
        total_members = await migrate_members(pg_conn)
        total_submissions = await migrate_raid_submissions(pg_conn)
        total_config = await migrate_config(pg_conn)
        
        # Verify
        await verify_migration(pg_conn)
        
        print("\n" + "=" * 60)
        print("✅ Migration completed successfully!")
        print("=" * 60)
        print(f"\n📊 Summary:")
        print(f"  - Ranks: {total_ranks}")
        print(f"  - Members: {total_members}")
        print(f"  - Raid Submissions: {total_submissions}")
        print(f"  - Config: {total_config}")
        print(f"\n💡 Next steps:")
        print(f"  1. Update your .env file with DATABASE_URL")
        print(f"  2. Restart your bot")
        print(f"  3. Verify bot connects to PostgreSQL")
        print(f"  4. Backup your SQLite database as a safety measure")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        await pg_conn.close()


def main():
    """Entry point."""
    if len(sys.argv) < 2:
        print("Usage: python migrate_to_postgres.py <postgresql_url>")
        print("\nExample:")
        print("  python migrate_to_postgres.py 'postgresql://botuser:password@localhost:5432/tophatclan'")
        print("\nOr set DATABASE_URL environment variable:")
        print("  export DATABASE_URL='postgresql://botuser:password@host:5432/tophatclan'")
        print("  python migrate_to_postgres.py")
        
        # Try to get from environment
        import os
        postgres_url = os.getenv('DATABASE_URL')
        if postgres_url:
            print(f"\n✅ Found DATABASE_URL in environment")
        else:
            sys.exit(1)
    else:
        postgres_url = sys.argv[1]
    
    # Validate PostgreSQL URL format
    if not postgres_url.startswith('postgresql://') and not postgres_url.startswith('postgres://'):
        print("❌ Error: Invalid PostgreSQL URL format")
        print("Format: postgresql://user:password@host:port/database")
        sys.exit(1)
    
    print(f"\n🔗 PostgreSQL URL: {postgres_url.split('@')[1] if '@' in postgres_url else postgres_url}")
    
    # Run migration
    asyncio.run(migrate(postgres_url))


if __name__ == '__main__':
    main()

