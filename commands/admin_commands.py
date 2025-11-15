"""
Admin commands for TophatC Clan Bot
Commands restricted to administrators for managing the clan.
"""
import asyncio
import logging
from typing import Optional, List, Dict, Any

import discord
from discord import app_commands
from discord.ext import commands

import database
import roblox_api
from config import Config

logger = logging.getLogger(__name__)


def is_admin():
    """Check if user has High Command permissions."""

    async def predicate(interaction: discord.Interaction) -> bool:
        user_id = interaction.user.id

        # Method 1: Check if user ID is in whitelist
        if Config.ADMIN_USER_IDS and user_id in Config.ADMIN_USER_IDS:
            return True

        # Method 2: Check if user has Discord administrator permission
        if interaction.user.guild_permissions.administrator:
            return True

        # Method 3: Check if user has the configured admin role (by ID or name)
        if Config.ADMIN_ROLE_ID:
            admin_role = discord.utils.get(interaction.user.roles, id=Config.ADMIN_ROLE_ID)
            if admin_role:
                return True

        admin_role = discord.utils.get(interaction.user.roles, name=Config.ADMIN_ROLE_NAME)
        if admin_role:
            return True

        # Access denied
        return False

    return app_commands.check(predicate)


def has_role(role_name: str = None, role_id: int = None):
    """Check if user has a specific role by name or ID.

    Args:
        role_name: Role name to check (optional)
        role_id: Role ID to check (optional)

    Note: At least one parameter must be provided.
    """

    async def predicate(interaction: discord.Interaction) -> bool:
        if not role_name and not role_id:
            raise ValueError("Either role_name or role_id must be provided")

        # Check by ID first (more reliable)
        if role_id:
            role = discord.utils.get(interaction.user.roles, id=role_id)
            if role:
                return True

        # Fallback to name
        if role_name:
            role = discord.utils.get(interaction.user.roles, name=role_name)
            if role:
                return True

        return False

    return app_commands.check(predicate)


def has_any_role(*role_names: str, role_ids: list = None):
    """Check if user has ANY of the specified roles (by name or ID).

    Args:
        *role_names: Variable number of role names
        role_ids: List of role IDs to check (optional)
    """

    async def predicate(interaction: discord.Interaction) -> bool:
        # Check role IDs first
        if role_ids:
            for role_id in role_ids:
                role = discord.utils.get(interaction.user.roles, id=role_id)
                if role:
                    return True

        # Check role names
        for role_name in role_names:
            role = discord.utils.get(interaction.user.roles, name=role_name)
            if role:
                return True

        return False

    return app_commands.check(predicate)


def has_all_roles(*role_names: str, role_ids: list = None):
    """Check if user has ALL of the specified roles (by name or ID).

    Args:
        *role_names: Variable number of role names
        role_ids: List of role IDs to check (optional)
    """

    async def predicate(interaction: discord.Interaction) -> bool:
        # Check role IDs
        if role_ids:
            for role_id in role_ids:
                role = discord.utils.get(interaction.user.roles, id=role_id)
                if not role:
                    return False

        # Check role names
        for role_name in role_names:
            role = discord.utils.get(interaction.user.roles, name=role_name)
            if not role:
                return False

        return True

    return app_commands.check(predicate)


def is_moderator():
    """Check if user has Moderator role or higher permissions."""

    async def predicate(interaction: discord.Interaction) -> bool:
        # Check if they're already an admin
        if interaction.user.guild_permissions.administrator:
            return True

        # Check if they have admin role (by ID or name)
        if Config.ADMIN_ROLE_ID:
            admin_role = discord.utils.get(interaction.user.roles, id=Config.ADMIN_ROLE_ID)
            if admin_role:
                return True

        admin_role = discord.utils.get(interaction.user.roles, name=Config.ADMIN_ROLE_NAME)
        if admin_role:
            return True

        # Check if they have moderator role (by ID or name)
        if Config.MODERATOR_ROLE_ID:
            mod_role = discord.utils.get(interaction.user.roles, id=Config.MODERATOR_ROLE_ID)
            if mod_role:
                return True

        mod_role = discord.utils.get(interaction.user.roles, name=Config.MODERATOR_ROLE_NAME)
        if mod_role:
            return True

        return False

    return app_commands.check(predicate)


def is_officer():
    """Check if user has Officer role or higher permissions."""

    async def predicate(interaction: discord.Interaction) -> bool:
        # Check if they're admin or moderator first
        if interaction.user.guild_permissions.administrator:
            return True

        # Check admin role (by ID or name)
        if Config.ADMIN_ROLE_ID:
            admin_role = discord.utils.get(interaction.user.roles, id=Config.ADMIN_ROLE_ID)
            if admin_role:
                return True

        admin_role = discord.utils.get(interaction.user.roles, name=Config.ADMIN_ROLE_NAME)
        if admin_role:
            return True

        # Check moderator role (by ID or name)
        if Config.MODERATOR_ROLE_ID:
            mod_role = discord.utils.get(interaction.user.roles, id=Config.MODERATOR_ROLE_ID)
            if mod_role:
                return True

        mod_role = discord.utils.get(interaction.user.roles, name=Config.MODERATOR_ROLE_NAME)
        if mod_role:
            return True

        # Check officer role (by ID or name)
        if Config.OFFICER_ROLE_ID:
            officer_role = discord.utils.get(interaction.user.roles, id=Config.OFFICER_ROLE_ID)
            if officer_role:
                return True

        officer_role = discord.utils.get(interaction.user.roles, name=Config.OFFICER_ROLE_NAME)
        if officer_role:
            return True

        return False

    return app_commands.check(predicate)


