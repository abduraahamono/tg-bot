#!/usr/bin/env python3
"""
engine/visual_card_generator.py
Generates high-resolution (1080x1350) branded visual cards for Telegram, Instagram, and Twitter.
Zero false claims, 100% professional typography, Turkish scenery/campus backdrops, and official @arkadasuzz branding.
"""

import os
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "output" / "cards"
ASSETS_DIR = BASE_DIR / "assets"
SCENERY_DIR = ASSETS_DIR / "scenery"

def get_font(name: str, size: int) -> ImageFont.FreeTypeFont:
    font_paths = [
        f"/System/Library/Fonts/Supplemental/{name}",
        f"/System/Library/Fonts/{name}",
        f"/Library/Fonts/{name}"
    ]
    for p in font_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    for fb in ['/System/Library/Fonts/Supplemental/Arial Bold.ttf', '/System/Library/Fonts/Helvetica.ttc']:
        if os.path.exists(fb):
            return ImageFont.truetype(fb, size)
    return ImageFont.load_default()

def draw_checkmark(draw: ImageDraw.ImageDraw, x: int, y: int, size: int = 36, fill: tuple = (46, 204, 113)):
    """Draws a crisp vector checkmark badge without relying on emojis."""
    draw.ellipse([x, y, x + size, y + size], fill=fill)
    line_w = max(3, int(size * 0.12))
    p1 = (x + size * 0.28, y + size * 0.52)
    p2 = (x + size * 0.44, y + size * 0.72)
    p3 = (x + size * 0.74, y + size * 0.32)
    draw.line([p1, p2], fill=(255, 255, 255), width=line_w)
    draw.line([p2, p3], fill=(255, 255, 255), width=line_w)

def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.ImageDraw) -> list:
    """Wraps text into lines that fit within max_width."""
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))
    return lines

def create_branded_card(
    category: str,
    title: str,
    bullets: list,
    output_filename: str,
    bg_choice: str = None
) -> str:
    """
    Creates a 1080x1350 vertical high-resolution card.
    bullets: list of tuples -> [("Header", "Description"), ...]
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    width, height = 1080, 1350

    # 1. Background image
    scenery_files = list(SCENERY_DIR.glob("*.jpg"))
    bg_file = None
    if bg_choice and (SCENERY_DIR / bg_choice).exists():
        bg_file = SCENERY_DIR / bg_choice
    elif scenery_files:
        bg_file = random.choice(scenery_files)

    if bg_file:
        try:
            bg = Image.open(bg_file).convert("RGB")
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
            bg = bg.filter(ImageFilter.GaussianBlur(radius=4))
        except Exception:
            bg = Image.new("RGB", (width, height), (15, 23, 42))
    else:
        bg = Image.new("RGB", (width, height), (15, 23, 42))

    # 2. Rich dark overlay
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw_over = ImageDraw.Draw(overlay)
    for y in range(height):
        alpha = int(140 + (y / height) * 90)  # 140 -> 230
        draw_over.line([(0, y), (width, y)], fill=(8, 16, 38, alpha))

    card = Image.alpha_composite(bg.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(card)

    # 3. Fonts
    font_brand = get_font("Arial Bold.ttf", 32)
    font_badge = get_font("Arial Bold.ttf", 24)
    font_cat = get_font("Arial Bold.ttf", 26)
    font_title = get_font("Arial Bold.ttf", 46)
    font_b_title = get_font("Arial Bold.ttf", 32)
    font_b_desc = get_font("Helvetica.ttc", 28)
    font_footer = get_font("Arial Bold.ttf", 28)

    # 4. Top Bar: Brand Pill (Left) & Turkey Flag Badge (Right)
    draw.rounded_rectangle([70, 65, 460, 130], radius=32, fill=(255, 255, 255, 240))
    logo_path = ASSETS_DIR / "logo_transparent.png"
    if logo_path.exists():
        try:
            logo = Image.open(logo_path).convert("RGBA")
            logo = logo.resize((150, 54), Image.Resampling.LANCZOS)
            card.paste(logo, (90, 71), logo)
            draw.text((255, 82), "CONSULTING", font=font_brand, fill=(18, 28, 55))
        except Exception:
            draw.text((100, 80), "ARKADAŞ CONSULTING", font=font_brand, fill=(18, 28, 55))
    else:
        draw.text((100, 80), "ARKADAŞ CONSULTING", font=font_brand, fill=(18, 28, 55))

    # Right Badge
    draw.rounded_rectangle([720, 65, 1010, 130], radius=32, fill=(20, 45, 90, 220), outline=(55, 110, 210), width=2)
    draw.text((750, 82), "RASMIY QABUL 2025", font=font_badge, fill=(240, 246, 255))

    # 5. Category Pill
    cat_clean = category.replace("💡", "").replace("🛡️", "").replace("📊", "").replace("⚖️", "").replace("🏛️", "").replace("🤝", "").replace("🎯", "").replace("🌍", "").replace("🏠", "").replace("📋", "").replace("🌟", "").replace("🏥", "").replace("💳", "").replace("❓", "").strip().upper()
    cat_y = 190
    c_bbox = draw.textbbox((0, 0), cat_clean, font=font_cat)
    cat_w = (c_bbox[2] - c_bbox[0]) + 50
    draw.rounded_rectangle([70, cat_y, 70 + cat_w, cat_y + 54], radius=27, fill=(235, 55, 55))
    draw.text((95, cat_y + 13), cat_clean, font=font_cat, fill=(255, 255, 255))

    # 6. Main Content Box
    box_x1, box_y1 = 70, 275
    box_x2, box_y2 = 1010, 1160
    draw.rounded_rectangle([box_x1, box_y1, box_x2, box_y2], radius=28, fill=(14, 24, 52, 230), outline=(42, 75, 135), width=2)

    # Title inside box
    title_lines = wrap_text(title, font_title, box_x2 - box_x1 - 80, draw)
    t_y = box_y1 + 45
    for t_line in title_lines[:3]:
        draw.text((box_x1 + 45, t_y), t_line, font=font_title, fill=(255, 255, 255))
        t_y += 58

    # Accent Divider
    t_y += 10
    draw.line([(box_x1 + 45, t_y), (box_x2 - 45, t_y)], fill=(45, 80, 140), width=2)
    t_y += 35

    # Bullet Points
    bullet_y = t_y
    for b_head, b_desc in bullets[:4]:
        draw_checkmark(draw, box_x1 + 45, bullet_y + 2, size=36, fill=(46, 204, 113))
        draw.text((box_x1 + 96, bullet_y), b_head, font=font_b_title, fill=(75, 215, 130))
        
        desc_lines = wrap_text(b_desc, font_b_desc, box_x2 - box_x1 - 145, draw)
        d_y = bullet_y + 44
        for d_line in desc_lines[:2]:
            draw.text((box_x1 + 96, d_y), d_line, font=font_b_desc, fill=(215, 230, 245))
            d_y += 36
        
        bullet_y += 118

    # 7. Bottom Contact Pill
    draw.rounded_rectangle([70, 1200, 1010, 1285], radius=42, fill=(28, 120, 242))
    draw.text((115, 1228), "Telegram: @arkadasuzz  |  Kanal: @arkadasuz", font=font_footer, fill=(255, 255, 255))
    draw.text((820, 1228), "arkadas.uz", font=font_footer, fill=(200, 230, 255))

    out_path = OUTPUT_DIR / output_filename
    card.convert("RGB").save(out_path, "PNG", quality=95)
    return str(out_path)
