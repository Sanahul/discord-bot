import discord
from discord.ext import commands

TOKEN = 'your_token'

bot = commands.Bot(command_prefix='!')

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command()
async def hello(ctx):
    await ctx.send('Hello!')

bot.run(TOKEN)