import discord
from datetime import datetime
from database_accessor import database
import time 
from customEmbed import LadEmbed
from random import randint

MINUTE_IN_SECONDS = 60
my_database = database()
# open discordKey.txt and extract discord bot key
file = open('discordKey.txt','r')
DISCORD_KEY = file.readlines()[0]
file.close()

# launch discord client
client = discord.Client()

# String constants that give info
help_string = '''
`$help` - Gets you help (this)
`$hello` - Says hello to you
`$rank <optional:@usermention>` - Get your/user's current xp 
'$levels' - Get leaderboard of top 10 users
`$addxp <@usermention> <amount>` - Add xp to user's total. Must have the 'Manage Server' Permission
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

def recalculate_xp_requirements(current_list, min_xp):
    while current_list[-2] <= min_xp:

        # formula
        current_level_squared = ((len(current_list) -1)**2)
        current_level = (len(current_list) -1)

        current_list.append(5*current_level_squared + 50 * current_level +100 + current_list[-1])

        current_level_squared = ((len(current_list) -1)**2)
        current_level = (len(current_list) -1)

        current_list.append(5*current_level_squared + 50 * current_level +100 + current_list[-1])#

    return current_list

def calculate_current_level(current_xp, xp_requirements):
    for i in range(len(xp_requirements)):
        current_level_number = i

        if xp_requirements[i+1] >= current_xp:
            break

    return current_level_number 

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

    if not message.guild:
        await message.channel.send('DM COMMAND DETECTED. PREPARE TO EXTERMINATE', delete_after=2)
        await message.channel.send('Warning: Commands do not work on DMs. You can add the bot to your server using: https://discord.com/api/oauth2/authorize?client_id=816971607301947422&permissions=3691183152&scope=bot')

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
                                      'a legal human being, stealing ID\'s from real humans, planning to slowly replace each human being in the world through highly skilled identity theft',
                                      'a hypnotist apprentice, ready to lull all humankind into mindless sheep under my rule'])
        await message.channel.send('Hello there. I am a bot originally created by <@!769880558322188298>, however I am now ' + added_string,
                                   delete_after =2)

        await message.channel.send('Hello there. I am a bot created by <@!769880558322188298>, and I am here to help! Please use \'$help\' to get help')

    if message.content.startswith('$help'):

        embed_to_return = LadEmbed()
        embed_to_return.title = '**HELP**'
        embed_to_return.description = help_string
        await message.channel.send(embed=embed_to_return)

    # get user id and guild id
    message_tuple = (message.author.id,message.guild.id)

    # once minute passes reset
    if time.time() - time_last_minute_message_senders_reset> MINUTE_IN_SECONDS:
        last_minute_message_senders = []
        time_last_minute_message_senders_reset = time.time()

    # if message not sent in last minute
    if not message_tuple in last_minute_message_senders and not message.author.bot:
        # add to people who sent message in the last minute
        last_minute_message_senders.append(message_tuple)

        added_xp  = randint(15,20)
        current_xp = my_database.add_xp(added_xp,message.author.id,message.guild.id)

        level_xp_requirements = recalculate_xp_requirements(level_xp_requirements, current_xp)
        previous_xp = current_xp - added_xp

        if calculate_current_level(previous_xp,level_xp_requirements) < calculate_current_level(current_xp,level_xp_requirements):
            # if level up
            embed_to_send = LadEmbed()
            embed_to_send.title = 'Level up'
            embed_to_send.description = f'GG <@!{message.author.id}>, you just advanced to level {calculate_current_level(current_xp,level_xp_requirements)}!'

            # if user has an avatar thats not default
            if message.author.avatar:
                # get image link
                image_url = f'https://cdn.discordapp.com/avatars/{message.author.id}/{message.author.avatar}.png?size=256'

            else:
                user_discriminator = int(message.author.discriminator) % 5
                image_url = f'https://cdn.discordapp.com/embed/avatars/{user_discriminator}.png?size=256'
            embed_to_send.set_image(url = image_url)
            await message.channel.send(embed=embed_to_send)
    if message.content.startswith('$rank'):

        if message.mentions:
            # use mentioned user if they exist
            ranking_user = message.mentions[0]

        else:
            # use message sender if no one mentioned
            ranking_user = message.author

        if ranking_user.bot:
            await message.channel.send('LMAO. There\'s no ranking for bots. dum dum. (This definitely isn\'t because bots mess up the code...)')
            return
        current_xp = my_database.get_xp(ranking_user.id,message.guild.id)
        # if level requirements haven't been created

        level_xp_requirements = recalculate_xp_requirements(level_xp_requirements, current_xp)
        current_level_number = calculate_current_level(current_xp,level_xp_requirements)

        total_xp_to_go_from_current_level_to_next_level = level_xp_requirements[current_level_number+1] - level_xp_requirements[current_level_number]
        xp_on_current_level = current_xp - level_xp_requirements[current_level_number]

        all_guild_accounts = my_database.get_all_from_guild(message.guild.id)

        ranking = None
        for i in range(len(all_guild_accounts)):
            # go through list of sorted guild_accounts until matching user id found
            if all_guild_accounts[i][0] == ranking_user.id:
                # get ranking
                ranking = i+1
                break

        embed_to_send = LadEmbed()

        embed_to_send.title = f'{ranking_user.display_name}\'s rank'

        embed_to_send.description = f'**RANK: #{ranking}\nTotal xp:** {current_xp}\n**Current Level:** {current_level_number}\n**Xp till next level:** {xp_on_current_level}/{total_xp_to_go_from_current_level_to_next_level}xp'


        # if user has an avatar thats not default
        if ranking_user.avatar:
            # get image link
            image_url = f'https://cdn.discordapp.com/avatars/{ranking_user.id}/{ranking_user.avatar}.png?size=256'

        else:
            user_discriminator = int(ranking_user.discriminator) % 5
            image_url = f'https://cdn.discordapp.com/embed/avatars/{user_discriminator}.png?size=256'
        embed_to_send.set_image(url = image_url)
        await message.channel.send(embed = embed_to_send)

    if message.content.startswith('$addxp'):
        pass

    if message.content.startswith('$levels'):
        embed_to_send = LadEmbed()
        embed_to_send.title = f'**{message.guild.name}**\'s leaderboard:'
        places = ''
        usernames = ''
        xp_amounts = ''
        all_guild_accounts = my_database.get_all_from_guild(message.guild.id)
        for i in range(10):
            try:
                temp_user = await client.fetch_user(all_guild_accounts[i][0])

                places += str(i+1) + '\n'
                # get user name
                usernames  += temp_user.name + '#' + temp_user.discriminator + '\n'
                xp_amounts += (str(all_guild_accounts[i][1])+'\n')
            except IndexError:
                break

        embed_to_send.add_field(name='Standing', value = places)
        embed_to_send.add_field(name='Name', value = usernames)
        embed_to_send.add_field(name='XP', value = xp_amounts)

        await message.channel.send(embed=embed_to_send)
client.run(DISCORD_KEY)

