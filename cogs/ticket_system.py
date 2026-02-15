import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
import asyncio
from datetime import datetime, timezone

class TicketModal(discord.ui.Modal, title='Create Middleman Ticket'):
    """Modal form for creating a new ticket"""
    
    other_trader = discord.ui.TextInput(
        label='What is the other trader user?',
        placeholder='Enter username or ID',
        required=True,
        max_length=100
    )
    
    giving = discord.ui.TextInput(
        label='What are you giving?',
        placeholder='Describe what you are giving',
        required=True,
        style=discord.TextStyle.paragraph,
        max_length=500
    )
    
    receiving = discord.ui.TextInput(
        label='What is the other trader giving?',
        placeholder='Describe what the other trader is giving',
        required=True,
        style=discord.TextStyle.paragraph,
        max_length=500
    )
    
    def __init__(self, cog):
        super().__init__()
        self.cog = cog
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Create the ticket
            ticket_channel = await self.cog.create_ticket(
                interaction.guild,
                interaction.user,
                str(self.other_trader),
                str(self.giving),
                str(self.receiving)
            )
            
            await interaction.followup.send(
                f'✅ Ticket created successfully! {ticket_channel.mention}',
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(
                f'❌ Error creating ticket: {str(e)}',
                ephemeral=True
            )

class TicketPanelView(discord.ui.View):
    """Persistent view with Create Ticket button"""
    
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog
    
    @discord.ui.button(
        label='Create Ticket',
        style=discord.ButtonStyle.green,
        emoji='🎫',
        custom_id='create_ticket_button'
    )
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = TicketModal(self.cog)
        await interaction.response.send_modal(modal)

class TicketControlView(discord.ui.View):
    """View with Claim and Close buttons for ticket management"""
    
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog
    
    @discord.ui.button(
        label='Claim',
        style=discord.ButtonStyle.primary,
        emoji='✋',
        custom_id='claim_ticket_button'
    )
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.cog.handle_claim(interaction)
    
    @discord.ui.button(
        label='Close',
        style=discord.ButtonStyle.danger,
        emoji='🔒',
        custom_id='close_ticket_button'
    )
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.cog.handle_close_button(interaction)

class TicketSystem(commands.Cog):
    """Middleman ticket system for Discord bot"""
    
    def __init__(self, bot):
        self.bot = bot
        self.tickets = {}  # Store ticket data {channel_id: ticket_info}
        self.ticket_counter = 0
        
        # Configuration - can be customized via commands later
        self.config = {
            'category_id': None,  # Category for ticket channels
            'support_role_id': None,  # Support/Middleman role ID
            'log_channel_id': None,  # Channel for ticket logs
        }
    
    async def cog_load(self):
        """Called when cog is loaded"""
        # Add persistent views
        self.bot.add_view(TicketPanelView(self))
        self.bot.add_view(TicketControlView(self))
    
    def get_support_role(self, guild: discord.Guild) -> Optional[discord.Role]:
        """Get the Middleman/Support role"""
        # Try to find by stored ID first
        if self.config['support_role_id']:
            role = guild.get_role(self.config['support_role_id'])
            if role:
                return role
        
        # Fallback: search for role by name
        for role in guild.roles:
            if 'middleman' in role.name.lower() or 'support' in role.name.lower():
                self.config['support_role_id'] = role.id
                return role
        
        return None
    
    def has_support_role(self, member: discord.Member) -> bool:
        """Check if member has support role"""
        support_role = self.get_support_role(member.guild)
        if not support_role:
            # If no support role found, allow members with manage_channels permission
            return member.guild_permissions.manage_channels
        return support_role in member.roles
    
    async def get_ticket_category(self, guild: discord.Guild) -> discord.CategoryChannel:
        """Get or create the ticket category"""
        if self.config['category_id']:
            category = guild.get_channel(self.config['category_id'])
            if category:
                return category
        
        # Create new category
        category = await guild.create_category('Middleman Tickets')
        self.config['category_id'] = category.id
        return category
    
    async def create_ticket(
        self,
        guild: discord.Guild,
        creator: discord.Member,
        other_trader: str,
        giving: str,
        receiving: str
    ) -> discord.TextChannel:
        """Create a new ticket channel"""
        
        # Get category
        category = await self.get_ticket_category(guild)
        
        # Increment ticket counter
        self.ticket_counter += 1
        ticket_num = self.ticket_counter
        
        # Create channel name
        channel_name = f'ticket-{ticket_num}-{creator.name.lower()}'
        
        # Get support role
        support_role = self.get_support_role(guild)
        
        # Set up permissions
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            creator: discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True,
                attach_files=True,
                embed_links=True
            ),
            guild.me: discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True,
                manage_channels=True,
                manage_messages=True
            )
        }
        
        if support_role:
            overwrites[support_role] = discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True,
                attach_files=True,
                embed_links=True,
                manage_messages=True
            )
        
        # Create the channel
        channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites
        )
        
        # Store ticket data
        self.tickets[channel.id] = {
            'ticket_num': ticket_num,
            'creator': creator.id,
            'other_trader': other_trader,
            'giving': giving,
            'receiving': receiving,
            'claimed_by': None,
            'created_at': datetime.now(timezone.utc),
            'status': 'open',
            'renamed': False
        }
        
        # Create embed
        embed = discord.Embed(
            title=f'🎫 Ticket #{ticket_num}',
            description='Middleman ticket created',
            color=discord.Color.green(),
            timestamp=datetime.now(timezone.utc)
        )
        embed.add_field(name='Creator', value=creator.mention, inline=True)
        embed.add_field(name='Other Trader', value=other_trader, inline=True)
        embed.add_field(name='Status', value='🟢 Open', inline=True)
        embed.add_field(name='Creator Gives', value=giving, inline=False)
        embed.add_field(name='Other Trader Gives', value=receiving, inline=False)
        
        # Send initial message with control buttons
        view = TicketControlView(self)
        msg = await channel.send(
            content=f'{creator.mention}' + (f' {support_role.mention}' if support_role else ''),
            embed=embed,
            view=view
        )
        
        # Pin the message
        await msg.pin()
        
        # Log ticket creation
        await self.log_ticket_action(guild, f'Ticket #{ticket_num} created by {creator}', channel)
        
        return channel
    
    async def handle_claim(self, interaction: discord.Interaction):
        """Handle claim button/command"""
        channel = interaction.channel
        
        if channel.id not in self.tickets:
            await interaction.response.send_message('❌ This is not a ticket channel!', ephemeral=True)
            return
        
        # Check if user has support role
        if not self.has_support_role(interaction.user):
            await interaction.response.send_message('❌ You need the Middleman role to claim tickets!', ephemeral=True)
            return
        
        ticket = self.tickets[channel.id]
        
        # Check if already claimed
        if ticket['claimed_by']:
            claimer = interaction.guild.get_member(ticket['claimed_by'])
            await interaction.response.send_message(
                f'❌ This ticket is already claimed by {claimer.mention if claimer else "someone"}!',
                ephemeral=True
            )
            return
        
        # Claim the ticket
        ticket['claimed_by'] = interaction.user.id
        ticket['status'] = 'claimed'
        
        embed = discord.Embed(
            title='✋ Ticket Claimed',
            description=f'{interaction.user.mention} has claimed this ticket!',
            color=discord.Color.blue(),
            timestamp=datetime.now(timezone.utc)
        )
        
        await interaction.response.send_message(embed=embed)
        await self.log_ticket_action(interaction.guild, f'Ticket #{ticket["ticket_num"]} claimed by {interaction.user}', channel)
    
    async def handle_close_button(self, interaction: discord.Interaction):
        """Handle close button"""
        await interaction.response.defer()
        await self.close_ticket(interaction.channel, interaction.user, interaction.guild)
    
    async def close_ticket(self, channel: discord.TextChannel, closer: discord.Member, guild: discord.Guild):
        """Close a ticket channel"""
        if channel.id not in self.tickets:
            return
        
        # Check if user has support role
        if not self.has_support_role(closer):
            return
        
        ticket = self.tickets[channel.id]
        ticket['status'] = 'closed'
        
        # Create transcript embed
        embed = discord.Embed(
            title=f'🔒 Ticket #{ticket["ticket_num"]} Closed',
            description=f'Ticket closed by {closer.mention}',
            color=discord.Color.red(),
            timestamp=datetime.now(timezone.utc)
        )
        embed.add_field(name='Creator', value=f'<@{ticket["creator"]}>', inline=True)
        embed.add_field(name='Other Trader', value=ticket['other_trader'], inline=True)
        if ticket['claimed_by']:
            embed.add_field(name='Claimed By', value=f'<@{ticket["claimed_by"]}>', inline=True)
        
        await channel.send(embed=embed)
        await self.log_ticket_action(guild, f'Ticket #{ticket["ticket_num"]} closed by {closer}', channel)
        
        # Delete ticket data
        del self.tickets[channel.id]
        
        # Delete channel after 5 seconds
        await asyncio.sleep(5)
        await channel.delete(reason=f'Ticket closed by {closer}')
    
    async def log_ticket_action(self, guild: discord.Guild, message: str, channel: discord.TextChannel = None):
        """Log ticket actions to log channel"""
        if self.config['log_channel_id']:
            log_channel = guild.get_channel(self.config['log_channel_id'])
            if log_channel:
                embed = discord.Embed(
                    description=message,
                    color=discord.Color.blue(),
                    timestamp=datetime.now(timezone.utc)
                )
                if channel:
                    embed.add_field(name='Channel', value=channel.mention)
                await log_channel.send(embed=embed)
    
    # ===== COMMANDS =====
    
    @commands.command(name='add')
    async def add_user(self, ctx, member: discord.Member):
        """Add a user to the ticket"""
        if ctx.channel.id not in self.tickets:
            await ctx.send('❌ This command can only be used in ticket channels!')
            return
        
        # Add permission to view channel
        await ctx.channel.set_permissions(
            member,
            read_messages=True,
            send_messages=True,
            attach_files=True,
            embed_links=True
        )
        
        embed = discord.Embed(
            description=f'✅ {member.mention} has been added to the ticket!',
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
        
        ticket = self.tickets[ctx.channel.id]
        await self.log_ticket_action(ctx.guild, f'{member} added to ticket #{ticket["ticket_num"]} by {ctx.author}', ctx.channel)
    
    @commands.command(name='remove')
    async def remove_user(self, ctx, member: discord.Member):
        """Remove a user from the ticket"""
        if ctx.channel.id not in self.tickets:
            await ctx.send('❌ This command can only be used in ticket channels!')
            return
        
        ticket = self.tickets[ctx.channel.id]
        
        # Don't allow removing the creator
        if member.id == ticket['creator']:
            await ctx.send('❌ Cannot remove the ticket creator!')
            return
        
        # Remove permission to view channel
        await ctx.channel.set_permissions(member, overwrite=None)
        
        embed = discord.Embed(
            description=f'✅ {member.mention} has been removed from the ticket!',
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)
        
        await self.log_ticket_action(ctx.guild, f'{member} removed from ticket #{ticket["ticket_num"]} by {ctx.author}', ctx.channel)
    
    @commands.command(name='claim')
    async def claim_command(self, ctx):
        """Claim the ticket (staff only)"""
        if ctx.channel.id not in self.tickets:
            await ctx.send('❌ This command can only be used in ticket channels!')
            return
        
        # Check if user has support role
        if not self.has_support_role(ctx.author):
            await ctx.send('❌ You need the Middleman role to claim tickets!')
            return
        
        ticket = self.tickets[ctx.channel.id]
        
        # Check if already claimed
        if ticket['claimed_by']:
            claimer = ctx.guild.get_member(ticket['claimed_by'])
            await ctx.send(f'❌ This ticket is already claimed by {claimer.mention if claimer else "someone"}!')
            return
        
        # Claim the ticket
        ticket['claimed_by'] = ctx.author.id
        ticket['status'] = 'claimed'
        
        embed = discord.Embed(
            title='✋ Ticket Claimed',
            description=f'{ctx.author.mention} has claimed this ticket!',
            color=discord.Color.blue(),
            timestamp=datetime.now(timezone.utc)
        )
        
        await ctx.send(embed=embed)
        await self.log_ticket_action(ctx.guild, f'Ticket #{ticket["ticket_num"]} claimed by {ctx.author}', ctx.channel)
    
    @commands.command(name='unclaim')
    async def unclaim_command(self, ctx):
        """Unclaim the ticket (staff only)"""
        if ctx.channel.id not in self.tickets:
            await ctx.send('❌ This command can only be used in ticket channels!')
            return
        
        # Check if user has support role
        if not self.has_support_role(ctx.author):
            await ctx.send('❌ You need the Middleman role to unclaim tickets!')
            return
        
        ticket = self.tickets[ctx.channel.id]
        
        # Check if claimed
        if not ticket['claimed_by']:
            await ctx.send('❌ This ticket is not claimed!')
            return
        
        # Check if claimed by this user
        if ticket['claimed_by'] != ctx.author.id:
            await ctx.send('❌ You can only unclaim tickets you have claimed!')
            return
        
        # Unclaim the ticket
        ticket['claimed_by'] = None
        ticket['status'] = 'open'
        
        embed = discord.Embed(
            title='🔓 Ticket Unclaimed',
            description=f'{ctx.author.mention} has unclaimed this ticket!',
            color=discord.Color.gold(),
            timestamp=datetime.now(timezone.utc)
        )
        
        await ctx.send(embed=embed)
        await self.log_ticket_action(ctx.guild, f'Ticket #{ticket["ticket_num"]} unclaimed by {ctx.author}', ctx.channel)
    
    @commands.command(name='renameticket')
    async def rename_ticket(self, ctx, *, name: str):
        """Rename the ticket (won't auto-close after 1 hour)"""
        if ctx.channel.id not in self.tickets:
            await ctx.send('❌ This command can only be used in ticket channels!')
            return
        
        ticket = self.tickets[ctx.channel.id]
        
        # Mark as renamed (prevents auto-close)
        ticket['renamed'] = True
        
        # Rename channel
        old_name = ctx.channel.name
        new_name = name.lower().replace(' ', '-')
        await ctx.channel.edit(name=new_name)
        
        embed = discord.Embed(
            description=f'✅ Ticket renamed from `{old_name}` to `{new_name}`',
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
        
        await self.log_ticket_action(ctx.guild, f'Ticket #{ticket["ticket_num"]} renamed to {new_name} by {ctx.author}', ctx.channel)
    
    @commands.command(name='transfer')
    async def transfer_ticket(self, ctx, member: discord.Member):
        """Transfer ticket to another middleman"""
        if ctx.channel.id not in self.tickets:
            await ctx.send('❌ This command can only be used in ticket channels!')
            return
        
        # Check if user has support role
        if not self.has_support_role(ctx.author):
            await ctx.send('❌ You need the Middleman role to transfer tickets!')
            return
        
        # Check if target has support role
        if not self.has_support_role(member):
            await ctx.send('❌ You can only transfer to another middleman!')
            return
        
        ticket = self.tickets[ctx.channel.id]
        
        # Transfer the ticket
        ticket['claimed_by'] = member.id
        ticket['status'] = 'claimed'
        
        embed = discord.Embed(
            title='🔄 Ticket Transferred',
            description=f'Ticket transferred to {member.mention} by {ctx.author.mention}',
            color=discord.Color.purple(),
            timestamp=datetime.now(timezone.utc)
        )
        
        await ctx.send(embed=embed)
        await self.log_ticket_action(ctx.guild, f'Ticket #{ticket["ticket_num"]} transferred from {ctx.author} to {member}', ctx.channel)
    
    @commands.command(name='close')
    async def close_command(self, ctx):
        """Close the current ticket (Middleman Team only)"""
        if ctx.channel.id not in self.tickets:
            await ctx.send('❌ This command can only be used in ticket channels!')
            return
        
        # Check if user has support role
        if not self.has_support_role(ctx.author):
            await ctx.send('❌ You need the Middleman role to close tickets!')
            return
        
        await self.close_ticket(ctx.channel, ctx.author, ctx.guild)
    
    @commands.command(name='ticketpanel')
    @commands.has_permissions(administrator=True)
    async def create_ticket_panel(self, ctx):
        """Create the ticket panel with Create Ticket button"""
        embed = discord.Embed(
            title='🎫 Middleman Ticket System',
            description=(
                'Welcome to the Middleman Ticket System!\n\n'
                'Click the button below to create a new ticket.\n'
                'Our team will assist you with your trade.'
            ),
            color=discord.Color.blue()
        )
        embed.add_field(
            name='How it works',
            value=(
                '1. Click "Create Ticket" button\n'
                '2. Fill out the form\n'
                '3. Wait for a middleman to claim your ticket\n'
                '4. Complete your trade safely'
            ),
            inline=False
        )
        
        view = TicketPanelView(self)
        await ctx.send(embed=embed, view=view)
    
    @commands.command(name='setticketcategory')
    @commands.has_permissions(administrator=True)
    async def set_ticket_category(self, ctx, category: discord.CategoryChannel):
        """Set the category for ticket channels"""
        self.config['category_id'] = category.id
        await ctx.send(f'✅ Ticket category set to {category.name}')
    
    @commands.command(name='setsupportrole')
    @commands.has_permissions(administrator=True)
    async def set_support_role(self, ctx, role: discord.Role):
        """Set the support/middleman role"""
        self.config['support_role_id'] = role.id
        await ctx.send(f'✅ Support role set to {role.name}')
    
    @commands.command(name='setlogchannel')
    @commands.has_permissions(administrator=True)
    async def set_log_channel(self, ctx, channel: discord.TextChannel):
        """Set the log channel for ticket actions"""
        self.config['log_channel_id'] = channel.id
        await ctx.send(f'✅ Log channel set to {channel.mention}')

async def setup(bot):
    await bot.add_cog(TicketSystem(bot))
