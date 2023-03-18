from ast import alias
import discord
from discord import app_commands
from discord.ext import commands
import interactions
from yt_dlp import YoutubeDL
import json
import time
loop = False
import ast
import gets

class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
        #all the music related stuff
        self.is_playing = False
        self.is_paused = False

        # 2d array containing [song, channel]
        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        self.vc = None

     #searching the item on youtube
    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try: 
                info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
            except Exception: 
                return False

        return {'source': info['formats'][0]['url'], 'title': info['title']}

    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            #get the first url
            m_url = self.music_queue[0][0]['source']

            #remove the first element as you are currently playing it
            if loop == False:
                self.music_queue.pop(0)
            else:
                time.sleep(1)
                pass
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False


    @app_commands.command(name="loop", description="Loops Current Playing Music")
    async def loop(self, ctx: discord.Interaction):
        global loop
        voice_channel = ctx.user.voice.channel
        if self.vc != None:
            if loop:
                await ctx.response.send_message('Loop mode is now `False!`')
                loop = False
                new_appender = gets.get_last_song()
                if self.music_queue[0][0]["title"] == new_appender["title"]:
                    self.music_queue.pop(0)
                else:
                    pass

            else:
                if self.is_playing == True:
                    new_appender = gets.get_last_song()
                    await ctx.response.send_message(f'Loop mode is now `True!`\nNow Looping: `{new_appender["title"]}`')
                    loop = True
                    self.music_queue.append([new_appender, voice_channel])
                else:
                    new_appender = gets.get_last_song()
                    self.music_queue.append([new_appender, voice_channel])
                    await ctx.response.send_message("Lopping Last Played Song Which is: `" + str(new_appender["title"]) + "`" + "\n" + "Loop mode is now `True`")
                    loop = True
                    await self.play_next()
        else:
            await ctx.response.send_message("Not Connected To Voice Channel :warning:")

    # infinite loop checking 
    async def play_music(self, ctx):
        global loop
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]['source']
            now_playing = self.music_queue[0][0]['title']
            #try to connect to voice channel if you are not already connected
            if self.vc == None or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()

                #in case we fail to connect
                if self.vc == None:
                    await ctx.send("Could not connect to the voice channel :warning:")
                    return
            else:
                await self.vc.move_to(self.music_queue[0][1])


            #remove the first element as you are currently playing it
            if loop == False:
                self.music_queue.pop(0)
            else:
                time.sleep(1)
                pass
            
            self.vc.play(discord.FFmpegPCMAudio(source=m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
            with open("now.txt", "w") as f:
                f.write(now_playing + "\n")
                f.close()
        else:
            self.is_playing = False

    @app_commands.command(name="play", description="Plays a selected song from youtube")
    async def play(self, ctx:discord.Interaction, song: str):
        global loop

        song_name = song

        query = "".join(song_name)
        if "https://www.youtube.com/watch?v=" in "".join(song_name):
            try:
                if "&t=" in "".join(song_name):
        
                    query = "".join(song_name).split("&t=", 1)[0]
                elif "?t=" in "".join(song_name):
                    query = "".join(song_name).split("?t=", 1)[0]
            except:
                pass
        elif "https://youtu.be/" in "".join(song_name):
            try:
                if "&t=" in "".join(song_name):
                    query = "".join(song_name).split("&t=", 1)[0]
                elif "?t=" in "".join(song_name):
                    query = "".join(song_name).split("?t=", 1)[0]
            except:
                pass
        voice_channel = ctx.user.voice.channel
        if voice_channel is None:
            #you need to be connected so that the bot knows where to go
            await ctx.reply("Connect to a voice channel!")
        elif self.is_paused:
            self.vc.resume()
        else:
            
            song = self.search_yt(query)
            embed_error = discord.Embed(title="Error :warning:", description="`Problem:`\n`Incorrect Format try another keyword. This error could be due to a playlist or livestream format`", color=discord.Color.red())
            song_embed = discord.Embed(title="Song Added :musical_note:", description="Song added to the queue \n " + "`" + song["title"] + "`", color=discord.Color.dark_blue())
            if type(song) == type(True):
                await ctx.response.send_message(embed=embed_error)
            else:
                await ctx.response.send_message(embed=song_embed)
                self.music_queue.append([song, voice_channel])

                with open("plays.txt", "w") as f:
                    f.write(str(song) + "\n")
                    f.close()

                if self.is_playing == False:
                    await self.play_music(ctx)

    @app_commands.command(name="pause", description="Pauses the current song being played")
    async def pause(self, ctx: discord.Interaction):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
        elif self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()
        await ctx.response.send_message("Paused Song :pause_button:")


    @app_commands.command(name = "resume", description="Resumes playing with the discord bot")
    async def resume(self, ctx: discord.Interaction):
        if self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()
            await ctx.response.send_message("Resuming Song :play_pause:")

    @app_commands.command(name="skip", description="Skips the current song being played")
    async def skip(self, ctx: discord.Interaction):
        global loop
        if loop == True:
            loop = False
            new_appender = gets.get_last_song()
            if self.music_queue[0][0]["title"] == new_appender["title"]:
                self.music_queue.pop(0)
            else:
                pass
        if self.vc != None and self.vc:
            self.vc.stop()
            #try to play next in the queue if it exists
            await self.play_music(ctx)
            await ctx.response.send_message("Skipped Song :white_check_mark: ")
        else:
            await ctx.response.send_message("Not Connected To Voice Channel :warning:")


    @app_commands.command(name="queue", description="Displays the current songs in queue")
    async def queue(self, ctx: discord.Interaction):
        retval = ""
        gets_resp = gets.get_last_song()
        if self.is_playing:
            # retval += f"`Playing`" + "  " + "`" + gets_resp['title'] +"`" + "\n"
            for i in range(0, len(self.music_queue)):
                # display a max of 5 songs in the current queue
                if (i > 4): break
                retval += f"`{str(i + 1)}`" + "  " + "`" + self.music_queue[i][0]['title'] +"`" + "\n"
            embed = discord.Embed(title="Music Queue :cd:",description=retval, color=discord.Color.dark_blue())
        else:
            for i in range(0, len(self.music_queue)):
                # display a max of 5 songs in the current queue
                if (i > 4): break
                retval += f"`{str(i + 1)}`" + "  " + "`" + self.music_queue[i][0]['title'] +"`" + "\n"
            embed = discord.Embed(title="Music Queue :cd:",description=retval, color=discord.Color.dark_blue())
        if retval != "":
            await ctx.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="Music Queue :cd:", description="No Music in Queue", color=discord.Color.dark_blue())
            await ctx.response.send_message(embed=embed)

    @app_commands.command(name="clear", description="Stops the music and clears the queue")
    async def clear(self, ctx: discord.Interaction):
        if self.vc != None and self.is_playing:
            self.vc.stop()
            loop = False
        self.music_queue = []
        await ctx.response.send_message("Music queue cleared :white_check_mark:")

    @app_commands.command(name="leave", description="Kick the bot from VC")
    async def dc(self, ctx: discord.Interaction):
        if self.vc == None:
            await ctx.response.send_message("Not In Voice Channel :warning:")
        else:
            global loop
            if loop == True:
                loop = False
            if self.vc != None and self.is_playing:
                self.vc.stop()
                loop = False
            self.music_queue = []
            self.is_playing = False
            self.is_paused = False
            await self.vc.disconnect()
            await ctx.response.send_message("Exited Voice Channel :white_check_mark:")
