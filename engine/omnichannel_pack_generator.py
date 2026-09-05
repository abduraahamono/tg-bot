#!/usr/bin/env python3
"""
omnichannel_pack_generator.py
Generates full multi-format visual & copy packs for Arkadaş Consulting:
1. 4:5 Post Card (1080x1350) -> Telegram feed, Instagram feed, Facebook, Twitter, YouTube Community
2. 9:16 Story Card (1080x1920) -> Telegram channel stories, Instagram stories, TikTok stories
3. Platform-specific copywriting pack (Telegram, Twitter, Instagram, TikTok, Facebook)
"""

import os
import sys
import re
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))
from engine.omnichannel_formatter import format_multichannel_pack

ASSETS_DIR = BASE_DIR / "assets"
AI_PHOTOS_DIR = ASSETS_DIR / "ai_photos"
SCENERY_DIR = ASSETS_DIR / "scenery"
OUTPUT_POSTS = BASE_DIR / "output" / "posts"
OUTPUT_STORIES = BASE_DIR / "output" / "stories"
POSTS_JSON = BASE_DIR / "brain_data" / "scheduled_telegram_posts.json"

OUTPUT_POSTS.mkdir(parents=True, exist_ok=True)
OUTPUT_STORIES.mkdir(parents=True, exist_ok=True)

def clean_label(text: str) -> str:
    """Removes emojis and unsupported glyphs for clean text rendering in PIL."""
    cleaned = re.sub(r"[^\w\s\+\-\'\:\.\,]", "", text, flags=re.UNICODE).strip()
    return cleaned if cleaned else "ARKADAS CONSULTING"

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

def get_photo_for_post(post_id: str, slot: str, cat_tag: str) -> Path:
    """Selects best matching authentic/AI photo based on post topic."""
    tag_l = cat_tag.lower()
    p_id = post_id.lower()
    
    if "til" in tag_l or "tomer" in p_id:
        cand = AI_PHOTOS_DIR / "turkish_student_library_1788569959193.jpg"
        if cand.exists(): return cand
    if "hamrohlik" in tag_l or "eve" in p_id:
        cand = AI_PHOTOS_DIR / "student_acceptance_celebration_1788569980820.jpg"
        if cand.exists(): return cand
    if "xarajat" in tag_l or "byudjet" in tag_l:
        cand = AI_PHOTOS_DIR / "turkish_campus_life_1788571305737.jpg"
        if cand.exists(): return cand
    if "juma" in p_id or "juma" in tag_l:
        cand = SCENERY_DIR / "istanbul_mosque.jpg"
        if cand.exists(): return cand
        
    pool = [
        AI_PHOTOS_DIR / "turkish_campus_life_1788571305737.jpg",
        AI_PHOTOS_DIR / "student_acceptance_celebration_1788569980820.jpg",
        AI_PHOTOS_DIR / "turkish_student_library_1788569959193.jpg",
        AI_PHOTOS_DIR / "student_lifestyle_story_1788569998856.jpg",
        SCENERY_DIR / "campus_students.jpg",
        SCENERY_DIR / "galata_tower.jpg"
    ]
    existing = [p for p in pool if p.exists()]
    if existing:
        idx = hash(post_id) % len(existing)
        return existing[idx]
    return SCENERY_DIR / "campus_students.jpg"

