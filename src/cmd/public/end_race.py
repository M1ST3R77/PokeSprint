from src.Class.Server import Server
from discord.ext import commands
from datetime import datetime
import pytz

async def end_race(ctx: commands.Context, server: Server, race_name: str):
    race = server.database.query("SELECT id, status FROM race WHERE server_id = %s AND name = %s", (server.guild_id, race_name), fetchone=True)

    if not race:
        await ctx.send("❌ Cette race n'existe pas.")
        return
    
    race_id, status = race

    if status not in ("pause", "en_cours"):
        await ctx.send("🚫 Cette race n'est ni en cours ni en pause, elle ne peut pas être terminée.")
        return
    
    paris_tz = pytz.timezone('Europe/Paris')
    now = datetime.now(paris_tz)

    server.database.query("UPDATE race SET status = 'terminé', date_end = %s WHERE id = %s", (now, race_id),)

    await ctx.send(f"🏁 La race **{race_name}** est maintenant terminée.")