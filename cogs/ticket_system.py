import discord
from discord.ext import commands

class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ticket')
    async def create_ticket(self, ctx):
        guild = ctx.guild
        ticket_channel = await guild.create_text_channel(f'ticket-{ctx.author.name}')
        await ticket_channel.send(f'Ticket created by {ctx.author.mention}. Please describe your issue.')
        await ctx.send(f'Ticket created: {ticket_channel.mention}')

    @commands.command(name='close_ticket')
    @commands.has_permissions(manage_channels=True)
    async def close_ticket(self, ctx):
        if ctx.channel.name.startswith('ticket-'):
            await ctx.send('Closing ticket...')
            await ctx.channel.delete()
        else:
            await ctx.send('This command can only be used in a ticket channel.')

def setup(bot):
    bot.add_cog(TicketSystem(bot))