import discord
from discord.ext import commands
from discord.ui import Button, View
import os
import asyncio

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='$', intents=intents)

# ===== MMINFO VIEW =====
class MMInfoView(View):
    """Persistent view for mminfo command buttons"""
    
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="✅ Understood", style=discord.ButtonStyle.green, custom_id="mminfo_understood")
    async def understood_button(self, interaction: discord.Interaction, button: Button):
        """Handle understood button click"""
        await interaction.response.send_message(
            f"{interaction.user.mention} understood the middleman system"
        )
    
    @discord.ui.button(label="❌ Didn't Understand", style=discord.ButtonStyle.danger, custom_id="mminfo_not_understood")
    async def not_understood_button(self, interaction: discord.Interaction, button: Button):
        """Handle didn't understand button click"""
        await interaction.response.send_message(
            f"{interaction.user.mention} doesn't understand the middleman system"
        )

# ===== FEE VIEW =====
class FeeView(View):
    """View for fee command with payment option buttons"""
    
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="100%", style=discord.ButtonStyle.primary, custom_id="fee_100_percent")
    async def full_fee_button(self, interaction: discord.Interaction, button: Button):
        """Handle 100% fee button click"""
        # Disable all buttons
        for item in self.children:
            item.disabled = True
        
        # Update the message to disable buttons
        await interaction.message.edit(view=self)
        
        # Send public message
        await interaction.response.send_message(
            f"{interaction.user.mention} decided to pay 100% of the fee",
            ephemeral=False
        )
    
    @discord.ui.button(label="50% Each", style=discord.ButtonStyle.primary, custom_id="fee_50_percent")
    async def split_fee_button(self, interaction: discord.Interaction, button: Button):
        """Handle 50% each fee button click"""
        # Disable all buttons
        for item in self.children:
            item.disabled = True
        
        # Update the message to disable buttons
        await interaction.message.edit(view=self)
        
        # Send public message
        await interaction.response.send_message(
            f"{interaction.user.mention} decided to pay 50% each",
            ephemeral=False
        )

# ===== CONFIRM VIEW =====
class ConfirmView(View):
    """View for confirm command with restricted button access"""
    
    def __init__(self, user1_id: int, user2_id: int):
        super().__init__(timeout=300)  # 5 minutes timeout
        self.user1_id = user1_id
        self.user2_id = user2_id
        self.confirmed_users = set()
    
    def is_authorized_user(self, user_id: int) -> bool:
        """Check if user is authorized to interact with buttons"""
        return user_id in [self.user1_id, self.user2_id]
    
    @discord.ui.button(label="✅ Confirm", style=discord.ButtonStyle.green, custom_id="confirm_button")
    async def confirm_button(self, interaction: discord.Interaction, button: Button):
        """Handle confirm button click"""
        if not self.is_authorized_user(interaction.user.id):
            await interaction.response.send_message(
                "❌ Only the two users involved in the trade can interact with these buttons.",
                ephemeral=True
            )
            return
        
        self.confirmed_users.add(interaction.user.id)
        await interaction.response.send_message(
            f"✅ {interaction.user.mention} confirmed the trade.",
            ephemeral=False
        )
        
        # Check if both users confirmed
        if len(self.confirmed_users) == 2:
            # Disable all buttons
            for item in self.children:
                item.disabled = True
            
            # Update the message to disable buttons
            await interaction.message.edit(view=self)
            
            await interaction.followup.send(
                "🎉 Both users have confirmed the trade!",
                ephemeral=False
            )
    
    @discord.ui.button(label="❌ Decline", style=discord.ButtonStyle.danger, custom_id="decline_button")
    async def decline_button(self, interaction: discord.Interaction, button: Button):
        """Handle decline button click"""
        if not self.is_authorized_user(interaction.user.id):
            await interaction.response.send_message(
                "❌ Only the two users involved in the trade can interact with these buttons.",
                ephemeral=True
            )
            return
        
        # Disable all buttons
        for item in self.children:
            item.disabled = True
        
        # Update the message to disable buttons
        await interaction.message.edit(view=self)
        
        await interaction.response.send_message(
            f"❌ {interaction.user.mention} declined the trade. Trade cancelled.",
            ephemeral=False
        )

