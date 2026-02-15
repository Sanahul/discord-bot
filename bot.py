import discord
from discord.ext import commands

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!')
        self.staff_users = []  # List to keep track of users who understood
        self.novice_users = []  # List to keep track of users who didn't understand

    async def setup_hook(self):
        self.add_command(self.mminfo)

    @commands.command()
    async def mminfo(self, ctx):
        embed = discord.Embed(title='Your Information', description='Please respond with one of the buttons below.', color=0x00ff00)
        embed.set_image(url='https://example.com/your-image.png')  # Update with actual image URL

        button1 = discord.ui.Button(label='Understand', style=discord.ButtonStyle.green)
        button2 = discord.ui.Button(label="Didn't Understand", style=discord.ButtonStyle.red)

        async def on_button1_click(interaction):
            self.staff_users.append(interaction.user.name)
            await interaction.response.send_message('Thank you for your feedback!', ephemeral=True)
            await self.update_embed(ctx)

        async def on_button2_click(interaction):
            self.novice_users.append(interaction.user.name)
            await interaction.response.send_message('Thank you for your feedback!', ephemeral=True)
            await self.update_embed(ctx)

        button1.callback = on_button1_click
        button2.callback = on_button2_click

        view = discord.ui.View()  
        view.add_item(button1)
        view.add_item(button2)
        await ctx.send(embed=embed, view=view)

    async def update_embed(self, ctx):
        embed = discord.Embed(title='Your Information', color=0x00ff00)
        embed.add_field(name='Users Who Understood:', value=', '.join(self.staff_users) if self.staff_users else 'None')
        embed.add_field(name='Users Who Didn\'t Understand:', value=', '.join(self.novice_users) if self.novice_users else 'None')
        await ctx.send(embed=embed)

intents = discord.Intents.default()
bot = MyBot()
bot.run('YOUR_TOKEN')  # Make sure to replace 'YOUR_TOKEN' with your actual bot token.