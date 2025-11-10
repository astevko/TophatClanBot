"""
Configuration management for TophatC Clan Bot
Loads environment variables and provides configuration access.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Bot configuration from environment variables."""
    
    # Discord Configuration
    DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    GUILD_ID = int(os.getenv("GUILD_ID", 0))
    
    # Admin Channel Configuration
    ADMIN_CHANNEL_ID = int(os.getenv("ADMIN_CHANNEL_ID", 0))
    
    # Roblox Configuration
    ROBLOX_GROUP_ID = int(os.getenv("ROBLOX_GROUP_ID", 0))
    ROBLOX_API_KEY = os.getenv("ROBLOX_API_KEY")
    ROBLOX_COOKIE = os.getenv("ROBLOX_COOKIE")
    
    # Admin Role Configuration
    ADMIN_ROLE_NAME = os.getenv("ADMIN_ROLE_NAME", "Admin")
    
    # Admin User IDs (whitelist) - comma-separated Discord user IDs
    # Example: "123456789012345678,987654321098765432"
    _admin_ids_str = os.getenv("ADMIN_USER_IDS", "")
    ADMIN_USER_IDS = [int(uid.strip()) for uid in _admin_ids_str.split(",") if uid.strip()]
    
    # Database Configuration
    # Railway/Render automatically sets DATABASE_URL for PostgreSQL
    DATABASE_URL = os.getenv("DATABASE_URL")
    # If no DATABASE_URL, use SQLite (local development)
    USE_SQLITE = DATABASE_URL is None
    
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

