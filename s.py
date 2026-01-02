import os
import discord
from discord.ext import commands
from discord import app_commands
import requests

# ================= CONFIG =================

TOKEN = os.getenv("TOKEN")  # ✅ من Render Environment Variables

API_URL = "https://idea-canvas--112dpro.replit.app/ban"
SECRET_KEY = "RBX-Discord-Private-KEY-2026!x9"

ROBLOX_USER_API = "https://users.roblox.com/v1/usernames/users"

# ================= BOT SETUP =================

intents = discord.Intents.default()
intents.message_content = True  # مهم لبعض الأوامر

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Bot is online as {bot.user}")

# ================= SLASH COMMAND ================

@bot.tree.command(
    name="ban-player",
    description="Ban a player from the Roblox game"
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
    evidence: str | None = None
):
    await interaction.response.defer(thinking=True)

    # ===== 1️⃣ Get Roblox UserId =====
    roblox_payload = {
        "usernames": [username],
        "excludeBannedUsers": False
    }

    try:
        roblox_response = requests.post(
            ROBLOX_USER_API,
            json=roblox_payload,
            timeout=10
        )
    except requests.exceptions.RequestException:
        await interaction.followup.send(
            "❌ Failed to connect to Roblox.",
            ephemeral=True
        )
        return

    if roblox_response.status_code != 200:
        await interaction.followup.send(
            "❌ Roblox API error.",
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
        "evidence": evidence or "None",
        "staff": str(interaction.user)
    }

    try:
        r = requests.post(API_URL, json=payload, timeout=10)
    except requests.exceptions.RequestException:
        await interaction.followup.send(
            "❌ Failed to send data to game server.",
            ephemeral=True
        )
        return

    if r.status_code != 200:
        await interaction.followup.send(
            "❌ Game server rejected the ban.",
            ephemeral=True
        )
        return

    # ===== 3️⃣ Success =====
    await interaction.followup.send(
        f"✅ **Banned Successfully**\n"
        f"👤 Roblox: `{username}`\n"
        f"🆔 UserId: `{user_id}`\n"
        f"📄 Reason: `{reason}`"
    )

# ================= RUN =================

if not TOKEN:
    raise RuntimeError("TOKEN environment variable not set")

bot.run(TOKEN)
