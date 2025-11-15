"""
PostgreSQL database adapter for TophatC Clan Bot
Used when deployed to cloud platforms (Railway, Render, etc.)
"""

import asyncpg
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from config import Config

logger = logging.getLogger(__name__)


async def get_pool():
    """Get or create connection pool."""
    if not hasattr(get_pool, "pool") or get_pool.pool is None:
        get_pool.pool = await asyncpg.create_pool(Config.DATABASE_URL, min_size=2, max_size=10)
        logger.info("PostgreSQL connection pool created")
    return get_pool.pool


async def init_database():
    """Initialize the database with required tables."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        # Members table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS members (
                discord_id BIGINT PRIMARY KEY,
                roblox_username TEXT UNIQUE,
                current_rank INTEGER DEFAULT 1,
                points INTEGER DEFAULT 0,
                created_at TIMESTAMP NOT NULL
            )
        """)

        # Raid submissions table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS raid_submissions (
                submission_id SERIAL PRIMARY KEY,
                submitter_id BIGINT NOT NULL,
                participants TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                image_url TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                points_awarded INTEGER,
                admin_id BIGINT,
                timestamp TIMESTAMP NOT NULL
            )
        """)

        # Rank requirements table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS rank_requirements (
                rank_order INTEGER PRIMARY KEY,
                rank_name TEXT NOT NULL UNIQUE,
                points_required INTEGER NOT NULL,
                roblox_group_rank_id INTEGER NOT NULL,
                admin_only BOOLEAN DEFAULT FALSE
            )
        """)

        # Config table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)

        logger.info("PostgreSQL database initialized successfully")

        # Insert default ranks
        await insert_default_ranks(conn)


async def insert_default_ranks(conn):
    """Insert default military ranks into the database."""
    default_ranks = [
        # Point-Based Ranks (can auto-promote based on points)
        (1, "Private", 0, 1, False),
        (2, "Corporal", 30, 2, False),
        (3, "Sergeant", 60, 3, False),
        (4, "Staff Sergeant", 100, 4, False),
        (5, "Lieutenant", 150, 5, False),
        (6, "Captain", 210, 6, False),
        (7, "Major", 280, 7, False),
        (8, "Colonel", 360, 8, False),
        (9, "General", 450, 9, False),
        # Admin-Only Ranks - Leadership
        (10, "Officer Cadet", 0, 10, True),
        (11, "Junior Officer", 0, 11, True),
        (12, "Senior Officer", 0, 12, True),
        (13, "Commander", 0, 13, True),
        (14, "High Commander", 0, 14, True),
        # Admin-Only Ranks - Honorary
        (15, "Veteran", 0, 15, True),
        (16, "Elite Guard", 0, 16, True),
        (17, "Legend", 0, 17, True),
        (18, "Hall of Fame", 0, 18, True),
        # Admin-Only Ranks - Trial/Probation
        (19, "Recruit", 0, 19, True),
        (20, "Probation", 0, 20, True),
    ]

    for rank_order, rank_name, points_required, roblox_rank_id, admin_only in default_ranks:
        await conn.execute(
            """
            INSERT INTO rank_requirements 
            (rank_order, rank_name, points_required, roblox_group_rank_id, admin_only)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (rank_order) DO NOTHING
        """,
            rank_order,
            rank_name,
            points_required,
            roblox_rank_id,
            admin_only,
        )

    logger.info("Default ranks inserted")


# ============= MEMBER OPERATIONS =============


async def get_member(discord_id: int) -> Optional[Dict[str, Any]]:
    """Get a member by their Discord ID."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT m.*, r.rank_name, r.points_required
            FROM members m
            JOIN rank_requirements r ON m.current_rank = r.rank_order
            WHERE m.discord_id = $1
        """,
            discord_id,
        )
        if row:
            return dict(row)
        return None


