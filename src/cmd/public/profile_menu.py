from src.Class.Server import Server
import discord

class PrevPageButton(discord.ui.Button):
    def __init__(self, view: "ProfileListView"):
        super().__init__(emoji="⬅️", style=discord.ButtonStyle.grey, row=0)
        self.view_ref = view

    async def callback(self, interaction: discord.Interaction):
        self.view_ref.current_page -= 1
        if self.view_ref.current_page < 0:
            self.view_ref.current_page = len(self.view_ref.profiles) - 1
        await self.view_ref.update_view(interaction)


class NextPageButton(discord.ui.Button):
    def __init__(self, view: "ProfileListView"):
        super().__init__(emoji="➡️", style=discord.ButtonStyle.grey, row=0)
        self.view_ref = view

    async def callback(self, interaction: discord.Interaction):
        self.view_ref.current_page += 1
        if self.view_ref.current_page >= len(self.view_ref.profiles):
            self.view_ref.current_page = 0
        await self.view_ref.update_view(interaction)

class EditButton(discord.ui.Button):
    def __init__(self, server: Server, discord_id: int):
        super().__init__(emoji="📝", style=discord.ButtonStyle.blurple, row=0)
        self.server = server
        self.discord_id = discord_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(EditProfileModal(self.server, self.discord_id))


class DeleteButton(discord.ui.Button):
    def __init__(self, server: Server, discord_id: int):
        super().__init__(emoji="🗑️", style=discord.ButtonStyle.red, row=0)
        self.server = server
        self.discord_id = discord_id

    async def callback(self, interaction: discord.Interaction):
        confirm = await ask_for_confirmation(interaction, f"Supprimer le profil de <@{self.discord_id}> ?")
        if confirm:
            self.server.database.query(
                "DELETE FROM profil WHERE discord_id = %s AND server_id = %s",
                (self.discord_id, self.server.guild_id)
            )


class ConfirmView(discord.ui.View):
    def __init__(self, timeout=30):
        super().__init__(timeout=timeout)
        self.value: bool | None = None

    @discord.ui.button(label="Oui", style=discord.ButtonStyle.green, emoji="✅")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        self.stop()
        await interaction.response.edit_message(content="✅ Suppression effectuée.", view=None)

    @discord.ui.button(label="Non", style=discord.ButtonStyle.red, emoji="❌")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = False
        self.stop()
        await interaction.response.edit_message(content="❌ Action annulée.", view=None)

async def ask_for_confirmation(interaction: discord.Interaction, message: str) -> bool:
    view = ConfirmView()
    await interaction.response.send_message(message, view=view, ephemeral=True)
    await view.wait()
    return view.value is True


