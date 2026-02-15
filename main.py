import discord
import os
from discord.ext import commands

# Intents are required for receiving certain events
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

# Bot command prefix
bot = commands.Bot(command_prefix='!', intents=intents)

# Event for when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found.")
    else:
        await ctx.send("An error occurred.")

# Ping command
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

# Hello command
@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention}!")

# Server information command
@bot.command()
async def mminfo(ctx):
    await ctx.send(f"This server's name is {ctx.guild.name} and it has {ctx.guild.member_count} members.")

# Purge command
@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"Deleted {amount} messages.", delete_after=5)

# Run the bot
TOKEN = os.getenv('DISCORD_TOKEN')  # Ensure your token is securely stored in environment variables
bot.run(TOKEN)