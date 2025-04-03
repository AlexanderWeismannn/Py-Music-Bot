import discord
import asyncio
import re
import json
import os

from discord import SelectOption 
from discord.ext import commands
from discord.ui import Button, View, Select
from asyncio import run_coroutine_threadsafe
from urllib import parse, request
from yt_dlp import YoutubeDL

class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_playing = {}
        self.is_paused = {}
        self.music_queue = {}
        self.queue_index = {}
        self.vc = {}
        self.YTDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        self.FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn -filter:a "volume=0.9"'
        }

        self.embed_blue = 0x2c76dd
        self.embed_red = 0xdf1141
        self.embed_green = 0x0eaa51

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            id = int(guild.id)
            self.music_queue[id] = []
            self.queue_index[id] = 0
            self.vc[id] = None
            self.is_paused[id] = False
            self.is_playing[id] = False

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        id = int(member.guild.id)
        if member.id != self.bot.user.id and before.channel != None and after.channel != before.channel:
            remaining = before.channel.members
            if len(remaining) == 1 and remaining[0].id == self.bot.user.id and self.vc[id].is_connected():
                self.is_playing[id] = False
                self.is_paused[id] = False
                self.music_queue[id] = []
                self.queue_index[id] = 0
                await asyncio.sleep(3)
                await self.vc[id].disconnect()

    def get_yt_title(self, video_id):
        params = {"format": "json", "url": f"https://www.youtube.com/watch?v={video_id}"}
        url = "https://www.youtube.com/oembed?" + parse.urlencode(params)
        with request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            return data['title']

    def search_yt(self, search):
        query_string = parse.urlencode({'search_query': search})
        url = 'http://www.youtube.com/results?' + query_string
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = request.Request(url, headers=headers)

        try:
            with request.urlopen(req) as response:
                html = response.read().decode()
                search_results = re.findall(r'/watch\?v=(.{11})', html)
            return search_results[:10]
        except Exception as e:
            print(f"Search Error: {e}")
            return []

    def extract_yt(self, url):
        with YoutubeDL(self.YTDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
            except:
                return False

        return {
            'link': f'https://www.youtube.com/watch?v={url}',
            'thumbnail': f'https://i.ytimg.com/vi/{url}/hqdefault.jpg',
            'source': info.get('url'),
            'title': info['title']
        }

    def now_playing_embed(self, ctx, song):
        embed = discord.Embed(
            title="Now Playing:",
            description=f"[{song['title']}]({song['link']})",
            colour=self.embed_blue
        )
        embed.set_thumbnail(url=song['thumbnail'])
        embed.set_footer(text=f"Song added by: {ctx.author}", icon_url=ctx.author.avatar.url)
        return embed

    def add_song_embed(self, ctx, song):
        embed = discord.Embed(
            title="Song Added to Queue:",
            description=f"[{song['title']}]({song['link']})",
            colour=self.embed_red
        )
        embed.set_thumbnail(url=song['thumbnail'])
        embed.set_footer(text=f"Song added by: {ctx.author}", icon_url=ctx.author.avatar.url)
        return embed

    def play_next(self, ctx):
        id = int(ctx.guild.id)
        if not self.is_playing[id]:
            return

        if self.queue_index[id] + 1 < len(self.music_queue[id]):
            self.is_playing[id] = True
            self.queue_index[id] += 1
            song = self.music_queue[id][self.queue_index[id]][0]
            coro = ctx.send(embed=self.now_playing_embed(ctx, song))
            fut = run_coroutine_threadsafe(coro, self.bot.loop)
            try:
                fut.result()
            except:
                pass
            self.vc[id].play(discord.FFmpegPCMAudio(
                song['source'], **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(ctx))
        else:
            self.queue_index[id] += 1
            self.is_playing[id] = False

    async def play_music(self, ctx):
        id = int(ctx.guild.id)
        if self.queue_index[id] < len(self.music_queue[id]):
            self.is_playing[id] = True
            self.is_paused[id] = False
            await self.join_vc(ctx, self.music_queue[id][self.queue_index[id]][1])
            song = self.music_queue[id][self.queue_index[id]][0]
            await ctx.send(embed=self.now_playing_embed(ctx, song))
            self.vc[id].play(discord.FFmpegPCMAudio(
                song['source'], **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(ctx))
        else:
            await ctx.send("There are no songs left in queue to play...")
            self.queue_index[id] += 1
            self.is_playing[id] = False

    async def join_vc(self, ctx, channel):
        id = int(ctx.guild.id)
        try:
            print(f"🔍 Attempting to join VC: {channel.name}")
            if self.vc.get(id) is None or not self.vc[id].is_connected():
                self.vc[id] = await channel.connect()
                print("✅ Joined VC successfully.")
            else:
                await self.vc[id].move_to(channel)
                print("🔁 Moved to another VC.")
        except Exception as e:
            print(f"❌ VC connection failed: {e.__class__.__name__}: {e}")
            await ctx.send(f"Couldn't join the voice channel.\n**Reason:** `{e}`")



    @commands.command(name="join", aliases=["j", "jon", "jin", "alex", "ahoy", "blogtv"], help="Joins the user's voice channel")
    async def join(self, ctx):
        if ctx.author.voice:
            user_channel = ctx.author.voice.channel
            await self.join_vc(ctx, user_channel)
            await ctx.send(f"Music Bot has joined {user_channel}")
        else:
            await ctx.send("You need to be connected to a Voice Channel...")


    @commands.command(name="previous", aliases=["pr","prev"], help="Play the previous song in the queue")
    async def previous(self,ctx):

        id = int(ctx.guild.id)
        if self.vc[id] == None:
            await ctx.send("Must be in a VC to use this command")
        elif self.queue_index[id] <= 0: # replay our current song if list is 1
            await ctx.send("No previous song in the queue. Replaying current song")
            self.vc[id].pause()
            await self.play_music(ctx)
        elif self.vc[id] != None and self.vc[id]: # we can go backwards so play the previous song
            self.vc[id].pause()
            self.queue_index[id] -= 1
            await self.play_music(ctx)

    @commands.command(name="skip", aliases=["sk","next"], help="Play the previous song in the queue")
    async def skip(self,ctx):

        id = int(ctx.guild.id)
        if self.vc[id] == None:
            await ctx.send("Must be in a VC to use this command")
        elif self.queue_index[id] >= len(self.music_queue[id]) - 1: # there are no songs to skip to
            await ctx.send("No next song in queue. Replaying current song")
            self.vc[id].pause()
            await self.play_music(ctx)
        elif self.vc[id] != None and self.vc[id]: # we can go backwards so play the previous song
            self.vc[id].pause()
            self.queue_index[id] += 1
            await self.play_music(ctx)

        

    @commands.command(name="queue", aliases=["q","list"], help="Shows songs in the queue")
    async def queue(self,ctx):
        id = int(ctx.guild.id)
        return_val = ""
        if self.music_queue[id] == []:
            await ctx.send("No songs in the queue")
            return
        for i in range(self.queue_index[id],len(self.music_queue[id])):
            next_songs = len(self.music_queue[id]) - self.queue_index[id]
            if i > 5 + next_songs: # only print the next 5 songs
                break 
            return_index = i - self.queue_index[id]
            if return_index == 0:
                return_index = "Playing"
            elif return_index == 1:
                return_index = "Next"

            return_val += f"{return_index} - [{self.music_queue[id][i][0]['title']}]({self.music_queue[id][i][0]['link']})\n"

            if return_val == "":
                await ctx.send("There are no songs in the queue")
                return

        queue = discord.Embed(
            title="Current Queue",
            description=return_val,
            colour=self.embed_green
        ) 

        await ctx.send(embed=queue)


    @commands.command(name="play", aliases=["p", "Play"], help="Plays or resumes music")
    async def play(self, ctx, *args):
        search = " ".join(args)
        id = int(ctx.guild.id)
        try:
            userChannel = ctx.author.voice.channel
        except:
            await ctx.send("Need to be connected to a voice channel.")
            return

        if not args:
            if len(self.music_queue[id]) == 0:
                await ctx.send("No songs to play in the queue")
                return
            elif not self.is_playing[id]:
                if self.music_queue[id] == None or self.vc[id] == None:
                    await self.play_music(ctx)
                else:
                    self.is_paused[id] = False
                    self.is_playing[id] = True
                    self.vc[id].resume()
            return

        song = self.extract_yt(self.search_yt(search)[0])
        if type(song) == type(True):
            await ctx.send("Could not download song. Incorrect format; Try different keywords")
        else:
            self.music_queue[id].append([song, userChannel])
            if not self.is_playing[id]:
                await self.play_music(ctx)
            else:
                await ctx.send(embed=self.add_song_embed(ctx, song))

    @commands.command(name="pause", aliases=["ps", "Pause", "pa", "stop"], help="Pauses the current song")
    async def pause(self, ctx):
        id = int(ctx.guild.id)
        if not self.vc[id]:
            await ctx.send("No audio to pause...")
        elif self.is_playing[id]:
            await ctx.send("Audio Paused.")
            self.is_playing[id] = False
            self.is_paused[id] = True
            self.vc[id].pause()

    @commands.command(name="resume", aliases=["re", "res", "r"], help="Resumes paused audio")
    async def resume(self, ctx):
        id = int(ctx.guild.id)
        if not self.vc[id]:
            await ctx.send("No audio to resume...")
        elif self.is_paused[id]:
            await ctx.send("Resuming audio...")
            self.is_playing[id] = True
            self.is_paused[id] = False
            self.vc[id].resume()

    @commands.command(name="leave", aliases=["l", "peaceoutbye", "byebye", "lv"], help="Leaves the voice channel")
    async def leave(self, ctx):
        id = int(ctx.guild.id)
        if self.vc[id] != None:
            self.is_playing[id] = False
            self.is_paused[id] = False
            self.music_queue[id] = []
            self.queue_index[id] = 0
            await ctx.send("Music Bot left the chat. Bye Bye...")
            await self.vc[id].disconnect()
            self.vc[id] = None

    @commands.command(
        name="add",
        aliases=["a"],
        help="Add a song to the queue"
    )
    async def add(self,ctx,*args):
        search = " ".join(args)
        try:
            userChannel = ctx.author.voice.channel
        except:
            await ctx.send("Must be in a voice channel to add music.")
            return
        if not args:
            await ctx.send("Invalid Input...")
        else:
            song = self.extract_yt(self.search_yt(search)[0])
            if type(song) == type(False):
                await ctx.send("Could not download song. Wrong format. Try new keywords")
                return
            else:
                self.music_queue[ctx.guild.id].append([song,userChannel])
                message = self.add_song_embed(ctx,song)
                await ctx.send(embed=message)

    @commands.command(name="search", aliases=["s", "sr"], help="Returns a list of search results")
    async def search(self, ctx, *args):
        if not args:
            await ctx.send("Must specify search terms")
            return

        search = " ".join(args)
        try:
            userChannel = ctx.author.voice.channel
        except:
            await ctx.send("Must be connected to a voice channel")
            return

        await ctx.send("Searching...")

        song_tokens = self.search_yt(search)
        if not song_tokens:
            await ctx.send("No results found.")
            return

        song_names = []
        embed_text = ""
        for i, token in enumerate(song_tokens):
            url = 'https://www.youtube.com/watch?v=' + token
            name = self.get_yt_title(token)
            song_names.append(name)
            embed_text += f"{i + 1} - [{name}]({url})\n"

        select_menu = Select(
            placeholder="Select a song to play...",
            options=[
                SelectOption(label=f"{i+1} - {name[:95]}", value=str(i))
                for i, name in enumerate(song_names)
            ]
        )

        cancel_button = Button(
            label="Cancel",
            style=discord.ButtonStyle.danger,
            custom_id="cancel"
        )

        view = View()
        view.add_item(select_menu)
        view.add_item(cancel_button)

        embed = discord.Embed(title="Search Results", description=embed_text, colour=self.embed_red)
        message = await ctx.send(embed=embed, view=view)

        def check(interaction):
            return interaction.user == ctx.author and interaction.message.id == message.id

        try:
            interaction = await self.bot.wait_for("interaction", timeout=60.0, check=check)

            if interaction.data["component_type"] == 2:
                if interaction.data['custom_id'] == "cancel":
                    await interaction.response.edit_message(content="❌ Search cancelled.", embed=None, view=None)
                    return

            elif interaction.data["component_type"] == 3:
                await interaction.response.defer()

                chosen_index = int(interaction.data['values'][0])
                song_token = song_tokens[chosen_index]
                song_ref = self.extract_yt(song_token)

                if not song_ref:
                    await interaction.followup.send("Could not download song. Try a different input", ephemeral=True)
                    return

                guild_id = ctx.guild.id
                if guild_id not in self.music_queue:
                    self.music_queue[guild_id] = []
                    self.queue_index[guild_id] = 0
                    self.is_playing[guild_id] = False
                    self.is_paused[guild_id] = False
                    self.vc[guild_id] = None

                self.music_queue[guild_id].append([song_ref, userChannel])

                if not self.is_playing[guild_id]:
                    await self.play_music(ctx)

                embed_response = discord.Embed(
                    title=f"Option #{chosen_index + 1} Selected",
                    description=f"[{song_ref['title']}]({song_ref['link']}) added to queue!",
                    colour=self.embed_red
                )
                embed_response.set_thumbnail(url=song_ref["thumbnail"])

                await interaction.followup.edit_message(message_id=message.id, embed=embed_response, view=None)

        except asyncio.TimeoutError:
            await message.edit(content="⏰ Timed out.", view=None)

    
