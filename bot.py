import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='$', intents=intents)


@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')


async def load_cogs():
    cogs_dir = os.path.join(os.path.dirname(__file__), 'cogs')
    if not os.path.exists(cogs_dir):
        print('⚠️  No cogs directory found, skipping cog loading')
        return
    for filename in os.listdir(cogs_dir):
        if filename.endswith('.py') and not filename.startswith('_'):
            cog_name = f'cogs.{filename[:-3]}'
            try:
                await bot.load_extension(cog_name)
                print(f'✅ Loaded cog: {cog_name}')
            except Exception as e:
                print(f'❌ Failed to load cog {cog_name}: {e}')


async def main():
    async with bot:
        await load_cogs()
        token = os.getenv('DISCORD_TOKEN')
        if not token:
            raise ValueError('DISCORD_TOKEN environment variable is not set')
        await bot.start(token)


if __name__ == '__main__':
    asyncio.run(main())