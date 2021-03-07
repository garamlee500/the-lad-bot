import discord
import random
# Default embed setttings
class LadEmbed(discord.Embed):
    def __init__(self):
        super().__init__()
        self.type = 'rich'
        # use random colour
        self.colour = discord.Colour(int('%06x' % random.randrange(16**6),16))
        self.set_author(name = 'the-lad-bot',
                              url='https://github.com/garamlee500/the-lad-bot',
                              icon_url='https://yt3.ggpht.com/ytc/AAUvwniw3YNL9F5GjX0nNV6u0r1pMJ2HoUQiO281zDxG=s176-c-k-c0x00ffffff-no-rj')