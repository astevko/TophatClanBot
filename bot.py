"""
TophatC Clan Discord Bot
Main bot entry point with Discord client setup and command registration.
"""

import asyncio
import logging
import sys
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands, tasks

import roblox_api
from config import Config
from security_utils import SanitizingFormatter

# Setup logging first with security sanitization
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler("bot.log")],
)

# Apply sanitizing formatter to all handlers
sanitizing_formatter = SanitizingFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
for handler in logging.getLogger().handlers:
    handler.setFormatter(sanitizing_formatter)

# Suppress Discord HTTP rate limit warnings (they're handled gracefully)
logging.getLogger("discord.http").setLevel(logging.ERROR)

logger = logging.getLogger(__name__)

# Import appropriate database module based on configuration
if Config.USE_SQLITE:
    import database

    logger.info("Using SQLite database (local development)")
else:
    import database_postgres as database

    logger.info("Using PostgreSQL database (production)")


class DiscordHandler(logging.Handler):
    """Custom logging handler that sends logs to a Discord channel."""

    # Class variable to control minimum log level sent to Discord
    # Options: 'NONE', 'CRITICAL', 'ERROR', 'WARNING'
    min_discord_level = "WARNING"

    def __init__(self, bot: Optional["TophatClanBot"] = None, channel_id: Optional[int] = None):
        super().__init__()
        self.bot = bot
        self.channel_id = channel_id or Config.LOG_CHANNEL_ID
        self.log_queue = asyncio.Queue()
        self._task = None

    def emit(self, record: logging.LogRecord):
        """Queue log record to be sent to Discord."""
        try:
            msg = self.format(record)
            # Add to queue for async processing
            if self.bot and self._task:
                asyncio.create_task(self._send_log(msg, record.levelname, record.name))
        except Exception:
            self.handleError(record)

    async def _send_log(self, message: str, level: str, logger_name: str):
        """Send log message to Discord channel."""
        if not self.bot or not self.bot.is_ready():
            return

        try:
            # Check if Discord logging is disabled
            if DiscordHandler.min_discord_level == "NONE":
                return

            # Filter based on minimum log level setting
            # Level hierarchy: DEBUG < INFO < WARNING < ERROR < CRITICAL
            allowed_levels = {
                "CRITICAL": ["CRITICAL"],
                "ERROR": ["ERROR", "CRITICAL"],
                "WARNING": ["WARNING", "ERROR", "CRITICAL"],
            }

            if level not in allowed_levels.get(DiscordHandler.min_discord_level, []):
                return

            # All logs go to the configured log channel
            channel = self.bot.get_channel(self.channel_id)
            if not channel:
                return

            # Color code by log level
            color_map = {
                "INFO": 0x43B581,  # Green
                "WARNING": 0xFAA61A,  # Yellow/Orange
                "ERROR": 0xF04747,  # Red
                "CRITICAL": 0x992D22,  # Dark Red
            }

            # Split message if too long (Discord has 2000 char limit)
            if len(message) > 1900:
                message = message[:1900] + "..."

            embed = discord.Embed(
                description=f"```\n{message}\n```",
                color=color_map.get(level, 0x7289DA),
                timestamp=discord.utils.utcnow(),
            )
            embed.set_footer(text=level)

            await channel.send(embed=embed)

            # Rate limit protection: Discord allows ~5 messages per 5 seconds
            # Use 1.1 second delay to stay well under the limit (max ~4.5 messages per 5 seconds)
            await asyncio.sleep(1.1)

        except discord.errors.HTTPException as e:
            # Handle rate limiting gracefully
            if e.status == 429:
                print("Discord rate limited - skipping log message", file=sys.stderr)
            else:
                print(f"Failed to send log to Discord: {e}", file=sys.stderr)
        except Exception as e:
            # Don't let Discord logging errors break the bot
            print(f"Failed to send log to Discord: {e}", file=sys.stderr)

    def start(self):
        """Start the handler (called when bot is ready)."""
        if not self._task or self._task.done():
            self._task = asyncio.create_task(self._process_queue())

    async def _process_queue(self):
        """Process queued log messages."""
        while True:
            await asyncio.sleep(0.1)


