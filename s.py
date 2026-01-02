import discord
from discord.ext import commands
from discord import app_commands
import requests

TOKEN = "MTQ1NjA5ODczNjI5NDg1ODc5Mw.GgEWcn.CT9K4S_XMWuJMTCg3Bseg98k5B724EGjaJRUyU"

API_URL = "https://idea-canvas--112dpro.replit.app/ban"
SECRET_KEY = "RBX-Discord-Private-KEY-2026!x9"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"تم تسجيل الدخول كبوت: {bot.user}")

# هذا الكوماند يظهر فقط في السيرفرات، ولن يظهر في الـ DM
@bot.tree.command(name="ban-player", description="Ban a player from the Roblox game.")
@app_commands.guild_only()  # يمنع ظهور الأمر في الديركت مسج
@app_commands.describe(
    username="The Roblox username of the player to ban",
    reason="The reason for the ban",
    evidence="The evidence for the ban"
)
async def ban_player(
    interaction: discord.Interaction,
    username: str,
    reason: str,
    evidence: str
):
    payload = {
        "key": SECRET_KEY,
        "username": username,
        "reason": reason
    }

    r = requests.post(API_URL, json=payload)

    if r.status_code != 200:
        await interaction.response.send_message(
            "Failed to send the ban to the game",
            ephemeral=True
        )
        return

    # هنا نعرض رسالة واحدة بدل Embed
    message = f"Banned {username} ({r.json().get('user_id', 'Unknown ID')}) for {reason}."

    await interaction.response.send_message(message)

bot.run(TOKEN)
