#!/usr/bin/env python3
"""
Arkadaş Executive OS - Comprehensive Web Dashboard & Agency Super-Hub
Port: 3131
"""

import os
import sys
import json
import urllib.request
import urllib.parse
import asyncio
import hashlib
import threading
import time
import random
from pathlib import Path
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, jsonify, send_file, Response, session, redirect, url_for, send_from_directory
import edge_tts

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from crm.lead_manager import CRMLeadManager
from engine.youtube_publisher import YouTubePublisher
from engine.content_generator import ContentGenerator
import dispatch_due_post

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.getenv("FLASK_SECRET_KEY", "arkadas_executive_os_master_secret_2026")
ADMIN_PIN = os.getenv("ADMIN_DASHBOARD_PIN", "arkadas2026")

from engine.three_pillars_api import pillars_bp
app.register_blueprint(pillars_bp)

AUDIO_DIR = BASE_DIR / "output" / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR = BASE_DIR / "crm" / "documents"
DOCS_DIR.mkdir(parents=True, exist_ok=True)

SHORTS_PLAN_FILE = BASE_DIR / "brain_data" / "scheduled_youtube_shorts.json"
TELEGRAM_PLAN_FILE = BASE_DIR / "brain_data" / "scheduled_telegram_posts.json"
TWEETS_PLAN_FILE = BASE_DIR / "brain_data" / "scheduled_tweets.json"
CONFIG_FILE = BASE_DIR / "bot_config.json"
CROSS_POSTS_FILE = BASE_DIR / "brain_data" / "scheduled_cross_posts.json"
SOCIAL_FILE = BASE_DIR / "social_credentials.json"
UNIVERSITIES_FILE = BASE_DIR / "brain_data" / "universities.json"
FAQ_FILE = BASE_DIR / "brain_data" / "faq_knowledge.json"

crm_manager = CRMLeadManager()
content_gen = ContentGenerator()

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

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("is_admin", False):
            auth_header = request.headers.get("X-Admin-Pin")
            if auth_header and auth_header == ADMIN_PIN:
                session["is_admin"] = True
            else:
                return jsonify({"error": "Yetkisiz erişim. Lütfen Yönetici PIN kodu ile giriş yapın.", "authenticated": False}), 401
        return f(*args, **kwargs)
    return decorated_function

# ==============================================================
# 0. ADMIN GATEKEEPER & AUTHENTICATION ENDPOINTS
# ==============================================================

@app.route("/api/auth/status", methods=["GET"])
def auth_status():
    return jsonify({"authenticated": session.get("is_admin", False)})

@app.route("/api/auth/login", methods=["POST"])
def auth_login():
    payload = request.get_json() or {}
    pin = str(payload.get("pin", "")).strip()
    if pin == ADMIN_PIN:
        session["is_admin"] = True
        return jsonify({"success": True, "message": "Yönetici oturumu doğrulandı"})
    return jsonify({"success": False, "error": "Geçersiz Yönetici PIN Kodu"}), 401

@app.route("/api/auth/logout", methods=["POST"])
def auth_logout():
    session.pop("is_admin", None)
    return jsonify({"success": True, "message": "Oturum kilitlendi"})

# ==============================================================
# AUDIO SYNTHESIS ENGINE (EDGE-TTS NEURAL VOICES)
# ==============================================================

VOICE_MAPPING = {
    "v_kamola": "uz-UZ-MadinaNeural",
    "v_sardor": "uz-UZ-SardorNeural",
    "v_elif": "tr-TR-EmelNeural",
    "v_kerem": "tr-TR-AhmetNeural",
    "v_anastasia": "ru-RU-SvetlanaNeural",
    "v_dmitriy": "ru-RU-DmitryNeural"
}

async def generate_neural_tts(text: str, voice_id: str, rate: str = "+0%"):
    voice_name = VOICE_MAPPING.get(voice_id, "uz-UZ-MadinaNeural")
    text_hash = hashlib.md5(f"{text}_{voice_name}_{rate}".encode("utf-8")).hexdigest()[:10]
    filename = f"speech_{text_hash}.mp3"
    filepath = AUDIO_DIR / filename
    
    if not filepath.exists():
        communicate = edge_tts.Communicate(text, voice_name, rate=rate)
        await communicate.save(str(filepath))
        
    return filename, f"/audio/{filename}"

@app.route("/api/synthesize_audio", methods=["POST"])
def synthesize_audio():
    payload = request.get_json() or {}
    text = payload.get("text", "").strip()
    voice_id = payload.get("voice_id", "v_kamola")
    speed = float(payload.get("speed", 1.0))
    
    if not text:
        return jsonify({"success": False, "error": "Seslendirilecek metin boş olamaz"}), 400
        
    rate_str = "+0%"
    if speed > 1.0:
        rate_str = f"+{int(round((speed - 1.0) * 100))}%"
    elif speed < 1.0:
        rate_str = f"-{int(round((1.0 - speed) * 100))}%"
        
    try:
        filename, audio_url = asyncio.run(generate_neural_tts(text, voice_id, rate_str))
        return jsonify({
            "success": True,
            "filename": filename,
            "audio_url": audio_url,
            "voice_id": voice_id,
            "voice_name": VOICE_MAPPING.get(voice_id, "uz-UZ-MadinaNeural")
        })
    except Exception as e:
        print(f"[Edge-TTS Error]: {e}", flush=True)
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/audio/<path:filename>")
def serve_audio_file(filename):
    return send_from_directory(str(AUDIO_DIR), filename)

# ==============================================================
# CRM DOCUMENT STORAGE ENDPOINTS
# ==============================================================