@bot.event
async def on_ready():
    print(f'✅ Bot is online as {bot.user}')
    await bot.change_presence(activity=discord.Game(name="$help | Middleman Tickets"))
    # Register persistent views
    bot.add_view(MMInfoView())
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
        embed.add_field(name="🆔 Server ID", value=guild.id, inline=True)
        embed.add_field(name="👑 Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
        embed.add_field(name="👥 Member Count", value=guild.member_count, inline=True)
        embed.add_field(name="📺 Channel Count", value=len(guild.channels), inline=True)
        embed.add_field(name="🎭 Role Count", value=len(guild.roles), inline=True)
        embed.add_field(name="📅 Creation Date", value=guild.created_at.strftime("%B %d, %Y"), inline=False)
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        print(f"Error in serverinfo command: {e}")  # Log server-side
        await ctx.send("❌ An error occurred while fetching server information. Please try again later.")

# ===== MMINFO COMMAND =====
@bot.command()
async def mminfo(ctx):
    """Display information about the Middleman system"""
    try:
        # Create embed with middleman information
        embed = discord.Embed(
            title="🎫 Middleman Information",
            description="A middleman is a trusted third party who facilitates trades between two users to ensure both parties are protected and the trade goes smoothly.",
            color=0xFFC0CB  # Pink color
        )
        
        # Add field: How it works
        embed.add_field(
            name="📋 How it Works",
            value=(
                "1️⃣ User creates a ticket using the Create Ticket button\n"
                "2️⃣ Fills out a form with trade details (other trader, what you're giving, what you're receiving)\n"
                "3️⃣ A middleman claims the ticket\n"
                "4️⃣ Both parties send items/currency to the middleman\n"
                "5️⃣ Middleman verifies both sides and completes the trade\n"
                "6️⃣ Ticket is closed"
            ),
            inline=False
        )
        
        # Add field: Benefits
        embed.add_field(
            name="✨ Benefits",
            value=(
                "• Protection against scams\n"
                "• Fair and transparent trades\n"
                "• Secure item/currency holding\n"
                "• Dispute resolution support"
            ),
            inline=False
        )
        
        # Add field: Getting Started
        embed.add_field(
            name="🚀 Getting Started",
            value="To create a ticket, look for the ticket panel and click the **Create Ticket** button. Fill out the form with your trade details and a middleman will assist you!",
            inline=False
        )
        
        await ctx.send(embed=embed, view=MMInfoView())
        
    except Exception as e:
        print(f"Error in mminfo command: {e}")  # Log server-side
        await ctx.send("❌ An error occurred while fetching middleman information. Please try again later.")

# ===== FEE COMMAND =====
@bot.command()
async def fee(ctx):
    """Display fee information with payment options"""
    try:
        # First embed
        embed1 = discord.Embed(
            title="MM FEE",
            description=(
                "Thank You For Using Our services\n"
                "Your items are currently being held for the time being.\n\n"
                "To proceed with the trade, please make the necessary donations that the MM deserves. We appreciate your cooperation."
            ),
            color=0xFFC0CB  # Pink color
        )
        
        # Second embed
        embed2 = discord.Embed(
            description=(
                "Please be patient while a MM will list a price\n"
                "Discuss with your trader about how you would want to do the Fee.\n\n"
                "Users are able to split the fee OR manage to pay the full fee if possible.\n"
                "(Once clicked, you can't redo)"
            ),
            color=0xFFC0CB  # Pink color
        )
        
        # Create view with buttons
        view = FeeView()
        
        # Send both embeds with buttons
        await ctx.send(embed=embed1)
        await ctx.send(embed=embed2, view=view)
        
    except Exception as e:
        print(f"Error in fee command: {e}")  # Log server-side
        await ctx.send("❌ An error occurred while displaying fee information. Please try again later.")

# ===== CONFIRM COMMAND =====
@bot.command()
async def confirm(ctx, user1: discord.Member, user2: discord.Member):
    """Create a trade confirmation request with two mentioned users"""
    try:
        # Check if users are the same
        if user1.id == user2.id:
            await ctx.send("❌ You cannot create a confirmation with the same user twice.")
            return
        
        # Create embed
        embed = discord.Embed(
            title="Confirmations",
            description="Do both users confirm the trade?\nPress Confirm if you agree.\nPress Decline if you don't confirm the trade.",
            color=0xFFC0CB  # Pink color
        )
        
        # Add field showing the two users involved
        embed.add_field(
            name="Users Involved",
            value=f"{user1.mention} and {user2.mention}",
            inline=False
        )
        
        # Create view with restricted access for the two users
        view = ConfirmView(user1.id, user2.id)
        
        # Send the embed with buttons
        await ctx.send(embed=embed, view=view)
        
    except Exception as e:
        print(f"Error in confirm command: {e}")  # Log server-side
        await ctx.send("❌ An error occurred while creating the confirmation. Please try again later.")

@confirm.error
async def confirm_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Usage: `$confirm @user1 @user2`")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ Member not found. Please mention a valid user.")

# ===== BAN COMMAND =====
@bot.command()
@commands.has_permissions(administrator=True)
async def ban(ctx, user: discord.Member, *, reason: str = "No reason provided"):
    """Ban a user from the server"""
    try:
        # Check if user is trying to ban themselves
        if user.id == ctx.author.id:
            await ctx.send("❌ You cannot ban yourself.")
            return
        
        # Check if user is trying to ban the bot
        if user.id == bot.user.id:
            await ctx.send("❌ You cannot ban the bot.")
            return
        
        # Check if the target user has higher or equal role than the command issuer (unless guild owner)
        if ctx.author.id != ctx.guild.owner_id and ctx.author.top_role <= user.top_role:
            await ctx.send("❌ You cannot ban a user with a role higher than or equal to yours.")
            return
        
        # Check if the bot has permission to ban this user
        if ctx.guild.me.top_role <= user.top_role:
            await ctx.send("❌ I cannot ban this user. My role is not high enough.")
            return
        
        # Ban the user
        await ctx.guild.ban(user, reason=reason)
        
        # Create embed with ban details
        embed = discord.Embed(
            title="User Banned",
            description=f"✅ {user.mention} has been successfully banned from the server.",
            color=0xFF0000  # Red color for danger
        )
        
        embed.add_field(name="Banned User", value=f"{user.mention} ({user})", inline=False)
        embed.add_field(name="Moderator", value=f"{ctx.author.mention} ({ctx.author})", inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Timestamp", value=discord.utils.format_dt(discord.utils.utcnow(), style='F'), inline=False)
        
        # Send embed
        await ctx.send(embed=embed)
        
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to ban this user. Make sure my role is higher than the user's role.")
    except discord.HTTPException:
        await ctx.send("❌ Failed to ban the user. They may already be banned.")
    except Exception as e:
        print(f"Error in ban command: {e}")  # Log server-side
        await ctx.send("❌ An error occurred while trying to ban the user. Please try again later.")

@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command. (Requires `Administrator`)")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Usage: `$ban @user [reason]`")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ Member not found. Please mention a valid user.")

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