class AdminCommands(commands.Cog):
    """Admin commands cog."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="promote", description="[HICOM] Promote a member to the next rank")
    @app_commands.describe(member="The member to promote")
    @is_admin()
    async def promote(self, interaction: discord.Interaction, member: discord.Member):
        """Promote a member to the next rank."""
        # Check if interaction is still valid before deferring
        if not interaction.response.is_done():
            try:
                await interaction.response.defer(ephemeral=True)
            except discord.errors.NotFound:
                logger.warning(
                    f"Interaction expired for promote command - user: {interaction.user.name}, target: {member.name}"
                )
                # Try to send a DM to the user to inform them
                try:
                    await interaction.user.send(
                        f"⚠️ Your `/promote {member.mention}` command timed out. This can happen due to network latency. Please try again."
                    )
                except Exception as e:
                    logger.debug(f"Could not send timeout DM to user {interaction.user.id}: {e}")
                return
            except Exception as e:
                logger.error(f"Error deferring interaction in promote: {e}")
                return
        else:
            logger.warning(f"Interaction already responded to in promote command")
            return

        # Check if user is trying to promote themselves
        if member.id == interaction.user.id:
            await interaction.followup.send(
                "❌ You cannot promote yourself! Ask High Command to promote you.", ephemeral=True
            )
            return

        # Get member data
        member_data = await database.get_member(member.id)
        if not member_data:
            await interaction.followup.send(
                f"❌ {member.mention} is not registered. They need to use `/link-roblox` first.",
                ephemeral=True,
            )
            return

        # FIRST: Sync rank from Roblox (Roblox is source of truth)
        sync_result = await roblox_api.sync_member_rank_from_roblox(member.id)

        if sync_result["success"] and sync_result["action"] == "updated":
            # Rank was updated from Roblox before promotion
            await self._update_member_role(
                member, sync_result["old_rank"]["rank_order"], sync_result["new_rank"]["rank_order"]
            )
            logger.info(
                f"Pre-promotion sync for {member.name}: "
                f"{sync_result['old_rank']['rank_name']} → {sync_result['new_rank']['rank_name']}"
            )

            # Show notification that rank was synced
            await interaction.followup.send(
                f"🔄 **Rank Synced from Roblox First**\n"
                f"{member.mention}'s rank was updated from Roblox: "
                f"{sync_result['old_rank']['rank_name']} → {sync_result['new_rank']['rank_name']}\n\n"
                f"Proceeding with promotion...",
                ephemeral=True,
            )

            # Refresh member data
            member_data = await database.get_member(member.id)
        elif sync_result["success"] and sync_result["action"] == "skipped":
            # Sync was skipped (no matching rank) - log but continue with promotion
            logger.warning(f"Pre-promotion sync skipped for {member.name}: {sync_result['reason']}")

        # Get next rank (include admin-only ranks for manual promotion)
        next_rank = await database.get_next_rank(
            member_data["current_rank"], include_admin_only=True
        )
        if not next_rank:
            await interaction.followup.send(
                f"❌ {member.mention} is already at the maximum rank!", ephemeral=True
            )
            return

        # Check if rank is admin-only
        is_admin_only = next_rank.get("admin_only", False)

        # If not admin-only, check if member has enough points
        if not is_admin_only and member_data["points"] < next_rank["points_required"]:
            points_needed = next_rank["points_required"] - member_data["points"]
            await interaction.followup.send(
                f"❌ {member.mention} needs {points_needed} more points to be promoted to **{next_rank['rank_name']}**.\n"
                f"Current: {member_data['points']}/{next_rank['points_required']} points",
                ephemeral=True,
            )
            return

        # Store the current rank for rollback if needed
        old_rank_order = member_data["current_rank"]
        old_rank = await database.get_rank_by_order(old_rank_order)

        # Update rank in database
        await database.set_member_rank(member.id, next_rank["rank_order"])

        # Update Discord role
        discord_role_success = False
        try:
            await self._update_member_role(
                member, member_data["current_rank"], next_rank["rank_order"]
            )
            discord_role_success = True
        except Exception as e:
            logger.error(f"Failed to update Discord role for {member.name}: {e}")

        # Update Roblox rank
        roblox_success = False
        roblox_error = None
        try:
            roblox_success = await roblox_api.update_member_rank(
                member_data["roblox_username"], next_rank["roblox_group_rank_id"]
            )
            if not roblox_success:
                roblox_error = "API returned False - check permissions or rate limits"
        except Exception as e:
            logger.error(f"Failed to update Roblox rank for {member_data['roblox_username']}: {e}")
            roblox_error = str(e)

        # Notify member
        dm_sent = False
        try:
            await member.send(
                f"🎉 **Congratulations!** You've been promoted to **{next_rank['rank_name']}**!\n"
                f"Keep up the great work in the clan!"
            )
            dm_sent = True
            logger.info(f"Sent promotion DM to {member.name} (ID: {member.id})")
        except discord.Forbidden:
            logger.warning(
                f"Cannot send DM to {member.name} (ID: {member.id}) - DMs disabled or bot blocked"
            )
        except Exception as e:
            logger.error(f"Failed to send promotion DM to {member.name} (ID: {member.id}): {e}")

        # Send confirmation
        # Determine embed color based on success/failure
        if roblox_success and discord_role_success:
            embed_color = discord.Color.green()
            embed_title = "✅ Promotion Successful"
        elif not roblox_success:
            embed_color = discord.Color.orange()
            embed_title = "⚠️ Promotion Complete (Roblox Sync Failed)"
        else:
            embed_color = discord.Color.orange()
            embed_title = "⚠️ Promotion Complete (Discord Role Failed)"

        embed = discord.Embed(
            title=embed_title, description=f"{member.mention} has been promoted!", color=embed_color
        )

        embed.add_field(name="Previous Rank", value=old_rank["rank_name"], inline=True)
        embed.add_field(name="New Rank", value=next_rank["rank_name"], inline=True)
        embed.add_field(name="Total Points", value=str(member_data["points"]), inline=True)

        # Show rank type
        if is_admin_only:
            embed.add_field(
                name="Rank Type", value="⚡ HICOM-Granted Rank (Manual Promotion)", inline=False
            )
        else:
            embed.add_field(name="Rank Type", value="📊 Point-Based Rank", inline=False)

        # Detailed status for each system
        db_status = "✅ Database updated"
        discord_status = (
            "✅ Discord role updated" if discord_role_success else "⚠️ Discord role update failed"
        )
        roblox_status = "✅ Roblox rank updated" if roblox_success else f"❌ Roblox sync failed"
        dm_status = "✅ DM sent" if dm_sent else "⚠️ DM failed (user has DMs disabled)"

        embed.add_field(name="Database", value=db_status, inline=True)
        embed.add_field(name="Discord Role", value=discord_status, inline=True)
        embed.add_field(name="Roblox Sync", value=roblox_status, inline=True)
        embed.add_field(name="Notification", value=dm_status, inline=True)

        # Add warning if Roblox sync failed
        if not roblox_success:
            warning_msg = (
                f"⚠️ **Manual Action Required**\n"
                f"The member's rank was updated in Discord/Database but **NOT in Roblox**.\n"
                f"• Use `/sync {member.mention}` to retry syncing to Roblox\n"
                f"• Or manually update their rank in the Roblox group\n"
            )
            if roblox_error:
                warning_msg += f"• Error: `{roblox_error}`"
            embed.add_field(name="⚠️ Action Required", value=warning_msg, inline=False)

            # Log the desync for tracking
            logger.warning(
                f"DESYNC: {member.name} promoted to {next_rank['rank_name']} in Discord "
                f"but Roblox update failed. Error: {roblox_error}"
            )

        await interaction.followup.send(embed=embed, ephemeral=True)

        # Announce in server (optional - you can customize this)
        # announcement_channel = interaction.channel
        # await announcement_channel.send(
        #     f"🎉 Congratulations to {member.mention} on their promotion to **{next_rank['rank_name']}**!"
        # )

    @app_commands.command(
        name="add-points", description="[ELITE+] Manually add or remove points from a member"
    )
    @app_commands.describe(
        member="The member to adjust points for",
        points="Points to add (positive) or remove (negative)",
    )
    @is_admin()
    async def add_points(
        self, interaction: discord.Interaction, member: discord.Member, points: int
    ):
        """Add or remove points from a member."""
        if not interaction.response.is_done():
            try:
                await interaction.response.defer(ephemeral=True)
            except discord.errors.NotFound:
                logger.warning(
                    f"Interaction expired for add-points command - user: {interaction.user.name}"
                )
                try:
                    await interaction.user.send(
                        f"⚠️ Your `/add-points` command timed out. Please try again."
                    )
                except Exception as e:
                    logger.debug(f"Could not send timeout DM to user {interaction.user.id}: {e}")
                return
            except Exception as e:
                logger.error(f"Error deferring interaction in add-points: {e}")
                return
        else:
            logger.warning("Interaction already responded to in add-points command")
            return

        # Check if user is trying to add points to themselves
        if member.id == interaction.user.id:
            await interaction.followup.send(
                "❌ You cannot add points to yourself! Ask HICOM to adjust your points.",
                ephemeral=True,
            )
            return

        # Get member data
        member_data = await database.get_member(member.id)
        if not member_data:
            await interaction.followup.send(
                f"❌ {member.mention} is not registered. They need to use `/link-roblox` first.",
                ephemeral=True,
            )
            return

        # Validate points won't go negative
        new_points = member_data["points"] + points
        if new_points < 0:
            await interaction.followup.send(
                f"❌ Cannot remove {abs(points)} points. Member only has {member_data['points']} points.",
                ephemeral=True,
            )
            return

        # Update points
        await database.add_points(member.id, points)

        # Notify member
        dm_sent = False
        try:
            if points > 0:
                await member.send(
                    f"🎁 You've been awarded **{points} points** by Command!\n"
                    f"New total: {new_points} points. Use `/xp` to check your progress."
                )
            else:
                await member.send(
                    f"⚠️ **{abs(points)} points** have been removed from your account by Command.\n"
                    f"New total: {new_points} points."
                )
            dm_sent = True
            logger.info(f"Sent points notification DM to {member.name} (ID: {member.id})")
        except discord.Forbidden:
            logger.warning(
                f"Cannot send DM to {member.name} (ID: {member.id}) - DMs disabled or bot blocked"
            )
        except Exception as e:
            logger.error(f"Failed to send points DM to {member.name} (ID: {member.id}): {e}")

        # Check if member is now eligible for promotion (only if points were added)
        promotion_eligible = False
        if points > 0:
            eligibility = await database.check_promotion_eligibility(member.id)
            if eligibility:
                promotion_eligible = True
                # Send notification to admin channel
                admin_channel_id = await database.get_config("admin_channel_id")
                if not admin_channel_id:
                    admin_channel_id = Config.ADMIN_CHANNEL_ID

                if admin_channel_id:
                    admin_channel = interaction.guild.get_channel(int(admin_channel_id))
                    if admin_channel:
                        next_rank = eligibility["next_rank"]

                        promo_embed = discord.Embed(
                            title="🎖️ Member Eligible for Promotion",
                            description=f"{member.mention} has earned enough points for a promotion!",
                            color=discord.Color.gold(),
                        )

                        promo_embed.add_field(name="Member", value=member.mention, inline=True)
                        promo_embed.add_field(
                            name="Current Rank", value=member_data["rank_name"], inline=True
                        )
                        promo_embed.add_field(
                            name="Total Points", value=str(new_points), inline=True
                        )

                        promo_embed.add_field(
                            name="Eligible For",
                            value=f"**{next_rank['rank_name']}**\n(Requires {next_rank['points_required']} points)",
                            inline=False,
                        )

                        promo_embed.set_footer(
                            text="Click the buttons below to approve or deny the promotion"
                        )

                        # Create promotion approval view
                        from commands.user_commands import PromotionApprovalView

                        promo_view = PromotionApprovalView(
                            member_id=member.id, next_rank_order=next_rank["rank_order"]
                        )

                        await admin_channel.send(embed=promo_embed, view=promo_view)

        # Send confirmation
        action = "added to" if points > 0 else "removed from"
        dm_status = "✅ DM sent" if dm_sent else "⚠️ DM failed (user has DMs disabled)"

        embed = discord.Embed(
            title="✅ Points Updated",
            description=f"{abs(points)} points {action} {member.mention}",
            color=discord.Color.blue(),
        )

        embed.add_field(name="Previous Points", value=str(member_data["points"]), inline=True)
        embed.add_field(name="Change", value=f"{points:+d}", inline=True)
        embed.add_field(name="New Points", value=str(new_points), inline=True)
        embed.add_field(name="Notification", value=dm_status, inline=False)

        if promotion_eligible:
            embed.add_field(
                name="🎖️ Promotion Available",
                value=f"{member.mention} is now eligible for promotion!",
                inline=False,
            )

        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="points-remove", description="[HICOM] Remove points from a member")
    @app_commands.describe(
        member="The member to remove points from", points="Number of points to remove"
    )
    @is_admin()
    async def points_remove(
        self, interaction: discord.Interaction, member: discord.Member, points: int
    ):
        """Remove points from a member."""
        if not interaction.response.is_done():
            try:
                await interaction.response.defer(ephemeral=True)
            except discord.errors.NotFound:
                logger.warning(
                    f"Interaction expired for points-remove command - user: {interaction.user.name}"
                )
                try:
                    await interaction.user.send(
                        f"⚠️ Your `/points-remove` command timed out. Please try again."
                    )
                except Exception as e:
                    logger.debug(f"Could not send timeout DM to user {interaction.user.id}: {e}")
                return
            except Exception as e:
                logger.error(f"Error deferring interaction in points-remove: {e}")
                return
        else:
            logger.warning("Interaction already responded to in points-remove command")
            return

        # Validate positive number
        if points <= 0:
            await interaction.followup.send(
                "❌ Please enter a positive number of points to remove.", ephemeral=True
            )
            return

        # Check if user is trying to remove points from themselves
        if member.id == interaction.user.id:
            await interaction.followup.send(
                "❌ You cannot remove points from yourself! Ask another admin.", ephemeral=True
            )
            return

        # Get member data
        member_data = await database.get_member(member.id)
        if not member_data:
            await interaction.followup.send(
                f"❌ {member.mention} is not registered. They need to use `/link-roblox` first.",
                ephemeral=True,
            )
            return

        # Validate member has enough points
        if member_data["points"] < points:
            await interaction.followup.send(
                f"❌ Cannot remove {points} points. {member.mention} only has {member_data['points']} points.",
                ephemeral=True,
            )
            return

        # Calculate new total
        new_points = member_data["points"] - points

        # Update points (use negative value)
        await database.add_points(member.id, -points)

        # Notify member
        dm_sent = False
        try:
            await member.send(
                f"⚠️ **{points} points** have been removed from your account by High Command.\n"
                f"New total: {new_points} points."
            )
            dm_sent = True
            logger.info(f"Sent point removal DM to {member.name} (ID: {member.id})")
        except discord.Forbidden:
            logger.warning(
                f"Cannot send DM to {member.name} (ID: {member.id}) - DMs disabled or bot blocked"
            )
        except Exception as e:
            logger.error(f"Failed to send removal DM to {member.name} (ID: {member.id}): {e}")

        # Send confirmation
        dm_status = "✅ DM sent" if dm_sent else "⚠️ DM failed (user has DMs disabled)"

        embed = discord.Embed(
            title="✅ Points Removed",
            description=f"{points} points removed from {member.mention}",
            color=discord.Color.orange(),
        )

        embed.add_field(name="Previous Points", value=str(member_data["points"]), inline=True)
        embed.add_field(name="Removed", value=f"-{points}", inline=True)
        embed.add_field(name="New Points", value=str(new_points), inline=True)
        embed.add_field(name="Notification", value=dm_status, inline=False)

        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(
        name="set-admin-channel", description="[ADMIN] Set the channel for raid submissions"
    )
    @app_commands.describe(channel="The channel where raid submissions will be posted")
    @is_admin()
    async def set_admin_channel(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ):
        """Set the admin channel for raid submissions."""
        if not interaction.response.is_done():
            try:
                await interaction.response.defer(ephemeral=True)
            except discord.errors.NotFound:
                logger.warning(
                    f"Interaction expired for set-admin-channel command - user: {interaction.user.name}"
                )
                try:
                    await interaction.user.send(
                        f"⚠️ Your `/set-admin-channel` command timed out. Please try again."
                    )
                except Exception as e:
                    logger.debug(f"Could not send timeout DM to user {interaction.user.id}: {e}")
                return
            except Exception as e:
                logger.error(f"Error deferring interaction in set-admin-channel: {e}")
                return
        else:
            logger.warning("Interaction already responded to in set-admin-channel command")
            return

        # Update config
        await database.set_config("admin_channel_id", str(channel.id))

        await interaction.followup.send(
            f"✅ Admin channel set to {channel.mention}. All raid submissions will be posted there.",
            ephemeral=True,
        )

    @app_commands.command(
        name="view-pending", description="[HICOM] View all pending raid submissions"
    )
    @is_admin()
    async def view_pending(self, interaction: discord.Interaction):
        """View all pending raid submissions."""
        if not interaction.response.is_done():
            try:
                await interaction.response.defer(ephemeral=True)
            except discord.errors.NotFound:
                logger.warning(
                    f"Interaction expired for view-pending command - user: {interaction.user.name}"
                )
                try:
                    await interaction.user.send(
                        f"⚠️ Your `/view-pending` command timed out. Please try again."
                    )
                except Exception as e:
                    logger.debug(f"Could not send timeout DM to user {interaction.user.id}: {e}")
                return
            except Exception as e:
                logger.error(f"Error deferring interaction in view-pending: {e}")
                return
        else:
            logger.warning("Interaction already responded to in view-pending command")
            return

        pending = await database.get_pending_submissions()

        if not pending:
            await interaction.followup.send("📋 No pending raid submissions.", ephemeral=True)
            return

        embed = discord.Embed(
            title="📋 Pending Raid Submissions",
            description=f"There are {len(pending)} pending submission(s)",
            color=discord.Color.blue(),
        )

        for submission in pending[:10]:  # Show first 10
            submitter = interaction.guild.get_member(submission["submitter_id"])
            submitter_name = (
                submitter.mention if submitter else f"Unknown ({submission['submitter_id']})"
            )

            embed.add_field(
                name=f"Submission #{submission['submission_id']}",
                value=(
                    f"**Submitter:** {submitter_name}\n"
                    f"**Start:** {submission['start_time']}\n"
                    f"**End:** {submission['end_time']}\n"
                    f"**Participants:** {submission['participants'][:100]}..."
                ),
                inline=False,
            )

        if len(pending) > 10:
            embed.set_footer(text=f"Showing 10 of {len(pending)} submissions")

        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(
        name="check-member", description="[HICOM] Check a member's stats and rank eligibility"
    )
    @app_commands.describe(member="The member to check")
    @is_admin()
    async def check_member(self, interaction: discord.Interaction, member: discord.Member):
        """Check a member's detailed stats."""
        if not interaction.response.is_done():
            try:
                await interaction.response.defer(ephemeral=True)
            except discord.errors.NotFound:
                logger.warning(
                    f"Interaction expired for check-member command - user: {interaction.user.name}"
                )
                try:
                    await interaction.user.send(
                        f"⚠️ Your `/check-member` command timed out. Please try again."
                    )
                except Exception as e:
                    logger.debug(f"Could not send timeout DM to user {interaction.user.id}: {e}")
                return
            except Exception as e:
                logger.error(f"Error deferring interaction in check-member: {e}")
                return
        else:
            logger.warning("Interaction already responded to in check-member command")
            return

        member_data = await database.get_member(member.id)
        if not member_data:
            await interaction.followup.send(
                f"❌ {member.mention} is not registered.", ephemeral=True
            )
            return

        # Auto-sync rank from Roblox (Roblox is source of truth)
        sync_result = await roblox_api.sync_member_rank_from_roblox(member.id)
        rank_synced = False

        if sync_result["success"] and sync_result["action"] == "updated":
            # Rank was updated from Roblox
            await self._update_member_role(
                member, sync_result["old_rank"]["rank_order"], sync_result["new_rank"]["rank_order"]
            )
            logger.info(
                f"Auto-synced {member_data['roblox_username']} on check-member: "
                f"{sync_result['old_rank']['rank_name']} → {sync_result['new_rank']['rank_name']}"
            )
            rank_synced = True

            # Refresh member data
            member_data = await database.get_member(member.id)
        elif sync_result["success"] and sync_result["action"] == "skipped":
            # Sync was skipped (no matching rank) - log but continue
            logger.info(
                f"Sync skipped for {member_data['roblox_username']} on check-member: {sync_result['reason']}"
            )

        # Get next rank info
        next_rank = await database.get_next_rank(member_data["current_rank"])

        embed = discord.Embed(
            title=f"📊 Member Stats: {member.display_name}", color=discord.Color.blue()
        )

        embed.add_field(name="Discord", value=member.mention, inline=True)
        embed.add_field(name="Roblox", value=member_data["roblox_username"], inline=True)
        embed.add_field(name="Member Since", value=member_data["created_at"][:10], inline=True)

        # Get current rank details
        current_rank_info = await database.get_rank_by_order(member_data["current_rank"])
        is_current_admin_only = (
            current_rank_info.get("admin_only", False) if current_rank_info else False
        )

        embed.add_field(name="Current Rank", value=member_data["rank_name"], inline=True)
        embed.add_field(name="Total Points", value=str(member_data["points"]), inline=True)

        # Show rank type
        rank_type = "⚡ Admin-Only" if is_current_admin_only else "📊 Point-Based"
        embed.add_field(name="Rank Type", value=rank_type, inline=True)

        # Get next point-based rank (for automatic promotion eligibility)
        next_point_rank = await database.get_next_rank(
            member_data["current_rank"], include_admin_only=False
        )

        if next_point_rank:
            points_needed = next_point_rank["points_required"] - member_data["points"]
            eligible = (
                "✅ Eligible for Promotion"
                if points_needed <= 0
                else f"❌ Needs {points_needed} more points"
            )

            embed.add_field(
                name="Next Point-Based Rank", value=next_point_rank["rank_name"], inline=True
            )
            embed.add_field(
                name="Auto-Promotion Status",
                value=f"{eligible}\n({member_data['points']}/{next_point_rank['points_required']} points)",
                inline=False,
            )
        else:
            embed.add_field(
                name="Point-Based Progress",
                value="🏆 Maximum point-based rank achieved",
                inline=False,
            )

        # Note about admin ranks
        if is_current_admin_only:
            embed.add_field(
                name="ℹ️ Note",
                value="This member has an HICOM-granted rank. Use `/promote` to change ranks manually.",
                inline=False,
            )

        # Add sync notification if rank was updated
        if rank_synced:
            embed.add_field(
                name="🔄 Auto-Synced",
                value=f"Rank was updated from Roblox: {sync_result['old_rank']['rank_name']} → {sync_result['new_rank']['rank_name']}",
                inline=False,
            )

        embed.set_thumbnail(url=member.display_avatar.url)

        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(
        name="list-roblox-ranks",
        description="[ADMIN] View all ranks from your Roblox group with their IDs",
    )
    @is_admin()
    async def list_roblox_ranks(self, interaction: discord.Interaction):
        """List all ranks from the Roblox group with their IDs."""
        if not interaction.response.is_done():
            try:
                await interaction.response.defer(ephemeral=True)
            except discord.errors.NotFound:
                logger.warning(
                    f"Interaction expired for list-roblox-ranks command - user: {interaction.user.name}"
                )
                try:
                    await interaction.user.send(
                        f"⚠️ Your `/list-roblox-ranks` command timed out. Please try again."
                    )
                except Exception as e:
                    logger.debug(f"Could not send timeout DM to user {interaction.user.id}: {e}")
                return
            except Exception as e:
                logger.error(f"Error deferring interaction in list-roblox-ranks: {e}")
                return
        else:
            logger.warning("Interaction already responded to in list-roblox-ranks command")
            return

        # Fetch ranks from Roblox
        roblox_roles = await roblox_api.get_group_roles()

        if not roblox_roles:
            try:
                await interaction.followup.send(
                    "❌ Failed to fetch ranks from Roblox. Check your group configuration and try again.",
                    ephemeral=True,
                )
            except discord.errors.NotFound:
                logger.warning("Interaction expired before sending error message")
            return

        # Get group info
        group_info = await roblox_api.get_group_info()
        group_name = group_info["name"] if group_info else "Unknown Group"

        # Create embed
        embed = discord.Embed(
            title=f"🎮 Roblox Group Ranks: {group_name}",
            description="All ranks from your Roblox group with their IDs for database configuration",
            color=discord.Color.blue(),
        )

        # Sort by rank number (ascending)
        sorted_roles = sorted(roblox_roles, key=lambda x: x["rank"])

        # Split into chunks for Discord field limit
        chunk_size = 10
        for i in range(0, len(sorted_roles), chunk_size):
            chunk = sorted_roles[i : i + chunk_size]

            ranks_text = ""
            for role in chunk:
                ranks_text += (
                    f"**{role['name']}**\n"
                    f"  • Rank #: `{role['rank']}`\n"
                    f"  • Role ID: `{role['id']}`\n"
                    f"  • Members: {role['member_count']}\n\n"
                )

            field_name = f"Ranks {i + 1}-{min(i + chunk_size, len(sorted_roles))}"
            embed.add_field(name=field_name, value=ranks_text, inline=False)

        embed.add_field(
            name="💡 How to Use",
            value=(
                "**To configure database ranks:**\n"
                "1. Choose either `Rank #` or `Role ID` for each rank\n"
                "2. Update `database.py` in `insert_default_ranks()`\n"
                "3. Use the format: `(order, 'Name', points, rank_or_id, admin_only)`\n\n"
                "**Recommendation:** Use `Rank #` for simplicity (works across groups)\n"
                "Use `Role ID` for precision (specific to your group)"
            ),
            inline=False,
        )

        embed.set_footer(text="Use /list-ranks to see your configured Discord ranks")

        try:
            await interaction.followup.send(embed=embed, ephemeral=True)
        except discord.errors.NotFound:
            logger.warning("Interaction expired before sending list-roblox-ranks response")
        except Exception as e:
            logger.error(f"Error sending list-roblox-ranks response: {e}")

    @app_commands.command(
        name="compare-ranks",
        description="[ADMIN] Compare Roblox ranks with configured database ranks",
    )
    @is_admin()
    async def compare_ranks(self, interaction: discord.Interaction):
        """Compare Roblox group ranks with configured database ranks."""
        if not interaction.response.is_done():
            try:
                await interaction.response.defer(ephemeral=True)
            except discord.errors.NotFound:
                logger.warning(
                    f"Interaction expired for compare-ranks command - user: {interaction.user.name}"
                )
                try:
                    await interaction.user.send(
                        f"⚠️ Your `/compare-ranks` command timed out. Please try again."
                    )
                except Exception as e:
                    logger.debug(f"Could not send timeout DM to user {interaction.user.id}: {e}")
                return
            except Exception as e:
                logger.error(f"Error deferring interaction in compare-ranks: {e}")
                return
        else:
            logger.warning("Interaction already responded to in compare-ranks command")
            return

        # Fetch Roblox ranks
        roblox_roles = await roblox_api.get_group_roles()

        if not roblox_roles:
            try:
                await interaction.followup.send(
                    "❌ Failed to fetch ranks from Roblox. Check your group configuration.",
                    ephemeral=True,
                )
            except discord.errors.NotFound:
                logger.warning("Interaction expired before sending error message")
            return

        # Get database ranks
        db_ranks = await database.get_all_ranks()

        # Create a map of Roblox role ID -> role data
        roblox_map = {role["id"]: role for role in roblox_roles}
        roblox_rank_map = {role["rank"]: role for role in roblox_roles}

        embed = discord.Embed(
            title="🔄 Rank Mapping Comparison",
            description="Compare your configured Discord ranks with Roblox group ranks",
            color=discord.Color.gold(),
        )

        # Check which database ranks have matching Roblox ranks
        mapped = []
        unmapped = []

        for db_rank in db_ranks:
            roblox_id = db_rank["roblox_group_rank_id"]

            # Try to find matching Roblox rank (by ID or rank number)
            roblox_match = roblox_map.get(roblox_id) or roblox_rank_map.get(roblox_id)

            if roblox_match:
                mapped.append(
                    {
                        "db": db_rank,
                        "roblox": roblox_match,
                        "match_type": "ID" if roblox_id == roblox_match["id"] else "Rank #",
                    }
                )
            else:
                unmapped.append(db_rank)

        # Show mapped ranks
        if mapped:
            mapped_text = ""
            for item in mapped[:15]:  # Show first 15
                db = item["db"]
                roblox = item["roblox"]
                match_icon = "🔗" if item["match_type"] == "ID" else "🔢"

                mapped_text += (
                    f"{match_icon} **{db['rank_name']}**\n"
                    f"  → Roblox: {roblox['name']} (Rank #{roblox['rank']})\n"
                )

            if len(mapped) > 15:
                mapped_text += f"\n_...and {len(mapped) - 15} more_"

            embed.add_field(
                name=f"✅ Mapped Ranks ({len(mapped)})", value=mapped_text or "None", inline=False
            )

        # Show unmapped ranks
        if unmapped:
            unmapped_text = ""
            for db_rank in unmapped[:10]:  # Show first 10
                unmapped_text += (
                    f"❌ **{db_rank['rank_name']}**\n"
                    f"  Looking for: ID/Rank# `{db_rank['roblox_group_rank_id']}`\n"
                )

            if len(unmapped) > 10:
                unmapped_text += f"\n_...and {len(unmapped) - 10} more_"

            embed.add_field(
                name=f"⚠️ Unmapped Ranks ({len(unmapped)})", value=unmapped_text, inline=False
            )

            embed.add_field(
                name="🔧 Fix Unmapped Ranks",
                value=(
                    "1. Run `/list-roblox-ranks` to see available Roblox ranks\n"
                    "2. Update `database.py` with correct rank IDs or numbers\n"
                    "3. Restart the bot to apply changes"
                ),
                inline=False,
            )

        # Check for Roblox ranks not in database
        db_ids = {r["roblox_group_rank_id"] for r in db_ranks}
        missing_in_db = []

        for role in roblox_roles:
            if role["id"] not in db_ids and role["rank"] not in db_ids:
                missing_in_db.append(role)

        if missing_in_db:
            missing_text = ""
            for role in missing_in_db[:10]:
                missing_text += (
                    f"➕ **{role['name']}**\n  Rank #: `{role['rank']}` | Role ID: `{role['id']}`\n"
                )

            if len(missing_in_db) > 10:
                missing_text += f"\n_...and {len(missing_in_db) - 10} more_"

            embed.add_field(
                name=f"💡 Roblox Ranks Not in Database ({len(missing_in_db)})",
                value=missing_text,
                inline=False,
            )

        # Summary
        embed.add_field(
            name="📊 Summary",
            value=(
                f"✅ Mapped: {len(mapped)}\n"
                f"⚠️ Unmapped: {len(unmapped)}\n"
                f"💡 Missing: {len(missing_in_db)}\n"
                f"🎮 Total Roblox Ranks: {len(roblox_roles)}\n"
                f"💾 Total Database Ranks: {len(db_ranks)}"
            ),
            inline=False,
        )

        # Legend
        embed.set_footer(text="🔗 = Matched by Role ID | 🔢 = Matched by Rank Number")

        try:
            await interaction.followup.send(embed=embed, ephemeral=True)
        except discord.errors.NotFound:
            logger.warning("Interaction expired before sending compare-ranks response")
        except Exception as e:
            logger.error(f"Error sending compare-ranks response: {e}")

    @app_commands.command(name="list-ranks", description="[ADMIN] View all rank requirements")
    @is_admin()
    async def list_ranks(self, interaction: discord.Interaction):
        """List all ranks and their requirements."""
        if not interaction.response.is_done():
            try:
                await interaction.response.defer(ephemeral=True)
            except discord.errors.NotFound:
                logger.warning(
                    f"Interaction expired for list-ranks command - user: {interaction.user.name}"
                )
                try:
                    await interaction.user.send(
                        f"⚠️ Your `/list-ranks` command timed out. Please try again."
                    )
                except Exception as e:
                    logger.debug(f"Could not send timeout DM to user {interaction.user.id}: {e}")
                return
            except Exception as e:
                logger.error(f"Error deferring interaction in list-ranks: {e}")
                return
        else:
            logger.warning("Interaction already responded to in list-ranks command")
            return

        ranks = await database.get_all_ranks()

        # Separate ranks by type
        point_based_ranks = [r for r in ranks if not r.get("admin_only", False)]
        admin_only_ranks = [r for r in ranks if r.get("admin_only", False)]

        embed = discord.Embed(
            title="🎖️ Clan Rank System",
            description="Complete overview of all ranks",
            color=discord.Color.gold(),
        )

        # Point-Based Ranks Section
        if point_based_ranks:
            point_ranks_text = ""
            for rank in point_based_ranks:
                point_ranks_text += f"**{rank['rank_order']}. {rank['rank_name']}** - {rank['points_required']} pts\n"

            embed.add_field(
                name="📊 Point-Based Ranks (Earn through raids)",
                value=point_ranks_text,
                inline=False,
            )

        # Admin-Only Ranks Section
        if admin_only_ranks:
            # Group by category
            leadership = [r for r in admin_only_ranks if r["rank_order"] in [10, 11, 12, 13, 14]]
            honorary = [r for r in admin_only_ranks if r["rank_order"] in [15, 16, 17, 18]]
            trial = [r for r in admin_only_ranks if r["rank_order"] in [19, 20]]

            if leadership:
                leadership_text = "\n".join(
                    [f"**{r['rank_order']}. {r['rank_name']}**" for r in leadership]
                )
                embed.add_field(
                    name="⚡ Leadership Ranks (HICOM-granted)", value=leadership_text, inline=True
                )

            if honorary:
                honorary_text = "\n".join(
                    [f"**{r['rank_order']}. {r['rank_name']}**" for r in honorary]
                )
                embed.add_field(
                    name="🏆 Honorary Ranks (HICOM-Granted)", value=honorary_text, inline=True
                )

            if trial:
                trial_text = "\n".join([f"**{r['rank_order']}. {r['rank_name']}**" for r in trial])
                embed.add_field(
                    name="🔰 Trial/Probation (HICOM-ranted)", value=trial_text, inline=True
                )

        embed.set_footer(
            text="Use /promote to assign any rank manually | /check-member to see eligibility"
        )

        try:
            await interaction.followup.send(embed=embed, ephemeral=True)
        except discord.errors.NotFound:
            logger.warning("Interaction expired before sending list-ranks response")
        except Exception as e:
            logger.error(f"Error sending list-ranks response: {e}")

    @app_commands.command(
        name="verify-rank",
        description="[ADMIN] Check if a member's Discord rank matches their Roblox rank",
    )
    @app_commands.describe(member="The member to verify")
    @is_admin()
    async def verify_rank(self, interaction: discord.Interaction, member: discord.Member):
        """Verify if a member's Discord rank matches their Roblox rank."""
        if not interaction.response.is_done():
            try:
                await interaction.response.defer(ephemeral=True)
            except discord.errors.NotFound:
                logger.warning(
                    f"Interaction expired for verify-rank command - user: {interaction.user.name}"
                )
                try:
                    await interaction.user.send(
                        f"⚠️ Your `/verify-rank` command timed out. Please try again."
                    )
                except Exception as e:
                    logger.debug(f"Could not send timeout DM to user {interaction.user.id}: {e}")
                return
            except Exception as e:
                logger.error(f"Error deferring interaction in verify-rank: {e}")
                return
        else:
            logger.warning("Interaction already responded to in verify-rank command")
            return

        # Get member from database
        member_data = await database.get_member(member.id)
        if not member_data:
            await interaction.followup.send(
                f"❌ {member.mention} is not registered. They need to use `/link-roblox` first.",
                ephemeral=True,
            )
            return

        # Compare ranks
        comparison = await roblox_api.compare_ranks(member_data)

        if comparison is None:
            # Ranks are in sync
            discord_rank = await database.get_rank_by_order(member_data["current_rank"])
            embed = discord.Embed(
                title="✅ Ranks In Sync",
                description=f"{member.mention}'s Discord and Roblox ranks match!",
                color=discord.Color.green(),
            )
            embed.add_field(name="Current Rank", value=discord_rank["rank_name"], inline=False)
            embed.add_field(
                name="Roblox Username", value=member_data["roblox_username"], inline=False
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        if comparison["status"] == "error":
            await interaction.followup.send(
                f"❌ Error checking ranks: {comparison['message']}", ephemeral=True
            )
            return

        # Ranks don't match
        embed = discord.Embed(
            title="⚠️ Rank Mismatch Detected",
            description=f"{member.mention}'s Discord and Roblox ranks don't match!",
            color=discord.Color.orange(),
        )

        embed.add_field(
            name="Discord Rank",
            value=f"**{comparison['discord_rank']['rank_name']}**\n(Order: {comparison['discord_rank']['rank_order']})",
            inline=True,
        )

        embed.add_field(
            name="Roblox Rank",
            value=f"**{comparison['roblox_rank']['rank_name']}**\n(Rank: {comparison['roblox_rank']['rank']})",
            inline=True,
        )

        if comparison["target_rank"]:
            embed.add_field(
                name="Suggested Action",
                value=f"Update Discord rank to **{comparison['target_rank']['rank_name']}**\nUse `/sync {member.mention}` to sync",
                inline=False,
            )
        else:
            embed.add_field(
                name="⚠️ Warning",
                value=f"No database rank matches Roblox rank ID {comparison['roblox_rank']['rank_id']}",
                inline=False,
            )

        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(
        name="sync", description="[ADMIN] Sync a member's Discord rank with their Roblox rank"
    )
    @app_commands.describe(member="The member to sync (leave empty to sync all members)")
    @is_admin()
    async def sync_rank(
        self, interaction: discord.Interaction, member: Optional[discord.Member] = None
    ):
        """Sync Discord ranks with Roblox ranks."""
        if not interaction.response.is_done():
            try:
                await interaction.response.defer(ephemeral=True)
            except discord.errors.NotFound:
                logger.warning(
                    f"Interaction expired for sync command - user: {interaction.user.name}"
                )
                try:
                    await interaction.user.send(
                        f"⚠️ Your `/sync` command timed out. Please try again."
                    )
                except Exception as e:
                    logger.debug(f"Could not send timeout DM to user {interaction.user.id}: {e}")
                return
            except Exception as e:
                logger.error(f"Error deferring interaction in sync: {e}")
                return
        else:
            logger.warning("Interaction already responded to in sync command")
            return

        if member:
            # Sync single member
            result = await roblox_api.sync_member_rank_from_roblox(member.id)

            if not result["success"]:
                await interaction.followup.send(
                    f"❌ Failed to sync {member.mention}: {result.get('error', 'Unknown error')}",
                    ephemeral=True,
                )
                return

            if result["action"] == "none":
                await interaction.followup.send(
                    f"✅ {member.mention} is already in sync!", ephemeral=True
                )
                return

            if result["action"] == "skipped":
                await interaction.followup.send(
                    f"⚠️ Sync skipped for {member.mention}\n"
                    f"Reason: {result['reason']}\n\n"
                    f"Their Roblox rank '{result['roblox_rank']['rank_name']}' doesn't have a matching Discord rank in the database.",
                    ephemeral=True,
                )
                return

            # Update Discord role
            await self._update_member_role(
                member, result["old_rank"]["rank_order"], result["new_rank"]["rank_order"]
            )

            embed = discord.Embed(
                title="✅ Rank Synced",
                description=f"Successfully synced {member.mention}'s rank from Roblox!",
                color=discord.Color.green(),
            )

            embed.add_field(
                name="Old Discord Rank", value=result["old_rank"]["rank_name"], inline=True
            )

            embed.add_field(
                name="New Discord Rank", value=result["new_rank"]["rank_name"], inline=True
            )

            embed.add_field(
                name="Roblox Rank",
                value=f"{result['roblox_rank']['rank_name']} (Rank {result['roblox_rank']['rank']})",
                inline=False,
            )

            await interaction.followup.send(embed=embed, ephemeral=True)

            # Log the sync
            logger.info(
                f"{interaction.user.name} synced {member.name}'s rank: "
                f"{result['old_rank']['rank_name']} -> {result['new_rank']['rank_name']}"
            )

        else:
            # Bulk sync all members
            initial_message = await interaction.followup.send(
                "🔄 Starting bulk rank synchronization for all members...", ephemeral=True
            )

            # Get all members from database
            # We need to add a function to get all members
            all_members = await self._get_all_discord_members()

            synced = 0
            already_synced = 0
            skipped = 0
            errors = 0
            updates = []

            for db_member in all_members:
                result = await roblox_api.sync_member_rank_from_roblox(db_member["discord_id"])

                if not result["success"]:
                    errors += 1
                    continue

                if result["action"] == "none":
                    already_synced += 1
                    continue

                if result["action"] == "skipped":
                    skipped += 1
                    continue

                # Update Discord role
                discord_member = interaction.guild.get_member(db_member["discord_id"])
                if discord_member:
                    await self._update_member_role(
                        discord_member,
                        result["old_rank"]["rank_order"],
                        result["new_rank"]["rank_order"],
                    )

                synced += 1
                updates.append(
                    f"• {db_member['roblox_username']}: {result['old_rank']['rank_name']} → {result['new_rank']['rank_name']}"
                )

                # Rate limit protection: Add delay between role updates to avoid hitting Discord rate limits
                await asyncio.sleep(0.5)

            embed = discord.Embed(
                title="✅ Bulk Sync Complete",
                description=f"Synchronized ranks for all registered members",
                color=discord.Color.green(),
            )

            embed.add_field(name="✅ Synced", value=str(synced), inline=True)
            embed.add_field(name="✓ Already In Sync", value=str(already_synced), inline=True)
            embed.add_field(name="⚠️ Skipped", value=str(skipped), inline=True)
            embed.add_field(name="❌ Errors", value=str(errors), inline=True)

            if updates:
                updates_text = "\n".join(updates[:10])  # Show first 10
                if len(updates) > 10:
                    updates_text += f"\n... and {len(updates) - 10} more"
                embed.add_field(name="Updates Made", value=updates_text, inline=False)

            await initial_message.edit(content=None, embed=embed)

            logger.info(
                f"{interaction.user.name} performed bulk sync: "
                f"{synced} updated, {already_synced} in sync, {skipped} skipped, {errors} errors"
            )

    @app_commands.command(
        name="set-discord-log-level", description="[ADMIN] Set minimum log level sent to Discord"
    )
    @app_commands.describe(level="Minimum log level: CRITICAL, ERROR, WARNING, or NONE")
    @app_commands.choices(
        level=[
            app_commands.Choice(name="Critical Only", value="CRITICAL"),
            app_commands.Choice(name="Error and Critical", value="ERROR"),
            app_commands.Choice(name="Warning, Error, and Critical", value="WARNING"),
            app_commands.Choice(name="None (Disable Discord Logging)", value="NONE"),
        ]
    )
    @is_admin()
    async def set_discord_log_level(self, interaction: discord.Interaction, level: str):
        """Set the minimum log level that gets sent to Discord logging channel."""
        # Defer response for processing time
        if not interaction.response.is_done():
            try:
                await interaction.response.defer(ephemeral=True)
            except discord.errors.NotFound:
                logger.warning(
                    f"Interaction expired for set-discord-log-level command - user: {interaction.user.name}"
                )
                return

        try:
            # Import DiscordHandler to modify its class variable
            from bot import DiscordHandler

            # Store old level for logging
            old_level = DiscordHandler.min_discord_level

            # Set new level
            DiscordHandler.min_discord_level = level

            # Create response embed
            level_descriptions = {
                "CRITICAL": "Only CRITICAL logs (most severe issues)",
                "ERROR": "ERROR and CRITICAL logs only",
                "WARNING": "WARNING, ERROR, and CRITICAL logs",
                "NONE": "Disabled - no logs sent to Discord",
            }

            embed = discord.Embed(
                title="✅ Discord Log Level Updated",
                description=f"Discord logging channel will now show: **{level_descriptions.get(level, level)}**",
                color=discord.Color.green(),
            )

            embed.add_field(name="Previous Level", value=old_level, inline=True)
            embed.add_field(name="New Level", value=level, inline=True)

            # Add helpful info
            if level == "NONE":
                embed.add_field(
                    name="ℹ️ Note",
                    value="Discord logging is now disabled. All logs still go to `bot.log` file.",
                    inline=False,
                )
            else:
                embed.add_field(
                    name="ℹ️ Note",
                    value="This change is immediate. All logs still go to `bot.log` file.",
                    inline=False,
                )

            await interaction.followup.send(embed=embed, ephemeral=True)

            logger.info(
                f"{interaction.user.name} changed Discord log level from {old_level} to {level}"
            )

        except Exception as e:
            logger.error(f"Error setting Discord log level: {e}")
            await interaction.followup.send(f"❌ Error setting log level: {str(e)}", ephemeral=True)

    async def _get_all_discord_members(self) -> List[Dict[str, Any]]:
        """Get all members from database. Helper function for bulk operations."""
        async with database.aiosqlite.connect(database.DATABASE_PATH) as db:
            db.row_factory = database.aiosqlite.Row
            async with db.execute("SELECT * FROM members") as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def _update_member_role(
        self, member: discord.Member, old_rank_order: int, new_rank_order: int
    ):
        """Update member's Discord role when promoted."""
        # Get old and new rank info
        old_rank = await database.get_rank_by_order(old_rank_order)
        new_rank = await database.get_rank_by_order(new_rank_order)

        if not old_rank or not new_rank:
            return

        # Remove old rank role with retry logic
        old_role = discord.utils.get(member.guild.roles, name=old_rank["rank_name"])
        if old_role:
            for attempt in range(Config.MAX_RATE_LIMIT_RETRIES):
                try:
                    await member.remove_roles(old_role)
                    break
                except discord.Forbidden:
                    logger.error("Bot doesn't have permission to remove roles")
                    return
                except discord.HTTPException as e:
                    if e.status == 429 and attempt < Config.MAX_RATE_LIMIT_RETRIES - 1:
                        # Exponential backoff: 1s, 2s, 4s, etc.
                        delay = Config.RATE_LIMIT_RETRY_DELAY * (2**attempt)
                        logger.warning(
                            f"Rate limited when removing role from {member.name} (attempt {attempt + 1}/{Config.MAX_RATE_LIMIT_RETRIES}) - retrying after {delay}s"
                        )
                        await asyncio.sleep(delay)
                    elif e.status == 429:
                        logger.error(
                            f"Failed to remove role from {member.name} after {Config.MAX_RATE_LIMIT_RETRIES} attempts due to rate limiting"
                        )
                        return
                    else:
                        logger.error(f"HTTP error removing role: {e}")
                        return

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
                except discord.Forbidden:
                    logger.error("Bot doesn't have permission to create roles")
                    return
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
                        return
                    else:
                        logger.error(f"HTTP error creating role: {e}")
                        return

        # Add the role with retry logic
        for attempt in range(Config.MAX_RATE_LIMIT_RETRIES):
            try:
                await member.add_roles(new_role)
                break
            except discord.Forbidden:
                logger.error("Bot doesn't have permission to assign roles")
                return
            except discord.HTTPException as e:
                if e.status == 429 and attempt < Config.MAX_RATE_LIMIT_RETRIES - 1:
                    # Exponential backoff: 1s, 2s, 4s, etc.
                    delay = Config.RATE_LIMIT_RETRY_DELAY * (2**attempt)
                    logger.warning(
                        f"Rate limited when adding role to {member.name} (attempt {attempt + 1}/{Config.MAX_RATE_LIMIT_RETRIES}) - retrying after {delay}s"
                    )
                    await asyncio.sleep(delay)
                elif e.status == 429:
                    logger.error(
                        f"Failed to add role to {member.name} after {Config.MAX_RATE_LIMIT_RETRIES} attempts due to rate limiting"
                    )
                    return
                else:
                    logger.error(f"HTTP error adding role: {e}")
                    return


async def setup(bot):
    """Setup function to load the cog."""
    await bot.add_cog(AdminCommands(bot))
