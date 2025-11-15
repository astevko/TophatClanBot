"""
User commands for TophatC Clan Bot
Commands available to all clan members.
"""

import discord
from discord import app_commands
from discord.ext import commands
import logging
import asyncio
from typing import Optional
import re

import database
from config import Config
from security_utils import (
    cooldown_manager,
    sanitize_embed_text,
    validate_image_attachment,
    get_user_error_message,
    check_admin_permissions,
    ERROR_CODES,
)

logger = logging.getLogger(__name__)


class RaidSubmissionModal(discord.ui.Modal, title="Submit Event"):
    """Modal for collecting event submission details."""

    event_type = discord.ui.TextInput(
        label="Event Type",
        placeholder="e.g., Patrol, Raid, Defense, Training, etc.",
        style=discord.TextStyle.short,
        required=True,
        max_length=50,
    )

    participants = discord.ui.TextInput(
        label="Participants (Roblox Usernames)",
        placeholder="Enter Roblox usernames, separated by commas or newlines\nExample: Player1, Player2, Player3",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=1000,
    )

    start_time = discord.ui.TextInput(
        label="Event Start Time",
        placeholder="e.g., 2024-11-09 14:30 or 2:30 PM EST",
        style=discord.TextStyle.short,
        required=True,
        max_length=100,
    )

    end_time = discord.ui.TextInput(
        label="Event End Time",
        placeholder="e.g., 2024-11-09 16:00 or 4:00 PM EST",
        style=discord.TextStyle.short,
        required=True,
        max_length=100,
    )

    def __init__(self, image_url: str, submitter: discord.Member):
        super().__init__()
        self.image_url = image_url
        self.submitter = submitter

    async def on_submit(self, interaction: discord.Interaction):
        """Handle the modal submission."""
        await interaction.response.defer(ephemeral=True)

        # Parse participants (Roblox usernames) - improved regex for better parsing
        participants_text = self.participants.value

        # Split by comma, newline, or multiple spaces and clean up
        raw_usernames = re.split(r"[,\n]+", participants_text)
        usernames = [username.strip() for username in raw_usernames if username.strip()]

        if not usernames:
            await interaction.followup.send(
                "❌ No participants found. Please enter at least one Roblox username.",
                ephemeral=True,
            )
            return

        # Check which participants are registered (but allow unregistered ones)
        linked_members = []
        unlinked_usernames = []

        for username in usernames:
            member = await database.get_member_by_roblox(username)
            if member:
                linked_members.append(member)
            else:
                unlinked_usernames.append(username)

        # Store submission in database
        submission_id = await database.create_raid_submission(
            submitter_id=self.submitter.id,
            event_type=self.event_type.value.strip(),
            participants=participants_text,
            start_time=self.start_time.value,
            end_time=self.end_time.value,
            image_url=self.image_url,
        )

        # Get admin channel
        admin_channel_id = await database.get_config("admin_channel_id")
        if not admin_channel_id:
            admin_channel_id = Config.ADMIN_CHANNEL_ID

        if not admin_channel_id:
            await interaction.followup.send(
                "❌ Admin channel not configured. Please contact an administrator.", ephemeral=True
            )
            return

        admin_channel = interaction.guild.get_channel(int(admin_channel_id))
        if not admin_channel:
            await interaction.followup.send(
                "❌ Could not find admin channel. Please contact an administrator.", ephemeral=True
            )
            return

        # Create embed for admin review - with sanitized inputs
        event_type_sanitized = sanitize_embed_text(self.event_type.value.strip(), max_length=50)
        participants_sanitized = sanitize_embed_text(participants_text, max_length=1000)
        start_time_sanitized = sanitize_embed_text(self.start_time.value, max_length=100)
        end_time_sanitized = sanitize_embed_text(self.end_time.value, max_length=100)

        embed = discord.Embed(
            title=f"🎯 New {event_type_sanitized} Submission",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow(),
        )

        embed.add_field(name="Event Type", value=event_type_sanitized, inline=True)
        embed.add_field(name="Submitted By", value=self.submitter.mention, inline=True)
        embed.add_field(name="Submission ID", value=f"#{submission_id}", inline=True)
        embed.add_field(name="Status", value="⏳ Pending Review", inline=True)

        # Show participant count and names with link status
        total_participants = len(usernames)
        participant_display = f"**Total: {total_participants} participant(s)**\n"
        participant_display += f"✅ Linked: {len(linked_members)}\n"
        if unlinked_usernames:
            participant_display += f"⚠️ Unlinked: {len(unlinked_usernames)}\n\n"
            participant_display += f"**All Participants:**\n{participants_sanitized}"
        else:
            participant_display += f"\n**Participants:**\n{participants_sanitized}"

        embed.add_field(name="Participants (Roblox)", value=participant_display, inline=False)
        embed.add_field(name="Start Time", value=start_time_sanitized, inline=True)
        embed.add_field(name="End Time", value=end_time_sanitized, inline=True)

        embed.set_image(url=self.image_url)
        embed.set_footer(text=f"Submission ID: {submission_id}")

        # Create approval buttons
        view = RaidApprovalView(submission_id)

        await admin_channel.send(embed=embed, view=view)

        # Build confirmation message
        event_name = self.event_type.value.strip()
        confirmation = f"✅ {event_name} submission sent for admin review! You'll be notified once it's processed.\n\n"
        confirmation += f"**Participants:** {total_participants} total\n"
        confirmation += f"✅ {len(linked_members)} will receive points (linked accounts)\n"

        if unlinked_usernames:
            confirmation += f"⚠️ {len(unlinked_usernames)} won't receive points (not linked):\n"
            confirmation += f"**{', '.join(unlinked_usernames)}**\n"
            confirmation += f"\nThese users can use `/link-roblox` to link their accounts and receive points in future events."

        await interaction.followup.send(confirmation, ephemeral=True)


