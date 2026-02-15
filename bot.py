import discord
from discord.ext import commands
import os
import asyncio

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot is online as {bot.user}')
    await bot.change_presence(activity=discord.Game(name="$help | Middleman Tickets"))
    print('✅ Ticket system loaded')

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
        await ctx.send("❌ Usage: `$purge <amount>`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Please provide a valid number. Usage: `$purge <amount>`")

# ===== SERVERINFO COMMAND =====
@bot.command()
async def serverinfo(ctx):
    """Display information about the server"""
    try:
        guild = ctx.guild
        
        if guild is None:
            await ctx.send("❌ This command can only be used in a server.")
            return
        
        # Create embed with server information
        embed = discord.Embed(
            title=f"📊 Server Information",
            description=f"Information about **{guild.name}**",
            color=0xFFC0CB  # Pink color
        )
        
        # Add server icon as thumbnail
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        # Add server information fields
        embed.add_field(name="🏷️ Server Name", value=guild.name, inline=True)
        embed.add_field(name="🆔 Server ID", value=guild.id, inline=True)
        embed.add_field(name="👑 Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
        embed.add_field(name="👥 Member Count", value=guild.member_count, inline=True)
        embed.add_field(name="📺 Channel Count", value=len(guild.channels), inline=True)
        embed.add_field(name="🎭 Role Count", value=len(guild.roles), inline=True)
        embed.add_field(name="📅 Creation Date", value=guild.created_at.strftime("%B %d, %Y"), inline=False)
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ An error occurred while fetching server information: {str(e)}")

async def load_cogs():
    """Load all cogs"""
    await bot.load_extension('cogs.ticket_system')
    print('✅ Loaded ticket_system cog')

async def main():
    """Main async function to start the bot"""
    async with bot:
        await load_cogs()
        
        # Load token
        TOKEN = os.getenv('DISCORD_TOKEN')
        if not TOKEN:
            raise ValueError("DISCORD_TOKEN not found! Set it as an environment variable.")
        
        await bot.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())