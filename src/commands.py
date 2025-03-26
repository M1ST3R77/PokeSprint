from src.cmd.trailer import get_trailer

def setup_commands(bot):
    @bot.command()
    async def trailer(ctx):
        embed = get_trailer()
        await ctx.send(embed=embed)