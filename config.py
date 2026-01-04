"""
Configuration management for Clan Bot
Loads environment variables and provides configuration access.
Supports multi-clan deployments with per-clan configuration.
"""

import json
import logging
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    """Bot configuration from environment variables."""

    # Clan Identity Configuration
    CLAN_NAME = os.getenv("CLAN_NAME", "Clan")  # Default to "Clan" for backward compatibility
    CLAN_CONFIG_DIR = os.getenv("CLAN_CONFIG_DIR")  # Optional: override config directory name
    DATABASE_SCHEMA = os.getenv("DATABASE_SCHEMA")  # Oracle schema name (optional, defaults to ORACLE_USER)
    DATABASE_PATH = os.getenv("DATABASE_PATH", "clan_data.db")  # SQLite database file path
    
    @classmethod
    def get_clan_config_dir(cls) -> str:
        """Get the clan configuration directory name."""
        if cls.CLAN_CONFIG_DIR:
            return cls.CLAN_CONFIG_DIR
        # Normalize CLAN_NAME to directory name: lowercase, replace spaces with underscores
        return cls.CLAN_NAME.lower().replace(" ", "_")

    # Discord Configuration
    DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    GUILD_ID = int(os.getenv("GUILD_ID", 0))

    # Channel Configuration
    ADMIN_CHANNEL_ID = int(os.getenv("ADMIN_CHANNEL_ID", 0))
    LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))

    # Roblox Configuration
    ROBLOX_GROUP_ID = int(os.getenv("ROBLOX_GROUP_ID", 0))
    ROBLOX_API_KEY = os.getenv("ROBLOX_API_KEY")
    ROBLOX_COOKIE = os.getenv("ROBLOX_COOKIE")

    # Role Configuration (by name)
    ADMIN_ROLE_NAME = os.getenv("ADMIN_ROLE_NAME", "Admin")
    MODERATOR_ROLE_NAME = os.getenv("MODERATOR_ROLE_NAME", "Moderator")
    OFFICER_ROLE_NAME = os.getenv("OFFICER_ROLE_NAME", "Officer")
    ELITE_ROLE_NAME = os.getenv("ELITE_ROLE_NAME", "Elite")
    MEMBER_ROLE_NAME = os.getenv("MEMBER_ROLE_NAME", "Member")

    # Role Configuration (by ID) - More reliable than names
    # Leave empty to rely on role names only
    ADMIN_ROLE_ID = int(os.getenv("ADMIN_ROLE_ID", "0")) or None
    MODERATOR_ROLE_ID = int(os.getenv("MODERATOR_ROLE_ID", "0")) or None
    OFFICER_ROLE_ID = int(os.getenv("OFFICER_ROLE_ID", "0")) or None
    ELITE_ROLE_ID = int(os.getenv("ELITE_ROLE_ID", "0")) or None
    MEMBER_ROLE_ID = int(os.getenv("MEMBER_ROLE_ID", "0")) or None

    # Admin User IDs (whitelist) - comma-separated Discord user IDs
    # Example: "123456789012345678,987654321098765432"
    _admin_ids_str = os.getenv("ADMIN_USER_IDS", "")
    ADMIN_USER_IDS = [int(uid.strip()) for uid in _admin_ids_str.split(",") if uid.strip()]

    # Database Configuration
    # Railway/Render automatically sets DATABASE_URL for PostgreSQL
    DATABASE_URL = os.getenv("DATABASE_URL")

    # Oracle Database Configuration
    ORACLE_USER = os.getenv("ORACLE_USER")
    ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD")
    ORACLE_DSN = os.getenv("ORACLE_DSN")
    ORACLE_CONFIG_DIR = os.getenv("ORACLE_CONFIG_DIR")  # Optional: for wallet
    ORACLE_WALLET_LOCATION = os.getenv("ORACLE_WALLET_LOCATION")  # Optional: for Python 3.13+
    ORACLE_WALLET_PASSWORD = os.getenv("ORACLE_WALLET_PASSWORD")  # Optional: for Python 3.13+

    # Database selection logic
    # Priority: Oracle > PostgreSQL > SQLite
    USE_ORACLE = ORACLE_USER is not None and ORACLE_PASSWORD is not None and ORACLE_DSN is not None
    USE_SQLITE = DATABASE_URL is None and not USE_ORACLE

    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    
    # Rate Limiting Configuration
    MAX_RATE_LIMIT_RETRIES = int(
        os.getenv("MAX_RATE_LIMIT_RETRIES", "3")
    )  # Maximum retry attempts for rate limited requests
    RATE_LIMIT_RETRY_DELAY = float(
        os.getenv("RATE_LIMIT_RETRY_DELAY", "1.0")
    )  # Initial delay in seconds before retry

    @classmethod
    def validate(cls):
        """Validate that required configuration is present."""
        errors = []

        if not cls.DISCORD_BOT_TOKEN:
            errors.append("DISCORD_BOT_TOKEN is required")

        if not cls.GUILD_ID:
            errors.append("GUILD_ID is required")

        if not cls.ROBLOX_GROUP_ID:
            errors.append("ROBLOX_GROUP_ID is required")

        if not cls.ROBLOX_API_KEY and not cls.ROBLOX_COOKIE:
            errors.append("Either ROBLOX_API_KEY or ROBLOX_COOKIE is required")

        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))

        return True


def load_ranks_config() -> Optional[List[Dict[str, Any]]]:
    """
    Load rank configuration from JSON file.
    Returns list of rank dictionaries or None if file not found.
    """
    config_dir = Config.get_clan_config_dir()
    ranks_file = Path("configs") / config_dir / "ranks.json"
    
    if not ranks_file.exists():
        logger.warning(f"Ranks config file not found: {ranks_file}. Using default ranks from code.")
        return None
    
    try:
        with open(ranks_file, "r", encoding="utf-8") as f:
            ranks = json.load(f)
            logger.info(f"Loaded {len(ranks)} ranks from {ranks_file}")
            return ranks
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading ranks config from {ranks_file}: {e}")
        return None
