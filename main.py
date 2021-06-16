import discord
from discord.ext import commands
import json
import requests
import os
import random
import asyncio

with open('config.json') as f:
  config = json.load(f)
with open('data.json') as f:
  data = json.load(f)

api_key = config["api_key"]

bot = commands.Bot(command_prefix=config["prefix"],intents=discord.Intents.all(),case_insensitive=True)

def multiplier(member):
  if member.guild.get_role(853986758789824582) in member.roles:
    return(2)
  elif member.guild.get_role(853986930735448085) in member.roles:
    return(2)
  elif member.guild.get_role(853987031331504178) in member.roles:
    return(2)
  elif member.guild.get_role(853987083672879125) in member.roles:
    return(1.75)
  elif member.guild.get_role(853987124268761090) in member.roles:
    return(1.5)
  elif member.guild.get_role(854039329897578516) in member.roles:
    return(1.25)
  else:
    return(1)  

async def rolesSetup(rolesChannel):
  await rolesChannel.purge(limit=100)
  embed=discord.Embed(title="Roles", description="React to the following roles that apply to you", color=0xf822fc)
  embed.add_field(name="1️⃣", value="she/her", inline=False)
  embed.add_field(name="2️⃣", value="he/him", inline=False)
  embed.add_field(name="3️⃣", value="they/them", inline=False)
  embed.add_field(name="4️⃣", value="it/itself", inline=False)
  embed.add_field(name="5️⃣", value="ze/zir", inline=False)
  embed.add_field(name="6️⃣", value="i prefer just my name - no pronouns", inline=False)
  embed.add_field(name="7️⃣", value="any/all", inline=False)
  embed.add_field(name="❌", value="Clear all cosmetic roles", inline=False)
  m = await rolesChannel.send(embed=embed)
  for i in ['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','❌']:
    await m.add_reaction(i)

@bot.event
async def on_ready():
  guild = bot.get_guild(848363067616395284)
  await update("e")
  await rolesSetup(bot.get_channel(854546485664546836))  
  print(bot.user)

@bot.event
async def on_member_join(member):
  if member.bot: return
  AuthorId = str(member.id)
  if not AuthorId in data:
    data[AuthorId] = {}
    data[AuthorId]["Coins"] = 0
    data[AuthorId]["LVL"] = 1
    data[AuthorId]["EXP"] = 0
  with open('data.json','w') as f:
    json.dump(data,f,indent=2)

@bot.event
async def on_reaction_add(reaction, user):
  if user.bot: return
  if reaction.message.channel.id == 854546485664546836:
    await reaction.message.remove_reaction(reaction, user)
    role = None
    if reaction.emoji == '1️⃣':
      role = "she/her"
    elif reaction.emoji == '2️⃣':
      role = 'he/him'
    elif reaction.emoji == '3️⃣':
      role = 'they/them'
    elif reaction.emoji == '4️⃣':
      role = 'it/itself'
    elif reaction.emoji == '5️⃣':
      role = 'ze/zir'
    elif reaction.emoji == '6️⃣':
      role = 'i prefer just my name - no pronouns'
    elif reaction.emoji == '7️⃣':
      role = 'any/all'
    if reaction.emoji == '❌':
      for role in user.roles:
        if not role.id == 848363067616395284 and not role.id == 854059398750404668 and not role.id == 853985058050015243 and not role.id == 854039329897578516 and not role.id == 853987124268761090 and not role.id == 853987083672879125 and not role.id == 853987031331504178 and not role.id == 854544288415088652 and not role.id == 853986930735448085 and not user.id == 263875673943179265:
          await user.remove_roles(role)
    else:
      if not discord.utils.get(reaction.message.guild.roles, name=role):
        await reaction.message.guild.create_role(name=role)
      await user.add_roles(discord.utils.get(reaction.message.guild.roles, name=role))


@bot.event
async def on_message(ctx):
  if ctx.author.bot: return
  if isinstance(ctx.channel, discord.channel.DMChannel): return

  AuthorId = str(ctx.author.id)
  data[AuthorId]["Coins"] += (1*multiplier(ctx.author))
  data[AuthorId]["EXP"] += (1*multiplier(ctx.author))

  if data[AuthorId]["EXP"] >= (data[AuthorId]["LVL"]+5) * 10:
    data[AuthorId]["EXP"] = 0
    data[AuthorId]["LVL"] += 1

  await bot.process_commands(ctx)

  if ctx.channel.id == 853983506120179714 or ctx.channel.id == 854546485664546836:
    await ctx.delete()

  with open('data.json','w') as f:
    json.dump(data,f,indent=2)

@bot.command()
async def gexp(ctx, arg=None):
  if arg:
    if len(arg) >= 3:
      m = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{arg}").json()
      if "id" in m:
        gData = requests.get(f'https://api.hypixel.net/guild?key={api_key}&name=aatrox').json()
        for u in gData["guild"]["members"]:
          if m["id"] == u["uuid"]:
            l = []
            for i in u["expHistory"]:
              l.append(u["expHistory"][i])
            await ctx.send(sum(l))

@bot.command()
async def gtop(ctx):
  gData = requests.get(f'https://api.hypixel.net/guild?key={api_key}&name=aatrox').json()
  day = None
  l = {}
  for u in gData["guild"]["members"]:
    for f in u["expHistory"]:
      if not day:
          day = f
    f = requests.get(f'https://api.mojang.com/user/profiles/{u["uuid"]}/names').json()
    l[f[-1]["name"]] = u["expHistory"][day]
  sort_orders = sorted(l.items(), key=lambda x: x[1], reverse=True)
  e = str()
  for i, v in enumerate(sort_orders):
    e += f'\n{i+1}. {v[1]} {v[0]} Guild Experience'
  await ctx.send(f"-----------------------------------------------------\n                       Top Guild Experience\n                       {day} (today)\n{e}\n-----------------------------------------------------")

