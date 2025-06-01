from src.Class.Server import Server
from discord.ext import commands

async def run_race(ctx: commands.Context, server: Server, race_name: str, *players: str):
    active_race = server.database.query("SELECT name FROM race WHERE server_id = %s AND status = 'en_cours'", (server.guild_id,), fetchone=True)

    if active_race:
        await ctx.send(f"🚫 Une race est déjà en cours : **{active_race[0]}**.")
        return
    
    race = server.database.query("SELECT id, status FROM race WHERE server_id = %s AND name = %s", (server.guild_id, race_name), fetchone=True)

    if not race:
        await ctx.send("❌ Cette race n'existe pas.")
        return
    
    race_id, status = race
    if status != "pause":
        await ctx.send("🚫 Cette race n'est pas en pause, elle ne peut pas être lancée.")
        return
    
    existing_players = server.database.query("SELECT COUNT(*) FROM race_ranking WHERE race_id = %s", (race_id,), fetchone=True)[0]

    if existing_players == 0:
        if not players:
            await ctx.send("❌ Aucun joueur fourni. Utilisation : `!run <nom_race> <joueur1> <joueur2>...`")
            return
        
        usernames = [p.strip() for p in players]
        placeholders = ', '.join(['%s'] * len(usernames))
        result = server.database.query(f"SELECT id, username FROM profil WHERE username IN ({placeholders}) AND server_id = %s", (*usernames, server.guild_id), fetchall=True)
        found_user_map = {username: profil_id for profil_id, username in result}
        found_usernames = set(found_user_map.keys())
        missing = set(usernames) - found_usernames

        if missing:
            await ctx.send(f"❌ Les joueurs suivants ne sont pas enregistrés pour jouer aux races : {', '.join(missing)}")
            return

        for username in usernames:
            profil_id = found_user_map[username]
            server.database.query("INSERT INTO race_ranking (race_id, player_name, position) VALUES (%s, %s, %s)", (race_id, username, 1))
            server.database.query("INSERT INTO profil_race (profil_id, race_id) VALUES (%s, %s)", (profil_id, race_id))
    
    server.database.query("UPDATE race SET status = 'en_cours' WHERE id = %s", (race_id,),)

    await ctx.send(f"✅ La race **{race_name}** a été lancée avec succès !")