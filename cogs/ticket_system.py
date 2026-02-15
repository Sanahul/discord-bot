import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View, Modal, TextInput
import json
import os
from datetime import datetime

# Configuration file path
CONFIG_FILE = 'ticket_config.json'

class TicketModal(Modal, title="Create a Ticket"):
    """Modal for ticket creation with 3 questions"""
    
    trader = TextInput(
        label="What is the other trader user?",
        placeholder="Enter the other trader's username or @mention",
        required=True,
        max_length=100
    )
    
    giving = TextInput(
        label="What are you giving?",
        placeholder="Describe what you're offering in the trade",
        required=True,
        style=discord.TextStyle.paragraph,
        max_length=500
    )
    
    receiving = TextInput(
        label="What is the other trader giving?",
        placeholder="Describe what you're receiving in the trade",
        required=True,
        style=discord.TextStyle.paragraph,
        max_length=500
    )
    
    def __init__(self, cog):
        super().__init__()
        self.cog = cog
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle ticket creation when modal is submitted"""
        await interaction.response.defer(ephemeral=True)
        
        # Create the ticket
        try:
            await self.cog.create_ticket(
                interaction,
                self.trader.value,
                self.giving.value,
                self.receiving.value
            )
        except Exception as e:
            await interaction.followup.send(f"❌ Error creating ticket: {str(e)}", ephemeral=True)

class TicketPanelView(View):
    """Persistent view for the ticket panel button"""
    
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog
    
    @discord.ui.button(
        label="Create Ticket",
        style=discord.ButtonStyle.green,
        custom_id="create_ticket_button",
        emoji="🎫"
    )
    async def create_ticket_button(self, interaction: discord.Interaction, button: Button):
        """Show modal when create ticket button is clicked"""
        modal = TicketModal(self.cog)
        await interaction.response.send_modal(modal)

class TicketManagementView(View):
    """View with Claim and Close buttons for ticket management"""
    
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog
    
    @discord.ui.button(
        label="Claim",
        style=discord.ButtonStyle.primary,
        custom_id="claim_ticket_button",
        emoji="✋"
    )
    async def claim_button(self, interaction: discord.Interaction, button: Button):
        """Handle claim button click"""
        await self.cog.handle_claim_button(interaction)
    
    @discord.ui.button(
        label="Close",
        style=discord.ButtonStyle.danger,
        custom_id="close_ticket_button",
        emoji="🔒"
    )
    async def close_button(self, interaction: discord.Interaction, button: Button):
        """Handle close button click"""
        await self.cog.handle_close_button(interaction)

class TicketSystem(commands.Cog):
    """Complete ticket system cog for middleman trading"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config = self.load_config()
        self.tickets = {}  # Store active tickets: {channel_id: ticket_data}
        self.ticket_counter = self.config.get('ticket_counter', 0)
    
    def load_config(self):
        """Load configuration from JSON file"""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        return {
            'support_role_id': None,
            'ticket_category_id': None,
            'log_channel_id': None,
            'ticket_counter': 0
        }
    
    def save_config(self):
        """Save configuration to JSON file"""
        self.config['ticket_counter'] = self.ticket_counter
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=4)
    
    async def cog_load(self):
        """Called when the cog is loaded"""
        # Add persistent views
        self.bot.add_view(TicketPanelView(self))
        self.bot.add_view(TicketManagementView(self))
        print("✅ Ticket system views registered")
    
    def get_support_role(self, guild):
        """Get the configured support role or auto-detect"""
        if self.config.get('support_role_id'):
            role = guild.get_role(self.config['support_role_id'])
            if role:
                return role
        
        # Auto-detect: look for roles containing "middleman" or "support"
        for role in guild.roles:
            if 'middleman' in role.name.lower() or 'support' in role.name.lower():
                return role
        
        return None
    
    def is_staff(self, member):
        """Check if member has staff role"""
        support_role = self.get_support_role(member.guild)
        if support_role and support_role in member.roles:
            return True
        return member.guild_permissions.administrator
    
    async def log_action(self, guild, message):
        """Log an action to the configured log channel"""
        if self.config.get('log_channel_id'):
            log_channel = guild.get_channel(self.config['log_channel_id'])
            if log_channel:
                embed = discord.Embed(
                    description=message,
                    color=discord.Color.blue(),
                    timestamp=datetime.utcnow()
                )
                await log_channel.send(embed=embed)
    
    # ===== ADMIN COMMANDS =====
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def ticketpanel(self, ctx):
        """Create the ticket panel with create ticket button"""
        # Embed 1 - Welcome/Header with image
        embed1 = discord.Embed(color=0xFFC0CB)  # Pink color
        embed1.set_image(url="https://cdn.discordapp.com/attachments/1466064818329882649/1472600743084167199/11223522fd5e54a39e3839fbb5dda945-1.jpg?ex=699329d0&is=6991d850&hm=4bb941c5b7d7e13a3e879947f9b6ce4b2ecadb4bc512b1edc14c4387697a071d&")
        
        # Embed 2 - Middleman rules and information
        embed2 = discord.Embed(
            title="**Middleman rules and information**",
            description=(
                "<:01apinkdot:1437864554750152764> at the moment, we do not MM account trades unless the other side is holdable (ex. pp for roblox). it is your responsibility to secure the account you receive. keep in mind we only have 1 account mm if the account needs to be held. \n"
                "<:01apinkdot:1437864554750152764> we can MM trades involving gift cards, as long as the other side of the trade is holdable! (example: adopt me for gift card)\n"
                "<:01apinkdot:1437864554750152764> we are not responsible for any items lost during or after the trade. (ex. if our account gets banned on roblox mid trade). make sure all the info you provide in the ticket is accurate. if it is incorrect and we send items to the wrong person, we are not responsible.\n"
                "<:01apinkdot:1437864554750152764> we do not handle conversions or exchanges. please complete any necessary exchanges before opening a ticket.\n"
                "<:01apinkdot:1437864554750152764> a tip is __REQUIRED__ for all risky trades.\n"
                "<:zzz:1439344035394359438><:01apinkline:1437864559057834055> the tip amount depends on the middleman and the trade value. a tip is non refundable, if you held your item/ received it, we still keep our tip even if the trade is canceled. \n"
                "<:01apinkdot:1437864554750152764> you must comply with the middleman and follow their TOS.\n"
                "<:01apinkdot:1437864554750152764> please understand the risks involved before you continue with a trade/ticket.\n"
                "<:01apinkdot:1437864554750152764> the middleman can decline any trade they're not comfortable with—please respect their decision and avoid arguing.\n"
                "<:01apinkdot:1437864554750152764> ghosting/scamming a trade is bannable (don't do it).\n"
                "<:01apinkdot:1437864554750152764> you cannot choose your middleman unless you need icyella herself. you can request a new mm if there are any issues i.e. fees, etc.\n"
                "<:zzz:1439344035394359438><:01apinkline:1437864559057834055> please keep in mind before opening a MM ticket for ella that she does require a 5% fee."
            ),
            color=0xFFC0CB  # Pink color
        )
        
        # Embed 3 - Additional information
        embed3 = discord.Embed(
            title="**additional information**",
            description=(
                "<:01apinkdot:1437864554750152764> if you're trading for cashapp make sure you both have adult cashapp accounts or minor cashapp accounts.\n"
                "cashapp will not let adults receive/send money to minors & vice versa.\n"
                "<:01apinkdot:1437864554750152764> if you have any questions or concerns regarding MMs, mmban, or ticket info please make a ticket in the HR section.\n"
                "<:01apinkdot:1437864554750152764> always remember just because someone has mod doesn't mean they are MM's, it is separate."
            ),
            color=0xFFC0CB  # Pink color
        )
        
        # Embed 4 - Need a trusted Middleman
        embed4 = discord.Embed(
            title="**need a trusted Middleman**",
            description=(
                "<:01apinkdot:1437864554750152764> open a ticket and complete the form, including the User ID of the person you are trading with.\n"
                "<:01apinkdot:1437864554750152764> only individuals with the MM role can serve as middlemen; be sure to check their limits beforehand.\n"
                "<:01apinkdot:1437864554750152764> __disclaimer:__ while we aim to respond to tickets as quickly as possible, please understand that we have other responsibilities."
            ),
            color=0xFFC0CB  # Pink color
        )
        
        view = TicketPanelView(self)
        await ctx.send(embed=embed1)
        await ctx.send(embed=embed2)
        await ctx.send(embed=embed3)
        await ctx.send(embed=embed4, view=view)
        await ctx.message.delete()
    
    @ticketpanel.error
    async def ticketpanel_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You need Administrator permission to use this command.")
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setsupportrole(self, ctx, role: discord.Role):
        """Set the support/middleman role"""
        self.config['support_role_id'] = role.id
        self.save_config()
        await ctx.send(f"✅ Support role set to {role.mention}")
    
    @setsupportrole.error
    async def setsupportrole_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You need Administrator permission to use this command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Usage: `$setsupportrole @role`")
        elif isinstance(error, commands.RoleNotFound):
            await ctx.send("❌ Role not found. Please mention a valid role.")
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setticketcategory(self, ctx, *, category_name: str):
        """Set the category for ticket channels"""
        category = discord.utils.get(ctx.guild.categories, name=category_name)
        if not category:
            await ctx.send(f"❌ Category '{category_name}' not found.")
            return
        
        self.config['ticket_category_id'] = category.id
        self.save_config()
        await ctx.send(f"✅ Ticket category set to **{category_name}**")
    
    @setticketcategory.error
    async def setticketcategory_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You need Administrator permission to use this command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Usage: `$setticketcategory CategoryName`")
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setlogchannel(self, ctx, channel: discord.TextChannel):
        """Set the log channel for ticket activities"""
        self.config['log_channel_id'] = channel.id
        self.save_config()
        await ctx.send(f"✅ Log channel set to {channel.mention}")
    
    @setlogchannel.error
    async def setlogchannel_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You need Administrator permission to use this command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Usage: `$setlogchannel #channel`")
        elif isinstance(error, commands.ChannelNotFound):
            await ctx.send("❌ Channel not found. Please mention a valid channel.")
    
    # ===== TICKET CREATION =====
    
    async def create_ticket(self, interaction, trader, giving, receiving):
        """Create a new ticket channel"""
        guild = interaction.guild
        user = interaction.user
        
        # Increment ticket counter
        self.ticket_counter += 1
        ticket_number = self.ticket_counter
        self.save_config()
        
        # Get category
        category = None
        if self.config.get('ticket_category_id'):
            category = guild.get_channel(self.config['ticket_category_id'])
        
        # Get support role
        support_role = self.get_support_role(guild)
        
        # Create channel with permissions
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(
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
                embed_links=True
            )
        
        # Create the ticket channel
        channel_name = f"ticket-{ticket_number}"
        channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites,
            topic=f"Ticket #{ticket_number} | Creator: {user.name}"
        )
        
        # Store ticket data
        self.tickets[channel.id] = {
            'number': ticket_number,
            'creator': user.id,
            'trader': trader,
            'giving': giving,
            'receiving': receiving,
            'claimed_by': None,
            'status': 'open',
            'created_at': datetime.utcnow().isoformat(),
            'renamed': False
        }
        
        # Create ticket info embed
        embed = discord.Embed(
            title=f"🎫 Ticket #{ticket_number}",
            description=f"Welcome {user.mention}! A middleman will be with you shortly.",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="📝 Other Trader", value=trader, inline=False)
        embed.add_field(name="📤 You're Giving", value=giving, inline=False)
        embed.add_field(name="📥 You're Receiving", value=receiving, inline=False)
        embed.add_field(name="📊 Status", value="🟢 Open", inline=True)
        embed.add_field(name="👤 Claimed By", value="None", inline=True)
        embed.set_footer(text=f"Created by {user.name}")
        
        # Send ticket info with management buttons
        view = TicketManagementView(self)
        mention_text = user.mention
        if support_role:
            mention_text += f" {support_role.mention}"
        
        await channel.send(mention_text)
        await channel.send(embed=embed, view=view)
        
        # Log the action
        await self.log_action(guild, f"🎫 Ticket #{ticket_number} created by {user.mention} in {channel.mention}")
        
        # Respond to user
        await interaction.followup.send(
            f"✅ Ticket created! {channel.mention}",
            ephemeral=True
        )
    
    # ===== USER COMMANDS =====
    
    @commands.command()
    async def add(self, ctx, member: discord.Member):
        """Add a user to the ticket"""
        if ctx.channel.id not in self.tickets:
            await ctx.send("❌ This command can only be used in ticket channels.")
            return
        
        ticket = self.tickets[ctx.channel.id]
        
        # Check if user is ticket creator or staff
        if ctx.author.id != ticket['creator'] and not self.is_staff(ctx.author):
            await ctx.send("❌ Only the ticket creator or staff can add users.")
            return
        
        # Add user to channel
        await ctx.channel.set_permissions(
            member,
            read_messages=True,
            send_messages=True,
            attach_files=True,
            embed_links=True
        )
        
        await ctx.send(f"✅ Added {member.mention} to the ticket.")
        await self.log_action(ctx.guild, f"➕ {member.mention} added to Ticket #{ticket['number']} by {ctx.author.mention}")
    
    @add.error
    async def add_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Usage: `$add @user`")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("❌ Member not found. Please mention a valid user.")
    
    @commands.command()
    async def remove(self, ctx, member: discord.Member):
        """Remove a user from the ticket"""
        if ctx.channel.id not in self.tickets:
            await ctx.send("❌ This command can only be used in ticket channels.")
            return
        
        ticket = self.tickets[ctx.channel.id]
        
        # Check if user is ticket creator or staff
        if ctx.author.id != ticket['creator'] and not self.is_staff(ctx.author):
            await ctx.send("❌ Only the ticket creator or staff can remove users.")
            return
        
        # Cannot remove ticket creator
        if member.id == ticket['creator']:
            await ctx.send("❌ Cannot remove the ticket creator.")
            return
        
        # Remove user from channel
        await ctx.channel.set_permissions(member, overwrite=None)
        
        await ctx.send(f"✅ Removed {member.mention} from the ticket.")
        await self.log_action(ctx.guild, f"➖ {member.mention} removed from Ticket #{ticket['number']} by {ctx.author.mention}")
    
    @remove.error
    async def remove_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Usage: `$remove @user`")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("❌ Member not found. Please mention a valid user.")
    
    @commands.command()
    async def renameticket(self, ctx, *, name: str):
        """Rename the ticket channel"""
        if ctx.channel.id not in self.tickets:
            await ctx.send("❌ This command can only be used in ticket channels.")
            return
        
        ticket = self.tickets[ctx.channel.id]
        
        # Check if user is ticket creator or staff
        if ctx.author.id != ticket['creator'] and not self.is_staff(ctx.author):
            await ctx.send("❌ Only the ticket creator or staff can rename tickets.")
            return
        
        # Rename channel
        old_name = ctx.channel.name
        await ctx.channel.edit(name=name)
        ticket['renamed'] = True
        
        await ctx.send(f"✅ Ticket renamed from **{old_name}** to **{name}**")
        await self.log_action(ctx.guild, f"✏️ Ticket #{ticket['number']} renamed from '{old_name}' to '{name}' by {ctx.author.mention}")
    
    @renameticket.error
    async def renameticket_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Usage: `$renameticket {name}`")
    
    # ===== STAFF COMMANDS =====
    
    @commands.command()
    async def claim(self, ctx):
        """Claim a ticket"""
        if ctx.channel.id not in self.tickets:
            await ctx.send("❌ This command can only be used in ticket channels.")
            return
        
        if not self.is_staff(ctx.author):
            await ctx.send("❌ You need the support role to claim tickets.")
            return
        
        ticket = self.tickets[ctx.channel.id]
        
        if ticket['claimed_by']:
            claimer = ctx.guild.get_member(ticket['claimed_by'])
            await ctx.send(f"❌ This ticket is already claimed by {claimer.mention if claimer else 'someone'}.")
            return
        
        # Claim the ticket
        ticket['claimed_by'] = ctx.author.id
        ticket['status'] = 'claimed'
        
        embed = discord.Embed(
            description=f"✋ {ctx.author.mention} has claimed this ticket!",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
        await self.log_action(ctx.guild, f"✋ Ticket #{ticket['number']} claimed by {ctx.author.mention}")
    
    @commands.command()
    async def unclaim(self, ctx):
        """Unclaim a ticket"""
        if ctx.channel.id not in self.tickets:
            await ctx.send("❌ This command can only be used in ticket channels.")
            return
        
        if not self.is_staff(ctx.author):
            await ctx.send("❌ You need the support role to unclaim tickets.")
            return
        
        ticket = self.tickets[ctx.channel.id]
        
        if not ticket['claimed_by']:
            await ctx.send("❌ This ticket is not claimed.")
            return
        
        if ticket['claimed_by'] != ctx.author.id and not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ You can only unclaim tickets that you have claimed.")
            return
        
        # Unclaim the ticket
        ticket['claimed_by'] = None
        ticket['status'] = 'open'
        
        embed = discord.Embed(
            description=f"🔓 {ctx.author.mention} has unclaimed this ticket.",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)
        await self.log_action(ctx.guild, f"🔓 Ticket #{ticket['number']} unclaimed by {ctx.author.mention}")
    
    @commands.command()
    async def transfer(self, ctx, member: discord.Member):
        """Transfer ticket to another middleman"""
        if ctx.channel.id not in self.tickets:
            await ctx.send("❌ This command can only be used in ticket channels.")
            return
        
        if not self.is_staff(ctx.author):
            await ctx.send("❌ You need the support role to transfer tickets.")
            return
        
        if not self.is_staff(member):
            await ctx.send("❌ You can only transfer tickets to other staff members.")
            return
        
        ticket = self.tickets[ctx.channel.id]
        
        # Transfer the ticket
        ticket['claimed_by'] = member.id
        ticket['status'] = 'claimed'
        
        embed = discord.Embed(
            description=f"🔄 Ticket transferred to {member.mention} by {ctx.author.mention}",
            color=discord.Color.purple()
        )
        await ctx.send(embed=embed)
        await self.log_action(ctx.guild, f"🔄 Ticket #{ticket['number']} transferred to {member.mention} by {ctx.author.mention}")
    
    @transfer.error
    async def transfer_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Usage: `$transfer @user`")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("❌ Member not found. Please mention a valid user.")
    
    @commands.command()
    async def close(self, ctx):
        """Close a ticket"""
        if ctx.channel.id not in self.tickets:
            await ctx.send("❌ This command can only be used in ticket channels.")
            return
        
        if not self.is_staff(ctx.author):
            await ctx.send("❌ You need the support role to close tickets.")
            return
        
        ticket = self.tickets[ctx.channel.id]
        
        # Close the ticket
        embed = discord.Embed(
            description=f"🔒 Ticket closed by {ctx.author.mention}\nChannel will be deleted in 5 seconds...",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        
        await self.log_action(ctx.guild, f"🔒 Ticket #{ticket['number']} closed by {ctx.author.mention}")
        
        # Delete ticket data and channel
        del self.tickets[ctx.channel.id]
        
        import asyncio
        await asyncio.sleep(5)
        await ctx.channel.delete()
    
    # ===== BUTTON HANDLERS =====
    
    async def handle_claim_button(self, interaction: discord.Interaction):
        """Handle the claim button click"""
        if interaction.channel.id not in self.tickets:
            await interaction.response.send_message("❌ This is not a valid ticket channel.", ephemeral=True)
            return
        
        if not self.is_staff(interaction.user):
            await interaction.response.send_message("❌ You need the support role to claim tickets.", ephemeral=True)
            return
        
        ticket = self.tickets[interaction.channel.id]
        
        if ticket['claimed_by']:
            claimer = interaction.guild.get_member(ticket['claimed_by'])
            await interaction.response.send_message(
                f"❌ This ticket is already claimed by {claimer.mention if claimer else 'someone'}.",
                ephemeral=True
            )
            return
        
        # Claim the ticket
        ticket['claimed_by'] = interaction.user.id
        ticket['status'] = 'claimed'
        
        embed = discord.Embed(
            description=f"✋ {interaction.user.mention} has claimed this ticket!",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed)
        await self.log_action(interaction.guild, f"✋ Ticket #{ticket['number']} claimed by {interaction.user.mention}")
    
    async def handle_close_button(self, interaction: discord.Interaction):
        """Handle the close button click"""
        if interaction.channel.id not in self.tickets:
            await interaction.response.send_message("❌ This is not a valid ticket channel.", ephemeral=True)
            return
        
        if not self.is_staff(interaction.user):
            await interaction.response.send_message("❌ You need the support role to close tickets.", ephemeral=True)
            return
        
        ticket = self.tickets[interaction.channel.id]
        
        # Close the ticket
        embed = discord.Embed(
            description=f"🔒 Ticket closed by {interaction.user.mention}\nChannel will be deleted in 5 seconds...",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)
        
        await self.log_action(interaction.guild, f"🔒 Ticket #{ticket['number']} closed by {interaction.user.mention}")
        
        # Delete ticket data and channel
        del self.tickets[interaction.channel.id]
        
        import asyncio
        await asyncio.sleep(5)
        await interaction.channel.delete()

async def setup(bot):
    await bot.add_cog(TicketSystem(bot))
