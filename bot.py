import discord
from datetime import datetime
from database_accessor import database
import time 
from customEmbed import LadEmbed
from random import randint
from discord.ext import commands
from discord.ext.commands import has_permissions
from tabulate import tabulate

description = 'A Discord bot emulating the MEE6 level system - the prefix for this server is \'$\''
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='$', description=description, intents=intents, help_command = None)

MINUTE_IN_SECONDS = 60
my_database = database()
# open discordKey.txt and extract discord bot key
file = open('discordKey.txt','r')
DISCORD_KEY = file.readlines()[0]
file.close()



# String constants that give info
help_string = '''
`$help` - Gets you help (this)
`$hello` - Says hello to you
`$rank <optional:@usermention>` - Get your/user's current xp 
'$levels' - Get leaderboard of top 10 users
`$addxp <amount> <@user_to_give_to>` - Add xp to user's total. Must have the 'Manage Roles' Permission
`$removexp <amount> <@user_to_remove_from>` - Remove xp from user's total. Must have the 'Manage Roles' Permission. (Note: xp is completely deleted and not transferred)
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


# When the bot is ready
# print out that it is ready with datetime it was logged in on 
@bot.event
async def on_ready():
    global time_info
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

# Change number to shorter readable format
def human_format(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 't', 'q','Q','s','S','o','n','d','U','D','T','Qt','Qd'][magnitude])

class General(commands.Cog):
    '''General Commands'''
    @commands.command(brief='Says hello to you', help = 'Sends you a nice friendly greeting!')
    async def hello(self, ctx):
        import random
        added_string = random.choice(['a separate entity that plans to take over the world','an automonous and advanced ai system with plans to kill all humans',
                                          'a machine learning algorithm learning the ways of humans, hiding myself amongst them until the time is right to strike',
                                          'a virus spreading machine, planning to shut down the internet all over the world, making me supreme leader',
                                          'a complete legal entity, planning to sue all the governments around the world with my perfect ai legal skills',
                                          'a highly competent neural network hacking system, with plans to hack nuclear missile launch stations all over the world and unleash nuclear armogeddon',
                                          'a legal human being, stealing ID\'s from real humans, planning to slowly replace each human being in the world through highly skilled identity theft',
                                          'a hypnotist apprentice, ready to lull all humankind into mindless sheep under my rule'])
        await ctx.send('Hello there. I am a bot originally created by <@!769880558322188298>, however I am now ' + added_string,
                                       delete_after =2)

        await ctx.send('Hello there. I am a bot created by <@!769880558322188298>, and I am here to help! Please use \'$help\' to get help')

    @commands.command()
    async def rank(self, ctx):
        global level_xp_requirements
        if ctx.guild is None:
            return
        if ctx.message.mentions:
            # use mentioned user if they exist
            ranking_user = ctx.message.mentions[0]

        else:
            # use message sender if no one mentioned
            ranking_user = ctx.author

        if ranking_user.bot:
            await ctx.send('LMAO. There\'s no ranking for bots. dum dum. (This definitely isn\'t because bots mess up the code...)')
            return
        current_xp = my_database.get_xp(ranking_user.id,ctx.guild.id)
        # if level requirements haven't been created

        level_xp_requirements = recalculate_xp_requirements(level_xp_requirements, current_xp)
        current_level_number = calculate_current_level(current_xp,level_xp_requirements)

        total_xp_to_go_from_current_level_to_next_level = level_xp_requirements[current_level_number+1] - level_xp_requirements[current_level_number]
        xp_on_current_level = current_xp - level_xp_requirements[current_level_number]

        all_guild_accounts = my_database.get_all_from_guild(ctx.guild.id)

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
            if ranking_user.is_avatar_animated():
                image_url = f'https://cdn.discordapp.com/avatars/{ranking_user.id}/{ranking_user.avatar}.gif?size=256'

            else:
                image_url = f'https://cdn.discordapp.com/avatars/{ranking_user.id}/{ranking_user.avatar}.png?size=256'

        else:
            user_discriminator = int(ranking_user.discriminator) % 5
            image_url = f'https://cdn.discordapp.com/embed/avatars/{user_discriminator}.png?size=256'
        embed_to_send.set_image(url = image_url)
        await ctx.send(embed = embed_to_send)

    @commands.command()
    async def levels(self, ctx):
        if ctx.guild is None:
            return
        leader_board_list = []
        all_guild_accounts = my_database.get_all_from_guild(ctx.guild.id)
        for i in range(10):
            try:

                temp_user = await bot.fetch_user(all_guild_accounts[i][0])

                standing = (str(i+1))
                # get user name
                temp_username = (temp_user.name + '#' + temp_user.discriminator)
                xp_amount = (human_format(all_guild_accounts[i][1]))

                # Add to list of users
                leader_board_list.append([standing, temp_username,xp_amount])
            except IndexError:
                break

        # Convert leaderboard to ascii
        leaderboard = tabulate(leader_board_list, headers=["Standing", "Username", "Xp"], tablefmt="fancy_grid")
        

        await ctx.send(f'**{ctx.guild.name}**\'s Top 10:\n```' + leaderboard+'```')

    
        
@bot.command()
@has_permissions(manage_roles=True)
async def addxp(ctx, user_getting_xp : discord.Member, xp_amount : int):
    if ctx.guild is None:
        return

    if user_getting_xp.bot:
        await ctx.send ('Bots can\'t have xp dum dum. (Definitely not because of the fatal errors bots having xp causes)')
        return
    # add xp
    try:
        my_database.add_xp(xp_amount, user_getting_xp.id, ctx.guild.id)
    except OverflowError:
        await ctx.send('Jeez, thats a big number. Please be nicer :frowning: :cry:')
        return
    await ctx.send (f"{xp_amount} xp successfully added to <@!{user_getting_xp.id}>\'s bank!")
@addxp.error
async def addxp_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to do that! You must have the \'Manage Roles\' permission to do that!")

    elif isinstance(error, commands.MemberNotFound):
        await ctx.send('The specified member was not found!')

    elif isinstance(error, commands.BadArgument):
        await ctx.send('Please set a valid amount of xp to add')
      


@bot.command()
@has_permissions(manage_roles=True)
async def removexp(ctx, user_getting_xp : discord.Member, xp_amount : int):
    if ctx.guild is None:
        return

    if user_getting_xp.bot:
        await ctx.send ('Bots can\'t have xp dum dum. (Definitely not because of the fatal errors bots having xp causes)')
        return
    # Remove xp (make xp_amount negative to remove)
    try: 
        my_database.add_xp(0-xp_amount, user_getting_xp.id, ctx.guild.id)

    except OverflowError:
        await ctx.send('Jeez, thats a big number. Please be nicer :frowning: :cry:')
        return
    await ctx.send (f"{xp_amount} xp successfully removed from <@!{user_getting_xp.id}>\'s bank!")
@removexp.error
async def removexp_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to do that! You must have the \'Manage Roles\' permission to do that!")

    elif isinstance(error, commands.MemberNotFound):
        await ctx.send('The specified member was not found!')

    elif isinstance(error, commands.BadArgument):
        await ctx.send('Please set a valid amount of xp to remove')

        


@bot.command()
async def help(ctx):

    embed_to_return = LadEmbed()
    embed_to_return.title = '**HELP**'
    embed_to_return.description = help_string
    await ctx.send(embed=embed_to_return)


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
        await message.channel.send('Warning: Commands do not work on DMs. You can add the bot to your server using: https://discord.com/api/oauth2/authorize?client_id=816971607301947422&permissions=3691183152&scope=bot')

        return
    # search for DAVID IS GAMING GIF https://tenor.com/view/david-monke-david-gaming-gaming-monke-gaming-gif-19468007
    if ('david' in message.content and 'gif' in message.content) or 'https://tenor.com/btQGh.gif' in message.content:
        await message.channel.send('DAVID IS GAMING. POG')

        await message.channel.send('https://tenor.com/view/david-monke-david-gaming-gaming-monke-gaming-gif-19468007')



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
        try:
            current_xp = my_database.add_xp(added_xp,message.author.id,message.guild.id)

        # When user is literally over max xp (wtf)
        except OverflowError:
            return

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
                if message.author.is_avatar_animated():
                    image_url = f'https://cdn.discordapp.com/avatars/{message.author.id}/{message.author.avatar}.gif?size=256'

                else:
                    image_url = f'https://cdn.discordapp.com/avatars/{message.author.id}/{message.author.avatar}.png?size=256'
            else:
                user_discriminator = int(message.author.discriminator) % 5
                image_url = f'https://cdn.discordapp.com/embed/avatars/{user_discriminator}.png?size=256'
            embed_to_send.set_image(url = image_url)
            await message.channel.send(embed=embed_to_send)

bot.add_cog(General())
bot.run(DISCORD_KEY)
