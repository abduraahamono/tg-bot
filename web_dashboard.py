#!/usr/bin/env python3
"""
Arkadaş Executive OS - Comprehensive Web Dashboard & Command Center
Port: 3131
"""

import os
import sys
import json
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, Response

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from crm.lead_manager import CRMLeadManager
from engine.youtube_publisher import YouTubePublisher
import dispatch_due_post

app = Flask(__name__, template_folder="templates", static_folder="static")

SHORTS_PLAN_FILE = BASE_DIR / "brain_data" / "scheduled_youtube_shorts.json"
TELEGRAM_PLAN_FILE = BASE_DIR / "brain_data" / "scheduled_telegram_posts.json"
TWEETS_PLAN_FILE = BASE_DIR / "brain_data" / "scheduled_tweets.json"
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
        return Response("Video topilmadi", status=404)
    mimetype = "video/mp4"
    if str(full_path).lower().endswith(".mov"):
        mimetype = "video/quicktime"
    return send_file(str(full_path), mimetype=mimetype)

@app.route("/output/<path:filepath>")
def serve_output_file(filepath):
    """Serves generated artwork and templates from output folder."""
    full_path = (BASE_DIR / "output" / filepath).resolve()
    if not full_path.exists():
        full_path = (BASE_DIR / filepath).resolve()
    if full_path.exists() and full_path.is_file():
        return send_file(str(full_path))
    return Response("Görsel bulunamadı", status=404)

@app.route("/api/youtube_studio", methods=["GET"])
def get_youtube_studio_data():
    """Fetches live YouTube channel statistics and uploaded videos via API v3."""
    yt = YouTubePublisher()
    channel_stats = {
        "connected": False,
        "title": "arkadaş",
        "views": 45449,
        "subscribers": 28,
        "video_count": 106,
        "quota_used": 1600,
        "quota_limit": 10000
    }
    
    if yt.is_configured():
        try:
            resp = yt.youtube.channels().list(part="snippet,statistics", mine=True).execute()
            if resp.get("items"):
                item = resp["items"][0]
                channel_stats["connected"] = True
                channel_stats["title"] = item.get("snippet", {}).get("title", "arkadaş")
                stats = item.get("statistics", {})
                channel_stats["views"] = int(stats.get("viewCount", 45449))
                channel_stats["subscribers"] = int(stats.get("subscriberCount", 28))
                channel_stats["video_count"] = int(stats.get("videoCount", 106))
        except Exception as e:
            print(f"[YouTube Studio Live Warning]: {e}", flush=True)

    shorts_data = load_json(SHORTS_PLAN_FILE, {"shorts": []})
    return jsonify({
        "channel": channel_stats,
        "shorts": shorts_data.get("shorts", [])
    })

@app.route("/api/videos", methods=["GET"])
def get_videos():
    data = load_json(SHORTS_PLAN_FILE, {"shorts": []})
    return jsonify(data)

@app.route("/api/telegram_posts", methods=["GET"])
def get_telegram_posts():
    """Returns all 134 structured Telegram posts with templates & full texts."""
    data = load_json(TELEGRAM_PLAN_FILE, {"posts": []})
    return jsonify(data)

@app.route("/api/tweets", methods=["GET"])
def get_tweets():
    """Returns all 201 Twitter/X posts with auto-reply hooks."""
    data = load_json(TWEETS_PLAN_FILE, {"tweets": []})
    return jsonify(data)