class ProfileListView(discord.ui.View):
    def __init__(self, server: Server, profiles: list[tuple[int, str]]):
        super().__init__(timeout=120)
        self.server = server
        self.profiles = profiles
        self.current_page = 0

        self.prev_button = PrevPageButton(self)
        self.edit_button = None
        self.delete_button = None
        self.next_button = NextPageButton(self)

        self.update_buttons()

    def update_buttons(self):
        self.clear_items()

        if not self.profiles:
            return

        discord_id, _ = self.profiles[self.current_page]

        self.add_item(self.prev_button)

        self.edit_button = EditButton(self.server, discord_id)
        self.add_item(self.edit_button)

        self.delete_button = DeleteButton(self.server, discord_id)
        self.add_item(self.delete_button)

        self.add_item(self.next_button)
    
    async def update_view(self, interaction: discord.Interaction):
        self.update_buttons()

        discord_id, username = self.profiles[self.current_page]
        user = interaction.client.get_user(discord_id) or await interaction.client.fetch_user(discord_id)
        avatar_url = user.avatar.url if user and user.avatar else user.default_avatar.url

        profile = self.server.database.query(
            "SELECT username, private_channel_id FROM profil WHERE discord_id = %s AND server_id = %s",
            (discord_id, self.server.guild_id), fetchone=True
        )
        if not profile:
            await interaction.response.edit_message(content="Profil introuvable.", embed=None, view=self)
            return

        username, private_channel_id = profile

        embed = discord.Embed(
            title=f"🎖️ Carte de Dresseur : {username} ({self.current_page + 1}/{len(self.profiles)})",
            color=discord.Color.dark_gray()
        )
        embed.set_thumbnail(url=avatar_url)
        embed.add_field(name="Nom", value=username, inline=False)
        embed.add_field(name="Salon privé", value=f"<#{private_channel_id}>" if private_channel_id else "Aucun", inline=False)
        embed.set_footer(text=f"ID: {discord_id}")

        await interaction.response.edit_message(embed=embed, view=self)
    
    async def get_current_embed(self, client: discord.Client) -> discord.Embed:
        if not self.profiles:
            return discord.Embed(title="Aucun profil", description="Aucun profil enregistré.", color=discord.Color.red())
        
        discord_id, username = self.profiles[self.current_page]
        user = client.get_user(discord_id) or await client.fetch_user(discord_id)
        avatar_url = user.avatar.url if user and user.avatar else user.default_avatar.url

        profile = self.server.database.query(
            "SELECT username, private_channel_id FROM profil WHERE discord_id = %s AND server_id = %s",
            (discord_id, self.server.guild_id), fetchone=True
        )
        if not profile:
            return discord.Embed(title="Profil introuvable", color=discord.Color.red())

        username, private_channel_id = profile

        embed = discord.Embed(
            title=f"🎖️ Carte de Dresseur : {username} ({self.current_page + 1}/{len(self.profiles)})",
            color=discord.Color.dark_gray()
        )
        embed.set_thumbnail(url=avatar_url)
        embed.add_field(name="Nom", value=username, inline=False)
        embed.add_field(name="Salon privé", value=f"<#{private_channel_id}>" if private_channel_id else "Aucun", inline=False)
        embed.set_footer(text=f"ID: {discord_id}")
        return embed


class AddProfileModal(discord.ui.Modal, title="Ajouter un profil"):
    discord_id = discord.ui.TextInput(label="ID Discord", placeholder="123456789012345678")
    username = discord.ui.TextInput(label="Nom d'utilisateur")
    channel_id = discord.ui.TextInput(label="ID salon privé", placeholder="123456789012345678")

    def __init__(self, server: Server):
        super().__init__()
        self.server = server

    async def on_submit(self, interaction: discord.Interaction):
        try:
            discord_id = int(self.discord_id.value)
            user = interaction.client.get_user(discord_id) or await interaction.client.fetch_user(discord_id)
        except Exception:
            await interaction.response.send_message("❌ Cet ID Discord ne correspond à aucun utilisateur.", ephemeral=True)
            return

        channel_id = self.channel_id.value.strip()
        if channel_id:
            try:
                channel_id = int(channel_id)
                channel = interaction.guild.get_channel(channel_id)
                if channel is None:
                    raise ValueError("Salon introuvable")
            except Exception:
                await interaction.response.send_message("❌ Salon privé invalide ou inexistant.", ephemeral=True)
                return
        else:
            channel_id = None

        ok = self.server.database.query("INSERT INTO profil (discord_id, username, private_channel_id, server_id) VALUES (%s, %s, %s, %s)", (int(self.discord_id.value), self.username.value, self.channel_id.value, int(self.server.guild_id)))
        msg = "✅ Profil ajouté." if ok else "❌ Erreur à l'ajout."
        await interaction.response.send_message(msg, ephemeral=True)

