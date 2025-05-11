from src.Class.Server import Server
from discord.ext import commands
from src.cmd.public.trailer import Trailer
from src.cmd.public.set_channel import set_channel
from src.cmd.admin.send_broadcast import send_broadcast

def setup_admin_commands(bot: commands.Bot):
    @bot.command()

    async def broadcast(ctx: commands.Context, message: str):
        server = Server(ctx.guild)
        if not server.is_admin():
            await ctx.send("❌ Ce serveur n'est pas administrateur.")
            return
        res = send_broadcast(server)
        if not res:
            await ctx.send("❌ Impossible de récupérer les serveurs non-admin.")
            return
        success, failure = 0, 0
        for (channel_id,) in res:
            channel = bot.get_channel(int(channel_id))
            if channel:
                try:
                    await channel.send(f"📢 **Annonce globale :**\n{message}")
                    success += 1
                except:
                    failure += 1
            else:
                failure += 1
        await ctx.send(f"✅ Message envoyé dans {success} serveurs. ❌ Échecs : {failure}")
    

def setup_commands(bot: commands.Bot):
    @bot.command()
    async def trailer(ctx: commands.Context):
        server = Server(ctx.guild)
        if server.is_admin():
            await ctx.send("❌ Ce serveur est administrateur.")
            return
        channel = bot.get_channel(int(server.get_notif()))
        if channel is None:
            await ctx.send("❌ Ce serveur n'est pas configuré pour recevoir des messages. Utilisez la commande `!setchannel <id_du_channel>`. Plus d'informations avec la commande `!help`")
            return
        view = Trailer()
        await channel.send(embed=view.pages[0], view=view)
    
    @bot.command()
    async def setchannel(ctx: commands.Context, channel_id: int):
        server = Server(ctx.guild)
        if server.is_admin():
            await ctx.send("❌ Ce serveur est administrateur.")
            return
        channel = bot.get_channel(channel_id)
        if not channel or channel.guild.id != ctx.guild.id:
            await ctx.send("❌ Ce channel n'existe pas ou n'est pas accessible.")
            return
        res = set_channel(server, channel_id)
        if not res:
            await ctx.send("❌ Ce channel n'a pas pu être sauvegardé.")
        else:
            await ctx.send(f"✅ Channel de notification enregistré : {channel.name}")
