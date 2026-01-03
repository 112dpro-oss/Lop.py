from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

BANS_FILE = "bans.json"
SECRET_KEY = "RBX-Discord-Private-KEY-2026!x9"

# ================= UTILITIES =================

def load_bans():
    if not os.path.exists(BANS_FILE):
        return {}
    with open(BANS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_bans(data):
    with open(BANS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# ================= GET BANS (ROBLOX) =================
@app.route("/bans", methods=["GET"])
def get_bans():
    bans = load_bans()

    # Roblox يحتاج فقط الاسم + السبب
    formatted = {name: info["reason"] for name, info in bans.items()}
    return jsonify(formatted), 200

# ================= BAN PLAYER (ONCE ONLY) =================
@app.route("/bans", methods=["POST"])
def ban_player():
    data = request.json

    if not data or data.get("key") != SECRET_KEY:
        return jsonify({"error": "Unauthorized"}), 403

    username = data.get("username")
    user_id = data.get("userId")
    reason = data.get("reason", "No reason provided")
    staff = data.get("staff", "Unknown")

    if not username or not user_id:
        return jsonify({"error": "Missing username or userId"}), 400

    bans = load_bans()

    # 🚫 إذا كان مبنّد مسبقًا → لا نعيد الباند
    if username in bans:
        return jsonify({
            "status": "already_banned",
            "username": username,
            "reason": bans[username]["reason"]
        }), 200

    # ✅ بان جديد (مرة واحدة فقط)
    bans[username] = {
        "userId": user_id,
        "reason": reason,
        "staff": staff,
        "time": datetime.utcnow().isoformat()
    }

    save_bans(bans)

    return jsonify({
        "status": "banned",
        "username": username
    }), 200

# ================= UNBAN PLAYER =================
@app.route("/bans", methods=["DELETE"])
def unban_player():
    data = request.json

    if not data or data.get("key") != SECRET_KEY:
        return jsonify({"error": "Unauthorized"}), 403

    username = data.get("username")

    if not username:
        return jsonify({"error": "Missing username"}), 400

    bans = load_bans()

    if username not in bans:
        return jsonify({
            "status": "not_banned",
            "username": username
        }), 200

    # 🔥 حذف نهائي
    del bans[username]
    save_bans(bans)

    return jsonify({
        "status": "unbanned",
        "username": username
    }), 200

# ================= RUN SERVER =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
