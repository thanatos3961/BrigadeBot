import discord
from discord.ext import commands
from discord import app_commands
import roblox
from roblox import Client, UserNotFound
import re

checkmark = "<:BrigadeAccepted:1281028040318652528>"
denied = "<:BrigadeDenied:1281026311682392134>"

successful = discord.Color.dark_green()
unsuccessful = discord.Color.dark_red()

GROUP_ID = 33252260
roblox = Client("_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_50FA267176A9E7813F9E8CAB109C6D20AFF8E9D2EE6318D58039049E2E3CA2893989A4BE2570AF3CDE0928AB5A134D2EA2DFBF9A8A8760AFD5669D477F64402E0600626033F346B21BE82CF933F7D803BA11149CCA33D5A090D558C6EC3EDE24ABCB805703E6C23D0C2559BDD691B3DB016224A815D143BCE634AA2BD52ACDD7F2D0BA8E10B1B0404125EFF3C0C588754E099F97640BD0DF70477A5B919483BC0EB91D3C849F989B5B81DBD9125537D1326041E24DBB20238E51CC539843D09B3FBCD70A8502C6BAA510946213627CFADC4C83AE156BA5E047F039E2FC87278C8864AD2EBFDEBAABCBC2600121A744C564BFD6479088496A44412993A322D0958E867871E9FBC4B2D23342F257FCC0D20E8BD8C36CEF2D842D392EEEB4233F2F8A61CDB5B916C5776A55243FE2FDDF20097782AAF3218E27764797456D97BDAAD0B53306174B57DE6D4722287066253F4040227285B144B0B7EBD0E5A7BE0051196A76DD38170CE91FBC15403A8614B8BA6E87F274E2736E00BAC9C700BCC008A267099892E34C9B85A57D2CEBBB40F03A26600E9CD7F811E8AFA0BC3E4603365BCBF9735CF8505805E8174FF8BD5583965440B4CA7377EF6C4051AD74DAA5608574DF7A7B238728A69C168FDDD865BFAE6CEAA6BB16264B4A3641E35F0E1C0F63A39484DFFFB67114C6AC677ECCE98F682DA379D75DBCBD7D4493D45A185D6F5E9697A5CAC9DB2473BCEB0BD2A601D7DECF63E3BAB2529D6FC2C99B8CB7BBA82C1E6CB95B12D9084035907127B65B08ECE56E32058FC66476C3E76B06EF6C81DA7FA8AC5A2EFCE8B1103B76AE5B6F919CD6C2ED0657817DF57476D7E986EC34DF89CEFF13D4F8FDF820ADDC6A48BC87DB756B946936B17329FB087D23AA8E9F8A6326918775417B0F4E09C0845AC0001206D91583E547C9C86BB073A8161662623DCEEF72B04DD8EC2FCF24BFAEFB3D81EF6BC0399FEE9F319A5D2CF92D8B48685076229C9A57AAF3F43F82062EE7278791BB3E8FAFEDFC604151BC1F0040870688B825")

###### JUGGERNAUT ######
# Junior Juggernaut: 4
# Juggernaut: 5
# Senior Juggernaut: 6
###### RECON ######
# Junior Heavy Recon: 10
# Heavy Recon: 11
# Senior Heavy Recon: 12
###### ENGINEER ######
# Junior Engineer: 17
# Engineer: 18
# Senior Engineer: 18

# Rank promotion map based on rank names
rank_promotion_map_by_name = {
    # Juggernauts
    "Junior Juggernaut": "Juggernaut",
    "Juggernaut": "Senior Juggernaut",
    
    # Recon
    "Senior Juggernaut": "Junior Heavy Recon",
    "Junior Heavy Recon": "Heavy Recon",
    "Heavy Recon": "Senior Heavy Recon",
    
    # Engineers
    "Senior Heavy Recon": "Junior Engineer",
    "Junior Engineer": "Engineer",
    "Engineer": "Senior Engineer"
}

