import discord
from discord.ext import commands
from discord import app_commands
import requests
import os

# ================= CONFIG =================
TOKEN = os.getenv("TOKEN")
API_BASE = "https://app-py-jcwg.onrender.com"
SECRET_KEY = "RBX-Discord-Private-KEY-2026!x9"
ROBLOX_USER_API = "https://users.roblox.com/v1/usernames/users"

# ================= BOT SETUP =================
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Logged in as {bot.user}")

# ================= HELPER =================
def get_user_id(username: str):
    r = requests.post(
        ROBLOX_USER_API,
        json={"usernames": [username], "excludeBannedUsers": False},
        timeout=10
    )
    r.raise_for_status()
    data = r.json().get("data")
    if not data:
        return None
    return data[0]["id"]

# ================= BAN PLAYER =================
@bot.tree.command(name="ban-player", description="Ban a Roblox player")
@app_commands.guild_only()
async def ban_player(
    interaction: discord.Interaction,
    username: str,
    reason: str,
    evidence: str
):
    await interaction.response.defer()

    try:
        user_id = get_user_id(username)
        if not user_id:
            await interaction.followup.send("❌ Roblox user not found.", ephemeral=True)
            return

        payload = {
            "key": SECRET_KEY,
            "username": username,
            "userId": user_id,
            "reason": reason,
            "evidence": evidence,
            "staff": str(interaction.user)
        }

        r = requests.post(f"{API_BASE}/bans", json=payload, timeout=10)
        r.raise_for_status()

        await interaction.followup.send(
            f"Banned {username} ({user_id}) for {reason}."
        )

    except Exception as e:
        await interaction.followup.send(f"❌ Failed to ban: {e}", ephemeral=True)

# ================= UNBAN PLAYER =================
@bot.tree.command(name="unban-player", description="Unban a Roblox player")
@app_commands.guild_only()
async def unban_player(
    interaction: discord.Interaction,
    username: str,
    reason: str
):
    await interaction.response.defer()

    try:
        user_id = get_user_id(username)
        if not user_id:
            await interaction.followup.send("❌ Roblox user not found.", ephemeral=True)
            return

        payload = {
            "key": SECRET_KEY,
            "username": username,
            "reason": reason
        }

        r = requests.delete(f"{API_BASE}/bans", json=payload, timeout=10)
        r.raise_for_status()

        await interaction.followup.send(
            f"Unbanned {username} ({user_id}) for {reason}."
        )

    except Exception as e:
        await interaction.followup.send(f"❌ Failed to unban: {e}", ephemeral=True)

# ================= BAN INFO =================
@bot.tree.command(name="ban-info", description="Show ban reason & evidence")
@app_commands.guild_only()
async def ban_info(interaction: discord.Interaction, username: str):
    await interaction.response.defer()

    try:
        r = requests.get(f"{API_BASE}/bans", timeout=10)
        r.raise_for_status()
        bans = r.json()

        if username not in bans:
            await interaction.followup.send(
                f"⚠️ {username} is not banned.", ephemeral=True
            )
            return

        info = bans[username]
        reason = info.get("reason", "No reason")
        evidence = info.get("evidence", "No evidence")

        await interaction.followup.send(
            f"📄 **Ban info for {username}**\n"
            f"**Reason:** {reason}\n"
            f"**Evidence:** {evidence}"
        )

    except Exception as e:
        await interaction.followup.send(f"❌ Failed to fetch ban info: {e}", ephemeral=True)

# ================= RUN =================
if not TOKEN:
    raise ValueError("TOKEN not set")

bot.run(TOKEN)
