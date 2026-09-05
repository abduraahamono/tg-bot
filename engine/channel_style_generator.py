#!/usr/bin/env python3
"""
channel_style_generator.py
Exact replication of authentic Telegram channel post cards from ChatExport:
1. Style 1: Q&A Dual Speech Bubbles (photo_137_0.jpg)
2. Style 2: Torn Sky-Blue Paper / Riddle (photo_100_0.jpg, photo_196_0.jpg)
3. Style 3: Split Campus Banner (photo_114_0.jpg)
4. Style 4: Real Student & Campus Feature (photo_247_0.jpg - photo_250_0.jpg)
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).parent.parent
ASSETS_DIR = BASE_DIR / "assets"
OUTPUT_DIR = BASE_DIR / "output" / "channel_samples"
SCENERY_DIR = ASSETS_DIR / "scenery"
PHOTOS_DIR = BASE_DIR / "ChatExport_Turkiyada ta'lim🇹🇷" / "photos"

def get_font(font_names, size: int):
    if isinstance(font_names, str):
        font_names = [font_names]
    candidate_dirs = [
        "/System/Library/Fonts/Supplemental",
        "/System/Library/Fonts",
        "/Library/Fonts"
    ]
    for name in font_names:
        for d in candidate_dirs:
            p = os.path.join(d, name)
            if os.path.exists(p):
                try:
                    return ImageFont.truetype(p, size)
                except Exception:
                    pass
    for fallback in ["Arial Bold.ttf", "Arial.ttf", "Helvetica.ttc"]:
        for d in candidate_dirs:
            p = os.path.join(d, fallback)
            if os.path.exists(p):
                try:
                    return ImageFont.truetype(p, size)
                except Exception:
                    pass
    return ImageFont.load_default()

def wrap_text(text: str, font: ImageFont.ImageFont, max_width: int, draw: ImageDraw.ImageDraw) -> list:
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if (bbox[2] - bbox[0]) <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
                current_line = [word]
            else:
                lines.append(word)
    if current_line:
        lines.append(" ".join(current_line))
    return lines

def draw_social_footer(img: Image.Image, draw: ImageDraw.ImageDraw, y_pos: int, dark_theme: bool = True):
    """Draws clean, professional social media bar at the bottom with no broken emoji glyphs."""
    font = get_font(["Arial Bold.ttf", "Helvetica.ttc"], 22)
    val_font = get_font(["Arial.ttf", "Helvetica.ttc"], 22)
    
    lbl_color = (200, 215, 245) if dark_theme else (90, 100, 120)
    val_color = (91, 163, 248) if dark_theme else (29, 83, 245)
    dot_color = (130, 145, 175) if dark_theme else (180, 190, 205)
    
    items = [
        ("Telegram:", "@arkadasuzz"),
        ("Kanal:", "@arkadasuz"),
        ("Instagram:", "@arkadasuz"),
        ("Web:", "arkadas.uz")
    ]
    
    parts = []
    for lbl, val in items:
        lw = draw.textbbox((0, 0), lbl + " ", font=font)[2] - draw.textbbox((0, 0), lbl + " ", font=font)[0]
        vw = draw.textbbox((0, 0), val, font=val_font)[2] - draw.textbbox((0, 0), val, font=val_font)[0]
        parts.append((lbl, val, lw, vw))
        
    sep = "   •   "
    sep_w = draw.textbbox((0, 0), sep, font=font)[2] - draw.textbbox((0, 0), sep, font=font)[0]
    total_w = sum(p[2] + p[3] for p in parts) + (len(parts) - 1) * sep_w
    start_x = (img.width - total_w) // 2
    
    curr_x = start_x
    for i, (lbl, val, lw, vw) in enumerate(parts):
        draw.text((curr_x, y_pos), lbl + " ", font=font, fill=lbl_color)
        curr_x += lw
        draw.text((curr_x, y_pos), val, font=val_font, fill=val_color)
        curr_x += vw
        if i < len(parts) - 1:
            draw.text((curr_x, y_pos), sep, font=font, fill=dot_color)
            curr_x += sep_w

# ========================================================
# 1. Q&A STYLE (Exact Match to photo_137_0.jpg)
# ========================================================
def generate_qa_card(
    question: str,
    answer: str,
    output_filename: str = "sample_style1_qa.png"
) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    width, height = 1080, 1350
    
    # Deep midnight navy background #070d24
    bg_color = (7, 13, 36)
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    badge_font = get_font(["Arial Bold.ttf", "Helvetica.ttc"], 36)
    q_font = get_font(["Georgia Bold.ttf", "Georgia.ttf"], 48)
    a_font = get_font(["Georgia.ttf", "Times New Roman.ttf"], 40)
    
    card_w = 840
    card_x = (width - card_w) // 2
    badge_w, badge_h = 380, 78
    badge_color = (29, 83, 245)  # Vibrant Royal Blue
    card_bg = (248, 249, 252)     # Off-white card
    
    # Question Card Layout
    q_lines = wrap_text(question, q_font, card_w - 120, draw)
    q_line_h = 60
    q_text_total_h = len(q_lines) * q_line_h
    q_card_h = max(240, q_text_total_h + 160)
    q_card_y = 230
    
    # Draw Q Card Background
    draw.rounded_rectangle([card_x, q_card_y, card_x + card_w, q_card_y + q_card_h], radius=40, fill=card_bg)
    # Draw Q Badge
    b_x = (width - badge_w) // 2
    b_y = q_card_y - (badge_h // 2)
    draw.rounded_rectangle([b_x, b_y, b_x + badge_w, b_y + badge_h], radius=39, fill=badge_color)
    b_bbox = draw.textbbox((0, 0), "Savol:", font=badge_font)
    draw.text((b_x + (badge_w - (b_bbox[2]-b_bbox[0]))//2, b_y + (badge_h - (b_bbox[3]-b_bbox[1]))//2 - 2), "Savol:", font=badge_font, fill=(255, 255, 255))
    
    # Draw Q Text
    cur_y = q_card_y + (q_card_h - q_text_total_h)//2 + 10
    for line in q_lines:
        bbox = draw.textbbox((0, 0), line, font=q_font)
        draw.text(((width - (bbox[2]-bbox[0]))//2, cur_y), line, font=q_font, fill=(15, 23, 42))
        cur_y += q_line_h
        
    # Answer Card Layout
    a_lines = wrap_text(answer, a_font, card_w - 120, draw)
    a_line_h = 54
    a_text_total_h = len(a_lines) * a_line_h
    a_card_h = max(320, a_text_total_h + 160)
    a_card_y = q_card_y + q_card_h + 90
    
    # Draw A Card
    draw.rounded_rectangle([card_x, a_card_y, card_x + card_w, a_card_y + a_card_h], radius=40, fill=card_bg)
    # Draw A Badge
    ab_y = a_card_y - (badge_h // 2)
    draw.rounded_rectangle([b_x, ab_y, b_x + badge_w, ab_y + badge_h], radius=39, fill=badge_color)
    ab_bbox = draw.textbbox((0, 0), "Javob:", font=badge_font)
    draw.text((b_x + (badge_w - (ab_bbox[2]-ab_bbox[0]))//2, ab_y + (badge_h - (ab_bbox[3]-b_bbox[1]))//2 - 2), "Javob:", font=badge_font, fill=(255, 255, 255))
    
    # Draw A Text
    cur_y = a_card_y + (a_card_h - a_text_total_h)//2 + 15
    for line in a_lines:
        bbox = draw.textbbox((0, 0), line, font=a_font)
        draw.text(((width - (bbox[2]-bbox[0]))//2, cur_y), line, font=a_font, fill=(20, 25, 40))
        cur_y += a_line_h
        
    # Logo Capsule at bottom
    logo_path = ASSETS_DIR / "logo_transparent.png"
    if logo_path.exists():
        logo = Image.open(logo_path).convert("RGBA")
        lw = 200
        lh = int(logo.height * (lw / logo.width))
        logo = logo.resize((lw, lh), Image.Resampling.LANCZOS)
        
        pill_w, pill_h = lw + 40, lh + 24
        px = (width - pill_w) // 2
        py = height - 190
        draw.rounded_rectangle([px, py, px + pill_w, py + pill_h], radius=28, fill=(255, 255, 255))
        img.paste(logo, (px + 20, py + 12), logo)
        
    draw_social_footer(img, draw, height - 90, dark_theme=True)
    out_path = OUTPUT_DIR / output_filename
    img.save(out_path, quality=95)
    return out_path

# ========================================================
# 2. TORN PAPER STYLE (Exact Match to photo_100_0.jpg)
# ========================================================
def generate_torn_paper_card(
    hook_text: str = "Buni o'qiy olasanmi?",
    sub_text: str = "Bunga to'g'ri javob bergan bo'lsang Arkadaş bilan Turkiyada ta'lim olishing mumkin",
    output_filename: str = "sample_style2_torn_paper.png"
) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    width, height = 1080, 1350
    
    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Ripped Blue Paper Sticker
    paper_path = ASSETS_DIR / "torn_blue_paper.png"
    if paper_path.exists():
        paper = Image.open(paper_path).convert("RGBA")
        pw = 900
        ph = int(paper.height * (pw / paper.width))
        paper = paper.resize((pw, ph), Image.Resampling.LANCZOS)
        px = (width - pw) // 2
        py = 220
        img.paste(paper, (px, py), paper)
    else:
        px, py, pw, ph = 90, 220, 900, 580
        draw.rounded_rectangle([px, py, px+pw, py+ph], radius=30, fill=(91, 163, 248))
        
    # Impact Condensed Black Font
    impact_font = get_font(["Impact.ttf", "Arial Black.ttf"], 72)
    lines = wrap_text(hook_text, impact_font, pw - 180, draw)
    line_h = 88
    tot_h = len(lines) * line_h
    start_y = py + (ph - tot_h) // 2
    
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=impact_font)
        lx = (width - (bbox[2] - bbox[0])) // 2
        draw.text((lx, start_y), line, font=impact_font, fill=(15, 20, 25))
        start_y += line_h
        
    # Georgia Italic Subtitle
    sub_font = get_font(["Georgia Italic.ttf", "Georgia.ttf"], 36)
    sub_lines = wrap_text(sub_text, sub_font, 780, draw)
    sy = py + ph + 80
    for line in sub_lines:
        bbox = draw.textbbox((0, 0), line, font=sub_font)
        lx = (width - (bbox[2] - bbox[0])) // 2
        draw.text((lx, sy), line, font=sub_font, fill=(60, 65, 75))
        sy += 50
        
    # Arkadaş Logo
    logo_path = ASSETS_DIR / "logo_transparent.png"
    if logo_path.exists():
        logo = Image.open(logo_path).convert("RGBA")
        lw = 240
        lh = int(logo.height * (lw / logo.width))
        logo = logo.resize((lw, lh), Image.Resampling.LANCZOS)
        lx = (width - lw) // 2
        ly = height - 230
        img.paste(logo, (lx, ly), logo)
        
    draw_social_footer(img, draw, height - 100, dark_theme=False)
    out_path = OUTPUT_DIR / output_filename
    img.save(out_path, quality=95)
    return out_path

# ========================================================
# 3. SPLIT BANNER STYLE (Exact Match to photo_114_0.jpg)
# ========================================================
def generate_split_banner_card(
    badge_label: str = "TURKIYADA",
    title: str = "XALQARO TA'LIM",
    description: str = "Chet elda o'qish - bu shunchaki ilmiy darajaga ega bo'lishdan ko'ra ko'proq, bu sizning kelajagingizni belgilaydigan hayotni o'zgartiruvchi sayohatdir.",
    bullets: list = None,
    photo_source: str = None,
    output_filename: str = "sample_style3_split_banner.png"
) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    width, height = 1080, 1350
    if bullets is None:
        bullets = [
            "Sifatli ta'lim",
            "Mustaqil hayot va o'sish",
            "Global istiqbol",
            "Karyera imkoniyatlari"
        ]
        
    # Deep royal blue container
    img = Image.new("RGB", (width, height), (39, 27, 135))
    draw = ImageDraw.Draw(img)
    
    # 1. Top Real Photo
    photo_h = 540
    if photo_source and Path(photo_source).exists():
        photo_path = Path(photo_source)
    else:
        # Fallback to campus or user's authentic photos
        photo_path = SCENERY_DIR / "campus_students.jpg"
        if not photo_path.exists():
            photo_path = PHOTOS_DIR / "photo_247_0.jpg"
        
    if photo_path.exists():
        top_img = Image.open(photo_path).convert("RGB")
        scale = max(width / top_img.width, photo_h / top_img.height)
        new_w, new_h = int(top_img.width * scale), int(top_img.height * scale)
        top_img = top_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        cx = (new_w - width) // 2
        cy = (new_h - photo_h) // 2
        top_crop = top_img.crop((cx, cy, cx + width, cy + photo_h))
        img.paste(top_crop, (0, 0))
        
    # 2. Bottom Container
    pill_font = get_font(["Impact.ttf", "Arial Black.ttf"], 44)
    p_bbox = draw.textbbox((0, 0), badge_label, font=pill_font)
    pw = (p_bbox[2] - p_bbox[0]) + 60
    ph = 64
    px = 60
    py = photo_h + 45
    draw.rounded_rectangle([px, py, px + pw, py + ph], radius=15, fill=(255, 255, 255))
    draw.text((px + 30, py + 8), badge_label, font=pill_font, fill=(20, 25, 35))
    
    title_font = get_font(["Impact.ttf", "Arial Black.ttf"], 68)
    draw.text((60, py + ph + 18), title, font=title_font, fill=(255, 255, 255))
    
    desc_font = get_font(["Arial.ttf", "Helvetica.ttc"], 26)
    d_lines = wrap_text(description, desc_font, 960, draw)
    dy = py + ph + 110
    for line in d_lines:
        draw.text((60, dy), line, font=desc_font, fill=(235, 240, 255))
        dy += 36
        
    # 3. Bullets in 2x2 Grid with '>'
    b_font = get_font(["Arial Bold.ttf", "Helvetica.ttc"], 28)
    col_w = 460
    badge_item_h = 58
    start_bx = 60
    start_by = dy + 35
    
    for i, item in enumerate(bullets[:4]):
        col = i % 2
        row = i // 2
        bx = start_bx + col * (col_w + 35)
        by = start_by + row * (badge_item_h + 20)
        draw.rounded_rectangle([bx, by, bx + col_w, by + badge_item_h], radius=14, fill=(255, 255, 255))
        draw.text((bx + 20, by + 12), ">", font=b_font, fill=(29, 83, 245))
        draw.text((bx + 48, by + 12), item, font=b_font, fill=(20, 25, 40))
        
    # 4. Bottom Footer Bar
    footer_y = height - 150
    # Left pill: Aloqa uchun ->
    c_pill_w, c_pill_h = 240, 60
    draw.rounded_rectangle([60, footer_y, 60 + c_pill_w, footer_y + c_pill_h], radius=30, fill=(255, 255, 255))
    btn_font = get_font(["Arial Bold.ttf", "Helvetica.ttc"], 24)
    draw.text((80, footer_y + 16), "Aloqa uchun ->", font=btn_font, fill=(20, 25, 40))
    
    ph_font = get_font(["Arial Bold.ttf", "Helvetica.ttc"], 22)
    draw.text((330, footer_y + 6), "+998 93 5999865", font=ph_font, fill=(255, 255, 255))
    draw.text((330, footer_y + 34), "@arkadasuzz", font=ph_font, fill=(200, 220, 255))
    
    logo_path = ASSETS_DIR / "logo_transparent.png"
    if logo_path.exists():
        logo = Image.open(logo_path).convert("RGBA")
        lw = 200
        lh = int(logo.height * (lw / logo.width))
        logo = logo.resize((lw, lh), Image.Resampling.LANCZOS)
        p_w, p_h = lw + 30, lh + 16
        rx = width - 60 - p_w
        draw.rounded_rectangle([rx, footer_y - 2, rx + p_w, footer_y + p_h], radius=20, fill=(255, 255, 255))
        img.paste(logo, (rx + 15, footer_y + 6), logo)
        
    draw_social_footer(img, draw, height - 55, dark_theme=True)
    out_path = OUTPUT_DIR / output_filename
    img.save(out_path, quality=95)
    return out_path

# ========================================================
# 4. REAL STUDENT FEATURE STYLE (photo_247_0.jpg)
# ========================================================
def generate_student_feature_card(
    photo_file: str = "photo_247_0.jpg",
    headline_lines: list = None,
    output_filename: str = "sample_style4_student.png"
) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    width, height = 1080, 1350
    
    base_photo = PHOTOS_DIR / photo_file
    if base_photo.exists():
        img = Image.open(base_photo).convert("RGB")
        img = img.resize((width, height), Image.Resampling.LANCZOS)
    else:
        img = Image.new("RGB", (width, height), (30, 70, 130))
        
    draw = ImageDraw.Draw(img)
    
    if headline_lines is None:
        headline_lines = ["Imkoniyatni", "boy", "bermang."]
        
    title_font = get_font(["Arial Bold.ttf", "HelveticaNeue.ttc"], 80)
    ty = 90
    for line in headline_lines:
        draw.text((70, ty), line, font=title_font, fill=(255, 255, 255))
        ty += 95
        
    logo_path = ASSETS_DIR / "logo_transparent.png"
    if logo_path.exists():
        logo = Image.open(logo_path).convert("RGBA")
        lw = 240
        lh = int(logo.height * (lw / logo.width))
        logo = logo.resize((lw, lh), Image.Resampling.LANCZOS)
        px = width - lw - 80
        py = height - lh - 120
        draw.rounded_rectangle([px - 20, py - 10, px + lw + 20, py + lh + 10], radius=24, fill=(255, 255, 255))
        img.paste(logo, (px, py), logo)
        
    draw_social_footer(img, draw, height - 60, dark_theme=False)
    out_path = OUTPUT_DIR / output_filename
    img.save(out_path, quality=95)
    return out_path

if __name__ == "__main__":
    generate_qa_card(
        question="Yashash joyi va ish ham bor mi?",
        answer="Ha, yashash joyi topishda yordam beramiz — talabalar uchun xavfsiz, hamyonbop yotoqxona variantlari beramiz.\n\nIsh topish bo'yicha ham maslahat va to'g'ri yo'nalish beramiz.",
        output_filename="sample_style1_qa.png"
    )
    generate_torn_paper_card(
        hook_text="Turk tilini bilmay talaba bo'la olasanmi?",
        sub_text="Bunga to'g'ri javob bergan bo'lsang Arkadaş bilan Turkiyada ta'lim olishing mumkin",
        output_filename="sample_style2_torn_paper.png"
    )
    generate_split_banner_card(
        badge_label="TURKIYADA",
        title="XALQARO TA'LIM",
        description="Chet elda o'qish - bu shunchaki diplom olish emas, balki kelajagingizni belgilaydigan eng muhim hayotiy qadamdir.",
        bullets=[
            "Sifatli ta'lim",
            "Mustaqil hayot va o'sish",
            "Global istiqbol",
            "Karyera imkoniyatlari"
        ],
        output_filename="sample_style3_split_banner.png"
    )
    generate_student_feature_card(
        photo_file="photo_247_0.jpg",
        headline_lines=["Imkoniyatni", "boy", "bermang."],
        output_filename="sample_style4_student.png"
    )
    print("ALL 4 SAMPLES GENERATED SUCCESSFULLY!")
