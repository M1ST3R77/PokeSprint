from dotenv import load_dotenv
import os

env_file = ".env"
if os.path.exists(env_file):
    load_dotenv(env_file)

token = os.getenv("DISCORD_TOKEN")

from src.init_bot import create_bot

if token:
  bot = create_bot()
  bot.run(token)