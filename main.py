import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the Discord token from environment variables
TOKEN = os.getenv('DISCORD_TOKEN')

# Set up intents
intents = discord.Intents.default()
intents.message_content = True

# Create bot instance with command prefix
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    """Event handler for when the bot successfully connects."""
    print(f'{bot.user} has connected to Discord!')
    # Set the bot's activity status
    await bot.change_presence(activity=discord.Game(name='!ping'))

@bot.command(name='ping')
async def ping(ctx):
    """Returns the bot's latency in milliseconds."""
    latency_ms = round(bot.latency * 1000)
    await ctx.send(f'Pong! Latency: {latency_ms}ms')

@bot.command(name='hello')
async def hello(ctx):
    """Greets the user with their username."""
    await ctx.send(f'Hello, {ctx.author.name}!')

# Run the bot
if __name__ == '__main__':
    bot.run(TOKEN)