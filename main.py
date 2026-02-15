import discord
from discord.ext import commands

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    if amount <= 0:
        await ctx.send("Please provide a number greater than 0.")
        return
    deleted = await ctx.channel.purge(limit=amount)
    await ctx.send(f'Deleted {len(deleted)} messages.', delete_after=5)

@purge.error
async def purge_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have permission to use this command.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Please provide a valid number of messages to purge.")

bot.run('your_token_here')