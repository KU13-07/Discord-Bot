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

    @commands.group(aliases=['p'], invoke_without_command=True)
    async def pokemon(self, ctx, gen=None, lives=None):
        if not ctx.invoked_subcommand:
            if ctx.channel.id == 855122761071984660:
                IsGen = False
                f = 1, 898
                if gen:
                    try: 
                        gen = int(gen)
                        if gen <= 8:
                            IsGen = True
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
                    except:
                        pass
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
                if IsGen:
                    f = f" | Generation {gen} Edition"
                if lives:
                    a = "Auto Pokémon"
                    l = f" | Lives Left: {lives}"
                embed=discord.Embed(title="Pokémon", description=f"{a}{f}{l}", color=0xffcb05)
                embed.set_image(url="attachment://pokemon.png")
                msg = await ctx.send(file=discord.File("pokemon.png"), embed=embed)

                #Checks
                def check(m):
                    global condition
                    condition = None
                    if m.content.lower() == pName.lower():
                        condition = True
                        return True
                    elif m.content.lower() == 'skip':
                        condition = 'skip'
                        return True
                    elif m.content.lower() == 'end':
                        condition = 'end'
                        return True


                r = False
                ended = False
                try:
                    if await self.bot.wait_for('message', check=check, timeout=config['pokemon_cooldown']):
                        pass
                except asyncio.TimeoutError:
                    embed.set_footer(text=f"Your {config['pokemon_cooldown']} seconds ran out, the correct answer was {pName}.")
                    r = True
                if condition == True:
                    embed.set_footer(text="Correct.")
                elif condition == 'skip':
                    embed.set_footer(text=f"Skipped, the pokemon was {pName}.")
                elif condition == 'end':
                    embed.set_footer(text=f"Game ended.")
                    ended = True
                embed.set_image(url=pImg)
                await msg.edit(embed=embed, attachments=None)
                
                if ended:
                    return "end"
                if r:
                    return True

    @pokemon.command(aliases=['h'])
    async def help(self, ctx):
        await ctx.send("HELP")

    @pokemon.command(aliases=['a'])
    async def auto(self, ctx, lives: int=3, gen: int=None):
        if ctx.channel.id == 855122761071984660:
            if lives <= 5:
                while not lives == 0:
                    global r
                    r = await ctx.invoke(self.bot.get_command('pokemon'),gen=gen,lives=lives)
                    if r == "end":
                        lives = 0
                    elif r:
                        lives -= 1
                if r != 'end':
                    embed=discord.Embed(title="Pokémon", description=f"Auto Pokémon | 0 Lives Remaining", color=0xffcb05)
                    await ctx.send(embed=embed)

    @pokemon.command(aliases=['c'])
    @commands.has_permissions(administrator=True)  
    async def cooldown(self, ctx, cooldown: int=None):
        if cooldown != None:
            config["pokemon_cooldown"] = cooldown
            with open("../config.json", "w") as f:
                json.dump(config, f, indent=2)
        await ctx.send(config["pokemon_cooldown"])

    @commands.command()
    async def pokedex(self, ctx, arg=None):
        if arg:
            page =  requests.get(f'https://www.pokemon.com/us/pokedex/{arg}')
            if page:
                tree = html.fromstring(page.content)
                pName = tree.xpath('/html/body/div[4]/section[1]/div[2]/div/text()')[0].strip()
                pImg = tree.xpath('/html/body/div[4]/section[3]/div[1]/div[1]/div/img')[0].attrib.get('src')

                embed=discord.Embed(title="Pokedex", description=pName, url='https://www.pokemon.com/us/pokedex', color=0xffcb05)
                embed.set_thumbnail(url=pImg)
                embed.add_field(name="Version X", value=tree.xpath('/html/body/div[4]/section[3]/div[2]/div/div[1]/p[2]/text()')[0])
                embed.add_field(name="Version Y", value=tree.xpath('/html/body/div[4]/section[3]/div[2]/div/div[1]/p[1]/text()')[0])
                await ctx.send(embed=embed)                
def setup(bot):
    bot.add_cog(Pokemon(bot))