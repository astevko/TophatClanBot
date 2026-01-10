#!/usr/bin/env python3
"""
Script to populate the Oracle rank_requirements table.

This script:
1. Connects to Oracle database using environment variables
2. Loads rank configuration from JSON file (if available) or uses hardcoded defaults
3. Inserts/updates ranks in the rank_requirements table using MERGE (upsert)
4. Provides detailed output about what it's doing
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

import oracledb
from dotenv import load_dotenv

# Add parent directory to path to import config
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config, load_ranks_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def get_connection():
    """Create a connection to Oracle database."""
    try:
        pool = oracledb.create_pool(
            user=Config.ORACLE_USER,
            password=Config.ORACLE_PASSWORD,
            dsn=Config.ORACLE_DSN,
            config_dir=Config.ORACLE_CONFIG_DIR,
            wallet_location=Config.ORACLE_WALLET_LOCATION,
            wallet_password=Config.ORACLE_WALLET_PASSWORD,
            min=1,
            max=2,
            increment=1,
        )
        logger.info("Oracle connection pool created")
        connection = pool.acquire()
        return connection, pool
    except oracledb.Error as e:
        logger.error(f"Failed to create Oracle connection: {type(e).__name__}")
        logger.error(f"Error details: {e}")
        raise


def get_ranks_data():
    """Get ranks data from JSON config or return hardcoded defaults."""
    ranks_config = load_ranks_config()
    
    if ranks_config:
        logger.info(f"Loaded {len(ranks_config)} ranks from JSON config file")
        # Convert JSON ranks to list of tuples (Oracle uses 0/1 for booleans)
        ranks = [
            (
                rank["rank_order"],
                rank["rank_name"],
                rank["points_required"],
                rank["roblox_group_rank_id"],
                1 if rank["admin_only"] else 0,  # Convert boolean to 0/1 for Oracle
            )
            for rank in ranks_config
        ]
        return ranks
    else:
        logger.info("No JSON config found, using hardcoded default ranks")
        # Fallback to hardcoded default ranks (TophatC format)
        return [
            # Point-Based Ranks (can auto-promote based on points)
            (1, "Pending", 0, 1, 0),
            (2, "E0 | Enlist", 1, 2, 0),
            (3, "E1 | Soldier", 3, 45, 0),
            (4, "E2 | Specialist", 1, 46, 0),
            (5, "E3 | Lance Corporal", 2, 47, 0),
            (6, "E4 | Corporal", 35, 48, 0),
            (7, "E5 | Seargeant", 50, 49, 0),
            (8, "E6 | Top Seargeant", 80, 50, 0),
            (9, "E7 | Lieutenant", 120, 50, 0),
            (10, "E8 | Top Lieutenant", 170, 51, 0),
            # Admin-Only Ranks - Honorary
            (11, "Allied Representative", 0, 118, 1),
            (12, "Veteran TC", 0, 118, 1),
            (13, "Queen TC", 0, 119, 1),
            # Point-Based Ranks (continued)
            (14, "C0 | Captain", 230, 121, 0),
            (15, "C1 | Major", 310, 122, 0),
            (16, "C2 | Colonel", 470, 124, 0),
            # Admin-Only Ranks - Leadership
            (17, "C3 | General", 0, 129, 1),
            (18, "C4 | Conquistador", 0, 130, 1),
            (19, "C5 | Chief Conquistador", 0, 149, 1),
            (20, "Commander", 0, 150, 1),
            (21, "Silver Leader", 0, 252, 1),
            (22, "Red Leader", 0, 253, 1),
            (23, "Gold Leader", 0, 255, 1),
        ]


async def populate_rank_requirements():
    """Populate the rank_requirements table."""
    # Validate Oracle configuration
    if not Config.ORACLE_USER or not Config.ORACLE_PASSWORD or not Config.ORACLE_DSN:
        logger.error("Oracle database configuration is missing!")
        logger.error("Please set ORACLE_USER, ORACLE_PASSWORD, and ORACLE_DSN environment variables")
        return False
    
    logger.info("=" * 60)
    logger.info("Oracle Rank Requirements Population Script")
    logger.info("=" * 60)
    logger.info(f"Oracle User: {Config.ORACLE_USER}")
    logger.info(f"DSN: {Config.ORACLE_DSN[:50]}..." if len(Config.ORACLE_DSN) > 50 else f"DSN: {Config.ORACLE_DSN}")
    logger.info("")
    
    connection = None
    pool = None
    
    try:
        # Get connection
        logger.info("Connecting to Oracle database...")
        connection, pool = get_connection()
        logger.info("✓ Connected successfully")
        logger.info("")
        
        # Get ranks data
        logger.info("Loading ranks data...")
        ranks = get_ranks_data()
        logger.info(f"✓ Loaded {len(ranks)} ranks")
        logger.info("")
        
        # Display ranks that will be inserted
        logger.info("Ranks to be inserted/updated:")
        logger.info("-" * 60)
        for rank_order, rank_name, points_required, roblox_rank_id, admin_only in ranks:
            admin_str = "ADMIN-ONLY" if admin_only else f"{points_required} points"
            logger.info(f"  {rank_order:2d}. {rank_name:30s} | {admin_str:15s} | Roblox ID: {roblox_rank_id}")
        logger.info("-" * 60)
        logger.info("")
        
        # Insert/update ranks using MERGE (upsert)
        logger.info("Inserting/updating ranks in database...")
        cursor = connection.cursor()
        
        success_count = 0
        error_count = 0
        
        for rank_order, rank_name, points_required, roblox_rank_id, admin_only in ranks:
            try:
                # Check if rank already exists
                cursor.execute(
                    "SELECT COUNT(*) FROM rank_requirements WHERE rank_order = :1",
                    [rank_order]
                )
                exists = cursor.fetchone()[0] > 0
                
                # Use MERGE to insert or update
                cursor.execute(
                    """
                    MERGE INTO rank_requirements r
                    USING (SELECT :1 AS rank_order, :2 AS rank_name, :3 AS points_required, 
                                  :4 AS roblox_group_rank_id, :5 AS admin_only FROM dual) src
                    ON (r.rank_order = src.rank_order)
                    WHEN MATCHED THEN
                        UPDATE SET 
                            rank_name = src.rank_name,
                            points_required = src.points_required,
                            roblox_group_rank_id = src.roblox_group_rank_id,
                            admin_only = src.admin_only
                    WHEN NOT MATCHED THEN
                        INSERT (rank_order, rank_name, points_required, roblox_group_rank_id, admin_only, discord_role_id)
                        VALUES (src.rank_order, src.rank_name, src.points_required, 
                                src.roblox_group_rank_id, src.admin_only, NULL)
                    """,
                    [rank_order, rank_name, points_required, roblox_rank_id, admin_only],
                )
                
                action = "Updated" if exists else "Inserted"
                success_count += 1
                logger.info(f"  ✓ {action}: {rank_name} (order {rank_order})")
                    
            except oracledb.DatabaseError as e:
                error_obj, = e.args
                error_count += 1
                logger.error(f"  ✗ Failed to insert/update {rank_name} (order {rank_order}): {error_obj.message}")
        
        # Commit changes
        connection.commit()
        logger.info("")
        logger.info("=" * 60)
        logger.info("Summary:")
        logger.info(f"  Total ranks processed: {len(ranks)}")
        logger.info(f"  Successfully inserted/updated: {success_count}")
        logger.info(f"  Errors: {error_count}")
        logger.info("=" * 60)
        
        # Verify by counting rows
        cursor.execute("SELECT COUNT(*) FROM rank_requirements")
        total_count = cursor.fetchone()[0]
        logger.info(f"Total ranks in database: {total_count}")
        logger.info("")
        
        if error_count == 0:
            logger.info("✓ Script completed successfully!")
            return True
        else:
            logger.warning(f"⚠ Script completed with {error_count} error(s)")
            return False
            
    except Exception as e:
        logger.error(f"Fatal error: {type(e).__name__}: {e}")
        if connection:
            connection.rollback()
        return False
        
    finally:
        if connection and pool:
            pool.release(connection)
            pool.close()
            logger.info("Connection closed")


async def main():
    """Main entry point."""
    try:
        success = await populate_rank_requirements()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\nScript interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

