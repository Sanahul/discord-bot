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

# ===== BUTTON VIEW =====
class MMInfoView(discord.ui.View):

    @discord.ui.button(label="Understand", style=discord.ButtonStyle.success)
    async def understand(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            f"{interaction.user.mention} understood ✅",
            ephemeral=False
        )

    @discord.ui.button(label="Didn't understand", style=discord.ButtonStyle.danger)
    async def didnt_understand(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            f"{interaction.user.mention} didn't understand ❌",
            ephemeral=False
        )


# ===== COMMAND =====
@bot.command()
async def mminfo(ctx):
    embed = discord.Embed(
        title="Middleman Information",
        description="**What is a MM?**
A MM (Middleman) is a trusted member of our server handpicked by server owners. MM's are required to follow Discord's Terms of Service.

**MM Rules**
Once a ticket is created the MM that claims it is responsible for your trade. You cannot choose your MM. After this trade you are required to vouch for your MM, otherwise you will be blacklisted from our server.

**How a MM Works**
MM's hold the items of the seller and wait for the buyer to give the items to the seller. Once this process has been completed the MM will transfer the items to the buyer. A photo with more details is shown below.
.\n\nClick a button below to confirm.",
        color=discord.Color.blue()
    )

    await ctx.send(embed=embed, view=MMInfoView())

# Load token
TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    raise ValueError("DISCORD_TOKEN not found! Set it as an environment variable.")

bot.run(TOKEN)