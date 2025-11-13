"""
Security utilities for TophatC Clan Bot
Includes logging sanitization, input validation, and error handling.
"""

import re
import logging
from typing import Optional
from datetime import datetime, timedelta


class SanitizingFormatter(logging.Formatter):
    """Custom formatter that redacts sensitive information from logs."""
    
    # Patterns to redact from logs
    REDACT_PATTERNS = [
        (r'\.ROBLOSECURITY[=:][^\s,}\]]*', '.ROBLOSECURITY=<REDACTED>'),
        (r'x-api-key[=:][^\s,}\]]*', 'x-api-key: <REDACTED>'),
        (r'Cookie[=:][^\s,}\]]*', 'Cookie: <REDACTED>'),
        (r'Authorization[=:][^\s,}\]]*', 'Authorization: <REDACTED>'),
        (r'DISCORD_BOT_TOKEN[=:][^\s,}\]]*', 'DISCORD_BOT_TOKEN=<REDACTED>'),
        (r'ROBLOX_COOKIE[=:][^\s,}\]]*', 'ROBLOX_COOKIE=<REDACTED>'),
        (r'ROBLOX_API_KEY[=:][^\s,}\]]*', 'ROBLOX_API_KEY=<REDACTED>'),
    ]
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with sensitive data redacted."""
        message = super().format(record)
        
        # Redact sensitive patterns
        for pattern, replacement in self.REDACT_PATTERNS:
            message = re.sub(pattern, replacement, message, flags=re.IGNORECASE)
        
        return message


class CooldownManager:
    """Manages command cooldowns to prevent spam and abuse."""
    
    def __init__(self):
        self.cooldowns = {}
        self._cleanup_interval = timedelta(hours=1)
        self._last_cleanup = datetime.utcnow()
    
    def check_cooldown(self, user_id: int, command: str, seconds: int) -> tuple[bool, Optional[int]]:
        """
        Check if user is on cooldown for a command.
        
        Args:
            user_id: Discord user ID
            command: Command name
            seconds: Cooldown duration in seconds
        
        Returns:
            Tuple of (can_execute: bool, remaining_seconds: Optional[int])
        """
        self._cleanup_old_cooldowns()
        
        key = f"{user_id}:{command}"
        now = datetime.utcnow()
        
        if key in self.cooldowns:
            if now < self.cooldowns[key]:
                remaining = int((self.cooldowns[key] - now).total_seconds())
                return False, remaining
        
        self.cooldowns[key] = now + timedelta(seconds=seconds)
        return True, None
    
    def reset_cooldown(self, user_id: int, command: str):
        """Reset cooldown for a specific user and command."""
        key = f"{user_id}:{command}"
        if key in self.cooldowns:
            del self.cooldowns[key]
    
    def _cleanup_old_cooldowns(self):
        """Remove expired cooldowns to prevent memory buildup."""
        now = datetime.utcnow()
        
        # Only cleanup periodically
        if now - self._last_cleanup < self._cleanup_interval:
            return
        
        expired_keys = [
            key for key, expiry in self.cooldowns.items()
            if now >= expiry
        ]
        
        for key in expired_keys:
            del self.cooldowns[key]
        
        self._last_cleanup = now


def sanitize_embed_text(text: str, max_length: int = 1024) -> str:
    """
    Sanitize user input for Discord embeds.
    Prevents markdown injection and limits length.
    
    Args:
        text: User input text
        max_length: Maximum allowed length
    
    Returns:
        Sanitized text safe for Discord embeds
    """
    if not text:
        return ""
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Escape Discord markdown characters to prevent injection
    markdown_chars = ['`', '*', '_', '~', '|', '>', '#']
    for char in markdown_chars:
        text = text.replace(char, f'\\{char}')
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length - 3] + "..."
    
    return text


def validate_image_attachment(attachment, max_size_mb: int = 10) -> tuple[bool, Optional[str]]:
    """
    Validate image attachment for security.
    
    Args:
        attachment: Discord attachment object
        max_size_mb: Maximum file size in megabytes
    
    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
    """
    # Check if it's an image
    if not attachment.content_type or not attachment.content_type.startswith('image/'):
        return False, "❌ Please attach a valid image file as proof."
    
    # Check file size
    max_size_bytes = max_size_mb * 1024 * 1024
    if attachment.size > max_size_bytes:
        return False, f"❌ Image is too large. Maximum size is {max_size_mb} MB."
    
    # Check for suspicious file extensions in filename
    suspicious_extensions = ['.exe', '.bat', '.cmd', '.ps1', '.sh', '.dll']
    filename_lower = attachment.filename.lower()
    for ext in suspicious_extensions:
        if ext in filename_lower:
            return False, "❌ Suspicious file type detected."
    
    return True, None


# Error codes for better error tracking
ERROR_CODES = {
    # User commands
    'XP_GENERAL': 'XP001',
    'XP_NOT_REGISTERED': 'XP002',
    'XP_SYNC_FAILED': 'XP003',
    
    'LINK_ROBLOX_GENERAL': 'LR001',
    'LINK_ROBLOX_NOT_FOUND': 'LR002',
    'LINK_ROBLOX_NOT_MEMBER': 'LR003',
    'LINK_ROBLOX_RANK_FAILED': 'LR004',
    'LINK_ROBLOX_DUPLICATE': 'LR005',
    
    'SUBMIT_RAID_GENERAL': 'SR001',
    'SUBMIT_RAID_NOT_REGISTERED': 'SR002',
    'SUBMIT_RAID_INVALID_IMAGE': 'SR003',
    'SUBMIT_RAID_NO_ADMIN_CHANNEL': 'SR004',
    
    'LEADERBOARD_GENERAL': 'LB001',
    
    # Admin commands
    'PROMOTE_GENERAL': 'PR001',
    'PROMOTE_NOT_FOUND': 'PR002',
    'PROMOTE_ROBLOX_FAILED': 'PR003',
    
    'ADD_POINTS_GENERAL': 'AP001',
    'REMOVE_POINTS_GENERAL': 'RP001',
    
    # Database errors
    'DATABASE_ERROR': 'DB001',
    'DATABASE_NOT_FOUND': 'DB002',
    
    # API errors
    'ROBLOX_API_ERROR': 'RX001',
    'DISCORD_API_ERROR': 'DC001',
}


def get_user_error_message(error_code: str, details: str = "") -> str:
    """
    Generate a user-friendly error message with error code.
    
    Args:
        error_code: Error code from ERROR_CODES
        details: Optional additional details for the user
    
    Returns:
        Formatted error message
    """
    message = "❌ An error occurred. Please try again later."
    
    if details:
        message = f"❌ {details}"
    
    message += f"\n\n*Error Code: {error_code}*"
    message += "\n*If this persists, please contact an administrator with this error code.*"
    
    return message


def check_admin_permissions(interaction) -> bool:
    """
    Centralized admin permission check.
    
    Args:
        interaction: Discord interaction object
    
    Returns:
        True if user has admin permissions, False otherwise
    """
    from config import Config
    import discord
    
    # Method 1: Discord administrator permission
    if interaction.user.guild_permissions.administrator:
        return True
    
    # Method 2: Admin user ID whitelist
    if interaction.user.id in Config.ADMIN_USER_IDS:
        return True
    
    # Method 3: Admin role by ID (more reliable)
    if Config.ADMIN_ROLE_ID:
        admin_role = discord.utils.get(interaction.user.roles, id=Config.ADMIN_ROLE_ID)
        if admin_role:
            return True
    
    # Method 4: Admin role by name (fallback)
    admin_role = discord.utils.get(interaction.user.roles, name=Config.ADMIN_ROLE_NAME)
    if admin_role:
        return True
    
    return False


# Global cooldown manager instance
cooldown_manager = CooldownManager()

