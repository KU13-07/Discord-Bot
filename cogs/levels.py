import discord
from discord.ext import commands
import json

def extract_level(json):
    print(json)

class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config
        self.data = bot.data

    @commands.Cog.listener()
    async def on_ready(self):
        print(self.qualified_name)

    @commands.command(aliases=["lvl", "exp", "experience"])
    async def level(self, ctx, member: commands.MemberConverter=None):
        f = None
        if member:
            if f'{member.id}' in self.data:
                e = self.data[f'{member.id}']
                f = [member, e['LVL'], e['EXP']]
            else: await ctx.send('user not in database')
        else:
            e = self.data[f'{ctx.author.id}']
            f = [ctx.author, e['LVL'], e['EXP']]
        if f:
            embed=discord.Embed(title="Levels", description=f'{f[0]} is currently level {f[1]}\nAnd {f[2]} exp / {(f[1]+5)*10} exp to the next level.', color=0x3a72f2)
            await ctx.send(embed=embed)
    
    @level.error
    async def level_error(self,ctx,error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.send('user not in database')

    @commands.command()
    async def leaderboard(self, ctx):
        f = sorted(self.data.items(), key=lambda k: k[1].get('LVL'), reverse=True)
        l = ""
        for x in range(0, 10):
            l += f'\n{x+1}. {ctx.guild.get_member(int(f[x][0]))} - {f[x][1].get("LVL")}'
        await ctx.send(l)

def setup(bot):
    bot.add_cog(Levels(bot))