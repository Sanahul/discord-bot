import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = '!'

# Create bot instance
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Events
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print('------')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)

# Commands
@bot.command(name='ping', help='Responds with Pong!')
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

@bot.command(name='hello', help='Greets the user')
async def hello(ctx):
    await ctx.send(f'Hello {ctx.author.name}! 👋')

@bot.command(name='help', help='Shows all available commands')
async def help_command(ctx):
    embed = discord.Embed(title='Available Commands', color=discord.Color.blue())
    for command in bot.commands:
        embed.add_field(name=f'{PREFIX}{command.name}', value=command.help or 'No description', inline=False)
    await ctx.send(embed=embed)

# Run the bot
if __name__ == '__main__':
    bot.run(TOKEN)