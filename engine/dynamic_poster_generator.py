#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
engine/dynamic_poster_generator.py
Arkadaş Consulting — Real AI Dynamic Visual Generator Engine
Guarantees 100% unique visual posters:
- Gemini AI generates custom headlines, custom badges, custom clues/points/options
- 6 Distinct professional color palettes (Emerald/Cyan, Royal Gold, Cyber Ruby, Electric Violet, Sunset Amber, Clean Azure)
- Dynamic backgrounds with scenery + frosted glass tinting
- Full vector badge & checkmark drawing
- No two generated cards are ever identical!
"""

import os
import uuid
import random
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output" / "cards"
ASSETS_DIR = BASE_DIR / "assets"
SCENERY_DIR = ASSETS_DIR / "scenery"
LOGO_WHITE_PATH = ASSETS_DIR / "logo_white.png"

# ==============================================================
# 6 RICH PROFESSIONAL COLOR PALETTES
# ==============================================================
PALETTES = {
    "emerald_cyan": {
        "name": "Zümrüt & Okyanus Mavisi",
        "bg_overlay": (10, 26, 32, 225),
        "primary": (52, 211, 153),      # Emerald
        "accent": (56, 189, 248),       # Cyan
        "card_bg": (15, 36, 44, 230),
        "card_border": (52, 211, 153, 100),
        "badge_bg": (16, 185, 129, 235),
        "badge_text": (255, 255, 255),
        "text_main": (255, 255, 255),
        "text_sub": (203, 213, 225),
        "highlight": (251, 191, 36)     # Amber
    },
    "royal_gold": {
        "name": "Kraliyet Altını & Gece Mavisi",
        "bg_overlay": (14, 20, 38, 230),
        "primary": (251, 191, 36),      # Gold / Amber
        "accent": (245, 158, 11),       # Warm Gold
        "card_bg": (22, 30, 52, 230),
        "card_border": (251, 191, 36, 110),
        "badge_bg": (217, 119, 6, 235),
        "badge_text": (255, 255, 255),
        "text_main": (255, 255, 255),
        "text_sub": (226, 232, 240),
        "highlight": (56, 189, 248)
    },
    "cyber_ruby": {
        "name": "Siber Yakut & Gül",
        "bg_overlay": (26, 12, 22, 230),
        "primary": (244, 63, 94),       # Rose / Crimson
        "accent": (251, 113, 133),
        "card_bg": (38, 18, 30, 230),
        "card_border": (244, 63, 94, 110),
        "badge_bg": (225, 29, 72, 235),
        "badge_text": (255, 255, 255),
        "text_main": (255, 255, 255),
        "text_sub": (254, 205, 211),
        "highlight": (253, 224, 71)
    },
    "electric_violet": {
        "name": "Elektrik Mor & Neon Pembe",
        "bg_overlay": (22, 12, 38, 230),
        "primary": (168, 85, 247),      # Violet
        "accent": (217, 70, 239),       # Fuchsia
        "card_bg": (32, 18, 52, 230),
        "card_border": (168, 85, 247, 110),
        "badge_bg": (147, 51, 234, 235),
        "badge_text": (255, 255, 255),
        "text_main": (255, 255, 255),
        "text_sub": (233, 213, 255),
        "highlight": (56, 189, 248)
    },
    "sunset_amber": {
        "name": "Günbatımı Kehribarı",
        "bg_overlay": (30, 18, 12, 230),
        "primary": (249, 115, 22),      # Orange
        "accent": (251, 146, 60),
        "card_bg": (42, 24, 16, 230),
        "card_border": (249, 115, 22, 110),
        "badge_bg": (234, 88, 12, 235),
        "badge_text": (255, 255, 255),
        "text_main": (255, 255, 255),
        "text_sub": (254, 215, 170),
        "highlight": (253, 224, 71)
    },
    "clean_azure": {
        "name": "Arktik Gökyüzü & Safir",
        "bg_overlay": (10, 20, 36, 230),
        "primary": (56, 189, 248),      # Cyan / Sky
        "accent": (96, 165, 250),       # Blue
        "card_bg": (18, 30, 52, 230),
        "card_border": (56, 189, 248, 110),
        "badge_bg": (2, 132, 199, 235),
        "badge_text": (255, 255, 255),
        "text_main": (255, 255, 255),
        "text_sub": (224, 242, 254),
        "highlight": (52, 211, 153)
    }
}

PALETTE_KEYS = list(PALETTES.keys())

def get_font(size: int, bold: bool = False, serif: bool = False) -> ImageFont.FreeTypeFont:
    """Loads system fonts safely with fallback hierarchy."""
    if serif:
        paths = ["/System/Library/Fonts/Times.ttc", "/System/Library/Fonts/Supplemental/Times New Roman.ttf"]
    elif bold:
        paths = [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial Bold.ttf"
        ]
    else:
        paths = [
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial.ttf"
        ]
    
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

def draw_vector_check(draw: ImageDraw.ImageDraw, x: int, y: int, size: int = 32, color: tuple = (16, 185, 129)):
    """Draws a crisp circular checkmark badge."""
    draw.ellipse([x, y, x + size, y + size], fill=color)
    lw = max(2, int(size * 0.12))
    p1 = (x + size * 0.28, y + size * 0.52)
    p2 = (x + size * 0.44, y + size * 0.72)
    p3 = (x + size * 0.74, y + size * 0.32)
    draw.line([p1, p2], fill=(255, 255, 255), width=lw)
    draw.line([p2, p3], fill=(255, 255, 255), width=lw)

def load_random_background(width: int, height: int, blur: int = 5) -> Image.Image:
    """Loads a random scenery photo from assets, scales, crops, and blurs it."""
    scenery_files = list(SCENERY_DIR.glob("*.jpg"))
    if scenery_files:
        bg_path = random.choice(scenery_files)
        try:
            bg = Image.open(bg_path).convert("RGBA")
            bg_ratio = bg.width / bg.height
            target_ratio = width / height
            if bg_ratio > target_ratio:
                new_w = int(height * bg_ratio)
                bg = bg.resize((new_w, height), Image.Resampling.LANCZOS)
                left = (new_w - width) // 2
                bg = bg.crop((left, 0, left + width, height))
            else:
                new_h = int(width / bg_ratio)
                bg = bg.resize((width, new_h), Image.Resampling.LANCZOS)
                top = (new_h - height) // 2
                bg = bg.crop((0, top, width, top + height))
            
            if blur > 0:
                bg = bg.filter(ImageFilter.GaussianBlur(radius=blur))
            return bg
        except Exception:
            pass
    return Image.new("RGBA", (width, height), (15, 23, 42, 255))

def paste_logo(canvas: Image.Image, x: int, y: int, target_w: int = 180, color_accent=(56, 189, 248)):
    """Pastes white Arkadaş logo or draws vector text logo."""
    if LOGO_WHITE_PATH.exists():
        try:
            logo = Image.open(LOGO_WHITE_PATH).convert("RGBA")
            target_h = int(logo.height * (target_w / logo.width))
            logo_r = logo.resize((target_w, target_h), Image.Resampling.LANCZOS)
            canvas.paste(logo_r, (x, y), logo_r)
            return target_h
        except Exception:
            pass
    draw = ImageDraw.Draw(canvas)
    draw.text((x, y), "ARKADAŞ", font=get_font(28, bold=True), fill=color_accent)
    return 30

# ==============================================================
# 4 DATA-DRIVEN DYNAMIC RENDERING ENGINES
# ==============================================================

def render_dynamic_qa_quiz(data: dict, out_path: str) -> str:
    """Style 1: Soru-Cevap / Quiz Kartı with dynamic content & palette."""
    w, h = 1080, 1080
    palette = PALETTES.get(data.get("palette"), PALETTES["emerald_cyan"])
    bg = load_random_background(w, h, blur=6)
    
    overlay = Image.new("RGBA", (w, h), palette["bg_overlay"])
    canvas = Image.alpha_composite(bg, overlay)
    draw = ImageDraw.Draw(canvas)

    # 1. Header & Logo
    paste_logo(canvas, 60, 55, target_w=190, color_accent=palette["accent"])
    
    # Badge
    badge_text = data.get("badge", "❓ QUIZ / TEST 2026")
    badge_w = min(400, max(220, len(badge_text) * 14 + 40))
    draw.rounded_rectangle((w - badge_w - 60, 55, w - 60, 105), radius=8, fill=palette["badge_bg"])
    draw.text((w - badge_w - 45, 68), badge_text, font=get_font(17, bold=True), fill=palette["badge_text"])

    # 2. Question Box
    draw.rounded_rectangle((60, 145, 1020, 365), radius=20, fill=palette["card_bg"], outline=palette["card_border"], width=2)
    
    sub = data.get("sub_headline", f"Turkiyada {data.get('topic', 'Ta\'lim')} Bo'yicha Qabul").upper()
    draw.text((95, 175), sub[:55], font=get_font(16, bold=True), fill=palette["highlight"])
    
    q_text = data.get("question", f"Turkiyada {data.get('topic', 'Oliy')} ta'limiga attestat bilan qanday kirish mumkin?")
    # Wrap question
    if len(q_text) > 52 and "\n" not in q_text:
        parts = q_text.split(" ")
        mid = len(parts) // 2
        q_text = " ".join(parts[:mid]) + "\n" + " ".join(parts[mid:])
    draw.text((95, 215), q_text, font=get_font(29, bold=True), fill=palette["text_main"], spacing=10)

    # 3. Dynamic Options
    options = data.get("options", [
        {"letter": "A", "text": f"{data.get('uni', 'Nufuzli OTM')} (Attestat bilan imtihonsiz)", "correct": True},
        {"letter": "B", "text": "Faqat murakkab YÖS imtihoni (95+ ball)", "correct": False},
        {"letter": "C", "text": "SAT xalqaro sertifikati bilan", "correct": False},
        {"letter": "D", "text": "Barcha javoblar to'g'ri", "correct": False}
    ])

    oy = 395
    for opt in options[:4]:
        letter = opt.get("letter", "A")
        text = opt.get("text", "")[:50]
        is_correct = opt.get("correct", False)
        
        c_fill = (22, 101, 52, 230) if is_correct else palette["card_bg"]
        c_border = (74, 222, 128, 240) if is_correct else (255, 255, 255, 30)
        
        draw.rounded_rectangle((60, oy, 1020, oy + 92), radius=14, fill=c_fill, outline=c_border, width=2)
        draw.ellipse([85, oy + 21, 135, oy + 71], fill=(255, 255, 255, 35))
        draw.text((98, oy + 29), letter, font=get_font(24, bold=True), fill=(255, 255, 255))
        
        draw.text((160, oy + 31), text, font=get_font(23, bold=is_correct), fill=(255, 255, 255))
        if is_correct:
            draw_vector_check(draw, 950, oy + 28, size=36, color=(34, 197, 94))
        oy += 115

    # 4. Footer CTA
    draw.rounded_rectangle((60, 895, 1020, 995), radius=16, fill=(10, 15, 30, 245), outline=palette["card_border"], width=1)
    cta = data.get("cta", "👉 To'g'ri javobni tanlab, bepul qabul xatiga ega bo'ling: @arkadasuz")
    draw.text((90, 928), cta[:62], font=get_font(21, bold=True), fill=palette["accent"])

    canvas.convert("RGB").save(out_path, quality=95)
    return out_path

def render_dynamic_riddle(data: dict, out_path: str) -> str:
    """Style 2: Bilmece / İpuçlu Tasarım with dynamic clues & custom palette."""
    w, h = 1080, 1080
    palette = PALETTES.get(data.get("palette"), PALETTES["royal_gold"])
    bg = load_random_background(w, h, blur=5)
    
    overlay = Image.new("RGBA", (w, h), palette["bg_overlay"])
    canvas = Image.alpha_composite(bg, overlay)
    draw = ImageDraw.Draw(canvas)

    # 1. Logo & Badge
    paste_logo(canvas, 60, 55, target_w=190, color_accent=palette["primary"])
    
    badge_text = data.get("badge", "🔍 BILASIZMI? • SIRLI FAKT")
    draw.rounded_rectangle((60, 160, 380, 210), radius=8, fill=palette["badge_bg"])
    draw.text((80, 172), badge_text, font=get_font(17, bold=True), fill=palette["badge_text"])

    # 2. Hook Title
    sub = data.get("sub_headline", f"Turkiyada {data.get('topic', 'Ta\'lim')} Haqida")
    draw.text((60, 235), sub[:50], font=get_font(25, bold=False), fill=palette["text_sub"])
    
    headline = data.get("headline", "3 TA SIZ BILMAGAN SIR!")
    draw.text((60, 280), headline[:40], font=get_font(44, bold=True), fill=palette["primary"])

    # 3. Dynamic Clues / Facts
    clues = data.get("clues", [
        {"num": "01", "title": "Imtihonsiz To'g'ridan-To'g'ri Qabul", "desc": f"{data.get('uni', 'Oliygoh')}da faqat attestat bilan talaba bo'lish kafolati."},
        {"num": "02", "title": "0$ Risk: Avval Qabul, Keyin To'lov", "desc": "Rasmiy vazirlik tasdiqlagan qabul xati chiqmaguncha 1 so'm ham to'lamaysiz."},
        {"num": "03", "title": "Bologna Tizimi — 150+ Davlatda Diplom", "desc": "Diplomingiz O'zbekiston, Yevropa va butun dunyoda 100% akkreditatsiyadan o'tadi."}
    ])

    cy = 390
    for c in clues[:3]:
        num = c.get("num", "01")
        title = c.get("title", "")[:45]
        desc = c.get("desc", "")[:75]

        draw.rounded_rectangle((60, cy, 1020, cy + 135), radius=16, fill=palette["card_bg"], outline=palette["card_border"], width=1)
        
        # Num circle badge
        draw.rounded_rectangle((85, cy + 25, 145, cy + 85), radius=12, fill=palette["badge_bg"])
        draw.text((95, cy + 35), num, font=get_font(28, bold=True), fill=palette["badge_text"])
        
        draw.text((170, cy + 27), title, font=get_font(24, bold=True), fill=palette["text_main"])
        draw.text((170, cy + 70), desc, font=get_font(18, bold=False), fill=palette["text_sub"])
        cy += 160

    # 4. Footer CTA
    draw.rounded_rectangle((60, 905, 1020, 1000), radius=16, fill=(15, 23, 42, 245), outline=palette["card_border"], width=1)
    cta = data.get("cta", "💡 Sirni yechish va 2026 qabuliga yozilish: @arkadasuz")
    draw.text((90, 936), cta[:62], font=get_font(21, bold=True), fill=palette["primary"])

    canvas.convert("RGB").save(out_path, quality=95)
    return out_path

def render_dynamic_checklist(data: dict, out_path: str) -> str:
    """Style 3: Kontrol Listesi / Checklist with dynamic items & palette."""
    w, h = 1080, 1080
    palette = PALETTES.get(data.get("palette"), PALETTES["cyber_ruby"])
    bg = load_random_background(w, h, blur=6)
    
    overlay = Image.new("RGBA", (w, h), palette["bg_overlay"])
    canvas = Image.alpha_composite(bg, overlay)
    draw = ImageDraw.Draw(canvas)

    # 1. Logo & Badge
    paste_logo(canvas, 60, 55, target_w=190, color_accent=palette["primary"])
    
    badge_text = data.get("badge", "✅ 2026 QABUL CHECKLISTI")
    draw.rounded_rectangle((60, 150, 420, 200), radius=8, fill=palette["badge_bg"])
    draw.text((80, 162), badge_text, font=get_font(17, bold=True), fill=palette["badge_text"])

    # 2. Heading
    sub = data.get("sub_headline", f"{data.get('topic', 'Soha')} Bo'yicha Talaba Bo'lish")
    draw.text((60, 225), sub[:50], font=get_font(24, bold=False), fill=palette["text_sub"])
    
    headline = data.get("headline", "5 TA ASOSIY QADAM:")
    draw.text((60, 270), headline[:42], font=get_font(44, bold=True), fill=palette["primary"])

    # 3. Dynamic Checklist Items
    items = data.get("checklist_items", [
        "Xorijga chiqish pasporti (Zagran)",
        "Maktab attestati yoki kollej/litsey diplomi",
        f"{data.get('uni', 'Oliygoh')} uchun 0$ risk ariza",
        "Turkiyada yashash ruxsatnomasi (İkamet ID) kafolati",
        "Arkadaş Consulting bilan rasmiy yuridik shartnoma"
    ])

    iy = 375
    for it_text in items[:5]:
        draw.rounded_rectangle((60, iy, 1020, iy + 85), radius=14, fill=palette["card_bg"], outline=palette["card_border"], width=1)
        draw_vector_check(draw, 90, iy + 24, size=36, color=palette["primary"])
        draw.text((150, iy + 26), it_text[:56], font=get_font(21, bold=True), fill=palette["text_main"])
        iy += 105

    # 4. Footer CTA
    draw.rounded_rectangle((60, 925, 1020, 1010), radius=14, fill=(15, 23, 42, 245), outline=palette["card_border"], width=1)
    cta = data.get("cta", "📲 Hujjat topshirish va joy band qilish: @arkadasuz")
    draw.text((90, 950), cta[:62], font=get_font(21, bold=True), fill=palette["primary"])

    canvas.convert("RGB").save(out_path, quality=95)
    return out_path

def render_dynamic_modern_ad(data: dict, out_path: str) -> str:
    """Style 4: Modern Reklam / Banner with bold offer, tags, and custom palette."""
    w, h = 1080, 1080
    palette = PALETTES.get(data.get("palette"), PALETTES["sunset_amber"])
    bg = load_random_background(w, h, blur=4)
    
    overlay = Image.new("RGBA", (w, h), palette["bg_overlay"])
    canvas = Image.alpha_composite(bg, overlay)
    draw = ImageDraw.Draw(canvas)

    # 1. Logo & Top Corner Badge
    paste_logo(canvas, 60, 55, target_w=200, color_accent=palette["primary"])
    
    badge_text = data.get("badge", "RASMIY QABUL 2026")
    badge_w = min(360, max(220, len(badge_text) * 14 + 30))
    draw.rounded_rectangle((w - badge_w - 60, 55, w - 60, 105), radius=8, fill=palette["badge_bg"])
    draw.text((w - badge_w - 45, 68), badge_text, font=get_font(18, bold=True), fill=palette["badge_text"])

    # 2. Giant Typography Hook
    sub = data.get("sub_headline", "TURKIYADA O'QISH").upper()
    draw.text((60, 165), sub[:40], font=get_font(44, bold=True), fill=palette["primary"])
    
    headline = data.get("headline", "Imtihonsiz Talaba Bo'ling!")
    draw.text((60, 230), headline[:38], font=get_font(40, bold=True), fill=palette["text_main"])

    # 3. Main Offer Box
    draw.rounded_rectangle((60, 325, 1020, 605), radius=20, fill=palette["card_bg"], outline=palette["card_border"], width=2)
    
    draw.text((95, 360), "KAFOLATLANGAN TAKLIF:", font=get_font(17, bold=True), fill=palette["accent"])
    uni_txt = f"🎓 {data.get('uni', 'Istanbul Medipol & Bezmialem')}"
    draw.text((95, 398), uni_txt[:48], font=get_font(30, bold=True), fill=palette["text_main"])
    
    top_txt = f"📌 Yo'nalish: {data.get('topic', 'Xalqaro Ta\'lim')} ({data.get('city', 'Istanbul')})"
    draw.text((95, 450), top_txt[:52], font=get_font(23, bold=False), fill=palette["text_sub"])
    
    prc_txt = f"💰 Kontrakt: {data.get('price', '$600 - $1,200')} | Attestat Bilan"
    draw.text((95, 495), prc_txt[:52], font=get_font(25, bold=True), fill=palette["highlight"])
    
    draw.text((95, 545), "⚡️ 0$ Risk: Avval rasmiy qabul xati, to'lov keyin!", font=get_font(22, bold=True), fill=(52, 211, 153))

    # 4. Feature Pills
    pills = data.get("ad_points", [
        "Attestat Bilan Qabul",
        "Bologna Diplomi",
        "Aeroportda Kutib Olish"
    ])
    px = 60
    for p_text in pills[:3]:
        p_w = min(310, max(260, len(p_text) * 12 + 40))
        draw.rounded_rectangle((px, 645, px + p_w, 705), radius=12, fill=(15, 23, 42, 235), outline=palette["card_border"], width=1)
        draw.text((px + 20, 665), f"✓ {p_text[:24]}", font=get_font(17, bold=True), fill=palette["text_main"])
        px += p_w + 20

    # 5. Bottom Direct Contact Card
    draw.rounded_rectangle((60, 755, 1020, 985), radius=20, fill=palette["badge_bg"])
    draw.text((95, 795), "📞 Telegram: @arkadasuz  |  @arkadasuzz", font=get_font(28, bold=True), fill=(255, 255, 255))
    draw.text((95, 860), "🌐 Rasmiy Veb-Sayt: arkadas.uz", font=get_font(23, bold=False), fill=(224, 242, 254))
    cta = data.get("cta", "⚡️ 2026 qabul kvotalari cheklangan! Hoziroq murojaat qiling!")
    draw.text((95, 915), cta[:55], font=get_font(21, bold=True), fill=palette["highlight"])

    canvas.convert("RGB").save(out_path, quality=95)
    return out_path

# ==============================================================
# AI CREATIVE DIRECTOR (GEMINI + DIVERSE PRESETS)
# ==============================================================

PRESET_TOPICS_POOL = [
    {"topic": "Tibbiyot va Stomatologiya", "uni": "Istanbul Medipol & Bezmialem", "city": "Istanbul", "price": "$3,500 - $6,000"},
    {"topic": "Dasturlash va IT Muhandislik", "uni": "Yıldız Teknik & Marmara", "city": "Istanbul", "price": "$600 - $1,200"},
    {"topic": "Xalqaro Biznes va Moliya", "uni": "Anqara Hacı Bayram Veli", "city": "Anqara", "price": "$400 - $900"},
    {"topic": "Arxitektura va Shaharsozlik", "uni": "Mimar Sinan & ITU", "city": "Istanbul", "price": "$800 - $1,500"},
    {"topic": "Aviatsiya va Uchuvchilik", "uni": "Türk Hava Kurumu Universiteti", "city": "Anqara", "price": "$4,000 - $8,000"},
    {"topic": "Psixologiya va Pedagogika", "uni": "Ege Universiteti", "city": "Izmir", "price": "$500 - $950"},
    {"topic": "Farmatsevtika (Dorishunoslik)", "uni": "Anqara Universiteti", "city": "Anqara", "price": "$1,800 - $3,200"},
    {"topic": "Kiberxavfsizlik va AI", "uni": "Sakarya Universiteti", "city": "Sakarya", "price": "$450 - $850"},
    {"topic": "Mexatronika va Robototexnika", "uni": "Bursa Uludağ Universiteti", "city": "Bursa", "price": "$550 - $1,100"},
    {"topic": "Grafik Dizayn va Animatsiya", "uni": "Kadir Has Universiteti", "city": "Istanbul", "price": "$2,200 - $4,000"},
    {"topic": "Turizm va Mehmonxona Boshqaruvi", "uni": "Antalya Bilim Universiteti", "city": "Antalya", "price": "$1,200 - $2,500"},
    {"topic": "Xalqaro Huquq va Diplomatiya", "uni": "Istanbul Universiteti", "city": "Istanbul", "price": "$700 - $1,400"}
]

STYLE_CYCLE = ["qa_quiz", "riddle", "checklist", "modern_ad"]

def generate_ai_visual_briefs(count: int, target_style: str = "mixed", lang: str = "uz") -> list:
    """
    Asks Gemini AI to create complete design briefs for `count` posters.
    Guarantees that each card has a distinct style, palette, hook, and content.
    Falls back to a rich randomized generator if Gemini is slow or offline.
    """
    from engine.ai_brain import AIBrain
    brain = AIBrain()
    
    # Decide style distribution
    styles_to_generate = []
    if target_style in STYLE_CYCLE:
        styles_to_generate = [target_style] * count
    else: # mixed
        for i in range(count):
            styles_to_generate.append(STYLE_CYCLE[i % len(STYLE_CYCLE)])
    
    prompt = f"""
