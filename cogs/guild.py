import discord
from discord.ext import commands
import requests
import json

class Guild(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config
        self.api_key = bot.config['api_key']

    @commands.Cog.listener()
    async def on_ready(self):
        print(self.qualified_name)

    @commands.command()
    async def gtop(self, ctx):
        gData = requests.get(f'https://api.hypixel.net/guild?key={self.api_key}&name=aatrox').json()
        day = None
        l = {}
        for u in gData["guild"]["members"]:
            for f in u["expHistory"]:
                if not day: day = f
            f = requests.get(f'https://api.mojang.com/user/profiles/{u["uuid"]}/names').json()
            l[f[-1]["name"]] = u["expHistory"][day]
        sort_orders = sorted(l.items(), key=lambda x: x[1], reverse=True)
        e = ""
        for x in range(0, 10):
            e += f'\n{x+1}. {sort_orders[x][0]} {sort_orders[x][1]} Guild Experience'
        await ctx.send(f"-----------------------------------------------------\n                       Top Guild Experience\n                       {day} (today)\n{e}\n-----------------------------------------------------")


def setup(bot):
    bot.add_cog(Guild(bot))