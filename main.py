import os
import discord
from discord import Client, Intents
from discord.ui import Button, View

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
        await message.channel.send(f'Hello {message.author.name}!')

    elif message.content.startswith('!mminfo'):
        # Create embed for MM info
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
            value="MM's hold the items of the seller and wait for the buyer to give the items to the seller. Once this process has been completed the MM will transfer the items to the buyer. A photo with more details is shown below.",
            inline=False
        )
        
        embed.set_image(url="https://cdn.discordapp.com/attachments/1454752493203623966/1472424403911577701/image-34.webp?ex=69928596&is=69913416&hm=504d0260a6f9e25a8d48f9f79b6170f594444b542410670e0738fbb2d8769eb0&")
        
        # Create view with buttons
        view = View()
        
        async def understand_callback(interaction):
            await interaction.response.send_message(f"✅ {interaction.user.mention} understood", ephemeral=False)
        
        async def not_understand_callback(interaction):
            await interaction.response.send_message(f"❌ {interaction.user.mention} doesn't understand", ephemeral=False)
        
        button1 = Button(label="I understand", style=discord.ButtonStyle.green)
        button1.callback = understand_callback
        
        button2 = Button(label="Didn't understand", style=discord.ButtonStyle.red)
        button2.callback = not_understand_callback
        
        view.add_item(button1)
        view.add_item(button2)
        
        await message.channel.send(embed=embed, view=view)

# Run the bot
client.run(TOKEN)