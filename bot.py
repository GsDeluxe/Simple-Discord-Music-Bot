
############################################### IMPORTS ###############################################

import asyncio
import functools
import itertools
import math
from signal import signal, SIGINT
import random
import requests
import json
import time
import threading
import os
import ffmpeg
import asyncio
import youtube_dl
import datetime
from async_timeout import timeout

import discord
from discord import app_commands # slash cmds
from discord.ext import commands
from discord.voice_client import VoiceClient
from discord.ext.commands import cooldown, BucketType
import interactions


import psutil
from music_cog_v2 import music_cog
import random2
import aiohttp

############################################### OTHER STUFF ###############################################

async def pyrandmeme():
    pymeme = discord.Embed(title="Meme", description="Meme Request", color=discord.Color.dark_blue())
    async with aiohttp.ClientSession() as cs:
        async with cs.get('https://www.reddit.com/r/memes/new.json?sort=hot') as r:
            res = await r.json()
            pymeme.set_image(url=res['data']['children'][random2.randint(0, 25)]['data']['url'])
            return pymeme
        await pyrandmeme()

############################################### BOT CREATION ###############################################

intents = discord.Intents.all()
intents.members = True
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix='d!', case_insensitive=True, description="The Superior Bot", intents=intents)
with open("TOKEN.txt", "r") as f:
	token = f.read()
	f.close()
intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix="m!", intents=intents)
bot.remove_command("help")


############################################### SETUP ###############################################

@bot.event
async def on_ready():
    print("Bot Is Ready")
    await bot.add_cog(music_cog(bot))
    await bot.change_presence(status = discord.Status.do_not_disturb, activity=discord.Game("With A PC"))
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} Commands") # sync cmds
    except Exception as e:
        print(e)


############################################### ERROR_HANDLE ###############################################

@bot.event
async def on_command_error(ctx, error):
  # Cooldown Error
  if isinstance(error, commands.CommandOnCooldown):
    embed = discord.Embed("**Cooldown**", Description="Please Wait {:.2f}s".format(error.retry_after), color=discord.Color.red())
    await ctx.reply(embed=embed)


############################################### MAINCMDS ###############################################

@bot.tree.command(name="help", description="All commands for this bot")
@commands.cooldown(1, 30, commands.BucketType.user)
async def help(interaction: discord.Interaction):
    embed = discord.Embed(title="Help Menu", description="Prefix: `/`\n\nCommands:", color=discord.Color.dark_blue())
    embed.add_field(name="Music Commands", value="`/play <song>`\n`/skip`\n`/loop`\n`/pause`\n`/resume`\n`/queue`\n`/clear`\n`/leave`", inline=True)
    embed.add_field(name="Other Commands", value="`/meme`\n`/ping`", inline=True)
    embed.set_footer(text = f"Requested by {interaction.user}")
    await interaction.response.send_message(embed = embed)



@bot.tree.command(name="ping", description="info about the server / bot")
@commands.cooldown(1, 30, commands.BucketType.user)
async def ping(interaction: discord.Interaction):
    cpuusage = psutil.cpu_percent()
    ramusage = psutil.virtual_memory().percent
    bytes = os.path.getsize("plays.txt")
    bytes_now = os.path.getsize("now.txt")
    embed = discord.Embed(title="Pong :ping_pong:", description=f"`Ping >> {round(bot.latency * 1000, 2)}ms`\n" + f"`CPU >> {str(cpuusage)}%`\n`RAM >> {str(ramusage)}%`\n`PLAYS >> {str(bytes)}B`\n`NOW >> {str(bytes_now)}B`", color=discord.Color.dark_blue())
    await interaction.response.send_message(embed = embed)





@bot.tree.command(name="meme", description="Generatre A meme from Reddit")
@commands.cooldown(1, 30, commands.BucketType.user)
async def meme(interaction: discord.Interaction):
    raw_data = os.popen("curl -s http://meme-api.com/gimme").read().strip()
    data = json.loads(raw_data)
    link = data["url"]
    title = data["title"]
    nsfw = data["nsfw"]
    subreddit = "subreddit: "+"r/" + data["subreddit"]
    if nsfw == True:
     embed = discord.Embed(title=title + "(NSFW)", description=subreddit + '\n\n', color=discord.Color.dark_blue())
     embed.set_image(url= "||" + link + "||")
    else:
        embed = discord.Embed(title=title, description=subreddit + '\n\n', color=discord.Color.dark_blue())
        embed.set_image(url=link)
    await interaction.response.send_message(embed=embed)

  # await interaction.response.send_message(embed=await pyrandmeme())

def check_nows_size():
    while True:
        if os.path.exists("now.txt"):
            bytes = os.path.getsize("now.txt")
            if int(bytes) > 100000000:
                os.remove("now.txt")
                with open("now.txt", "w", encoding="utf-8") as f:
                    f.close()
            else:
                print(f"Current 'now.txt' Byte Size: {str(bytes)}")
            time.sleep(1800)
        else:
            with open("now.txt", "w", encoding="utf-8") as f:
                f.close()

def check_plays_size():
    while True:
        if os.path.exists("plays.txt"):
            bytes = os.path.getsize("plays.txt")
            if int(bytes) > 100000000:
                os.remove("plays.txt")
                with open("plays.txt", "w", encoding="utf-8") as f:
                    f.close()
            else:
                print(f"Current 'plays.txt' Byte Size: {str(bytes)}")
            time.sleep(1800)
        else:
            with open("plays.txt", "w", encoding="utf-8") as f:
                f.close()

threading.Thread(target=check_plays_size, daemon=True).start()
threading.Thread(target=check_nows_size, daemon=True).start()
bot.run(token)