class TophatClanBot(commands.Bot):
    """Custom bot class for TophatC Clan Bot."""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True

        super().__init__(
            command_prefix="!",  # Fallback prefix (we mainly use slash commands)
            intents=intents,
            help_command=None,
        )

        self.guild_id = Config.GUILD_ID

        # Setup Discord logging handler
        # Only send INFO, WARNING, ERROR, and CRITICAL logs to Discord (no DEBUG)
        self.discord_handler = DiscordHandler(bot=self)
        self.discord_handler.setLevel(logging.INFO)  # Minimum level: INFO (excludes DEBUG)
        self.discord_handler.setFormatter(
            SanitizingFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )

    async def setup_hook(self):
        """Called when the bot is starting up."""
        logger.debug("Setting up bot...")

        # Initialize database
        await database.init_database()

        # Verify Roblox API credentials
        logger.debug("Verifying Roblox API credentials...")
        roblox_verified = await roblox_api.verify_roblox_credentials()
        if roblox_verified:
            logger.info("✅ Roblox API credentials verified successfully")
        else:
            logger.warning("⚠️ Roblox API verification failed - some features may not work")

        # Load command modules
        await self.load_extension("commands.user_commands")
        await self.load_extension("commands.admin_commands")

        # Sync commands with Discord
        if self.guild_id:
            guild = discord.Object(id=self.guild_id)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            logger.debug(f"Synced commands to guild {self.guild_id}")
        else:
            await self.tree.sync()
            logger.info("Synced commands globally")

        # Start background tasks
        if not self.auto_sync_ranks.is_running():
            self.auto_sync_ranks.start()
            logger.info("✅ Started automatic rank synchronization task")

        logger.info("Bot setup complete")

    async def on_ready(self):
        """Called when the bot is ready."""
        logger.debug(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.debug(f"Connected to {len(self.guilds)} guild(s)")

        # Set bot status
        await self.change_presence(activity=discord.Game(name="/xp to check your rank"))

        # Enable Discord logging
        self.discord_handler.start()
        logging.getLogger().addHandler(self.discord_handler)

        logger.info("Bot is ready!")
        logger.debug(f"Discord logging enabled to channel {Config.LOG_CHANNEL_ID}")

    async def on_command_error(self, ctx, error):
        """Global error handler for commands."""
        if isinstance(error, commands.CommandNotFound):
            return

        logger.error(f"Command error: {error}", exc_info=error)

        if ctx.interaction:
            await ctx.interaction.response.send_message(
                f"An error occurred: {str(error)}", ephemeral=True
            )

    @tasks.loop(hours=1)
    async def auto_sync_ranks(self):
        """Background task to automatically sync ranks every hour (Roblox is source of truth)."""
        try:
            logger.debug("🔄 Starting automatic rank synchronization...")

            # Get all members from database
            all_members = await self._get_all_members()

            synced = 0
            already_synced = 0
            skipped = 0
            errors = 0

            for member in all_members:
                try:
                    result = await roblox_api.sync_member_rank_from_roblox(member["discord_id"])

                    if not result["success"]:
                        errors += 1
                        continue

                    if result["action"] == "none":
                        already_synced += 1
                        continue

                    if result["action"] == "skipped":
                        skipped += 1
                        continue

                    # Update Discord role if member is in guild
                    for guild in self.guilds:
                        discord_member = guild.get_member(member["discord_id"])
                        if discord_member:
                            await self._update_discord_role(
                                discord_member,
                                result["old_rank"]["rank_order"],
                                result["new_rank"]["rank_order"],
                            )
                            break

                    synced += 1
                    logger.info(
                        f"Auto-synced {member['roblox_username']}: "
                        f"{result['old_rank']['rank_name']} -> {result['new_rank']['rank_name']}"
                    )

                    # Rate limit protection: Add small delay between role updates
                    await asyncio.sleep(0.5)

                except Exception as e:
                    logger.error(f"Error syncing member {member.get('discord_id')}: {e}")
                    errors += 1

            logger.info(
                f"✅ Automatic sync complete: {synced} updated, "
                f"{already_synced} in sync, {skipped} skipped (no matching rank), {errors} errors"
            )

        except Exception as e:
            logger.error(f"Error in automatic rank sync task: {e}")

    @auto_sync_ranks.before_loop
    async def before_auto_sync(self):
        """Wait until bot is ready before starting sync task."""
        await self.wait_until_ready()
        logger.debug("Bot ready, automatic sync task will start soon...")

    async def _get_all_members(self):
        """Get all members from database."""
        async with database.aiosqlite.connect(database.DATABASE_PATH) as db:
            db.row_factory = database.aiosqlite.Row
            async with db.execute("SELECT * FROM members") as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def _update_discord_role(
        self, member: discord.Member, old_rank_order: int, new_rank_order: int
    ):
        """Update member's Discord role when rank changes."""
        try:
            # Get old and new rank info
            old_rank = await database.get_rank_by_order(old_rank_order)
            new_rank = await database.get_rank_by_order(new_rank_order)

            if not old_rank or not new_rank:
                return

            # Remove old rank role with retry logic
            old_role = discord.utils.get(member.guild.roles, name=old_rank["rank_name"])
            if old_role and old_role in member.roles:
                for attempt in range(Config.MAX_RATE_LIMIT_RETRIES):
                    try:
                        await member.remove_roles(old_role)
                        break
                    except discord.HTTPException as e:
                        if e.status == 429 and attempt < Config.MAX_RATE_LIMIT_RETRIES - 1:
                            # Exponential backoff: 1s, 2s, 4s, etc.
                            delay = Config.RATE_LIMIT_RETRY_DELAY * (2**attempt)
                            logger.warning(
                                f"Rate limited when removing role (attempt {attempt + 1}/{Config.MAX_RATE_LIMIT_RETRIES}) - retrying after {delay}s"
                            )
                            await asyncio.sleep(delay)
                        elif e.status == 429:
                            logger.error(
                                f"Failed to remove role after {Config.MAX_RATE_LIMIT_RETRIES} attempts due to rate limiting"
                            )
                            raise
                        else:
                            raise

            # Add new rank role (create if doesn't exist) with retry logic
            new_role = discord.utils.get(member.guild.roles, name=new_rank["rank_name"])
            if not new_role:
                # Create the role if it doesn't exist with retry logic
                for attempt in range(Config.MAX_RATE_LIMIT_RETRIES):
                    try:
                        new_role = await member.guild.create_role(
                            name=new_rank["rank_name"], reason="Clan rank role"
                        )
                        break
                    except discord.HTTPException as e:
                        if e.status == 429 and attempt < Config.MAX_RATE_LIMIT_RETRIES - 1:
                            # Exponential backoff: 1s, 2s, 4s, etc.
                            delay = Config.RATE_LIMIT_RETRY_DELAY * (2**attempt)
                            logger.warning(
                                f"Rate limited when creating role (attempt {attempt + 1}/{Config.MAX_RATE_LIMIT_RETRIES}) - retrying after {delay}s"
                            )
                            await asyncio.sleep(delay)
                        elif e.status == 429:
                            logger.error(
                                f"Failed to create role after {Config.MAX_RATE_LIMIT_RETRIES} attempts due to rate limiting"
                            )
                            raise
                        else:
                            raise

            # Add the role with retry logic
            for attempt in range(Config.MAX_RATE_LIMIT_RETRIES):
                try:
                    await member.add_roles(new_role)
                    break
                except discord.HTTPException as e:
                    if e.status == 429 and attempt < Config.MAX_RATE_LIMIT_RETRIES - 1:
                        # Exponential backoff: 1s, 2s, 4s, etc.
                        delay = Config.RATE_LIMIT_RETRY_DELAY * (2**attempt)
                        logger.warning(
                            f"Rate limited when adding role (attempt {attempt + 1}/{Config.MAX_RATE_LIMIT_RETRIES}) - retrying after {delay}s"
                        )
                        await asyncio.sleep(delay)
                    elif e.status == 429:
                        logger.error(
                            f"Failed to add role after {Config.MAX_RATE_LIMIT_RETRIES} attempts due to rate limiting"
                        )
                        raise
                    else:
                        raise

        except discord.Forbidden:
            logger.error(f"Missing permissions to update roles for {member.name}")
        except Exception as e:
            logger.error(f"Error updating Discord role: {e}")


def is_admin():
    """Check if user has admin permissions."""

    async def predicate(interaction: discord.Interaction) -> bool:
        # Check if user has administrator permission
        if interaction.user.guild_permissions.administrator:
            return True

        # Check if user has the configured admin role
        admin_role = discord.utils.get(interaction.user.roles, name=Config.ADMIN_ROLE_NAME)
        if admin_role:
            return True

        return False

    return app_commands.check(predicate)


async def main():
    """Main entry point for the bot."""
    try:
        # Validate configuration
        Config.validate()
        logger.debug("Configuration validated successfully")

        # Create and run bot
        bot = TophatClanBot()
        async with bot:
            await bot.start(Config.DISCORD_BOT_TOKEN)

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
