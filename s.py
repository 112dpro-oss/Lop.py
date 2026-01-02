import discord
from discord.ext import commands
from discord import app_commands
import requests

# ================= CONFIG =================

TOKEN = "MTQ1NjA5ODczNjI5NDg1ODc5Mw.GgEWcn.CT9K4S_XMWuJMTCg3Bseg98k5B724EGjaJRUyU"

API_URL = "https://idea-canvas--112dpro.replit.app/ban"
SECRET_KEY = "RBX-Discord-Private-KEY-2026!x9"

ROBLOX_USER_API = "https://users.roblox.com/v1/usernames/users"

# ================= BOT SETUP =================

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Logged in as: {bot.user}")

# ================= SLASH COMMAND =================

@bot.tree.command(
    name="ban-player",
    description="Ban a player from the Roblox game."
)
@app_commands.guild_only()  # ❌ يمنع العمل في الـ DM
@app_commands.describe(
    username="Roblox username",
    reason="Reason for the ban",
    evidence="Evidence (optional)"
)
async def ban_player(
    interaction: discord.Interaction,
    username: str,
    reason: str,
    evidence: str
):
    await interaction.response.defer()

    # ===== 1️⃣ Get Roblox UserId =====
    roblox_payload = {
        "usernames": [username],
        "excludeBannedUsers": False
    }

    roblox_response = requests.post(
        ROBLOX_USER_API,
        json=roblox_payload,
        timeout=10
    )

    if roblox_response.status_code != 200:
        await interaction.followup.send(
            "❌ Failed to connect to Roblox.",
            ephemeral=True
        )
        return

    data = roblox_response.json().get("data")
    if not data:
        await interaction.followup.send(
            "❌ Roblox user not found.",
            ephemeral=True
        )
        return

    user_id = data[0]["id"]

    # ===== 2️⃣ Send ban to your API =====
    payload = {
        "key": SECRET_KEY,
        "username": username,
        "userId": user_id,
        "reason": reason,
        "evidence": evidence,
        "staff": str(interaction.user)
    }

    r = requests.post(API_URL, json=payload, timeout=10)

    if r.status_code != 200:
        await interaction.followup.send(
            "❌ Failed to send the ban to the game.",
            ephemeral=True
        )
        return

    # ===== 3️⃣ Final message =====
    message = f"Banned {username} ({user_id}) for {reason}."

    await interaction.followup.send(message)

# ================= RUN =================
bot.run(TOKEN)
