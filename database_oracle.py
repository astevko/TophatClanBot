"""
Oracle database adapter for TophatC Clan Bot
Used when deployed to Oracle Cloud Infrastructure
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import oracledb

from config import Config

logger = logging.getLogger(__name__)


# Custom exceptions for better error handling
class DatabaseError(Exception):
    """Base database error."""
    pass


class DatabaseConnectionError(DatabaseError):
    """Database connection failed."""
    pass


class DatabaseValidationError(DatabaseError):
    """Input validation failed."""
    pass

# Global connection pool
_pool = None


async def get_pool():
    """Get or create connection pool."""
    global _pool
    if _pool is None:
        try:
            # Create connection pool
            _pool = oracledb.create_pool(
                user=Config.ORACLE_USER,
                password=Config.ORACLE_PASSWORD,
                dsn=Config.ORACLE_DSN,
                config_dir=Config.ORACLE_CONFIG_DIR,
                wallet_location=Config.ORACLE_WALLET_LOCATION,
                wallet_password=Config.ORACLE_WALLET_PASSWORD,
                min=2,
                max=10,
                increment=1,
            )
            logger.info("Oracle connection pool created")
        except oracledb.Error as e:
            logger.error(f"Failed to create Oracle connection pool: {type(e).__name__}")
            logger.debug(f"Full Oracle connection error details: {e}")
            raise DatabaseConnectionError("Unable to connect to Oracle database")
    return _pool


def _dict_from_row(cursor, row):
    """Convert Oracle row to dictionary using cursor description."""
    if row is None:
        return None
    columns = [col[0].lower() for col in cursor.description]
    return dict(zip(columns, row))


async def init_database():
    """Initialize the database with required tables."""
    pool = await get_pool()
    connection = pool.acquire()

    try:
        cursor = connection.cursor()

        # Members table
        try:
            cursor.execute("""
                CREATE TABLE members (
                    discord_id NUMBER(20) PRIMARY KEY,
                    roblox_username VARCHAR2(100) UNIQUE,
                    current_rank NUMBER(10) DEFAULT 1,
                    points NUMBER(10) DEFAULT 0,
                    created_at TIMESTAMP NOT NULL
                )
            """)
            logger.info("Created members table")
        except oracledb.DatabaseError as e:
            error_obj, = e.args
            if error_obj.code == 955:  # Table already exists
                logger.info("Members table already exists")
            else:
                raise

        # Raid submissions table
        try:
            cursor.execute("""
                CREATE TABLE raid_submissions (
                    submission_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    submitter_id NUMBER(20) NOT NULL,
                    event_type VARCHAR2(50) NOT NULL,
                    participants CLOB NOT NULL,
                    start_time VARCHAR2(50) NOT NULL,
                    end_time VARCHAR2(50) NOT NULL,
                    image_url VARCHAR2(500) NOT NULL,
                    status VARCHAR2(20) DEFAULT 'pending',
                    points_awarded NUMBER(10),
                    admin_id NUMBER(20),
                    timestamp TIMESTAMP NOT NULL
                )
            """)
            logger.info("Created raid_submissions table")
        except oracledb.DatabaseError as e:
            error_obj, = e.args
            if error_obj.code == 955:  # Table already exists
                logger.info("Raid submissions table already exists")
            else:
                raise

        # Rank requirements table
        try:
            cursor.execute("""
                CREATE TABLE rank_requirements (
                    rank_order NUMBER(10) PRIMARY KEY,
                    rank_name VARCHAR2(100) NOT NULL UNIQUE,
                    points_required NUMBER(10) NOT NULL,
                    roblox_group_rank_id NUMBER(10) NOT NULL,
                    admin_only NUMBER(1) DEFAULT 0
                )
            """)
            logger.info("Created rank_requirements table")
        except oracledb.DatabaseError as e:
            error_obj, = e.args
            if error_obj.code == 955:  # Table already exists
                logger.info("Rank requirements table already exists")
            else:
                raise

        # Config table
        try:
            cursor.execute("""
                CREATE TABLE config (
                    key VARCHAR2(100) PRIMARY KEY,
                    value VARCHAR2(1000) NOT NULL
                )
            """)
            logger.info("Created config table")
        except oracledb.DatabaseError as e:
            error_obj, = e.args
            if error_obj.code == 955:  # Table already exists
                logger.info("Config table already exists")
            else:
                raise

        connection.commit()
        logger.info("Oracle database initialized successfully")

        # Insert default ranks
        await insert_default_ranks(connection)

    finally:
        pool.release(connection)


async def insert_default_ranks(connection):
    """Insert default military ranks into the database."""
    default_ranks = [
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

    cursor = connection.cursor()

    for rank_order, rank_name, points_required, roblox_rank_id, admin_only in default_ranks:
        try:
            cursor.execute(
                """
                INSERT INTO rank_requirements
                (rank_order, rank_name, points_required, roblox_group_rank_id, admin_only)
                VALUES (:1, :2, :3, :4, :5)
                """,
                [rank_order, rank_name, points_required, roblox_rank_id, admin_only],
            )
        except oracledb.IntegrityError:
            # Rank already exists, skip
            pass

    connection.commit()
    logger.info("Default ranks inserted")


# ============= MEMBER OPERATIONS =============


async def get_member(discord_id: int) -> Optional[Dict[str, Any]]:
    """Get a member by their Discord ID."""
    pool = await get_pool()
    connection = pool.acquire()

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT m.*, r.rank_name, r.points_required
            FROM members m
            JOIN rank_requirements r ON m.current_rank = r.rank_order
            WHERE m.discord_id = :1
            """,
            [discord_id],
        )
        row = cursor.fetchone()
        return _dict_from_row(cursor, row)
    finally:
        pool.release(connection)


