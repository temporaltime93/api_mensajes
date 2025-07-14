from discord.ext import commands
import discord
from discord import SelectOption, ui, Interaction
import datetime
import os

# Lista de comandos registrados para el embed de ayuda
comandos_registrados = []

# Registrar comando para ayuda
def crear_comando(nombre, descripcion):
    comandos_registrados.append({
        "nombre": nombre,
        "descripcion": descripcion,
    })

# Función para crear embeds de respuesta
def embed(titulo, descripcion):
    e = discord.Embed(
        title=titulo,
        description=descripcion,
        color=13948116
    )
    e.set_image(url="https://raw.githubusercontent.com/1RubiUwU1/ChatPgx/refs/heads/main/Frame%2015%201.png")
    return e

CANAL_SALIDA_ID = 1380015764030881903

WEBHOOKS = {
    "RUBI_BOT": {
        "nombre": "RUBI_BOT",
        "canal_id": 1379157312073105450,
        "webhook_id": 1379160851432341695,
        "filtro": "desconocido"
    },
    "PROTOTYPE": {
        "nombre": "PROTOTYPE",
        "canal_id": 1379157312073105451,
        "webhook_id": 1379160851269025934,
        "filtro": "[no encontrado]"
    },
}

embeds_filtrados = {}

# --- Detectar texto prohibido en embed ---
def contiene_texto_prohibido(embed: discord.Embed, filtro: str):
    filtro = filtro.lower()
    def contiene(texto):
        return texto and filtro in texto.lower()

    if contiene(embed.title): return True
    if contiene(embed.description): return True
    for field in embed.fields:
        if contiene(field.name) or contiene(field.value):
            return True
    return False

# --- Vista de botones para elegir webhook ---
class SeleccionWebhookView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="RUBI_BOT", style=discord.ButtonStyle.primary, custom_id="btn_rubi")
    async def rubi_callback(self, interaction: Interaction, button: ui.Button):
        await interaction.response.defer()
        await iniciar_busqueda(interaction, "RUBI_BOT")

    @ui.button(label="PROTOTYPE", style=discord.ButtonStyle.success, custom_id="btn_prototype")  # ! Clave corregida
    async def prototype_callback(self, interaction: Interaction, button: ui.Button):
        await interaction.response.defer()
        await iniciar_busqueda(interaction, "PROTOTYPE")

# --- Menú desplegable para seleccionar un embed ---
class FiltroEmbedView(ui.View):
    def __init__(self, clave_webhook):
        super().__init__(timeout=None)
        self.clave_webhook = clave_webhook

    @discord.ui.select(
        placeholder="Selecciona un embed para mostrar",
        options=[],
        custom_id="select_embed_menu"
    )
    async def select_callback(self, interaction: Interaction, select: discord.ui.Select):
        index = int(select.values[0])
        clave = self.clave_webhook
        embed_data = embeds_filtrados[clave][index]

        embed = discord.Embed.from_dict(embed_data["embed"])
        await interaction.response.send_message(embed=embed)

# --- Buscar y mostrar embeds válidos ---
async def iniciar_busqueda(interaction: Interaction, clave_webhook: str):
    canal_salida = interaction.guild.get_channel(CANAL_SALIDA_ID)
    if not canal_salida:
        await interaction.followup.send("❌ No se encontró el canal de salida.")
        return

    config = WEBHOOKS[clave_webhook]
    canal_origen = interaction.guild.get_channel(config["canal_id"])
    if not canal_origen:
        await canal_salida.send(f"❌ No se encontró el canal origen para `{config['nombre']}`.")
        return

    await canal_salida.send(f"🔎 Buscando embeds de `{config['nombre']}`...")

    embeds = []
    async for message in canal_origen.history(limit=500):
        autor = message.author
        nombre_autor = autor.name if isinstance(autor, discord.User) else str(autor)

        if nombre_autor == config["nombre"] or message.webhook_id == config["webhook_id"]:
            for i, embed in enumerate(message.embeds):
                if contiene_texto_prohibido(embed, config["filtro"]):
                    continue
                embeds.append({
                    "embed": embed.to_dict(),
                    "timestamp": str(message.created_at),
                    "index": i
                })

    # * Guardar y limitar a 25 para evitar error de Discord
    embeds = embeds[:25]
    embeds_filtrados[clave_webhook] = embeds

    if not embeds:
        await canal_salida.send(f"🚫 No se encontraron embeds válidos de `{config['nombre']}`.")
        return

    view = FiltroEmbedView(clave_webhook)
    options = [
        SelectOption(label=f"Embed #{i+1}", value=str(i), description=f"Enviado el {data['timestamp'][:10]}")
        for i, data in enumerate(embeds)
    ]
    view.children[0].options = options

    await canal_salida.send(f"📌 Selecciona un embed de `{config['nombre']}`:", view=view)

