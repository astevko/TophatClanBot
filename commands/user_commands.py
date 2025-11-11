"""
User commands for TophatC Clan Bot
Commands available to all clan members.
"""

import discord
from discord import app_commands
from discord.ext import commands
import logging
from typing import Optional
import re

import database
from config import Config

logger = logging.getLogger(__name__)


class RaidSubmissionModal(discord.ui.Modal, title="Submit Raid Event"):
    """Modal for collecting raid submission details."""
    
    participants = discord.ui.TextInput(
        label="Participants",
        placeholder="@user1 @user2 @user3 or mention them by name",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=1000
    )
    
    start_time = discord.ui.TextInput(
        label="Raid Start Time",
        placeholder="e.g., 2024-11-09 14:30 or 2:30 PM EST",
        style=discord.TextStyle.short,
        required=True,
        max_length=100
    )
    
    end_time = discord.ui.TextInput(
        label="Raid End Time",
        placeholder="e.g., 2024-11-09 16:00 or 4:00 PM EST",
        style=discord.TextStyle.short,
        required=True,
        max_length=100
    )
    
    def __init__(self, image_url: str, submitter: discord.Member):
        super().__init__()
        self.image_url = image_url
        self.submitter = submitter
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle the modal submission."""
        await interaction.response.defer(ephemeral=True)
        
        # Parse participants (extract user IDs from mentions)
        participants_text = self.participants.value
        
        # Store submission in database
        submission_id = await database.create_raid_submission(
            submitter_id=self.submitter.id,
            participants=participants_text,
            start_time=self.start_time.value,
            end_time=self.end_time.value,
            image_url=self.image_url
        )
        
        # Get admin channel
        admin_channel_id = await database.get_config("admin_channel_id")
        if not admin_channel_id:
            admin_channel_id = Config.ADMIN_CHANNEL_ID
        
        if not admin_channel_id:
            await interaction.followup.send(
                "❌ Admin channel not configured. Please contact an administrator.",
                ephemeral=True
            )
            return
        
        admin_channel = interaction.guild.get_channel(int(admin_channel_id))
        if not admin_channel:
            await interaction.followup.send(
                "❌ Could not find admin channel. Please contact an administrator.",
                ephemeral=True
            )
            return
        
        # Create embed for admin review
        embed = discord.Embed(
            title="🎯 New Raid Submission",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        
        embed.add_field(name="Submitted By", value=self.submitter.mention, inline=True)
        embed.add_field(name="Submission ID", value=f"#{submission_id}", inline=True)
        embed.add_field(name="Status", value="⏳ Pending Review", inline=True)
        
        embed.add_field(name="Participants", value=participants_text, inline=False)
        embed.add_field(name="Start Time", value=self.start_time.value, inline=True)
        embed.add_field(name="End Time", value=self.end_time.value, inline=True)
        
        embed.set_image(url=self.image_url)
        embed.set_footer(text=f"Submission ID: {submission_id}")
        
        # Create approval buttons
        view = RaidApprovalView(submission_id)
        
        await admin_channel.send(embed=embed, view=view)
        
        await interaction.followup.send(
            "✅ Raid submission sent for admin review! You'll be notified once it's processed.",
            ephemeral=True
        )


class RaidApprovalView(discord.ui.View):
    """View with Approve/Decline buttons for raid submissions."""
    
    def __init__(self, submission_id: int):
        super().__init__(timeout=None)  # No timeout - buttons work indefinitely
        self.submission_id = submission_id
        
        # Add custom_id for persistence
        self.approve_button = discord.ui.Button(
            label="Approve",
            style=discord.ButtonStyle.green,
            custom_id=f"raid_approve_{submission_id}"
        )
        self.approve_button.callback = self.approve_callback
        
        self.decline_button = discord.ui.Button(
            label="Decline",
            style=discord.ButtonStyle.red,
            custom_id=f"raid_decline_{submission_id}"
        )
        self.decline_button.callback = self.decline_callback
        
        self.add_item(self.approve_button)
        self.add_item(self.decline_button)
    
    async def approve_callback(self, interaction: discord.Interaction):
        """Handle approve button click."""
        # Check if user has admin permissions
        if not interaction.user.guild_permissions.administrator:
            admin_role = discord.utils.get(interaction.user.roles, name=Config.ADMIN_ROLE_NAME)
            if not admin_role:
                await interaction.response.send_message(
                    "❌ You don't have permission to approve raids.",
                    ephemeral=True
                )
                return
        
        # Show modal to get points
        modal = PointsInputModal(self.submission_id, interaction)
        await interaction.response.send_modal(modal)
    
    async def decline_callback(self, interaction: discord.Interaction):
        """Handle decline button click."""
        # Check if user has admin permissions
        if not interaction.user.guild_permissions.administrator:
            admin_role = discord.utils.get(interaction.user.roles, name=Config.ADMIN_ROLE_NAME)
            if not admin_role:
                await interaction.response.send_message(
                    "❌ You don't have permission to decline raids.",
                    ephemeral=True
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
            submitter = interaction.guild.get_member(submission['submitter_id'])
            if submitter:
                await submitter.send(
                    f"❌ Your raid submission #{self.submission_id} has been declined by {interaction.user.mention}."
                )
        except:
            pass
        
        await interaction.followup.send("✅ Raid submission declined.", ephemeral=True)


class PointsInputModal(discord.ui.Modal, title="Award Points"):
    """Modal for inputting points to award."""
    
    points = discord.ui.TextInput(
        label="Points to Award (1-8)",
        placeholder="Enter a number between 1 and 8",
        style=discord.TextStyle.short,
        required=True,
        min_length=1,
        max_length=1
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
                    "❌ Points must be between 1 and 8.",
                    ephemeral=True
                )
                return
        except ValueError:
            await interaction.followup.send(
                "❌ Invalid points value. Please enter a number between 1 and 8.",
                ephemeral=True
            )
            return
        
        # Get submission details
        submission = await database.get_raid_submission(self.submission_id)
        if not submission:
            await interaction.followup.send("❌ Submission not found.", ephemeral=True)
            return
        
        # Update database
        await database.approve_raid_submission(
            self.submission_id,
            interaction.user.id,
            points_value
        )
        
        # Parse and award points to participants
        participants_text = submission['participants']
        participant_ids = re.findall(r'<@!?(\d+)>', participants_text)
        
        awarded_members = []
        for user_id in participant_ids:
            user_id_int = int(user_id)
            member = await database.get_member(user_id_int)
            
            if member:
                await database.add_points(user_id_int, points_value)
                awarded_members.append(f"<@{user_id_int}>")
        
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
        
        # Notify participants
        for user_id in participant_ids:
            try:
                member = interaction.guild.get_member(int(user_id))
                if member:
                    await member.send(
                        f"🎉 You've been awarded **{points_value} points** for raid #{self.submission_id}!\n"
                        f"Use `/xp` to check your progress."
                    )
            except:
                pass
        
        await interaction.followup.send(
            f"✅ Awarded {points_value} points to {len(participant_ids)} participant(s).",
            ephemeral=True
        )


class UserCommands(commands.Cog):
    """User commands cog."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="xp", description="Check your current rank and points progress")
    async def xp(self, interaction: discord.Interaction):
        """Check your XP and rank progress."""
        member = await database.get_member(interaction.user.id)
        
        if not member:
            await interaction.response.send_message(
                "❌ You're not registered yet! Use `/link-roblox` to link your Roblox account.",
                ephemeral=True
            )
            return
        
        # Get current rank details
        current_rank_info = await database.get_rank_by_order(member['current_rank'])
        is_admin_only = current_rank_info.get('admin_only', False) if current_rank_info else False
        
        # Get next point-based rank only (not admin-only ranks)
        next_rank = await database.get_next_rank(member['current_rank'], include_admin_only=False)
        
        embed = discord.Embed(
            title=f"📊 {interaction.user.display_name}'s Progress",
            color=discord.Color.blue()
        )
        
        # Show current rank with type indicator
        rank_display = f"**{member['rank_name']}**"
        if is_admin_only:
            rank_display += " ⚡"
        
        embed.add_field(
            name="Current Rank",
            value=rank_display,
            inline=True
        )
        
        embed.add_field(
            name="Total Points",
            value=f"**{member['points']}**",
            inline=True
        )
        
        # Show rank type
        rank_type = "⚡ Admin-Granted" if is_admin_only else "📊 Point-Based"
        embed.add_field(
            name="Rank Type",
            value=rank_type,
            inline=True
        )
        
        if next_rank:
            points_needed = next_rank['points_required'] - member['points']
            progress_bar = self._create_progress_bar(
                member['points'],
                next_rank['points_required'],
                member.get('points_required', 0)
            )
            
            embed.add_field(
                name="Next Point-Based Rank",
                value=f"**{next_rank['rank_name']}**",
                inline=True
            )
            
            embed.add_field(
                name="Progress to Next Rank",
                value=f"{progress_bar}\n{member['points']}/{next_rank['points_required']} ({points_needed} points needed)",
                inline=False
            )
        else:
            embed.add_field(
                name="Status",
                value="🏆 **Maximum Point-Based Rank Achieved!**",
                inline=False
            )
        
        # Add note for admin-only ranks
        if is_admin_only:
            embed.add_field(
                name="ℹ️ Note",
                value="You have an admin-granted rank. Points still count toward point-based ranks!",
                inline=False
            )
        
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_footer(text=f"Roblox: {member['roblox_username']}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="show-my-id", description="Get your Discord User ID for admin configuration")
    async def show_my_id(self, interaction: discord.Interaction):
        """Show user their Discord ID."""
        embed = discord.Embed(
            title="📋 Your Discord User ID",
            description=f"Your Discord User ID is: **`{interaction.user.id}`**",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="What is this?",
            value="This is your unique Discord identifier. Admins can use this to grant you special permissions.",
            inline=False
        )
        
        embed.add_field(
            name="How to use",
            value=(
                "To add you as a bot admin, the server owner needs to:\n"
                f"1. Add `{interaction.user.id}` to ADMIN_USER_IDS in .env\n"
                "2. Restart the bot"
            ),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="leaderboard", description="View the top clan members by points")
    async def leaderboard(self, interaction: discord.Interaction):
        """Display the clan leaderboard."""
        members = await database.get_leaderboard(10)
        
        if not members:
            await interaction.response.send_message(
                "📊 No members found in the leaderboard yet.",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="🏆 TophatC Clan Leaderboard",
            description="Top 10 members by activity points",
            color=discord.Color.gold()
        )
        
        medals = ["🥇", "🥈", "🥉"]
        
        leaderboard_text = ""
        for idx, member in enumerate(members):
            medal = medals[idx] if idx < 3 else f"**{idx + 1}.**"
            user = interaction.guild.get_member(member['discord_id'])
            username = user.mention if user else member['roblox_username']
            
            leaderboard_text += (
                f"{medal} {username} - "
                f"**{member['rank_name']}** ({member['points']} pts)\n"
            )
        
        embed.description = leaderboard_text
        embed.set_footer(text="Keep raiding to climb the ranks!")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="link-roblox", description="Link your Discord account to your Roblox username")
    @app_commands.describe(username="Your Roblox username")
    async def link_roblox(self, interaction: discord.Interaction, username: str):
        """Link Discord account to Roblox username."""
        await interaction.response.defer(ephemeral=True)
        
        # Check if user already exists
        existing_member = await database.get_member(interaction.user.id)
        
        if existing_member:
            # Update existing member
            success = await database.update_member_roblox(interaction.user.id, username)
            if success:
                await interaction.followup.send(
                    f"✅ Updated your Roblox username to **{username}**!",
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    f"❌ That Roblox username is already linked to another Discord account.",
                    ephemeral=True
                )
        else:
            # Create new member
            success = await database.create_member(interaction.user.id, username)
            if success:
                # Assign initial rank role
                await self._assign_rank_role(interaction.user, 1)
                
                await interaction.followup.send(
                    f"✅ Successfully linked your account to **{username}**!\n"
                    f"You've been assigned the **Private** rank. Use `/xp` to check your progress.",
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    f"❌ Failed to link account. That Roblox username might already be taken.",
                    ephemeral=True
                )
    
    @app_commands.command(name="submit-raid", description="Submit a raid event for approval")
    async def submit_raid(
        self,
        interaction: discord.Interaction,
        proof_image: discord.Attachment
    ):
        """Submit a raid event with proof image."""
        # Check if user is registered
        member = await database.get_member(interaction.user.id)
        if not member:
            await interaction.response.send_message(
                "❌ You need to link your Roblox account first! Use `/link-roblox`.",
                ephemeral=True
            )
            return
        
        # Validate image attachment
        if not proof_image.content_type or not proof_image.content_type.startswith('image/'):
            await interaction.response.send_message(
                "❌ Please attach a valid image file as proof.",
                ephemeral=True
            )
            return
        
        # Show modal for raid details
        modal = RaidSubmissionModal(proof_image.url, interaction.user)
        await interaction.response.send_modal(modal)
    
    async def _assign_rank_role(self, member: discord.Member, rank_order: int):
        """Assign Discord role based on rank."""
        rank_info = await database.get_rank_by_order(rank_order)
        if not rank_info:
            return
        
        # Find or create the role
        role = discord.utils.get(member.guild.roles, name=rank_info['rank_name'])
        if not role:
            # Create the role if it doesn't exist
            try:
                role = await member.guild.create_role(
                    name=rank_info['rank_name'],
                    reason="Clan rank role"
                )
            except discord.Forbidden:
                logger.error("Bot doesn't have permission to create roles")
                return
        
        # Assign the role
        try:
            await member.add_roles(role)
        except discord.Forbidden:
            logger.error("Bot doesn't have permission to assign roles")
    
    def _create_progress_bar(self, current: int, target: int, base: int = 0) -> str:
        """Create a visual progress bar."""
        progress = min(1.0, max(0.0, (current - base) / (target - base)))
        filled = int(progress * 10)
        bar = "█" * filled + "░" * (10 - filled)
        return f"[{bar}] {int(progress * 100)}%"


async def setup(bot):
    """Setup function to load the cog."""
    await bot.add_cog(UserCommands(bot))