async def get_member_by_roblox(roblox_username: str) -> Optional[Dict[str, Any]]:
    """Get a member by their Roblox username (case-insensitive)."""
    pool = await get_pool()
    connection = pool.acquire()

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT m.*, r.rank_name, r.points_required
            FROM members m
            JOIN rank_requirements r ON m.current_rank = r.rank_order
            WHERE LOWER(m.roblox_username) = LOWER(:1)
            """,
            [roblox_username],
        )
        row = cursor.fetchone()
        return _dict_from_row(cursor, row)
    finally:
        pool.release(connection)


async def create_member(discord_id: int, roblox_username: str) -> bool:
    """Create a new member entry."""
    # Input validation (SECURITY: Added per audit recommendations)
    if not isinstance(discord_id, int) or discord_id <= 0:
        raise DatabaseValidationError("Invalid Discord ID")
    if not roblox_username or not isinstance(roblox_username, str):
        raise DatabaseValidationError("Invalid Roblox username")
    if len(roblox_username) > 100:
        raise DatabaseValidationError("Roblox username too long (max 100 characters)")
    if len(roblox_username.strip()) == 0:
        raise DatabaseValidationError("Roblox username cannot be empty")
    
    try:
        pool = await get_pool()
        connection = pool.acquire()
        
        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO members (discord_id, roblox_username, current_rank, points, created_at)
                VALUES (:1, :2, 1, 0, :3)
                """,
                [discord_id, roblox_username.strip(), datetime.utcnow()],
            )
            connection.commit()
            logger.info(f"Created member: {discord_id}")
            return True
        finally:
            pool.release(connection)
    except oracledb.IntegrityError as e:
        logger.error(f"Failed to create member: {type(e).__name__}")
        logger.debug(f"Full error: {e}")
        return False


async def update_member_roblox(discord_id: int, roblox_username: str) -> bool:
    """Update a member's Roblox username."""
    try:
        pool = await get_pool()
        connection = pool.acquire()

        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                UPDATE members SET roblox_username = :1 WHERE discord_id = :2
                """,
                [roblox_username, discord_id],
            )
            connection.commit()
            logger.info(f"Updated Roblox username for {discord_id}: {roblox_username}")
            return True
        finally:
            pool.release(connection)
    except oracledb.IntegrityError:
        return False


async def add_points(discord_id: int, points: int) -> bool:
    """Add points to a member."""
    pool = await get_pool()
    connection = pool.acquire()

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            UPDATE members SET points = points + :1 WHERE discord_id = :2
            """,
            [points, discord_id],
        )
        connection.commit()
        logger.info(f"Added {points} points to member {discord_id}")
        return True
    finally:
        pool.release(connection)


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
    if current_rank.get("admin_only", 0):
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
    """Set a member's rank."""
    pool = await get_pool()
    connection = pool.acquire()

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            UPDATE members SET current_rank = :1 WHERE discord_id = :2
            """,
            [rank_order, discord_id],
        )
        connection.commit()
        logger.info(f"Updated rank for member {discord_id} to {rank_order}")
        return True
    finally:
        pool.release(connection)


async def get_all_members() -> List[Dict[str, Any]]:
    """Get all members from the database."""
    pool = await get_pool()
    connection = pool.acquire()
    
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT * FROM members ORDER BY discord_id
        """)
        rows = cursor.fetchall()
        return [_dict_from_row(cursor, row) for row in rows]
    finally:
        pool.release(connection)


async def get_leaderboard(limit: int = 10) -> List[Dict[str, Any]]:
    """Get top members by points."""
    pool = await get_pool()
    connection = pool.acquire()
    
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT m.discord_id, m.roblox_username, m.points, r.rank_name
            FROM members m
            JOIN rank_requirements r ON m.current_rank = r.rank_order
            ORDER BY m.points DESC
            FETCH FIRST :1 ROWS ONLY
            """,
            [limit],
        )
        rows = cursor.fetchall()
        return [_dict_from_row(cursor, row) for row in rows]
    finally:
        pool.release(connection)


# ============= RANK OPERATIONS =============


async def get_all_ranks() -> List[Dict[str, Any]]:
    """Get all ranks ordered by rank_order."""
    pool = await get_pool()
    connection = pool.acquire()

    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT * FROM rank_requirements ORDER BY rank_order ASC
        """)
        rows = cursor.fetchall()
        return [_dict_from_row(cursor, row) for row in rows]
    finally:
        pool.release(connection)


