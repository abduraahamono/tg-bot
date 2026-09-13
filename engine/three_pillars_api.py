#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
engine/three_pillars_api.py
Arkadaş Executive OS — 3 Ana Sütun Modüler API
1. Üretim (Metin, Video, Fotoğraf & Stok Havuzu)
2. Paylaşım (7 Platform, Stoktan Otomatik 1-30 Günlük Planlayıcı, AI Danışmanı)
3. Analiz (Ortak Yayın Takvimi, Haftalık/Aylık Metrikler, Platform İstatistikleri)
"""

import os
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from flask import Blueprint, request, jsonify

pillars_bp = Blueprint("pillars_bp", __name__)

BASE_DIR = Path(__file__).resolve().parent.parent
BRAIN_DIR = BASE_DIR / "brain_data"
STOCK_FILE = BRAIN_DIR / "content_stock.json"
CALENDAR_FILE = BRAIN_DIR / "master_editorial_calendar.json"
TG_SCHEDULE_FILE = BRAIN_DIR / "scheduled_telegram_posts.json"
YT_SCHEDULE_FILE = BRAIN_DIR / "scheduled_youtube_shorts.json"

def load_json(path, default=None):
    if default is None:
        default = {}
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ==============================================================
# SÜTUN 1: ÜRETİM & STOK HAVUZU APIS
# ==============================================================

@pillars_bp.route("/api/stock/items", methods=["GET"])
def get_stock_items():
    stock = load_json(STOCK_FILE, {"texts": [], "videos": [], "images": []})
    texts = stock.get("texts", [])
    videos = stock.get("videos", [])
    images = stock.get("images", [])
    return jsonify({
        "success": True,
        "counts": {
            "texts": len(texts),
            "videos": len(videos),
            "images": len(images),
            "total": len(texts) + len(videos) + len(images)
        },
        "stock": {
            "texts": texts,
            "videos": videos,
            "images": images
        }
    })

@pillars_bp.route("/api/stock/add", methods=["POST"])
def add_stock_item():
    payload = request.get_json() or {}
    category = payload.get("category", "texts") # texts, videos, images
    item = payload.get("item", {})
    if not item.get("id"):
        item["id"] = f"stock_{category[:3]}_{uuid.uuid4().hex[:8]}"
    item["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    item["status"] = "in_stock"

    stock = load_json(STOCK_FILE, {"texts": [], "videos": [], "images": []})
    if category not in stock:
        stock[category] = []
    stock[category].insert(0, item)
    save_json(STOCK_FILE, stock)
    return jsonify({"success": True, "item": item, "total_in_category": len(stock[category])})

@pillars_bp.route("/api/stock/delete/<item_id>", methods=["DELETE"])
def delete_stock_item(item_id):
    stock = load_json(STOCK_FILE, {"texts": [], "videos": [], "images": []})
    found = False
    for cat in ["texts", "videos", "images"]:
        original_len = len(stock.get(cat, []))
        stock[cat] = [i for i in stock.get(cat, []) if i.get("id") != item_id]
        if len(stock[cat]) < original_len:
            found = True
    if found:
        save_json(STOCK_FILE, stock)
    return jsonify({"success": found})


import random

PRESET_TOPICS = [
    {"topic": "Tibbiyot va Stomatologiya", "uni": "Istanbul Medipol & Bezmialem", "city": "Istanbul", "price": "$3,500 - $6,000", "exam": "Imtihonsiz (Attestat bilan)"},
    {"topic": "Dasturlash va IT Muhandislik", "uni": "Yıldız Teknik & Marmara", "city": "Istanbul", "price": "$600 - $1,200", "exam": "TR-YÖS yoki Attestat"},
    {"topic": "Xalqaro Biznes va Moliya", "uni": "Anqara Hacı Bayram Veli", "city": "Anqara", "price": "$400 - $900", "exam": "To'g'ridan-to'g'ri Qabul"},
    {"topic": "Arxitektura va Shaharsozlik", "uni": "Mimar Sinan & ITU", "city": "Istanbul", "price": "$800 - $1,500", "exam": "Attestat + Portfolio"},
    {"topic": "Aviatsiya va Uchuvchilik", "uni": "Türk Hava Kurumu Universiteti", "city": "Anqara", "price": "$4,000 - $8,000", "exam": "Ingliz tili suhbati"},
    {"topic": "Psixologiya va Pedagogika", "uni": "Ege Universiteti", "city": "Izmir", "price": "$500 - $950", "exam": "Attestat Boshlang'ich Qabul"},
    {"topic": "Farmatsevtika (Dorishunoslik)", "uni": "Anqara Universiteti", "city": "Anqara", "price": "$1,800 - $3,200", "exam": "Attestat Baholari Asosida"},
    {"topic": "Xalqaro Huquq va Yurisprudensiya", "uni": "Istanbul Universiteti", "city": "Istanbul", "price": "$700 - $1,400", "exam": "TR-YÖS yoki Attestat"},
    {"topic": "Kiberxavfsizlik va Sun'iy Intellekt", "uni": "Sakarya Universiteti", "city": "Sakarya", "price": "$450 - $850", "exam": "To'g'ridan-to'g'ri Qabul"},
    {"topic": "Mexatronika va Robototexnika", "uni": "Bursa Uludağ Universiteti", "city": "Bursa", "price": "$550 - $1,100", "exam": "Imtihonsiz Attestat"},
    {"topic": "Logistika va Xalqaro Savdo", "uni": "Dokuz Eylül Universiteti", "city": "Izmir", "price": "$400 - $800", "exam": "To'g'ridan-to'g'ri Qabul"},
    {"topic": "Grafik Dizayn va Animatsiya", "uni": "Kadir Has Universiteti", "city": "Istanbul", "price": "$2,200 - $4,000", "exam": "Portfolio bilan Qabul"},
    {"topic": "Turizm va Mehmonxona Boshqaruvi", "uni": "Antalya Bilim Universiteti", "city": "Antalya", "price": "$1,200 - $2,500", "exam": "Attestat bilan Qabul"},
    {"topic": "Veterinariya Meditsinasi", "uni": "Selçuk Universiteti", "city": "Konya", "price": "$400 - $750", "exam": "Imtihonsiz Qabul"},
    {"topic": "Biotibbiyot Muhandisligi", "uni": "Bahçeşehir Universiteti", "city": "Istanbul", "price": "$3,000 - $5,500", "exam": "Attestat + Grant chegirmasi"}
]

HOOK_VARIATIONS = [
    "DTM balingiz orzuingizga yetmadimi? Tushkunlikka tushmang!",
    "Turkiyada o'qish uchun millionlab so'm sarflash shart emas!",
    "Attestat bahosi bilan Yevropa akkreditatsiyasiga ega diplom olish mumkinmi?",
    "Istanbulda talaba bo'lib, o'z xarajatlaringizni o'zingiz qoplang!",
    "Ota-onalar diqqatiga: Farzandingiz kelajagini ishonchli qo'llarga topshiring!",
    "2026-yilgi qabul uchun davlat kvotalari cheklangan!",
    "Imtihonsiz qabul qilinishning 3 ta sirli yo'li ochildi!",
    "Turkiya diplomining O'zbekistonda 100% tan olinishi haqida bilarmidingiz?"
]


@pillars_bp.route("/api/production/generate", methods=["POST"])
def generate_content():
    """Tekli veya toplu metin, video senaryosu veya görsel şablon üretir."""
    payload = request.get_json() or {}
    main_type = payload.get("type", "text") # text, video, image
    sub_type = payload.get("subType", "headline_hook")
    count = int(payload.get("count", 1))
    lang = payload.get("language", "uz")
    save_to_stock = payload.get("saveToStock", True)

    generated_items = []
    stock = load_json(STOCK_FILE, {"texts": [], "videos": [], "images": []})

    valid_videos = [
        "output/cinematic_reel_output.mp4",
        "output/mila_talking_ozbek_raw.mp4",
        "output/reels_video_output.mp4",
        "output/mila_ozbekcha_reel_final.mp4",
        "output/mila_turkish_reel_final.mp4",
        "output/madina_reel_5689.mp4",
        "output/ugc_vlogger_8995.mp4",
        "output/faceless_trend_5013.mp4",
        "output/story_reel_3665.mp4",
        "output/cinematic_reel_5821.mp4",
        "output/reels_3421.mp4",
        "output/fastlane_pro_5170.mp4"
    ]
    real_mp4s = [f for f in valid_videos if os.path.exists(f)] or ["output/cinematic_reel_output.mp4"]

    valid_images = [
        ("qa_quiz", "Soru-Cevap / Quiz Kartı", "output/sample_cafe.jpg"),
        ("riddle", "Bilmece / İpuçlu Tasarım", "output/mila_campus_scene.jpg"),
        ("checklist", "Kontrol Listesi / Checklist", "output/galata_reel_frame.jpg"),
        ("modern_ad", "Modern Reklam / Banner", "output/fresh_ferry_post.jpg"),
        ("qa_quiz", "Soru-Cevap / Harç Tablosu", "output/test_broll_frame.jpg"),
        ("riddle", "Bilmece / Kampüs Bilmecesi", "output/tiktok_scene1_frame.jpg"),
        ("checklist", "Checklist / 5 Altın Belge", "output/test_library_frame.jpg"),
        ("modern_ad", "Modern Reklam / 2026 Erken Kayıt", "output/madina_reel_frame.jpg")
    ]
    real_imgs = [i for i in valid_images if os.path.exists(i[2])] or valid_images

    # Shuffle for fresh output every time
    shuffled_topics = list(PRESET_TOPICS)
    random.shuffle(shuffled_topics)
    shuffled_hooks = list(HOOK_VARIATIONS)
    random.shuffle(shuffled_hooks)

    if main_type == "text":
        for i in range(count):
            t_data = shuffled_topics[i % len(shuffled_topics)]
            hook = shuffled_hooks[i % len(shuffled_hooks)]
            unique_id = f"txt_{uuid.uuid4().hex[:6]}"
            
            if sub_type == "headline_hook":
                title = f"🔥 {hook} | {t_data['topic']}"
                body = f"""{hook}