class PromotionApprovalView(discord.ui.View):
    """View with Approve/Deny buttons for promotion eligibility."""

    def __init__(self, member_id: int, next_rank_order: int):
        super().__init__(timeout=None)
        self.member_id = member_id
        self.next_rank_order = next_rank_order

    @discord.ui.button(label="Approve Promotion", style=discord.ButtonStyle.green, emoji="✅")
    async def approve_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle promotion approval."""
        # Check admin permissions using centralized check
        if not check_admin_permissions(interaction):
            await interaction.response.send_message(
                "❌ You don't have permission to approve promotions.", ephemeral=True
            )
            return

        await interaction.response.defer()

        # Get member
        member = interaction.guild.get_member(self.member_id)
        if not member:
            await interaction.followup.send("❌ Member not found.", ephemeral=True)
            return

        # Get member data
        member_data = await database.get_member(self.member_id)
        if not member_data:
            await interaction.followup.send("❌ Member data not found.", ephemeral=True)
            return

        # Get next rank
        next_rank = await database.get_rank_by_order(self.next_rank_order)
        if not next_rank:
            await interaction.followup.send("❌ Rank not found.", ephemeral=True)
            return

        # Update rank in database
        await database.set_member_rank(self.member_id, self.next_rank_order)

        # Update Discord role (simplified - you can expand this)
        # await self._update_member_role(member, member_data['current_rank'], self.next_rank_order)

        # Update Roblox rank
        import roblox_api

        roblox_success = False
        try:
            roblox_success = await roblox_api.update_member_rank(
                member_data["roblox_username"], next_rank["roblox_group_rank_id"]
            )
            if roblox_success:
                logger.info(
                    f"Updated Roblox rank for {member_data['roblox_username']} to {next_rank['rank_name']}"
                )
            else:
                logger.warning(f"Failed to update Roblox rank for {member_data['roblox_username']}")
        except Exception as e:
            logger.error(f"Error updating Roblox rank during auto-promotion: {e}")

        # Notify member
        try:
            await member.send(
                f"🎉 **Congratulations!** You've been promoted to **{next_rank['rank_name']}**!\n"
                f"Keep up the great work in the clan!"
            )
        except Exception as e:
            logger.debug(f"Could not send promotion DM to user {member.id}: {e}")

        # Update the embed
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.green()
        embed.title = "✅ Promotion Approved"
        embed.add_field(name="Approved By", value=interaction.user.mention, inline=False)

        # Add Roblox sync status
        roblox_status = "✅ Roblox rank updated" if roblox_success else "⚠️ Roblox sync failed"
        embed.add_field(name="Roblox Sync", value=roblox_status, inline=False)

        # Disable buttons
        for item in self.children:
            item.disabled = True

        await interaction.message.edit(embed=embed, view=self)

        # Send confirmation with sync status
        confirmation_msg = f"✅ {member.mention} has been promoted to **{next_rank['rank_name']}**!"
        if not roblox_success:
            confirmation_msg += (
                f"\n⚠️ Roblox rank update failed. Use `/sync {member.mention}` to retry."
            )

        await interaction.followup.send(confirmation_msg, ephemeral=True)

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.red, emoji="❌")
    async def deny_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle promotion denial."""
        # Check admin permissions using centralized check
        if not check_admin_permissions(interaction):
            await interaction.response.send_message(
                "❌ You don't have permission to deny promotions.", ephemeral=True
            )
            return

        await interaction.response.defer()

        # Update the embed
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.red()
        embed.title = "❌ Promotion Denied"
        embed.add_field(name="Denied By", value=interaction.user.mention, inline=False)

        # Disable buttons
        for item in self.children:
            item.disabled = True

        await interaction.message.edit(embed=embed, view=self)
        await interaction.followup.send("❌ Promotion denied.", ephemeral=True)


