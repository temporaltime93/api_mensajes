import discord
from discord.ext import commands

import os

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# todo: Cargar comandos externos desde comandos.py
import comandos_bot
comandos_bot.setup(bot)

bot.run(TOKEN)
