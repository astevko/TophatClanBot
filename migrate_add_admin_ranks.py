"""
Migration script to add admin_only column and new ranks to existing database.
Run this if you're upgrading from the old rank system.
"""

import sqlite3
import asyncio
import sys

DATABASE_PATH = "tophat_clan.db"


def migrate_sqlite():
    """Migrate SQLite database to include admin_only column and new ranks."""
    print("🔄 Starting migration...")
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Check if admin_only column exists
        cursor.execute("PRAGMA table_info(rank_requirements)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'admin_only' not in columns:
            print("✅ Adding admin_only column...")
            cursor.execute("""
                ALTER TABLE rank_requirements 
                ADD COLUMN admin_only BOOLEAN DEFAULT 0
            """)
            conn.commit()
            print("   Added admin_only column")
        else:
            print("ℹ️  admin_only column already exists")
        
        # Insert new admin-only ranks
        print("✅ Adding new admin-only ranks...")
        
        new_ranks = [
            # Leadership
            (10, "Officer Cadet", 0, 10, 1),
            (11, "Junior Officer", 0, 11, 1),
            (12, "Senior Officer", 0, 12, 1),
            (13, "Commander", 0, 13, 1),
            (14, "High Commander", 0, 14, 1),
            
            # Honorary
            (15, "Veteran", 0, 15, 1),
            (16, "Elite Guard", 0, 16, 1),
            (17, "Legend", 0, 17, 1),
            (18, "Hall of Fame", 0, 18, 1),
            
            # Trial/Probation
            (19, "Recruit", 0, 19, 1),
            (20, "Probation", 0, 20, 1),
        ]
        
        added_count = 0
        for rank_order, rank_name, points_required, roblox_rank_id, admin_only in new_ranks:
            try:
                cursor.execute("""
                    INSERT INTO rank_requirements 
                    (rank_order, rank_name, points_required, roblox_group_rank_id, admin_only)
                    VALUES (?, ?, ?, ?, ?)
                """, (rank_order, rank_name, points_required, roblox_rank_id, admin_only))
                added_count += 1
                print(f"   Added: {rank_name}")
            except sqlite3.IntegrityError:
                print(f"   Skipped: {rank_name} (already exists)")
        
        conn.commit()
        print(f"✅ Added {added_count} new ranks")
        
        # Show current ranks
        print("\n📋 Current rank structure:")
        cursor.execute("""
            SELECT rank_order, rank_name, points_required, admin_only 
            FROM rank_requirements 
            ORDER BY rank_order
        """)
        
        point_based = []
        admin_only_ranks = []
        
        for row in cursor.fetchall():
            rank_order, rank_name, points_required, admin_only = row
            if admin_only:
                admin_only_ranks.append(f"  {rank_order}. {rank_name} (Admin-Only)")
            else:
                admin_only_ranks.append(f"  {rank_order}. {rank_name} ({points_required} pts)")
        
        print("\nPoint-Based Ranks:")
        for rank in point_based:
            print(rank)
        
        print("\nAdmin-Only Ranks:")
        for rank in admin_only_ranks:
            print(rank)
        
        conn.close()
        print("\n✅ Migration completed successfully!")
        print("\n💡 Tip: Restart your bot to apply changes")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)


async def migrate_postgres():
    """Migrate PostgreSQL database to include admin_only column and new ranks."""
    try:
        import asyncpg
        from config import Config
        
        print("🔄 Starting PostgreSQL migration...")
        
        conn = await asyncpg.connect(Config.DATABASE_URL)
        
        # Add admin_only column if it doesn't exist
        try:
            await conn.execute("""
                ALTER TABLE rank_requirements 
                ADD COLUMN admin_only BOOLEAN DEFAULT FALSE
            """)
            print("✅ Added admin_only column")
        except asyncpg.DuplicateColumnError:
            print("ℹ️  admin_only column already exists")
        
        # Insert new admin-only ranks
        print("✅ Adding new admin-only ranks...")
        
        new_ranks = [
            # Leadership
            (10, "Officer Cadet", 0, 10, True),
            (11, "Junior Officer", 0, 11, True),
            (12, "Senior Officer", 0, 12, True),
            (13, "Commander", 0, 13, True),
            (14, "High Commander", 0, 14, True),
            
            # Honorary
            (15, "Veteran", 0, 15, True),
            (16, "Elite Guard", 0, 16, True),
            (17, "Legend", 0, 17, True),
            (18, "Hall of Fame", 0, 18, True),
            
            # Trial/Probation
            (19, "Recruit", 0, 19, True),
            (20, "Probation", 0, 20, True),
        ]
        
        added_count = 0
        for rank_order, rank_name, points_required, roblox_rank_id, admin_only in new_ranks:
            try:
                await conn.execute("""
                    INSERT INTO rank_requirements 
                    (rank_order, rank_name, points_required, roblox_group_rank_id, admin_only)
                    VALUES ($1, $2, $3, $4, $5)
                """, rank_order, rank_name, points_required, roblox_rank_id, admin_only)
                added_count += 1
                print(f"   Added: {rank_name}")
            except asyncpg.UniqueViolationError:
                print(f"   Skipped: {rank_name} (already exists)")
        
        print(f"✅ Added {added_count} new ranks")
        
        await conn.close()
        print("\n✅ Migration completed successfully!")
        print("\n💡 Tip: Restart your bot to apply changes")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 50)
    print("TophatC Clan Bot - Database Migration")
    print("Adding Admin-Only Ranks System")
    print("=" * 50)
    print()
    
    # Check which database to migrate
    import os
    if os.path.exists(DATABASE_PATH):
        print(f"📁 Found SQLite database: {DATABASE_PATH}")
        migrate_sqlite()
    elif os.getenv("DATABASE_URL"):
        print("📁 Found PostgreSQL connection (Railway/Cloud)")
        asyncio.run(migrate_postgres())
    else:
        print("❌ No database found!")
        print("\nPlease either:")
        print("  1. Run the bot first to create the database")
        print("  2. Set DATABASE_URL for PostgreSQL")
        sys.exit(1)

