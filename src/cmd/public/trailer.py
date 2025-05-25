import discord

class Trailer(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.pages = [self.page1, self.page2, self.page3]
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
        return embed, None
    
    def page2(self):
        embed = discord.Embed(title="🕵️ Deuxième indice", color=discord.Color.green())
        embed.set_image(url="attachment://second_hint.PNG")
        file = discord.File("data/second_hint.PNG", filename="second_hint.PNG")
        return embed, file
    
    def page3(self):
        embed = discord.Embed(
            title="🔊 Troisième indice",
            description="Écoutez l'audio ci-dessus",
            color=discord.Color.blue()
        )
        file = discord.File("data/third_hint.ogg", filename="third_hint.ogg")
        return embed, file

    async def update_page(self, interaction: discord.Interaction):
        embed, file = self.pages[self.current]()
        await interaction.response.edit_message(
            embed=embed,
            view=self,
            attachments=[file] if file else []
        )
    
    @discord.ui.button(label="⬅️ Précédent", style=discord.ButtonStyle.gray)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current = (self.current - 1) % len(self.pages)
        await self.update_page(interaction)
    
    @discord.ui.button(label="➡️ Suivant", style=discord.ButtonStyle.gray)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current = (self.current + 1) % len(self.pages)
        await self.update_page(interaction)
