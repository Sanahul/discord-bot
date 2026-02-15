import discord
from discord.ext import commands
import os

# Validate token
TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    raise ValueError("No token found! Please set the DISCORD_TOKEN environment variable.")

# Create bot instance
bot = commands.Bot(command_prefix='!')

# Event to handle bot ready
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

# Error handling for commands
@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f'An error occurred: {str(error)}')

# Example command
@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

# Run the bot
try:
    bot.run(TOKEN)
except Exception as e:
    print(f'Error running the bot: {str(e)}')

