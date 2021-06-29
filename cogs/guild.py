import discord
from discord.ext import commands
import requests
import json

with open('config.json') as f:
  config = json.load(f)
api_key = config["api_key"]

class Guild(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(self.qualified_name)

    @commands.command()
    async def gtop(self, ctx):
        gData = requests.get(f'https://api.hypixel.net/guild?key={api_key}&name=aatrox').json()
        day = None
        l = {}
        for u in gData["guild"]["members"]:
            for f in u["expHistory"]:
                if not day: day = f
            f = requests.get(f'https://api.mojang.com/user/profiles/{u["uuid"]}/names').json()
            l[f[-1]["name"]] = u["expHistory"][day]
        sort_orders = sorted(l.items(), key=lambda x: x[1], reverse=True)
        e = str()
        for i, v in enumerate(sort_orders):
            e += f'\n{i+1}. {v[1]} {v[0]} Guild Experience'
        await ctx.send(f"-----------------------------------------------------\n                       Top Guild Experience\n                       {day} (today)\n{e}\n-----------------------------------------------------")


def setup(bot):
    bot.add_cog(Guild(bot))