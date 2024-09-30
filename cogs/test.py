import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class testcog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name='test', with_app_command=True)
    async def help(self, ctx: commands.Context, number: int = 10):
        if number > 30:
            await ctx.send("Countdown too long, limit is `30` for ratelimiting purposes.", ephemeral=True)
            return
        time = number
        response = await ctx.send(f"Countdown will end in ``{time}`` seconds.")
        await asyncio.sleep(1)
        while time != 0:
            time -= 1
            await response.edit(content=f"Countdown will end in ``{time}`` seconds.")
            await asyncio.sleep(1)
        else:
            await response.edit(content=f"Countdown has ended.")

async def setup(bot: commands.Bot):
    await bot.add_cog(testcog(bot))
