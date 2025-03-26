from discord.ext import commands
from src.commands import setup_commands
import discord

def create_bot():
    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix="!", intents=intents)

    setup_commands(bot)

    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user}")
    
    return bot