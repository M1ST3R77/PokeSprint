from src.Class.Server import Server
from discord.ext import commands
from src.cmd.public.trailer import Trailer
from src.cmd.public.profile_menu import ProfileMenu
from src.cmd.public.races_menu import RaceView
from src.cmd.public.set_channel import set_channel
from src.cmd.public.run_race import run_race
from src.cmd.public.pause_race import pause_race
from src.cmd.public.end_race import end_race
from src.cmd.public.info_race import info_race
from src.cmd.public.next_race import next_race
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
        embed, file = view.pages[0]()
        await ctx.send(embed=embed, file=file, view=view)
    
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
    
    @bot.command()
    async def profiles(ctx: commands.Context):
        server = Server(ctx.guild)
        if server.is_admin():
            await ctx.send("❌ Ce serveur est administrateur.")
            return
        view = ProfileMenu(server)
        await ctx.send("📋 **Gestion des profils**", view=view, ephemeral=True)
    
    @bot.command()
    async def races(ctx: commands.Context):
        server = Server(ctx.guild)
        if server.is_admin():
            await ctx.send("❌ Ce serveur est administrateur.")
            return
        view = RaceView(server)
        await ctx.send(embed=view.get_embed(), view=view)
    
    @bot.command()
    async def run(ctx: commands.Context, race_name: str, *players: str):
        server = Server(ctx.guild)
        if server.is_admin():
            await ctx.send("❌ Ce serveur est administrateur.")
            return
        await run_race(ctx, server, race_name, *players)
    
    @bot.command()
    async def pause(ctx: commands.Context, race_name: str):
        server = Server(ctx.guild)
        if server.is_admin():
            await ctx.send("❌ Ce serveur est administrateur.")
            return
        await pause_race(ctx, server, race_name)
    
    @bot.command()
    async def end(ctx: commands.Context, race_name: str):
        server = Server(ctx.guild)
        if server.is_admin():
            await ctx.send("❌ Ce serveur est administrateur.")
            return
        await end_race(ctx, server, race_name)
    
    @bot.command()
    async def info(ctx: commands.Context):
        server = Server(ctx.guild)
        if server.is_admin():
            await ctx.send("❌ Ce serveur est administrateur.")
            return
        await info_race(ctx, server)
    
    @bot.command()
    async def next(ctx: commands.Context):
        server = Server(ctx.guild)
        if server.is_admin():
            await ctx.send("❌ Ce serveur est administrateur.")
            return
        await next_race(bot, ctx, server)