# ========================================================
# 1. 4:5 POST GENERATOR (1080x1350)
# ========================================================
def generate_post_card_4_5(post: dict) -> Path:
    width, height = 1080, 1350
    post_id = post["id"]
    topic = post.get("topic", "Turkiyada Xalqaro Ta'lim")
    cat_tag = clean_label(post.get("cat_tag", "ARKADAŞ CONSULTING"))
    
    out_file = OUTPUT_POSTS / f"post_{post_id}.png"
    
    # Check if Q&A style is best suited (e.g. FAQ, Til & Qabul, Xarajat)
    is_qa = "savol" in topic.lower() or "haqiqati" in topic.lower() or "lun" in post_id
    
    if is_qa:
        # Style 1: Q&A Dual Card (Matches photo_137_0.jpg)
        bg_color = (7, 13, 36) # Deep midnight navy
        img = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(img)
        
        badge_font = get_font(["Arial Bold.ttf", "Helvetica.ttc"], 36)
        q_font = get_font(["Georgia Bold.ttf", "Georgia.ttf"], 44)
        a_font = get_font(["Georgia.ttf", "Times New Roman.ttf"], 36)
        
        card_w = 860
        card_x = (width - card_w) // 2
        badge_w, badge_h = 360, 74
        badge_color = (29, 83, 245)
        card_bg = (248, 249, 252)
        
        q_text = topic.split(":")[-1].strip() if ":" in topic else topic
        if len(q_text) > 85:
            q_text = q_text[:85] + "..."
        q_lines = wrap_text(q_text, q_font, card_w - 100, draw)
        q_card_h = max(240, len(q_lines) * 58 + 150)
        q_card_y = 220
        
        draw.rounded_rectangle([card_x, q_card_y, card_x + card_w, q_card_y + q_card_h], radius=36, fill=card_bg)
        bx = (width - badge_w) // 2
        by = q_card_y - (badge_h // 2)
        draw.rounded_rectangle([bx, by, bx + badge_w, by + badge_h], radius=37, fill=badge_color)
        b_bbox = draw.textbbox((0, 0), "Savol:", font=badge_font)
        draw.text((bx + (badge_w - (b_bbox[2]-b_bbox[0]))//2, by + 16), "Savol:", font=badge_font, fill=(255, 255, 255))
        
        cy = q_card_y + 90
        for l in q_lines:
            lb = draw.textbbox((0, 0), l, font=q_font)
            draw.text(((width - (lb[2]-lb[0]))//2, cy), l, font=q_font, fill=(15, 23, 42))
            cy += 58
            
        raw_content = post.get("content", "")
        clean_rc = re.sub(r"<[^>]+>", "", raw_content)
        ans_points = [p.replace("•", "").strip() for p in clean_rc.splitlines() if "•" in p][:2]
        if ans_points:
            a_text = "\n".join(ans_points)
        else:
            a_text = "Arkadaş Consulting orqali barcha hujjatlar, yotoqxona va qonuniy rasmiylashtirish 100% kafolat bilan bajariladi."
        a_text = re.sub(r"<[^>]+>", "", a_text)
            
        a_lines = wrap_text(a_text, a_font, card_w - 100, draw)
        a_card_h = max(340, len(a_lines) * 50 + 160)
        a_card_y = q_card_y + q_card_h + 80
        
        draw.rounded_rectangle([card_x, a_card_y, card_x + card_w, a_card_y + a_card_h], radius=36, fill=card_bg)
        aby = a_card_y - (badge_h // 2)
        draw.rounded_rectangle([bx, aby, bx + badge_w, aby + badge_h], radius=37, fill=badge_color)
        ab_bbox = draw.textbbox((0, 0), "Javob:", font=badge_font)
        draw.text((bx + (badge_w - (ab_bbox[2]-ab_bbox[0]))//2, aby + 16), "Javob:", font=badge_font, fill=(255, 255, 255))
        
        cy = a_card_y + 90
        for l in a_lines:
            lb = draw.textbbox((0, 0), l, font=a_font)
            draw.text(((width - (lb[2]-lb[0]))//2, cy), l, font=a_font, fill=(20, 25, 40))
            cy += 50
            
        logo_path = ASSETS_DIR / "logo_transparent.png"
        if logo_path.exists():
            logo = Image.open(logo_path).convert("RGBA")
            lw = 200
            lh = int(logo.height * (lw / logo.width))
            logo = logo.resize((lw, lh), Image.Resampling.LANCZOS)
            pw, ph = lw + 36, lh + 20
            px = (width - pw) // 2
            py = height - 180
            draw.rounded_rectangle([px, py, px + pw, py + ph], radius=24, fill=(255, 255, 255))
            img.paste(logo, (px + 18, py + 10), logo)
            
        val_f = get_font(["Arial.ttf", "Helvetica.ttc"], 22)
        full_str = "Telegram: @arkadasuzz   •   Kanal: @arkadasuz   •   Instagram: @arkadasuz   •   Web: arkadas.uz"
        w_bbox = draw.textbbox((0, 0), full_str, font=val_f)
        draw.text(((width - (w_bbox[2]-w_bbox[0]))//2, height - 60), full_str, font=val_f, fill=(200, 215, 245))
        
    else:
        # Style 2: Split Banner Infographic (Matches photo_114_0.jpg)
        img = Image.new("RGB", (width, height), (32, 24, 115))
        draw = ImageDraw.Draw(img)
        
        photo_h = 540
        photo_path = get_photo_for_post(post_id, post.get("slot", ""), cat_tag)
        if photo_path.exists():
            raw_p = Image.open(photo_path).convert("RGB")
            scale = max(width / raw_p.width, photo_h / raw_p.height)
            nw, nh = int(raw_p.width * scale), int(raw_p.height * scale)
            scaled_p = raw_p.resize((nw, nh), Image.Resampling.LANCZOS)
            cx = (nw - width) // 2
            cy = max(0, int((nh - photo_h) * 0.45))
            crop_p = scaled_p.crop((cx, cy, cx + width, cy + photo_h))
            img.paste(crop_p, (0, 0))
            
        # Badge Pill
        pill_font = get_font(["Impact.ttf", "Arial Black.ttf"], 36)
        p_bbox = draw.textbbox((0, 0), cat_tag, font=pill_font)
        pw = (p_bbox[2] - p_bbox[0]) + 44
        ph = 56
        px = 60
        py = photo_h + 38
        draw.rounded_rectangle([px, py, px + pw, py + ph], radius=14, fill=(255, 255, 255))
        draw.text((px + 22, py + 8), cat_tag, font=pill_font, fill=(20, 25, 40))
        
        # Title
        title_font = get_font(["Impact.ttf", "Arial Black.ttf"], 60)
        t_clean = topic.split(":")[-1].strip() if ":" in topic else topic
        if len(t_clean) > 42:
            t_clean = t_clean[:40] + "..."
        draw.text((60, py + ph + 16), t_clean.upper(), font=title_font, fill=(255, 255, 255))
        
        # 4 Bullets cleanly extracted without HTML tags
        raw_c = post.get("content", "")
        clean_c = re.sub(r"<[^>]+>", "", raw_c)
        extracted_b = []
        for line in clean_c.splitlines():
            if "•" in line or "1." in line or "2." in line or "3." in line or "4." in line:
                b_txt = re.sub(r"^[\s•\d\.\:\-]+", "", line).strip()
                if ":" in b_txt and len(b_txt.split(":")[0].strip()) <= 30:
                    b_txt = b_txt.split(":")[0].strip()
                if b_txt:
                    extracted_b.append(b_txt[:30])
        bullets = (extracted_b[:4] if len(extracted_b) >= 2 else [
            "100% Qabul kafolati",
            "Yotoqxona va stipendiya",
            "Xalqaro amaliyot (Erasmus+)",
            "Diplom O'zbekistonda tan olinadi"
        ])
        
        b_font = get_font(["Arial Bold.ttf", "Helvetica.ttc"], 26)
        col_w = 460
        badge_item_h = 56
        start_bx = 60
        start_by = py + ph + 105
        
        for i, item in enumerate(bullets[:4]):
            col = i % 2
            row = i // 2
            bx = start_bx + col * (col_w + 35)
            by = start_by + row * (badge_item_h + 16)
            draw.rounded_rectangle([bx, by, bx + col_w, by + badge_item_h], radius=14, fill=(255, 255, 255))
            draw.text((bx + 18, by + 12), ">", font=b_font, fill=(29, 83, 245))
            draw.text((bx + 44, by + 12), item[:28], font=b_font, fill=(20, 25, 40))
            
        # Bottom Bar
        footer_y = height - 145
        c_pill_w, c_pill_h = 220, 58
        draw.rounded_rectangle([60, footer_y, 60 + c_pill_w, footer_y + c_pill_h], radius=29, fill=(255, 255, 255))
        btn_font = get_font(["Arial Bold.ttf", "Helvetica.ttc"], 24)
        draw.text((80, footer_y + 15), "Aloqa uchun ->", font=btn_font, fill=(20, 25, 40))
        
        ph_font = get_font(["Arial Bold.ttf", "Helvetica.ttc"], 22)
        draw.text((310, footer_y + 6), "+998 93 5999865", font=ph_font, fill=(255, 255, 255))
        draw.text((310, footer_y + 32), "@arkadasuzz", font=ph_font, fill=(200, 220, 255))
        
        logo_path = ASSETS_DIR / "logo_transparent.png"
        if logo_path.exists():
            logo = Image.open(logo_path).convert("RGBA")
            lw = 190
            lh = int(logo.height * (lw / logo.width))
            logo = logo.resize((lw, lh), Image.Resampling.LANCZOS)
            pw, ph = lw + 30, lh + 16
            rx = width - 60 - pw
            draw.rounded_rectangle([rx, footer_y - 2, rx + pw, footer_y + ph], radius=20, fill=(255, 255, 255))
            img.paste(logo, (rx + 15, footer_y + 6), logo)
            
        val_f = get_font(["Arial.ttf", "Helvetica.ttc"], 22)
        full_str = "Telegram: @arkadasuzz   •   Kanal: @arkadasuz   •   Instagram: @arkadasuz   •   Web: arkadas.uz"
        w_bbox = draw.textbbox((0, 0), full_str, font=val_f)
        draw.text(((width - (w_bbox[2]-w_bbox[0]))//2, height - 52), full_str, font=val_f, fill=(210, 225, 255))

    img.save(out_file, quality=95)
    return out_file

# ========================================================
# 2. 9:16 STORY GENERATOR (1080x1920)
# ========================================================
def generate_story_card_9_16(post: dict) -> Path:
    width, height = 1080, 1920
    post_id = post["id"]
    topic = post.get("topic", "Turkiyada Ta'lim")
    cat_tag = clean_label(post.get("cat_tag", "ARKADAŞ CONSULTING"))
    
    out_file = OUTPUT_STORIES / f"story_{post_id}.png"
    
    photo_path = get_photo_for_post(post_id, post.get("slot", ""), cat_tag)
    if photo_path.exists():
        raw_p = Image.open(photo_path).convert("RGB")
        scale = max(width / raw_p.width, height / raw_p.height)
        nw, nh = int(raw_p.width * scale), int(raw_p.height * scale)
        scaled_p = raw_p.resize((nw, nh), Image.Resampling.LANCZOS)
        cx = (nw - width) // 2
        cy = max(0, int((nh - height) * 0.35))
        img = scaled_p.crop((cx, cy, cx + width, cy + height))
    else:
        img = Image.new("RGB", (width, height), (25, 35, 75))
        
    draw = ImageDraw.Draw(img)
    
    # Top Subtle Dark Vignette
    vignette = Image.new("RGBA", (width, 450), (0, 0, 0, 140))
    img.paste(vignette, (0, 0), vignette)
    
    # Top Capsule Badge
    pill_font = get_font(["Arial Bold.ttf", "Helvetica.ttc"], 28)
    badge_text = cat_tag.upper()
    p_bbox = draw.textbbox((0, 0), badge_text, font=pill_font)
    pw = (p_bbox[2] - p_bbox[0]) + 48
    ph = 56
    px = (width - pw) // 2
    py = 110
    draw.rounded_rectangle([px, py, px + pw, py + ph], radius=28, fill=(255, 255, 255, 230))
    draw.text((px + 24, py + 12), badge_text, font=pill_font, fill=(20, 25, 40))
    
    # Story Hook Headline
    hook_font = get_font(["Impact.ttf", "Arial Black.ttf"], 72)
    clean_topic = topic.split(":")[-1].strip() if ":" in topic else topic
    lines = wrap_text(clean_topic, hook_font, width - 140, draw)
    hy = 195
    for line in lines[:3]:
        # Drop shadow
        draw.text(((width - (draw.textbbox((0,0), line, font=hook_font)[2]-draw.textbbox((0,0), line, font=hook_font)[0]))//2 + 3, hy + 3), line, font=hook_font, fill=(0, 0, 0, 180))
        draw.text(((width - (draw.textbbox((0,0), line, font=hook_font)[2]-draw.textbbox((0,0), line, font=hook_font)[0]))//2, hy), line, font=hook_font, fill=(255, 255, 255))
        hy += 86
        
    # Bottom Arkadaş Logo
    logo_path = ASSETS_DIR / "logo_transparent.png"
    if logo_path.exists():
        logo = Image.open(logo_path).convert("RGBA")
        lw = 240
        lh = int(logo.height * (lw / logo.width))
        logo = logo.resize((lw, lh), Image.Resampling.LANCZOS)
        pw, ph = lw + 44, lh + 24
        px = (width - pw) // 2
        py = height - 260
        draw.rounded_rectangle([px, py, px + pw, py + ph], radius=28, fill=(255, 255, 255, 240))
        img.paste(logo, (px + 22, py + 12), logo)
        
    # Bottom Dark Bar
    bar_h = 110
    bar_overlay = Image.new("RGBA", (width, bar_h), (10, 15, 30, 220))
    img.paste(bar_overlay, (0, height - bar_h), bar_overlay)
    
    cta_font = get_font(["Arial Bold.ttf", "Helvetica.ttc"], 28)
    cta_txt = "Savollaringiz bormi? Telegram: @arkadasuzz"
    cb = draw.textbbox((0, 0), cta_txt, font=cta_font)
    draw.text(((width - (cb[2]-cb[0]))//2, height - bar_h + 20), cta_txt, font=cta_font, fill=(255, 220, 100))
    
    sub_font = get_font(["Arial.ttf", "Helvetica.ttc"], 22)
    sub_txt = "Kanal: @arkadasuz   •   Instagram: @arkadasuz   •   arkadas.uz"
    sb = draw.textbbox((0, 0), sub_txt, font=sub_font)
    draw.text(((width - (sb[2]-sb[0]))//2, height - bar_h + 62), sub_txt, font=sub_font, fill=(220, 230, 250))
    
    img.save(out_file, quality=95)
    return out_file

# ========================================================
# 3. FULL OMNICHANNEL RUNNER
# ========================================================
def build_all_omnichannel_packs():
    if not POSTS_JSON.exists():
        print(f"[ERR] File not found: {POSTS_JSON}")
        return
        
    with open(POSTS_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    posts = data.get("posts", [])
    print(f"Loaded {len(posts)} posts. Generating multi-format assets...")
    
    for i, post in enumerate(posts):
        p_id = post["id"]
        # 1. 4:5 Post Card
        post_card_path = generate_post_card_4_5(post)
        # 2. 9:16 Story Card
        story_card_path = generate_story_card_9_16(post)
        # 3. Omnichannel Copywriting Pack
        copy_pack = format_multichannel_pack({
            "media_type": "image",
            "caption": post.get("content", ""),
            "content": post.get("content", "")
        })
        
        post["photo_path"] = str(post_card_path.relative_to(BASE_DIR))
        post["story_path"] = str(story_card_path.relative_to(BASE_DIR))
        post["multichannel_pack"] = copy_pack
        print(f"[{i+1}/{len(posts)}] Built Omnichannel Pack for {p_id}")
        
    with open(POSTS_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print("\n[SUCCESS] All 14 posts updated with 4:5 Post + 9:16 Story + Multichannel Pack!")

if __name__ == "__main__":
    build_all_omnichannel_packs()
