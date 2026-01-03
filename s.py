import discord
from discord.ext import commands
from discord import app_commands
import requests
import os

TOKEN = os.getenv("TOKEN")
BAN_API_URL = "https://idea-canvas--112dpro.replit.app/ban"
UNBAN_API_URL = "https://idea-canvas--112dpro.replit.app/unban"
BANS_LIST_URL = "https://idea-canvas--112dpro.replit.app/bans"
ROBLOX_USER_API = "https://users.roblox.com/v1/usernames/users"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Logged in as {bot.user}")

# ===== Utils =====
def get_roblox_user_id(username: str):
    r = requests.post(ROBLOX_USER_API, json={"usernames": [username], "excludeBannedUsers": False}, timeout=10)
    data = r.json().get("data")
    if not data:
        return None
    return data[0]["id"]

def get_current_bans():
    r = requests.get(BANS_LIST_URL, timeout=10)
    if r.status_code != 200:
        return {}
    return r.json()

# ===== /ban-player =====
@bot.tree.command(name="ban-player", description="Ban a Roblox player (once).")
@app_commands.describe(username="Roblox username", reason="Reason for ban")
async def ban_player(interaction: discord.Interaction, username: str, reason: str):
    await interaction.response.defer(ephemeral=True)
    user_id = get_roblox_user_id(username)
    if not user_id:
        await interaction.followup.send("❌ Roblox user not found.")
        return
    user_id_str = str(user_id)

    bans = get_current_bans()
    if user_id_str in bans:
        await interaction.followup.send(f"❌ Player {username} is already banned.\nReason: {bans[user_id_str]}")
        return

    r = requests.post(BAN_API_URL, json={"userId": user_id_str, "reason": reason}, timeout=10)
    if r.status_code != 200:
        await interaction.followup.send("❌ Failed to send ban.")
        return

    await interaction.followup.send(f"✅ Banned {username}\nReason: {reason}")

# ===== /unban-player =====
@bot.tree.command(name="unban-player", description="Unban a Roblox player.")
@app_commands.describe(username="Roblox username")
async def unban_player(interaction: discord.Interaction, username: str):
    await interaction.response.defer(ephemeral=True)
    user_id = get_roblox_user_id(username)
    if not user_id:
        await interaction.followup.send("❌ Roblox user not found.")
        return
    user_id_str = str(user_id)

    r = requests.post(UNBAN_API_URL, json={"userId": user_id_str}, timeout=10)
    if r.status_code != 200:
        await interaction.followup.send("❌ Failed to unban.")
        return

    await interaction.followup.send(f"✅ Unbanned {username}")

# ===== Run =====
if not TOKEN:
    raise RuntimeError("TOKEN environment variable not set")

bot.run(TOKEN)