# --- Setup principal ---
def setup(bot):
    crear_comando('!AYUDA', 'Muestra los comandos disponibles.')
    crear_comando('!ID', 'Muestra tu id de discord.')
    crear_comando("!LINK", "Muetra el link del servidor")

    @bot.command(name='borrar')
    @commands.has_permissions(manage_messages=True)
    async def borrar(ctx, cantidad: int):
        if cantidad < 1 or cantidad > 100:
            await ctx.send("❌ Número entre 1 y 100 por favor.")
            return
        await ctx.message.delete()
        borrados = await ctx.channel.purge(limit=cantidad)
        await ctx.send(embed=embed("🧹 BORRADO", f"Se borraron **{len(borrados)}** mensajes."), delete_after=5)

    @bot.command(name="id")
    async def id(ctx):
        user_id = ctx.author.id
        username = ctx.author.name
        await ctx.send(embed=embed("👤 Tu ID de usuario", f"Hola **{username}**, tu ID es: `{user_id}`"))

    @bot.command(name="link")
    async def link(ctx):
        await ctx.send(embed=embed("INVITACION", "INVITA A TUS AMIGOS A NUESTRO SERVIDOR: https://discord.gg/2qcRceCmtC"))

    @bot.command(name="buscar")
    async def buscar_embeds(ctx):
        canal_salida = ctx.guild.get_channel(CANAL_SALIDA_ID)
        if ctx.channel.id != CANAL_SALIDA_ID:
            await ctx.send(f"⚠️ Este comando solo puede usarse en <#{CANAL_SALIDA_ID}>")
            return
        view = SeleccionWebhookView()
        await canal_salida.send("📌 Selecciona de qué webhook quieres buscar embeds:", view=view)

    @bot.command(name='ayuda')
    async def ayuda(ctx):
        goku = ""
        for cmd in comandos_registrados:
            name = f"[2;30m[0m[2;35m[1;35m{cmd['nombre']}[0m[2;35m[0m"
            value = f"[2;30m[0m[2;35m[0m[2;37m{cmd['descripcion']}[0m"
            separa = "[2;30m[0m[2;30m[1;30m----------------------------------[0m[2;30m[0m"
            goku += separa+"\n" + name+"\n" + value +"\n"

        XDD = f"""```ansi
{goku}
```"""

        ayuda_embed = discord.Embed(
            title="📘 Comandos disponibles",
            description=XDD,
            color=13948116
        )

        ayuda_embed.set_image(
            url="https://raw.githubusercontent.com/1RubiUwU1/ChatPgx/refs/heads/main/Frame%2015%201.png"
        )

        await ctx.send(embed=ayuda_embed)

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ No tienes permiso para usar este comando.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Faltan argumentos para este comando.")
        elif isinstance(error, commands.CommandNotFound):
            pass  # Silenciar comandos desconocidos
        else:
            await ctx.send("❌ Ocurrió un error inesperado.")
            print("🧨 Error:", error)

    # --- Fix para evento de reacción ---
    @bot.event
    async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
        guild = bot.get_guild(payload.guild_id)
        if guild is None:
            return  # ! No se pudo obtener la guild

        # Obtener el miembro (puede no venir en payload, especialmente si no está cacheado)
        member = payload.member
        if member is None:
            try:
                member = await guild.fetch_member(payload.user_id)
            except discord.NotFound:
                return  # ! No se encontró al miembro
            except discord.HTTPException:
                return  # ! Error de conexión con Discord

        if member.bot:
            return  # * Ignorar reacciones de bots

        # Obtener canal y mensaje
        channel = guild.get_channel(payload.channel_id)
        if not channel:
            return  # ! No se encontró el canal

        try:
            message = await channel.fetch_message(payload.message_id)
        except discord.NotFound:
            return  # ! Mensaje eliminado o inexistente
        except discord.Forbidden:
            return  # ! Sin permisos para ver el mensaje
        except discord.HTTPException:
            return  # ! Otro error al obtener el mensaje

        emoji = payload.emoji.name

        # ? Aquí va la lógica personalizada para reaccionar
        # Por ejemplo:
        if emoji == "✅":
            await channel.send(f"✅ {member.mention} reaccionó al mensaje con ✅")
        elif emoji == "❌":
            await channel.send(f"❌ {member.display_name} canceló con ❌")

        # todo: Agrega aquí lógica de roles, votos, acciones personalizadas, etc.
