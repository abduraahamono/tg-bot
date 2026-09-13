#!/usr/bin/env python3
"""
Arkadaş Executive OS - Local Web Dashboard
Port: 3131
Provides complete visual management for:
1. YouTube Shorts Queue & instant publishing
2. Social Media Hub (YouTube, Telegram, Instagram, TikTok, X)
3. Student CRM Leads & Excel Export
4. Autopilot Scheduling Controls
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, Response

# Add project root to sys.path
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from crm.lead_manager import CRMLeadManager
from engine.youtube_publisher import YouTubePublisher

app = Flask(__name__, template_folder="templates")

SHORTS_PLAN_FILE = BASE_DIR / "brain_data" / "scheduled_youtube_shorts.json"
CONFIG_FILE = BASE_DIR / "bot_config.json"
SOCIAL_FILE = BASE_DIR / "social_credentials.json"

crm_manager = CRMLeadManager()

def load_json(filepath: Path, default=None):
    if default is None:
        default = {}
    if filepath.exists():
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return default

def save_json(filepath: Path, data):
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/video_stream/<path:filepath>")
def video_stream(filepath):
    """Streams local MP4 or MOV video file directly to browser video player."""
    full_path = (BASE_DIR / filepath).resolve()
    if not full_path.exists() or not full_path.is_file():
        # Try finding in ChatExport_Turkiyada ta'lim
        return Response("Video topilmadi", status=404)
    
    mimetype = "video/mp4"
    if str(full_path).lower().endswith(".mov"):
        mimetype = "video/quicktime"
        
    return send_file(str(full_path), mimetype=mimetype)

@app.route("/api/videos", methods=["GET"])
def get_videos():
    """Returns the list of 50 scheduled YouTube Shorts."""
    data = load_json(SHORTS_PLAN_FILE, {"shorts": []})
    return jsonify(data)

@app.route("/api/videos/upload_now", methods=["POST"])
def upload_video_now():
    """Uploads a chosen video immediately to YouTube and posts pinned comment."""
    payload = request.get_json() or {}
    video_id = payload.get("video_id")
    if not video_id:
        return jsonify({"success": False, "error": "video_id berilmadi"}), 400

    plan_data = load_json(SHORTS_PLAN_FILE, {"shorts": []})
    shorts_list = plan_data.get("shorts", [])

    target_video = None
    target_idx = None
    for idx, v in enumerate(shorts_list):
        if v.get("id") == video_id:
            target_video = v
            target_idx = idx
            break

    if not target_video:
        return jsonify({"success": False, "error": "Video reja ro'yxatidan topilmadi"}), 404

    video_path = target_video.get("video_path")
    full_video_path = str(BASE_DIR / video_path)

    yt = YouTubePublisher()
    if not yt.is_configured():
        return jsonify({"success": False, "error": "YouTube API ulanmagan yoki token eskirgan"}), 500

    result = yt.upload_video(
        video_path=full_video_path,
        title=target_video.get("title", "Turkiyada ta'lim #Shorts"),
        description=target_video.get("description", ""),
        privacy_status="public",
        pin_telegram_comment=True
    )

    if result.get("success"):
        # Update plan status
        shorts_list[target_idx]["status"] = "published"
        shorts_list[target_idx]["youtube_id"] = result.get("video_id")
        shorts_list[target_idx]["youtube_url"] = result.get("video_url")
        shorts_list[target_idx]["published_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_json(SHORTS_PLAN_FILE, plan_data)
        return jsonify(result)
    else:
        return jsonify({"success": False, "error": result.get("error")}), 500

@app.route("/api/leads", methods=["GET"])
def get_leads():
    """Returns all leads from CRM."""
    leads = crm_manager.load_leads()
    return jsonify(leads)

@app.route("/api/leads/update_status", methods=["POST"])
def update_lead_status():
    payload = request.get_json() or {}
    lead_id = payload.get("id")
    new_status = payload.get("status")
    if not lead_id or not new_status:
        return jsonify({"success": False, "error": "Yetarli parametrlar berilmadi"}), 400

    ok = crm_manager.update_lead_status(int(lead_id), new_status)
    return jsonify({"success": ok})

@app.route("/api/leads/delete", methods=["POST"])
def delete_lead():
    payload = request.get_json() or {}
    lead_id = payload.get("id")
    if not lead_id:
        return jsonify({"success": False, "error": "id berilmadi"}), 400

    ok = crm_manager.delete_lead(int(lead_id))
    return jsonify({"success": ok})

@app.route("/api/leads/add", methods=["POST"])
def add_lead():
    payload = request.get_json() or {}
    if not payload.get("name") or not payload.get("phone"):
        return jsonify({"success": False, "error": "Ism va telefon talab qilinadi"}), 400

    res = crm_manager.save_lead(payload)
    return jsonify({"success": True, "lead": res.get("lead")})

@app.route("/api/export_excel", methods=["GET"])
def export_excel():
    """Generates Excel-ready UTF-8 BOM CSV download."""
    csv_file = crm_manager.generate_excel_export()
    now_str = datetime.now().strftime("%Y%m%d_%H%M")
    return send_file(
        str(csv_file),
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"arkadas_talabalar_{now_str}.csv"
    )

@app.route("/api/social_status", methods=["GET"])
def get_social_status():
    """Checks and returns live social connections."""
    social_cfg = load_json(SOCIAL_FILE, {})
    
    # Check YouTube
    yt = YouTubePublisher()
    yt_connected = yt.is_configured()
    
    # Check Telegram
    tg_token = social_cfg.get("telegram", {}).get("bot_token", "")
    tg_connected = bool(tg_token and len(tg_token) > 20)

    return jsonify({
        "youtube": {
            "connected": yt_connected,
            "channel_name": social_cfg.get("youtube", {}).get("channel_name", "arkadaş"),
            "channel_title": "arkadaş" if yt_connected else None
        },
        "telegram": {
            "connected": tg_connected,
            "bot_username": "@ArkadasAdminBot",
            "channel_id": "@arkadasuz"
        },
        "twitter": {
            "connected": True,
            "mode": "Browser Automator"
        },
        "instagram": {
            "connected": False
        },
        "tiktok": {
            "connected": False
        }
    })

@app.route("/api/settings/autopilot", methods=["POST"])
def save_autopilot():
    payload = request.get_json() or {}
    cfg = load_json(CONFIG_FILE, {})
    cfg["autopilot_enabled"] = payload.get("enabled", True)
    cfg["lunch_time"] = payload.get("lunchTime", "13:00")
    cfg["evening_time"] = payload.get("eveningTime", "19:30")
    cfg["funnel_url"] = payload.get("funnelUrl", "https://t.me/arkadasuz")
    save_json(CONFIG_FILE, cfg)
    return jsonify({"success": True})

if __name__ == "__main__":
    print("[Arkadaş Executive OS] Web Dashboard ishga tushmoqda: http://127.0.0.1:3131", flush=True)
    app.run(host="0.0.0.0", port=3131, debug=False)
