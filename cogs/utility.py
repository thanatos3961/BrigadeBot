import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class UtilityCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="clean", description="Deletes a set amount of messages at once.")
    async def clear(self, ctx: commands.Context, number: int = 5):
        if number < 0:
            embed = discord.Embed(
                title="Invalid Amount",
                
            )

    @commands.hybrid_command(name="status", description="Shows the status and the latency of the bot.")
    async def status(self, ctx: commands.Context):
        latency = round(self.bot.latency * 1000)
        await ctx.send(f"Online! Latency: **{latency}ms**")

    @commands.hybrid_command(name="ping", description="Shows the latency of the bot.")
    async def ping(self, ctx: commands.Context):
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(title=f"Pong! {latency}MS", color=discord.Color.dark_green())
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="culag", description="Clears a members roles.")
    async def culag(self, ctx: commands.Context, member: discord.Member = None):
        if not ctx.author.guild_permissions.mute_members:
            embed = discord.Embed(
                title="Permission Denied",
                description="You don't have the required permissions to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        elif member == None:
            embed = discord.Embed(
                title="Invalid Member",
                description="Please specify a member.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        elif member.guild_permissions.mute_members or member.guild_permissions.kick_members:
            if ctx.author.id == 678456343413260307:
                culagRole = ctx.guild.get_role(1271824207839363234)
                await member.edit(roles=[culagRole])
                embed = discord.Embed(
                    title="Member sent to the slammer.",
                    description=f"{member.name} Was successfully culagged.",
                    color=discord.Color.dark_green()
                )
                await ctx.send(embed=embed)
                return
            else:
                embed = discord.Embed(
                title="Invalid Member",
                description=f"You can't culag ``{member}``, they are an officer...",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        else:
            culagRole = ctx.guild.get_role(1271824207839363234)
            await member.edit(roles=[culagRole])
            embed = discord.Embed(
                title="Member sent to the slammer.",
                description=f"{member.name} Was successfully culagged.",
                color=discord.Color.dark_green()
            )
            await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(UtilityCog(bot))
