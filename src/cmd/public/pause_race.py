from src.Class.Server import Server
from discord.ext import commands

async def pause_race(ctx: commands.Context, server: Server, race_name: str):
    race = server.database.query("SELECT id, status FROM race WHERE server_id = %s AND name = %s", (server.guild_id, race_name), fetchone=True)

    if not race:
        await ctx.send("❌ Cette race n'existe pas.")
        return
    
    race_id, status = race

    if status == "pause":
        await ctx.send("⏸️ Cette race est déjà en pause.")
        return
    
    if status == "terminé":
        server.database.query(
            "UPDATE race SET status = 'pause', date_end = NULL WHERE id = %s",
            (race_id,)
        )
        await ctx.send(f"🔄 La race **{race_name}** a été réouverte et mise en pause.")
        return

    if status == "en_cours":
        server.database.query("UPDATE race SET status = 'pause' WHERE id = %s", (race_id,),)
        await ctx.send(f"⏸️ La race **{race_name}** a été mise en pause.")
        return 