async def get_rank_by_order(rank_order: int) -> Optional[Dict[str, Any]]:
    """Get rank information by rank order."""
    pool = await get_pool()
    connection = pool.acquire()

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT * FROM rank_requirements WHERE rank_order = :1
            """,
            [rank_order],
        )
        row = cursor.fetchone()
        return _dict_from_row(cursor, row)
    finally:
        pool.release(connection)


async def get_next_rank(
    current_rank_order: int, include_admin_only: bool = False
) -> Optional[Dict[str, Any]]:
    """Get the next rank after the current one."""
    pool = await get_pool()
    connection = pool.acquire()

    try:
        cursor = connection.cursor()

        if include_admin_only:
            # Include all ranks
            query = """
                SELECT * FROM rank_requirements
                WHERE rank_order > :1
                ORDER BY rank_order ASC
                FETCH FIRST 1 ROWS ONLY
            """
        else:
            # Only point-based ranks
            query = """
                SELECT * FROM rank_requirements
                WHERE rank_order > :1 AND admin_only = 0
                ORDER BY rank_order ASC
                FETCH FIRST 1 ROWS ONLY
            """

        cursor.execute(query, [current_rank_order])
        row = cursor.fetchone()
        return _dict_from_row(cursor, row)
    finally:
        pool.release(connection)


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
    connection = pool.acquire()

    try:
        cursor = connection.cursor()
        # Use RETURNING clause to get the generated ID
        cursor.execute(
            """
            INSERT INTO raid_submissions
            (submitter_id, event_type, participants, start_time, end_time, image_url, status, timestamp)
            VALUES (:1, :2, :3, :4, :5, :6, 'pending', :7)
            RETURNING submission_id INTO :8
            """,
            [
                submitter_id,
                event_type,
                participants,
                start_time,
                end_time,
                image_url,
                datetime.utcnow(),
                cursor.var(oracledb.NUMBER),
            ],
        )
        submission_id = cursor.getvalue(7)
        connection.commit()
        logger.info(f"Created {event_type} submission {submission_id}")
        return int(submission_id)
    finally:
        pool.release(connection)


async def get_raid_submission(submission_id: int) -> Optional[Dict[str, Any]]:
    """Get a raid submission by ID."""
    pool = await get_pool()
    connection = pool.acquire()

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT * FROM raid_submissions WHERE submission_id = :1
            """,
            [submission_id],
        )
        row = cursor.fetchone()
        return _dict_from_row(cursor, row)
    finally:
        pool.release(connection)


async def approve_raid_submission(submission_id: int, admin_id: int, points: int) -> bool:
    """Approve a raid submission and set the points awarded."""
    pool = await get_pool()
    connection = pool.acquire()

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            UPDATE raid_submissions
            SET status = 'approved', admin_id = :1, points_awarded = :2
            WHERE submission_id = :3
            """,
            [admin_id, points, submission_id],
        )
        connection.commit()
        logger.info(f"Approved raid submission {submission_id} with {points} points")
        return True
    finally:
        pool.release(connection)


async def decline_raid_submission(submission_id: int, admin_id: int) -> bool:
    """Decline a raid submission."""
    pool = await get_pool()
    connection = pool.acquire()

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            UPDATE raid_submissions
            SET status = 'declined', admin_id = :1
            WHERE submission_id = :2
            """,
            [admin_id, submission_id],
        )
        connection.commit()
        logger.info(f"Declined raid submission {submission_id}")
        return True
    finally:
        pool.release(connection)


async def get_pending_submissions() -> List[Dict[str, Any]]:
    """Get all pending raid submissions."""
    pool = await get_pool()
    connection = pool.acquire()

    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT * FROM raid_submissions
            WHERE status = 'pending'
            ORDER BY timestamp DESC
        """)
        rows = cursor.fetchall()
        return [_dict_from_row(cursor, row) for row in rows]
    finally:
        pool.release(connection)


# ============= CONFIG OPERATIONS =============


async def get_config(key: str) -> Optional[str]:
    """Get a configuration value."""
    pool = await get_pool()
    connection = pool.acquire()

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT value FROM config WHERE key = :1
            """,
            [key],
        )
        row = cursor.fetchone()
        if row:
            return row[0]
        return None
    finally:
        pool.release(connection)


async def set_config(key: str, value: str) -> bool:
    """Set a configuration value."""
    pool = await get_pool()
    connection = pool.acquire()

    try:
        cursor = connection.cursor()
        # Oracle MERGE statement for UPSERT
        cursor.execute(
            """
            MERGE INTO config c
            USING (SELECT :1 AS key, :2 AS value FROM dual) src
            ON (c.key = src.key)
            WHEN MATCHED THEN
                UPDATE SET c.value = src.value
            WHEN NOT MATCHED THEN
                INSERT (key, value) VALUES (src.key, src.value)
            """,
            [key, value],
        )
        connection.commit()
        logger.info(f"Set config {key} = {value}")
        return True
    finally:
        pool.release(connection)