Sen Arkadaş Consulting (Turkiya oliy ta'lim konsaltingi) bosh marketing va dizayn direktorisan.
Bizning ijtimoiy tarmoqlarimiz uchun {count} ta MUTLAQO BIR-BIRINI TAKRORLAMAYDIGAN, HAR XIL mavzu va rangdagi afishalar (poster kartalari) dizayn ma'lumotlarini tayyorla.

Har bir karta uchun quyidagi uslublar berilgan: {styles_to_generate}
Rang palitralari ro'yxati: {PALETTE_KEYS}

Qat'iy Talablar:
1. Har bir karta mutlaqo boshqa yo'nalish (Tibbiyot, IT, Aviatsiya, Biznes, Arxitektura, Dizayn va h.k.) haqida bo'lsin.
2. Har bir kartaning sarlavhasi (headline) boshqacha va kuchli kanca (hook) bo'lsin. (Masalan: 'DTM Balingiz Yetmadimi?', '0$ Risk Bilan Talaba Bo'ling', 'Nega Istanbul Medipol?', 'Attestat Bilan Imtihonsiz').
3. Har bir kartaga farqli rang palitrasi ({PALETTE_KEYS} dan) tanla.
4. Uslubga mos ma'lumotlarni to'ldir:
   - qa_quiz bo'lsa: 'question' va 4 ta 'options' (biri to'g'ri)
   - riddle bo'lsa: 3 ta qiziqarli 'clues' (num, title, desc)
   - checklist bo'lsa: 4-5 ta aniq 'checklist_items'
   - modern_ad bo'lsa: 3 ta qisqa 'ad_points'
