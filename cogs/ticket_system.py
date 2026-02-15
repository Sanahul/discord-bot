import discord
from discord.ext import commands

class TicketModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Create a Ticket")
        self.name = discord.ui.TextInput(label="Ticket Name", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        ticket_channel = await interaction.guild.create_text_channel(self.name.value)
        await interaction.response.send_message(f'Ticket created: {ticket_channel.mention}', ephemeral=True)

class TicketPanelView(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.primary)
    async def create_ticket(self, button: discord.ui.Button, interaction: discord.Interaction):
        modal = TicketModal()
        await interaction.response.send_modal(modal)

class TicketControlView(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger)
    async def close_ticket(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.channel.delete()
        await interaction.response.send_message('Ticket closed.', ephemeral=True)

class TicketSystem:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ticketpanel')
    @commands.has_permissions(manage_roles=True)
    async def ticket_panel(self, ctx):
        view = TicketPanelView()
        await ctx.send('Click to create a ticket:', view=view)