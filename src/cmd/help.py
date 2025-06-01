import discord

def get_help(type: str):
    if type == "public":
        embed = discord.Embed(
            title="📌 Aide - Commandes publiques",
            description="Voici les commandes disponibles pour tous les serveurs.",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="🎬 `!trailer`",
            value="Affiche les indices pour le prochain jeu.",
            inline=False
        )
        embed.add_field(
            name="📢 `!setchannel <id_du_channel>`",
            value="Définit le channel de notifications pour ce serveur.",
            inline=False
        )
        embed.add_field(
            name="📜 `!profiles`",
            value="Affiche la liste des utilisateurs participants aux races",
            inline=False
        )
        embed.add_field(
            name="🏁 `!races`",
            value="Affiche la liste des races",
            inline=False
        )
        embed.add_field(
            name="🚀 `!run <nom_de_la_race> <joueur1> <joueur2>...`",
            value="Lance une race en pause avec les joueurs donnés. Une seule race peut être en cours à la fois.",
            inline=False
        )
        embed.add_field(
            name="⏸️ `!pause <nom_de_la_race>`",
            value="Met en pause une race en cours.",
            inline=False
        )
        embed.add_field(
            name="🏁 `!end <nom_de_la_race>`",
            value="Termine une race (en cours ou en pause).",
            inline=False
        )
    elif type == "admin":
        embed = discord.Embed(
            title="🛠️ Aide - Commandes administrateur",
            description="Commandes réservées au serveur admin.",
            color=discord.Color.red()
        )
        embed.add_field(
            name="🌍 `!broadcast <message>`",
            value="Envoie un message global à tous les serveurs ayant un channel de notification défini.",
            inline=False
        )
    else:
        return
    return embed