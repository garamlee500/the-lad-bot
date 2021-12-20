import io

import discord
from datetime import datetime

from discord.ext.commands import has_permissions
from discord_slash.utils import manage_components
from discord_slash.utils.manage_components import create_actionrow, create_button

from database_accessor import Database
from xp_calculator import XpCalculator
import time
from customEmbed import LadEmbed
from random import randint
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext, ButtonStyle
import requests
from discord_slash.context import ComponentContext

description = 'A Discord bot emulating the MEE6 level system - the prefix for this server is \'£\''
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='£', description=description, intents=intents, help_command=None)
slash = SlashCommand(bot, sync_commands=True, sync_on_cog_reload=True)

# Open discordKey.txt and extract discord bot key
file = open('discordKey.txt', 'r')
DISCORD_KEY = file.readlines()[0]
file.close()

# Bot checks for xp every minute - you can only get xp once a minute
MINUTE_IN_SECONDS = 60

# Initialise database
my_database = Database()

# Some dodgy welcome sign displayed when bot is added to a server
welcome = '''
Thank you for installing the-lad-bot!
View my commands by typing in \'/\'

To ensure all functionality works, drag up the-lad-bot's role in Role settings (as high as possible)!
If you want, use /set_rank_channel to set where level up messages are sent!
'''

# This stores a list of everyone who has received xp in the last minute
last_minute_message_senders = []

# This stores the last time above list was reset
time_last_minute_message_senders_reset = time.time()

# Initialise xp calculator
level_xp_requirements = XpCalculator()


# When the bot is ready
# Print out that it is ready with datetime it was logged in on
@bot.listen('on_ready')
async def on_ready():
    time_info = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f'We have logged in as {bot.user.name} on {time_info}')

    FISH_GAMING_WEDNESDAY_CHANNEL_ID = 765245461505245267
    sent_fish_gaming_wednesday = False
    fishy_video = requests.get(
        "https://cdn.discordapp.com/attachments/765245461505245267/834510823787200552/fishgaminwensday.mp4"
    ).content
    fishy_file = discord.File(fp=io.BytesIO(fishy_video), filename='fishgaminwensday.mp4')

    while True:
        current_time = datetime.now()

        if not sent_fish_gaming_wednesday and current_time.weekday() == 2 and current_time.hour >=6:
            await bot.get_channel(FISH_GAMING_WEDNESDAY_CHANNEL_ID).send(file=fishy_file)
            sent_fish_gaming_wednesday = True

        elif sent_fish_gaming_wednesday and current_time.weekday() == 3:
            sent_fish_gaming_wednesday = False

        time.sleep(60)


# When bot joins a guild
@bot.listen('on_guild_join')
async def on_guild_join(guild):
    # Find the system channel of the guild if it exists
    if guild.system_channel is None:
        try:
            await guild.text_channels[0].send(welcome)
        except IndexError:
            print(f'Guild {guild.name} has no text channels, and thus welcoming has failed')

    else:
        # Send Welcome message
        await guild.system_channel.send(welcome)

    # Get all members of guild
    members = guild.members

    # Add all members to database, if they are not bot
    for member in members:
        if not member.bot:
            my_database.get_xp(member.id, guild.id)


# When new member joins guild
@bot.listen('on_member_join')
async def on_member_join(member):
    # Add user to database
    if not member.bot:
        my_database.get_xp(member.id, member.guild.id)


# This does autoroling
async def autorole_apply(guild):
    global level_xp_requirements

    # Get all members from database
    members = my_database.get_all_from_guild(guild.id)

    # Get all auotroles from database
    autoroles = my_database.autorole_guild(guild.id)

    # Go through all autoroles
    for rule in autoroles:

        try:
            # rule[1] gets minimum level for role
            # Find the minimum xp for that level
            xp_for_autorole = level_xp_requirements.calculate_xp_for_level(rule[1])
        except IndexError:
            # Normally happens when role level is negative
            xp_for_autorole = 0

        # Find the role
        # rule[0] gets role id
        role_to_add = guild.get_role(rule[0])

        # Loop through each member
        for member in members:

            # member[1] gets xp
            # If member has enough xp
            if member[1] >= xp_for_autorole:

                # get discord.Member object of that member
                member = guild.get_member(member[0])

                # If they are a real member and aren't a bot
                if member and not member.bot:
                    try:
                        # Add role
                        await member.add_roles(role_to_add, reason='Role added due to autorole')

                    except Exception as e:
                        print(e)



@slash.slash(name="inspiro",
             description='Generate a quote from inspirobot.me')
async def inspiro(ctx: SlashContext):

    embed_to_return = LadEmbed()
    embed_to_return.title = 'Inspirobot quote'
    embed_to_return.description = 'An auto-generated quote from the official Inspirobot api'

    buttons = [
        manage_components.create_button(
            style=ButtonStyle.blue,
            label='🔄 Reload 🔄',
            custom_id="Reload",
        )
    ]
    action_row = create_actionrow(*buttons)

    inspiro_image_url = requests.get('https://inspirobot.me/api?generate=true&oy=vey').text
    embed_to_return.set_image(url=inspiro_image_url)

    await ctx.send(embed=embed_to_return, components=[action_row])

    while True:
        button_ctx: ComponentContext = await manage_components.wait_for_component(bot, components=action_row)

        if button_ctx.custom_id == "Reload":
            inspiro_image_url = requests.get('https://inspirobot.me/api?generate=true&oy=vey').text
            embed_to_return.set_image(url=inspiro_image_url)
            await button_ctx.edit_origin(embed=embed_to_return)