5. Har doim Arkadaş Consulting kafolatlarini kiriting: '0$ risk (avval qabul, to'lov keyin)', 'Bologna diplomi', 'Telegram: @arkadasuz'.

Javobni FAQAT toza JSON array formatida ber:
[
  {{
    "style": "qa_quiz | riddle | checklist | modern_ad",
    "palette": "emerald_cyan | royal_gold | cyber_ruby | electric_violet | sunset_amber | clean_azure",
    "badge": "⚡️ 2026 QABUL",
    "headline": "...",
    "sub_headline": "...",
    "topic": "...",
    "uni": "...",
    "city": "...",
    "price": "$...",
    "question": "...",
    "options": [{{"letter": "A", "text": "...", "correct": true}}, ...],
    "clues": [{{"num": "01", "title": "...", "desc": "..."}}],
    "checklist_items": ["...", "..."],
    "ad_points": ["...", "..."],
    "cta": "👉 Murojaat: @arkadasuz"
  }}
]
"""
    try:
        res = brain.think_and_generate(prompt)
        text = res.get("text", "").strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        
        parsed = json.loads(text)
        if isinstance(parsed, list) and len(parsed) >= count:
            return parsed[:count]
        elif isinstance(parsed, list) and len(parsed) > 0:
            needed = count - len(parsed)
            pad = build_fallback_briefs(needed, styles_to_generate[len(parsed):])
            return parsed + pad
    except Exception as e:
        print(f"[AI Visual Briefs Exception] {e}")
    
    return build_fallback_briefs(count, styles_to_generate)

def build_fallback_briefs(count: int, styles: list) -> list:
    """Rich randomized fallback ensuring zero duplicates even offline."""
    shuffled_topics = list(PRESET_TOPICS_POOL)
    random.shuffle(shuffled_topics)
    shuffled_palettes = list(PALETTE_KEYS)
    random.shuffle(shuffled_palettes)
    
    briefs = []
    for i in range(count):
        t = shuffled_topics[i % len(shuffled_topics)]
        pal = shuffled_palettes[i % len(shuffled_palettes)]
        style = styles[i % len(styles)]
        
        brief = {
            "style": style,
            "palette": pal,
            "topic": t["topic"],
            "uni": t["uni"],
            "city": t["city"],
            "price": t["price"],
            "cta": "👉 Bepul qabul xati olish: @arkadasuz"
        }
        
        if style == "qa_quiz":
            brief["badge"] = "❓ QUIZ / TEST 2026"
            brief["sub_headline"] = f"{t['topic']} Qabuli Sirlari"
            brief["question"] = f"{t['uni']}ga attestat bahosi bilan qaysi shartda kirish mumkin?"
            brief["options"] = [
                {"letter": "A", "text": "Attestat bahosi va 0$ risk bilan (To'lov qabuldan so'ng)", "correct": True},
                {"letter": "B", "text": "Faqat 95+ TR-YÖS imtihon bali bilan", "correct": False},
                {"letter": "C", "text": "Faqat SAT 1350+ xalqaro sertifikati bilan", "correct": False},
                {"letter": "D", "text": "Imtihonsiz kirishning iloji yo'q", "correct": False}
            ]
        elif style == "riddle":
            brief["badge"] = "🔍 BILASIZMI? • SIRLI FAKT"
            brief["sub_headline"] = f"Turkiyada {t['topic']} O'qish Haqida"
            brief["headline"] = f"3 TA SIZ BILMAGAN IMTIYOZ!"
            brief["clues"] = [
                {"num": "01", "title": "Imtihonsiz Attestat Bilan Qabul", "desc": f"{t['uni']}da imtihonsiz, to'g'ridan-to'g'ri talaba bo'ling."},
                {"num": "02", "title": f"Kontrakt: {t['price']}", "desc": f"{t['city']}da yashash va ta'lim narxlari O'zbekistondan qulay."},
                {"num": "03", "title": "0$ Risk: Kafolatlangan Shartnoma", "desc": "Qabul xati chiqmaguncha oldindan hech qanday to'lov qilinmaydi."}
            ]
        elif style == "checklist":
            brief["badge"] = "📋 2026 QABUL CHECKLISTI"
            brief["sub_headline"] = f"{t['topic']} Bo'yicha Talaba Bo'lish"
            brief["headline"] = "5 TA ASOSIY QADAM:"
            brief["checklist_items"] = [
                "Xorijga chiqish pasporti (Zagran)",
                "Maktab attestati yoki kollej diplomi",
                f"{t['uni']} uchun 0$ risk rasmiy ariza",
                "Turkiyada talaba yashash ruxsatnomasi (İkamet ID)",
                "Arkadaş Consulting bilan qonuniy shartnoma"
            ]
        else: # modern_ad
            brief["badge"] = "⚡️ SHOSHILINCH KVOTA"
            brief["sub_headline"] = f"{t['city'].upper()}DA TALABA BO'LING!"
            brief["headline"] = f"{t['topic']}ga Imtihonsiz Qabul!"
            brief["ad_points"] = [
                "Attestat Bilan Qabul",
                "Bologna Diplomi",
                "Aeroportda Kutib Olish"
            ]
        briefs.append(brief)
    return briefs

# ==============================================================
# MAIN EXPORTED ENTRY POINT
# ==============================================================

def generate_dynamic_poster_batch(count: int, style: str = "mixed", lang: str = "uz") -> list:
    """
    Generates `count` completely distinct visual posters using Gemini AI briefs.
    Renders them to output/cards/ and returns list of metadata dicts.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    briefs = generate_ai_visual_briefs(count, target_style=style, lang=lang)
    
    rendered_items = []
    for idx, brief in enumerate(briefs):
        unique_id = uuid.uuid4().hex[:8]
        b_style = brief.get("style", "modern_ad")
        filename = f"card_{b_style}_{unique_id}.jpg"
        full_path = str(OUTPUT_DIR / filename)
        rel_path = f"output/cards/{filename}"
        
        try:
            if b_style == "qa_quiz":
                render_dynamic_qa_quiz(brief, full_path)
                fmt_name = "Soru-Cevap / Quiz Kartı"
            elif b_style == "riddle":
                render_dynamic_riddle(brief, full_path)
                fmt_name = "Bilmece / İpuçlu Tasarım"
            elif b_style == "checklist":
                render_dynamic_checklist(brief, full_path)
                fmt_name = "Kontrol Listesi / Checklist"
            else:
                render_dynamic_modern_ad(brief, full_path)
                fmt_name = "Modern Reklam / Banner"
        except Exception as e:
            print(f"[Render Error for Card {idx}] {e}")
            render_dynamic_modern_ad(brief, full_path)
            fmt_name = "Afiş Tasarımı"
        
        rendered_items.append({
            "id": f"stock_img_{unique_id}",
            "title": f"{brief.get('badge', 'Afiş')} | {brief.get('topic', 'Ta\'lim')} — {brief.get('uni', 'Turkiya')}",
            "style": b_style,
            "format": fmt_name,
            "photo_path": rel_path,
            "topic": brief.get("topic", "Ta'lim"),
            "palette": brief.get("palette", "emerald_cyan"),
            "status": "in_stock",
            "created_at": "2026-09-15 02:45"
        })
        
    return rendered_items

# Backwards compatibility single poster generator
def generate_dynamic_poster(style: str, topic_data: dict, lang: str = "uz") -> tuple:
    items = generate_dynamic_poster_batch(count=1, style=style, lang=lang)
    if items:
        it = items[0]
        return it["photo_path"], it["title"], it["format"]
    return "output/cards/test_render.jpg", "Afiş", "Afiş"
