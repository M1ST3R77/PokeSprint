from discord.ext import commands
from src.commands import setup_commands, setup_admin_commands
from src.cmd.help import get_help
from src.Class.Server import Server
import discord

def create_bot():
    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

    @bot.command()
    async def help(ctx: commands.Context):
        server = Server(ctx.guild)
        embed = get_help("admin" if server.is_admin() else "public")
        await ctx.send(embed=embed)

    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user.name}")
        for guild in bot.guilds:
            server = Server(guild)
            server.add_server_to_db()
                
    setup_admin_commands(bot)
    setup_commands(bot)
    return bot