class RobloxCog(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.bot = client
        print("roblox_cog loaded")
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if "#IGNORE" in message.content:
            return
        if message.channel.id != 1290171785547087892:  # Your specific channel ID
            return
        
        usernames = [username.strip() for username in message.content.split(" ")]
        logchannel = message.guild.get_channel(1273119467425108020)
        await message.delete(delay=10)

        allowed_roles = [1273116774551916555]  # Add the role IDs that can use the command

        if not any(discord.utils.get(message.author.roles, id=role_id) for role_id in allowed_roles):
            bot_message = await message.channel.send(embed=discord.Embed(
                title="Permission Denied",
                description="You don't have the required rank to use this command.",
                color=discord.Color.dark_red()
            ))
            await bot_message.delete(delay=10)
            return

        for username in usernames:
            try:
                # Fetch the user and their group roles
                user = await roblox.get_user_by_username(username)
                group_roles = await user.get_group_roles()

                # Find the user's role in the specific group
                group_role = next((role for role in group_roles if role.group.id == GROUP_ID), None)
                
                if group_role:
                    current_rank_name = group_role.name  # Fetch the rank by name

                    # Check if the current rank name is in the promotion map
                    if current_rank_name in rank_promotion_map_by_name:
                        new_rank_name = rank_promotion_map_by_name[current_rank_name]

                        # Find the new rank ID by its name
                        group = await roblox.get_group(GROUP_ID)
                        ranks = await group.get_roles()
                        new_rank = next((rank for rank in ranks if rank.name == new_rank_name), None)

                        if new_rank:
                            member = await group.get_member_by_username(username)
                            await member.set_rank(new_rank.rank)  # Set the rank by its ID
                            
                            # Fetch new role after promotion
                            newroles = await user.get_group_roles()
                            newrole = next((role for role in newroles if role.group.id == GROUP_ID), None)

                            bot_message = await message.channel.send(embed=discord.Embed(
                                title="Promotion Successful",
                                description=f"{checkmark}| User `{username}` has been promoted to `{newrole.name}`.",
                                color=discord.Color.dark_green()
                            ))
                            await logchannel.send(embed=discord.Embed(
                                title="Promotion Log",
                                description=f"{checkmark}| User `{username}` has been promoted to `{newrole.name}`.",
                                color=discord.Color.dark_green()
                            ))
                        else:
                            bot_message = await message.channel.send(embed=discord.Embed(
                                title="Error",
                                description=f"Could not find the rank `{new_rank_name}` in the group.",
                                color=discord.Color.dark_red()
                            ))
                    else:
                        bot_message = await message.channel.send(embed=discord.Embed(
                            title="No Further Promotion",
                            description=f"User `{username}` cannot be promoted further from their current rank.",
                            color=discord.Color.orange()
                        ))
                else:
                    bot_message = await message.channel.send(embed=discord.Embed(
                        title="User Not in Group",
                        description=f"User `{username}` is not in the group.",
                        color=discord.Color.dark_red()
                    ))
            except UserNotFound:
                bot_message = await message.channel.send(embed=discord.Embed(
                    title="User Not Found",
                    description=f"User `{username}` not found. Please check the spelling and try again.",
                    color=discord.Color.dark_red()
                ))
            except Exception as e:
                bot_message = await message.channel.send(embed=discord.Embed(
                    title="Error",
                    description=f"An error occurred: {str(e)}",
                    color=discord.Color.dark_red()
                ))

            await bot_message.delete(delay=10)


    @commands.hybrid_command(name="rowho", description="Shows the info of a Roblox user's profile.")
    async def rowho(self, ctx: commands.Context, username: str):
        try:
            user = await roblox.get_user_by_username(username)
            group_roles = await user.get_group_roles()
            
            group_role = next((role for role in group_roles if role.group.id == GROUP_ID), None)
            role_name = group_role.name if group_role else "Not in the group"

            embed = discord.Embed(title=f"Info for {user.name}")
            embed.add_field(name="Username", value=f"`{user.name}`")
            embed.add_field(name="Display Name", value=f"`{user.display_name}`")
            embed.add_field(name="User ID", value=f"`{user.id}`")
            embed.add_field(name="Description", value=f"```{user.description or 'No description'}```")
            embed.add_field(name="Rank in Pot Brigade:", value=f"{role_name}", inline=False)
            embed.colour = discord.Color.from_str(value="#2b2d31")
            await ctx.send(embed=embed)
        except UserNotFound:
            await ctx.send(f"User `{username}` not found. Please check the spelling and try again.")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

    @app_commands.command(name="setrank", description="Sets the rank of a Roblox user in the group.")
    async def setrank(self, interaction: discord.Interaction, username: str, rank: int):
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="Permission Denied",
                description="You don't have the required permissions to use this command.",
                color=discord.Color.dark_red()
            )
            await interaction.response.send_message(embed=embed)
            return

        if not (1 <= rank <= 255):
            embed = discord.Embed(
                title="Invalid Rank",
                description="Rank must be at least 1 and at most 255.",
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed)
            return

        try:
            group = await roblox.get_group(GROUP_ID)
            member = await group.get_member_by_username(username)
            if member:
                await member.set_rank(rank)  # Correct method to set rank
                embed = discord.Embed(
                    title="Rank Updated",
                    description=f"User `{username}` has been set to rank `{rank}` in the group.",
                    color=discord.Color.dark_green()
                )
                await interaction.response.send_message(embed=embed)
            else:
                embed = discord.Embed(
                    title="User Not Found",
                    description=f"User `{username}` not found in the group.",
                    color=discord.Color.dark_red()
                )
                await interaction.response.send_message(embed=embed)
        except UserNotFound:
            embed = discord.Embed(
                title="User Not Found",
                description=f"User `{username}` not found. Please check the spelling and try again.",
                color=discord.Color.dark_red()
            )
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"An error occurred: {str(e)}",
                color=discord.Color.dark_red()
            )
            await interaction.response.send_message(embed=embed)

    @commands.hybrid_command(name="exile", description="Exiles a user from a Roblox group.")
    @commands.has_permissions(manage_guild=True)  # Guild managers only
    async def exile(self, ctx: commands.Context, username: str, profile_link: str = "No link provided.", *, reason: str = "No reason given."):
        logchannel = self.bot.get_channel(1247415991701471272)
        if not ctx.author.guild_permissions.administrator:
            embed = discord.Embed(
                title="Permission Denied",
                description="You don't have the required permissions to use this command.",
                color=discord.Color.dark_red()
            )
            await ctx.send(embed=embed)
            return

        try:
            group = await roblox.get_group(GROUP_ID)
            member = await group.get_member_by_username(username)
            
            if member:
                await member.kick()
                embed = discord.Embed(
                    title="User Exiled",
                    description=f"User `{username}` has been exiled from the group.",
                    color=discord.Color.dark_green()
                )
                embed.add_field(name="Reason", value=reason, inline=False)
                embed.add_field(name="Profile Link", value=profile_link, inline=False)
                embed.set_footer(text=f"User exiled by: {ctx.author.name} ({ctx.author.id})")
                await ctx.send(embed=embed)
                await logchannel.send(embed=embed)
            else:
                embed = discord.Embed(
                    title="User Not Found",
                    description=f"User `{username}` not found in the group.",
                    color=discord.Color.dark_red()
                )
                await ctx.send(embed=embed)
        except UserNotFound:
            embed = discord.Embed(
                title="User Not Found",
                description=f"User `{username}` not found. Please check the spelling and try again.",
                color=discord.Color.dark_red()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"An error occurred: {str(e)}",
                color=discord.Color.dark_red()
            )
            await ctx.send(embed=embed)

    @app_commands.command(name="promote", description="Promotes a user in the Roblox group by a specified amount of ranks.")
    async def promote(self, interaction: discord.Interaction, username: str):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(embed=discord.Embed(
                title="Permission Denied",
                description="You don't have the required permissions to use this command.",
                color=discord.Color.dark_red()
            ))
            return

        try:
            # Fetch the user and their group roles
            user = await roblox.get_user_by_username(username)
            group_roles = await user.get_group_roles()

            # Find the user's role in the specific group
            group_role = next((role for role in group_roles if role.group.id == GROUP_ID), None)
            
            if group_role:
                current_rank = group_role.rank
                new_rank = current_rank + 1

                # List of restricted ranks
                restricted_ranks = [7, 8, 13, 14, 19, 20, 252, 253, 254]

                # Check if the new rank is a restricted role
                if new_rank in restricted_ranks:
                    await interaction.response.send_message(embed=discord.Embed(
                        title="Promotion Restricted",
                        description=f"Cannot promote `{username}` to rank `{new_rank}`. Promotion to this rank is restricted.",
                        color=discord.Color.orange()
                    ))
                    return

                # Set the new rank
                group = await roblox.get_group(GROUP_ID)
                member = await group.get_member_by_username(username)
                await member.set_rank(new_rank)
                newroles = await user.get_group_roles()
                newrole = next((role for role in newroles if role.group.id == GROUP_ID), None)

                await interaction.response.send_message(embed=discord.Embed(
                    title="Promotion Successful",
                    description=f"User `{username}` has been promoted to `{newrole.name}`.",
                    color=discord.Color.dark_green()
                ))
            else:
                await interaction.response.send_message(embed=discord.Embed(
                    title="User Not in Group",
                    description=f"User `{username}` is not in the group.",
                    color=discord.Color.dark_red()
                ))
        except UserNotFound:
            await interaction.response.send_message(embed=discord.Embed(
                title="User Not Found",
                description=f"User `{username}` not found. Please check the spelling and try again.",
                color=discord.Color.dark_red()
            ))
        except Exception as e:
            await interaction.response.send_message(embed=discord.Embed(
                title="Error",
                description=f"An error occurred: {str(e)}",
                color=discord.Color.dark_red()
            ))

    @commands.hybrid_command(name="demote", description="Demotes a user in the Roblox group by a specified amount of ranks.")
    async def demote(self, ctx: commands.Context, username: str, profile_link: str = "No link provided.", *, reason: str = "No reason provided"):
        logchannel = self.bot.get_channel(1242660812171251823)
        if not ctx.author.guild_permissions.administrator:
            await ctx.send(embed=discord.Embed(
                title="Permission Denied",
                description="You don't have the required permissions to use this command.",
                color=discord.Color.dark_red()
            ))
            return

        try:
            # Fetch the user and their group roles
            user = await roblox.get_user_by_username(username)
            group_roles = await user.get_group_roles()

            # Find the user's role in the specific group
            group_role = next((role for role in group_roles if role.group.id == GROUP_ID), None)
            
            if group_role:
                current_rank = group_role.rank
                new_rank = current_rank - 1

                # List of restricted ranks
                restricted_ranks = [7, 8, 13, 14, 19, 20, 252, 253, 254]

                # Check if the new rank is a restricted role
                if new_rank in restricted_ranks:
                    await ctx.send(embed=discord.Embed(
                        title="Demotion Restricted",
                        description=f"Cannot demote `{username}` to rank `{new_rank}`. Demotion to this rank is restricted.",
                        color=discord.Color.orange()
                    ))
                    return

                # Set the new rank
                group = await roblox.get_group(GROUP_ID)
                member = await group.get_member_by_username(username)
                await member.set_rank(new_rank)
                newroles = await user.get_group_roles()
                newrole = next((role for role in newroles if role.group.id == GROUP_ID), None)

                embed = discord.Embed(
                    title="User Demoted",
                    description=f"User `{username}` has been demoted to `{newrole.name}`.",
                    color=discord.Color.dark_green()
                )
                embed.add_field(name="Reason", value=reason, inline=False)
                embed.add_field(name="Profile Link", value=profile_link, inline=False)
                embed.set_footer(text=f"User demoted by: {ctx.author.name} ({ctx.author.id})")
                await ctx.send(embed=embed)
                await logchannel.send(embed=embed)
            else:
                await ctx.send(embed=discord.Embed(
                    title="User Not in Group",
                    description=f"User `{username}` is not in the group.",
                    color=discord.Color.dark_red()
                ))
        except UserNotFound:
            await ctx.send(embed=discord.Embed(
                title="User Not Found",
                description=f"User `{username}` not found. Please check the spelling and try again.",
                color=discord.Color.dark_red()
            ))
        except Exception as e:
            await ctx.send(embed=discord.Embed(
                title="Error",
                description=f"An error occurred: {str(e)}",
                color=discord.Color.dark_red()
            ))