class RaidApprovalView(discord.ui.View):
    """View with Approve/Decline buttons for raid submissions."""

    def __init__(self, submission_id: int):
        super().__init__(timeout=None)  # No timeout - buttons work indefinitely
        self.submission_id = submission_id

        # Add custom_id for persistence
        self.approve_button = discord.ui.Button(
            label="Approve",
            style=discord.ButtonStyle.green,
            custom_id=f"raid_approve_{submission_id}",
        )
        self.approve_button.callback = self.approve_callback

        self.decline_button = discord.ui.Button(
            label="Decline",
            style=discord.ButtonStyle.red,
            custom_id=f"raid_decline_{submission_id}",
        )
        self.decline_button.callback = self.decline_callback

        self.add_item(self.approve_button)
        self.add_item(self.decline_button)

    async def approve_callback(self, interaction: discord.Interaction):
        """Handle approve button click."""
        # Check if user has admin permissions using centralized check
        if not check_admin_permissions(interaction):
            await interaction.response.send_message(
                "❌ You don't have permission to approve raids.", ephemeral=True
            )
            return

        # Show modal to get points
        modal = PointsInputModal(self.submission_id, interaction)
        await interaction.response.send_modal(modal)

    async def decline_callback(self, interaction: discord.Interaction):
        """Handle decline button click."""
        # Check if user has admin permissions using centralized check
        if not check_admin_permissions(interaction):
            await interaction.response.send_message(
                "❌ You don't have permission to decline raids.", ephemeral=True
            )
            return

        await interaction.response.defer()

        # Get submission details
        submission = await database.get_raid_submission(self.submission_id)
        if not submission:
            await interaction.followup.send("❌ Submission not found.", ephemeral=True)
            return

        # Update database
        await database.decline_raid_submission(self.submission_id, interaction.user.id)

        # Update embed
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.red()

        # Update status field
        for i, field in enumerate(embed.fields):
            if field.name == "Status":
                embed.set_field_at(i, name="Status", value="❌ Declined", inline=True)
                break

        embed.add_field(name="Reviewed By", value=interaction.user.mention, inline=True)

        # Disable buttons
        for item in self.children:
            item.disabled = True

        await interaction.message.edit(embed=embed, view=self)

        # Notify submitter
        try:
            submitter = interaction.guild.get_member(submission["submitter_id"])
            event_type = submission.get("event_type", "event")
            if submitter:
                await submitter.send(
                    f"❌ Your {event_type} submission has been declined by {interaction.user.mention}."
                )
        except Exception as e:
            logger.debug(f"Could not send decline notification DM: {e}")

        await interaction.followup.send("✅ Raid submission declined.", ephemeral=True)


