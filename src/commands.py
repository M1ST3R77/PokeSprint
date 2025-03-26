from discord.ext import commands
from src.cmd.trailer import get_trailer

def setup_commands(bot):
    @bot.command()
    async def ping(ctx):
        await ctx.send("pong")