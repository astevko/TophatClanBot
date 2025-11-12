"""
Admin commands for TophatC Clan Bot
Commands restricted to administrators for managing the clan.
"""

import discord
from discord import app_commands
from discord.ext import commands
import logging

import database
from config import Config
import roblox_api

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
        
        # Method 3: Check if user has the configured admin role
        admin_role = discord.utils.get(interaction.user.roles, name=Config.ADMIN_ROLE_NAME)
        if admin_role:
            return True
        
        # Access denied
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
        await interaction.response.defer(ephemeral=True)
        
        # Check if user is trying to promote themselves
        if member.id == interaction.user.id:
            await interaction.followup.send(
                "❌ You cannot promote yourself! Ask High Command to promote you.",
                ephemeral=True
            )
            return
        
        # Get member data
        member_data = await database.get_member(member.id)
        if not member_data:
            await interaction.followup.send(
                f"❌ {member.mention} is not registered. They need to use `/link-roblox` first.",
                ephemeral=True
            )
            return
        
        # Get next rank (include admin-only ranks for manual promotion)
        next_rank = await database.get_next_rank(member_data['current_rank'], include_admin_only=True)
        if not next_rank:
            await interaction.followup.send(
                f"❌ {member.mention} is already at the maximum rank!",
                ephemeral=True
            )
            return
        
        # Check if rank is admin-only
        is_admin_only = next_rank.get('admin_only', False)
        
        # If not admin-only, check if member has enough points
        if not is_admin_only and member_data['points'] < next_rank['points_required']:
            points_needed = next_rank['points_required'] - member_data['points']
            await interaction.followup.send(
                f"❌ {member.mention} needs {points_needed} more points to be promoted to **{next_rank['rank_name']}**.\n"
                f"Current: {member_data['points']}/{next_rank['points_required']} points",
                ephemeral=True
            )
            return
        
        # Update rank in database
        await database.set_member_rank(member.id, next_rank['rank_order'])
        
        # Update Discord role
        await self._update_member_role(member, member_data['current_rank'], next_rank['rank_order'])
        
        # Update Roblox rank
        roblox_success = False
        try:
            roblox_success = await roblox_api.update_member_rank(
                member_data['roblox_username'],
                next_rank['roblox_group_rank_id']
            )
        except Exception as e:
            logger.error(f"Failed to update Roblox rank: {e}")
        
        # Notify member
        try:
            await member.send(
                f"🎉 **Congratulations!** You've been promoted to **{next_rank['rank_name']}**!\n"
                f"Keep up the great work in the clan!"
            )
        except:
            pass
        
        # Send confirmation
        roblox_status = "✅ Roblox rank updated" if roblox_success else "⚠️ Roblox rank update failed"
        
        embed = discord.Embed(
            title="✅ Promotion Successful",
            description=f"{member.mention} has been promoted!",
            color=discord.Color.green()
        )
        
        embed.add_field(name="Previous Rank", value=member_data['rank_name'], inline=True)
        embed.add_field(name="New Rank", value=next_rank['rank_name'], inline=True)
        embed.add_field(name="Total Points", value=str(member_data['points']), inline=True)
        
        # Show rank type
        if is_admin_only:
            embed.add_field(name="Rank Type", value="⚡ HICOM-Granted Rank (Manual Promotion)", inline=False)
        else:
            embed.add_field(name="Rank Type", value="📊 Point-Based Rank", inline=False)
        
        embed.add_field(name="Roblox Sync", value=roblox_status, inline=False)
        
        await interaction.followup.send(embed=embed, ephemeral=True)
        
        # Announce in server (optional - you can customize this)
        # announcement_channel = interaction.channel
        # await announcement_channel.send(
        #     f"🎉 Congratulations to {member.mention} on their promotion to **{next_rank['rank_name']}**!"
        # )
    
    @app_commands.command(name="add-points", description="[ELITE+] Manually add or remove points from a member")
    @app_commands.describe(
        member="The member to adjust points for",
        points="Points to add (positive) or remove (negative)"
    )
    @is_admin()
    async def add_points(self, interaction: discord.Interaction, member: discord.Member, points: int):
        """Add or remove points from a member."""
        await interaction.response.defer(ephemeral=True)
        
        # Check if user is trying to add points to themselves
        if member.id == interaction.user.id:
            await interaction.followup.send(
                "❌ You cannot add points to yourself! Ask HICOM to adjust your points.",
                ephemeral=True
            )
            return
        
        # Get member data
        member_data = await database.get_member(member.id)
        if not member_data:
            await interaction.followup.send(
                f"❌ {member.mention} is not registered. They need to use `/link-roblox` first.",
                ephemeral=True
            )
            return
        
        # Validate points won't go negative
        new_points = member_data['points'] + points
        if new_points < 0:
            await interaction.followup.send(
                f"❌ Cannot remove {abs(points)} points. Member only has {member_data['points']} points.",
                ephemeral=True
            )
            return
        
        # Update points
        await database.add_points(member.id, points)
        
        # Notify member
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
        except:
            pass
        
        # Send confirmation
        action = "added to" if points > 0 else "removed from"
        embed = discord.Embed(
            title="✅ Points Updated",
            description=f"{abs(points)} points {action} {member.mention}",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Previous Points", value=str(member_data['points']), inline=True)
        embed.add_field(name="Change", value=f"{points:+d}", inline=True)
        embed.add_field(name="New Points", value=str(new_points), inline=True)
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @app_commands.command(name="set-admin-channel", description="[ADMIN] Set the channel for raid submissions")
    @app_commands.describe(channel="The channel where raid submissions will be posted")
    @is_admin()
    async def set_admin_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Set the admin channel for raid submissions."""
        await interaction.response.defer(ephemeral=True)
        
        # Update config
        await database.set_config("admin_channel_id", str(channel.id))
        
        await interaction.followup.send(
            f"✅ Admin channel set to {channel.mention}. All raid submissions will be posted there.",
            ephemeral=True
        )
    
    @app_commands.command(name="view-pending", description="[HICOM] View all pending raid submissions")
    @is_admin()
    async def view_pending(self, interaction: discord.Interaction):
        """View all pending raid submissions."""
        await interaction.response.defer(ephemeral=True)
        
        pending = await database.get_pending_submissions()
        
        if not pending:
            await interaction.followup.send(
                "📋 No pending raid submissions.",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="📋 Pending Raid Submissions",
            description=f"There are {len(pending)} pending submission(s)",
            color=discord.Color.blue()
        )
        
        for submission in pending[:10]:  # Show first 10
            submitter = interaction.guild.get_member(submission['submitter_id'])
            submitter_name = submitter.mention if submitter else f"Unknown ({submission['submitter_id']})"
            
            embed.add_field(
                name=f"Submission #{submission['submission_id']}",
                value=(
                    f"**Submitter:** {submitter_name}\n"
                    f"**Start:** {submission['start_time']}\n"
                    f"**End:** {submission['end_time']}\n"
                    f"**Participants:** {submission['participants'][:100]}..."
                ),
                inline=False
            )
        
        if len(pending) > 10:
            embed.set_footer(text=f"Showing 10 of {len(pending)} submissions")
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @app_commands.command(name="check-member", description="[HICOM] Check a member's stats and rank eligibility")
    @app_commands.describe(member="The member to check")
    @is_admin()
    async def check_member(self, interaction: discord.Interaction, member: discord.Member):
        """Check a member's detailed stats."""
        await interaction.response.defer(ephemeral=True)
        
        member_data = await database.get_member(member.id)
        if not member_data:
            await interaction.followup.send(
                f"❌ {member.mention} is not registered.",
                ephemeral=True
            )
            return
        
        # Get next rank info
        next_rank = await database.get_next_rank(member_data['current_rank'])
        
        embed = discord.Embed(
            title=f"📊 Member Stats: {member.display_name}",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Discord", value=member.mention, inline=True)
        embed.add_field(name="Roblox", value=member_data['roblox_username'], inline=True)
        embed.add_field(name="Member Since", value=member_data['created_at'][:10], inline=True)
        
        # Get current rank details
        current_rank_info = await database.get_rank_by_order(member_data['current_rank'])
        is_current_admin_only = current_rank_info.get('admin_only', False) if current_rank_info else False
        
        embed.add_field(name="Current Rank", value=member_data['rank_name'], inline=True)
        embed.add_field(name="Total Points", value=str(member_data['points']), inline=True)
        
        # Show rank type
        rank_type = "⚡ Admin-Only" if is_current_admin_only else "📊 Point-Based"
        embed.add_field(name="Rank Type", value=rank_type, inline=True)
        
        # Get next point-based rank (for automatic promotion eligibility)
        next_point_rank = await database.get_next_rank(member_data['current_rank'], include_admin_only=False)
        
        if next_point_rank:
            points_needed = next_point_rank['points_required'] - member_data['points']
            eligible = "✅ Eligible for Promotion" if points_needed <= 0 else f"❌ Needs {points_needed} more points"
            
            embed.add_field(name="Next Point-Based Rank", value=next_point_rank['rank_name'], inline=True)
            embed.add_field(
                name="Auto-Promotion Status",
                value=f"{eligible}\n({member_data['points']}/{next_point_rank['points_required']} points)",
                inline=False
            )
        else:
            embed.add_field(name="Point-Based Progress", value="🏆 Maximum point-based rank achieved", inline=False)
        
        # Note about admin ranks
        if is_current_admin_only:
            embed.add_field(
                name="ℹ️ Note",
                value="This member has an HICOM-granted rank. Use `/promote` to change ranks manually.",
                inline=False
            )
        
        embed.set_thumbnail(url=member.display_avatar.url)
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @app_commands.command(name="list-ranks", description="[ADMIN] View all rank requirements")
    @is_admin()
    async def list_ranks(self, interaction: discord.Interaction):
        """List all ranks and their requirements."""
        await interaction.response.defer(ephemeral=True)
        
        ranks = await database.get_all_ranks()
        
        # Separate ranks by type
        point_based_ranks = [r for r in ranks if not r.get('admin_only', False)]
        admin_only_ranks = [r for r in ranks if r.get('admin_only', False)]
        
        embed = discord.Embed(
            title="🎖️ Clan Rank System",
            description="Complete overview of all ranks",
            color=discord.Color.gold()
        )
        
        # Point-Based Ranks Section
        if point_based_ranks:
            point_ranks_text = ""
            for rank in point_based_ranks:
                point_ranks_text += f"**{rank['rank_order']}. {rank['rank_name']}** - {rank['points_required']} pts\n"
            
            embed.add_field(
                name="📊 Point-Based Ranks (Earn through raids)",
                value=point_ranks_text,
                inline=False
            )
        
        # Admin-Only Ranks Section
        if admin_only_ranks:
            # Group by category
            leadership = [r for r in admin_only_ranks if r['rank_order'] in [10, 11, 12, 13, 14]]
            honorary = [r for r in admin_only_ranks if r['rank_order'] in [15, 16, 17, 18]]
            trial = [r for r in admin_only_ranks if r['rank_order'] in [19, 20]]
            
            if leadership:
                leadership_text = "\n".join([f"**{r['rank_order']}. {r['rank_name']}**" for r in leadership])
                embed.add_field(
                    name="⚡ Leadership Ranks (HICOM-granted)",
                    value=leadership_text,
                    inline=True
                )
            
            if honorary:
                honorary_text = "\n".join([f"**{r['rank_order']}. {r['rank_name']}**" for r in honorary])
                embed.add_field(
                    name="🏆 Honorary Ranks (HICOM-Granted)",
                    value=honorary_text,
                    inline=True
                )
            
            if trial:
                trial_text = "\n".join([f"**{r['rank_order']}. {r['rank_name']}**" for r in trial])
                embed.add_field(
                    name="🔰 Trial/Probation (HICOM-ranted)",
                    value=trial_text,
                    inline=True
                )
        
        embed.set_footer(text="Use /promote to assign any rank manually | /check-member to see eligibility")
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    async def _update_member_role(self, member: discord.Member, old_rank_order: int, new_rank_order: int):
        """Update member's Discord role when promoted."""
        # Get old and new rank info
        old_rank = await database.get_rank_by_order(old_rank_order)
        new_rank = await database.get_rank_by_order(new_rank_order)
        
        if not old_rank or not new_rank:
            return
        
        # Remove old rank role
        old_role = discord.utils.get(member.guild.roles, name=old_rank['rank_name'])
        if old_role:
            try:
                await member.remove_roles(old_role)
            except discord.Forbidden:
                logger.error("Bot doesn't have permission to remove roles")
        
        # Add new rank role
        new_role = discord.utils.get(member.guild.roles, name=new_rank['rank_name'])
        if not new_role:
            # Create the role if it doesn't exist
            try:
                new_role = await member.guild.create_role(
                    name=new_rank['rank_name'],
                    reason="Clan rank role"
                )
            except discord.Forbidden:
                logger.error("Bot doesn't have permission to create roles")
                return
        
        try:
            await member.add_roles(new_role)
        except discord.Forbidden:
            logger.error("Bot doesn't have permission to assign roles")


async def setup(bot):
    """Setup function to load the cog."""
    await bot.add_cog(AdminCommands(bot))

