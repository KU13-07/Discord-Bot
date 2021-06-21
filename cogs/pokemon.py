import discord
from discord.ext import commands
import random
import asyncio
import json
import requests
from PIL import Image
from lxml import html

with open('config.json', 'r') as f:
    config = json.load(f)

class Pokemon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(self.qualified_name)

    @commands.group(aliases=['p'])
    async def pokemon(self, ctx):
        if ctx.channel.id == 855122761071984660:
            if ctx.invoked_subcommand is None:
                await help(ctx)

    @pokemon.command(aliases=['h'])
    async def help(self, ctx):
        await ctx.send("HELP")

    @pokemon.command(aliases=['aw','awtp', 'autowhosthatpokemon'])
    async def auto_whos_that_pokemon(ctx, lives: int=3, gen: int=None):
        if lives <= 10:
            while not lives == 0:
                if await whos_that_pokemon(ctx, gen, lives):
                    lives -= 1
            embed=discord.Embed(title="Pokémon", description=f"Auto Pokémon | 0 Lives Remaining", color=0xffcb05)
            await ctx.send(embed=embed)
            
    @pokemon.command(aliases=['wtp', 'w', 'whosthatpokemon'])
    async def whos_that_pokemon(self, ctx, gen: int=None, lives=None):
        if ctx.channel.id == 855122761071984660:
            f = 1, 898
            if gen:
                if gen <= 8:
                    if gen == 1:
                        f = 1, 151
                    elif gen == 2:
                        f = 152, 251
                    elif gen == 3:
                        f = 252, 386
                    elif gen == 4:
                        f = 387, 493
                    elif gen == 5:
                        f = 494, 649
                    elif gen == 6:
                        f = 650, 721
                    elif gen == 7:
                        f = 722, 809
                    elif gen == 8:
                        f = 810, 898
            e = random.randint(f[0],f[1])
            page = requests.get(f"https://www.pokemon.com/us/pokedex/{e}")
            
                    
            tree = html.fromstring(page.content)
            pName = tree.xpath('/html/body/div[4]/section[1]/div[2]/div/text()')[0].strip()
            if e == 32 or e == 29:
                pName = "Nidoran"
            pImg = tree.xpath('/html/body/div[4]/section[3]/div[1]/div[1]/div/img')[0].attrib.get('src')

            #Image Conversion
            img = Image.open(requests.get(pImg, stream=True).raw)
            img = img.convert("RGBA")
            datas = img.getdata()

            newData = []
            for item in datas:
                if item[3] != 0:
                    newData.append((0,0,0))
                else:
                    newData.append(item)
            img.putdata(newData)
            img.save("pokemon.png", "PNG")

            #Message Send
            a = "Who's That Pokémon?"
            f = ""
            l = ""
            if gen:
                f = f" | Generation {gen} Edition"
            if lives:
                a = "Auto Pokémon"
                l = f" | Lives Left: {lives}"
            embed=discord.Embed(title="Pokémon", description=f"{a}{f}{l}", color=0xffcb05)
            embed.set_image(url="attachment://pokemon.png")
            msg = await ctx.send(file=discord.File("pokemon.png"), embed=embed)

            def check(m):
                return m.content.lower() == pName.lower()
            r = False
            try:
                await self.bot.wait_for('message', check=check, timeout=config['pokemon_cooldown'])
            except asyncio.TimeoutError:
                embed.set_footer(text=f"Your {config['pokemon_cooldown']} seconds ran out, the correct answer was {pName}.")
                r = True
            else:
                embed.set_footer(text="Correct.")

            embed.set_image(url=pImg)
            await msg.edit(embed=embed, attachments=None)
            
            if r:
                return True

    @pokemon.command(aliases=['c'])
    @commands.has_permissions(administrator=True)  
    async def cooldown(self, ctx, cooldown: int=None):
        if cooldown != None:
            config["pokemon_cooldown"] = cooldown
            with open("../config.json", "w") as f:
                json.dump(config, f, indent=2)
        await ctx.send(config["pokemon_cooldown"])

def setup(bot):
    bot.add_cog(Pokemon(bot))