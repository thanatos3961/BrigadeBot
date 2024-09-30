import discord
import discord.app_commands
from discord.ext import commands
import discord.ext
import discord.ext.commands
import token_1
import os
import sqlite3

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="r!", owner_id = 678456343413260307 ,intents=intents)
guild_id = 1162861741902942379

MY_GUILD = discord.Object(id=1162861741902942379)

conn = sqlite3.connect('blacklist.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS blacklist (
    user_id INTEGER PRIMARY KEY
)
''')

conn.commit()
conn.close()

bot_locked = False

bot.remove_command("help")

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Brigade Bot Online"))
    await bot.change_presence(activity=discord.CustomActivity(name="r!help | Pot Brigade", emoji="🖥️"))
    cogs_path = os.path.join(os.path.dirname(__file__), 'cogs')
    for filename in os.listdir(cogs_path):
        if filename.endswith('.py') and filename != '__init__.py':
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f"Loaded extension: {filename[:-3]}")
            except Exception as e:
                print(f"Failed to load extension {filename[:-3]}: {e}")

@bot.event
async def on_command_error(ctx, error):
    channel = bot.get_channel(1267740999644352574)
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(
            title="Command not found.",
            description="Sorry, that is not one of my commands. If you'd like to see a list of my commands, run ``r!help``. I mostly use slash commands.",
            color=discord.Color.dark_red()
        )
        await ctx.send(embed=embed, )
    else:
        # Handle other errors
        embed = discord.Embed(
            title="Error log",
            description=f"An error occured: {error} ",
            color=discord.Color.dark_red()
        )
        await channel.send(embed=embed)

@bot.command(name='lock', description='Locks the bot for everyone except the owner.')
@commands.is_owner()
async def lock(ctx: commands.Context):
    if ctx.author.id != 678456343413260307:
        await ctx.send("You aren't the owner of this bot.", ephemeral=True)
        return
    global bot_locked
    bot_locked = True
    await ctx.send(embed=discord.Embed(
        title="Bot Locked",
        description="The bot is now locked. Only the owner can use commands.",
        color=discord.Color.dark_red()
    ), ephemeral=True)

@bot.tree.command(name='reload', description="Reloads a cog.")
@commands.is_owner()
async def reload(interaction: discord.Interaction, cog_name: str):
    if interaction.user.id != 678456343413260307:
        await interaction.response.send_message("You aren't the owner of this bot.", ephemeral=True)
        return
    try:
        await bot.reload_extension(f"cogs.{cog_name}")
        embed = discord.Embed(
            title="Cog Reloaded",
            description=f"Successfully reloaded the cog `{cog_name}`.",
            color=discord.Color.dark_green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        embed = discord.Embed(
            title="Error",
            description=f"Failed to reload the cog `{cog_name}`: {str(e)}",
            color=discord.Color.dark_red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name='unlock', description='Unlocks the bot for everyone.')
@commands.is_owner()
async def unlock(ctx: commands.Context):
    if ctx.user.id != 678456343413260307:
        await ctx.send("You aren't the owner of this bot.", ephemeral=True)
        return
    global bot_locked
    bot_locked = False
    await ctx.send(embed=discord.Embed(
        title="Bot Unlocked",
        description="The bot is now unlocked. All users can use commands.",
        color=discord.Color.dark_green()
    ), ephemeral=True)

@bot.tree.context_menu(name='Report to Moderators')
async def report_message(interaction: discord.Interaction, message: discord.Message):
    # We're sending this response message with ephemeral=True, so only the command executor can see it
    await interaction.response.send_message(
        f'Thanks for reporting this message by {message.author.mention} to our moderators.', ephemeral=True
    )

    # Handle report by sending it into a log channel
    log_channel = interaction.guild.get_channel(1277482895979708436)  # replace with your channel id

    embed = discord.Embed(title='Reported Message')
    if message.content:
        embed.description = message.content


    embed.add_field(name=f"Reported by: {interaction.user.name} ({interaction.user.id})", value="")

    embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
    embed.timestamp = message.created_at

    url_view = discord.ui.View()
    url_view.add_item(discord.ui.Button(label='Go to Message', style=discord.ButtonStyle.url, url=message.jump_url))

    await log_channel.send(content="## Reported Message",embed=embed, view=url_view)



@bot.command(name="sync")
@commands.is_owner()
async def sync(ctx: commands.Context):
    if ctx.author.id != 678456343413260307:
        await ctx.send("You aren't the owner of this bot.", ephemeral=True) 
    guild = bot.get_guild(guild_id)
    bot.tree.copy_global_to(guild=MY_GUILD)
    await bot.tree.sync()
    print(f"Commands synced for guild: {guild.name} ({guild.id})")
    print(f"Available commands: {[cmd.name for cmd in bot.tree.get_commands(guild=guild)]}")
    await ctx.send(embed=discord.Embed(
            title=f"Commands synced for guild: {guild.name} ({guild.id})",
            description=f"Available commands: {[cmd.name for cmd in bot.tree.get_commands(guild=guild)]}",
            color=discord.Color.dark_green()
        ))


@bot.hybrid_command(name="help", description="Shows this help message")
async def help(ctx: commands.Context):
    embed = discord.Embed(
        title="Bot Commands",
        description="Here are all the available commands:",
        color=discord.Color.orange()
    )
    for command in bot.tree.get_commands(guild=MY_GUILD):
        if isinstance(command, discord.app_commands.Command) and command.description:
            embed.add_field(
                name=f"/{command.name}",
                value=command.description or "No description provided",
                inline=False
            )
    await ctx.send("I sent the list of commands to your DMs.", ephemeral=True)
    dm = await ctx.author.create_dm()
    await dm.send(embed=embed)

@bot.check
async def globally_block_commands(interaction: discord.Interaction):
    if bot_locked and interaction.user.id != bot.owner_id:
        await interaction.response.send_message(embed=discord.Embed(
            title="Locked",
            description="The bot is currently locked. Only the owner can use commands.",
            color=discord.Color.dark_red()
        ), ephemeral=True)
        return False
    return True


# Ensure your bot token is stored in a secure manner and never exposed in your code.
bot.run(token_1.tokenval)
