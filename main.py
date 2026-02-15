import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!')

# Disabling the default help command
bot.remove_command('help')

# Custom commands (formerly help command)
@bot.command(name='commands')
async def commands(ctx):
    help_text = "Here are the commands you can use:
    - !command1
    - !command2\n    More commands coming soon!"
    await ctx.send(help_text)