async def create_member(discord_id: int, roblox_username: str) -> bool:
    """Create a new member entry."""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO members (discord_id, roblox_username, current_rank, points, created_at)
                VALUES ($1, $2, 1, 0, $3)
            """,
                discord_id,
                roblox_username,
                datetime.utcnow(),
            )
            logger.info(f"Created member: {discord_id} - {roblox_username}")
            return True
    except asyncpg.UniqueViolationError as e:
        logger.error(f"Failed to create member: {e}")
        return False


async def update_member_roblox(discord_id: int, roblox_username: str) -> bool:
    """Update a member's Roblox username."""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE members SET roblox_username = $1 WHERE discord_id = $2
            """,
                roblox_username,
                discord_id,
            )
            logger.info(f"Updated Roblox username for {discord_id}: {roblox_username}")
            return True
    except asyncpg.UniqueViolationError:
        return False


async def add_points(discord_id: int, points: int) -> bool:
    """Add points to a member."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE members SET points = points + $1 WHERE discord_id = $2
        """,
            points,
            discord_id,
        )
        logger.info(f"Added {points} points to member {discord_id}")
        return True


async def set_member_rank(discord_id: int, rank_order: int) -> bool:
    """Set a member's rank."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE members SET current_rank = $1 WHERE discord_id = $2
        """,
            rank_order,
            discord_id,
        )
        logger.info(f"Updated rank for member {discord_id} to {rank_order}")
        return True


async def get_leaderboard(limit: int = 10) -> List[Dict[str, Any]]:
    """Get top members by points."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT m.discord_id, m.roblox_username, m.points, r.rank_name
            FROM members m
            JOIN rank_requirements r ON m.current_rank = r.rank_order
            ORDER BY m.points DESC
            LIMIT $1
        """,
            limit,
        )
        return [dict(row) for row in rows]


# ============= RANK OPERATIONS =============


async def get_all_ranks() -> List[Dict[str, Any]]:
    """Get all ranks ordered by rank_order."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT * FROM rank_requirements ORDER BY rank_order ASC
        """)
        return [dict(row) for row in rows]


async def get_rank_by_order(rank_order: int) -> Optional[Dict[str, Any]]:
    """Get rank information by rank order."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT * FROM rank_requirements WHERE rank_order = $1
        """,
            rank_order,
        )
        if row:
            return dict(row)
        return None


async def get_next_rank(
    current_rank_order: int, include_admin_only: bool = False
) -> Optional[Dict[str, Any]]:
    """Get the next rank after the current one."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        if include_admin_only:
            # Include all ranks
            query = """
                SELECT * FROM rank_requirements 
                WHERE rank_order > $1
                ORDER BY rank_order ASC
                LIMIT 1
            """
        else:
            # Only point-based ranks
            query = """
                SELECT * FROM rank_requirements 
                WHERE rank_order > $1 AND admin_only = FALSE
                ORDER BY rank_order ASC
                LIMIT 1
            """

        row = await conn.fetchrow(query, current_rank_order)
        if row:
            return dict(row)
        return None


# ============= RAID SUBMISSION OPERATIONS =============


async def create_raid_submission(
    submitter_id: int, participants: str, start_time: str, end_time: str, image_url: str
) -> int:
    """Create a new raid submission and return its ID."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        submission_id = await conn.fetchval(
            """
            INSERT INTO raid_submissions 
            (submitter_id, participants, start_time, end_time, image_url, status, timestamp)
            VALUES ($1, $2, $3, $4, $5, 'pending', $6)
            RETURNING submission_id
        """,
            submitter_id,
            participants,
            start_time,
            end_time,
            image_url,
            datetime.utcnow(),
        )
        logger.info(f"Created raid submission {submission_id}")
        return submission_id


async def get_raid_submission(submission_id: int) -> Optional[Dict[str, Any]]:
    """Get a raid submission by ID."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT * FROM raid_submissions WHERE submission_id = $1
        """,
            submission_id,
        )
        if row:
            return dict(row)
        return None


async def approve_raid_submission(submission_id: int, admin_id: int, points: int) -> bool:
    """Approve a raid submission and set the points awarded."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE raid_submissions 
            SET status = 'approved', admin_id = $1, points_awarded = $2
            WHERE submission_id = $3
        """,
            admin_id,
            points,
            submission_id,
        )
        logger.info(f"Approved raid submission {submission_id} with {points} points")
        return True


async def decline_raid_submission(submission_id: int, admin_id: int) -> bool:
    """Decline a raid submission."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE raid_submissions 
            SET status = 'declined', admin_id = $1
            WHERE submission_id = $2
        """,
            admin_id,
            submission_id,
        )
        logger.info(f"Declined raid submission {submission_id}")
        return True


async def get_pending_submissions() -> List[Dict[str, Any]]:
    """Get all pending raid submissions."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT * FROM raid_submissions 
            WHERE status = 'pending'
            ORDER BY timestamp DESC
        """)
        return [dict(row) for row in rows]


# ============= CONFIG OPERATIONS =============


async def get_config(key: str) -> Optional[str]:
    """Get a configuration value."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT value FROM config WHERE key = $1
        """,
            key,
        )
        if row:
            return row["value"]
        return None


async def set_config(key: str, value: str) -> bool:
    """Set a configuration value."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO config (key, value) VALUES ($1, $2)
            ON CONFLICT (key) DO UPDATE SET value = $2
        """,
            key,
            value,
        )
        logger.info(f"Set config {key} = {value}")
        return True