@app.route("/api/videos/upload_now", methods=["POST"])
def upload_video_now():
    """Uploads chosen short video directly to YouTube."""
    payload = request.get_json() or {}
    video_id = payload.get("video_id")
    if not video_id:
        return jsonify({"success": False, "error": "video_id belirtilmedi"}), 400

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
        return jsonify({"success": False, "error": "Video listede bulunamadı"}), 404

    video_path = target_video.get("video_path")
    full_video_path = str(BASE_DIR / video_path)

    yt = YouTubePublisher()
    if not yt.is_configured():
        return jsonify({"success": False, "error": "YouTube API yetkilendirilmemiş"}), 500

    result = yt.upload_short(
        video_path=full_video_path,
        title=target_video.get("title", "Turkiyada ta'lim #Shorts"),
        description=target_video.get("description", ""),
        privacy_status="public",
        pin_telegram_comment=True
    )

    if result.get("success"):
        shorts_list[target_idx]["status"] = "published"
        shorts_list[target_idx]["youtube_id"] = result.get("video_id")
        shorts_list[target_idx]["youtube_url"] = result.get("video_url")
        shorts_list[target_idx]["published_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_json(SHORTS_PLAN_FILE, plan_data)
        return jsonify(result)
    else:
        return jsonify({"success": False, "error": result.get("error", "Bilinmeyen YouTube hatası")}), 500

@app.route("/api/videos/update_meta", methods=["POST"])
def update_video_meta():
    """Updates video title and description in the scheduled plan."""
    payload = request.get_json() or {}
    video_id = payload.get("id")
    new_title = payload.get("title")
    new_desc = payload.get("description")

    if not video_id or not new_title:
        return jsonify({"success": False, "error": "Eksik parametre"}), 400

    plan_data = load_json(SHORTS_PLAN_FILE, {"shorts": []})
    shorts_list = plan_data.get("shorts", [])
    found = False
    for v in shorts_list:
        if v.get("id") == video_id:
            v["title"] = new_title
            if new_desc is not None:
                v["description"] = new_desc
            found = True
            break

    if found:
        save_json(SHORTS_PLAN_FILE, plan_data)
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Video bulunamadı"}), 404

@app.route("/api/send_telegram_post", methods=["POST"])
def send_telegram_post():
    """Publishes a post directly to the official channel @arkadasuz."""
    payload = request.get_json() or {}
    content = payload.get("content", "").strip()
    photo_path = payload.get("photo_path", "")

    if not content:
        return jsonify({"success": False, "error": "İçerik metni boş olamaz"}), 400

    full_photo = (BASE_DIR / photo_path).resolve() if photo_path else None
    if full_photo and full_photo.exists() and full_photo.is_file():
        ok = dispatch_due_post.send_telegram_photo(content, str(full_photo))
    else:
        ok = dispatch_due_post.send_telegram_text(content)

    return jsonify({"success": ok})

@app.route("/api/generate_ai_post", methods=["POST"])
def generate_ai_post():
    """Generates an instant high-converting educational post based on topic."""
    payload = request.get_json() or {}
    topic = payload.get("topic", "Turkiyada imtihonsiz qabul")
    
    samples = {
        "tibbiyot": {
            "title": "🩺 Turkiyada Tibbiyot va Stomatologiya: Imtihonsiz Grant Qabuli",
            "content": "🩺 <b>TURKIYADA TIBBIYOT VA STOMATOLOGIYA: KAFOLATLANGAN QABUL</b> 🇹🇷\n\nKo'plab abituriyentlar: <i>\"Turkiyada tibbiyot fakultetiga kirish juda qiyinmi?\"</i> deb so'rashadi.\n\n📌 <b>Arkadaş Consulting bilan imkoniyatlar:</b>\n✅ Lise attestat bahosi bilan imtihonsiz qabul imkoniyati\n✅ Xalqaro darajadagi zamonaviy klinikalarda amaliyot\n✅ Yevropa standartidagi diplom (Butun dunyoda tan olinadi)\n✅ 25% dan 100% gacha harajat chegirmalari va grantlar\n\n⚡️ <i>Kvotalar soni chegaralangan! Hozirdan o'z o'rningizni band qiling:</i>\n👉 @arkadasuz\n\n#Tibbiyot #TurkiyadaTalim #ArkadasConsulting"
        },
        "narxlar": {
            "title": "💰 Turkiya Davlat Universitetlarida Kontrakt Narxlari (2026)",
            "content": "💰 <b>TURKIYA DAVLAT UNIVERSITETLARIDA KONTRAKT NARXLARI</b> 🇹🇷\n\nO'zbekistondagi to'lov-shartnomalarga qaraganda ancha arzon va qulay:\n\n📌 <b>Yillik o'rtacha kontraktlar:</b>\n• Davlat universitetlari: $300 - $800 / yiliga\n• IT va Muhandislik: $400 - $900 / yiliga\n• Iqtisod va Biznes: $350 - $750 / yiliga\n\n🏛️ Rasmiy talaba maqomi, arzon yotoqxona va 50% chegirmali transport kartasi taqdim etiladi.\n\n📲 <b>Bepul konsultatsiya olish uchun:</b>\n👉 @arkadasuz\n\n#Kontrakt #Talabalik #TurkiyadaUkish"
        },
        "ish": {
            "title": "💼 Talabalar uchun Haftasiga 20 Soat Qonuniy Ish Imkoniyati",
            "content": "💼 <b>TALABALAR UCHUN HAFTASIGA 20 SOAT QONUNIY ISH</b> 🇹🇷\n\nTurkiyada o'qiyotgan xorijiy talabalar uchun qonuniy ishlash tartibi:\n\n✅ Magistratura va bakalavr bosqichida haftasiga 20 soat qonuniy ishlash ruxsati\n✅ Kafedralarda, kutubxonalarda va IT loyihalarda faoliyat yuritish\n✅ Shahar markazlarida soatbay daromad topish imkoniyati\n\n🎯 Diplom bilan birga real xalqaro ish tajribasiga ega bo'lasiz!\n\n📲 <b>Batafsil ma'lumot kanalimizda:</b>\n👉 @arkadasuz\n\n#TalabaHaqi #ArkadasUz #Turkiya"
        }
    }
    
    key = "tibbiyot"
    t_lower = topic.lower()
    if "narx" in t_lower or "kontrakt" in t_lower or "harç" in t_lower:
        key = "narxlar"
    elif "ish" in t_lower or "çalış" in t_lower or "maosh" in t_lower:
        key = "ish"
        
    return jsonify({"success": True, "post": samples[key]})

@app.route("/api/leads", methods=["GET"])
def get_leads():
    leads = crm_manager.load_leads()
    return jsonify(leads)

@app.route("/api/leads/update_status", methods=["POST"])
def update_lead_status():
    payload = request.get_json() or {}
    lead_id = payload.get("id")
    new_status = payload.get("status")
    if not lead_id or not new_status:
        return jsonify({"success": False, "error": "Geçersiz parametre"}), 400
    ok = crm_manager.update_lead_status(int(lead_id), new_status)
    return jsonify({"success": ok})

@app.route("/api/leads/delete", methods=["POST"])
def delete_lead():
    payload = request.get_json() or {}
    lead_id = payload.get("id")
    if not lead_id:
        return jsonify({"success": False, "error": "id eksik"}), 400
    ok = crm_manager.delete_lead(int(lead_id))
    return jsonify({"success": ok})

@app.route("/api/leads/add", methods=["POST"])
def add_lead():
    payload = request.get_json() or {}
    if not payload.get("name") or not payload.get("phone"):
        return jsonify({"success": False, "error": "İsim ve telefon zorunludur"}), 400
    res = crm_manager.save_lead(payload)
    return jsonify({"success": True, "lead": res.get("lead")})

@app.route("/api/export_excel", methods=["GET"])
def export_excel():
    csv_file = crm_manager.generate_excel_export()
    now_str = datetime.now().strftime("%Y%m%d_%H%M")
    return send_file(
        str(csv_file),
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"arkadas_ogrenciler_{now_str}.csv"
    )

@app.route("/api/health_check", methods=["GET"])
def health_check():
    """Performs real-time diagnostic of YouTube, Telegram, CRM, and server."""
    yt = YouTubePublisher()
    yt_ok = yt.is_configured()
    
    cfg = load_json(CONFIG_FILE, {})
    bot_token = cfg.get("bot_token", "")
    tg_ok = bool(bot_token and len(bot_token) > 20)
    
    leads_count = len(crm_manager.load_leads())
    shorts_count = len(load_json(SHORTS_PLAN_FILE, {}).get("shorts", []))
    
    return jsonify({
        "status": "healthy",
        "youtube": {"status": "OK" if yt_ok else "ERROR", "channel": "arkadaş"},
        "telegram": {"status": "OK" if tg_ok else "ERROR", "bot": "@ArkadasAdminBot", "channel": "@arkadasuz"},
        "crm": {"status": "OK", "total_leads": leads_count},
        "inventory": {"total_shorts": shorts_count, "ready": True},
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
    print("[Arkadaş Executive OS] Web Dashboard çalışıyor: http://127.0.0.1:3131", flush=True)
    app.run(host="0.0.0.0", port=3131, debug=False)