@bot.command(aliases=['p'])
async def pokemon(ctx):
  f = random.choice(os.listdir("Pokemon"))
  e = f[4:-4]
  await ctx.send(file=discord.File(f'Pokemon/{f}'))
  def check(m):
    return m.content.lower() == e.lower()
  try:
    await bot.wait_for('message', check=check, timeout=10)
  except asyncio.TimeoutError:
    await ctx.send(f'Your 10 seconds ran out, the correct answer was {e}.')
  else:
    await ctx.send("Correct")

@bot.command()
async def role(ctx, arg=None):
  if arg:
    if not discord.utils.get(ctx.guild.roles, name=arg):
      await ctx.guild.create_role(name=arg)
    await ctx.author.add_roles(discord.utils.get(ctx.guild.roles, name=arg))

@bot.command()
async def verify(ctx, arg=None):
  if arg:
    gData = requests.get(f'https://api.hypixel.net/guild?key={api_key}&name=aatrox').json()
    pData = requests.get(f"https://api.hypixel.net/player?key={api_key}&name={arg}").json()
    if pData["success"] and pData["player"] and pData["player"]["socialMedia"]:
      if pData["player"]["socialMedia"]["links"] and pData["player"]["socialMedia"]["links"]["DISCORD"]:
        if pData["player"]["socialMedia"]["links"]["DISCORD"] == f"{ctx.author.name}#{ctx.author.discriminator}":
          data[str(ctx.author.id)]["uuid"] = pData["player"]["uuid"]
          await ctx.author.add_roles(ctx.guild.get_role(853985058050015243))
          for u in gData["guild"]["members"]:
            if pData["player"]["uuid"] == u["uuid"]:
              if u["rank"] != "Guild Master":
                await ctx.author.add_roles(ctx.guild.get_role(854039329897578516), discord.utils.get(ctx.guild.roles,name=u["rank"]))
          msg = await ctx.send("Success")
          await msg.delete(delay=2)
          if ctx.author.id != 263875673943179265:
            await ctx.author.edit(nick=pData["player"]["displayname"])
        else:
          msg = await ctx.send("Error, not a match")
          await msg.delete(delay=3)
      else:
          msg = await ctx.send("Error, no discord attached to account")
          await msg.delete(delay=3)
    else:
      msg = await ctx.send("Error, api on cooldown, please try again in a minute.")
      await msg.delete(delay=3)
  else:
    msg = await ctx.send("Error, no username given")
    await msg.delete(delay=3)

@bot.command(aliases=["bal","purse"])
async def balance(ctx, member: discord.Member=None):
  if member:
    if member.bot: return
    await ctx.send(data[f'{member.id}']["Coins"])
  else:
    await ctx.send(data[f'{ctx.author.id}']["Coins"])

@bot.command(aliases=["lvl", "exp", "experience"])
async def level(ctx, member: discord.Member=None):
  if member:
    if member.bot: return
    embed=discord.Embed(title="Leveling", description=f'You are level {data[f"{member.id}"]["LVL"]}\nExperience: {data[f"{member.id}"]["EXP"]} / {(data[f"{member.id}"]["LVL"]+5)*10}', color=0x3a72f2)
    await ctx.send(embed=embed)
  else:
    embed=discord.Embed(title="Leveling", description=f'You are level {data[f"{ctx.author.id}"]["LVL"]}\nExperience: {data[f"{ctx.author.id}"]["EXP"]} / {(data[f"{ctx.author.id}"]["LVL"]+5)*10}', color=0x3a72f2)
    await ctx.send(embed=embed)

#Moderation
@bot.command(aliases=["purge"])
@commands.has_permissions(manage_messages=True)  
async def clear(ctx, number: int=None):
  if number:
    await ctx.channel.purge(limit=number)

@bot.command()
@commands.has_permissions(administrator=True)  
async def update(ctx):
  print("starting update")
  guild = bot.get_guild(848363067616395284)
  gData = requests.get(f'https://api.hypixel.net/guild?key={api_key}&name=aatrox').json()
  for m in guild.members:
    r = None
    if m.id != 263875673943179265 and not m.bot and not guild.get_role(854544288415088652) in m.roles:
      await m.remove_roles(
        guild.get_role(853986930735448085),
        guild.get_role(853987031331504178),
        guild.get_role(853987083672879125),
        guild.get_role(853987124268761090),
        guild.get_role(854039329897578516),
        guild.get_role(853985058050015243))
      if not f'{m.id}' in data:
        data[f'{m.id}'] = {}
        data[f'{m.id}']["Coins"] = 0
        data[f'{m.id}']["LVL"] = 1
        data[f'{m.id}']["EXP"] = 0
        with open('data.json','w') as f:
          json.dump(data,f,indent=2)
      if "uuid" in data[f'{m.id}']:
        pData = requests.get(f"https://api.hypixel.net/player?key={api_key}&uuid={data[str(m.id)]['uuid']}").json()
        await m.edit(nick=pData["player"]["displayname"])
        r = guild.get_role(853985058050015243)
        for u in gData["guild"]["members"]:
          if data[f'{m.id}']["uuid"] == u["uuid"]:
            if u["rank"] != "Guild Master":
              await m.add_roles(r, guild.get_role(854039329897578516), discord.utils.get(guild.roles,name=u["rank"]))
  print("update complete")

bot.run(config["token"])