class ConfirmView(discord.ui.View):
    def __init__(self, author, username, user_id):
        super().__init__(timeout=60)
        self.author = author
        self.username = username
        self.user_id = user_id
        self.result = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user == self.author

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        group = await roblox.get_group(GROUP_ID)
        try:
            await group.accept_user(self.user_id)
            await interaction.response.send_message(f"`{self.username}` has been accepted into the group.")
        except Exception as e:
            await interaction.response.send_message(f"Failed to accept `{self.username}`: {e}")
        self.result = True
        self.stop()

    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(content="Action canceled.")
        self.result = False
        self.stop()

class AcceptCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("accept_cog loaded")

    @app_commands.command(name="accept", description="Accepts a user into the Roblox group.")
    async def accept(self, interaction: discord.Interaction, username: str):
        await interaction.response.defer()

        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(embed=discord.Embed(
                title="Permission Denied",
                description="You don't have the required permissions to use this command.",
                color=discord.Color.dark_red()
            ))
            return
        
        try:
            user = await roblox.get_user_by_username(username)
        except UserNotFound:
            await interaction.followup.send(f"User `{username}` not found. Please check the spelling and try again.")
            return

        user_id = user.id

        view = ConfirmView(author=interaction.user, username=username, user_id=user_id)
        embed = discord.Embed(
            title="Accept Request",
            description=f"Are you sure you want to accept `{username}` into the group?"
        )

        prompt_message = await interaction.followup.send(embed=embed, view=view)

        await view.wait()
        if view.result is None:
            await interaction.response.send_message(content="Timed out. No action taken.", view=None)


    @app_commands.AppCommandError
    async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        elif isinstance(error, app_commands.errors.CommandInvokeError):
            await interaction.response.send_message("An error occurred while executing the command.", ephemeral=True)
        else:
            await interaction.response.send_message(f"An unknown error occurred. Error if it exists: {error}", ephemeral=True)

async def setup(client: commands.Bot):
    await client.add_cog(RobloxCog(client))
    await client.add_cog(AcceptCog(client))