#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
engine/dynamic_poster_generator.py
Renders genuine high-resolution (1080x1080) branded visual posters with PIL.
Never reuses old static files; generates fresh unique graphics with custom typography,
background scenery, frosted overlays, and Arkadaş Consulting branding.
"""

import os
import uuid
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output" / "cards"
ASSETS_DIR = BASE_DIR / "assets"
SCENERY_DIR = ASSETS_DIR / "scenery"
LOGO_WHITE_PATH = ASSETS_DIR / "logo_white.png"

def get_font(size: int, bold: bool = False, serif: bool = False) -> ImageFont.FreeTypeFont:
    """Safely loads system fonts with fallbacks."""
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

def load_random_background(width: int, height: int, blur: int = 6) -> Image.Image:
    """Loads a random scenery image and crops/resizes/blurs it as a background."""
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
    canvas = Image.new("RGBA", (width, height), (15, 23, 42, 255))
    return canvas

def paste_logo(canvas: Image.Image, x: int, y: int, target_w: int = 180):
    """Pastes official Arkadaş white logo if available."""
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
    draw.text((x, y), "ARKADAŞ", font=get_font(28, bold=True), fill=(56, 189, 248))
    return 30

def render_poster_qa_quiz(topic_data: dict, out_path: str) -> str:
    """Style 1: Soru-Cevap / Quiz Kartı (Interactive test format)"""
    w, h = 1080, 1080
    bg = load_random_background(w, h, blur=8)
    
    overlay = Image.new("RGBA", (w, h), (10, 15, 30, 210))
    canvas = Image.alpha_composite(bg, overlay)
    draw = ImageDraw.Draw(canvas)

    paste_logo(canvas, 60, 60, target_w=190)
    draw.rounded_rectangle((780, 60, 1020, 105), radius=8, fill=(30, 58, 138, 240), outline=(56, 189, 248, 180), width=1)
    draw.text((800, 72), "QUIZ / TEST 2026", font=get_font(16, bold=True), fill=(56, 189, 248))

    draw.rounded_rectangle((60, 160, 1020, 360), radius=20, fill=(15, 23, 42, 230), outline=(56, 189, 248, 100), width=2)
    draw.text((100, 195), "SAVOL / VAZIFA:", font=get_font(18, bold=True), fill=(251, 191, 36))
    
    q_text = f"Turkiyada {topic_data['topic']} fakultetiga\nattestat bahosi bilan qaysi universitetda o'qish mumkin?"
    draw.text((100, 235), q_text, font=get_font(30, bold=True), fill=(255, 255, 255), spacing=10)

    options = [
        ("A", f"{topic_data['uni']} ({topic_data['city']})", True),
        ("B", "Istanbul Teknik Universiteti (TR-YÖS 95+)", False),
        ("C", "Anqara Davlat Universiteti (SAT 1300+)", False),
        ("D", "Barcha javoblar to'g'ri", False)
    ]

    oy = 400
    for letter, text, is_highlight in options:
        card_fill = (22, 101, 52, 220) if is_highlight else (30, 41, 59, 200)
        border_col = (74, 222, 128, 220) if is_highlight else (255, 255, 255, 30)
        
        draw.rounded_rectangle((60, oy, 1020, oy + 90), radius=14, fill=card_fill, outline=border_col, width=2)
        draw.ellipse([85, oy + 20, 135, oy + 70], fill=(255, 255, 255, 30))
        draw.text((100, oy + 28), letter, font=get_font(24, bold=True), fill=(255, 255, 255))
        
        draw.text((160, oy + 30), text, font=get_font(24, bold=is_highlight), fill=(255, 255, 255))
        if is_highlight:
            draw_vector_check(draw, 950, oy + 26, size=36)
        oy += 115

    draw.rounded_rectangle((60, 900, 1020, 1000), radius=16, fill=(15, 23, 42, 250), outline=(56, 189, 248, 120), width=1)
    draw.text((90, 930), "👉 To'g'ri javobni tanlab, bepul qabul xatiga ega bo'ling: @arkadasuz", font=get_font(21, bold=True), fill=(56, 189, 248))

    canvas.convert("RGB").save(out_path, quality=95)
    return out_path

def render_poster_riddle(topic_data: dict, out_path: str) -> str:
    """Style 2: Bilmece / İpuçlu Tasarım (Mystery & Facts)"""
    w, h = 1080, 1080
    bg = load_random_background(w, h, blur=5)
    
    overlay = Image.new("RGBA", (w, h), (15, 10, 35, 220))
    canvas = Image.alpha_composite(bg, overlay)
    draw = ImageDraw.Draw(canvas)

    paste_logo(canvas, 60, 60, target_w=190)

    draw.rounded_rectangle((60, 170, 360, 220), radius=8, fill=(147, 51, 234, 220))
    draw.text((80, 182), "🔍 BILASIZMI? • SIRLI FAKT", font=get_font(17, bold=True), fill=(255, 255, 255))

    draw.text((60, 250), f"Turkiyada {topic_data['topic']} o'qish haqida", font=get_font(26, bold=False), fill=(203, 213, 225))
    draw.text((60, 295), "3 TA SIZ BILMAGAN SIR!", font=get_font(46, bold=True), fill=(244, 63, 94))

    clues = [
        ("01", "Imtihonsiz kirish", f"{topic_data['uni']}da imtihonsiz, faqat attestat bilan to'g'ridan-to'g'ri qabul qilinadi!"),
        ("02", "Kontrakt afzalligi", f"Yillik kontrakt narxi bor-yo'g'i {topic_data['price']}. DTMdan 3 barobar arzon!"),
        ("03", "150+ Davlatda Tan Olinadi", "Bologna tizimi diplomi O'zbekistonda ham, butun Yevropada ham 100% akkreditatsiyadan o'tadi.")
    ]

    cy = 410
    for num, header, desc in clues:
        draw.rounded_rectangle((60, cy, 1020, cy + 130), radius=16, fill=(24, 24, 47, 230), outline=(168, 85, 247, 100), width=1)
        draw.text((90, cy + 25), num, font=get_font(32, bold=True), fill=(168, 85, 247))
        draw.text((170, cy + 25), header, font=get_font(24, bold=True), fill=(255, 255, 255))
        draw.text((170, cy + 65), desc, font=get_font(18, bold=False), fill=(203, 213, 225))
        cy += 155

    draw.rounded_rectangle((60, 910, 1020, 1000), radius=16, fill=(15, 23, 42, 240), outline=(244, 63, 94, 120), width=1)
    draw.text((90, 940), "💡 Sirni yechish va 2026 qabuliga yozilish: @arkadasuz", font=get_font(22, bold=True), fill=(255, 255, 255))

    canvas.convert("RGB").save(out_path, quality=95)
    return out_path

def render_poster_checklist(topic_data: dict, out_path: str) -> str:
    """Style 3: Kontrol Listesi / Checklist (5 Altın Belge)"""
    w, h = 1080, 1080
    bg = load_random_background(w, h, blur=7)
    
    overlay = Image.new("RGBA", (w, h), (8, 25, 30, 225))
    canvas = Image.alpha_composite(bg, overlay)
    draw = ImageDraw.Draw(canvas)

    paste_logo(canvas, 60, 60, target_w=190)

    draw.rounded_rectangle((60, 160, 420, 210), radius=8, fill=(16, 185, 129, 220))
    draw.text((80, 172), "✅ 2026 QABUL CHECKLISTI", font=get_font(18, bold=True), fill=(255, 255, 255))

    draw.text((60, 235), f"{topic_data['topic']} Bo'yicha Talaba Bo'lish Uchun", font=get_font(24, bold=False), fill=(203, 213, 225))
    draw.text((60, 280), "5 TA ASOSIY TALAB:", font=get_font(46, bold=True), fill=(52, 211, 153))

    items = [
        "Xorijga chiqish pasporti (Zagran)",
        "Maktab attestati yoki litsey/kollej diplomi",
        f"{topic_data['uni']} uchun 0$ risk qabul arizasi",
        "Turkiyada yashash ruxsatnomasi (İkamet ID) kafolati",
        "Arkadaş Consulting bilan rasmiy yuridik shartnoma"
    ]

    iy = 385
    for item_text in items:
        draw.rounded_rectangle((60, iy, 1020, iy + 85), radius=14, fill=(15, 35, 40, 220), outline=(52, 211, 153, 90), width=1)
        draw_vector_check(draw, 90, iy + 24, size=36, color=(16, 185, 129))
        draw.text((150, iy + 26), item_text, font=get_font(22, bold=True), fill=(255, 255, 255))
        iy += 105

    draw.rounded_rectangle((60, 930, 1020, 1010), radius=14, fill=(15, 23, 42, 240), outline=(52, 211, 153, 140), width=1)
    draw.text((90, 955), "📲 Ro'yxatdan o'tish va hujjat topshirish: @arkadasuz", font=get_font(22, bold=True), fill=(52, 211, 153))

    canvas.convert("RGB").save(out_path, quality=95)
    return out_path

def render_poster_modern_ad(topic_data: dict, out_path: str) -> str:
    """Style 4: Modern Reklam / Banner (High-Impact Acceptance Banner)"""
    w, h = 1080, 1080
    bg = load_random_background(w, h, blur=3)
    
    overlay = Image.new("RGBA", (w, h), (15, 23, 42, 220))
    canvas = Image.alpha_composite(bg, overlay)
    draw = ImageDraw.Draw(canvas)

    paste_logo(canvas, 60, 60, target_w=200)

    draw.rounded_rectangle((740, 60, 1020, 110), radius=8, fill=(239, 68, 68, 230))
    draw.text((765, 73), "RASMIY QABUL 2026", font=get_font(18, bold=True), fill=(255, 255, 255))

    draw.text((60, 175), "TURKIYADA", font=get_font(52, bold=True), fill=(239, 68, 68))
    draw.text((60, 245), "Imtihonsiz Talaba Bo'ling!", font=get_font(44, bold=True), fill=(255, 255, 255))

    draw.rounded_rectangle((60, 345, 1020, 620), radius=20, fill=(30, 41, 59, 230), outline=(56, 189, 248, 140), width=2)
    
    draw.text((100, 380), "OTM & YO'NALISH:", font=get_font(18, bold=True), fill=(56, 189, 248))
    draw.text((100, 420), f"🎓 {topic_data['uni']}", font=get_font(32, bold=True), fill=(255, 255, 255))
    draw.text((100, 475), f"📌 Yo'nalish: {topic_data['topic']} ({topic_data['city']})", font=get_font(24, bold=False), fill=(203, 213, 225))
    draw.text((100, 520), f"💰 Yillik Kontrakt: {topic_data['price']}", font=get_font(26, bold=True), fill=(251, 191, 36))
    draw.text((100, 565), "⚡️ 0$ Risk: Avval qabul xati chiqadi, to'lov keyin!", font=get_font(22, bold=True), fill=(52, 211, 153))

    pills = ["Attestat bilan Qabul", "Bologna Diplomi", "Aeroportda Kutib Olish"]
    px = 60
    for p_text in pills:
        draw.rounded_rectangle((px, 660, px + 300, 720), radius=12, fill=(15, 23, 42, 230), outline=(255, 255, 255, 40), width=1)
        draw.text((px + 25, 680), f"✓ {p_text}", font=get_font(18, bold=True), fill=(255, 255, 255))
        px += 330

    draw.rounded_rectangle((60, 770, 1020, 990), radius=20, fill=(2, 132, 199, 230))
    draw.text((100, 810), "📞 Telegram: @arkadasuz  |  @arkadasuzz", font=get_font(30, bold=True), fill=(255, 255, 255))
    draw.text((100, 875), "🌐 Rasmiy Veb-Sayt: arkadas.uz", font=get_font(24, bold=False), fill=(224, 242, 254))
    draw.text((100, 925), "⚡️ Joylar soni cheklangan! Shoshiling!", font=get_font(22, bold=True), fill=(254, 240, 138))

    canvas.convert("RGB").save(out_path, quality=95)
    return out_path

def generate_dynamic_poster(style: str, topic_data: dict, lang: str = "uz") -> tuple:
    """
    Main entry point: Generates a brand new custom visual poster card.
    Returns (relative_file_path, title, format_name).
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    unique_id = uuid.uuid4().hex[:8]
    filename = f"card_{style}_{unique_id}.jpg"
    full_path = str(OUTPUT_DIR / filename)
    rel_path = f"output/cards/{filename}"

    if style == "qa_quiz":
        render_poster_qa_quiz(topic_data, full_path)
        title = f"🎯 Quiz: {topic_data['topic']} — {topic_data['uni']}"
        fmt_name = "Soru-Cevap / Quiz Kartı"
    elif style == "riddle":
        render_poster_riddle(topic_data, full_path)
        title = f"🔍 Bilmece: {topic_data['topic']} — 3 Gizli Gerçek"
        fmt_name = "Bilmece / İpuçlu Tasarım"
    elif style == "checklist":
        render_poster_checklist(topic_data, full_path)
        title = f"✅ Checklist: {topic_data['topic']} İçin 5 Altın Belge"
        fmt_name = "Kontrol Listesi / Checklist"
    else: # modern_ad
        render_poster_modern_ad(topic_data, full_path)
        title = f"📢 Reklam: {topic_data['city']}da {topic_data['topic']} Qabuli"
        fmt_name = "Modern Reklam / Banner"

    return rel_path, title, fmt_name
