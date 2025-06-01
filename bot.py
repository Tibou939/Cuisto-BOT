import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} est prêt !")

# Chargement des extensions (cogs)
if __name__ == "__main__":
    for extension in ["cogs.points", "cogs.reglement"]:
        bot.load_extension(extension)

token = os.getenv("DISCORD_TOKEN")
bot.run(token)
