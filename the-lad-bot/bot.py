import discord
from datetime import datetime

import schedule

from database_accessor import Database
from xp_calculator import XpCalculator
import time
from customEmbed import LadEmbed
from random import randint
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
import requests

description = 'A Discord bot emulating the MEE6 level system - the prefix for this server is \'£\''
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='£', description=description, intents=intents, help_command=None)
slash = SlashCommand(bot, sync_commands=True, sync_on_cog_reload=True)

# Open discordKey.txt and extract discord bot key
file = open('discordKey.txt', 'r')
DISCORD_KEY = file.readlines()[0]
file.close()


FISH_GAMING_WEDNESDAY_CHANNEL_ID = 765245461505245267

# Bot checks for xp every minute - you can only get xp once a minute
MINUTE_IN_SECONDS = 60

# Initialise database
my_database = Database()

# Some dodgy welcome sign displayed when bot is added to a server
welcome = '''
Ummm. Thanks for installing ig?
Um
My creator forced me to post this here:
https://youtu.be/dQw4w9WgXcQ
Um
You can get help using '£help'
'''

# This stores a list of everyone who has received xp in the last minute
last_minute_message_senders = []

# This stores the last time above list was reset
time_last_minute_message_senders_reset = time.time()

# Initialise xp calculator
level_xp_requirements = XpCalculator()

async def send_fish_gaming_wednesday():

    # Sennd Fish Gaming Wednesday
    await discord.get_channel(FISH_GAMING_WEDNESDAY_CHANNEL_ID).send(
        "https://cdn.discordapp.com/attachments/765245461505245267/834510823787200552/fishgaminwensday.mp4"
    )

# When the bot is ready
# Print out that it is ready with datetime it was logged in on
@bot.event
async def on_ready():
    time_info = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f'We have logged in as {bot.user.name} on {time_info}')


# When bot joins a guild
@bot.event
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
    members = await guild.fetch_members(limit=150).flatten()

    # Add all members to database, if they are not bot
    for member in members:
        if not member.bot:
            my_database.get_xp(member.id, guild.id)


# When new member joins guild
@bot.event
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
                member = await guild.fetch_member(member[0])

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
    inspiro_image_url = requests.get('https://inspirobot.me/api?generate=true&oy=vey').text
    embed_to_return = LadEmbed()
    embed_to_return.title = 'Inspirobot quote'
    embed_to_return.description = 'An auto-generated quote from the official Inspirobot api'
    embed_to_return.set_image(url=inspiro_image_url)
    await ctx.send(embed=embed_to_return)


# When bot receives message
@bot.listen('on_message')
async def on_message(message):
    schedule.run_pending()

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
            'https://discord.com/oauth2/authorize?client_id=816971607301947422&permissions=268749824&scope=bot%20applications.commands')

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

        if level_xp_requirements.calculate_current_level(previous_xp) < level_xp_requirements.calculate_current_level(current_xp):

            # if level up
            embed_to_send = LadEmbed()
            embed_to_send.title = 'Level up'
            embed_to_send.description = f'GG <@!{message.author.id}>, you just advanced to level {level_xp_requirements.calculate_current_level(current_xp)}! '

            # apply autorole
            await autorole_apply(message.guild)
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
            await message.channel.send(embed=embed_to_send)

bot.load_extension("Admin")
bot.load_extension("General")

schedule.every().wednesday.at("05:00").do(send_fish_gaming_wednesday)

bot.run(DISCORD_KEY)
