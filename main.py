import discord
from discord.ext import commands

class MatchmakingInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='mminfo')
    async def mminfo(self, ctx):
        embed = discord.Embed(
            title='Matchmaking Information',
            color=discord.Color.blue()
        )
        embed.add_field(name='Status', value='Currently matchmaking is underway.', inline=False)
        embed.add_field(name='Estimated Time', value='2-5 minutes', inline=False)
        embed.add_field(name='Players in Queue', value='42', inline=False)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(MatchmakingInfo(bot))