# When bot receives message
@bot.listen('on_message')
async def on_message(message):

    global last_minute_message_senders
    global time_last_minute_message_senders_reset
    global level_xp_requirements
    global my_database
    # if the message sender is the bot, just return
    if message.author == bot.user:
        return

    if not message.guild:
        await message.channel.send('DM COMMAND DETECTED. PREPARE TO EXTERMINATE', delete_after=2)
        await message.channel.send(
            'Warning: Commands do not work on DMs. You can add the bot to your server using: '
            'https://discord.com/oauth2/authorize?client_id=816971607301947422&permissions=268749888&scope=bot%20applications.commands')

        return

    # get user id and guild id
    message_tuple = (message.author.id, message.guild.id)

    # once minute passes reset
    if time.time() - time_last_minute_message_senders_reset > MINUTE_IN_SECONDS:
        last_minute_message_senders = []
        time_last_minute_message_senders_reset = time.time()

    # if message not sent in last minute
    if message_tuple not in last_minute_message_senders and not message.author.bot:
        # add to people who sent message in the last minute
        last_minute_message_senders.append(message_tuple)

        added_xp = randint(15, 20)
        try:
            current_xp = my_database.add_xp(added_xp, message.author.id, message.guild.id)

        # When user is literally over max xp (wtf)
        except OverflowError:
            return

        previous_xp = current_xp - added_xp

        if level_xp_requirements.calculate_current_level(previous_xp) < level_xp_requirements.calculate_current_level(
                current_xp):

            # apply autorole
            await autorole_apply(message.guild)

            try:
                rank_channel_id = my_database.get_rank_channel(message.guild.id)[0][0]
                rank_channel = bot.get_channel(rank_channel_id)
            except IndexError:
                # If rank messaging is turned off
                return

            # if level up
            embed_to_send = LadEmbed()
            embed_to_send.title = 'Level up'
            embed_to_send.description = f'GG <@!{message.author.id}>, you just advanced to level {level_xp_requirements.calculate_current_level(current_xp)}! '

            # if user has an avatar thats not default
            if message.author.avatar:
                # get image link
                if message.author.is_avatar_animated():
                    image_url = f'https://cdn.discordapp.com/avatars/{message.author.id}/{message.author.avatar}.gif' \
                                f'?size=256 '

                else:
                    image_url = f'https://cdn.discordapp.com/avatars/{message.author.id}/{message.author.avatar}.png' \
                                f'?size=256 '
            else:
                user_discriminator = int(message.author.discriminator) % 5
                image_url = f'https://cdn.discordapp.com/embed/avatars/{user_discriminator}.png?size=256'
            embed_to_send.set_image(url=image_url)
            await rank_channel.send(embed=embed_to_send)


@slash.slash(
    name="create_buttonrole",
    description="Create button that gives users roles",

    options=[
        {

            'name': 'message',
            'description': 'Message to be sent',
            'type': 3,
            'required': True
        },
        {
            'name': 'role',
            'description': 'Role to give when button pressed',
            'type': 8,
            'required': True
        },
        {
            'name': 'button_text',
            'description': "Text for button",
            'type': 3,
            'required': True
        },

    ]
)
@has_permissions(manage_guild=True)
async def create_buttonrole(ctx: SlashContext, message: str, role: discord.Role, button_text: str):
    if ctx.guild is None:
        return

    button_action_row = create_actionrow(*[
        create_button(
            style=ButtonStyle.green,
            label=button_text,
            custom_id="add"
        ),
        create_button(
            style=ButtonStyle.red,
            label="Remove Role",
            custom_id="remove"
        )
    ])

    sent_message = await ctx.send(message, components=[button_action_row])

    my_database.create_reactrole(
        sent_message.id,
        role.id
    )


@create_buttonrole.error
async def create_buttonrole_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(
            "You don't have permission to do that! You must have the \'Manage Server\' permission to do that!"
        )

    elif isinstance(error, commands.RoleNotFound):
        await ctx.send(
            "The specified role was not found!"
        )


@bot.listen('on_component')
async def on_component(ctx: ComponentContext):
    react_role = my_database.find_reactrole(ctx.origin_message_id)
    if ctx.custom_id == "add":
        if react_role:
            role_to_add = ctx.guild.get_role(react_role[0][1])
            if not ctx.author.bot:
                await ctx.author.add_roles(role_to_add, reason='Pressed special button for role!')
                await ctx.send(f'Successfully added {role_to_add.name} role!', hidden=True)

    elif ctx.custom_id == "remove":
        role_to_add = ctx.guild.get_role(react_role[0][1])
        await ctx.author.remove_roles(role_to_add, reason='Pressed special button to remove role')
        await ctx.send(f'Successfully removed {role_to_add.name} role!', hidden=True)


bot.load_extension("Admin")
bot.load_extension("General")

bot.run(DISCORD_KEY)
