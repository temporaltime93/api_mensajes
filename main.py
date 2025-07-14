import discord
from discord.ext import commands
from discord import app_commands
import os

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# todo: Cargar comandos externos desde comandos.py
import comandos_bot
comandos_bot.setup(bot)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"✅ Comandos slash sincronizados ({len(synced)})")
    except Exception as e:
        print(f"❌ Error al sincronizar comandos slash: {e}")

bot.run(TOKEN)