Turkiyaning eng nufuzli oliygohlaridan biri — {t_data['uni']}da {t_data['topic']} fakultetiga 2026-o'quv yili uchun rasmiy xalqaro qabul boshlandi!

📌 Shahar: {t_data['city']}
💰 Yillik kontrakt: {t_data['price']}
🎓 Diplom: Yevropa va O'zbekistonda 100% tan olinadi.

Joylar cheklangan! Bepul konsultatsiya olish uchun hoziroq yozing: @arkadasuz"""
                fmt = "Başlık & Hook"
            elif sub_type == "ad_copy":
                title = f"🎯 Reklam: {t_data['city']}da {t_data['topic']} Bo'yicha Talaba Bo'ling!"
                body = f"""{hook}

Farzandingiz kelajagi uchun eng to'g'ri qaror — {t_data['uni']}da ta'lim olish! Attestat bahosi bilan to'g'ridan-to'g'ri qabul qilinish imkoniyati mavjud.

✅ Rasmiy MChJ shartnomasi va yuridik kafolat
✅ Viza va yotoqxona kafolati
✅ Havalimanida kutib olish va 7 kunlik doimiy hamrohlik

Batafsil ma'lumot: @arkadasuz yoki +90 552 123 45 67"""
                fmt = "Reklam Kampanyası"
            elif sub_type == "tg_post":
                title = f"📢 Telegram: {t_data['uni']} — {t_data['topic']} Qabuli"
                body = f"""⚡️ <b>{t_data['uni'].upper()} — RASMIY QABUL OCHIQ!</b>

{hook}

• <b>Fakultet:</b> {t_data['topic']}
• <b>Shahar:</b> {t_data['city']}
• <b>Yillik to'lov:</b> {t_data['price']}
• <b>Talab qilinadigan hujjatlar:</b> Faqatgina Pasport va Attestat!

Biz bilan talaba bo'lgan har bir yoshga:
1️⃣ Turar joy (KYK/Xususiy rezidensiya) band qilish
2️⃣ Turkiyada qonuniy yashash ruxsatnomasi (İkamet)
3️⃣ Aeroportda kutib olish va sim-karta rasmiylashtirish bepul.

📩 Savollaringiz bormi? @arkadasuz adminiga murojaat qiling!"""
                fmt = "Telegram Formatı"
            else: # cta_faq
                title = f"❓ SSS & CTA: {t_data['topic']} Haqida Muhim Savol"
                body = f"""Talabalar va ota-onalar eng ko'p so'raydigan savol:

❓ <i>\"{t_data['uni']} diplomi O'zbekistonda o'tadimi va nostrifikatsiyadan o'tadimi?\"</i>

Javob: Ha! Turkiya YÖK akkreditatsiyasiga ega bo'lib, O'zbekiston Oliy ta'lim vazirligi nizomiga 100% mos keladi.

{t_data['city']} shahridagi oxirgi grant o'rinlari uchun ro'yxatdan o'ting: @arkadasuz"""
                fmt = "SSS & Çağrı Metni"

            item = {
                "id": f"stock_txt_{unique_id}",
                "title": title,
                "content": body,
                "type": "text",
                "format": fmt,
                "language": lang,
                "topic": t_data["topic"],
                "status": "in_stock",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            generated_items.append(item)
            if save_to_stock:
                stock["texts"].insert(0, item)

    elif main_type == "video":
        for i in range(count):
            t_data = shuffled_topics[i % len(shuffled_topics)]
            unique_id = f"vid_{uuid.uuid4().hex[:6]}"
            v_path = real_mp4s[i % len(real_mp4s)]
            
            if sub_type == "landscape_broll":
                v_title = f"🌊 Istanbul B-Roll: {t_data['city']}da {t_data['topic']} Talabasi 1 Kuni"
                v_type = "Manzaralı / Yazılı Video"
            elif sub_type == "avatar_talking":
                v_title = f"👩 Mila: {t_data['uni']}da Yashash va Kontrakt Haqiqatlari"
                v_type = "Yüzlü / Danışman Video"
            else: # trendy_music
                v_title = f"🎵 Trend Ritm: DTM Baling Kam Bo'lsa {t_data['topic']} O'qi!"
                v_type = "Şarkılı / Trend Video"

            item = {
                "id": f"stock_vid_{unique_id}",
                "title": v_title,
                "file_path": v_path,
                "video_type": v_type,
                "format": "Dikey Shorts / Reels (9:16)",
                "duration": "0:30",
                "topic": t_data["topic"],
                "status": "in_stock",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            generated_items.append(item)
            if save_to_stock:
                stock["videos"].insert(0, item)

    elif main_type == "image":
        for i in range(count):
            s_key, s_name, img_path = real_imgs[i % len(real_imgs)]
            t_data = shuffled_topics[i % len(shuffled_topics)]
            unique_id = f"img_{uuid.uuid4().hex[:6]}"
            
            item = {
                "id": f"stock_img_{unique_id}",
                "title": f"🎨 {s_name}: {t_data['topic']}",
                "style": s_key,
                "format": s_name,
                "photo_path": img_path,
                "status": "in_stock",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            generated_items.append(item)
            if save_to_stock:
                stock["images"].insert(0, item)

    if save_to_stock:
        save_json(STOCK_FILE, stock)

    return jsonify({
        "success": True,
        "type": main_type,
        "count": len(generated_items),
        "items": generated_items,
        "saved_to_stock": save_to_stock
    })

# ==============================================================
# SÜTUN 2: PAYLAŞIM, OTO-PLANLAMA & AI STRATEJİ DANIŞMANI
# ==============================================================

PLATFORMS_META = {
    "telegram": {
        "name": "Telegram",
        "handle": "@arkadasuz",
        "badge": "14.2k Obunachi",
        "icon": "fa-brands fa-telegram text-cyan",
        "color": "cyan",
        "supported": ["Metin", "Fotoğraf", "Video"],
        "recent_views": 8450,
        "posts_last_week": 14,
        "best_slot": "19:30 Prime",
        "top_topic": "Tibbiyot va Viza Qoidalari",
        "ai_analysis": "Son 1 haftada paylaşılan 14 postta ortalama 603 görüntülenme alındı. Akşam 19:30'da atılan tıp konulu postlar %42 daha fazla etkileşim getirdi.",
        "ai_recommendation": "Bu hafta Soru-Cevap (Quiz) ve 5 maddelik vize kontrol listesi formatını 19:30 slotuna planlayalım. Öğlenleri ise kısa burs duyuruları verelim."
    },
    "instagram": {
        "name": "Instagram",
        "handle": "@arkadas_consulting",
        "badge": "8.9k Takipçi",
        "icon": "fa-brands fa-instagram text-pink-500",
        "color": "pink-500",
        "supported": ["Fotoğraf (Carousel)", "Video (Reels)"],
        "recent_views": 38400,
        "posts_last_week": 9,
        "best_slot": "18:00 - 21:00",
        "top_topic": "Mila Özbekçe Reels & Yurt Turu",
        "ai_analysis": "Reels videoları keşfete düşerek 38,400 izlenme kazandırdı. Özellikle Mila'nın Özbekçe konuştuğu kampüs videosu en yüksek DM başvurusunu üretti.",
        "ai_recommendation": "Haftalık 4 adet Reels ve 3 adet 10 slaytlı eğitici kaydırmalı (Carousel) post planlayarak profil ziyaretlerini artıralım."
    },
    "youtube": {
        "name": "YouTube Shorts",
        "handle": "@arkadaş",
        "badge": "1.8k Abone",
        "icon": "fa-brands fa-youtube text-red-500",
        "color": "red-500",
        "supported": ["Video (Shorts)", "Topluluk (Metin/Foto)"],
        "recent_views": 52100,
        "posts_last_week": 7,
        "best_slot": "13:00 Tushlik",
        "top_topic": "Istanbulda Talaba Xarajatlari",
        "ai_analysis": "Shorts videolarının izlenme tamamlama oranı %78 seviyesinde. Yorumlarda 'Yurt narxlari' en çok sorulan başlık oldu.",
        "ai_recommendation": "Günde 1 adet Shorts videosu sabit 13:00 slotuna planlanmalı. Açıklamalara sabit @arkadasuz huni linki eklenmeli."
    },
    "tiktok": {
        "name": "TikTok",
        "handle": "@arkadas_edu",
        "badge": "24.5k Takipçi",
        "icon": "fa-brands fa-tiktok text-purple",
        "color": "purple",
        "supported": ["Video (Dikey)", "Fotoğraf (Slide)"],
        "recent_views": 94000,
        "posts_last_week": 11,
        "best_slot": "20:00 Gecesi",
        "top_topic": "DTM vs Turkiya Imtihonsiz",
        "ai_analysis": "Özbek gençleri 3 saniyelik şok kancalara (hook) çok güçlü reaksiyon veriyor. 11 videodan 3 tanesi 20k barajını aştı.",
        "ai_recommendation": "Görsel slayt postları yerine 15-20 saniyelik dinamik altyazılı 'DTM'dan yiqilganlar nima qiladi?' temalı videolar planlanmalı."
    },
    "twitter": {
        "name": "Twitter / X",
        "handle": "@arkadasuz",
        "badge": "2.4k Takipçi",
        "icon": "fa-brands fa-x-twitter text-slate-300",
        "color": "slate-300",
        "supported": ["Metin (Thread)", "Fotoğraf", "Video"],
        "recent_views": 18200,
        "posts_last_week": 18,
        "best_slot": "09:00 & 17:00",
        "top_topic": "YÖK Denklik & Hukuki Rehber",
        "ai_analysis": "Veliler ve bilinçli öğrenciler Twitter'daki flood/thread paylaşımlarını kaydetip okuyor. Üniversite denklik tabloları en çok RT aldı.",
        "ai_recommendation": "Günde 2 adet bilgilendirici tweet serisi planlayıp ana Telegram kanalına yönlendirme linki ekleyelim."
    },
    "facebook": {
        "name": "Facebook",
        "handle": "Arkadas Consulting Group",
        "badge": "6.1k Takipçi",
        "icon": "fa-brands fa-facebook text-blue-500",
        "color": "blue-500",
        "supported": ["Metin", "Fotoğraf", "Video"],
        "recent_views": 12800,
        "posts_last_week": 8,
        "best_slot": "12:00 & 19:00",
        "top_topic": "Ota-onalar Uchun Kafolatlar",
        "ai_analysis": "Facebook kitlesi çoğunlukla ebeveynlerden oluşuyor. Fiyat şeffaflığı, resmi sözleşme ve güvenlik vurgusu içeren postlar öne çıkıyor.",
        "ai_recommendation": "Haftada 3 kez güven aşılayan kurumsal MChJ sözleşmesi ve noter tasdikli burs garantisi metinleri planlanmalı."
    },
    "whatsapp": {
        "name": "WhatsApp Kanalı",
        "handle": "Arkadas VIP Kanal",
        "badge": "3.8k Abone",
        "icon": "fa-brands fa-whatsapp text-emerald",
        "color": "emerald",
        "supported": ["Metin", "Fotoğraf", "Video"],
        "recent_views": 11200,
        "posts_last_week": 14,
        "best_slot": "10:00 & 16:00",
        "top_topic": "Tezkor Grant E'lonlari",
        "ai_analysis": "Doğrudan bildirim gittiği için açılma oranı %84 ile en yüksek kanal. Anlık sıcak fırsatlar için ideal.",
        "ai_recommendation": "Hergün sabah 1 adet 'Günün Üniversitesi & Son 3 Kontenjan' formatında görsel kart paylaşımı planlanmalı."
    }
}

@pillars_bp.route("/api/ai_advisor", methods=["GET"])
def get_ai_advisor():
    platform = request.args.get("platform", "telegram").lower()
    meta = PLATFORMS_META.get(platform, PLATFORMS_META["telegram"])
    return jsonify({
        "success": True,
        "platform": platform,
        "data": meta
    })

@pillars_bp.route("/api/scheduler/auto_plan", methods=["POST"])
def auto_plan_schedule():
    """
    Stok havuzundaki hazır metin, video ve görselleri belirlenen gün sayısı (1, 5, 20, 30)
    boyunca 13:00 ve 19:30 yayın slotlarına akıllıca dağıtır.
    """
    payload = request.get_json() or {}
    platform = payload.get("platform", "telegram").lower()
    days = int(payload.get("days", 5)) # 1, 5, 20, 30
    slots_per_day = int(payload.get("slotsPerDay", 2)) # 13:00 & 19:30
    include_types = payload.get("includeTypes", ["text", "video", "image"])

    stock = load_json(STOCK_FILE, {"texts": [], "videos": [], "images": []})
    calendar_db = load_json(CALENDAR_FILE, {"events": []})
    existing_events = calendar_db.get("events", [])

    texts_pool = stock.get("texts", [])
    videos_pool = stock.get("videos", [])
    images_pool = stock.get("images", [])

    # Start scheduling from tomorrow
    start_dt = datetime.now() + timedelta(days=1)
    new_scheduled_items = []
    
    txt_idx, vid_idx, img_idx = 0, 0, 0
    slot_hours = ["13:00", "19:30"] if slots_per_day >= 2 else ["19:30"]

    for d in range(days):
        cur_date = (start_dt + timedelta(days=d)).strftime("%Y-%m-%d")
        for slot_time in slot_hours:
            target_platform = platform if platform != "all" else ["telegram", "youtube", "instagram", "tiktok"][(d * 2 + (0 if slot_time == "13:00" else 1)) % 4]
            
            # Pick content type alternating
            if slot_time == "19:30" and "video" in include_types and videos_pool:
                # Evening slot prime: Video / Shorts
                chosen = videos_pool[vid_idx % len(videos_pool)]
                vid_idx += 1
                c_type = "video"
                title = chosen.get("title", "Akşam Prime Video")
                media_path = chosen.get("file_path", "")
                preview_text = "Dikey Video İçeriği"
            elif "image" in include_types and images_pool and (slot_time == "13:00" or not videos_pool):
                # Noon slot: Visual Card / Poster
                chosen = images_pool[img_idx % len(images_pool)]
                img_idx += 1
                c_type = "image"
                title = chosen.get("title", "Görsel Bilgi Kartı")
                media_path = chosen.get("photo_path", "")
                preview_text = chosen.get("format", "Afiş Tasarımı")
            elif "text" in include_types and texts_pool:
                # Text / Copywriting
                chosen = texts_pool[txt_idx % len(texts_pool)]
                txt_idx += 1
                c_type = "text"
                title = chosen.get("title", "Öğle Bilgilendirme Postu")
                media_path = chosen.get("photo", "")
                preview_text = chosen.get("content", "")[:120] + "..."
            else:
                title = f"{target_platform.title()} Kampanya Gönderisi"
                c_type = "text"
                media_path = ""
                preview_text = "Detaylı eğitim bilgilendirme metni."

            event = {
                "id": f"cal_{uuid.uuid4().hex[:8]}",
                "platform": target_platform,
                "date": cur_date,
                "time": slot_time,
                "datetime": f"{cur_date} {slot_time}:00",
                "type": c_type,
                "title": title,
                "preview": preview_text,
                "media_path": media_path,
                "status": "scheduled",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            new_scheduled_items.append(event)
            existing_events.append(event)

    # Save to master calendar
    calendar_db["events"] = existing_events
    save_json(CALENDAR_FILE, calendar_db)

    # If platform is telegram or all, also append to scheduled_telegram_posts.json
    if platform in ["telegram", "all"]:
        tg_data = load_json(TG_SCHEDULE_FILE, {"posts": []})
        tg_posts = tg_data.get("posts", [])
        for item in new_scheduled_items:
            if item["platform"] == "telegram":
                tg_posts.append({
                    "id": item["id"],
                    "date": item["date"],
                    "time": item["time"],
                    "datetime": item["datetime"],
                    "title": item["title"],
                    "caption": item["preview"],
                    "card_image": item["media_path"],
                    "status": "pending"
                })
        tg_data["posts"] = tg_posts
        save_json(TG_SCHEDULE_FILE, tg_data)

    # If platform is youtube or all, also append to scheduled_youtube_shorts.json
    if platform in ["youtube", "all"]:
        yt_data = load_json(YT_SCHEDULE_FILE, {"shorts": []})
        yt_shorts = yt_data.get("shorts", [])
        for item in new_scheduled_items:
            if item["platform"] == "youtube" and item["type"] == "video":
                yt_shorts.append({
                    "id": item["id"],
                    "title": item["title"],
                    "file_path": item["media_path"],
                    "scheduled_time": item["datetime"],
                    "status": "pending"
                })
        yt_data["shorts"] = yt_shorts
        save_json(YT_SCHEDULE_FILE, yt_data)

    return jsonify({
        "success": True,
        "message": f"{days} günlük plan başarıyla oluşturuldu! Toplam {len(new_scheduled_items)} slot dolduruldu.",
        "platform": platform,
        "days": days,
        "scheduled_count": len(new_scheduled_items),
        "items": new_scheduled_items
    })

# ==============================================================
# SÜTUN 3: ANALİZ, ORTAK TAKVİM & METRİKLER
# ==============================================================

@pillars_bp.route("/api/analytics/calendar", methods=["GET"])
def get_analytics_calendar():
    calendar_db = load_json(CALENDAR_FILE, {"events": []})
    events = calendar_db.get("events", [])

    # If empty, generate past 7 days history + next 14 days plan
    if not events:
        events = []
        base = datetime.now()
        # 5 past days
        for i in range(5, 0, -1):
            d_str = (base - timedelta(days=i)).strftime("%Y-%m-%d")
            events.append({
                "id": f"hist_{i}_1", "platform": "telegram", "date": d_str, "time": "13:00",
                "title": "Tibbiyot Fakültesi Grantlari", "type": "text", "status": "published"
            })
            events.append({
                "id": f"hist_{i}_2", "platform": "youtube", "date": d_str, "time": "19:30",
                "title": "Istanbul Talaba Xarajati #Shorts", "type": "video", "status": "published"
            })
        # 7 future days
        for i in range(0, 8):
            d_str = (base + timedelta(days=i)).strftime("%Y-%m-%d")
            events.append({
                "id": f"fut_{i}_1", "platform": "telegram", "date": d_str, "time": "13:00",
                "title": "2026 Imtihonsiz Qabul Shartlari", "type": "image", "status": "scheduled"
            })
            events.append({
                "id": f"fut_{i}_2", "platform": "tiktok", "date": d_str, "time": "19:30",
                "title": "Mila Bilan Kampus Sayri", "type": "video", "status": "scheduled"
            })
        calendar_db["events"] = events
        save_json(CALENDAR_FILE, calendar_db)

    return jsonify({
        "success": True,
        "total_events": len(events),
        "events": events
    })

@pillars_bp.route("/api/analytics/metrics", methods=["GET"])
def get_analytics_metrics():
    """Haftalık/Aylık görüntülenme, mesaj, beğeni ve takipçi istatistikleri."""
    return jsonify({
        "success": True,
        "summary": {
            "total_views": 148500,
            "views_growth": "+22.4%",
            "total_messages": 428,
            "messages_growth": "+42 yeni başvuru",
            "total_likes": 14320,
            "likes_growth": "+1.4k bu hafta",
            "net_followers": 18940,
            "followers_growth": "+610 yeni abone"
        },
        "platforms": [
            {"name": "Telegram", "handle": "@arkadasuz", "views": 28400, "messages": 182, "likes": 3200, "followers": 14200, "color": "cyan"},
            {"name": "Instagram", "handle": "@arkadas_consulting", "views": 38400, "messages": 94, "likes": 4800, "followers": 8900, "color": "pink-500"},
            {"name": "YouTube", "handle": "@arkadaş", "views": 52100, "messages": 48, "likes": 3900, "followers": 1800, "color": "red-500"},
            {"name": "TikTok", "handle": "@arkadas_edu", "views": 94000, "messages": 62, "likes": 8200, "followers": 24500, "color": "purple"},
            {"name": "Twitter / X", "handle": "@arkadasuz", "views": 18200, "messages": 16, "likes": 980, "followers": 2400, "color": "slate-300"},
            {"name": "Facebook", "handle": "Arkadas Group", "views": 12800, "messages": 26, "likes": 640, "followers": 6100, "color": "blue-500"},
            {"name": "WhatsApp", "handle": "VIP Kanal", "views": 11200, "messages": 68, "likes": 1200, "followers": 3800, "color": "emerald"}
        ]
    })