class EditProfileModal(discord.ui.Modal, title="Modifier un profil"):
    def __init__(self, server: Server, discord_id: int | None = None):
        super().__init__()
        self.server = server
        self.discord_id = discord_id

        if self.discord_id is None:
            self.profile_id = discord.ui.TextInput(
                label="ID du profil à modifier",
                placeholder="123456789012345678"
            )
            self.add_item(self.profile_id)
        
        self.username = discord.ui.TextInput(
            label="Nouveau nom (vide pour ne pas changer)", required=False
        )
        self.add_item(self.username)

        self.channel_id = discord.ui.TextInput(
            label="Nouveau salon (vide pour ne pas changer)",
            required=False,
            placeholder="123456789012345678"
        )
        self.add_item(self.channel_id)

    async def on_submit(self, interaction: discord.Interaction):
        pid = self.discord_id or int(self.profile_id.value.strip())

        exists = self.server.database.query(
            "SELECT 1 FROM profil WHERE discord_id = %s AND server_id = %s",
            (pid, self.server.guild_id),
            fetchone=True
        )

        if not exists:
            await interaction.response.send_message("❌ Aucun profil trouvé avec cet ID.", ephemeral=True)
            return
        
        fields = []
        values = []

        if self.username.value:
            fields.append("username = %s")
            values.append(self.username.value)
        if self.channel_id.value:
            try:
                cid = int(self.channel_id.value.strip())
                channel = interaction.guild.get_channel(cid)
                if channel is None:
                    raise ValueError("Salon introuvable")
                fields.append("private_channel_id = %s")
                values.append(cid)
            except Exception:
                await interaction.response.send_message("❌ Salon privé invalide ou inexistant.", ephemeral=True)
                return

            fields.append("private_channel_id = %s")
            values.append(self.channel_id.value)
        
        if not fields:
            await interaction.response.send_message("⚠️ Rien à modifier.", ephemeral=True)
            return
        
        values.append(pid)
        values.append(self.server.guild_id)

        query = f"UPDATE profil SET {', '.join(fields)} WHERE discord_id = %s AND server_id = %s"
        ok = self.server.database.query(query, tuple(values))

        msg = "✅ Profil mis à jour." if ok else "❌ Erreur durant la mise à jour."
        await interaction.response.send_message(msg, ephemeral=True)


class DeleteProfileModal(discord.ui.Modal, title="Supprimer un profil"):
    def __init__(self, server: Server, discord_id: int | None = None):
        super().__init__()
        self.server = server
        self.discord_id = discord_id

        if self.discord_id is None:
            self.profile_id = discord.ui.TextInput(
                label="ID du profil à supprimer",
                placeholder="123456789012345678"
            )
            self.add_item(self.profile_id)

    async def on_submit(self, interaction: discord.Interaction):
        pid = self.discord_id or int(self.profile_id.value.strip())

        exists = self.server.database.query(
            "SELECT 1 FROM profil WHERE discord_id = %s AND server_id = %s",
            (pid, self.server.guild_id),
            fetchone=True
        )

        if not exists:
            await interaction.response.send_message("❌ Aucun profil trouvé avec cet ID.", ephemeral=True)
            return

        ok = self.server.database.query(
            "DELETE FROM profil WHERE discord_id = %s AND server_id = %s",
            (int(self.profile_id.value), self.server.guild_id)
        )
        msg = "✅ Profil supprimé." if ok else "❌ Erreur à la suppression."
        await interaction.response.send_message(msg, ephemeral=True)


class ProfileMenu(discord.ui.View):
    def __init__(self, server: Server):
        super().__init__(timeout=120)
        self.server = server
    
    @discord.ui.button(label="Lister", style=discord.ButtonStyle.blurple)
    async def list_profiles(self, interaction: discord.Interaction, button: discord.ui.Button):
        rows = self.server.database.query("SELECT discord_id, username FROM profil WHERE server_id = %s", (self.server.guild_id,), fetchall=True)
        if not rows:
            await interaction.response.send_message("Aucun profil enregistré.", ephemeral=True)
            return
        
        view = ProfileListView(self.server, rows)
        embed = await view.get_current_embed(interaction.client)

        await interaction.response.send_message(embed=embed, view=view)

    @discord.ui.button(label="Ajouter", style=discord.ButtonStyle.green)
    async def add_profile(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = AddProfileModal(self.server)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Modifier", style=discord.ButtonStyle.gray)
    async def edit_profile(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = EditProfileModal(self.server)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Supprimer", style=discord.ButtonStyle.red)
    async def delete_profile(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = DeleteProfileModal(self.server)
        await interaction.response.send_modal(modal)