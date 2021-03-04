import discord
from datetime import datetime

# open discordKey.txt and extract discord bot key
file = open('discordKey.txt','r')
DISCORD_KEY = file.readlines()[0]
file.close()

# launch discord client
client = discord.Client()

# String constants that give info
help_string = '''
$Help - Gets you help (this)
'''
welcome = '''
Ummm. Thanks for installing ig?
Um
My creator forced me to post this here:
https://youtu.be/dQw4w9WgXcQ
'''


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
client.run(DISCORD_KEY)

