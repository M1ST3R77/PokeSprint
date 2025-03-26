import discord

def get_trailer():
    embed = discord.Embed(
        title="🎬 Le Duel Inachevé",
        description=(
            "❄️ **Décembre 2021**. Réalité et idéal s’affrontaient dans une course effrénée. Qui finirait vainqueur ?\n\n"
            "Mais cette histoire **ne s’est jamais vraiment terminée**.\n\n"
            "🔥 **2025**. L'affrontement reprend, régi par **l’aléa**, sous l’ombre grandissante du crépuscule.\n"
            "🌘 Une atmosphère rougeoyante à l’horizon, où les vents marins murmurent le retour d’un défi oublié…\n"
            "🏝️ *Un voyage, une course, un destin à sceller.*\n\n"
            "🏁 **Préparez-vous. L’inévitable approche.**"
        ),
        color=discord.Color.orange()
    )
    embed.set_footer(text="Qui deviendra le meilleur dresseur ? ⭐")
    return embed
