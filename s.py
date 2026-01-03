import discord
from discord.ext import commands
from discord import app_commands
import requests
import os

# ================= CONFIG =================

TOKEN = os.getenv("TOKEN")

BAN_API_URL = "https://idea-canvas--112dpro.replit.app/ban"
UNBAN_API_URL = "https://idea-canvas--112dpro.replit.app/unban"
BANS_LIST_URL = "https://idea-canvas--112dpro.replit.app/bans"

ROBLOX_USER_API = "https://users.roblox.com/v1/usernames/users"

# ================= BOT SETUP =================

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Logged in as {bot.user}")

# ================= HELPERS =================

def get_roblox_user_id(username: str):
    payload = {
        "usernames": [username],
        "excludeBannedUsers": False
    }
    r = requests.post(ROBLOX_USER_API, json=payload, timeout=10)
    if r.status_code != 200:
        return None

    data = r.json().get("data")
    if not data:
        return None

    return data[0]["id"]

def get_all_bans():
    r = requests.get(BANS_LIST_URL, timeout=10)
    if r.status_code != 200:
        return {}
    return r.json()

# ================= /ban-player =================

@bot.tree.command(
    name="ban-player",
    description="Ban a Roblox player (one-time only)."
)
@app_commands.describe(
    username="Roblox username",
    reason="Reason for the ban"
)
async def ban_player(
    interaction: discord.Interaction,
    username: str,
    reason: str
):
    await interaction.response.defer(ephemeral=True)

    # 1️⃣ Get UserId
    user_id = get_roblox_user_id(username)
    if not user_id:
        await interaction.followup.send("❌ Roblox user not found.")
        return

    user_id_str = str(user_id)

    # 2️⃣ Check existing bans (URL = BanCheck)
    bans = get_all_bans()
    if user_id_str in bans:
        await interaction.followup.send(
            f"❌ Player **{username}** is already banned.\n"
            f"Reason: {bans[user_id_str]}"
        )
        return

    # 3️⃣ Send ban ONCE
    payload = {
        "userId": user_id_str,
        "reason": reason
    }

    r = requests.post(BAN_API_URL, json=payload, timeout=10)
    if r.status_code != 200:
        await interaction.followup.send("❌ Failed to send ban.")
        return

    await interaction.followup.send(
        f"✅ **Banned {username}**\n"
        f"🆔 UserId: {user_id}\n"
        f"📄 Reason: {reason}"
    )

# ================= /unban-player =================

@bot.tree.command(
    name="unban-player",
    description="Unban a Roblox player (remove ALL bans)."
)
@app_commands.describe(
    username="Roblox username"
)
async def unban_player(
    interaction: discord.Interaction,
    username: str
):
    await interaction.response.defer(ephemeral=True)

    # 1️⃣ Get UserId
    user_id = get_roblox_user_id(username)
    if not user_id:
        await interaction.followup.send("❌ Roblox user not found.")
        return

    user_id_str = str(user_id)

    # 2️⃣ Send UNBAN (removes all bans for this user)
    payload = {
        "userId": user_id_str
    }

    r = requests.post(UNBAN_API_URL, json=payload, timeout=10)
    if r.status_code != 200:
        await interaction.followup.send("❌ Failed to unban player.")
        return

    await interaction.followup.send(
        f"✅ **{username}** has been completely unbanned.\n"
        f"🧹 All bans removed."
    )

# ================= RUN =================

if not TOKEN:
    raise RuntimeError("❌ TOKEN environment variable is not set")

bot.run(TOKEN)
