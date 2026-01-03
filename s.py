import discord
from discord.ext import commands
from discord import app_commands
import requests
import os

# ================= CONFIG =================
TOKEN = os.getenv("TOKEN")  # توكن البوت من Environment Variables
API_URL = "https://idea-canvas--112dpro.replit.app/bans"
SECRET_KEY = "RBX-Discord-Private-KEY-2026!x9"
ROBLOX_USER_API = "https://users.roblox.com/v1/usernames/users"

# ================= BOT SETUP =================
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Logged in as: {bot.user}")

# ================= BAN PLAYER =================
@bot.tree.command(
    name="ban-player",
    description="Ban a player from the Roblox game."
)
@app_commands.guild_only()
@app_commands.describe(
    username="Roblox username",
    reason="Reason for the ban",
    evidence="Evidence (optional)"
)
async def ban_player(
    interaction: discord.Interaction,
    username: str,
    reason: str,
    evidence: str = ""
):
    await interaction.response.defer()

    # الحصول على UserId من Roblox
    roblox_payload = {"usernames": [username], "excludeBannedUsers": False}
    try:
        roblox_response = requests.post(ROBLOX_USER_API, json=roblox_payload, timeout=10)
        roblox_response.raise_for_status()
    except Exception as e:
        await interaction.followup.send(f"❌ Failed to connect to Roblox: {e}", ephemeral=True)
        return

    data = roblox_response.json().get("data")
    if not data:
        await interaction.followup.send("❌ Roblox user not found.", ephemeral=True)
        return

    user_id = data[0]["id"]

    # إرسال البان إلى API
    payload = {
        "key": SECRET_KEY,
        "username": username,
        "userId": user_id,
        "reason": reason,
        "evidence": evidence,
        "staff": str(interaction.user)
    }

    try:
        r = requests.post(API_URL, json=payload, timeout=10)
        r.raise_for_status()
        await interaction.followup.send(f"✅ {username} has been banned permanently.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Failed to ban player: {e}", ephemeral=True)

# ================= UNBAN PLAYER =================
@bot.tree.command(
    name="unban-player",
    description="Remove a player from the Roblox ban list."
)
@app_commands.guild_only()
@app_commands.describe(
    username="Roblox username to unban"
)
async def unban_player(interaction: discord.Interaction, username: str):
    await interaction.response.defer()

    payload = {
        "key": SECRET_KEY,
        "username": username
    }

    try:
        r = requests.delete(API_URL, json=payload, timeout=10)
        r.raise_for_status()
        await interaction.followup.send(f"✅ {username} has been unbanned permanently.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Failed to unban player: {e}", ephemeral=True)

# ================= RUN BOT =================
if not TOKEN:
    raise ValueError("⚠️ TOKEN is not set in Environment Variables!")

bot.run(TOKEN)