class PointsInputModal(discord.ui.Modal, title="Award Points"):
    """Modal for inputting points to award."""

    points = discord.ui.TextInput(
        label="Points to Award (1-8)",
        placeholder="Enter a number between 1 and 8",
        style=discord.TextStyle.short,
        required=True,
        min_length=1,
        max_length=1,
    )

    def __init__(self, submission_id: int, approval_interaction: discord.Interaction):
        super().__init__()
        self.submission_id = submission_id
        self.approval_interaction = approval_interaction

    async def on_submit(self, interaction: discord.Interaction):
        """Handle points submission."""
        await interaction.response.defer()

        # Validate points
        try:
            points_value = int(self.points.value)
            if points_value < 1 or points_value > 8:
                await interaction.followup.send(
                    "❌ Points must be between 1 and 8.", ephemeral=True
                )
                return
        except ValueError:
            await interaction.followup.send(
                "❌ Invalid points value. Please enter a number between 1 and 8.", ephemeral=True
            )
            return

        # Get submission details
        submission = await database.get_raid_submission(self.submission_id)
        if not submission:
            await interaction.followup.send("❌ Submission not found.", ephemeral=True)
            return

        # Update database
        await database.approve_raid_submission(
            self.submission_id, interaction.user.id, points_value
        )

        # Parse and award points to participants (Roblox usernames)
        participants_text = submission["participants"]

        # Split by comma, newline, or whitespace and clean up
        raw_usernames = re.split(r"[,\n]+", participants_text)
        usernames = [username.strip() for username in raw_usernames if username.strip()]

        awarded_members = []
        awarded_discord_ids = []
        for username in usernames:
            member = await database.get_member_by_roblox(username)

            if member:
                await database.add_points(member["discord_id"], points_value)
                awarded_members.append(f"{username} (<@{member['discord_id']}>)")
                awarded_discord_ids.append(member["discord_id"])

        # Update embed
        embed = self.approval_interaction.message.embeds[0]
        embed.color = discord.Color.green()

        # Update status field
        for i, field in enumerate(embed.fields):
            if field.name == "Status":
                embed.set_field_at(i, name="Status", value="✅ Approved", inline=True)
                break

        embed.add_field(name="Points Awarded", value=str(points_value), inline=True)
        embed.add_field(name="Reviewed By", value=interaction.user.mention, inline=True)

        # Get the view and disable buttons
        view = discord.ui.View.from_message(self.approval_interaction.message)
        for item in view.children:
            item.disabled = True

        await self.approval_interaction.message.edit(embed=embed, view=view)

        # Notify participants and check for promotion eligibility
        event_type = submission.get("event_type", "event")
        eligible_for_promotion = []

        for discord_id in awarded_discord_ids:
            # Send DM notification
            try:
                member = interaction.guild.get_member(discord_id)
                if member:
                    await member.send(
                        f"🎉 You've been awarded **{points_value} points** for {event_type}!\n"
                        f"Use `/xp` to check your progress."
                    )
            except Exception as e:
                logger.debug(f"Could not send points award DM to user: {e}")

            # Check if now eligible for promotion
            eligibility = await database.check_promotion_eligibility(discord_id)
            if eligibility:
                eligible_for_promotion.append({"discord_id": discord_id, "info": eligibility})

        # Send promotion eligibility notifications to admin channel
        if eligible_for_promotion:
            admin_channel_id = await database.get_config("admin_channel_id")
            if not admin_channel_id:
                admin_channel_id = Config.ADMIN_CHANNEL_ID

            if admin_channel_id:
                admin_channel = interaction.guild.get_channel(int(admin_channel_id))
                if admin_channel:
                    for eligible in eligible_for_promotion:
                        member_info = eligible["info"]["member"]
                        next_rank = eligible["info"]["next_rank"]
                        discord_member = interaction.guild.get_member(eligible["discord_id"])

                        promo_embed = discord.Embed(
                            title="🎖️ Member Eligible for Promotion",
                            description=f"{discord_member.mention} has earned enough points for a promotion!",
                            color=discord.Color.gold(),
                        )

                        promo_embed.add_field(
                            name="Member", value=discord_member.mention, inline=True
                        )
                        promo_embed.add_field(
                            name="Current Rank", value=member_info["rank_name"], inline=True
                        )
                        promo_embed.add_field(
                            name="Total Points", value=str(member_info["points"]), inline=True
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
                        promo_view = PromotionApprovalView(
                            member_id=eligible["discord_id"],
                            next_rank_order=next_rank["rank_order"],
                        )

                        await admin_channel.send(embed=promo_embed, view=promo_view)

        # Build result message
        total_usernames = len(usernames)
        result_msg = f"✅ {event_type.capitalize()} approved with {points_value} points!\n\n"
        result_msg += (
            f"**Points awarded to {len(awarded_members)} of {total_usernames} participant(s)**\n"
        )

        if len(awarded_members) < total_usernames:
            unlinked_count = total_usernames - len(awarded_members)
            result_msg += (
                f"⚠️ {unlinked_count} participant(s) didn't receive points (accounts not linked)"
            )

        await interaction.followup.send(result_msg, ephemeral=True)


class UserCommands(commands.Cog):
    """User commands cog."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="xp", description="Check your current rank and points progress")
    @app_commands.checks.cooldown(1, 10)  # 1 use per 10 seconds per user
    async def xp(self, interaction: discord.Interaction):
        """Check your XP and rank progress."""
        if not interaction.response.is_done():
            try:
                await interaction.response.defer(ephemeral=True)
            except discord.errors.NotFound:
                logger.warning(
                    f"Interaction expired for xp command - user: {interaction.user.name}"
                )
                return
            except Exception as e:
                logger.error(f"Error deferring interaction in xp: {e}", exc_info=True)
                await interaction.followup.send(
                    get_user_error_message(ERROR_CODES["XP_GENERAL"]), ephemeral=True
                )
                return
        else:
            logger.warning("Interaction already responded to in xp command")
            return

        try:
            member = await database.get_member(interaction.user.id)
        except Exception as e:
            logger.error(f"Database error in xp command: {e}", exc_info=True)
            await interaction.followup.send(
                get_user_error_message(ERROR_CODES["DATABASE_ERROR"]), ephemeral=True
            )
            return

        if not member:
            await interaction.followup.send(
                "❌ You're not registered yet! Use `/link-roblox` to link your Roblox account.",
                ephemeral=True,
            )
            return

        # Auto-sync rank from Roblox (Roblox is source of truth)
        import roblox_api

        sync_result = await roblox_api.sync_member_rank_from_roblox(interaction.user.id)

        rank_updated = False
        if sync_result["success"] and sync_result["action"] == "updated":
            # Rank was updated from Roblox
            await self._assign_rank_role(interaction.user, sync_result["new_rank"]["rank_order"])
            logger.info(
                f"Auto-synced {member['roblox_username']} on /xp: "
                f"{sync_result['old_rank']['rank_name']} → {sync_result['new_rank']['rank_name']}"
            )
            rank_updated = True

            # Refresh member data to get updated rank
            member = await database.get_member(interaction.user.id)
        elif sync_result["success"] and sync_result["action"] == "skipped":
            # Log warning but don't fail
            logger.info(
                f"Sync skipped for {member['roblox_username']} on /xp: {sync_result['reason']}"
            )

        # Get current rank details
        current_rank_info = await database.get_rank_by_order(member["current_rank"])
        is_admin_only = current_rank_info.get("admin_only", False) if current_rank_info else False

        # Get next point-based rank only (not admin-only ranks)
        next_rank = await database.get_next_rank(member["current_rank"], include_admin_only=False)

        embed = discord.Embed(
            title=f"📊 {interaction.user.display_name}'s Progress", color=discord.Color.blue()
        )

        # Show current rank with type indicator
        rank_display = f"**{member['rank_name']}**"
        if is_admin_only:
            rank_display += " ⚡"

        embed.add_field(name="Current Rank", value=rank_display, inline=True)

        embed.add_field(name="Total Points", value=f"**{member['points']}**", inline=True)

        # Show rank type
        rank_type = "⚡ Admin-Granted" if is_admin_only else "📊 Point-Based"
        embed.add_field(name="Rank Type", value=rank_type, inline=True)

        if next_rank:
            points_needed = next_rank["points_required"] - member["points"]
            progress_bar = self._create_progress_bar(
                member["points"], next_rank["points_required"], member.get("points_required", 0)
            )

            embed.add_field(
                name="Next Point-Based Rank", value=f"**{next_rank['rank_name']}**", inline=True
            )

            embed.add_field(
                name="Progress to Next Rank",
                value=f"{progress_bar}\n{member['points']}/{next_rank['points_required']} ({points_needed} points needed)",
                inline=False,
            )
        else:
            embed.add_field(
                name="Status", value="🏆 **Maximum Point-Based Rank Achieved!**", inline=False
            )

        # Add note for admin-only ranks
        if is_admin_only:
            embed.add_field(
                name="ℹ️ Note",
                value="You have an admin-granted rank. Points still count toward point-based ranks!",
                inline=False,
            )

        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_footer(text=f"Roblox: {member['roblox_username']}")

        # Add sync notification if rank was updated
        if rank_updated:
            embed.add_field(
                name="🔄 Auto-Synced",
                value=f"Your rank was updated from Roblox: {sync_result['old_rank']['rank_name']} → {sync_result['new_rank']['rank_name']}",
                inline=False,
            )

        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(
        name="show-my-id", description="Get your Discord User ID for admin configuration"
    )
    async def show_my_id(self, interaction: discord.Interaction):
        """Show user their Discord ID."""
        if not interaction.response.is_done():
            try:
                await interaction.response.defer(ephemeral=True)
            except discord.errors.NotFound:
                logger.warning(
                    f"Interaction expired for show-my-id command - user: {interaction.user.name}"
                )
                return
            except Exception as e:
                logger.error(f"Error deferring interaction in show-my-id: {e}")
                return
        else:
            logger.warning("Interaction already responded to in show-my-id command")
            return

        embed = discord.Embed(
            title="📋 Your Discord User ID",
            description=f"Your Discord User ID is: **`{interaction.user.id}`**",
            color=discord.Color.blue(),
        )

        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="leaderboard", description="View the top clan members by points")
    @app_commands.checks.cooldown(1, 30)  # 1 use per 30 seconds per user
    async def leaderboard(self, interaction: discord.Interaction):
        """Display the clan leaderboard."""
        if not interaction.response.is_done():
            try:
                await interaction.response.defer()
            except discord.errors.NotFound:
                logger.warning(
                    f"Interaction expired for leaderboard command - user: {interaction.user.name}"
                )
                return
            except Exception as e:
                logger.error(f"Error deferring interaction in leaderboard: {e}", exc_info=True)
                await interaction.followup.send(
                    get_user_error_message(ERROR_CODES["LEADERBOARD_GENERAL"]), ephemeral=True
                )
                return
        else:
            logger.warning("Interaction already responded to in leaderboard command")
            return

        members = await database.get_leaderboard(10)

        if not members:
            await interaction.followup.send(
                "📊 No members found in the leaderboard yet.", ephemeral=True
            )
            return

        embed = discord.Embed(
            title="🏆 TophatC Clan Leaderboard",
            description="Top 10 members by activity points",
            color=discord.Color.gold(),
        )

        medals = ["🥇", "🥈", "🥉"]

        leaderboard_text = ""
        for idx, member in enumerate(members):
            medal = medals[idx] if idx < 3 else f"**{idx + 1}.**"
            user = interaction.guild.get_member(member["discord_id"])
            username = user.mention if user else member["roblox_username"]

            leaderboard_text += (
                f"{medal} {username} - **{member['rank_name']}** ({member['points']} pts)\n"
            )

        embed.description = leaderboard_text
        embed.set_footer(text="Keep raiding to climb the ranks!")

        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="link-roblox", description="Link your Discord account to your Roblox username"
    )
    @app_commands.describe(username="Your Roblox username")
    @app_commands.checks.cooldown(1, 30)  # 1 use per 30 seconds per user
    async def link_roblox(self, interaction: discord.Interaction, username: str):
        """Link Discord account to Roblox username."""
        if not interaction.response.is_done():
            try:
                await interaction.response.defer(ephemeral=True)
            except discord.errors.NotFound:
                logger.warning(
                    f"Interaction expired for link-roblox command - user: {interaction.user.name}"
                )
                return
            except Exception as e:
                logger.error(f"Error deferring interaction in link-roblox: {e}", exc_info=True)
                await interaction.followup.send(
                    get_user_error_message(ERROR_CODES["LINK_ROBLOX_GENERAL"]), ephemeral=True
                )
                return
        else:
            logger.warning("Interaction already responded to in link-roblox command")
            return

        # Import roblox_api here to avoid circular imports
        import roblox_api

        # Step 1: Verify the Roblox user exists
        user_id = await roblox_api.get_user_id_from_username(username)
        if not user_id:
            await interaction.followup.send(
                f"❌ Could not find Roblox user **{username}**. Please check the spelling and try again.",
                ephemeral=True,
            )
            return

        # Step 2: Verify the user is in the Roblox group
        is_member = await roblox_api.verify_group_membership(username)
        if not is_member:
            group_info = await roblox_api.get_group_info()
            group_name = group_info["name"] if group_info else "the clan group"
            await interaction.followup.send(
                f"❌ **{username}** is not a member of {group_name}. Please join the group first, then try linking again.",
                ephemeral=True,
            )
            return

        # Step 3: Get their current Roblox rank
        rank_info = await roblox_api.get_member_rank(username)
        if not rank_info:
            await interaction.followup.send(
                f"❌ Could not retrieve rank information for **{username}**. Please try again later.",
                ephemeral=True,
            )
            return

        # Find the database rank that matches the Roblox rank
        # Try matching by both rank_id and rank number
        target_db_rank = await roblox_api.get_database_rank_by_roblox_id(
            rank_info["rank_id"], rank_info["rank"]
        )

        if not target_db_rank:
            # No matching rank found - use default
            logger.warning(
                f"No database rank found for Roblox rank '{rank_info['rank_name']}' "
                f"(ID: {rank_info['rank_id']}, Rank: {rank_info['rank']})"
            )
            target_rank_order = 1  # Default to first rank
        else:
            target_rank_order = target_db_rank["rank_order"]

        # Check if user already exists
        existing_member = await database.get_member(interaction.user.id)

        if existing_member:
            # Update existing member
            success = await database.update_member_roblox(interaction.user.id, username)
            if success:
                # Sync their rank from Roblox (override Discord rank)
                old_rank_order = existing_member["current_rank"]
                await database.set_member_rank(interaction.user.id, target_rank_order)

                # Update Discord role
                if old_rank_order != target_rank_order:
                    await self._assign_rank_role(interaction.user, target_rank_order)

                    old_rank = await database.get_rank_by_order(old_rank_order)
                    new_rank_name = target_db_rank["rank_name"] if target_db_rank else "Pending"

                    await interaction.followup.send(
                        f"✅ Updated your Roblox username to **{username}**!\n"
                        f"📊 Your current Roblox rank: **{rank_info['rank_name']}** (Rank {rank_info['rank']})\n"
                        f"🔄 **Discord rank synced:** {old_rank['rank_name']} → {new_rank_name}",
                        ephemeral=True,
                    )
                    logger.info(
                        f"Auto-synced {username} rank on link: {old_rank['rank_name']} → {new_rank_name}"
                    )
                else:
                    await interaction.followup.send(
                        f"✅ Updated your Roblox username to **{username}**!\n"
                        f"📊 Your current Roblox rank: **{rank_info['rank_name']}** (Rank {rank_info['rank']})\n"
                        f"✓ Your ranks are already in sync!",
                        ephemeral=True,
                    )
            else:
                await interaction.followup.send(
                    f"❌ That Roblox username is already linked to another Discord account.",
                    ephemeral=True,
                )
        else:
            # Create new member with rank from Roblox
            success = await database.create_member(interaction.user.id, username)
            if success:
                # Set rank to match Roblox (override default)
                await database.set_member_rank(interaction.user.id, target_rank_order)

                # Assign rank role based on Roblox
                await self._assign_rank_role(interaction.user, target_rank_order)

                rank_name = target_db_rank["rank_name"] if target_db_rank else "Pending"

                await interaction.followup.send(
                    f"✅ Successfully linked your account to **{username}**!\n"
                    f"📊 Your current Roblox rank: **{rank_info['rank_name']}** (Rank {rank_info['rank']})\n"
                    f"🎖️ **Discord rank set to:** {rank_name}\n"
                    f"💡 Your ranks will stay synced automatically. Use `/xp` to check your progress.",
                    ephemeral=True,
                )
                logger.info(f"New member {username} linked with rank {rank_name} from Roblox")
            else:
                await interaction.followup.send(
                    f"❌ Failed to link account. That Roblox username might already be taken.",
                    ephemeral=True,
                )

    @app_commands.command(
        name="submit-raid", description="Submit an event (patrol, raid, defense, etc.) for approval"
    )
    @app_commands.checks.cooldown(1, 60)  # 1 use per 60 seconds per user (prevent spam)
    async def submit_raid(self, interaction: discord.Interaction, proof_image: discord.Attachment):
        """Submit an event with proof image."""
        # Check if user is registered
        try:
            member = await database.get_member(interaction.user.id)
        except Exception as e:
            logger.error(f"Database error in submit-raid: {e}", exc_info=True)
            await interaction.response.send_message(
                get_user_error_message(ERROR_CODES["DATABASE_ERROR"]), ephemeral=True
            )
            return

        if not member:
            await interaction.response.send_message(
                "❌ You need to link your Roblox account first! Use `/link-roblox`.", ephemeral=True
            )
            return

        # Validate image attachment with security checks
        is_valid, error_message = validate_image_attachment(proof_image, max_size_mb=10)
        if not is_valid:
            await interaction.response.send_message(error_message, ephemeral=True)
            return

        # Show modal for event details
        modal = RaidSubmissionModal(proof_image.url, interaction.user)
        await interaction.response.send_modal(modal)

    async def _assign_rank_role(self, member: discord.Member, rank_order: int):
        """Assign Discord role based on rank."""
        rank_info = await database.get_rank_by_order(rank_order)
        if not rank_info:
            return

        # Find or create the role with retry logic
        role = discord.utils.get(member.guild.roles, name=rank_info["rank_name"])
        if not role:
            # Create the role if it doesn't exist with retry logic
            for attempt in range(Config.MAX_RATE_LIMIT_RETRIES):
                try:
                    role = await member.guild.create_role(
                        name=rank_info["rank_name"], reason="Clan rank role"
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

        # Assign the role with retry logic
        for attempt in range(Config.MAX_RATE_LIMIT_RETRIES):
            try:
                await member.add_roles(role)
                break
            except discord.Forbidden:
                logger.error("Bot doesn't have permission to assign roles")
                return
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
                    return
                else:
                    logger.error(f"HTTP error adding role: {e}")
                    return

    def _create_progress_bar(self, current: int, target: int, base: int = 0) -> str:
        """Create a visual progress bar."""
        progress = min(1.0, max(0.0, (current - base) / (target - base)))
        filled = int(progress * 10)
        bar = "█" * filled + "░" * (10 - filled)
        return f"[{bar}] {int(progress * 100)}%"


async def setup(bot):
    """Setup function to load the cog."""
    await bot.add_cog(UserCommands(bot))
