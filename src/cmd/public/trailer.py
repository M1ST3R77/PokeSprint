from discord.ext import commands
import discord

class Trailer(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.pages = [self.page1(), self.page2()]
        self.current = 0
    
    def page1(self):
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
    
    def page2(self):
        embed = discord.Embed(color=discord.Color.green())
        embed.set_image(url="https://cdn.discordapp.com/attachments/1354532813659181317/1371206794935930951/second_hint.PNG?ex=68224b57&is=6820f9d7&hm=01b2518065d2bf924093fa9ef3f0dfa9635c6a165040af696c30f2ec1976176d&")
        embed.set_footer(text="Voici le deuxième indice 🕵️‍♂️")
        return embed
    
    @discord.ui.button(label="⬅️ Précédent", style=discord.ButtonStyle.gray)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current = (self.current - 1) % len(self.pages)
        await interaction.response.edit_message(embed=self.pages[self.current], view=self)
    
    @discord.ui.button(label="➡️ Suivant", style=discord.ButtonStyle.gray)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current = (self.current + 1) % len(self.pages)
        await interaction.response.edit_message(embed=self.pages[self.current], view=self)
