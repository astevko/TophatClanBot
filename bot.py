"""
TophatC Clan Discord Bot
Main bot entry point with Discord client setup and command registration.
"""

import discord
from discord import app_commands
from discord.ext import commands
import logging
import sys

from config import Config

# Import appropriate database module based on configuration
if Config.USE_SQLITE:
    import database
    logger.info("Using SQLite database (local development)")
else:
    import database_postgres as database
    logger.info("Using PostgreSQL database (production)")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log')
    ]
)
logger = logging.getLogger(__name__)


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
            help_command=None
        )
        
        self.guild_id = Config.GUILD_ID
    
    async def setup_hook(self):
        """Called when the bot is starting up."""
        logger.info("Setting up bot...")
        
        # Initialize database
        await database.init_database()
        
        # Load command modules
        await self.load_extension("commands.user_commands")
        await self.load_extension("commands.admin_commands")
        
        # Sync commands with Discord
        if self.guild_id:
            guild = discord.Object(id=self.guild_id)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            logger.info(f"Synced commands to guild {self.guild_id}")
        else:
            await self.tree.sync()
            logger.info("Synced commands globally")
        
        logger.info("Bot setup complete")
    
    async def on_ready(self):
        """Called when the bot is ready."""
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guild(s)")
        
        # Set bot status
        await self.change_presence(
            activity=discord.Game(name="/xp to check your rank")
        )
        
        logger.info("Bot is ready!")
    
    async def on_command_error(self, ctx, error):
        """Global error handler for commands."""
        if isinstance(error, commands.CommandNotFound):
            return
        
        logger.error(f"Command error: {error}", exc_info=error)
        
        if ctx.interaction:
            await ctx.interaction.response.send_message(
                f"An error occurred: {str(error)}",
                ephemeral=True
            )


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
        logger.info("Configuration validated successfully")
        
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
    import asyncio
    asyncio.run(main())

