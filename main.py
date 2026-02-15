# Updated main.py to disable the default help command and set a custom help command

import discord
from discord.ext import commands

intents = discord.Intents.default()

# Create a bot instance with help_command set to None
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.command(name='commands')
async def commands(ctx):
    await ctx.send("Available commands:") # Add your custom command responses here

# Other bot events and commands can go here


# Start the bot
bot.run('YOUR_TOKEN')