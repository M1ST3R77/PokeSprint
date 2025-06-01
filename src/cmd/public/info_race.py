from src.Class.Server import Server
from discord.ext import commands

async def info_race(ctx: commands.Context, server: Server):
    user_discord_id = ctx.author.id
    current_channel_id = str(ctx.channel.id)

    result = server.database.query("SELECT id, private_channel_id, username FROM profil WHERE discord_id = %s AND server_id = %s", (user_discord_id, server.guild_id), fetchone=True)

    if not result:
        await ctx.send("❌ Profil non trouvé.")
        return
    
    profil_id, private_channel_id, username = result

    if current_channel_id != private_channel_id:
        await ctx.send("❌ Cette commande ne peut être utilisée que dans ton channel privé.")
        return
    
    result = server.database.query("SELECT r.id, r.name, r.game FROM race r INNER JOIN profil_race pr ON pr.race_id = r.id WHERE pr.profil_id = %s AND r.status = 'en_cours'", (profil_id,), fetchone=True)

    if not result:
        await ctx.send("❌ Tu ne participes à aucune race en cours.")
        return
    
    race_id, race_name, race_game = result

    result = server.database.query("SELECT milestone_position FROM race_ranking WHERE race_id = %s AND player_name = %s", (race_id, username), fetchone=True)

    current_milestone_pos = result[0]

    current_milestone = server.database.query("SELECT name FROM race_milestone WHERE race_id = %s AND position = %s", (race_id, current_milestone_pos), fetchone=True)

    current_milestone_name = current_milestone[0] if current_milestone else "Inconnu"

    next_milestone = server.database.query("SELECT name FROM race_milestone WHERE race_id = %s AND position = %s", (race_id, current_milestone_pos + 1), fetchone=True)

    next_milestone_name = next_milestone[0] if next_milestone else "Aucun, tu as atteint la fin ! 🎉"

    await ctx.send(
        f"🏁 Tu participes à la race **{race_name}** sur **{race_game}**.\n"
        f"🎯 Objectif actuel : **{current_milestone_name}**\n"
        f"➡️ Prochain objectif : **{next_milestone_name}**"
    )