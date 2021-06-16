import discord
from discord.ext import commands
import json
import requests
import os

with open('config.json') as f:
  config = json.load(f)
with open('data.json') as f:
  data = json.load(f)

api_key = config["api_key"]

bot = commands.Bot(command_prefix=config["prefix"],intents=discord.Intents.all(),case_insensitive=True)

def multiplier(member):
  if discord.utils.get(member.guild.roles, id=853986758789824582) in member.roles:
    return(2)
  elif discord.utils.get(member.guild.roles, id=853987031331504178) in member.roles:
    return(2)
  elif discord.utils.get(member.guild.roles, id=853987083672879125) in member.roles:
    return(1.75)
  elif discord.utils.get(member.guild.roles, id=853987124268761090) in member.roles:
    return(1.5)
  elif discord.utils.get(member.guild.roles, id=854039329897578516) in member.roles:
    return(1.25)
  else:
    return(1)  

@bot.event
async def on_ready():
  await update("e")
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

  if ctx.channel.id == 853983506120179714:
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
async def verify(ctx, arg=None):
  if arg:
    gData = requests.get(f'https://api.hypixel.net/guild?key={api_key}&name=aatrox').json()
    pData = requests.get(f"https://api.hypixel.net/player?key={api_key}&name={arg}").json()
    if pData["success"] and pData["player"] and pData["player"]["socialMedia"]:
      if pData["player"]["socialMedia"]["links"] and pData["player"]["socialMedia"]["links"]["DISCORD"]:
        if pData["player"]["socialMedia"]["links"]["DISCORD"] == f"{ctx.author.name}#{ctx.author.discriminator}":
          data[str(ctx.author.id)]["uuid"] = pData["player"]["uuid"]
          await ctx.author.add_roles(discord.utils.get(ctx.guild.roles,id=853985058050015243))
          for u in gData["guild"]["members"]:
            if pData["player"]["uuid"] == u["uuid"]:
              if u["rank"] != "Guild Master":
                await ctx.author.add_roles(discord.utils.get(ctx.guild.roles, id=854039329897578516), discord.utils.get(ctx.guild.roles,name=u["rank"]))
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

@bot.command(aliases=["bal"])
async def balance(ctx, member: discord.Member=None):
  if member:
    if member.bot: return
    await ctx.send(data[f'{member.id}']["Coins"])
  else:
    await ctx.send(data[f'{ctx.author.id}']["Coins"])

@bot.command(aliases=["lvl"])
async def level(ctx, member: discord.Member=None):
  if member:
    if member.bot: return
    await ctx.send(data[f'{member.id}']["LVL"])
  else:
    await ctx.send(data[f'{ctx.author.id}']["LVL"])

@bot.command(aliases=["exp"])
async def experience(ctx, member: discord.Member=None):
  if member:
    if member.bot: return
    await ctx.send(data[f'{member.id}']["EXP"])
  else:
    await ctx.send(data[f'{ctx.author.id}']["EXP"])

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
  guild = discord.utils.get(bot.guilds, id=848363067616395284)
  gData = requests.get(f'https://api.hypixel.net/guild?key={api_key}&name=aatrox').json()
  for m in guild.members:
    r = None
    if m.id != 263875673943179265 and not m.bot:
      await m.edit(roles=[])
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
        r = discord.utils.get(guild.roles, id=853985058050015243)
        for u in gData["guild"]["members"]:
          if data[f'{m.id}']["uuid"] == u["uuid"]:
            if u["rank"] != "Guild Master":
              await m.edit(roles=[r, discord.utils.get(guild.roles, id=854039329897578516), discord.utils.get(guild.roles,name=u["rank"])])
  print("update complete")

bot.run(config["token"])
