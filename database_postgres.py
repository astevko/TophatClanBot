"""
PostgreSQL database adapter for TophatC Clan Bot
Used when deployed to cloud platforms (Railway, Render, etc.)
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import asyncpg

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
                total_points INTEGER DEFAULT 0,
                created_at TIMESTAMP NOT NULL
            )
        """)
        
        # Migration: Add total_points column if it doesn't exist (for existing databases)
        try:
            await conn.execute("""
                ALTER TABLE members ADD COLUMN IF NOT EXISTS total_points INTEGER DEFAULT 0
            """)
            # Set total_points = points for existing members
            await conn.execute("""
                UPDATE members SET total_points = points WHERE total_points = 0
            """)
            logger.info("Migrated existing members: set total_points = points")
        except Exception as e:
            # Column might already exist, skip migration
            logger.debug(f"Migration check: {e}")

        # Raid submissions table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS raid_submissions (
                submission_id SERIAL PRIMARY KEY,
                submitter_id BIGINT NOT NULL,
                event_type TEXT NOT NULL,
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
                admin_only BOOLEAN DEFAULT FALSE,
                discord_role_id BIGINT
            )
        """)
        
        # Migration: Add discord_role_id column if it doesn't exist
        try:
            await conn.execute("""
                ALTER TABLE rank_requirements ADD COLUMN IF NOT EXISTS discord_role_id BIGINT
            """)
            logger.info("Added discord_role_id column to rank_requirements table")
        except Exception as e:
            # Column might already exist, skip migration
            logger.debug(f"Migration check: {e}")

        # Config table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)

        # Blacklist table for blocking users from commands
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS blacklist (
                discord_id BIGINT PRIMARY KEY,
                reason TEXT,
                blacklisted_at TIMESTAMP NOT NULL,
                blacklisted_by BIGINT
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
            (rank_order, rank_name, points_required, roblox_group_rank_id, admin_only, discord_role_id)
            VALUES ($1, $2, $3, $4, $5, NULL)
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


async def get_member_by_roblox(roblox_username: str) -> Optional[Dict[str, Any]]:
    """Get a member by their Roblox username (case-insensitive)."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT m.*, r.rank_name, r.points_required
            FROM members m
            JOIN rank_requirements r ON m.current_rank = r.rank_order
            WHERE LOWER(m.roblox_username) = LOWER($1)
        """,
            roblox_username,
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
                INSERT INTO members (discord_id, roblox_username, current_rank, points, total_points, created_at)
                VALUES ($1, $2, 1, 0, 0, $3)
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
            UPDATE members SET points = points + $1, total_points = total_points + $2 WHERE discord_id = $3
        """,
            points,
            points,
            discord_id,
        )
        logger.info(f"Added {points} points to member {discord_id}")
        return True


async def check_promotion_eligibility(discord_id: int) -> Optional[Dict[str, Any]]:
    """Check if a member is eligible for promotion. Returns next rank info if eligible, None otherwise."""
    member = await get_member(discord_id)
    if not member:
        return None

    # Get current rank info
    current_rank = await get_rank_by_order(member["current_rank"])
    if not current_rank:
        return None

    # Skip if current rank is admin-only (can't auto-promote from admin ranks)
    if current_rank.get("admin_only", False):
        return None

    # Get next point-based rank
    next_rank = await get_next_rank(member["current_rank"], include_admin_only=False)
    if not next_rank:
        return None  # Already at max rank

    # Check if they have enough points
    if member["points"] >= next_rank["points_required"]:
        return {
            "member": member,
            "current_rank": current_rank,
            "next_rank": next_rank,
            "eligible": True,
        }

    return None


async def set_member_rank(discord_id: int, rank_order: int) -> bool:
    """Set a member's rank. Resets points to 0 on promotion."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE members SET current_rank = $1, points = 0 WHERE discord_id = $2
        """,
            rank_order,
            discord_id,
        )
        logger.info(f"Updated rank for member {discord_id} to {rank_order} (points reset to 0)")
        return True


async def get_all_members() -> List[Dict[str, Any]]:
    """Get all members from the database."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT * FROM members ORDER BY discord_id
        """)
        return [dict(row) for row in rows]


async def get_leaderboard(limit: int = 10) -> List[Dict[str, Any]]:
    """Get top members by total points (lifetime points)."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT m.discord_id, m.roblox_username, m.total_points AS points, r.rank_name
            FROM members m
            JOIN rank_requirements r ON m.current_rank = r.rank_order
            ORDER BY m.total_points DESC
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


async def set_rank_discord_role_id(rank_order: int, discord_role_id: Optional[int]) -> bool:
    """Update the Discord role ID for a rank."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE rank_requirements SET discord_role_id = $1 WHERE rank_order = $2
        """,
            discord_role_id,
            rank_order,
        )
        logger.info(f"Updated Discord role ID for rank {rank_order} to {discord_role_id}")
        return True


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
    submitter_id: int,
    event_type: str,
    participants: str,
    start_time: str,
    end_time: str,
    image_url: str,
) -> int:
    """Create a new event submission and return its ID."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        submission_id = await conn.fetchval(
            """
            INSERT INTO raid_submissions
            (submitter_id, event_type, participants, start_time, end_time, image_url, status, timestamp)
            VALUES ($1, $2, $3, $4, $5, $6, 'pending', $7)
            RETURNING submission_id
        """,
            submitter_id,
            event_type,
            participants,
            start_time,
            end_time,
            image_url,
            datetime.utcnow(),
        )
        logger.info(f"Created {event_type} submission {submission_id}")
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


# ============= BLACKLIST OPERATIONS =============


async def is_blacklisted(discord_id: int) -> bool:
    """Check if a user is blacklisted."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT discord_id FROM blacklist WHERE discord_id = $1
        """,
            discord_id,
        )
        return row is not None


async def add_to_blacklist(discord_id: int, reason: Optional[str] = None, blacklisted_by: Optional[int] = None) -> bool:
    """Add a user to the blacklist."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO blacklist (discord_id, reason, blacklisted_at, blacklisted_by)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (discord_id) DO UPDATE SET reason = $2, blacklisted_at = $3, blacklisted_by = $4
        """,
            discord_id,
            reason,
            datetime.utcnow(),
            blacklisted_by,
        )
        logger.info(f"Added {discord_id} to blacklist (reason: {reason})")
        return True


async def remove_from_blacklist(discord_id: int) -> bool:
    """Remove a user from the blacklist."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute(
            """
            DELETE FROM blacklist WHERE discord_id = $1
        """,
            discord_id,
        )
        if result == "DELETE 1":
            logger.info(f"Removed {discord_id} from blacklist")
            return True
        return False


async def get_blacklist() -> List[Dict[str, Any]]:
    """Get all blacklisted users."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT discord_id, reason, blacklisted_at, blacklisted_by
            FROM blacklist
            ORDER BY blacklisted_at DESC
        """
        )
        return [dict(row) for row in rows]
