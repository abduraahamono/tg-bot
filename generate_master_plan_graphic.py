#!/usr/bin/env python3
"""
generate_master_plan_graphic.py
Generates a pixel-perfect, ultra-high-resolution 2-Month Master Publishing Calendar & Infographic Poster
for Arkadaş Consulting, and sends + pins it in the Telegram Admin chat.
"""

import os
import json
import urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from bot.telegram_client import TelegramClient

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(BASE_DIR, "output", "master_plan_infographic.jpg")

# Colors
BG_TOP = (11, 19, 43)        # #0B132B
BG_BOTTOM = (8, 14, 28)      # #080E1C
ACCENT_RED = (230, 57, 70)   # Arkadaş Crimson #E63946
ACCENT_GOLD = (244, 162, 97) # Amber / Gold
ACCENT_CYAN = (76, 201, 240) # Cyan
TEXT_WHITE = (255, 255, 255)
TEXT_MUTED = (160, 174, 192)
TEXT_DIM = (120, 135, 160)
GREEN_BADGE = (46, 204, 113)

def get_font(size, bold=False):
    f_bold = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
    f_reg = "/System/Library/Fonts/Supplemental/Arial.ttf"
    font_path = f_bold if bold else f_reg
    try:
        return ImageFont.truetype(font_path, size)
    except Exception:
        return ImageFont.load_default()

