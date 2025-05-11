from src.Class.Server import Server

def send_broadcast(server: Server):
    return server.database.query("SELECT channel_notification_id FROM server WHERE channel_notification_id IS NOT NULL AND discord_id != %s", (server.guild_id,), fetchall=True)