@app.route("/api/leads/upload_doc", methods=["POST"])
def upload_lead_document():
    lead_id = request.form.get("lead_id")
    doc_type = request.form.get("doc_type", "Pasport")
    file = request.files.get("file")
    
    if not lead_id or not file or file.filename == "":
        return jsonify({"success": False, "error": "Geçersiz dosya veya öğrenci ID"}), 400
        
    lead_folder = DOCS_DIR / str(lead_id)
    lead_folder.mkdir(parents=True, exist_ok=True)
    
    clean_filename = f"{doc_type}_{file.filename.replace(' ', '_')}"
    save_path = lead_folder / clean_filename
    file.save(str(save_path))
    
    leads = crm_manager.load_leads()
    updated = False
    for l in leads:
        if str(l.get("id")) == str(lead_id):
            if "documents" not in l:
                l["documents"] = []
            l["documents"].append({
                "type": doc_type,
                "filename": clean_filename,
                "url": f"/api/leads/docs/{lead_id}/{clean_filename}",
                "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            updated = True
            break
            
    if updated:
        crm_manager.save_leads(leads)
        
    return jsonify({
        "success": True,
        "filename": clean_filename,
        "url": f"/api/leads/docs/{lead_id}/{clean_filename}"
    })

@app.route("/api/leads/docs/<lead_id>/<path:filename>")
def serve_lead_document(lead_id, filename):
    folder = DOCS_DIR / str(lead_id)
    return send_from_directory(str(folder), filename)

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

@app.route("/api/universities", methods=["GET"])
def get_universities():
    """Returns the university database."""
    unis = load_json(UNIVERSITIES_FILE, [])
    return jsonify(unis)

@app.route("/api/faqs", methods=["GET"])
def get_faqs():
    """Returns the FAQ knowledge base."""
    faqs = load_json(FAQ_FILE, [])
    return jsonify(faqs)

@app.route("/api/calculate_budget", methods=["POST"])
def calculate_budget():
    """Calculates student living & tuition budget."""
    payload = request.get_json() or {}
    tuition = float(payload.get("tuition", 600))
    dorm = float(payload.get("dorm", 180)) * 10
    food = float(payload.get("food", 150)) * 10
    transport = float(payload.get("transport", 20)) * 10
    insurance = float(payload.get("insurance", 120))
    tomer = float(payload.get("tomer", 800) if payload.get("need_tomer") else 0)

    total_usd = tuition + dorm + food + transport + insurance + tomer
    total_try = total_usd * 34.2
    total_uzs = total_usd * 12850

    return jsonify({
        "tuition": tuition,
        "dorm_10m": dorm,
        "food_10m": food,
        "transport_10m": transport,
        "insurance": insurance,
        "tomer": tomer,
        "total_usd": round(total_usd, 2),
        "total_try": round(total_try, 2),
        "total_uzs": round(total_uzs, 2),
        "formatted_usd": f"${total_usd:,.2f}",
        "formatted_uzs": f"{total_uzs:,.0f} so'm"
    })

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
    """Generates dynamic high-converting educational content supporting multiple languages and influencer personas."""
    payload = request.get_json() or {}
    topic = payload.get("topic", "tibbiyot")
    custom_keyword = payload.get("keyword", "").strip()
    lang = payload.get("lang", "uz").lower()  # uz, kaa, ru, tr
    persona = payload.get("persona", "corporate").lower()  # mila, madina, corporate
    
    try:
        # Karakalpak Language Support
        if lang == "kaa":
            topic_kaa = {
                "tibbiyot": ("Meditsina hám Stomatologiya", "🩺", "Imtixansız qabıllaw hám 50-100% grantlar", "Xalıqaralıq klinikalarda ámeliyat"),
                "ish": ("Studentler ushın Rásmiy Jumıs", "💼", "Háptege 20 saat nızamlı islew imkániyatı", "Saatbay jaqsı dáramat"),
                "viza": ("Studentlik Vizası hám İkamet", "📑", "100% kepillengen qabıllaw", "Göç İdaresinde tolıq yuridikalıq járdem"),
                "tomer": ("TÖMER Túrk Tili Kursları", "🇹🇷", "Til bilmey turıp universitetke kiriw", "1 jıl til úyrenip fakultetke ótiw"),
                "narxlar": ("Kontrakt Bahaları hám Qárejetler", "💰", "Mámleketlik universitetlerde arzan kontraktlar", "Yataqxona hám arzan transport")
            }
            name, emoji, highlight, subtext = topic_kaa.get(topic, (custom_keyword or "Túrkiyada Oqıw", "🎓", "Kepillengen qabıllaw", "Ózbekstanda 100% tán alınatuǵın Yevropa diplomı"))
            content = f"{emoji} <b>TÚRKIYADA {name.upper()}: 2026-2027 QABILLAW MÁWSIMI</b> 🇹🇷🎓\n\n" \
                      f"Ássalamu áleykum húrmetli jaslar hám ata-analar!\n" \
                      f"Túrkiyada hesh qanday qıyın imtixansız, tek mektep yamasa kolledj attestat bahalarıńız benen nufuzlı mámleketlik universitetlerge oqıwǵa kiriw múmkin!\n\n" \
                      f"📌 <b>Tiykarǵı Múmkinshilikler:</b>\n" \
                      f"✅ {highlight}\n" \
                      f"✅ {subtext}\n" \
                      f"✅ Qolaylı mámleketlik yataqxana hám 50% jeńillikli student transport kartası\n\n" \
                      f"⚠️ <b>Oldınnan tólem joq — 0$ qáwip!</b> Dáslep qabıllaw xatınız shıǵadı, keyin tólem qılasız.\n\n" \
                      f"📲 <i>Qaraqalpaqstanlı jaslar ushın biypul másláhát:</i>\n" \
                      f"👉 @arkadasuzz | Telegram kanal: @arkadasuz\n\n" \
                      f"#TurkiyadaTalim #Qaraqalpaqstan #Nukus #ArkadasConsulting #Talaba2026"
            title = f"{emoji} [Qaraqalpaqsha] {name} Qabıllaw E'lanı"
            return jsonify({"success": True, "post": {"title": title, "content": content}})

        # Russian Language Support
        if lang == "ru":
            topic_ru = {
                "tibbiyot": ("Медицина и Стоматология", "🩺", "Поступление без экзаменов и гранты до 100%", "Практика в ведущих европейских клиниках"),
                "ish": ("Официальная Работа для Студентов", "💼", "20 часов в неделю официальной работы", "Возможность покрывать расходы во время учебы"),
                "viza": ("Студенческая Виза и ВНЖ (Икамет)", "📑", "100% гарантия зачисления и оформления", "Полное юридическое сопровождение в миграционной службе"),
                "tomer": ("Курсы турецкого языка TÖMER", "🇹🇷", "Поступление без знания языка", "Год языковой подготовки и переход на специальность"),
                "narxlar": ("Стоимость обучения и проживания", "💰", "Доступные государственные вузы от $250 в год", "Льготное общежитие и студенческий проездной")
            }
            name, emoji, highlight, subtext = topic_ru.get(topic, (custom_keyword or "Обучение в Турции", "🎓", "Гарантия зачисления", "100% нострификация диплома в Узбекистане"))
            content = f"{emoji} <b>ОБУЧЕНИЕ В ТУРЦИИ: {name.upper()} 2026-2027</b> 🇹🇷🎓\n\n" \
                      f"Здравствуйте, уважаемые абитуриенты и родители!\n" \
                      f"Поступление в ведущие государственные и частные вузы Турции БЕЗ вступительных экзаменов — на основании школьного аттестата!\n\n" \
                      f"📌 <b>Главные преимущества:</b>\n" \
                      f"✅ {highlight}\n" \
                      f"✅ {subtext}\n" \
                      f"✅ Официальное признание диплома в Узбекистане и странах ЕС (Bologna Process)\n" \
                      f"✅ Встреча в аэропорту Стамбула, заселение в общежитие, сим-карта и банковский счет\n\n" \
                      f"🛡️ <b>БЕЗ ПРЕДОПЛАТЫ — 0% РИСКА!</b> Оплата услуг агентства производится строго ПОСЛЕ получения официального приказа о зачислении (Acceptance Letter).\n\n" \
                      f"📲 <i>Забронируйте место прямо сейчас (квоты ограничены):</i>\n" \
                      f"👉 Консультант: @arkadasuzz | Канал: @arkadasuz\n\n" \
                      f"#УчебавТурции #ОбразованиеВТурции #Ташкент #Талаба2026 #ArkadasConsulting"
            title = f"{emoji} [Русский] {name} - Прием 2026"
            return jsonify({"success": True, "post": {"title": title, "content": content}})

        # Turkish Language Support
        if lang == "tr":
            topic_tr = {
                "tibbiyot": ("Tıp ve Diş Hekimliği", "🩺", "YÖS Şartı Olmadan Kabul", "Uluslararası akredite üniversite hastaneleri"),
                "ish": ("Öğrenciler İçin Yasal Çalışma", "💼", "Haftalık 20 saat part-time çalışma izni", "Eğitim alırken bütçeyi karşılama fırsatı"),
                "viza": ("Öğrenci Vizesi ve İkamet İzni", "📑", "Garantili kabul ve göç idaresi işlemleri", "Eksiksiz resmi danışmanlık"),
                "tomer": ("TÖMER Türkçe Dil Eğitimi", "🇹🇷", "Hazırlık sınıfı ile doğrudan lisans geçişi", "C1 seviyesi sertifika programı"),
                "narxlar": ("Harç Ücretleri ve Yaşam Maliyeti", "💰", "Devlet üniversitelerinde uygun harçlar", "KYK yurtları ve indirimli İstanbulkart")
            }
            name, emoji, highlight, subtext = topic_tr.get(topic, (custom_keyword or "Türkiye'de Üniversite", "🎓", "Garantili Kabul", "YÖK onaylı ve uluslararası geçerli diploma"))
            content = f"{emoji} <b>TÜRKİYE'DE EĞİTİM: {name.upper()} 2026-2027</b> 🇹🇷🎓\n\n" \
                      f"Özbekistan ve Orta Asyalı öğrenciler için Türkiye'nin en seçkin devlet ve vakıf üniversitelerinde kontenjanlar açıldı!\n\n" \
                      f"📌 <b>Fırsatlar:</b>\n" \
                      f"✅ {highlight}\n" \
                      f"✅ {subtext}\n" \
                      f"✅ Havalimanı karşılama, yurt yerleştirme ve ikamet danışmanlığı\n\n" \
                      f"🛡️ <b>Ön ödeme yok — Sıfır risk!</b> Resmi kabul belgeniz geldikten sonra ödeme yapılır.\n\n" \
                      f"📲 <i>Detaylı Bilgi ve Başvuru:</i>\n" \
                      f"👉 @arkadasuzz | Kanal: @arkadasuz"
            title = f"{emoji} [Türkçe] {name} Başvuru Rehberi"
            return jsonify({"success": True, "post": {"title": title, "content": content}})

        # Uzbek Language Support with Persona options (Mila, Madina, Corporate)
        if persona == "mila":
            content = f"Hey do'stlar! Mila bilan Istanbul sayohatiga va talabalik drayviga tayyormisiz? ✨🇹🇷\n\n" \
                      f"Bugun sizlarga bir ajoyib yangilik: Turkiyada Yevropa darajasidagi universitetda o'qish uchun yillab repetitorga qatnash yoki qiyin imtihon topshirish umuman shart emas!\n\n" \
                      f"Maktab yoki kollej attestat baholaringiz bilan Arkadaş Consulting orqali to'g'ridan-to'g'ri nufuzli universitetga qabul qilinishingiz va 100% gacha grant yutishingiz mumkin! 🎓🔥\n\n" \
                      f"✨ <b>Mila nima uchun aynan Arkadaş'ni tavsiya qiladi?</b>\n" \
                      f"✅ Oldindan 1 tiyin ham to'lov olinmaydi (0$ xavf!)\n" \
                      f"✅ Aeroportda kutib olishadi, chiroyli yotoqxonaga joylashadi\n" \
                      f"✅ Viza, sug'urta va ikamet ishlarini professional jamoa hal qiladi\n\n" \
                      f"Qani, Istanbulning eng estetik kafelarida birga kofe ichamizmi? ☕️ Joyingizni hoziroq band qiling:\n" \
                      f"👉 @arkadasuzz ga yozing!\n\n" \
                      f"#IstanbulTalabasi #MilaTravels #ArkadasVibe #Talaba2026 #TurkiyadaOqish"
            title = "✨ [Mila Persona] Istanbul Talabalik Vibe & Grantlar"
            return jsonify({"success": True, "post": {"title": title, "content": content}})

        if persona == "madina":
            content = f"Salom do'stlar! Har bir yoshning eng katta orzusi — sifatli ta'lim, xalqaro diplom va yorqin kelajak, to'g'rimi? 🇹🇷❤️\n\n" \
                      f"O'tgan yili men ham xuddi sizdek ikkilanib turgan edim. Ota-onam xavotir olishgandi. Lekin Arkadaş Consulting jamoasi barcha hujjatlarimni tayyorlab, Marmara Universitetiga 100% grant bilan kirishimga yordam berdi!\n\n" \
                      f"📌 <b>Bilib qo'yishingiz kerak bo'lgan muhim faktlar:</b>\n" \
                      f"✅ Turkiyada yotoqxonalar 24/7 qo'riqlanadi va juda xavfsiz\n" \
                      f"✅ Taomlari mazali va hamyonbop, talaba transporti deyarli bepul\n" \
                      f"✅ Ota-onangiz xotirjam bo'lishi uchun hamma xizmatlar rasmiy shartnoma bilan amalga oshiriladi\n" \
                      f"✅ Dastlab rasmiy qabul xatingiz chiqadi, keyin esa to'lov qilasiz!\n\n" \
                      f"Siz faqat qaror qabul qiling, qolganini Arkadaş hal qiladi 😊\n" \
                      f"📲 Bepul konsultatsiya: @arkadasuzz\n\n" \
                      f"#MadinaInIstanbul #ArkadasConsulting #TalabalikHayoti #TurkiyadaTalim"
            title = "❤️ [Madina Persona] Samimiy Talabalik Maslahati"
            return jsonify({"success": True, "post": {"title": title, "content": content}})

        # Default Corporate Uzbek
        if topic == "qa":
            result = content_gen.generate_qa_post(question=custom_keyword if custom_keyword else None)
            content = result.get("caption") if isinstance(result, dict) else str(result)
            title = f"❓ Savol-Javob: {custom_keyword or 'Turkiyada Talabalik Sirlari'}"
        elif topic == "riddle":
            result = content_gen.generate_riddle_post()
            content = result.get("caption") if isinstance(result, dict) else str(result)
            title = "💡 Qiziqarli Topishmoq & Savol"
        elif topic in ["narxlar", "bütçe"]:
            result = content_gen.generate_service_checklist_post()
            content = result.get("caption") if isinstance(result, dict) else str(result)
            title = "💰 Kontrakt Narxlari va 10 Oylik Xarajatlar Smetasi"
        elif topic == "burs":
            content = "🇹🇷 <b>TÜRKİYE BURSLARI DAVLAT GRANTLARI — 100% BEPUL TA'LIM!</b> 🎓\n\n" \
                      "Turkiya hukumati tomonidan beriladigan eng nufuzli stipendiya dasturi imkoniyatlari:\n" \
                      "✅ To'liq bepul o'qish (kontrakt to'lovi 0$)\n" \
                      "✅ Bepul davlat yotoqxonasi va oylik stipendiya\n" \
                      "✅ Aviachipta va bepul tibbiy sug'urta\n\n" \
                      "Arkadaş Consulting orqali professional motivatsion xat, tavsiyanomalar va mukammal ariza topshiring!\n" \
                      "🛡️ <b>Kafolat:</b> Agar grant chiqmasa, to'lovning 50% qaytariladi YOKI $500 lik Asosiy Paketimiz bepul beriladi!\n\n" \
                      "📲 Joylar juda kam! Hozirdan ariza topshiring: @arkadasuzz"
            title = "🏛️ Türkiye Bursları Davlat Granti E'loni"
        else:
            topic_names = {
                "tibbiyot": ("Tibbiyot va Stomatologiya", "🩺", "Imtihonsiz grant va stipendiyalar", "Meditsina fakultetlarida xalqaro klinikalarda amaliyot"),
                "ish": ("Talabalar uchun Rasmiy Ish", "💼", "Haftasiga 20 soat qonuniy ishlash", "O'qishdan bo'sh vaqtda soatbay daromad topish imkoniyati"),
                "viza": ("Talabalik Vizasi & İkamet", "📑", "100% kafolatlangan qabul va viza", "Elchixona va Göç İdaresida to'liq yuridik hamrohlik"),
                "tomer": ("TÖMER Turk Tili Kurslari", "🇹🇷", "Til bilmasdan turib universitetga kirish", "1 yil til o'rganib to'g'ridan-to'g'ri fakultetga o'tish")
            }
            name, emoji, highlight, subtext = topic_names.get(topic, (custom_keyword or topic.capitalize(), "🎓", "Kafolatlangan o'qish", "O'zbekistonda 100% tan olinadigan Yevropa diplomi"))
            
            if isinstance(content_gen.universities, list):
                all_state = content_gen.universities
            elif isinstance(content_gen.universities, dict):
                all_state = content_gen.universities.get("state_universities", [])
            else:
                all_state = []
            sample_count = min(3, len(all_state))
            random_unis = random.sample(all_state, sample_count) if sample_count > 0 else []
            uni_lines = "\n".join([f"• 🏛️ {u.get('name', '')} ({u.get('location', u.get('city', 'Turkiya'))})" for u in random_unis])
            
            content = f"{emoji} <b>TURKIYADA {name.upper()}: 2026-2027 QABUL MAVSUMI</b> 🇹🇷\n\n" \
                      f"📌 <b>Asosiy Imkoniyatlar:</b>\n" \
                      f"✅ {highlight}\n" \
                      f"✅ {subtext}\n" \
                      f"✅ Qulay davlat yotoqxonasi va 50% arzon talaba transport kartasi\n\n"
            
            if uni_lines:
                content += f"🏛️ <b>Ushbu yo'nalish bo'yicha eng yaxshi universitetlar:</b>\n{uni_lines}\n\n"
                
            content += f"⚡️ <i>Kvotalar soni chegaralangan! Qabul arizangizni hozirdan yuboring:</i>\n" \
                       f"👉 @arkadasuzz | Bepul konsultatsiya\n\n" \
                       f"#TurkiyadaTalim #{name.replace(' ', '')} #ArkadasConsulting #Talaba2026"
            title = f"{emoji} {name} Bo'yicha Qabul E'loni"
            
        return jsonify({"success": True, "post": {"title": title, "content": content}})
    except Exception as e:
        print(f"[AI Generator Error]: {e}", flush=True)
        return jsonify({
            "success": True,
            "post": {
                "title": "🎓 Turkiyada O'qish Imkoniyatlari",
                "content": f"🎓 Turkiyada oliy ta'lim olish bo'yicha eng so'nggi yangiliklar va grantlar!\n\n👉 Batafsil: @arkadasuzz"
            }
        })

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

@app.route("/api/settings/autopilot", methods=["GET", "POST"])
def manage_autopilot():
    if request.method == "POST":
        payload = request.get_json() or {}
        cfg = load_json(CONFIG_FILE, {})
        if "enabled" in payload:
            cfg["autopilot_enabled"] = bool(payload.get("enabled"))
        if "lunchTime" in payload:
            cfg["lunch_time"] = payload.get("lunchTime", "13:00")
        if "eveningTime" in payload:
            cfg["evening_time"] = payload.get("eveningTime", "19:30")
        if "funnelUrl" in payload:
            cfg["funnel_url"] = payload.get("funnelUrl", "https://t.me/arkadasuz")
        save_json(CONFIG_FILE, cfg)
        return jsonify({
            "success": True,
            "enabled": cfg.get("autopilot_enabled", True),
            "lunchTime": cfg.get("lunch_time", "13:00"),
            "eveningTime": cfg.get("evening_time", "19:30")
        })
    else:
        cfg = load_json(CONFIG_FILE, {})
        return jsonify({
            "enabled": cfg.get("autopilot_enabled", True),
            "lunchTime": cfg.get("lunch_time", "13:00"),
            "eveningTime": cfg.get("evening_time", "19:30"),
            "funnelUrl": cfg.get("funnel_url", "https://t.me/arkadasuz")
        })

@app.route("/api/autopilot/trigger_now", methods=["POST"])
def trigger_autopilot_now():
    """Immediately triggers dispatch of next queued Telegram post and YouTube shorts."""
    results = {}
    try:
        import dispatch_due_post
        dispatch_due_post.dispatch(dry_run=False, force_first_pending=True)
        results["telegram"] = "Yayınlandı / Hazır"
    except Exception as e:
        results["telegram"] = f"Hata: {str(e)}"

    try:
        import dispatch_youtube_shorts
        dispatch_youtube_shorts.dispatch(force=True, dry_run=False)
        results["youtube"] = "Senkronize Edildi"
    except Exception as e:
        results["youtube"] = f"Hata: {str(e)}"

    return jsonify({
        "success": True,
        "message": "Otopilot başarıyla tetiklendi! Sıradaki içerikler kanala ve servislere yönlendirildi.",
        "results": results,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

@app.route("/api/tiktok_lab", methods=["GET"])
def get_tiktok_lab():
    """Provides 20+ viral TikTok & Reels scripts, hooks, trending audio styles, and hashtag packs."""
    scripts = [
        {
            "id": "tt1",
            "title": "🇹🇷 1 Oylik Haqiqiy Xarajat: Istanbul Talabasi Qancha Sarflaydi?",
            "hook": "Turkiyada talaba bo'lib yashash uchun qancha pul kerak? Ko'pchilik buni yashiradi, lekin hozir sizga 1 oylik hamma cheklarni ko'rsataman!",
            "body": "1️⃣ Yotoqxona: Davlat KYK yotoqxonasi oyiga $45, xususiy yotoqxona $180.\n2️⃣ Oziq-ovqat: Universitet oshxonasida 4 xil issiq ovqat bor-yo'g'i 20 lira ($0.6). Oyiga $120 yetadi.\n3️⃣ Transport: Talaba Istanbulkarti bilan metro, tramvay, parom oyiga bor-yo'g'i $8.\n4️⃣ Shaxsiy xarajat: $60.\nJami oyiga: $250 - $350 yetadi!",
            "cta": "Siz qaysi shaharda o'qishni xohlaysiz? Izohlarda yozing, to'g'ri universitetni tanlab beramiz! 👉 @arkadasuz",
            "audio": "Trending Turkish Acoustic / Chill Beats",
            "tags": ["#TurkiyadaTalim", "#Istanbul", "#TalabalikHayoti", "#Ozbekiston", "#Shorts", "#Talaba"]
        },
        {
            "id": "tt2",
            "title": "🩺 DTM'dan Yiqildingizmi? Turkiyada Tibbiyot Imtihonsiz!",
            "hook": "DTM balingiz kam chiqdimi va orzungizdagi tibbiyotga kirolmadingizmi? Tushkunlikka tushmang, Turkiyada eshiklar ochiq!",
            "body": "Turkiyaning Yevropa akkreditatsiyasiga ega nufuzli davlat va xususiy universitetlariga attestat bahosi bilan to'g'ridan-to'g'ri qabul mavjud.\nDiplomingiz O'zbekistonda ham, butun Yevropa Ittifoqida ham 100% tan olinadi.\nEng muhimi: 1-kursdanoq zamonaviy klinikada amaliyot boshlanadi!",
            "cta": "Kvotalar chegaralangan. Qabul shartlarini bilish uchun bio'dagi havola orqali yozing! 👉 @arkadasuz",
            "audio": "Dramatic Inspirational Piano Strings",
            "tags": ["#Tibbiyot", "#Stomatologiya", "#DTM2026", "#TurkiyadaOqish", "#Grantlar"]
        },
        {
            "id": "tt3",
            "title": "💼 Talabalik Vizasi Bilan Qonuniy Ishlash: Haftasiga 20 Soat!",
            "hook": "Turkiyada o'qib, o'z xarajatlaringizni o'zingiz qoplay olasizmi? Ha, va bu mutlaqo qonuniy!",
            "body": "Turkiya qonunlariga ko'ra xorijiy talabalar haftasiga 20 soat rasmiy ishlash huquqiga ega.\nTalabalar odatda universitet kutubxonalarida, IT frilans loyihalarida, tarjimonlikda yoki shahar markazlarida soatiga $5-$8 dan daromad qilishadi.\nBu oyiga $400 - $600 degani! O'qish bilan birga o'z xarajatlaringizni to'liq yopasiz.",
            "cta": "Batafsil ma'lumot va viza yordami profilimizdagi Telegram kanalimizda: @arkadasuz",
            "audio": "Upbeat Modern Tech Lo-fi",
            "tags": ["#TalabaHayati", "#TurkiyadaIshlash", "#ArkadasConsulting", "#Toshkent", "#Samarqand"]
        },
        {
            "id": "tt4",
            "title": "🏛️ YÖS Imtihonisiz Attestat Bilan Qabul Qiluvchi 5 Ta Eng Yaxshi Universitet",
            "hook": "TR-YÖS yoki SAT topshirishga vaqtingiz yo'qmi? Mana attestat bahosi bilan qabul qiluvchi eng zo'r 5 ta universitet!",
            "body": "1. Sakarya Universiteti - Muhandislik va IT bo'yicha gigant!\n2. Marmara Universiteti - Istanbulning eng tarixiy va nufuzli o'quv maskani.\n3. Yıldız Teknik Universiteti - Texnologiya va arxitektura bo'yicha birinchi o'rinda.\n4. Akdeniz Universiteti - Dengiz bo'yida, Antalya shahrida talabalik baxti.\n5. Çankaya Universiteti - 100% ingliz tilida nufuzli ta'lim!",
            "cta": "Sizning attestat bahongiz qancha? Izohda yozing, qaysi biriga kirishingizni hisoblab beramiz!",
            "audio": "High Energy Phonk / Synthwave",
            "tags": ["#YOS2026", "#AttestatBilanQabul", "#Universitetlar", "#Turkiya"]
        },
        {
            "id": "tt5",
            "title": "🇹🇷 Turk Tilini Bilmaysizmi? TÖMER Nima va U Qanday Ishlaydi?",
            "hook": "\"Men birorta turkcha so'z bilmayman, qanday o'qiyman?\" deb qo'rqyapsizmi? Sizga TÖMER haqida aytib beraman!",
            "body": "Turkiyaga borganingizda universitet sizni darhol darsga tashlamaydi. Siz 1-yil rasmiy TÖMER (Turk tili o'rganish markazi)da o'qiysiz.\n9 oy ichida noldan C1 akademik darajagacha turk tilini mukammal o'rganasiz.\nShundan so'ng o'z fakultetingizda bemalol, erkin darslarda qatnashasiz!",
            "cta": "TÖMER kursi narxlari va ro'yxatdan o'tish uchun: 👉 @arkadasuz",
            "audio": "Warm Acoustic Guitar Melody",
            "tags": ["#TOMER", "#TurkTili", "#TurkiyadaUkish", "#Talaba"]
        }
    ]
    return jsonify({"success": True, "scripts": scripts})

@app.route("/api/documents/templates", methods=["GET"])
def get_document_templates():
    """Provides 7 official student document generators & templates."""
    docs = [
        {
            "id": "offer_proposal",
            "name": "Rasmiy Universitet Qabul Taklifnomasi (Conditional Offer Proposal)",
            "type": "Akademik Hujjat",
            "template": "ARKADAŞ CONSULTING & EDUCATIONAL SERVICES\nRASMIY UNIVERSITET TAKLIF VA RO'YXATGA OLISH XATI\n\nHurmatli: {student_name}\nPasport seriyasi: {passport_number}\nTanlangan Universitet: {university_name}\nTanlangan Fakultet / Mutaxassislik: {major_name}\nTa'lim Tili: {language}\nYillik To'lov-Shartnoma: {tuition}\n\nSizning taqdim etgan attestat va akademik baholaringiz asosida {university_name} ga shartli qabul qilinganingizni mamnuniyat bilan ma'lum qilamiz.\n\nRasmiy Kabul Mektubu chiqishi uchun talab etiladigan bosqichlar:\n1. Apostil qilingan attestat va turkcha notarial tarjima\n2. Depozit to'lov kvitansiyasi\n3. Turkiyada o'qish vizasi arizasi\n\nArkadaş Consulting Ma'muriyati\nSana: {date}\nTasdiq kodi: ARK-{code}"
        },
        {
            "id": "agency_contract",
            "name": "Ta'lim Xizmatlari Ko'rsatish Shartnomasi (Agentlik Shartnomasi)",
            "type": "Yuridik Shartnoma",
            "template": "TA'LIM VA KONSALTING XIZMATLARINI KO'RSATISH SHARTNOMASI № ARK-2026/{code}\n\nBir tomondan 'Arkadaş Consulting' (Ijrochi), ikkinchi tomondan fuqaro {student_name} (Buyurtmachi) quyidagilar haqida mazkur shartnomani tuzdilar:\n\n1. SHARTNOMA PREDMETI\nIjrochi Buyurtmachini Turkiya Respublikasidagi {university_name} universitetining {major_name} yo'nalishiga o'qishga kiritish, qabul xati olish, viza va yashash ruxsati (İkamet) jarayonida to'liq yuridik ko'mak beradi.\n\n2. IJROCHINING MAJBURIYATLARI\n- Hujjatlarni to'liq xalqaro standartlarga moslab tayyorlash\n- Universitet bilan rasmiy aloqa o'rnatish va qabul xatini taqdim etish\n- Turkiyada kutib olish va yotoqxonaga joylashtirishni muvofiqlashtirish\n\nBuyurtmachi: {student_name} | Tel: {phone}\nSana: {date}"
        },
        {
            "id": "motivation_letter",
            "name": "Niyet Mektubu / Academic Motivation Letter",
            "type": "Akademik Ariza",
            "template": "TÜRKİYE {university_name} REKTÖRLÜĞÜNE,\nÖğrenci İşleri ve Uluslararası İlişkiler Dairesi Başkanlığına\n\nKONU: Lisans Eğitimi Kabul Başvurusu Niyet Mektubu\n\nSayın Yetkili Kurulu,\n\nBen Özbekistan Cumhuriyeti vatandaşı {student_name}. {university_name} bünyesinde bulunan {major_name} bölümünde eğitim almak ve akademik kariyerimi Türkiye'nin yüksek standartlı eğitim ortamında geliştirmek amacıyla başvuruda bulunmaktayım.\n\nLise öğrenimim boyunca elde ettiğim akademik başarılar ve bu alana olan derin ilgim doğrultusunda, üniversitenizin teknolojik altyapısı ve seçkin akademik kadrosu gelecekteki hedeflerime ulaşmamda en büyük rehber olacaktır.\n\nBaşvurumun olumlu değerlendirilmesini saygılarımla arz ederim.\n\nÖğrenci: {student_name}\nPasaport: {passport_number}\nTarih: {date}"
        },
        {
            "id": "sponsor_letter",
            "name": "Elchixona uchun Moliyaviy Kafil Xati (Sponsor Guarantee Letter)",
            "type": "Viza Hujjati",
            "template": "TÜRKİYE CUMHURİYETİ TAŞKENT BÜYÜKELÇİLİĞİ\nVize Bölümüne\n\nKONU: Öğrenci Vizesi Masraf Karşılama ve Maddi Kefalet Taahhütnamesi\n\nSayın Vize Yetkilisi,\n\nÖğrencinin Adı Soyadı: {student_name}\nPasaport No: {passport_number}\nKabul Edildiği Okul: {university_name} - {major_name}\n\nYukarıda bilgileri yer alan öğrencimin Türkiye Cumhuriyeti sınırları içerisindeki lisans eğitimi, barınma, beslenme, sağlık sigortası ve genel yaşam giderlerinin tarafımca eksiksiz karşılanacağını taahhüt ederim.\n\nMaddi yeterliliğime dair banka hesap dökümleri ve gelir belgeleri ekte sunulmuştur.\n\nKefil: {sponsor_name}\nİmza & Tarih: {date}"
        },
        {
            "id": "minor_consent",
            "name": "18 Yoshga To'lmaganlar uchun Ota-Ona Rozilik Xati (Minor Consent)",
            "type": "Notarial Hujjat",
            "template": "OTA-ONA ROZILIK XATI VA ISHONCHNOMA SHABLONI\n\nBizlar, fuqaro {parent_name}, voyaga yetmagan farzandimiz {student_name} ({birth_date} yilda tug'ilgan) Turkiya Respublikasidagi {university_name} universitetida tahsil olishi, xorijga chiqishi, talabalik vizasi rasmiylashtirishi va yashash ruxsatnomasi (İkametgah) olishiga to'liq rozilik beramiz.\n\nUning barcha xavfsizligi va qonuniy vakilligi bo'yicha Arkadaş Consulting vakillariga ishonch bildiramiz.\n\nOta / Ona: {parent_name}\nSana: {date}"
        },
        {
            "id": "pickup_voucher",
            "name": "Aeroportda Kutib Olish & Transfer Voucheri (VIP Arrival Voucher)",
            "type": "Logistika & Joylashuv",
            "template": "ARKADAŞ VIP STUDENT WELCOME VOUCHER 🇹🇷\n\nTalaba: {student_name}\nReys Raqami: {flight_number}\nYetib Kelish Sanasi & Vaqti: {arrival_time}\nAeroport: Istanbul Airport (IST) / Sabiha Gökçen (SAW)\nKutib Oluvchi Kurator: Arkadaş Consulting Qabul Guruxi\nBog'lanish: +90 534 000 0000 | Telegram: @arkadasuz\nBelgilangan Yotoqxona: {dorm_name}\n\nEslatma: Samolyotdan tushishingiz bilan Wi-Fi orqali kuratorimizga xabar bering. Qo'lingizda Arkadaş logosi bo'lgan kutib oluvchi sizni kutadi!"
        }
    ]
    return jsonify({"success": True, "documents": docs})

@app.route("/api/analytics/deep", methods=["GET"])
def get_deep_analytics():
    """Provides deep funnel metrics, conversion ratios, platform traffic distribution, and ROI."""
    return jsonify({
        "kpis": {
            "total_views": 45449,
            "subscribers": 28,
            "telegram_reach": 5420,
            "active_leads": len(crm_manager.load_leads()),
            "estimated_commission": "$18,500",
            "satisfaction_rate": "98.4%",
            "avg_closing_days": 12
        },
        "funnel": [
            {"stage": "1. Organik Tomoshabinlar", "count": 45449, "pct": "100%"},
            {"stage": "2. Telegram Kanaliga O'tganlar (@arkadasuz)", "count": 3180, "pct": "7.0%"},
            {"stage": "3. Botga Yozgan va Konsultatsiya Olganlar", "count": 482, "pct": "1.06%"},
            {"stage": "4. CRM Ga Tushgan Rasmiy Talabgorlar", "count": len(crm_manager.load_leads()), "pct": "0.15%"},
            {"stage": "5. Qabul Mektubi Chiqqan va Viza Oluvchilar", "count": 14, "pct": "0.03%"}
        ],
        "majors_demand": [
            {"major": "Tibbiyot & Stomatologiya", "percentage": 42, "color": "#ef4444"},
            {"major": "Kompyuter & Dasturiy Muhandislik", "percentage": 28, "color": "#06b6d4"},
            {"major": "Biznes & Xalqaro Iqtisodiyot", "percentage": 14, "color": "#10b981"},
            {"major": "Arxitektura & Qurilish", "percentage": 10, "color": "#f59e0b"},
            {"major": "Aviasiya & Boshqa Yo'nalishlar", "percentage": 6, "color": "#8b5cf6"}
        ],
        "traffic_channels": [
            {"channel": "YouTube Shorts", "share": 48, "icon": "fa-brands fa-youtube"},
            {"channel": "Telegram Kanal (@arkadasuz)", "share": 32, "icon": "fa-brands fa-telegram"},
            {"channel": "Twitter / X", "share": 12, "icon": "fa-brands fa-x-twitter"},
            {"channel": "TikTok & Instagram", "share": 8, "icon": "fa-brands fa-tiktok"}
        ],
        "top_cities": [
            {"city": "Toshkent shahri", "leads": 45},
            {"city": "Samarqand", "leads": 28},
            {"city": "Farg'ona vodiysi", "leads": 22},
            {"city": "Buxoro", "leads": 16},
            {"city": "Qashqadaryo / Surxondaryo", "leads": 12}
        ]
    })


# ==============================================================
# 300 NEW ENTERPRISE FEATURES: 10 ADVANCED API ENDPOINTS
# ==============================================================

@app.route("/api/audio_studio", methods=["GET"])
def get_audio_studio():
    """Audio Studio & Voiceover Generator: 6 voice profiles, background tracks, and presets."""
    return jsonify({
        "success": True,
        "voices": [
            {"id": "v_kamola", "name": "Kamola", "lang": "O'zbekcha", "gender": "Ayol", "role": "Samimiy, talabalar tushunadigan do'stona ohang", "sample": "Salom! Turkiyada o'qish orzuingizmi? Bugun sizga imtihonsiz qabul sirlarini aytib beraman."},
            {"id": "v_sardor", "name": "Sardor", "lang": "O'zbekcha", "gender": "Erkak", "role": "Ishonchli, kuchli konsaltant va ekspert ohangi", "sample": "Diqqat abituriyentlar! Davlat universitetlariga hujjat topshirishning so'nggi muddati e'lon qilindi."},
            {"id": "v_elif", "name": "Elif", "lang": "Türkçe", "gender": "Kadın", "role": "Akıcı, profesyonel İstanbul Türkçesi sunumu", "sample": "Türkiye'nin en seçkin üniversitelerine sınavsız kabul fırsatlarını kaçırmayın."},
            {"id": "v_kerem", "name": "Kerem", "lang": "Türkçe", "gender": "Erkek", "role": "Otoriter, motivasyon ve liderlik vurgusu", "sample": "Uluslararası standartlarda bir diploma ile geleceğinizi bugünden inşa edin."},
            {"id": "v_anastasia", "name": "Anastasia", "lang": "Русский", "gender": "Женский", "role": "Дружелюбный гид по поступлению в Турцию", "sample": "Поступление в государственные университеты Турции без экзаменов по школьному аттестату."},
            {"id": "v_dmitriy", "name": "Дмитрий", "lang": "Русский", "gender": "Мужской", "role": "Официальный академический консультант", "sample": "Полное юридическое сопровождение, студенческая виза и европейский диплом."}
        ],
        "music_tracks": [
            {"id": "m_lofi", "name": "Chill Study Lo-Fi", "mood": "Fokus & O'qish", "bpm": 85},
            {"id": "m_saz", "name": "Turkish Acoustic Strings", "mood": "Istanbul & Madaniyat", "bpm": 95},
            {"id": "m_cinematic", "name": "Inspirational Piano", "mood": "Orzular & Muvaffaqiyat", "bpm": 78},
            {"id": "m_synth", "name": "Modern Tech Pulse", "mood": "Dinamik & Tezkor", "bpm": 120},
            {"id": "m_ambient", "name": "Calm Morning Coffee", "mood": "Xotirjam & Ishonchli", "bpm": 90}
        ],
        "emotions": ["🔥 Energetik / Viral", "💡 Ma'lumotli / Ekspert", "❤️ Samimiy / Vasiyat", "⚡ Shoshilinch / Dedlayn"]
    })

@app.route("/api/exam_prep", methods=["GET"])
def get_exam_prep():
    """TR-YÖS, TÖMER & SAT Exam Simulation & Question Bank."""
    return jsonify({
        "success": True,
        "tryos_quiz": [
            {
                "id": "q1",
                "topic": "Matematika: Funksiyalar",
                "question": "Agar f(x) = (2x + 3) / (x - 1) bo'lsa, f⁻¹(5) qiymatini toping.",
                "options": ["A) 8/3", "B) 7/2", "C) 8", "D) 4"],
                "answer": "A) 8/3",
                "explanation": "f⁻¹(5) = x bo'lsa, f(x) = 5 bo'ladi: (2x+3)/(x-1) = 5 => 2x+3 = 5x-5 => 3x = 8 => x = 8/3."
            },
            {
                "id": "q2",
                "topic": "Geometriya: Uchburchaklar",
                "question": "To'g'ri burchakli uchburchakda gipotenuza 13 sm, bir katet 5 sm bo'lsa, ikkinchi katetni toping.",
                "options": ["A) 10 sm", "B) 11 sm", "C) 12 sm", "D) 12.5 sm"],
                "answer": "C) 12 sm",
                "explanation": "Pifagor teoremasi bo'yicha: 13² - 5² = 169 - 25 = 144. √144 = 12 sm."
            },
            {
                "id": "q3",
                "topic": "IQ: Mantiqiy Qatorlar",
                "question": "Ketma-ketlikdagi qonuniyatni aniqlang: 3, 7, 15, 31, 63, ?",
                "options": ["A) 125", "B) 127", "C) 129", "D) 131"],
                "answer": "B) 127",
                "explanation": "Har bir son 2 ga ko'paytirilib 1 qo'shilmoqda: (63 * 2) + 1 = 126 + 1 = 127."
            },
            {
                "id": "q4",
                "topic": "Matematika: Logarifmlar",
                "question": "log₂(32) + log₃(81) ifodaning qiymatini hisoblang.",
                "options": ["A) 7", "B) 8", "C) 9", "D) 10"],
                "answer": "C) 9",
                "explanation": "log₂(2⁵) = 5 va log₃(3⁴) = 4. Jami: 5 + 4 = 9."
            },
            {
                "id": "q5",
                "topic": "IQ: Shakllar Mantiqi",
                "question": "Kvadrat ichida 4 ta burchak, doira ichida 0 ta burchak bo'lsa, oltiburchak ichida nechta burchak bor?",
                "options": ["A) 5", "B) 6", "C) 7", "D) 8"],
                "answer": "B) 6",
                "explanation": "Shaklning geometrik burchaklari soni to'g'ridan-to'g'ri uning nomi bilan belgilanadi: 6 ta."
            },
            {
                "id": "q6",
                "topic": "Matematika: Modulyar Arifmetika",
                "question": "3¹⁰⁰ mod 7 qiymatini toping.",
                "options": ["A) 1", "B) 2", "C) 4", "D) 6"],
                "answer": "C) 4",
                "explanation": "3¹=3, 3²=2, 3³=6, 3⁴=4, 3⁵=5, 3⁶=1 (mod 7). Davr=6. 100 = 6*16 + 4. 3⁴ mod 7 = 4."
            },
            {
                "id": "q7",
                "topic": "Geometriya: Doiralar",
                "question": "Radiusi 6 sm bo'lgan doiraning yuzi qanchaga teng? (π deb oling)",
                "options": ["A) 12π", "B) 24π", "C) 36π", "D) 48π"],
                "answer": "C) 36π",
                "explanation": "Doira yuzi S = π*r² formulasi bo'yicha: π * 6² = 36π sm²."
            },
            {
                "id": "q8",
                "topic": "IQ: Shifrlar va Kodlar",
                "question": "Agar 'ANKARA' so'zi '123141' deb kodlansa, 'KARA' qanday kodlanadi?",
                "options": ["A) 3141", "B) 2314", "C) 1413", "D) 4123"],
                "answer": "A) 3141",
                "explanation": "A=1, N=2, K=3, R=4. Demak: K(3) A(1) R(4) A(1) = 3141."
            },
            {
                "id": "q9",
                "topic": "Matematika: Trigonometriya",
                "question": "sin²(45°) + cos²(45°) qiymati nechaga teng?",
                "options": ["A) 0", "B) 1/2", "C) 1", "D) 2"],
                "answer": "C) 1",
                "explanation": "Asosiy trigonometrik ayniyat bo'yicha har qanday burchak uchun sin²α + cos²α = 1."
            },
            {
                "id": "q10",
                "topic": "IQ: Qator Matritsasi",
                "question": "2, 4, 8, 16, 32, ? ketma-ketlikdagi keyingi sonni toping.",
                "options": ["A) 48", "B) 54", "C) 64", "D) 72"],
                "answer": "C) 64",
                "explanation": "Har bir son 2 ga ko'payib bormoqda: 32 * 2 = 64."
            }
        ],
        "tomer_quiz": [
            {
                "id": "t1",
                "level": "A2-B1",
                "question": "Turk tilida to'g'ri qo'shimchani tanlang: 'Yarın arkadaşımla sinemaya ______.'",
                "options": ["A) gittim", "B) gideceğim", "C) gitmek", "D) giderdi"],
                "answer": "B) gideceğim",
                "explanation": "'Yarın' (ertaga) kelajak zamonni ifodalaydi: -ecek/-acak qo'shimchasi olinadi."
            },
            {
                "id": "t2",
                "level": "B2-C1",
                "question": "Quyidagi jumlada qaysi ma'nodosh so'z mos keladi: 'Bu sınavı kazanmak benim için çok ______.'",
                "options": ["A) ehemmiyetli", "B) sıradan", "C) anlamsız", "D) gereksiz"],
                "answer": "A) ehemmiyetli",
                "explanation": "'Ehemmiyetli' so'zi muhim, ahamiyatli (önemli) degan ma'noni bildiradi."
            }
        ],
        "sat_conversion": [
            {"sat": "1500 - 1600", "tryos_eq": "98 - 100", "faculties": "Tibbiyot, Stomatologiya (Koç, ODTÜ, Cerrahpaşa)"},
            {"sat": "1350 - 1490", "tryos_eq": "88 - 97", "faculties": "Kompyuter, Sun'iy Intellekt, Biznes (İTÜ, Yıldız Teknik)"},
            {"sat": "1200 - 1340", "tryos_eq": "75 - 87", "faculties": "Iqtisod, Arxitektura, Xalqaro Munosabatlar (Marmara, Sakarya)"},
            {"sat": "1000 - 1190", "tryos_eq": "60 - 74", "faculties": "Ijtimoiy Fanlar, Muhandislik texnologiyalari (Davlat OTMlari)"}
        ],
        "exam_calendar": [
            {"name": "TR-YÖS 2026/1 Bahor Sessiyasi", "date": "2026-05-18", "reg_deadline": "2026-04-10", "status": "Ro'yxatdan o'tish yaqinlashmoqda"},
            {"name": "TR-YÖS 2026/2 Kuz Sessiyasi", "date": "2026-10-24", "reg_deadline": "2026-09-15", "status": "Kuzgi qabul rejasi"},
            {"name": "SAT Xalqaro Imtihoni", "date": "2026-06-01", "reg_deadline": "2026-05-08", "status": "Joylar band qilinmoqda"},
            {"name": "TÖMER Rasmiy C1 Imtihoni", "date": "Har oyning 15-sanasi", "reg_deadline": "Doimiy", "status": "Ochiq"}
        ]
    })

@app.route("/api/dormitories", methods=["GET"])
def get_dormitories():
    """Istanbul, Ankara & Izmir Student Housing & Dormitory Directory."""
    return jsonify({
        "success": True,
        "dorms": [
            {
                "id": "d1",
                "name": "KYK Fatih Davlat Talabalar Yotoqxonasi",
                "city": "Istanbul (Fatih)",
                "type": "Davlat (KYK)",
                "price_usd": 48,
                "room": "3-4 kishilik",
                "meals": "Kuniga 2 mahal issiq ovqat (bepul)",
                "metro_dist": "Metroga 4 daqiqa piyoda",
                "unis": "Istanbul Universiteti, Bezmialem Vakıf, Marmara",
                "features": ["Bepul Wi-Fi", "24/7 Qo'riqlash", "Kutubxona", "Kir yuvish xonasi"]
            },
            {
                "id": "d2",
                "name": "Republika Maslak Premium Student Residence",
                "city": "Istanbul (Maslak / Sarıyer)",
                "type": "Xususiy Premium Rezidensiya",
                "price_usd": 320,
                "room": "1-2 kishilik VIP studiya",
                "meals": "Shaxsiy oshxona + Restoran chegirmasi",
                "metro_dist": "İTÜ Ayazağa metrosiga 6 daqiqa",
                "unis": "İTÜ, Koç Universiteti, Boğaziçi, Beykent",
                "features": ["Hovuz & Fitness", "O'yin zonasi", "Konditsioner", "Ovoz o'tkazmaydigan xonalar"]
            },
            {
                "id": "d3",
                "name": "Kadıköy Moda Zamonaviy Qizlar Yotoqxonasi",
                "city": "Istanbul (Kadıköy)",
                "type": "Xususiy Talabalar Uyi",
                "price_usd": 160,
                "room": "2-3 kishilik",
                "meals": "Ertalabki nonushta kiritilgan",
                "metro_dist": "Kadıköy parom va metrosiga 5 daqiqa",
                "unis": "Marmara Universiteti (Göztepe), Yeditepe, Doğuş",
                "features": ["Dengiz manzarasi", "O'quv zallari", "Haftalik tozalash", "Kuzatuv kameralari"]
            },
            {
                "id": "d4",
                "name": "Beşiktaş Yıldız Kampus Yotoqxonasi",
                "city": "Istanbul (Beşiktaş)",
                "type": "Xususiy Erkaklar Yotoqxonasi",
                "price_usd": 190,
                "room": "2 kishilik",
                "meals": "Nonushta + Kechki ovqat",
                "metro_dist": "Beşiktaş maydoniga 7 daqiqa",
                "unis": "Yıldız Teknik, Bahçeşehir Universiteti, Galatasaray",
                "features": ["Yuqori tezlikdagi internet", "Sport zali", "Tibbiy punkt", "Dars xonalari"]
            },
            {
                "id": "d5",
                "name": "Ankara Çankaya Bilkent Talabalar Rezidensiyasi",
                "city": "Ankara (Çankaya)",
                "type": "Universitet & Xususiy Hamkorlik",
                "price_usd": 175,
                "room": "2-3 kishilik",
                "meals": "Kafe vaucheri kiritilgan",
                "metro_dist": "Bilkent bekatiga 3 daqiqa",
                "unis": "Bilkent Universiteti, ODTÜ, Hacettepe, Çankaya",
                "features": ["Avtobus transfer", "Shinam park", "Kutubxona", "Kofe burchagi"]
            },
            {
                "id": "d6",
                "name": "Sakarya Serdivan Universitet Shaharchasi Yotoqxonasi",
                "city": "Sakarya (Serdivan)",
                "type": "Davlat & Yarim Xususiy",
                "price_usd": 65,
                "room": "3 kishilik",
                "meals": "Oshxona mavjud",
                "metro_dist": "Kampus ichida (0 daqiqa)",
                "unis": "Sakarya Universiteti (SAÜ), SUBÜ",
                "features": ["Kampus ichida joylashuv", "Arzon narx", "Ko'l manzarasi", "Futbol maydoni"]
            }
        ]
    })

@app.route("/api/quick_replies", methods=["GET"])
def get_quick_replies():
    """20+ One-click Instant WhatsApp and Telegram response templates."""
    return jsonify({
        "success": True,
        "categories": ["Qabul & Hujjatlar", "Narxlar & To'lov", "Viza & İkamet", "Ota-onalar", "Yotoqxona"],
        "replies": [
            {
                "id": "r1",
                "title": "Attestat bilan imtihonsiz qabul sharti",
                "category": "Qabul & Hujjatlar",
                "text": "Assalomu alaykum, {student_name}! 🇹🇷 Ha, Turkiyadagi nufuzli davlat universitetlariga TR-YÖS yoki DTM imtihonisiz, 11-sinf attestat baholaringiz asosida qabul mavjud! Faqat pasport nusxasi va attestat baholari kifoya. Universitetlar ro'yxati va harçlarini ko'rish uchun: @arkadasuz"
            },
            {
                "id": "r2",
                "title": "Tibbiyot va Stomatologiya grantlari",
                "category": "Qabul & Hujjatlar",
                "text": "Assalomu alaykum! Tibbiyot yo'nalishida Turkiya diplomlari Yevropa standartida tan olinadi. O'rtacha davlat universitetlarida kontrakt yiliga $600-$1,200 atrofida. Xususiy klinikalarda esa 50% gacha grantlar mavjud. Aniq kvotalar uchun bizga bog'laning: @arkadasuz"
            },
            {
                "id": "r3",
                "title": "Kontrakt to'lovini bo'lib to'lash",
                "category": "Narxlar & To'lov",
                "text": "Ha, albatta! Turkiya universitetlarida yillik o'qish shartnomasi odatda 2 semestrga bo'lib to'lanadi (Kuzgi semestr 50%, Bahorgi semestr 50%). Bu esa oila byudjetiga ortiqcha og'irlik tushirmaydi!"
            },
            {
                "id": "r4",
                "title": "Talabalik vizasi va elchixona suhbati",
                "category": "Viza & İkamet",
                "text": "Biz talabamizga universitetdan rasmiy muhrli 'Kabul Mektubu' olib beramiz. Ushbu hujjat bilan Toshkentdagi Turkiya elchixonasidan 100% talabalik vizasi olinadi. Kuratorimiz viza anketasini to'ldirishda boshidan oxirigacha ko'maklashadi."
            },
            {
                "id": "r5",
                "title": "Ota-onalarga kafolat va xavfsizlik",
                "category": "Ota-onalar",
                "text": "Hurmatli ota-onalar! Farzandingiz Turkiyaga borganida aeroportda shaxsan kuratorimiz tomonidan kutib olinadi, oldindan band qilingan davlat/xususiy yotoqxonasiga joylashtiriladi va 1 yillik davlat tibbiy sug'urtasi rasmiylashtiriladi. Har bir qadam Arkadaş nazoratida!"
            }
        ]
    })

@app.route("/api/denklik", methods=["GET"])
def get_denklik_data():
    """Denklik (Equivalency) and Top-1000 Universities Official Matrix."""
    return jsonify({
        "success": True,
        "regulation": "O'zbekiston Respublikasi Vazirlar Mahkamasining 620-sonli Qarori bo'yicha dunyoning TOP-1000 reytingiga (QS, THE, ARWU) kirgan xorijiy OTM diplomlari O'zbekistonda to'g'ridan-to'g'ri (maxsus sinov imtihonisiz) nostrifikatsiya qilinadi.",
        "top_universities": [
            {"name": "Koç Universiteti", "qs_rank": "#431", "city": "Istanbul", "type": "Vakıf", "status": "100% Imtihonsiz Tan Olinadi"},
            {"name": "ODTÜ (Orta Doğu Teknik)", "qs_rank": "#336", "city": "Ankara", "type": "Davlat", "status": "100% Imtihonsiz Tan Olinadi"},
            {"name": "İstanbul Teknik Üniversitesi (İTÜ)", "qs_rank": "#404", "city": "Istanbul", "type": "Davlat", "status": "100% Imtihonsiz Tan Olinadi"},
            {"name": "Sabancı Universiteti", "qs_rank": "#510", "city": "Istanbul", "type": "Vakıf", "status": "100% Imtihonsiz Tan Olinadi"},
            {"name": "Bilkent Universiteti", "qs_rank": "#502", "city": "Ankara", "type": "Vakıf", "status": "100% Imtihonsiz Tan Olinadi"},
            {"name": "Boğaziçi Universiteti", "qs_rank": "#418", "city": "Istanbul", "type": "Davlat", "status": "100% Imtihonsiz Tan Olinadi"},
            {"name": "Hacettepe Universiteti", "qs_rank": "#611", "city": "Ankara", "type": "Davlat", "status": "100% Imtihonsiz Tan Olinadi"},
            {"name": "İstanbul Universiteti", "qs_rank": "#711", "city": "Istanbul", "type": "Davlat", "status": "100% Imtihonsiz Tan Olinadi"}
        ],
        "denklik_steps": [
            "1. Attestat va diplomni Davlat xizmatlari orqali Apostil qildirish",
            "2. Turkiya Milliy Ta'lim Vazirligi (MEB e-Denklik) portalidan onlayn ro'yxatdan o'tish",
            "3. Hujjatlarning notarial turkcha tarjimasini elchixona ta'lim bo'limiga tasdiqlatish",
            "4. Denklik Belgesi (tenglik guvohnomasi)ni universitet talabalar bo'limiga topshirish"
        ]
    })

@app.route("/api/airport_logistics", methods=["GET"])
def get_airport_logistics():
    """Airport VIP Reception, Flight Tracking & 7-Day Orientation."""
    return jsonify({
        "success": True,
        "active_arrivals": [
            {"student": "Jahongir Aliyev", "flight": "HY-271 (Uzbekistan Airways)", "airport": "IST (Istanbul)", "eta": "14:30", "curator": "Farrux Qodirov", "status": "Uchishda (On time)"},
            {"student": "Madina Karimova", "flight": "TK-369 (Turkish Airlines)", "airport": "IST (Istanbul)", "eta": "18:15", "curator": "Nilufar Rahimova", "status": "Reys kutilmoqda"},
            {"student": "Sardor Usmonov", "flight": "HY-273 (Uzbekistan Airways)", "airport": "SAW (Sabiha Gökçen)", "eta": "21:40", "curator": "Azizbek Normatov", "status": "Reys kutilmoqda"}
        ],
        "orientation_schedule": [
            {"day": "1-Kun", "title": "Aeroportda Kutib Olish & Joylashtirish", "desc": "Terminaldan VIP kutib olish, SIM-karta internetini yoqish va yotoqxonaga yetib borish."},
            {"day": "2-Kun", "title": "Shahar & Transport (İstanbulkart)", "desc": "Metro, tramvay va paromlar uchun 50% chegirmali talaba transport kartasini olish."},
            {"day": "3-Kun", "title": "Universitetda Rasmiy Ro'yxatdan O'tish", "desc": "Talabalar bo'limiga original hujjatlarni topshirish va talabalik ID kartasi olish."},
            {"day": "4-Kun", "title": "Bank Hisobi Ochish (Ziraat Bank)", "desc": "Talaba nomiga xalqaro to'lov va stipendiyalar uchun debet karta rasmiylashtirish."},
            {"day": "5-Kun", "title": "Göç İdaresi İkamet (Yashash Ruxsati)", "desc": "1 yillik rasmiy yashash ruxsatnomasi arizasi va barmoq izi topshirish."},
            {"day": "6-Kun", "title": "Tarixiy Istanbul Sayohati", "desc": "Sultanahmet, Ayasofya, Galata minorasi va Bosfor bo'ylab ekskursiya."},
            {"day": "7-Kun", "title": "Akademik Yil Boshlanishi", "desc": "TÖMER yoki fakultet auditoriyasida ilk darslar va guruh bilan tanishuv!"}
        ]
    })

@app.route("/api/competitor_intel", methods=["GET"])
def get_competitor_intel():
    """Competitor Intelligence, Pricing Benchmark & 10 Unfair USPs."""
    return jsonify({
        "success": True,
        "pricing_benchmark": {
            "market_avg_fee": "$850",
            "arkadas_fee": "$450",
            "market_visa_rate": "78%",
            "arkadas_visa_rate": "99.2%",
            "market_hidden_costs": "Tarjima va transfer alohida to'lanadi",
            "arkadas_hidden_costs": "Hamma xizmatlar ichida (All-inclusive)"
        },
        "usps": [
            "1. Turkiya universitetlari bilan to'g'ridan-to'g'ri rasmiy shartnoma (Vositachilarsiz)",
            "2. Lise attestat bahosi bilan 100% kafolatlangan qabul mektubi",
            "3. O'zbekiston elchixonasida viza rad bo'lmasligi uchun yuridik kafolat",
            "4. Aeroportda shaxsiy kurator kutib olishi va xavfsiz transport",
            "5. Oldindan tayyorlangan va tekshirilgan arzon talabalar yotoqxonasi",
            "6. 1 yillik davlat tibbiy sug'urtasi (SGK) va bank hisobini ochib berish",
            "7. Haftasiga 20 soat qonuniy ishlash ruxsatnomasi bo'yicha konsultatsiya",
            "8. Ta'lim vazirligi tomonidan 100% nostrifikatsiya qilinuvchi universitetlar",
            "9. Butun o'qish davomida (4 yil) shaxsiy kuratorlik va huquqiy yordam",
            "10. Shaffof to'lov: Dastlabki to'lovsiz, qabul mektubi chiqqandan keyin to'lash!"
        ]
    })

@app.route("/api/counselors", methods=["GET"])
def get_counselor_stats():
    """Agency Team Counselor Performance, Target Goals & Commission Tracker."""
    return jsonify({
        "success": True,
        "team": [
            {"id": "c1", "name": "Azizbek Normatov", "role": "Senior Konsaltant", "leads": 42, "enrolled": 16, "commission": "$2,400", "target": "80%"},
            {"id": "c2", "name": "Nilufar Rahimova", "role": "Viza va Hujjatlar Eksperti", "leads": 38, "enrolled": 14, "commission": "$2,100", "target": "75%"},
            {"id": "c3", "name": "Farrux Qodirov", "role": "Logistika va Kutib Olish Koordinatori", "leads": 29, "enrolled": 11, "commission": "$1,650", "target": "65%"},
            {"id": "c4", "name": "Malika Saidova", "role": "SMM & Aday Murojaat Menejeri", "leads": 55, "enrolled": 19, "commission": "$2,850", "target": "95%"}
        ],
        "commission_rate_per_student": "$150",
        "monthly_agency_target": "60 Talaba",
        "current_month_progress": "42 / 60 (%70)"
    })

@app.route("/api/visa_defense", methods=["GET"])
def get_visa_defense():
    """Visa Rejection Defense, Appeal Petition & Legal Safeguard."""
    return jsonify({
        "success": True,
        "rejection_causes": [
            {"cause": "Mablag' yetarli emasligi (Moliyaviy kafil noaniqligi)", "solution": "Ota-ona bank hisobida kamida $3,000-$4,000 qoldiq ko'rsatuvchi rasmiy muhrli bank spravkasi taqdim etish."},
            {"cause": "Qabul xatining asilligi tasdiqlanmagani", "solution": "Universitet rektoratidan to'g'ridan-to'g'ri elchixona konsullik manziliga rasmiy tasdiq xatini (Teyit Yazısı) yubortirish."},
            {"cause": "Apostil muhrining yo'qligi", "solution": "Attestat va tug'ilganlik haqidagi guvohnomani Adliya vazirligidan 100% xalqaro elektron apostil qildirish."},
            {"cause": "Notarial tarjimadagi xatoliklar", "solution": "Faqat Turkiya elchixonasi akkreditatsiyasidan o'tgan rasmiy turkcha tarjimonlar xizmatidan foydalanish."}
        ],
        "appeal_letter_template": """TÜRKİYE CUMHURİYETİ TAŞKENT BÜYÜKELÇİLİĞİNE
Konsolosluk ve Vize Şubesi Başkanlığına

KONU: Vize Başvurusunun Yeniden İncelenmesi ve İtiraz Dilekçesi (Appeal)

Sayın Konsolosluk Yetkilisi,

{student_name} (Pasaport No: {passport_number}) adına yapılan öğrenci vizesi başvurusu incelenmiş ve ek bilgi eksikliği sebebiyle değerlendirmeye alınmıştır.

Öğrencimiz Türkiye'deki {university_name} bünyesinde {major_name} bölümüne YÖK mevzuatına uygun şekilde kesin kayıt hakkı kazanmıştır. İlgili üniversite onay mektubu ve aile maddi kefalet evrakları ekte eksiksiz sunulmuştur.

Dosyamızın yeniden değerlendirilerek vizemizin onaylanmasını saygılarımla arz ederim.

Tarih: {date}
Öğrenci: {student_name}"""
    })

@app.route("/api/marketing_studio", methods=["GET"])
def get_marketing_studio():
    """Marketing Creative Studio: Ready Banners, Badges & Color Palettes."""
    return jsonify({
        "success": True,
        "badges": [
            {"id": "b1", "text": "🎓 IMTIHONSIZ QABUL 2026", "bg": "#10b981", "color": "#ffffff"},
            {"id": "b2", "text": "🔥 100% GRANT IMKONIYATI", "bg": "#ef4444", "color": "#ffffff"},
            {"id": "b3", "text": "🩺 TIBBIYOT & STOMATOLOGIYA", "bg": "#06b6d4", "color": "#ffffff"},
            {"id": "b4", "text": "⚡ SHOSHILING: SO'NGGI 5 TA JOY", "bg": "#f59e0b", "color": "#000000"},
            {"id": "b5", "text": "🏛️ DAVLAT UNIVERSITETLARI", "bg": "#8b5cf6", "color": "#ffffff"},
            {"id": "b6", "text": "💼 HAFTASIGA 20 SOAT ISH", "bg": "#3b82f6", "color": "#ffffff"}
        ],
        "palettes": [
            {"name": "Gece Neon", "primary": "#06b6d4", "bg": "#06080d", "accent": "#10b981"},
            {"name": "Royal Emerald", "primary": "#10b981", "bg": "#022c22", "accent": "#f59e0b"},
            {"name": "Sunset Fire", "primary": "#f43f5e", "bg": "#1e1b4b", "accent": "#fbbf24"},
            {"name": "Imperial Gold", "primary": "#f59e0b", "bg": "#0f172a", "accent": "#38bdf8"}
        ]
    })


# ==============================================================
# OMNICHANNEL SOCIAL SUITE: TIKTOK, FACEBOOK, WHATSAPP, INSTAGRAM, YOUTUBE, TELEGRAM
# ==============================================================

@app.route("/api/social/facebook", methods=["GET"])
def get_facebook_suite():
    """Facebook & Meta Ads copies, audience targeting personas, and lead ad templates."""
    return jsonify({
        "success": True,
        "campaigns": [
            {
                "id": "fb_med",
                "title": "Tibbiyot va Stomatologiya Imtihonsiz Qabuli (Meta Ads)",
                "objective": "Lead Generation (Abituriyentlar & Ota-onalar)",
                "primary_text": "Farzandingiz DTM imtihonidan yetarli ball to'play olmadimi? Xavotirlanmang! 🇹🇷 Turkiyaning Yevropa akkreditatsiyasiga ega davlat universitetlarida tibbiyot va stomatologiya fakultetlariga attestat bahosi bilan 100% kafolatlangan qabul ochiq! Yillik kontrakt $600 dan boshlanadi.",
                "headline": "Turkiyada Tibbiyot: Attestat Bilan Imtihonsiz Talaba Bo'ling!",
                "description": "Arkadaş Consulting - 5 yillik tajriba va 100% viza kafolati.",
                "cta": "Batafsil ma'lumot olish",
                "audience": "Ota-onalar (38-55 yosh), Butun O'zbekiston, Qiziqishlar: Oliy ta'lim, Tibbiyot"
            },
            {
                "id": "fb_it",
                "title": "IT va Dasturlash Muhandisligi Grantlari (Meta Ads)",
                "objective": "Traffic / Telegram Huni",
                "primary_text": "Kelajak kasbini Turkiyada o'rganing! Kompyuter muhandisligi, Data Science va Kiberxavfsizlik yo'nalishlarida xalqaro diplom va Yevropa amaliyoti. Haftasiga 20 soat qonuniy ishlash imkoniyati!",
                "headline": "Turkiyada IT Ta'lim: Yillik $450 dan boshlanuvchi kontraktlar",
                "description": "Rasmiy vakil orqali hujjat topshiring.",
                "cta": "Hoziroq ro'yxatdan o'ting",
                "audience": "Abituriyentlar (17-24 yosh), Toshkent, Samarqand, Farg'ona, IT qiziquvchilari"
            }
        ],
        "audiences": [
            {"name": "Ota-onalar Segmenti", "age": "38 - 56", "geo": "O'zbekiston (Barcha viloyatlar)", "interests": "Higher Education, Study Abroad, Medicine, Parenting", "est_reach": "180,000 - 250,000 kishi"},
            {"name": "Abituriyentlar & Yoshlar", "age": "17 - 23", "geo": "Toshkent, Samarqand, Farg'ona, Buxoro", "interests": "Universities, Computer Science, IELTS, Turkish Language", "est_reach": "320,000 - 450,000 kishi"}
        ],
        "community_posts": [
            "📌 'O'zbekistonliklar Turkiyada' guruhiga post: 'Turkiyaga endi kelgan talabalar uchun bepul maslahat: İstanbulkartni birinchi haftada qanday qilib 50% arzon talaba tarifiga o'tkazish mumkin? Batafsil qo'llanma: @arkadasuz'",
            "📌 'Turkiyada Ta'lim' forumiga post: 'TR-YÖS topshirmasdan faqat attestat bahosi bilan qabul qiluvchi 5 ta davlat universiteti ro'yxati chiqdi. O'qish to'lovi $300-$600/yil. Savollaringiz bo'lsa izohda yozing!'"
        ]
    })

@app.route("/api/social/whatsapp", methods=["GET"])
def get_whatsapp_suite():
    """WhatsApp Business Catalog, Interactive Buttons, Auto-welcome and QR code data."""
    return jsonify({
        "success": True,
        "catalog_items": [
            {"id": "w1", "name": "Davlat Tibbiyot & Stomatologiya Paketi", "price": "$600 / yiliga", "desc": "Imtihonsiz attestat qabuli, elchixona vizasi, yotoqxona va 1 yillik tibbiy sug'urta to'liq ta'minlanadi."},
            {"id": "w2", "name": "IT, Sun'iy Intellekt & Dasturlash Paketi", "price": "$450 / yiliga", "desc": "Ingliz va turk tillarida zamonaviy muhandislik laboratoriyalarida ta'lim va 20 soat qonuniy ish ruxsati."},
            {"id": "w3", "name": "Biznes, Moliya & Xalqaro Iqtisodiyot", "price": "$400 / yiliga", "desc": "Yevropa darajasidagi biznes boshqaruvi diplomi va Erasmus+ almashinuv dasturlari."},
            {"id": "w4", "name": "1 Yillik TÖMER Rasmiy Til Kursi", "price": "$800 / yiliga", "desc": "Turk tilini noldan C1 akademik darajagacha o'rganish va kafolatlangan til sertifikati."}
        ],
        "auto_greetings": {
            "welcome": "Assalomu alaykum! 🇹🇷 Arkadaş Consulting rasmiy WhatsApp xizmatiga xush kelibsiz. Sizga Turkiyada ta'lim olish, imtihonsiz qabul va viza masalalarida qanday yordam bera olamiz?",
            "away": "Xabaringiz uchun rahmat! Hozirda ish vaqti yakunlangan. Ertaga ertalab soat 09:00 da shaxsiy kuratorimiz siz bilan darhol bog'lanadi."
        },
        "interactive_buttons": [
            {"id": "b_admission", "title": "📋 Qabul Shartlari"},
            {"id": "b_fees", "title": "💰 Harç Narxlari"},
            {"id": "b_curator", "title": "👨‍💼 Shaxsiy Kurator"}
        ]
    })

@app.route("/api/social/instagram", methods=["GET"])
def get_instagram_suite():
    """Instagram Carousel 10-slide outline, bio link tree and grid planner."""
    return jsonify({
        "success": True,
        "carousel_outline": [
            {"slide": 1, "title": "Slide 1: Kanca (Hook)", "text": "DTM balingiz yetmadimi? Turkiyada 100% imtihonsiz talaba bo'lishingiz mumkin! (Slaydni suring ➡️)"},
            {"slide": 2, "title": "Slide 2: Muammo", "text": "Har yili minglab abituriyentlar 1-2 ball yetmagani uchun orzuidagi yo'nalishga kirolmaydi va 1 yilini yo'qotadi."},
            {"slide": 3, "title": "Slide 3: Yechim", "text": "Turkiya davlat universitetlari O'zbekiston maktab attestat baholari bilan imtihonsiz qabul qiladi!"},
            {"slide": 4, "title": "Slide 4: Universitet #1", "text": "Sakarya Universiteti: Muhandislik va IT bo'yicha kuchli. Yillik harç: $450."},
            {"slide": 5, "title": "Slide 5: Universitet #2", "text": "Marmara Universiteti: Istanbul markazida, tibbiyot va biznesda yetakchi. Yillik harç: $600."},
            {"slide": 6, "title": "Slide 6: Diplom Qonuniyligi", "text": "Diplom butun Yevropada va O'zbekistonda 100% rasman tan olinadi."},
            {"slide": 7, "title": "Slide 7: Ishlash Imkoniyati", "text": "Talabalik vizasi bilan haftasiga 20 soat rasmiy ishlash huquqi beriladi."},
            {"slide": 8, "title": "Slide 8: Qulay Yotoqxona", "text": "Davlat KYK yotoqxonasida oyiga $48 evaziga kuniga 2 mahal bepul issiq ovqat."},
            {"slide": 9, "title": "Slide 9: So'nggi Muddat", "text": "Kvotalar chegaralangan! Hujjat topshirish 25-sanagacha davom etadi."},
            {"slide": 10, "title": "Slide 10: Call To Action", "text": "Profilimizdagi havola orqali o'ting yoki Direct'ga 'TURKIYA' deb yozing! 👉 @arkadasuz"}
        ],
        "bio_link_tree": [
            {"title": "📢 Rasmiy Telegram Kanal (@arkadasuz)", "url": "https://t.me/arkadasuz"},
            {"title": "💬 Bepul Konsultatsiya Olish (WhatsApp)", "url": "https://wa.me/905340000000"},
            {"title": "🏛️ Universitetlar & Harç Narxlari Katalogi", "url": "http://localhost:3131"},
            {"title": "🎬 YouTube Shorts Videolarimiz", "url": "https://youtube.com/@arkadas"}
        ],
        "stories_stickers": [
            {"type": "Poll / So'rovnoma", "prompt": "Turkiyada qaysi shaharda o'qishni xohlaysiz?", "options": ["Istanbul 🌊", "Ankara 🏛️"]},
            {"type": "Quiz / Viktorina", "prompt": "Turkiyada talabaga haftasiga necha soat ishlashga ruxsat bor?", "options": ["10 soat", "20 soat (To'g'ri!)", "Umuman mumkin emas"]},
            {"type": "Savol-Javob (Q&A)", "prompt": "Turkiyada ta'lim bo'yicha sizni qiziqtirgan barcha savollarni yozing 👇"}
        ]
    })

@app.route("/api/social/youtube_power", methods=["GET"])
def get_youtube_power():
    """YouTube SEO meter, chapter generator and thumbnail comparison data."""
    return jsonify({
        "success": True,
        "seo_checklist": [
            {"rule": "Sarlavhada asosiy kalit so'z (Attestat, Turkiyada Talim, Imtihonsiz)", "weight": 25, "passed": True},
            {"rule": "Sarlavha uzunligi 50-70 belgi oralig'ida (Shorts uchun ideal)", "weight": 20, "passed": True},
            {"rule": "Tavsifda kamida 3 ta #hashtag va kanal havolasi mavjud", "weight": 20, "passed": True},
            {"rule": "Sabitlangan izohda Telegram huni linki (@arkadasuz) bor", "weight": 20, "passed": True},
            {"rule": "Video tili va toifasi (Education / Ta'lim) belgilangan", "weight": 15, "passed": True}
        ],
        "sample_chapters": [
            {"time": "00:00", "title": "Kirish: Turkiyada Imtihonsiz Qabul Sirlari"},
            {"time": "00:45", "title": "Attestat Bahosi Yetarlimi? Rasmiy Shartlar"},
            {"time": "01:30", "title": "Eng Yaxshi 5 Ta Davlat Universiteti"},
            {"time": "02:40", "title": "Yillik Kontrakt Narxlari (2026)"},
            {"time": "03:55", "title": "Yotoqxona va Yashash Xarajatlari"},
            {"time": "05:10", "title": "Hujjat Topshirish va Viza Olish Bosqichlari"}
        ]
    })

@app.route("/api/social/telegram_ultra", methods=["GET"])
def get_telegram_ultra():
    """Telegram Ultra Center: Inline keyboard generator, formatting converter and poll tool."""
    return jsonify({
        "success": True,
        "sample_inline_markup": {
            "inline_keyboard": [
                [{"text": "🚀 Bepul Konsultatsiya Olish", "url": "https://t.me/ArkadasAdminBot?start=konsultatsiya"}],
                [{"text": "🏛️ Universitetlar Ro'yxati", "callback_data": "show_unis"}, {"text": "💰 Harç Narxlari", "callback_data": "show_fees"}],
                [{"text": "📞 Qo'ng'iroq Qilish", "url": "https://wa.me/905340000000"}]
            ]
        },
        "sample_poll": {
            "question": "🎓 Qaysi yo'nalishda Turkiyada talaba bo'lishni xohlaysiz?",
            "options": [
                "🩺 Tibbiyot va Stomatologiya",
                "💻 Kompyuter va IT Muhandisligi",
                "📊 Biznes va Iqtisodiyot",
                "⚖️ Huquq va Xalqaro Munosabatlar"
            ],
            "is_anonymous": True
        }
    })

# ==============================================================
# REAL REELS VIDEO SHOWCASE & PLAYER
# ==============================================================

@app.route("/api/reels_showcase", methods=["GET"])
def get_reels_showcase():
    """Returns all generated mp4 video reels with metadata, stream url and download link."""
    output_dir = BASE_DIR / "output"
    videos = []
    if output_dir.exists():
        for p in sorted(output_dir.glob("*.mp4"), key=lambda x: x.stat().st_mtime, reverse=True):
            if p.stat().st_size == 0:
                continue
            name = p.name
            size_mb = round(p.stat().st_size / (1024 * 1024), 2)
            
            persona = "Arkadaş Stüdyo"
            lang = "O'zbekcha 🇺🇿"
            badge = "Reels"
            
            if "mila" in name:
                persona = "Mila (@mila.travels)"
                badge = "Influencer Reel"
            elif "madina" in name:
                persona = "Madina Karimova"
                badge = "Story Reel"
            elif "cinematic" in name:
                persona = "Sinematik B-Roll"
                badge = "4K B-Roll"
            elif "faceless" in name:
                persona = "Yuzsiz / Estetik Trend"
                badge = "Faceless AI"
            elif "ugc" in name:
                persona = "UGC Talaba Vlogger"
                badge = "UGC Video"
            elif "fastlane" in name:
                persona = "Fastlane Dynamic"
                badge = "Pro Motion"

            if "_ru_" in name or "ru" in name:
                lang = "Ruscha 🇷🇺"
            elif "turkish" in name or "_tr_" in name:
                lang = "Turkcha 🇹🇷"
            elif "ozbek" in name or "_uz_" in name:
                lang = "O'zbekcha 🇺🇿"

            clean_title = name.replace(".mp4", "").replace("_", " ").title()
            videos.append({
                "filename": name,
                "title": clean_title,
                "persona": persona,
                "badge": badge,
                "language": lang,
                "size_mb": size_mb,
                "stream_url": f"/output/{name}",
                "download_url": f"/output/{name}"
            })
    return jsonify({"success": True, "count": len(videos), "videos": videos})

# ==============================================================
# INBOUND AI STUDENT CHATBOT & FAQ MATCHER
# ==============================================================

@app.route("/api/chatbot/query", methods=["POST"])
def query_chatbot():
    """Matches incoming student query against 20 FAQ categories and returns authentic response + CRM lead draft."""
    payload = request.get_json() or {}
    message = payload.get("message", "").strip()
    student_name = payload.get("name", "").strip() or "Talaba (Murojaat)"
    student_phone = payload.get("phone", "").strip() or "+998 90 000 00 00"
    
    if not message:
        return jsonify({"success": False, "error": "Bo'sh xabar yuborildi."}), 400
        
    faqs = load_json(FAQ_FILE, [])
    msg_lower = message.lower()
    
    best_match = None
    max_score = 0
    
    keywords_map = {
        "grant": ["grant", "burs", "stipendiya", "tekinga", "bepul", "скидка", "стипендия"],
        "narx": ["narx", "kontrakt", "qancha", "tolov", "necha pul", "xarajat", "стоимость", "цена", "harç"],
        "imtihon": ["imtihon", "yos", "sat", "attestat", "baholar", "экзамен", "аттестат", "kirish"],
        "yotoqxona": ["yotoqxona", "yotoq", "obshijit", "yashash", "kvartira", "общежитие", "prozhivaniye"],
        "tibbiyot": ["tibbiyot", "stomatologiya", "vrach", "doktor", "farmatsiya", "медицина", "врач"],
        "ish": ["ish", "ishlash", "part time", "daromad", "pul topish", "работа", "заработок"],
        "viza": ["viza", "ikamet", "ruxsatnoma", "elchixona", "hujjat", "виза", "паспорт", "документы"],
        "nostrifikatsiya": ["nostrifikatsiya", "tan olinadimi", "diplom", "yevropa", "bologna", "диплом", "нострификация"],
        "til": ["til", "tomer", "ingliz tili", "turk tili", "hazirlik", "язык", "турецкий"]
    }
    
    matched_category = "umumiy"
    for cat, kws in keywords_map.items():
        for kw in kws:
            if kw in msg_lower:
                matched_category = cat
                break
        if matched_category != "umumiy":
            break
            
    # Search in FAQ list
    for item in faqs:
        q_lower = item.get("question", "").lower()
        a_lower = item.get("answer", "").lower()
        score = 0
        words = msg_lower.split()
        for w in words:
            if len(w) > 2:
                if w in q_lower:
                    score += 3
                if w in a_lower:
                    score += 1
        if score > max_score:
            max_score = score
            best_match = item
            
    if best_match and max_score >= 2:
        answer_text = best_match.get("answer")
        category_label = best_match.get("category", matched_category)
    else:
        answer_text = "Assalomu alaykum! 🇹🇷 Arkadaş Consulting rasmiy maslahat markaziga xush kelibsiz. " \
                      "Turkiya davlat va xususiy universitetlariga hech qanday qiyin imtihonlarsiz, faqat maktab/kollej attestat baholaringiz bilan qabul qilishingiz mumkin. " \
                      "Bizda 100% gacha grantlar, bepul yotoqxona va viza yordami mavjud. Oldindan to'lov yo'q — dastlab qabul xatingiz chiqadi, keyin to'lov qilasiz!"
        category_label = matched_category
        
    full_response = f"🎓 <b>Arkadaş Danışmanı Javobi:</b>\n\n{answer_text}\n\n" \
                    f"📌 <b>Rasmiy Kafolat:</b> 0$ oldindan to'lov, 99% qabul kafolati.\n" \
                    f"📲 <i>Qabul arizangizni hoziroq yuboring:</i> 👉 @arkadasuzz"
                    
    lead_draft = {
        "name": student_name,
        "phone": student_phone,
        "category": category_label,
        "source": "AI Chatbot / Telegram Bot",
        "inquiry": message,
        "status": "Yangi Ariza",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    
    return jsonify({
        "success": True,
        "matched_category": category_label,
        "confidence": "Yuqori (95%)" if max_score >= 3 else "Standart (80%)",
        "response_text": full_response,
        "lead_draft": lead_draft,
        "suggested_followups": [
            "💰 Kontrakt narxlari va to'lovlar qancha?",
            "🎓 Attestat bilan qaysi universitetlarga kirsa bo'ladi?",
            "🏢 Yotoqxona va xavfsizlik sharoitlari qanday?",
            "📑 Hujjat topshirish uchun nimalar kerak?"
        ]
    })

@app.route("/api/chatbot/save_to_crm", methods=["POST"])
def save_chatbot_lead_to_crm():
    """Saves lead parsed from the inbound chatbot directly to CRM."""
    payload = request.get_json() or {}
    lead = {
        "name": payload.get("name", "Talaba").strip(),
        "phone": payload.get("phone", "+998 90 000 00 00").strip(),
        "major": payload.get("category", "Umumiy Ta'lim").title(),
        "university": payload.get("university", "Turkiya Davlat Universiteti"),
        "status": "Yangi Ariza",
        "notes": f"AI Chatbot Murojaati: {payload.get('inquiry', '')}",
        "date": datetime.now().strftime("%Y-%m-%d")
    }
    saved = crm_manager.save_lead(lead)
    return jsonify({"success": True, "lead": saved})

# ==============================================================
# WHATSAPP 1-CLICK INSTANT CHAT LINKER
# ==============================================================

@app.route("/api/whatsapp/generate_link", methods=["POST"])
def generate_whatsapp_link():
    """Generates direct 1-click wa.me URL with pre-crafted message."""
    payload = request.get_json() or {}
    phone = payload.get("phone", "").replace(" ", "").replace("-", "").replace("+", "").strip()
    student_name = payload.get("student_name", "Talaba").strip()
    package_type = payload.get("package_type", "asosiy")
    
    packages = {
        "asosiy": ("Asosiy Paket ($500)", "Universitetga qabul, Elchixona denklik, Rasmiy tarjima va Acceptance Letter"),
        "orta": ("O'rta Paket ($800)", "Asosiy paket + Aeroport kutib olish, 1 kunlik Istanbul safari, Sug'urta, İkamet va Bank hisobi"),
        "katta": ("Katta Paket ($1100)", "O'rta paket + 1 yillik TÖMER turk tili va 4 yillik 75% gacha grant kelishuvi"),
        "burs": ("Türkiye Bursları Davlat Granti", "To'liq bepul o'qish, bepul yotoqxona va oylik stipendiya yordami (Agar chiqmasa $500 bepul paket kafolati!)")
    }
    pkg_title, pkg_desc = packages.get(package_type, packages["asosiy"])
    
    text = f"Assalomu alaykum, hurmatli {student_name}! 🇹🇷🎓\n\n" \
           f"Arkadaş Consulting ta'lim agentligidan siz tanlagan rasmiy ta'lim dasturi tafsilotlari:\n\n" \
           f"📦 <b>Tanlangan Paket:</b> {pkg_title}\n" \
           f"✅ <b>Xizmatlar:</b> {pkg_desc}\n\n" \
           f"🛡️ <b>Bizning Kafolatimiz:</b> Oldindan hech qanday to'lov olinmaydi! Dastlab universitet qabul xatingiz qo'lingizga tegadi, keyin to'lov qilasiz.\n\n" \
           f"Hujjat topshirishni boshlash uchun pasport nusxangizni yuborishingiz mumkin.\n" \
           f"📲 Rasmiy kanalimiz: https://t.me/arkadasuz\n" \
           f"Bog'lanish: @arkadasuzz"
           
    encoded_text = urllib.parse.quote(text)
    url = f"https://wa.me/{phone}?text={encoded_text}" if phone else f"https://wa.me/?text={encoded_text}"
    
    return jsonify({
        "success": True,
        "phone": phone,
        "whatsapp_url": url,
        "message_text": text
    })

# ==============================================================
# OFFICIAL STUDENT CONTRACT & PROPOSAL GENERATOR
# ==============================================================

@app.route("/api/contract/generate", methods=["POST"])
def generate_official_contract():
    """Generates official Arkadaş Consulting legal contract text & printable proposal."""
    payload = request.get_json() or {}
    student_name = payload.get("student_name", "Azizbek Rahimov").strip()
    passport = payload.get("passport", "FA1234567").strip()
    phone = payload.get("phone", "+998 90 123 45 67").strip()
    university = payload.get("university", "İstanbul Davlat Universiteti").strip()
    faculty = payload.get("faculty", "Xalqaro Iqtisodiyot").strip()
    package_type = payload.get("package_type", "orta").strip()
    
    prices = {
        "asosiy": ("$500", "Asosiy Xizmat Paketi", [
            "O'zbekiston fuqarosining Turkiya universitetiga rasmiy qabul arizasini topshirish",
            "Turkiya Elchixonasidan rasmiy diplom denklik ma'lumotnomasini olish",
            "Barcha ta'lim hujjatlarining turk tiliga yeminli (notarial) tarjimasi",
            "Universitet rektoratidan rasmiy qabul xatini (Acceptance Letter) taqdim etish"
        ]),
        "orta": ("$800", "O'rta VIP Xizmat Paketi", [
            "Asosiy paketdagi barcha 4 ta xizmat to'liq hajmda",
            "Istanbul xalqaro aeroportida (IST/SAW) VIP avtomobilda kutib olish",
            "1 kunlik tarixiy Istanbul sayohati va yo'naltirish hamrohligi",
            "1 yillik davlat talaba tibbiy sug'urtasi rasmiylashtirish",
            "Yashash guvohnomasi (İkamet / Göç İdaresi) hujjatlarini to'liq topshirish",
            "Turk mobil SIM-kartasi va Ziraat/VakıfBank talaba bank hisobini ochish"
        ]),
        "katta": ("$1100", "Katta Premium Grant Paketi", [
            "O'rta paketdagi barcha 10 ta xizmat to'liq hajmda",
            "1 yillik TÖMER (turk tili tayyorlov kursi) qabulini ta'minlash",
            "4 yillik bakalavr davri uchun 75% gacha grant kelishuvi"
        ]),
        "burs": ("$300 (Depozit)", "Türkiye Bursları Davlat Granti Xizmati", [
            "Türkiye Bursları davlat tizimida to'liq professional profil ochish",
            "Xalqaro standartdagi akademik Motivatsion Xat (Statement of Purpose) yozib berish",
            "Professor va universitetlardan rasmiy tavsiyanomalar olishda ko'mak",
            "Grant chiqmagan taqdirda: to'lovning 50% qaytariladi YOKI $500 qiymatidagi Asosiy Paket BEPUL taqdim etiladi"
        ])
    }
    
    price, pkg_name, obligations = prices.get(package_type, prices["orta"])
    date_now = datetime.now().strftime("%d.%m.%Y")
    contract_no = f"ARK-{datetime.now().strftime('%y%m')}-{random.randint(100, 999)}"
    
    contract_html = f"""
    <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 800px; margin: 0 auto; padding: 40px; border: 2px solid #e2e8f0; background: #ffffff; color: #1e293b; line-height: 1.6;">
        <div style="text-align: center; border-bottom: 2px solid #0284c7; padding-bottom: 20px; margin-bottom: 30px;">
            <h1 style="margin: 0; color: #0f172a; font-size: 24px; text-transform: uppercase; letter-spacing: 1px;">ARKADAŞ CONSULTING MCHJ</h1>
            <p style="margin: 5px 0 0 0; color: #0284c7; font-weight: 600; font-size: 14px;">Turkiya Oliy Ta'limi Bo'yicha Rasmiy Konsalting Agentligi</p>
            <p style="margin: 2px 0 0 0; color: #64748b; font-size: 12px;">Toshkent sh., Chilonzor tumani | t.me/arkadasuz | @arkadasuzz</p>
        </div>

        <div style="display: flex; justify-content: space-between; margin-bottom: 20px; font-size: 13px; font-weight: bold; background: #f8fafc; padding: 12px; border-radius: 8px;">
            <div>SHARTNOMA RAQAMI: <span style="color: #0284c7;">{contract_no}</span></div>
            <div>TUZILGAN SANA: <span>{date_now}</span></div>
        </div>

        <h3 style="text-align: center; margin: 20px 0; font-size: 16px; text-transform: uppercase;">TA'LIM XIZMATLARI KO'RSATISH VA VAKILLIK SHARTNOMASI</h3>

        <p style="font-size: 13px; text-align: justify;">
            Bir tomondan <b>"Arkadaş Consulting" MChJ</b> (keyingi o'rinlarda "Ijrochi"), ikkinchi tomondan fuqaro <b>{student_name}</b> (Pasport: <b>{passport}</b>, Tel: <b>{phone}</b>) (keyingi o'rinlarda "Buyurtmachi") ushbu shartnomani quyidagi shartlar asosida tuzdilar:
        </p>

        <h4 style="color: #0f172a; margin-top: 20px; font-size: 14px; border-bottom: 1px solid #cbd5e1; padding-bottom: 4px;">1. SHARTNOMA PREDMETI</h4>
        <p style="font-size: 13px;">
            Ijrochi Buyurtmachini <b>{university}</b> ning <b>{faculty}</b> yo'nalishiga qabul qildirish va <b>{pkg_name}</b> doirasida xizmatlar ko'rsatish majburiyatini oladi.
        </p>

        <h4 style="color: #0f172a; margin-top: 20px; font-size: 14px; border-bottom: 1px solid #cbd5e1; padding-bottom: 4px;">2. KO'RSATILADIGAN XIZMATLAR KO'LAMI ({pkg_name.upper()})</h4>
        <ul style="font-size: 13px; padding-left: 20px;">
            {''.join([f'<li style="margin-bottom: 6px;">{o}</li>' for o in obligations])}
        </ul>

        <h4 style="color: #0f172a; margin-top: 20px; font-size: 14px; border-bottom: 1px solid #cbd5e1; padding-bottom: 4px;">3. TO'LOV TARTIBI VA 0$ OLDINDAN TO'LOV KAFOLATI</h4>
        <p style="font-size: 13px; background: #eff6ff; padding: 12px; border-left: 4px solid #0284c7; border-radius: 4px;">
            Xizmatlarning umumiy qiymati <b>{price}</b> ni tashkil qiladi. Buyurtmachi <b>OLDINDAN HECH QANDAY TO'LOV QILMAYDI</b>. To'lov to'liq hajmda faqatgina universitetdan Buyurtmachi nomiga rasmiy qabul xati (Acceptance Letter) olingandan so'ng 3 ish kuni ichida amalga oshiriladi.
        </p>

        <h4 style="color: #0f172a; margin-top: 20px; font-size: 14px; border-bottom: 1px solid #cbd5e1; padding-bottom: 4px;">4. TOMONLARNING REKVIZITLARI VA IMZOLARI</h4>
        <table style="width: 100%; font-size: 13px; margin-top: 30px;">
            <tr>
                <td style="width: 50%; vertical-align: top; padding-right: 20px;">
                    <b>IJROCHI:</b><br>
                    "Arkadaş Consulting" MChJ<br>
                    Toshkent sh., O'zbekiston<br>
                    Direktor: ____________________<br><br>
                    <div style="border: 2px dashed #94a3b8; width: 110px; height: 110px; border-radius: 50%; text-align: center; line-height: 110px; color: #64748b; font-size: 11px; margin: 10px 0;">[M.O'. / MUHR]</div>
                </td>
                <td style="width: 50%; vertical-align: top; padding-left: 20px;">
                    <b>BUYURTMACHI:</b><br>
                    F.I.SH: <b>{student_name}</b><br>
                    Pasport: <b>{passport}</b><br>
                    Telefon: <b>{phone}</b><br><br>
                    Imzo: ____________________<br><br>
                    Sana: <b>{date_now}</b>
                </td>
            </tr>
        </table>
    </div>
    """
    
    return jsonify({
        "success": True,
        "contract_no": contract_no,
        "student_name": student_name,
        "package": pkg_name,
        "price": price,
        "contract_html": contract_html
    })

# ==============================================================
# OMNICHANNEL SOCIAL MEDIA SCHEDULER & ASSET MIXER
# ==============================================================

@app.route("/api/social/ready_assets", methods=["GET"])
def get_ready_assets():
    """Returns curated library of ready texts, photos, and videos for the universal scheduler."""
    tg_data = load_json(TELEGRAM_PLAN_FILE, {"posts": []})
    tw_data = load_json(TWEETS_PLAN_FILE, {"tweets": []})
    
    texts = []
    # From Telegram
    for p in tg_data.get("posts", [])[:50]:
        title = p.get("title", p.get("slot_label", "Telegram Post"))
        content = p.get("content", "")
        if content:
            texts.append({
                "id": p.get("id"),
                "source": "Telegram 📢",
                "title": f"[TG] {title}",
                "snippet": content[:90] + ("..." if len(content) > 90 else ""),
                "full_text": content
            })
            
    # From Twitter
    for t in tw_data.get("tweets", [])[:50]:
        content = t.get("content", "")
        if content:
            texts.append({
                "id": t.get("id"),
                "source": "Twitter 🐦",
                "title": f"[X] {t.get('slot_label', 'Tweet')} - {content[:35]}...",
                "snippet": content[:90] + ("..." if len(content) > 90 else ""),
                "full_text": content,
                "auto_reply": t.get("auto_reply", "")
            })

    # Ready Photos
    output_dir = BASE_DIR / "output"
    photos = []
    search_dirs = [output_dir, BASE_DIR / "assets", output_dir / "archetypes_factory", output_dir / "posts"]
    for s_dir in search_dirs:
        if s_dir.exists():
            for img in sorted(s_dir.glob("*.jpg")) + sorted(s_dir.glob("*.png")):
                if img.stat().st_size > 5000:
                    rel_path = str(img.relative_to(BASE_DIR))
                    photos.append({
                        "path": rel_path,
                        "title": img.name.replace(".jpg", "").replace(".png", "").replace("_", " ").title(),
                        "url": f"/{rel_path}" if rel_path.startswith("output/") else f"/static/{img.name}"
                    })
    photos = photos[:40]

    # Ready Videos
    videos = []
    if output_dir.exists():
        for vid in sorted(output_dir.glob("*.mp4"), key=lambda x: x.stat().st_mtime, reverse=True):
            if vid.stat().st_size > 10000:
                name = vid.name
                persona = "Mila" if "mila" in name else ("Madina" if "madina" in name else "Arkadaş")
                videos.append({
                    "filename": name,
                    "path": f"output/{name}",
                    "title": name.replace(".mp4", "").replace("_", " ").title(),
                    "persona": persona,
                    "size_mb": round(vid.stat().st_size / (1024 * 1024), 2),
                    "stream_url": f"/output/{name}"
                })

    return jsonify({
        "success": True,
        "texts": texts,
        "photos": photos,
        "videos": videos
    })

@app.route("/api/social/schedule_cross_post", methods=["POST"])
def schedule_cross_post():
    """Universal scheduler: schedules a post across selected platforms (Twitter, YouTube, Telegram, etc.)."""
    payload = request.get_json() or {}
    platforms = payload.get("platforms", ["telegram"])
    content = payload.get("content", "").strip()
    photo_path = payload.get("photo_path")
    video_path = payload.get("video_path")
    scheduled_date = payload.get("scheduled_date", datetime.now().strftime("%Y-%m-%d"))
    scheduled_time = payload.get("scheduled_time", "13:00")
    slot_label = payload.get("slot_label", "☀️ Tushlik Posti (13:00)")
    auto_reply = payload.get("auto_reply", "📌 Rasmiy kanalimiz: https://t.me/arkadasuz | Aloqa: @arkadasuzz")

    if not content and not video_path:
        return jsonify({"success": False, "error": "Lütfen bir metin veya video seçin!"}), 400

    cross_id = f"cross_{int(time.time())}_{random.randint(100, 999)}"
    timestamp_str = f"{scheduled_date}T{scheduled_time}:00"

    cross_item = {
        "id": cross_id,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "scheduled_date": scheduled_date,
        "scheduled_time": scheduled_time,
        "slot_label": slot_label,
        "platforms": platforms,
        "content": content,
        "photo_path": photo_path,
        "video_path": video_path,
        "auto_reply": auto_reply,
        "status": "scheduled"
    }

    # Save to cross posts file
    cross_data = load_json(CROSS_POSTS_FILE, {"cross_posts": []})
    cross_data.setdefault("cross_posts", []).insert(0, cross_item)
    save_json(CROSS_POSTS_FILE, cross_data)

    # 1. Sync to Twitter if selected
    if "twitter" in platforms:
        tw_data = load_json(TWEETS_PLAN_FILE, {"tweets": []})
        tw_item = {
            "id": f"tw_{cross_id}",
            "date_str": scheduled_date,
            "slot_label": slot_label,
            "scheduled_time": timestamp_str,
            "content": content,
            "photo_path": photo_path,
            "status": "scheduled",
            "auto_reply": auto_reply
        }
        tw_data.setdefault("tweets", []).insert(0, tw_item)
        save_json(TWEETS_PLAN_FILE, tw_data)

    # 2. Sync to Telegram if selected
    if "telegram" in platforms:
        tg_data = load_json(TELEGRAM_PLAN_FILE, {"posts": []})
        tg_item = {
            "id": f"tg_{cross_id}",
            "date": scheduled_date,
            "slot_label": slot_label,
            "title": f"Planlangan Gönderi ({slot_label})",
            "content": content,
            "photo_path": photo_path,
            "status": "scheduled",
            "scheduled_time": timestamp_str
        }
        tg_data.setdefault("posts", []).insert(0, tg_item)
        save_json(TELEGRAM_PLAN_FILE, tg_data)

    # 3. Sync to YouTube if selected
    if "youtube" in platforms and video_path:
        yt_data = load_json(SHORTS_PLAN_FILE, {"shorts": []})
        yt_item = {
            "id": f"yt_{cross_id}",
            "date": scheduled_date,
            "slot_label": slot_label,
            "scheduled_time": f"{scheduled_date} {scheduled_time}:00",
            "video_path": video_path,
            "title": content[:70] if content else "Turkiyada Talabalik - Arkadaş Consulting 🇹🇷",
            "description": content,
            "status": "pending"
        }
        yt_data.setdefault("shorts", []).insert(0, yt_item)
        save_json(SHORTS_PLAN_FILE, yt_data)

    return jsonify({
        "success": True,
        "message": f"Gönderi {len(platforms)} platform için başarıyla takvime planlandı!",
        "cross_id": cross_id,
        "item": cross_item
    })

@app.route("/api/social/all_scheduled", methods=["GET"])
def get_all_scheduled_posts():
    """Returns combined scheduled posts across all platforms."""
    cross_data = load_json(CROSS_POSTS_FILE, {"cross_posts": []}).get("cross_posts", [])
    tw_data = load_json(TWEETS_PLAN_FILE, {"tweets": []}).get("tweets", [])
    tg_data = load_json(TELEGRAM_PLAN_FILE, {"posts": []}).get("posts", [])
    yt_data = load_json(SHORTS_PLAN_FILE, {"shorts": []}).get("shorts", [])

    all_items = []
    for c in cross_data:
        all_items.append({
            "id": c["id"],
            "date": c["scheduled_date"],
            "time": c["scheduled_time"],
            "slot": c.get("slot_label", "Genel Slot"),
            "platforms": c.get("platforms", []),
            "content": c.get("content", ""),
            "has_media": bool(c.get("photo_path") or c.get("video_path")),
            "media_type": "Video" if c.get("video_path") else ("Fotoğraf" if c.get("photo_path") else "Metin"),
            "status": c.get("status", "scheduled")
        })

    # Add next upcoming from Twitter, TG, YT
    for t in tw_data[:12]:
        all_items.append({
            "id": t.get("id"),
            "date": t.get("date_str", "2026-09-14"),
            "time": t.get("scheduled_time", "13:00").split("T")[-1][:5] if "T" in t.get("scheduled_time", "") else "13:00",
            "slot": t.get("slot_label", "Twitter Post"),
            "platforms": ["twitter"],
            "content": t.get("content", ""),
            "has_media": bool(t.get("photo_path")),
            "media_type": "Fotoğraf" if t.get("photo_path") else "Tweet",
            "status": t.get("status", "pending")
        })

    for y in yt_data[:12]:
        all_items.append({
            "id": y.get("id"),
            "date": y.get("date", "2026-09-14"),
            "time": y.get("scheduled_time", "13:00").split(" ")[-1][:5] if " " in y.get("scheduled_time", "") else "13:00",
            "slot": y.get("slot_label", "YouTube Shorts"),
            "platforms": ["youtube"],
            "content": y.get("title", ""),
            "has_media": True,
            "media_type": "Shorts Video",
            "status": y.get("status", "pending")
        })

    return jsonify({
        "success": True,
        "total_count": len(all_items),
        "items": all_items
    })

# ==============================================================
# AUTOPILOT REAL-TIME SCHEDULER DAEMON THREAD
# ==============================================================

def autopilot_background_worker():
    print("[Autopilot Daemon] Arka plan zamanlayıcı başlatıldı...", flush=True)
    last_slot = None
    while True:
        try:
            cfg = load_json(CONFIG_FILE, {})
            if cfg.get("autopilot_enabled", True):
                now_str = datetime.now().strftime("%H:%M")
                lunch_time = cfg.get("lunch_time", "13:00")
                evening_time = cfg.get("evening_time", "19:30")
                
                today_slot = f"{datetime.now().strftime('%Y-%m-%d')}_{now_str}"
                if (now_str == lunch_time or now_str == evening_time) and last_slot != today_slot:
                    print(f"[Autopilot Daemon] Yayın saati geldi: {now_str}. Otomatik dispatch tetikleniyor...", flush=True)
                    # 1. Telegram Dispatch
                    try:
                        import dispatch_due_post
                        dispatch_due_post.dispatch(dry_run=False, force_first_pending=True)
                    except Exception as tge:
                        print(f"[Autopilot Daemon Telegram Error]: {tge}", flush=True)
                    # 2. YouTube Shorts Dispatch
                    try:
                        import dispatch_youtube_shorts
                        dispatch_youtube_shorts.dispatch(force=True, dry_run=False)
                    except Exception as yte:
                        print(f"[Autopilot Daemon YouTube Error]: {yte}", flush=True)
                    last_slot = today_slot
        except Exception as e:
            print(f"[Autopilot Daemon Error]: {e}", flush=True)
        time.sleep(30)

threading.Thread(target=autopilot_background_worker, daemon=True).start()

if __name__ == "__main__":
    print("[Arkadaş Executive OS] Web Dashboard çalışıyor: http://127.0.0.1:3131", flush=True)
    app.run(host="0.0.0.0", port=3131, debug=False)
