import discord
from discord.ext import commands
from discord.ui import View, Button
from datetime import datetime
import sqlite3

checkmark = "<:BrigadeAccepted:1281028040318652528>"
denied = "<:BrigadeDenied:1281026311682392134>"

successful = discord.Color.dark_green()
unsuccessful = discord.Color.dark_red()

class ProfileCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.embed_color = discord.Color.yellow()
        self.vc_start_time = {}
        
        # PROFILE DATABASE

        self.conn = sqlite3.connect('brigadeProfiles.db')
        self.c = self.conn.cursor()

        self.c.execute('''CREATE TABLE IF NOT EXISTS profiles (
                            user_id INTEGER PRIMARY KEY,
                            username TEXT,
                            bio TEXT,
                            vc_time INTEGER DEFAULT 0
                        )''')

        self.c.execute('''CREATE TABLE IF NOT EXISTS followers (
                            follower_id INTEGER,
                            following_id INTEGER,
                            PRIMARY KEY (follower_id, following_id)
                        )''')

        self.conn.commit()


    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if before.channel and not after.channel:
            if member.id in self.vc_start_time:
                start_time = self.vc_start_time.pop(member.id)
                vc_time = int((datetime.now() - start_time).total_seconds())
                
                self.c.execute('UPDATE profiles SET vc_time = vc_time + ? WHERE user_id = ?', (vc_time, member.id))
                self.conn.commit()

        elif after.channel and not before.channel:
            self.vc_start_time[member.id] = datetime.now()

    @commands.hybrid_command(name='register')
    async def register(self, ctx: commands.Context):
        user_id = ctx.author.id
        username = ctx.author.name

        self.c.execute('SELECT * FROM profiles WHERE user_id = ?', (user_id,))
        profile = self.c.fetchone()

        if profile:
            embed = discord.Embed(
                title=None,
                description="<:BrigadeAccepted:1281028040318652528> | You already have a profile.",
                color=discord.Color.yellow()
            )
        else:
            self.c.execute('INSERT INTO profiles (user_id, username, bio) VALUES (?, ?, ?)', (user_id, username, ""))
            self.conn.commit()
            embed = discord.Embed(
                title=None,
                description=f"<:BrigadeAccepted:1281028040318652528> | {username}, your profile has been created!",
                color=discord.Color.yellow()
            )

        await ctx.send(embed=embed)


    @commands.hybrid_command(name='profile')
    async def profile(self, ctx: commands.Context, member: discord.Member = None):
        if member is None:
            member = ctx.author

        user_id = member.id
        self.c.execute('SELECT * FROM profiles WHERE user_id = ?', (user_id,))
        profile = self.c.fetchone()

        if profile:
            self.c.execute('SELECT COUNT(*) FROM followers WHERE following_id = ?', (user_id,))
            follower_count = self.c.fetchone()[0]

            vc_time_seconds = profile[3]
            vc_time_str = f"{vc_time_seconds // 3600}h {vc_time_seconds % 3600 // 60}m {vc_time_seconds % 60}s"

            embed = discord.Embed(
                title=f"{member.display_name}'s Profile",
                description=f"**Username:** {member.name}\n**Bio:** ```{profile[2]}```",
                color=discord.Color.yellow(),
            )
            embed.add_field(
                name=f"**Followers:**",
                value=f"`{follower_count}`",
                inline=False,
            )
            embed.add_field(
                name=f"**Total VC Time:**",
                value=f"`{vc_time_str}`",
                inline=False,
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text="Please refer to server rules when setting your bio.")

            view = ProfileEditView(member)

            await ctx.send(embed=embed, view=view)
        else:
            embed = discord.Embed(
                title=None,
                description=f"<:BrigadeDenied:1281026311682392134> | `{member.name}` doesn't have a profile yet.",
                color=discord.Color.yellow()
            )
            await ctx.send(embed=embed)



    @commands.hybrid_command(name='delete')
    async def delete(self, ctx: commands.Context):
        user_id = ctx.author.id

        self.c.execute('SELECT * FROM profiles WHERE user_id = ?', (user_id,))
        profile = self.c.fetchone()

        if profile:
            self.c.execute('DELETE FROM profiles WHERE user_id = ?', (user_id,))
            self.c.execute('DELETE FROM followers WHERE following_id = ? OR follower_id = ?', (user_id, user_id))
            self.conn.commit()
            embed = discord.Embed(
                title=None,
                description="<:BrigadeAccepted:1281028040318652528> | Your profile has been deleted.",
                color=discord.Color.yellow()
            )
        else:
            embed = discord.Embed(
                title=None,
                description="<:BrigadeDenied:1281026311682392134> | You don't have a profile to delete.",
                color=discord.Color.yellow()
            )

        await ctx.send(embed=embed)


    @commands.hybrid_command(name='follow')
    async def follow(self, ctx: commands.Context, member: discord.Member):
        follower_id = ctx.author.id
        following_id = member.id

        self.c.execute('SELECT * FROM followers WHERE follower_id = ? AND following_id = ?', (follower_id, following_id))
        follow_record = self.c.fetchone()

        if follow_record:
            embed = discord.Embed(
                title=None,
                description=f"<:BrigadeDenied:1281026311682392134> | You're already following {member.name}!",
                color=discord.Color.yellow()
            )
            await ctx.send(embed=embed)
        else:
            self.c.execute('INSERT INTO followers (follower_id, following_id) VALUES (?, ?)', (follower_id, following_id))
            self.conn.commit()

            embed = discord.Embed(
                title=None,
                description=f"<:BrigadeAccepted:1281028040318652528> | You're now following {member.name}!",
                color=discord.Color.yellow()
            )

            await ctx.send(embed=embed)


    @commands.hybrid_command(name='force-delete', description="Force delete a user's profile for moderation.")
    async def force_delete(self, ctx: commands.Context, member: discord.Member):
        if not ctx.author.guild_permissions.mute_members:
            embed = discord.Embed(
                title=None,
                description="<:BrigadeDenied:1281026311682392134> | You don't have the required permissions to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        user_id = member.id

        self.c.execute('SELECT * FROM profiles WHERE user_id = ?', (user_id,))
        profile = self.c.fetchone()

        if profile:
            self.c.execute('DELETE FROM profiles WHERE user_id = ?', (user_id,))
            self.c.execute('DELETE FROM followers WHERE following_id = ? OR follower_id = ?', (user_id, user_id))
            self.conn.commit()

            embed = discord.Embed(
                title=None  ,
                description=f"<:BrigadeAccepted:1281028040318652528> | {member.name}'s profile has been forcefully deleted",
                color=self.embed_color
            )
        else:
            embed = discord.Embed(
                title=None,
                description=f"<:BrigadeDenied:1281026311682392134> | {member.name} doesn't have a profile to delete.",
                color=self.embed_color
            )

        await ctx.send(embed=embed)



class ProfileEditView(View):
    def __init__(self, owner: discord.Member):
        super().__init__(timeout=None)
        self.owner = owner

    @discord.ui.button(label="Edit Bio", style=discord.ButtonStyle.primary)
    async def edit_bio(self, interaction: discord.Interaction, button: Button ):
        if interaction.user.id != self.owner.id:
            await interaction.response.send_message("You can only edit your own profile.", ephemeral=True)
            return
        
        await interaction.response.send_modal(EditBioModal())

class EditBioModal(discord.ui.Modal, title="Edit Bio"):
    bio = discord.ui.TextInput(label="Enter your new bio", style=discord.TextStyle.short, min_length=0, max_length=100)

    async def on_submit(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        new_bio = self.bio.value

        c = interaction.client.get_cog('ProfileCog').c
        c.execute('UPDATE profiles SET bio = ? WHERE user_id = ?', (new_bio, user_id))
        interaction.client.get_cog('ProfileCog').conn.commit()

        embed = discord.Embed(
            title=None,
            description=f"<:BrigadeAccepted:1281028040318652528> | Your bio has been updated to: `{new_bio}`",
            color=discord.Color.yellow()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(ProfileCog(bot))