def build_graphic():
    W, H = 1200, 2220
    img = Image.new("RGBA", (W, H), BG_TOP)
    draw = ImageDraw.Draw(img)

    # Background gradient
    for y in range(H):
        ratio = y / H
        r = int(BG_TOP[0] * (1 - ratio) + BG_BOTTOM[0] * ratio)
        g = int(BG_TOP[1] * (1 - ratio) + BG_BOTTOM[1] * ratio)
        b = int(BG_TOP[2] * (1 - ratio) + BG_BOTTOM[2] * ratio)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # Atmospheric glow highlights
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse([(-100, -100), (550, 550)], fill=(76, 201, 240, 30))
    glow_draw.ellipse([(W - 450, 550), (W + 200, 1200)], fill=(230, 57, 70, 22))
    glow_draw.ellipse([(-150, 1400), (480, 2050)], fill=(244, 162, 97, 20))
    glow = glow.filter(ImageFilter.GaussianBlur(90))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img)

    # 1. HEADER SECTION
    logo_path = os.path.join(BASE_DIR, "assets", "logo_white.png")
    if os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
            logo.thumbnail((200, 75), Image.Resampling.LANCZOS)
            img.paste(logo, (60, 50), logo)
        except Exception:
            pass

    # Status Pill (Top Right)
    badge_x, badge_y, badge_w, badge_h = W - 340, 55, 280, 46
    draw.rounded_rectangle([badge_x, badge_y, badge_x + badge_w, badge_y + badge_h], radius=23, fill=(16, 185, 129, 45), outline=(16, 185, 129, 150), width=2)
    draw.ellipse([badge_x + 18, badge_y + 17, badge_x + 28, badge_y + 27], fill=(16, 185, 129))
    draw.text((badge_x + 38, badge_y + 12), "BULUT CRON FAOL (7/24)", font=get_font(15, bold=True), fill=(255, 255, 255))

    # Main Title
    draw.text((60, 140), "ARKADAŞ CONSULTING  |  STRATEGIK REJA", font=get_font(18, bold=True), fill=ACCENT_CYAN)
    draw.text((60, 172), "2 OYLIK MASTER YAYIN REJASI", font=get_font(46, bold=True), fill=TEXT_WHITE)
    draw.text((60, 235), "Telegram (@arkadasuz) & Twitter (@arkadasuz) Avtomatlashtirilgan Kontent Xaritasi", font=get_font(21), fill=TEXT_MUTED)
    draw.text((60, 270), "Davr: 11-Sentyabr 2026 — 10-Noyabr 2026 (60 Kunlik To'liq Sikl)", font=get_font(18, bold=True), fill=ACCENT_GOLD)

    draw.line([(60, 315), (W - 60, 315)], fill=(255, 255, 255, 35), width=1)

    # 2. KEY METRICS (4 CARDS)
    cards = [
        ("134 TA POST", "Telegram @arkadasuz", "Kuniga 2x (13:00 & 19:30)", ACCENT_CYAN),
        ("201 TA TVIT", "Twitter / X @arkadasuz", "Kuniga 3x (10:00, 14:00, 20:00)", ACCENT_GOLD),
        ("0 TAKRORLANISH", "Dinamik Fabrika", "Har bir post unikal mavzuda", GREEN_BADGE),
        ("GITHUB ACTIONS", "Avtonom Bulut", "Mac o'chganda ham to'xtamaydi", ACCENT_RED),
    ]

    card_w = (W - 120 - 3 * 20) // 4
    card_h = 135
    for i, (title, sub1, sub2, accent) in enumerate(cards):
        cx = 60 + i * (card_w + 20)
        cy = 340
        draw.rounded_rectangle([cx, cy, cx + card_w, cy + card_h], radius=16, fill=(18, 30, 56), outline=(255, 255, 255, 25), width=1)
        draw.line([(cx + 20, cy), (cx + card_w - 20, cy)], fill=accent, width=3)
        draw.text((cx + 18, cy + 22), title, font=get_font(22, bold=True), fill=TEXT_WHITE)
        draw.text((cx + 18, cy + 62), sub1, font=get_font(15, bold=True), fill=accent)
        draw.text((cx + 18, cy + 90), sub2, font=get_font(13), fill=TEXT_MUTED)

    # 3. CONTENT ARCHETYPES (4 TEMPLATES BAR)
    cy_arch = 505
    draw.text((60, cy_arch), "FOYDALANILADIGAN 4 XIL MASTER DIZAYN QOLIPI (ZERO REPETITION)", font=get_font(20, bold=True), fill=TEXT_WHITE)
    draw.text((60, cy_arch + 30), "Postlar doimiy ravishda quyidagi 4 ta format va salt matnlar o'rtasida aylanadi:", font=get_font(16), fill=TEXT_MUTED)

    archs = [
        ("1. Sade Sinematik", "Galata & Bosfor fonida samimiy talaba voqeasi", (76, 201, 240)),
        ("2. Cool Manifesto", "Prestijli OTM, intellektual brend matnlari", (244, 162, 97)),
        ("3. Taqqoslash Kardi", "O'zbekiston vs Turkiya davlat qabuli jadvali", (230, 57, 70)),
        ("4. Minimal Konsept", "Studiya stoli, qabul xati va aniq tavsiyalar", (16, 185, 129)),
    ]
    aw = (W - 120 - 3 * 16) // 4
    for i, (atitle, adesc, acolor) in enumerate(archs):
        ax = 60 + i * (aw + 16)
        ay = cy_arch + 68
        draw.rounded_rectangle([ax, ay, ax + aw, ay + 95], radius=12, fill=(15, 25, 48), outline=(acolor[0], acolor[1], acolor[2], 90), width=1)
        draw.text((ax + 16, ay + 16), atitle, font=get_font(16, bold=True), fill=acolor)
        draw.text((ax + 16, ay + 46), adesc, font=get_font(13), fill=TEXT_MUTED)

    # 4. 8-WEEK STRATEGIC ROADMAP (THE CORE TABLE)
    cy_weeks = 705
    draw.text((60, cy_weeks), "8 HAFTALIK BOSQICHMA-BOSQICH KONTENT STRATEGIYASI", font=get_font(24, bold=True), fill=TEXT_WHITE)
    draw.text((60, cy_weeks + 34), "Auditoriyani ishonch va qiziqishdan to'g'ridan-to'g'ri qabulga olib boruvchi 60 kunlik voronka:", font=get_font(16), fill=TEXT_MUTED)

    weeks_data = [
        ("1-2 HAFTA", "11 - 24 SENTYABR", "KATTA TAQQOSLASH & FARKINDALIK BOSQICHI",
         "DTM imtihon stressi va super-kontrakt ($2,000+) ga muqobil taklif.\n"
         "Turkiya davlat universitetlariga imtihonsiz to'g'ridan-to'g'ri qabul ($300-$800).\n"
         "Diplomlarning O'zbekistonda to'g'ridan-to'g'ri (nostrifikatsiyasiz) tan olinishi.",
         ACCENT_CYAN),

        ("3-4 HAFTA", "25 SEN - 08 OKTYABR", "SHAHARLAR & UNIVERSITET TANLOVI BOSQICHI",
         "Istanbul, Ankara, Izmir, Bursa, Sakarya va Antaliya davlat universitetlari.\n"
         "YÖK akkreditatsiyasi, kampus infratuzilmasi, kutubxonalar va laboratoriyalar.\n"
         "Nega aynan ushbu oliygohlar xalqaro reytinglarda Top-1000 talikda turadi?",
         ACCENT_GOLD),

        ("5-6 HAFTA", "09 - 22 OKTYABR", "FAKULTETLAR & KARYERA REJASI BOSQICHI",
         "Tibbiyot va Stomatologiya: Yevropa andozasidagi amaliyot va arzon yillik to'lovlar.\n"
         "Dasturlash, IT va Muhandislik: Erasmus+ orqali Yevropaga bepul almashinuv.\n"
         "Xalqaro biznes, iqtisod va logistika: Global korporatsiyalarda stajirovkalar.",
         GREEN_BADGE),

        ("7-8 HAFTA", "23 OKT - 10 NOYABR", "TALABALIK XARAJATLARI & ERTA QABUL BOSQICHI",
         "Turkiyada oylik talaba byudjeti: KYK va xususiy yotoqxonalar, arzon oziq-ovqat.\n"
         "TÖMER til tayyorgarligi sirlari va 1 yilda turk tilini mukammal o'rganish.\n"
         "Hujjat topshirish yakuniy muddatlari va 2026/27 qabul o'rinlarini bron qilish.",
         ACCENT_RED),
    ]

    wy = cy_weeks + 80
    for w_code, w_dates, w_title, w_desc, w_color in weeks_data:
        box_h = 160
        draw.rounded_rectangle([60, wy, W - 60, wy + box_h], radius=16, fill=(18, 28, 54), outline=(255, 255, 255, 30), width=1)

        # Left Accent Tag Box
        draw.rounded_rectangle([60, wy, 240, wy + box_h], radius=16, fill=(14, 22, 42))
        draw.line([(240, wy), (240, wy + box_h)], fill=(255, 255, 255, 20), width=1)
        draw.line([(60, wy + 16), (60, wy + box_h - 16)], fill=w_color, width=5)

        draw.text((80, wy + 35), w_code, font=get_font(22, bold=True), fill=TEXT_WHITE)
        draw.text((80, wy + 72), w_dates, font=get_font(13, bold=True), fill=w_color)
        draw.text((80, wy + 105), "16 Post + 28 Tvit", font=get_font(13), fill=TEXT_MUTED)

        # Right Content
        draw.text((270, wy + 25), w_title, font=get_font(20, bold=True), fill=w_color)
        lines = w_desc.split("\n")
        ly = wy + 62
        for line in lines:
            draw.ellipse([272, ly + 6, 278, ly + 12], fill=w_color)
            draw.text((290, ly), line, font=get_font(15), fill=TEXT_WHITE)
            ly += 28

        wy += box_h + 18

    # 5. DAILY PUBLISHING CLOCK (RITM)
    cy_clock = wy + 15
    draw.text((60, cy_clock), "KUNLIK AVTOMATIK NASHR VAQTLARI & PLATFORMALAR", font=get_font(22, bold=True), fill=TEXT_WHITE)

    slots = [
        ("10:00", "Twitter / X", "SABAH MOTIVATSIYASI", "Tezkor fakt, motivatsiya va fikr uyg'otuvchi qisqa tvit", ACCENT_GOLD),
        ("13:00", "Telegram + Twitter", "TUSHLIK QO'LLANMASI", "Universitet tahlili, rasmiy kontraktlar, yotoqxona ma'lumotlari", ACCENT_CYAN),
        ("19:30 & 20:00", "Telegram + Twitter", "KECHKI ASOSIY POST", "Yuqori sifatli Dizayn Kartasi + Hikoya + Qabulga chaqiruv", ACCENT_RED),
    ]

    sw = (W - 120 - 2 * 20) // 3
    for i, (stime, schan, stype, sdetail, scolor) in enumerate(slots):
        sx = 60 + i * (sw + 20)
        sy = cy_clock + 45
        sh = 145
        draw.rounded_rectangle([sx, sy, sx + sw, sy + sh], radius=14, fill=(16, 26, 50), outline=(scolor[0], scolor[1], scolor[2], 90), width=1)
        draw.text((sx + 18, sy + 16), stime, font=get_font(22, bold=True), fill=TEXT_WHITE)
        draw.text((sx + 18, sy + 46), schan, font=get_font(13, bold=True), fill=scolor)
        draw.text((sx + 18, sy + 74), stype, font=get_font(15, bold=True), fill=TEXT_WHITE)
        draw.text((sx + 18, sy + 102), sdetail, font=get_font(13), fill=TEXT_MUTED)

    # 6. HOW TO TRACK IN TELEGRAM (FOOTER CARD)
    fy = sy + sh + 30
    draw.rounded_rectangle([60, fy, W - 60, fy + 165], radius=16, fill=(12, 19, 36), outline=(76, 201, 240, 120), width=2)
    draw.text((90, fy + 22), "TELEGRAMDAN REJANI QANDAY KUZATIB BORASIZ?", font=get_font(20, bold=True), fill=ACCENT_CYAN)
    draw.text((90, fy + 58), "1. Admin Bot Menyusi: Botga kirib '1 Haftalik Reja & Takvim' tugmasini bosing yoki 'reja' deb yozing.", font=get_font(15), fill=TEXT_WHITE)
    draw.text((90, fy + 90), "2. Jonli Holat & Kunlar: Bot barcha kunlar bo'yicha [Joylandi] va [Kutilmoqda] postlar ro'yxatini ko'rsatadi.", font=get_font(15), fill=TEXT_WHITE)
    draw.text((90, fy + 122), "3. Ushbu Rasmni Chatga Qadab Qo'ying (Pin): 2 oylik umumiy yo'nalish va tematik reja doim ko'z o'ngingizda bo'ladi!", font=get_font(15, bold=True), fill=ACCENT_GOLD)

    # Brand Signature
    draw.text((60, H - 45), "Arkadaş Consulting — Turkiyada Talaba Bo'lishingizdagi Ishonchli Hamkoringiz", font=get_font(14), fill=TEXT_DIM)
    draw.text((W - 270, H - 45), "Yagona Aloqa: @arkadasuzz", font=get_font(14, bold=True), fill=ACCENT_CYAN)

    # Save
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    img_rgb = img.convert("RGB")
    img_rgb.save(OUTPUT_PATH, quality=95)
    print(f"[OK] Master Plan Grafik qayta yaratildi: {OUTPUT_PATH}")
    return OUTPUT_PATH

