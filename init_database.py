#!/usr/bin/env python3
"""
Quick Database Initialization Script
Initializes the database based on current configuration.
"""

import asyncio
import logging
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

async def main():
    """Initialize the database."""
    try:
        # Import config to determine which database to use
        from config import Config
        
        print("\n" + "=" * 60)
        print("DATABASE INITIALIZATION")
        print("=" * 60)
        
        # Determine which database module to use
        if Config.USE_ORACLE:
            print("\n📊 Using Oracle Database")
            print(f"   User: {Config.ORACLE_USER}")
            print(f"   DSN: {Config.ORACLE_DSN[:50]}...")
            import database_oracle as database
            
        elif Config.USE_SQLITE:
            print("\n📊 Using SQLite Database")
            print(f"   File: tophat_clan.db")
            import database
            
        else:
            print("\n📊 Using PostgreSQL Database")
            print(f"   URL: {Config.DATABASE_URL[:50]}...")
            import database_postgres as database
        
        # Initialize the database
        print("\n🔧 Initializing database tables...")
        await database.init_database()
        
        print("\n✅ Database initialized successfully!")
        print("\nYou can now restart the bot.")
        
        # If SQLite, show some stats
        if Config.USE_SQLITE:
            import os
            if os.path.exists("tophat_clan.db"):
                size = os.path.getsize("tophat_clan.db")
                print(f"\n📈 Database file size: {size:,} bytes")
        
        print("\n" + "=" * 60)
        
    except ImportError as e:
        logger.error(f"Failed to import database module: {e}")
        print("\n❌ Error: Required database module not found")
        
        if "oracledb" in str(e):
            print("   Install Oracle client: pip install oracledb")
        elif "asyncpg" in str(e):
            print("   Install PostgreSQL client: pip install asyncpg")
        
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        print("\nPlease check:")
        print("  1. Database credentials in .env file")
        print("  2. Network connectivity to database server")
        print("  3. Database server is running")
        print("  4. Bot has permissions to create tables")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n❌ Initialization cancelled by user")
        sys.exit(1)

