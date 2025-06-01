from src.Class.Server import Server
from datetime import datetime
import discord
import pytz

class ConfirmationView(discord.ui.View):
    def __init__(self, on_confirm, *, timeout=30):
        super().__init__(timeout=timeout)
        self.on_confirm = on_confirm

    @discord.ui.button(label="✅ Confirmer", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.on_confirm(interaction)
        self.stop()

    @discord.ui.button(label="❌ Annuler", style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("❎ Suppression annulée.", ephemeral=True)
        self.stop()

class RaceView(discord.ui.View):
    def __init__(self, server: Server):
        super().__init__(timeout=120)
        self.server = server
        self.server_id = server.guild_id
        self.current_index = 0

        query = server.database.query("SELECT id, name, game FROM race WHERE server_id = %s", (self.server_id,), fetchall=True)
        self.races = [{"id": r[0], "name": r[1], "game": r[2]} for r in query]
           
    def get_embed(self):
        if not self.races:
            return discord.Embed(title="Aucune race disponible", color=discord.Color.red())

        race = self.races[self.current_index]
        milestones = self.server.database.query(
            "SELECT name FROM race_milestone WHERE race_id = %s ORDER BY position ASC",
            (race['id'],), fetchall=True
        )
        positive_events = self.server.database.query(
            "SELECT name FROM race_event WHERE race_id = %s AND is_positive = TRUE",
            (race['id'],), fetchall=True
        )
        negative_events = self.server.database.query(
            "SELECT name FROM race_event WHERE race_id = %s AND is_positive = FALSE",
            (race['id'],), fetchall=True
        )
        result = self.server.database.query(
            "SELECT status, date_creation, date_end FROM race WHERE id = %s",
            (race['id'],), fetchone=True
        )
        status, created_at, finished_at = result

        embed = discord.Embed(title=f"Race : {race['name']}", color=discord.Color.blue())
        embed.add_field(name="Jeu", value=race['game'], inline=False)
        embed.add_field(name="Statut", value=status.replace('_', ' ').capitalize(), inline=True)
        embed.add_field(name="Créée le", value=created_at.strftime("%d/%m/%Y %H:%M"), inline=True)

        if status == "terminé" and finished_at:
            embed.add_field(name="Terminée le", value=finished_at.strftime("%d/%m/%Y %H:%M"), inline=True)

            ranking = self.server.database.query(
                "SELECT player_name, position FROM race_ranking WHERE race_id = %s ORDER BY position ASC",
                (race['id'],), fetchall=True
            )
            if ranking:
                classement_str = "\n".join(f"{pos}. {name}" for name, pos in ranking)
                embed.add_field(name="🏁 Classement", value=classement_str, inline=False)

        embed.add_field(name="Paliers", value="\n".join(m[0] for m in milestones) or "Aucun", inline=False)
        embed.add_field(name="✅ Événements positifs", value="\n".join(e[0] for e in positive_events) or "Aucun", inline=True)
        embed.add_field(name="❌ Événements négatifs", value="\n".join(e[0] for e in negative_events) or "Aucun", inline=True)
        embed.set_footer(text=f"Race {self.current_index + 1}/{len(self.races)}")
        return embed
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return True
    
    @discord.ui.button(label="⬅️ Précédent", style=discord.ButtonStyle.grey, custom_id="prev")
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.races:
            await interaction.response.send_message("Aucune race à afficher.", ephemeral=True)
            return
        self.current_index = (self.current_index - 1) % len(self.races)
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="Créer une Race", style=discord.ButtonStyle.green, custom_id="create")
    async def create(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CreateRaceModal(self.server, self, interaction))

    @discord.ui.button(label="Modifier", style=discord.ButtonStyle.blurple, custom_id="edit")
    async def edit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.races:
            await interaction.response.send_message("Aucune race à modifier.", ephemeral=True)
            return
        race = self.races[self.current_index]
        await interaction.response.send_modal(EditRaceModal(race, self.server, self, interaction))

    @discord.ui.button(label="Supprimer", style=discord.ButtonStyle.red, custom_id="delete")
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.races:
            await interaction.response.send_message("Aucune race à supprimer.", ephemeral=True)
            return

        race_name = self.races[self.current_index]["name"]

        async def confirm_deletion(interaction: discord.Interaction):
            race_id = self.races[self.current_index]['id']
            self.server.database.query("DELETE FROM race WHERE id = %s", (race_id,))
            del self.races[self.current_index]
            self.current_index = max(0, self.current_index - 1)
            await interaction.response.send_message(
                f"🗑️ La race **{race_name}** a bien été supprimée.", ephemeral=True
            )

        view = ConfirmationView(on_confirm=confirm_deletion)
        await interaction.response.send_message(
            f"⚠️ Es-tu sûr de vouloir supprimer la race **{race_name}** ?",
            view=view,
            ephemeral=True
        )

    @discord.ui.button(label="Suivant ➡️", style=discord.ButtonStyle.grey, custom_id="next")
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.races:
            await interaction.response.send_message("Aucune race à afficher.", ephemeral=True)
            return
        self.current_index = (self.current_index + 1) % len(self.races)
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

class CreateRaceModal(discord.ui.Modal):
    def __init__(self, server: Server, view: RaceView, interaction: discord.Interaction):
        super().__init__(title="Créer une nouvelle race")
        self.server = server
        self.view = view
        self.interaction = interaction

        self.add_item(discord.ui.TextInput(label="Nom de la race", placeholder="Nom", max_length=100))
        self.add_item(discord.ui.TextInput(label="Jeu", placeholder="Nom du jeu", max_length=100))
        self.add_item(discord.ui.TextInput(label="Paliers (1 par ligne)", placeholder="Obj 1\nObj 2\netc...", style=discord.TextStyle.paragraph))
        self.add_item(discord.ui.TextInput(label="Événements positifs (1 par ligne)", style=discord.TextStyle.paragraph))
        self.add_item(discord.ui.TextInput(label="Événements négatifs (1 par ligne)", style=discord.TextStyle.paragraph))

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        name = self.children[0].value
        game = self.children[1].value
        milestones = [x.strip() for x in self.children[2].value.strip().splitlines() if x.strip()]
        positive_events = [x.strip() for x in self.children[3].value.strip().splitlines() if x.strip()]
        negative_events = [x.strip() for x in self.children[4].value.strip().splitlines() if x.strip()]

        paris_tz = pytz.timezone('Europe/Paris')
        now = datetime.now(paris_tz)
        self.server.database.query(
            "INSERT INTO race (name, game, server_id, status, date_creation) VALUES (%s, %s, %s, %s, %s)",
            (name, game, self.server.guild_id, 'pause', now)
        )
        race_id = self.server.database.query("SELECT LAST_INSERT_ID()", fetchone=True)[0]

        for i, desc in enumerate(milestones):
            self.server.database.query("INSERT INTO race_milestone (race_id, name, position) VALUES (%s, %s, %s)", (race_id, desc, i))
        for desc in positive_events:
            self.server.database.query("INSERT INTO race_event (race_id, name, is_positive) VALUES (%s, %s, TRUE)", (race_id, desc))
        for desc in negative_events:
            self.server.database.query("INSERT INTO race_event (race_id, name, is_positive) VALUES (%s, %s, FALSE)", (race_id, desc))

        self.view.races.append({"id": race_id, "name": name, "game": game})
        await self.interaction.edit_original_response(embed=self.view.get_embed(), view=self.view)


class EditRaceModal(CreateRaceModal):
    def __init__(self, race: dict[str, any], server: Server, view: RaceView, interaction: discord.Interaction):
        super().__init__(server, view, interaction)
        self.race = race
        self.title = f"Modifier la race : {race['name']}"

        milestones = [x[0] for x in self.server.database.query(
            "SELECT name FROM race_milestone WHERE race_id = %s ORDER BY position ASC", (race['id'],), fetchall=True)]
        pos_events = [x[0] for x in self.server.database.query(
            "SELECT name FROM race_event WHERE race_id = %s AND is_positive = TRUE", (race['id'],), fetchall=True)]
        neg_events = [x[0] for x in self.server.database.query(
            "SELECT name FROM race_event WHERE race_id = %s AND is_positive = FALSE", (race['id'],), fetchall=True)]

        self.children[0].default = race['name']
        self.children[1].default = race['game']
        self.children[2].default = "\n".join(milestones)
        self.children[3].default = "\n".join(pos_events)
        self.children[4].default = "\n".join(neg_events)

        for child in self.children:
            child.required = False

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        race_id = self.race['id']

        name_input = self.children[0].value.strip()
        game_input = self.children[1].value.strip()
        milestones_input = self.children[2].value.strip()
        pos_events_input = self.children[3].value.strip()
        neg_events_input = self.children[4].value.strip()

        if name_input:
            self.server.database.query("UPDATE race SET name=%s WHERE id=%s", (name_input, race_id))
            self.race['name'] = name_input

        if game_input:
            self.server.database.query("UPDATE race SET game=%s WHERE id=%s", (game_input, race_id))
            self.race['game'] = game_input

        if milestones_input:
            milestones = [x.strip() for x in milestones_input.splitlines() if x.strip()]
            self.server.database.query("DELETE FROM race_milestone WHERE race_id=%s", (race_id,))
            for i, desc in enumerate(milestones):
                self.server.database.query(
                    "INSERT INTO race_milestone (race_id, name, position) VALUES (%s, %s, %s)",
                    (race_id, desc, i))

        if pos_events_input:
            positive_events = [x.strip() for x in pos_events_input.splitlines() if x.strip()]
            self.server.database.query("DELETE FROM race_event WHERE race_id=%s AND is_positive=TRUE", (race_id,))
            for desc in positive_events:
                self.server.database.query(
                    "INSERT INTO race_event (race_id, name, is_positive) VALUES (%s, %s, TRUE)",
                    (race_id, desc))

        if neg_events_input:
            negative_events = [x.strip() for x in neg_events_input.splitlines() if x.strip()]
            self.server.database.query("DELETE FROM race_event WHERE race_id=%s AND is_positive=FALSE", (race_id,))
            for desc in negative_events:
                self.server.database.query(
                    "INSERT INTO race_event (race_id, name, is_positive) VALUES (%s, %s, FALSE)",
                    (race_id, desc))

        await self.interaction.edit_original_response(embed=self.view.get_embed(), view=self.view)