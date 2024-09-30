import discord
from discord.ext import commands
from discord import app_commands
from typing import Literal
import asyncio

checkmark = "<:BrigadeAccepted:1281028040318652528>"
denied = "<:BrigadeDenied:1281026311682392134>"

successful = discord.Color.dark_green()
unsuccessful = discord.Color.dark_red()

class ModerationCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="ban", description="Removes a user from the server with specified ban length")
    @commands.has_permissions(ban_members=True)
    async def ban(
        self, 
        ctx: commands.Context, 
        member: discord.Member = None, 
        length: Literal["Permanent", "7 Days", "30 Days", "90 Days"] = "Permanent", 
        reason: str = "No reason provided"
    ):
        if not ctx.author.guild_permissions.ban_members:
            embed = discord.Embed(
                title=None,
                description="<:BrigadeDenied:1281026311682392134> | You don't have the required permissions to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        if member is None:
            embed = discord.Embed(
                title="Ban Failed", 
                description=f"{denied} Please specify a user to ban.", 
                color=unsuccessful
            )
            embed.add_field(name="Command Issued By", value=ctx.author.mention)
            await ctx.send(embed=embed)
            return
        
        if member == ctx.author:
            embed = discord.Embed(
                title="Ban Failed", 
                description=f"{denied} You cannot ban yourself.", 
                color=unsuccessful
            )
            embed.add_field(name="Command Issued By", value=ctx.author.mention)
            await ctx.send(embed=embed)
            return

        # Calculate unban time if it's not permanent
        unban_time = None
        if length == "7 Days":
            unban_time = 7 * 86400  # 7 days in seconds
        elif length == "30 Days":
            unban_time = 30 * 86400  # 30 days in seconds
        elif length == "90 Days":
            unban_time = 90 * 86400  # 90 days in seconds

        try:
            # Ban the member
            await member.ban(reason=reason)
            
            # Create a detailed embed for the ban
            embed = discord.Embed(
                title="Ban Successful", 
                description=f"{checkmark} {member.mention} has been banned.",
                color=successful,
                timestamp=ctx.message.created_at  # Adds timestamp to embed
            )
            embed.add_field(name="Banned User", value=f"{member.mention} (ID: {member.id})", inline=False)
            embed.add_field(name="Ban Length", value=length, inline=True)
            embed.add_field(name="Reason", value=reason, inline=True)
            embed.add_field(name="Issued By", value=ctx.author.mention, inline=True)
            embed.set_thumbnail(url=member.display_avatar.url)  # User's avatar in embed
            embed.set_footer(text=f"Ban command issued by {ctx.author.name}", icon_url=ctx.author.display_avatar.url)

            await ctx.send(embed=embed)

            # Schedule unban if necessary
            if unban_time is not None:
                await asyncio.sleep(unban_time)
                await ctx.guild.unban(member)
                
                # Unban notification with detailed embed
                unban_embed = discord.Embed(
                    title="Unban Notification",
                    description=f"{member.mention} has been automatically unbanned after {length}.",
                    color=successful,
                    timestamp=discord.utils.utcnow()  # Current time for the unban
                )
                unban_embed.add_field(name="Unbanned User", value=f"{member.mention} (ID: {member.id})", inline=False)
                unban_embed.add_field(name="Original Ban Duration", value=length, inline=True)
                unban_embed.add_field(name="Unban Initiated By", value="System (Automatic)", inline=True)
                await ctx.send(embed=unban_embed)

        except discord.Forbidden:
            # If bot lacks permissions
            embed = discord.Embed(
                title="Ban Failed", 
                description=f"{denied} I do not have permission to ban {member.mention}.", 
                color=unsuccessful
            )
            embed.add_field(name="Attempted User", value=f"{member.mention} (ID: {member.id})", inline=False)
            embed.add_field(name="Issued By", value=ctx.author.mention, inline=True)
            await ctx.send(embed=embed)

        except Exception as e:
            # If something unexpected went wrong
            embed = discord.Embed(
                title="Ban Failed", 
                description=f"{denied} Something went wrong: {str(e)}.", 
                color=unsuccessful
            )
            embed.add_field(name="Issued By", value=ctx.author.mention, inline=True)
            await ctx.send(embed=embed)

    # Optional unban command (just in case you want to manually unban users later)
    @commands.hybrid_command(name="unban", description="Unbans a user from the server")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx: commands.Context, user: discord.User):
        try:
            await ctx.guild.unban(user)
            
            # Unban confirmation embed
            embed = discord.Embed(
                title="Unban Successful", 
                description=f"{checkmark} {user.mention} has been unbanned.", 
                color=successful
            )
            embed.add_field(name="Unbanned User", value=f"{user.mention} (ID: {user.id})", inline=False)
            embed.add_field(name="Issued By", value=ctx.author.mention, inline=True)
            await ctx.send(embed=embed)
        
        except discord.NotFound:
            embed = discord.Embed(
                title="Unban Failed", 
                description=f"{denied} User {user.mention} is not banned or doesn't exist.", 
                color=unsuccessful
            )
            await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(ModerationCog(bot))
