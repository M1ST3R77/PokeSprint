from src.Class.Server import Server

def set_channel(server: Server, channel_id: int):
    return server.database.query("UPDATE server SET channel_notification_id = %s WHERE discord_id = %s", (channel_id, server.guild_id))