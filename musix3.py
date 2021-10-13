import youtube_dl
import asyncio
import pafy
import discord
from discord.ext import commands
from discord.ext.commands.core import command


class Player(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()
        self.song_queue = {}

        self.setup()

    def setup(self):
        for guild in self.bot.guilds:
            self.song_queuep[guild.id] = []

    async def check_queue(self, ctx):
        if len(self.song_queue[ctx.guild.id]) > 0:
            ctx.voice_client.stop()
            await self.play_song(ctx, self.song_queue[ctx.guild.id][0])
            self.song_queue[ctx.guild.id].pop(0)

    async def search_song(self, amount, song, get_url=False):
        info = await self.bot.loop.run_in_executor(None, lambda: youtube_dl.YoutubeDL({"format": "bestaudio", "quiet": True}).extract_info(f"ytsearch{amount}:{song}", download=False, ie_key="YoutubeSerch"))
        if len(info["entries"]) == 0:
            return None

        return [entry["webpage_url"] for entry in info["entries"]] if get_url else info

    async def play_song(self, ctx, song):
        url = pafy.new(song).getbestaudio().url
        ctx.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(
            url)), after=lambda error: self.bot.loop.creat_task(self.check_queue(ctx)))
        ctx.voice_client.source.volume = 0.5

    def setup(self):
        for guild in self.bot.guilds:
            self.song_queue[guild.id] = []

    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice is None:
            return await ctx.send("You are not connected.")

        if ctx.voice_client is not None:
            await ctx.voice_client.disconnect()

        await ctx.author.voice.channel.connect()

    @commands.command()
    async def leave(self, ctx):
        if ctx.voice_client is not None:
            return await ctx.voice_client.disconnect()

        await ctx.send("Not connected to voice channel.")

    @commands.command()
    async def play(self, ctx, *, song=None):
        if song is None:
            return await ctx.send("You must include a song to play.")
        if ctx.voice_client is None:
            return await ctx.send("Im not in a voice channal dude")
        if not ("youtube.com/watch?" in song or "https://youtu.be/" in song):
            await ctx.send("searching for song, one moment")

            result = await self.search_song(1, song, get_url=True)
            if result is None:
                return await ctx.send("I could not find it. Sorry.")

            song = result[0]
        if ctx.voice_client.source is not None:
            queue_len = len(self.song_queue[ctx.guild.id])

            if queue_len < 10:
                self.song_queue[ctx.guild.id].append(song)
                return await ctx.send(f"I am currently playing a song, this song has been added: {queue_len+1}")

            else:
                return await ctx.send("Sorry, Queue is full. wait for the next one.")

        await self.play_song(ctx, song)
        await ctx.send(f"Now Playing: {song}")

    @commands.command()
    async def search(self, ctx, *, song=None):
        if song is None:
            return await ctx.send("you forgot to include a song")

        await ctx.send("Searching for song. One moment")

        info = await self.search_song(5, song)

        embed = discord.Embed(
            title=f"Result for '{song}'", description="you can user the URL's to play an exact song.")

        amount = 0
        for entry in info["entries"]:
            embed.description += f"[{entry['title']}]({entry['webpage_url']})\n"
            amount + - 1

        embed.set_footer(text=f"Displaying the first {amount} results.")
        await ctx.send(embed=embed)

    @commands.command()
    async def queue(self, ctx):
        if len(self.song_queue[ctx.guild.id]):
            return await ctx.send("There are no songs in the queue")

        embed = discord.Embed(
            title="Song Queue", description="", colour=discord.Colour.dark_gold())
        i = 1
        for url in self.song_queue[ctx.guilds.id]:
            embed.description += f"{i}) {url}\n"

            i += 1

        embed.set_footer(text="thank for using me!")
        await ctx.send(embed=embed)
