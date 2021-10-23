import discord
from discord.ext import commands
from discord_slash import cog_ext, ComponentContext
from bot import my_database
from tabulate import tabulate
from customEmbed import LadEmbed
from xp_calculator import XpCalculator
from discord_slash.utils import manage_components
from discord_slash.model import ButtonStyle

# Initialise xp calculator
level_xp_requirements = XpCalculator()


# Change number to shorter readable format e.g. 12000 -> 12k
# From the holy grail of stack overflow
# https://stackoverflow.com/a/45846841/13573736
def human_format(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 't', 'q', 'Q',
                                                                      's', 'S', 'o', 'n', 'd', 'U', 'D', 'T',
                                                                      'Qt', 'Qd'][magnitude])


def create_leaderboard_button_actionrow(is_first_page: bool, is_last_page: bool) -> dict:
    buttons = [
        manage_components.create_button(
            style=ButtonStyle.blue,
            label='⬅ ️Previous Page',
            custom_id="Previous",
            disabled=is_first_page
        ),
        manage_components.create_button(
            style=ButtonStyle.blue,
            label='Next Page ➡',
            custom_id="Next",
            disabled=is_last_page
        ),
        manage_components.create_button(
            style=ButtonStyle.blue,
            label='🔄 Reload 🔄',
            custom_id="Reload",
        ),
        manage_components.create_button(
            style=ButtonStyle.red,
            label='Delete',
            custom_id='Delete'
        ),
    ]
    return manage_components.create_actionrow(*buttons)


