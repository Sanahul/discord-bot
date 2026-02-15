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

# Ping command
@bot.command(name='ping')
async def ping(ctx):
    """Check bot latency"""
    latency = round(bot.latency * 1000)
    await ctx.send(f'🏓 Pong! Latency: {latency}ms')

# Purge command
@bot.command(name='purge')
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    """Delete messages from the channel"""
    if amount <= 0 or amount > 100:
        await ctx.send('❌ Please enter a number between 1 and 100.')
        return
    
    deleted = await ctx.channel.purge(limit=amount)
    await ctx.send(f'✅ Deleted {len(deleted)} messages.', delete_after=5)

@purge.error
async def purge_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command.")

# MMInfo command
@bot.command(name='mminfo')
async def mminfo(ctx):
    """Display Middleman (MM) information"""
    embed = discord.Embed(
        title="Middleman (MM) Information",
        description="Learn about our Middleman system",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="What is a MM?",
        value="A MM (Middleman) is a trusted member of our server handpicked by server owners. MM's are required to follow Discord's Terms of Service.",
        inline=False
    )
    
    embed.add_field(
        name="MM Rules",
        value="Once a ticket is created the MM that claims it is responsible for your trade. You cannot choose your MM. After this trade you are required to vouch for your MM, otherwise you will be blacklisted from our server.",
        inline=False
    )
    
    embed.add_field(
        name="How a MM Works",
        value="MM's hold the items of the seller and wait for the buyer to give the items to the seller. Once this process has been completed the MM will transfer the items to the buyer.",
        inline=False
    )
    
    await ctx.send(embed=embed)

# Load token
TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    raise ValueError("DISCORD_TOKEN not found! Set it as an environment variable.")

bot.run(TOKEN)