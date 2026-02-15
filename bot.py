import discord
from discord.ext import commands
import os

# Bot setup
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot is online as {bot.user}')
    await bot.change_presence(activity=discord.Game(name="!help"))

# Load token
TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    raise ValueError("DISCORD_TOKEN not found! Set it as an environment variable.")

bot.run(TOKEN)