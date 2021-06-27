import discord
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_choice
from bot import my_database
from tabulate import tabulate
from discord.ext.commands import has_permissions
from bot import autorole_apply


class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.my_database = my_database

    @cog_ext.cog_slash(
        name="xp",
        description="Add or remove xp from user's total. Must have the 'Administrator' Permission",
        options=[
            {
                'name': 'add_remove_xp',
                'description': 'Add or Remove Xp from user',
                'type': 3,
                'required': True,
                'choices': [
                    create_choice(
                        name="add",
                        value="add",
                    ),

                    create_choice(
                        name="remove",
                        value="remove"
                    )
                ]
            },
            {
                'name': 'user',
                'description': 'User to add xp to',
                'type': 6,
                'required': True
            },

            {
                'name': 'amount',
                'description': 'Amount of xp to add',
                'type': 4,
                'required': True
            }
        ])
    @has_permissions(administrator=True)
    async def xp(self, ctx, add_remove_xp: bool, user: discord.Member, amount: int):
        if ctx.guild is None:
            return

        if user.bot:
            await ctx.send(
                'Bots can\'t have xp dum dum. (Definitely not because of the fatal errors bots having xp causes)')
            return

        if add_remove_xp == "add":
            try:
                self.my_database.add_xp(amount, user.id, ctx.guild.id)
            except OverflowError:
                await ctx.send('Jeez, that\'s a big number. Please be nicer :frowning: :cry:')
                return
            await ctx.send(f"{amount} xp successfully added to <@!{user.id}>\'s bank!")

        else:
            try:
                self.my_database.add_xp(-amount, user.id, ctx.guild.id)
            except OverflowError:
                await ctx.send('Jeez, that\'s a big number. Please be nicer :frowning: :cry:')
                return
            await ctx.send(f"{amount} xp successfully removed from <@!{user.id}>\'s bank!")

        await autorole_apply(ctx.guild)

    @xp.error
    async def xp_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                "You don't have permission to do that! You must have the \'Administrator\' permission to do that!")

        elif isinstance(error, commands.MemberNotFound):
            await ctx.send('The specified member was not found!')

        elif isinstance(error, commands.BadArgument):
            await ctx.send('Please set a valid amount of xp to add')

    '''
    @cog_ext.cog_slash(

        name="addxp",
        description = "Add xp to user's total. Must have the 'Administrator' Permission",
        options = [
            {
                'name':'user',
                'description':'User to add xp to',
                'type': 6,
                'required':True
            },

            {
                'name':'amount',
                'description':'Amount of xp to add',
                'type': 4,
                'required':True
            }
        ]
    )

    @has_permissions(administrator=True)
    async def addxp(self, ctx, user: discord.Member, amount: int):
        if ctx.guild is None:
            return

        if user.bot:
            await ctx.send(
                'Bots can\'t have xp dum dum. (Definitely not because of the fatal errors bots having xp causes)')
            return
        # add xp
        try:
            self.my_database.add_xp(amount, user.id, ctx.guild.id)
        except OverflowError:
            await ctx.send('Jeez, thats a big number. Please be nicer :frowning: :cry:')
            return
        await ctx.send(f"{amount} xp successfully added to <@!{user.id}>\'s bank!")

        await autorole_apply(ctx.guild)

    @addxp.error
    async def addxp_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                "You don't have permission to do that! You must have the \'Administrator\' permission to do that!")

        elif isinstance(error, commands.MemberNotFound):
            await ctx.send('The specified member was not found!')

        elif isinstance(error, commands.BadArgument):
            await ctx.send('Please set a valid amount of xp to add')


    @cog_ext.cog_slash(

        name="removexp",
        description="Remove xp from user's total. Must have the 'Administrator' Permission",
        options=[
            {
                'name': 'user',
                'description': 'User to remove xp from',
                'type': 6,
                'required': True
            },

            {
                'name': 'amount',
                'description': 'Amount of xp to remove',
                'type': 4,
                'required': True
            }
        ]
    )
    @has_permissions(administrator=True)
    async def removexp(self, ctx, user: discord.Member, amount: int):
        if ctx.guild is None:
            return

        if user.bot:
            await ctx.send(
                'Bots can\'t have xp dum dum. (Definitely not because of the fatal errors bots having xp causes)')
            return
        # Remove xp (make xp_amount negative to remove)
        try:
            self.my_database.add_xp(0 - amount, user.id, ctx.guild.id)

        except OverflowError:
            await ctx.send('Jeez, thats a big number. Please be nicer :frowning: :cry:')
            return
        await ctx.send(f"{amount} xp successfully removed from <@!{user.id}>\'s bank!")

    @removexp.error
    async def removexp_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                "You don't have permission to do that! You must have the \'Administrator\' permission to do that!")

        elif isinstance(error, commands.MemberNotFound):
            await ctx.send('The specified member was not found!')

        elif isinstance(error, commands.BadArgument):
            await ctx.send('Please set a valid amount of xp to remove')
'''

    # Create an automatically applying role
    @cog_ext.cog_slash(
        name="autorole",
        description="Automatically applying role for users of a certain level. Role must be below the bot's "
                    "role",
        options=[

            {
                'name': 'role',
                'description': 'Role to automatically apply',
                'type': 8,
                'required': True
            },
            {
                'name': 'minimum_level',
                'description': 'Minimum Level for Role to apply',
                'type': 4,
                'required': True
            }
        ]
    )
    @has_permissions(administrator=True)
    async def autorole(self, ctx, role: discord.Role, minimum_level: int):
        if ctx.guild is None:
            return
        try:
            self.my_database.create_new_auto_role(role.id, minimum_level, ctx.guild.id)
        except OverflowError:
            await ctx.send('Jeez, thats a big number. Please be nicer :frowning: :cry:')
            return
        await ctx.send(
            f"Successfully created automatic roling for {role.mention}, for users with a level of (at least) {minimum_level}")

        await autorole_apply(ctx.guild)

    @autorole.error
    async def autorole_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                "You don't have permission to do that! You must have the \'Administrator\' permission to do that!")

        elif isinstance(error, commands.RoleNotFound):
            await ctx.send('The specified role was not found!')

        elif isinstance(error, commands.BadArgument):
            await ctx.send('Please set a valid minimum level')

    @cog_ext.cog_slash(
        name="remove_autorole",
        description="Stop autoroling. Must have the 'Administrator' Permission.",

        options=[

            {
                'name': 'role',
                'description': 'Role to stop autoroling',
                'type': 8,
                'required': True
            },
        ]
    )
    @has_permissions(administrator=True)
    async def remove_autorole(self, ctx, role: discord.Role):
        if ctx.guild is None:
            return

        self.my_database.remove_autorole(role.id, ctx.guild.id)

        await ctx.send(f"Successfully removed automatic roling for {role.mention} (if existant)")

        await autorole_apply(ctx.guild)

    @remove_autorole.error
    async def remove_autorole_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                "You don't have permission to do that! You must have the \'Administrator\' permission to do that!")

        elif isinstance(error, commands.RoleNotFound):
            await ctx.send('The specified role was not found!')

    # Views all automatically applying roles
    @cog_ext.cog_slash(
        name='view_autoroles',
        description="View all automatically applying roles. Must have the 'Administrator' Permission",
    )
    @has_permissions(administrator=True)
    async def view_autoroles(self, ctx):
        if ctx.guild is None:
            return

        autoroles = self.my_database.autorole_guild(ctx.guild.id)

        autorole_list = []

        for rule in autoroles:
            autorole_list.append([rule[1], f"{ctx.guild.get_role(rule[0]).name}"])

        autorole_table = tabulate(autorole_list, headers=["Minimum Level", "Role"], tablefmt="fancy_grid")

        await ctx.send(f"Autoroles on {ctx.guild.name}:\n```{autorole_table}```")

    @view_autoroles.error
    async def view_autoroles_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                "You don't have permission to do that! You must have the \'Administrator\' permission to do that!")


def setup(bot):
    bot.add_cog(Admin(bot))
