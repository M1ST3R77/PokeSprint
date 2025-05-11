from dotenv import load_dotenv
from src.Class.Database import Database
import os
import discord

load_dotenv("../../")
ADMIN_SERVER_ID = int(os.getenv("DISCORD_SERVER_ADMIN_ID"))

class Server:
    def __init__(self, guild: discord.guild.Guild):
        self.database = Database()
        self.guild = guild
        self.guild_id = guild.id
        self.guild_name = guild.name
        self.is_admin_server = self.guild_id == ADMIN_SERVER_ID
    
    def add_server_to_db(self):
        res = self.database.query("SELECT * FROM server WHERE discord_id = %s", (self.guild_id,), fetchone=True)
        if not res:
            self.database.query("INSERT INTO server (discord_id, name) VALUES (%s, %s)", (self.guild_id, self.guild_name))

    def is_admin(self):
        return self.guild_id == ADMIN_SERVER_ID
    
    def get_notif(self):
        res = self.database.query("SELECT channel_notification_id FROM server WHERE discord_id = %s", (self.guild_id,), fetchone=True)
        if res:
            return res[0]
        else:
            return None