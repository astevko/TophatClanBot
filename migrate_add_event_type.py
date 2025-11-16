"""
Migration script to add event_type column to raid_submissions table
This is needed for databases created before this field was added.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Import the appropriate database module
from config import Config

if Config.USE_ORACLE:
    import oracledb
    
    async def migrate_oracle():
        """Add event_type column to Oracle database."""
        print("Migrating Oracle database...")
        
        pool = oracledb.create_pool(
            user=Config.ORACLE_USER,
            password=Config.ORACLE_PASSWORD,
            dsn=Config.ORACLE_DSN,
            config_dir=Config.ORACLE_CONFIG_DIR,
            min=1,
            max=2,
        )
        
        connection = pool.acquire()
        
        try:
            cursor = connection.cursor()
            
            # Check if column exists
            cursor.execute("""
                SELECT COUNT(*) 
                FROM user_tab_columns 
                WHERE table_name = 'RAID_SUBMISSIONS' 
                AND column_name = 'EVENT_TYPE'
            """)
            exists = cursor.fetchone()[0]
            
            if exists > 0:
                print("✓ event_type column already exists")
                return True
            
            # Add the column
            cursor.execute("""
                ALTER TABLE raid_submissions 
                ADD event_type VARCHAR2(50) DEFAULT 'Raid' NOT NULL
            """)
            
            connection.commit()
            print("✓ Added event_type column to raid_submissions")
            return True
            
        except oracledb.Error as e:
            error_obj, = e.args
            print(f"✗ Error: {error_obj.message}")
            return False
        finally:
            pool.release(connection)
    
    async def main():
        success = await migrate_oracle()
        if success:
            print("\n✓ Migration completed successfully!")
        else:
            print("\n✗ Migration failed!")
            sys.exit(1)

elif Config.USE_SQLITE:
    import aiosqlite
    
    async def migrate_sqlite():
        """Add event_type column to SQLite database."""
        print("Migrating SQLite database...")
        
        async with aiosqlite.connect("tophat_clan.db") as db:
            # Check if column exists
            async with db.execute("PRAGMA table_info(raid_submissions)") as cursor:
                columns = await cursor.fetchall()
                column_names = [col[1] for col in columns]
                
                if 'event_type' in column_names:
                    print("✓ event_type column already exists")
                    return True
            
            # Add the column
            await db.execute("""
                ALTER TABLE raid_submissions 
                ADD COLUMN event_type TEXT NOT NULL DEFAULT 'Raid'
            """)
            
            await db.commit()
            print("✓ Added event_type column to raid_submissions")
            return True
    
    async def main():
        try:
            success = await migrate_sqlite()
            if success:
                print("\n✓ Migration completed successfully!")
            else:
                print("\n✗ Migration failed!")
                sys.exit(1)
        except Exception as e:
            print(f"✗ Error: {e}")
            sys.exit(1)

else:  # PostgreSQL
    import asyncpg
    
    async def migrate_postgres():
        """Add event_type column to PostgreSQL database."""
        print("Migrating PostgreSQL database...")
        
        conn = await asyncpg.connect(Config.DATABASE_URL)
        
        try:
            # Check if column exists
            exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT 1 
                    FROM information_schema.columns 
                    WHERE table_name = 'raid_submissions' 
                    AND column_name = 'event_type'
                )
            """)
            
            if exists:
                print("✓ event_type column already exists")
                return True
            
            # Add the column
            await conn.execute("""
                ALTER TABLE raid_submissions 
                ADD COLUMN event_type TEXT NOT NULL DEFAULT 'Raid'
            """)
            
            print("✓ Added event_type column to raid_submissions")
            return True
            
        except asyncpg.PostgresError as e:
            print(f"✗ Error: {e}")
            return False
        finally:
            await conn.close()
    
    async def main():
        success = await migrate_postgres()
        if success:
            print("\n✓ Migration completed successfully!")
        else:
            print("\n✗ Migration failed!")
            sys.exit(1)


if __name__ == "__main__":
    print("=" * 60)
    print("Database Migration: Add event_type column")
    print("=" * 60)
    print()
    
    asyncio.run(main())

