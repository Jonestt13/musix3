import discord
from discord.ext import commands
from musix3 import Player
import config

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)


@bot.event
async def on_ready():
    print("f{bot.user.name} is ready")


bot.add_cog(Player(bot))
bot.run(config.Token)
