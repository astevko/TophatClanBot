#!/usr/bin/env python3
"""
Database Diagnostic Tool
Checks which database the bot is configured to use and verifies its status.
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_database_config():
    """Check which database is configured."""
    print("=" * 60)
    print("DATABASE CONFIGURATION CHECK")
    print("=" * 60)
    
    # Check Oracle configuration
    oracle_user = os.getenv("ORACLE_USER")
    oracle_password = os.getenv("ORACLE_PASSWORD")
    oracle_dsn = os.getenv("ORACLE_DSN")
    oracle_config_dir = os.getenv("ORACLE_CONFIG_DIR")
    
    # Check PostgreSQL configuration
    database_url = os.getenv("DATABASE_URL")
    
    # Determine which database is configured
    use_oracle = oracle_user and oracle_password and oracle_dsn
    use_sqlite = not database_url and not use_oracle
    use_postgres = database_url and not use_oracle
    
    print(f"\n📊 Database Type Detection:")
    print(f"  USE_ORACLE:    {use_oracle}")
    print(f"  USE_POSTGRES:  {use_postgres}")
    print(f"  USE_SQLITE:    {use_sqlite}")
    
    print(f"\n🔧 Configuration Details:")
    print(f"  ORACLE_USER:       {'✓ Set' if oracle_user else '✗ Not set'}")
    print(f"  ORACLE_PASSWORD:   {'✓ Set' if oracle_password else '✗ Not set'}")
    print(f"  ORACLE_DSN:        {'✓ Set' if oracle_dsn else '✗ Not set'}")
    print(f"  ORACLE_CONFIG_DIR: {'✓ Set' if oracle_config_dir else '✗ Not set'}")
    print(f"  DATABASE_URL:      {'✓ Set' if database_url else '✗ Not set'}")
    
    if use_sqlite:
        print(f"\n⚠️  WARNING: Bot is configured to use SQLite (local development mode)")
        print(f"  Database file: tophat_clan.db")
        if os.path.exists("tophat_clan.db"):
            size = os.path.getsize("tophat_clan.db")
            print(f"  File exists: ✓ ({size} bytes)")
        else:
            print(f"  File exists: ✗ (This is the problem!)")
    
    return use_oracle, use_postgres, use_sqlite

async def initialize_sqlite():
    """Initialize SQLite database if it's being used."""
    print("\n" + "=" * 60)
    print("INITIALIZING SQLITE DATABASE")
    print("=" * 60)
    
    import database
    
    try:
        await database.init_database()
        print("\n✅ SQLite database initialized successfully!")
        
        # Verify tables exist
        import aiosqlite
        async with aiosqlite.connect("tophat_clan.db") as db:
            cursor = await db.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tables = await cursor.fetchall()
            print(f"\n📋 Tables created:")
            for table in tables:
                print(f"  - {table[0]}")
        
        return True
    except Exception as e:
        print(f"\n❌ Failed to initialize SQLite database: {e}")
        return False

async def test_oracle_connection():
    """Test Oracle database connection."""
    print("\n" + "=" * 60)
    print("TESTING ORACLE CONNECTION")
    print("=" * 60)
    
    try:
        import database_oracle
        
        # Try to initialize and connect
        await database_oracle.init_database()
        print("\n✅ Oracle database connection successful!")
        return True
        
    except ImportError as e:
        print(f"\n❌ Oracle client not installed: {e}")
        print("   Run: pip install oracledb")
        return False
    except Exception as e:
        print(f"\n❌ Oracle connection failed: {e}")
        return False

async def test_postgres_connection():
    """Test PostgreSQL database connection."""
    print("\n" + "=" * 60)
    print("TESTING POSTGRESQL CONNECTION")
    print("=" * 60)
    
    try:
        import database_postgres
        
        # Try to initialize and connect
        await database_postgres.init_database()
        print("\n✅ PostgreSQL database connection successful!")
        return True
        
    except ImportError as e:
        print(f"\n❌ PostgreSQL client not installed: {e}")
        print("   Run: pip install asyncpg")
        return False
    except Exception as e:
        print(f"\n❌ PostgreSQL connection failed: {e}")
        return False

async def main():
    """Main diagnostic routine."""
    print("\n🔍 TophatC Clan Bot - Database Diagnostic Tool")
    
    # Check configuration
    use_oracle, use_postgres, use_sqlite = check_database_config()
    
    # Test the appropriate database
    success = False
    if use_oracle:
        success = await test_oracle_connection()
    elif use_postgres:
        success = await test_postgres_connection()
    elif use_sqlite:
        success = await initialize_sqlite()
    
    # Print recommendations
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)
    
    if success:
        print("\n✅ Database is working correctly!")
        print("   You can restart the bot now.")
    else:
        print("\n⚠️  Database needs attention!")
        
        if use_sqlite:
            print("\n🔧 For SQLite (local development):")
            print("   1. Make sure the bot has write permissions to the current directory")
            print("   2. Run this script again to initialize the database")
            print("   3. Restart the bot")
        
        if use_oracle:
            print("\n🔧 For Oracle (production):")
            print("   1. Verify ORACLE_USER, ORACLE_PASSWORD, and ORACLE_DSN are set correctly")
            print("   2. Make sure Oracle wallet is in the correct location")
            print("   3. Check network connectivity to Oracle Cloud")
            print("   4. Review ORACLE_DEPLOYMENT_GUIDE.md for setup instructions")
        
        if use_postgres:
            print("\n🔧 For PostgreSQL:")
            print("   1. Verify DATABASE_URL is set correctly")
            print("   2. Check network connectivity to PostgreSQL server")
            print("   3. Ensure asyncpg is installed: pip install asyncpg")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n❌ Diagnostic cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Diagnostic failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

