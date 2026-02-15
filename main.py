import os
from discord import Client, Intents

# Load the Discord token from environment variables
TOKEN = os.getenv('DISCORD_TOKEN')

# Set intents for the bot
intents = Intents.default()
intents.message_content = True

client = Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!ping'):
        await message.channel.send('Pong!')

    elif message.content.startswith('!hello'):
        await message.channel.send('Hello!')

# Run the bot
client.run(TOKEN)