from src.Class.Server import Server
from discord.ext import commands
from discord.abc import GuildChannel, PrivateChannel
from discord.threads import Thread
from datetime import datetime
import pytz
import random
import asyncio

async def lancer_roulette(channel_notif: GuildChannel | Thread | PrivateChannel | None, ctx: commands.Context, server: Server, race_id: int, new_milestone_position: int, total_milestones: int):
    malus_rows = server.database.query("SELECT name FROM race_event WHERE race_id = %s AND is_positive = FALSE", (race_id,), fetchall=True)
    bonus_rows = server.database.query("SELECT name FROM race_event WHERE race_id = %s AND is_positive = TRUE", (race_id,), fetchall=True)
    
    roulette_malus = [row[0] for row in malus_rows] if malus_rows else []
    roulette_bonus = [row[0] for row in bonus_rows] if bonus_rows else []

    malus_obtenus = set()
    bonus_obtenus = set()
    relance_count = 0

    base_relance_chance = 0.10
    max_relance_chance = 0.25
    progress_ratio = new_milestone_position / (total_milestones - 1)
    relance_chance = base_relance_chance + (max_relance_chance - base_relance_chance) * progress_ratio

    first_pos = server.database.query("SELECT MAX(milestone_position) FROM race_ranking WHERE race_id = %s", (race_id,), fetchone=True)[0]
    dist_from_first = max(first_pos - new_milestone_position, 0)
    max_dist = max(first_pos, 1)
    progress_ratio = min(dist_from_first / max_dist, 1.0)
    base_bonus_chance = 0.20
    max_bonus_chance = 0.40
    if dist_from_first == 0:
        bonus_chance = base_bonus_chance
    else:
        bonus_chance = base_bonus_chance + (max_bonus_chance - base_bonus_chance) * progress_ratio

    while True:
        roulette_type = "malus"
        valeur_aleatoire = random.randint(0, 10) / 10
        if valeur_aleatoire < bonus_chance:
            roulette_type = "bonus"

        if roulette_type == "malus":
            malus_possibles = [m for m in roulette_malus if m not in malus_obtenus]
            if not malus_possibles:
                malus_possibles = roulette_malus
                malus_obtenus.clear()
            choix = random.choice(malus_possibles)
            malus_obtenus.add(choix)
        else:
            bonus_possibles = [m for m in roulette_bonus if m not in bonus_obtenus]
            if not bonus_possibles:
                bonus_possibles = roulette_bonus
                bonus_obtenus.clear()
            choix = random.choice(bonus_possibles)
            bonus_obtenus.add(choix)

        await channel_notif.send(f"🎡 Lancement de la roulette {roulette_type}...")
        animation_msg = await channel_notif.send("🎡 La roulette tourne...")

        for _ in range(5):
            random_spin = random.choice(malus_possibles if roulette_type == "malus" else bonus_possibles)
            await animation_msg.edit(content=f"🎡 La roulette tourne... {random_spin}")
            await asyncio.sleep(0.5)

        await animation_msg.edit(content=f"🎉 La roulette s'arrête sur : **{choix}** !")

        valeur_aleatoire = random.randint(0, 10) / 10
        if relance_count <= 3 and valeur_aleatoire < relance_chance:
            relance_count += 1
            await channel_notif.send("🔄 La roulette relance !")
            await asyncio.sleep(1)
            continue
        else:
            break

async def next_race(bot: commands.Bot, ctx: commands.Context, server: Server):
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
    
    race_id, race_name, _ = result

    result = server.database.query("SELECT id, position, milestone_position FROM race_ranking WHERE race_id = %s AND player_name = %s", (race_id, username), fetchone=True)

    ranking_id, _, milestone_position = result

    result = server.database.query("SELECT COUNT(*) FROM race_milestone WHERE race_id = %s", (race_id,), fetchone=True)
    total_milestones = result[0]

    if milestone_position >= total_milestones - 1:
        await ctx.send("✅ Tu as déjà atteint le dernier objectif.")
        return
    
    new_milestone_position = milestone_position + 1
    server.database.query("UPDATE race_ranking SET milestone_position = %s WHERE id = %s", (new_milestone_position, ranking_id))

    finished_count = server.database.query("SELECT COUNT(*) FROM race_ranking WHERE race_id = %s AND milestone_position = %s", (race_id, total_milestones - 1), fetchone=True)[0]

    rankings = server.database.query("SELECT player_name, milestone_position FROM race_ranking WHERE race_id = %s AND milestone_position < %s ORDER BY milestone_position DESC", (race_id, total_milestones - 1), fetchall=True)

    new_rankings = {}
    current_rank = finished_count + 1
    last_milestone = None

    result = server.database.query("SELECT channel_notification_id FROM server WHERE discord_id = %s", (server.guild_id,), fetchone=True)
    notification_channel_id = result[0]

    notification_channel = bot.get_channel(int(notification_channel_id))

    for idx, (player, milestone) in enumerate(rankings):
        if milestone != last_milestone:
            current_rank = finished_count + idx + 1
            last_milestone = milestone
        new_rankings[player] = current_rank
    
    for player, rank in new_rankings.items():
        server.database.query("UPDATE race_ranking SET position = %s WHERE race_id = %s AND player_name = %s", (rank, race_id, player))

    if new_milestone_position == total_milestones - 1:
        await notification_channel.send(f"🎉 {ctx.author.mention} a terminé la course **{race_name}** !")

        finished = server.database.query("SELECT COUNT(*) FROM race_ranking WHERE race_id = %s AND milestone_position = %s", (race_id, total_milestones - 1), fetchone=True)[0]

        total_players = server.database.query("SELECT COUNT(*) FROM race_ranking WHERE race_id = %s", (race_id,), fetchone=True)[0]

        if finished == total_players - 1:
            paris_tz = pytz.timezone('Europe/Paris')
            now = datetime.now(paris_tz)

            server.database.query("UPDATE race SET status = 'terminé', date_end = %s WHERE id = %s", (now, race_id),)

            await notification_channel.send("🏁 L'avant-dernier joueur vient de finir, la course est maintenant **terminée**. Le dernier joueur n'a pas terminé à temps.")

    else:
        milestones = server.database.query("SELECT position, name FROM race_milestone WHERE race_id = %s ORDER BY position ASC", (race_id,), fetchall=True)
        current_objective = next_objective = None
        for position, name in milestones:
            if position == new_milestone_position:
                current_objective = name
            elif position == new_milestone_position + 1:
                next_objective = name
        
        message = f"✅ Tu es passé à l'objectif **{new_milestone_position}** : **{current_objective}**."
        if next_objective:
            await lancer_roulette(notification_channel, ctx, server, race_id, new_milestone_position, total_milestones)
            message += f"\n🔜 Prochain objectif : **{next_objective}**."
        else:
            message += "\n🏁 Tu as atteint le dernier objectif !"

        await ctx.send(message)