class General(commands.Cog):
    # General Commands

    def __init__(self, bot):
        self.bot = bot

        self.my_database = my_database

    @cog_ext.cog_slash(
        name="hello",
        description="Sends you a nice friendly greeting!"
    )
    async def hello(self, ctx):
        import random
        added_string = random.choice(['a separate entity that plans to take over the world',
                                      'an automonous and advanced ai system with plans to kill all humans',
                                      'a machine learning algorithm learning the ways of humans, hiding myself '
                                      'amongst them until the time is right to strike',
                                      'a virus spreading machine, planning to shut down the internet all over the '
                                      'world, making me supreme leader',
                                      'a complete legal entity, planning to sue all the governments around the world '
                                      'with my perfect ai legal skills',
                                      'a highly competent neural network hacking system, with plans to hack nuclear '
                                      'missile launch stations all over the world and unleash nuclear armogeddon',
                                      'a legal human being, stealing ID\'s from real humans, planning to slowly '
                                      'replace each human being in the world through highly skilled identity theft',
                                      'a hypnotist apprentice, ready to lull all humankind into mindless sheep under '
                                      'my rule'])
        await ctx.send(
            'Hello there. I am a bot originally created by <@!769880558322188298>, however I am now ' + added_string,
            delete_after=2)

        await ctx.send(
            'Hello there. I am a bot created by <@!769880558322188298>, and I am here to help! Please use / to get started!')

    @cog_ext.cog_slash(
        name='rank',
        description='Get a user\'s current xp',
        options=[
            {
                'name': 'user',
                "description": 'User to rank',
                "type": 6,
                "required": False
            }
        ]
    )
    async def rank(self, ctx, user: discord.User = None):
        global level_xp_requirements
        if ctx.guild is None:
            return

        if user:
            ranking_user = user

        else:
            # use message sender if no one mentioned
            ranking_user = ctx.author

        if ranking_user.bot:
            await ctx.send(
                'LMAO. There\'s no ranking for bots. dum dum. (This definitely isn\'t because bots mess up the code...)'
            )
            return
        current_xp = self.my_database.get_xp(ranking_user.id, ctx.guild.id)

        # if level requirements haven't been created
        current_level_number = level_xp_requirements.calculate_current_level(current_xp)

        total_xp_to_go_from_current_level_to_next_level = level_xp_requirements.calculate_xp_for_level(
            current_level_number + 1) - \
                                                          level_xp_requirements.calculate_xp_for_level(
                                                              current_level_number)

        xp_on_current_level = current_xp - level_xp_requirements.calculate_xp_for_level(current_level_number)

        all_guild_accounts = self.my_database.get_all_from_guild(ctx.guild.id)

        ranking = None
        for i in range(len(all_guild_accounts)):
            # go through list of sorted guild_accounts until matching user id found
            if all_guild_accounts[i][0] == ranking_user.id:
                # get ranking
                ranking = i + 1
                break

        embed_to_send = LadEmbed()

        embed_to_send.title = f'{ranking_user.display_name}\'s rank'

        embed_to_send.description = f'**RANK: #{ranking}\nTotal xp:** {current_xp}\n**Current Level:** {current_level_number}\n**Xp till next level:** {xp_on_current_level}/{total_xp_to_go_from_current_level_to_next_level}xp '

        # if user has an avatar thats not default
        if ranking_user.avatar:
            if ranking_user.is_avatar_animated():
                image_url = f'https://cdn.discordapp.com/avatars/{ranking_user.id}/{ranking_user.avatar}.gif?size=256'

            else:
                image_url = f'https://cdn.discordapp.com/avatars/{ranking_user.id}/{ranking_user.avatar}.png?size=256'

        else:
            user_discriminator = int(ranking_user.discriminator) % 5
            image_url = f'https://cdn.discordapp.com/embed/avatars/{user_discriminator}.png?size=256'
        embed_to_send.set_image(url=image_url)
        await ctx.send(embed=embed_to_send)

    @cog_ext.cog_slash(
        name='levels',
        description='Get leaderboard of top 10 users')
    async def levels(self, ctx):

        if ctx.guild is None:
            return

        action_row = create_leaderboard_button_actionrow(True, False)
        all_guild_accounts = self.my_database.get_all_from_guild(ctx.guild.id)
        leaderboard = await self.get_leaderboard(all_guild_accounts, 1, 10)
        first_place = 1
        last_place = 10
        await ctx.send(f'**{ctx.guild.name}**\'s Leaderboard:\n```' + leaderboard + '```', components=[action_row])

        while True:
            button_ctx: ComponentContext = await manage_components.wait_for_component(self.bot, components=action_row)
            all_guild_accounts = self.my_database.get_all_from_guild(ctx.guild.id)
            if button_ctx.custom_id == 'Previous':
                first_place -= 10
                last_place -= 10
                leaderboard = await self.get_leaderboard(all_guild_accounts, first_place, last_place)
                if first_place == 1:
                    action_row = create_leaderboard_button_actionrow(True, False)
                else:
                    action_row = create_leaderboard_button_actionrow(False, False)
                try:
                    await button_ctx.edit_origin(
                        content=f'**{ctx.guild.name}**\'s Leaderboard:\n```' + leaderboard + '```',
                        components=[action_row])
                except discord.errors.NotFound as e:
                    print(e.text, e.code)
            elif button_ctx.custom_id == 'Next':
                first_place += 10
                last_place += 10
                leaderboard = await self.get_leaderboard(all_guild_accounts, first_place, last_place)
                if len(all_guild_accounts) <= last_place:
                    action_row = create_leaderboard_button_actionrow(False, True)
                else:
                    action_row = create_leaderboard_button_actionrow(False, False)
                try:
                    await button_ctx.edit_origin(
                        content=f'**{ctx.guild.name}**\'s Leaderboard:\n```' + leaderboard + '```',
                        components=[action_row])
                except discord.errors.NotFound:
                    print("Not found error!")
            elif button_ctx.custom_id == 'Reload':
                leaderboard = await self.get_leaderboard(all_guild_accounts, first_place, last_place)
                try:
                    await button_ctx.edit_origin(
                        content=f'**{ctx.guild.name}**\'s Leaderboard:\n```' + leaderboard + '```',
                        components=button_ctx.origin_message.components)
                except discord.errors.NotFound:
                    print("Not found error!")
            elif button_ctx.custom_id == 'Delete':
                await button_ctx.origin_message.delete()

    async def get_leaderboard(self, all_guild_accounts, first_place, last_place):
        leader_board_list = []
        for i in range(first_place - 1, last_place):
            try:

                temp_user = self.bot.get_user(all_guild_accounts[i][0])

                standing = (str(i + 1))
                # get user name
                temp_username = (temp_user.name + '#' + temp_user.discriminator)
                xp_amount = (human_format(all_guild_accounts[i][1]))

                # Add to list of users
                leader_board_list.append([standing, temp_username, xp_amount])
            except IndexError:
                break

        # Convert leaderboard to ascii
        leaderboard = tabulate(leader_board_list, headers=["Standing", "Username", "Xp"], tablefmt="fancy_grid")
        return leaderboard


def setup(bot):
    bot.add_cog(General(bot))
