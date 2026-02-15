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

# ===== PURGE COMMAND =====
@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    if amount < 1 or amount > 100:
        await ctx.send("❌ Please provide a number between 1 and 100.", delete_after=5)
        return

    deleted = await ctx.channel.purge(limit=amount + 1)  # +1 to include the command message
    await ctx.send(f"🗑️ Deleted {len(deleted) - 1} messages.", delete_after=5)

@purge.error
async def purge_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command. (Requires `Manage Messages`)")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Usage: `!purge <amount>`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Please provide a valid number. Usage: `!purge <amount>`")

# Load token
TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    raise ValueError("DISCORD_TOKEN not found! Set it as an environment variable.")

bot.run(TOKEN)