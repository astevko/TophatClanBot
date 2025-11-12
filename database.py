"""
Database module for TophatC Clan Bot
Handles all SQLite database operations for members, raid submissions, and rank requirements.
"""

import aiosqlite
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)

DATABASE_PATH = "tophat_clan.db"


async def init_database():
    """Initialize the database with required tables."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Members table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS members (
                discord_id INTEGER PRIMARY KEY,
                roblox_username TEXT UNIQUE,
                current_rank INTEGER DEFAULT 1,
                points INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (current_rank) REFERENCES rank_requirements(rank_order)
            )
        """)
        
        # Raid submissions table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS raid_submissions (
                submission_id INTEGER PRIMARY KEY AUTOINCREMENT,
                submitter_id INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                participants TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                image_url TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                points_awarded INTEGER,
                admin_id INTEGER,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (submitter_id) REFERENCES members(discord_id)
            )
        """)
        
        # Rank requirements table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS rank_requirements (
                rank_order INTEGER PRIMARY KEY,
                rank_name TEXT NOT NULL UNIQUE,
                points_required INTEGER NOT NULL,
                roblox_group_rank_id INTEGER NOT NULL,
                admin_only BOOLEAN DEFAULT 0
            )
        """)
        
        # Config table for storing bot configuration
        await db.execute("""
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        
        await db.commit()
        logger.info("Database initialized successfully")
        
        # Insert default ranks if they don't exist
        await insert_default_ranks(db)


async def insert_default_ranks(db):
    """Insert default military ranks into the database."""
    default_ranks = [
        # Point-Based Ranks (can auto-promote based on points)
        (1, "Pending", 0, 1, False),
        (2, "E0 | Enlist", 1, 2, False),
        (3, "E1 | Soldier", 3, 45, False),
        (4, "E2 | Specialist", 1, 46, False),
        (5, "E3 | Lance Corporal", 2, 47, False),
        (6, "E4 | Corporal", 35, 48, False),
        (7, "E5 | Seargeant", 50, 49, False),
        (8, "E6 | Top Seargeant", 80, 50, False),
        (9, "E7 | Lieutenant", 120, 50, False),
        (10, "E8 | Top Lieutenant", 170, 51, False),
        (14, "C0 | Captain", 230, 121, False),
        (15, "C1 | Major", 310, 122, False),
        (16, "C2 | Colonel", 470, 124, False),
        
       
     # Admin-Only Ranks - Honorary
        (11, "Allied Representative", 0, 118, True),
        (12, "Veteran TC", 0, 118, True),
        (13, "Queen TC", 0, 119, True),

        # Admin-Only Ranks - Leadership
        (17, "C3 | General", 0, 129, True),
        (18, "C4 | Conquistador", 0, 130, True),
        (19, "C5 | Chief Conquistador", 0, 149, True),
        (20, "Commander", 0, 150, True),
        (21, "Silver Leader", 0, 252, True),
        (22, "Red Leader", 0, 253, True),
        (23, "Gold Leader", 0, 255, True),
    
        
    ]
    
    for rank_order, rank_name, points_required, roblox_rank_id, admin_only in default_ranks:
        await db.execute("""
            INSERT OR IGNORE INTO rank_requirements 
            (rank_order, rank_name, points_required, roblox_group_rank_id, admin_only)
            VALUES (?, ?, ?, ?, ?)
        """, (rank_order, rank_name, points_required, roblox_rank_id, admin_only))
    
    await db.commit()
    logger.info("Default ranks inserted")


# ============= MEMBER OPERATIONS =============

async def get_member(discord_id: int) -> Optional[Dict[str, Any]]:
    """Get a member by their Discord ID."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT m.*, r.rank_name, r.points_required
            FROM members m
            JOIN rank_requirements r ON m.current_rank = r.rank_order
            WHERE m.discord_id = ?
        """, (discord_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
            return None


async def get_member_by_roblox(roblox_username: str) -> Optional[Dict[str, Any]]:
    """Get a member by their Roblox username (case-insensitive)."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT m.*, r.rank_name, r.points_required
            FROM members m
            JOIN rank_requirements r ON m.current_rank = r.rank_order
            WHERE LOWER(m.roblox_username) = LOWER(?)
        """, (roblox_username,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
            return None


async def create_member(discord_id: int, roblox_username: str) -> bool:
    """Create a new member entry."""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute("""
                INSERT INTO members (discord_id, roblox_username, current_rank, points, created_at)
                VALUES (?, ?, 1, 0, ?)
            """, (discord_id, roblox_username, datetime.utcnow().isoformat()))
            await db.commit()
            logger.info(f"Created member: {discord_id} - {roblox_username}")
            return True
    except aiosqlite.IntegrityError as e:
        logger.error(f"Failed to create member: {e}")
        return False


async def update_member_roblox(discord_id: int, roblox_username: str) -> bool:
    """Update a member's Roblox username."""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute("""
                UPDATE members SET roblox_username = ? WHERE discord_id = ?
            """, (roblox_username, discord_id))
            await db.commit()
            logger.info(f"Updated Roblox username for {discord_id}: {roblox_username}")
            return True
    except aiosqlite.IntegrityError:
        return False


async def add_points(discord_id: int, points: int) -> bool:
    """Add points to a member."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            UPDATE members SET points = points + ? WHERE discord_id = ?
        """, (points, discord_id))
        await db.commit()
        logger.info(f"Added {points} points to member {discord_id}")
        return True


async def set_member_rank(discord_id: int, rank_order: int) -> bool:
    """Set a member's rank."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            UPDATE members SET current_rank = ? WHERE discord_id = ?
        """, (rank_order, discord_id))
        await db.commit()
        logger.info(f"Updated rank for member {discord_id} to {rank_order}")
        return True


async def get_leaderboard(limit: int = 10) -> List[Dict[str, Any]]:
    """Get top members by points."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT m.discord_id, m.roblox_username, m.points, r.rank_name
            FROM members m
            JOIN rank_requirements r ON m.current_rank = r.rank_order
            ORDER BY m.points DESC
            LIMIT ?
        """, (limit,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


# ============= RANK OPERATIONS =============

async def get_all_ranks() -> List[Dict[str, Any]]:
    """Get all ranks ordered by rank_order."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM rank_requirements ORDER BY rank_order ASC
        """) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def get_rank_by_order(rank_order: int) -> Optional[Dict[str, Any]]:
    """Get rank information by rank order."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM rank_requirements WHERE rank_order = ?
        """, (rank_order,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
            return None


async def get_next_rank(current_rank_order: int, include_admin_only: bool = False) -> Optional[Dict[str, Any]]:
    """Get the next rank after the current one."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        if include_admin_only:
            # Include all ranks
            query = """
                SELECT * FROM rank_requirements 
                WHERE rank_order > ?
                ORDER BY rank_order ASC
                LIMIT 1
            """
        else:
            # Only point-based ranks
            query = """
                SELECT * FROM rank_requirements 
                WHERE rank_order > ? AND admin_only = 0
                ORDER BY rank_order ASC
                LIMIT 1
            """
        
        async with db.execute(query, (current_rank_order,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
            return None


# ============= RAID SUBMISSION OPERATIONS =============

async def create_raid_submission(
    submitter_id: int,
    event_type: str,
    participants: str,
    start_time: str,
    end_time: str,
    image_url: str
) -> int:
    """Create a new event submission and return its ID."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO raid_submissions 
            (submitter_id, event_type, participants, start_time, end_time, image_url, status, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, 'pending', ?)
        """, (submitter_id, event_type, participants, start_time, end_time, image_url, datetime.utcnow().isoformat()))
        await db.commit()
        submission_id = cursor.lastrowid
        logger.info(f"Created {event_type} submission {submission_id}")
        return submission_id


async def get_raid_submission(submission_id: int) -> Optional[Dict[str, Any]]:
    """Get a raid submission by ID."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM raid_submissions WHERE submission_id = ?
        """, (submission_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
            return None


async def approve_raid_submission(submission_id: int, admin_id: int, points: int) -> bool:
    """Approve a raid submission and set the points awarded."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            UPDATE raid_submissions 
            SET status = 'approved', admin_id = ?, points_awarded = ?
            WHERE submission_id = ?
        """, (admin_id, points, submission_id))
        await db.commit()
        logger.info(f"Approved raid submission {submission_id} with {points} points")
        return True


async def decline_raid_submission(submission_id: int, admin_id: int) -> bool:
    """Decline a raid submission."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            UPDATE raid_submissions 
            SET status = 'declined', admin_id = ?
            WHERE submission_id = ?
        """, (admin_id, submission_id))
        await db.commit()
        logger.info(f"Declined raid submission {submission_id}")
        return True


async def get_pending_submissions() -> List[Dict[str, Any]]:
    """Get all pending raid submissions."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM raid_submissions 
            WHERE status = 'pending'
            ORDER BY timestamp DESC
        """) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


# ============= CONFIG OPERATIONS =============

async def get_config(key: str) -> Optional[str]:
    """Get a configuration value."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute("""
            SELECT value FROM config WHERE key = ?
        """, (key,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return row[0]
            return None


async def set_config(key: str, value: str) -> bool:
    """Set a configuration value."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)
        """, (key, value))
        await db.commit()
        logger.info(f"Set config {key} = {value}")
        return True

