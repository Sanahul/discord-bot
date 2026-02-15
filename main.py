import discord
from discord.ext import commands

# Create a bot instance
bot = commands.Bot(command_prefix='!')

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command()
async def hello(ctx):
    await ctx.send('Hello!')

@bot.command()
async def mminfo(ctx):
    await ctx.send('MM Info here!')

@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    if amount <= 0 or amount > 100:
        await ctx.send('Please enter a number between 1 and 100.')
    else:
        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(f'Deleted {len(deleted)} messages.', delete_after=5)  

# Run the bot with the token
bot.run('YOUR_TOKEN')
