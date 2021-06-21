import discord
from discord.ext import commands
import youtube_dl
import os

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(self.qualified_name)

    @commands.command(aliases=['join'])
    async def connect(self, ctx):
        voice = ctx.author.voice
        if voice:
            botVoice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
            if not botVoice:
                await voice.channel.connect()
            elif botVoice.is_connected() and botVoice.channel == ctx.author.voice.channel:
                print('already connected to your channel')
            else:
               await botVoice.move_to(voice.channel)
        else:
            print('user not in voice channel')

    @commands.command(aliases=['leave'])
    async def disconnect(self, ctx):
        if ctx.author.voice:
            voice_client = discord.utils.get(self.bot.voice_clients, channel=ctx.author.voice.channel)
            if voice_client:
                if voice_client.channel == ctx.author.voice.channel:
                    await voice_client.disconnect()

    @commands.command()
    async def cleanup(self, ctx):
        for voice_client in self.bot.voice_clients:
            await voice_client.disconnect()

    @commands.command()
    async def play(self, ctx, url: str=None):
        if not discord.utils.get(self.bot.voice_clients, guild=ctx.guild):
            await self.bot.get_command('connect').invoke(ctx)
        botVoice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if botVoice:
            if ctx.author.voice.channel == botVoice.channel:
                song_there = os.path.isfile('song.mp3')
                try:
                    if song_there:
                        os.remove('song.mp3')
                except PermissionError:
                    await ctx.send("Wait for the current playing music to end or use the 'stop' command.")

                ydl_opts = {
                    'format': 'worstaudio',
                    'outtmpl': 'song.mp3',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                }
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    try:
                        ydl.download([url])
                        botVoice.play(discord.FFmpegPCMAudio("song.mp3"))
                    except:
                        print('An error has occured')
    
    @commands.command()
    async def stop(self, ctx):
        botVoice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        voice = ctx.author.voice
        if botVoice and ctx.author.voice:
            if botVoice.channel == voice.channel:
                botVoice.stop()

def setup(bot):
    bot.add_cog(Music(bot))