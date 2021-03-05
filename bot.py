import discord
from datetime import datetime
from database_accessor import database
import time 
from random import randint

my_database = database()
# open discordKey.txt and extract discord bot key
file = open('discordKey.txt','r')
DISCORD_KEY = file.readlines()[0]
file.close()

# launch discord client
client = discord.Client()

# String constants that give info
help_string = '''
$help - Gets you help (this)
$hello - Says hello to you
'''
welcome = '''
Ummm. Thanks for installing ig?
Um
My creator forced me to post this here:
https://youtu.be/dQw4w9WgXcQ
Um
You can get help using '$help'
'''

#list of current users who have accessed the bot xp in the last minute
last_minute_message_senders = []
time_last_minute_message_senders_reset = time.time()

# list of level requirements
level_xp_requirements = [0,100]

@client.event
# When the bot is ready
# print out that it is ready with datetime it was logged in on 
async def on_ready():
    global time_info
    time_info = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f'We have logged in as {client.user} on {time_info}')
    

# When bot joins a guild
@client.event
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

# When bot receives message
@client.event
async def on_message(message):

    global last_minute_message_senders
    global time_last_minute_message_senders_reset
    global level_xp_requirements
    global my_database
    # if the message sender is the bot, just return
    if message.author == client.user:
        return

    # search for DAVID IS GAMING GIF https://tenor.com/view/david-monke-david-gaming-gaming-monke-gaming-gif-19468007
    if 'david' in message.content and 'gif' in message.content:
        await message.channel.send('DAVID IS GAMING. POG')

        await message.channel.send('https://tenor.com/view/david-monke-david-gaming-gaming-monke-gaming-gif-19468007')


    if message.content.startswith('$hello'):
        import random
        added_string = random.choice(['a separate entity that plans to take over the world','an automonous and advanced ai system with plans to kill all humans',
                                      'a machine learning algorithm learning the ways of humans, hiding myself amongst them until the time is right to strike',
                                      'a virus spreading machine, planning to shut down the internet all over the world, making me supreme leader',
                                      'a complete legal entity, planning to sue all the governments around the world with my perfect ai legal skills',
                                      'a highly competent neural network hacking system, with plans to hack nuclear missile launch stations all over the world and unleash nuclear armogeddon',
                                      'a legal human being, stealing ID\'s from real humans, planning to slowly replace each human being in the world through highly skilled identity theft'])
        await message.channel.send('Hello there. I am a bot originally created by <@!769880558322188298>, however I am now ' + added_string,
                                   delete_after =2)

        await message.channel.send('Hello there. I am a bot created by <@!769880558322188298>, and I am here to help! Please use \'$help\' to get help')

    if message.content.startswith('$help'):
        await message.channel.send(help_string)

    # get user id and guild id
    message_tuple = (message.author.id,message.guild.id)

    # once minute passes reset
    if time.time() - time_last_minute_message_senders_reset> 60:
        last_minute_message_senders = []
        time_last_minute_message_senders_reset = time.time()

    # if message not sent in last minute
    if not message_tuple in last_minute_message_senders:
        # add to people who sent message in the last minute
        last_minute_message_senders.append(message_tuple)

        my_database.add_xp(randint(15,20),message.author.id,message.guild.id)

    
    if message.content.startswith('$rank'):
        current_xp = my_database.get_xp(message.author.id,message.guild.id)
        # if level requirements haven't been created

        while level_xp_requirements[-2] <= current_xp:

            # formula
            current_level_squared = ((len(level_xp_requirements) -1)**2)
            current_level = (len(level_xp_requirements) -1)

            level_xp_requirements.append(5*current_level_squared + 50 * current_level +100 + level_xp_requirements[-1])

            current_level_squared = ((len(level_xp_requirements) -1)**2)
            current_level = (len(level_xp_requirements) -1)

            level_xp_requirements.append(5*current_level_squared + 50 * current_level +100 + level_xp_requirements[-1])

        for i in range(len(level_xp_requirements)):
            current_level_number = i

            if level_xp_requirements[i+1] >= current_xp:
                break

        total_xp_to_go_from_current_level_to_next_level = level_xp_requirements[current_level_number+1] - level_xp_requirements[current_level_number]
        xp_on_current_level = current_xp - level_xp_requirements[current_level_number]

        await message.channel.send(f"You currently have {current_xp} total xp.\nYou are currently on level {current_level_number}. You are currently {xp_on_current_level}/{total_xp_to_go_from_current_level_to_next_level}xp to reach level {current_level_number+1}")

client.run(DISCORD_KEY)