def send_and_pin():
    graphic_path = build_graphic()
    with open(os.path.join(BASE_DIR, "bot_config.json")) as f:
        cfg = json.load(f)
    token = cfg.get("bot_token")
    admin_id = cfg.get("admin_chat_id", "8021468690")
    client = TelegramClient(token)

    caption = (
        "📊 <b>ARKADAŞ CONSULTING — 2 AYLIK MASTER YAYIN REJASI</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Ushbu grafik kartada <b>11-Sentyabrdan 10-Noyabrgacha</b> bo'lgan 60 kunlik to'liq nashr strategiyasi, "
        "8 haftalik mavzular, kunlik nashr soatlari va 4 xil dizayn qoliplari jamlangan.\n\n"
        "📌 <b>Ushbu xabar chatingiz yuqorisiga avtomatik qadaldi (PIN)!</b>\n\n"
        "📱 <b>Telegramdan jonli kuzatish uchun:</b>\n"
        "• Bot menyusidagi <code>🗓️ 1 Haftalik Reja & Takvim</code> tugmasini bosing\n"
        "• Yoki shunchaki <code>reja</code> yoki <code>takvim</code> deb yozing\n"
        "• Bot barcha kunlar bo'yicha (✅ Joylangan / ⏳ Navbatda) holatini ko'rsatib boradi.\n\n"
        "🚀 <i>Ertaga (11-sentyabr) 10:00 (Twitter) va 13:00 (Telegram) da avtomatik start oladi!</i>"
    )

    print(f"[SENDING] Admin Telegramiga yuborilmoqda: {admin_id}...")
    res = client.send_photo(admin_id, graphic_path, caption=caption)
    print("Response:", res)
    if res.get("ok"):
        msg_id = res["result"]["message_id"]
        # Pin message
        pin_url = f"https://api.telegram.org/bot{token}/pinChatMessage"
        req = urllib.request.Request(
            pin_url,
            data=json.dumps({"chat_id": admin_id, "message_id": msg_id, "disable_notification": False}).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req) as r:
                print("Pin response:", json.loads(r.read().decode("utf-8")))
        except Exception as e:
            print("Pin error:", e)

if __name__ == "__main__":
    send_and_pin()
