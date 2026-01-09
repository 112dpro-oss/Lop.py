import discord
from discord.ext import commands
from discord import app_commands
import requests
import os
import json

# ================= CONFIG =================
TOKEN = os.getenv("TOKEN")  # Discord Bot Token
API_BASE = "https://app-py-jcwg.onrender.com"
SECRET_KEY = "RBX-Discord-Private-KEY-2026!x9"
ROBLOX_USER_API = "https://users.roblox.com/v1/usernames/users"
BAN_FILE = "bans.json"  # ملف حفظ الباندات

# ================= BOT SETUP =================
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

# ================= HELPERS =================
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

def load_bans():
    try:
        with open(BAN_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_bans(bans):
    with open(BAN_FILE, "w", encoding="utf-8") as f:
        json.dump(bans, f, indent=4, ensure_ascii=False)

# ================= BAN PLAYER =================
@bot.tree.command(name="ban-player", description="Ban a Roblox player.")
@app_commands.guild_only()
@app_commands.describe(
    username="Roblox username",
    reason="Reason for the ban",
    evidence="Evidence of the ban"
)
async def ban_player(
    interaction: discord.Interaction,
    username: str,
    reason: str,
    evidence: str
):
    await interaction.response.defer()

    if not username or not reason or not evidence:
        await interaction.followup.send("You must provide username, reason, and evidence.", ephemeral=True)
        return

    try:
        user_id = get_user_id(username)
        if not user_id:
            await interaction.followup.send("Roblox user not found.", ephemeral=True)
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

        # ================= حفظ الباند محليًا =================
        bans = load_bans()
        bans[str(user_id)] = {
            "username": username,
            "reason": reason,
            "evidence": evidence,
            "staff": str(interaction.user)
        }
        save_bans(bans)
        # ====================================================

        await interaction.followup.send(f"Banned {username} ({user_id}) for {reason}.")

    except Exception as e:
        await interaction.followup.send(f"Ban Failed Please wait until the bot servers are fully online. This may take a few seconds.", ephemeral=True)

# ================= UNBAN PLAYER =================
@bot.tree.command(name="unban-player", description="Unban a Roblox player.")
@app_commands.guild_only()
@app_commands.describe(
    username="Roblox username to unban",
    reason="Reason for unban"
)
async def unban_player(
    interaction: discord.Interaction,
    username: str,
    reason: str
):
    await interaction.response.defer()

    if not username or not reason:
        await interaction.followup.send("You must provide username and reason for unban.", ephemeral=True)
        return

    try:
        user_id = get_user_id(username)
        if not user_id:
            await interaction.followup.send("Roblox user not found.", ephemeral=True)
            return

        payload = {"key": SECRET_KEY, "username": username, "reason": reason}

        r = requests.delete(f"{API_BASE}/bans", json=payload, timeout=10)
        r.raise_for_status()

        # ================= إزالة الباند محليًا =================
        bans = load_bans()
        if str(user_id) in bans:
            bans.pop(str(user_id))
            save_bans(bans)
        # ====================================================

        await interaction.followup.send(f"Unbanned {username} ({user_id}) for {reason}.")

    except Exception as e:
        await interaction.followup.send(f"Unban Failed Please wait until the bot servers are fully online. This may take a few seconds.", ephemeral=True)

# ================= BAN INFO =================
@bot.tree.command(name="ban-info", description="Show game ban info.")
@app_commands.guild_only()
@app_commands.describe(username="Roblox username")
async def ban_info(interaction: discord.Interaction, username: str):
    await interaction.response.defer(ephemeral=True)

    try:
        user_id = get_user_id(username)
        if not user_id:
            await interaction.followup.send("Roblox user not found.")
            return

        r = requests.get(f"{API_BASE}/bans", timeout=10)
        r.raise_for_status()
        bans_api = r.json()

        # البحث في API القديم
        ban_data = None
        if username in bans_api:
            ban_data = bans_api[username]
        else:
            for b in bans_api.values():
                if str(b.get("userId")) == str(user_id):
                    ban_data = b
                    break

        # ================= البحث في الملف المحلي =================
        bans_local = load_bans()
        ban_local = bans_local.get(str(user_id))

        if ban_local:
            ban_data = ban_local

        if not ban_data:
            await interaction.followup.send(f"{username} is not banned in the game.")
            return

        await interaction.followup.send(
            f"GAME BAN INFO\n"
            f"Player: {ban_data.get('username', username)}\n"
            f"Reason: {ban_data.get('reason', 'N/A')}\n"
            f"Evidence: {ban_data.get('evidence', 'N/A')}\n"
            f"Staff: {ban_data.get('staff', 'Unknown')}"
        )

    except Exception as e:
        print("BAN INFO ERROR:", e)
        await interaction.followup.send("Failed to fetch game ban info.")

# ================= RUN BOT =================
if not TOKEN:
    raise ValueError("TOKEN is not set")

bot.run(TOKEN)
