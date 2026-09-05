#!/usr/bin/env python3
"""
Arkadaş Consulting - Fastlane-Style Faceless Aesthetic Video Engine
Features:
1. 4K Drone / Istanbul / Bosphorus / Campus B-Roll
2. Progressive Satır-Satır (Line-by-Line) Kinetic Subtitles:
   - Line 1 appears at t=0s
   - Line 2 reveals underneath at t=3s
   - Line 3 reveals at t=6s
   - Line 4 (CTA / Arkadaş branding) reveals at t=9s
   - High-contrast frosted glass card with gold & cyan accent highlights
3. Trend Music Integration:
   - Blok3 "Ne Yapıyorsun" viral hook (assets/audio/trend_blok3_hook.mp3)
   - Or inspiring travel vibe / acoustic guitar
"""

import os
import sys
import re
import json
import random
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

ASSETS_DIR = BASE_DIR / "assets"
CLEAN_VIDEOS_DIR = ASSETS_DIR / "clean_videos"
AUDIO_DIR = ASSETS_DIR / "audio"
OUTPUT_DIR = BASE_DIR / "output"
FFMPEG_BIN = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"
FFPROBE_BIN = "/opt/homebrew/opt/ffmpeg-full/bin/ffprobe"

from templates.template5_video import get_font, wrap_text
from engine.ai_brain import AIBrain

class FastlaneFacelessEngine:
    def __init__(self):
        self.ai = AIBrain()
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    def generate_viral_script(self, topic: str = "Turkiyada 100% grant yutish") -> dict:
        """Generates 4-line punchy progressive storytelling script."""
        prompt = (
            f"Mavzu: '{topic}'.\n"
            "Instagram Reels va TikTok uchun 4 ta kuchli qatordan iborat viral matn yoz:\n"
            "1-qator (Hook): O'quvchini to'xtatadigan provokatsion savol (maksimum 5-6 so'z)\n"
            "2-qator (Fakt): Hech kim bilmaydigan haqiqat (maksimum 6-7 so'z)\n"
            "3-qator (Yechim): Qanday qilish mumkinligi (maksimum 6-7 so'z)\n"
            "4-qator (CTA): Arkadaş Consulting ga chaqiruv (maksimum 5-6 so'z)\n\n"
            "Format:\n"
            "{\n"
            '  "line1": "...",\n'
            '  "line2": "...",\n'
            '  "line3": "...",\n'
            '  "line4": "...",\n'
            '  "caption": "Post uchun to\'liq tavsif (emojilar va hashtaglar bilan)"\n'
            "}"
        )
        res = self.ai.think_and_generate(prompt)
        text = res.get("text", "")
        try:
            m = re.search(r'\{.*\}', text, re.DOTALL)
            if m:
                return json.loads(m.group(0))
        except Exception:
            pass

        return {
            "line1": "TURKIYADA O'QISH QIMMATMI?",
            "line2": "YO'Q, FAQAT ATTESTAT BILAN 100% GRANT MUMKIN!",
            "line3": "IMTIHONSIZ VA DAVLAT DIPLOMI BILAN!",
            "line4": "OLDINDAN TO'LOV YO'Q — @ARKADASUZ GA YOZING!",
            "caption": "Turkiyada talaba bo'lish imkoniyatini boy bermang! 🇹🇷🎓\n\nArkadaş Consulting bilan 0$ oldindan to'lovsiz 100% grant yuting!"
        }

    def render_progressive_subtitle_card(
        self,
        visible_lines: list,
        output_png: Path,
        badge_text: str = "ARKADAŞ CONSULTING"
    ):
        """
        Renders an ultra-modern Fastlane frosted card with lines appearing progressively.
        """
        width, height = 1080, 1920
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        font_badge = get_font("Arial Bold", 30)
        font_line1 = get_font("Georgia Bold", 54)
        font_body = get_font("Arial Bold", 44)

        # Card geometry at center
        card_w = 980
        card_x1 = (width - card_w) // 2
        card_y1 = height // 2 - 380
        card_h = 740
        card_x2 = card_x1 + card_w
        card_y2 = card_y1 + card_h

        # Frosted glass card backing
        card_overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        c_draw = ImageDraw.Draw(card_overlay)
        c_draw.rounded_rectangle(
            [card_x1, card_y1, card_x2, card_y2],
            radius=36,
            fill=(10, 18, 32, 215),
            outline=(0, 220, 255, 200),
            width=3
        )
        img = Image.alpha_composite(img, card_overlay)
        draw = ImageDraw.Draw(img)

        # Top Badge Pill
        badge_bbox = draw.textbbox((0, 0), badge_text, font=font_badge)
        bw = badge_bbox[2] - badge_bbox[0] + 44
        bh = badge_bbox[3] - badge_bbox[1] + 20
        bx = (width - bw) // 2
        by = card_y1 + 35
        draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=16, fill=(0, 210, 255, 255))
        draw.text((bx + 22, by + 8), badge_text, font=font_badge, fill=(10, 15, 25, 255))

        # Progressive Lines
        current_y = by + bh + 45
        colors = [
            (255, 255, 255, 255),  # Line 1: White
            (255, 215, 0, 255),    # Line 2: Gold
            (0, 230, 255, 255),    # Line 3: Cyan
            (100, 255, 150, 255)   # Line 4: Neon Green (CTA)
        ]

        for idx, line_text in enumerate(visible_lines):
            fnt = font_line1 if idx == 0 else font_body
            color = colors[min(idx, len(colors) - 1)]
            wrapped = wrap_text(line_text.upper(), fnt, card_w - 90, draw)
            for w in wrapped:
                bbox = draw.textbbox((0, 0), w, font=fnt)
                lw = bbox[2] - bbox[0]
                lx = (width - lw) // 2
                # Shadow
                draw.text((lx + 2, current_y + 2), w, font=fnt, fill=(0, 0, 0, 240))
                draw.text((lx, current_y), w, font=fnt, fill=color)
                current_y += 58
            current_y += 18

        # Small bottom logo sticker at bottom of entire frame (never overlaps card)
        sticker_path = ASSETS_DIR / "sticker_clean.png"
        if sticker_path.exists():
            stk = Image.open(sticker_path).convert("RGBA")
            sw = 280
            sh = int(stk.height * (sw / stk.width))
            stk = stk.resize((sw, sh), Image.Resampling.LANCZOS)
            img.paste(stk, ((width - sw) // 2, height - sh - 70), stk)

        img.save(output_png, "PNG")

    def create_faceless_video(
        self,
        topic: str = "Turkiyada 100% grant yutish",
        music_type: str = "blok3",
        duration: int = 12,
        output_filename: str = None
    ) -> dict:
        """
        Produces 4K Faceless Aesthetic Reel with:
        - Clean Drone B-Roll
        - Line-by-line animated subtitle cards
        - Blok3 viral hook or trend music
        """
        out_name = output_filename or f"faceless_trend_{random.randint(1000, 9999)}.mp4"
        out_mp4 = OUTPUT_DIR / out_name

        # 1. Script
        script = self.generate_viral_script(topic)
        l1 = script["line1"]
        l2 = script["line2"]
        l3 = script["line3"]
        l4 = script["line4"]

        # 2. Select Clean Video B-Roll
        videos = list(CLEAN_VIDEOS_DIR.glob("*.mp4"))
        broll = random.choice(videos) if videos else (ASSETS_DIR / "clean_videos" / "broll_istanbul_aerial.mp4")

        # 3. Render 4 Progressive Cards
        c1 = OUTPUT_DIR / f"temp_card1_{random.randint(100, 999)}.png"
        c2 = OUTPUT_DIR / f"temp_card2_{random.randint(100, 999)}.png"
        c3 = OUTPUT_DIR / f"temp_card3_{random.randint(100, 999)}.png"
        c4 = OUTPUT_DIR / f"temp_card4_{random.randint(100, 999)}.png"

        self.render_progressive_subtitle_card([l1], c1)
        self.render_progressive_subtitle_card([l1, l2], c2)
        self.render_progressive_subtitle_card([l1, l2, l3], c3)
        self.render_progressive_subtitle_card([l1, l2, l3, l4], c4)

        # 4. Music Selection
        if music_type == "blok3":
            music_file = AUDIO_DIR / "trend_blok3_hook.mp3"
            if not music_file.exists():
                music_file = AUDIO_DIR / "inspiring_travel_vibe.mp3"
        else:
            music_file = AUDIO_DIR / "inspiring_travel_vibe.mp3"

        # 5. FFmpeg Assembly with Timed Progressive Revealing
        t1, t2, t3, t4 = 3.0, 6.0, 9.0, duration
        filter_complex = (
            f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1/1[vbase];"
            f"[vbase][1:v]overlay=0:0:enable='between(t,0,{t1})'[vo1];"
            f"[vo1][2:v]overlay=0:0:enable='between(t,{t1},{t2})'[vo2];"
            f"[vo2][3:v]overlay=0:0:enable='between(t,{t2},{t3})'[vo3];"
            f"[vo3][4:v]overlay=0:0:enable='between(t,{t3},{t4})'[vout];"
            f"[5:a]volume=0.90,afade=t=in:ss=0:d=0.5,afade=t=out:st={t4-1.5}:d=1.5[aout]"
        )

        cmd = [
            FFMPEG_BIN, "-y",
            "-stream_loop", "-1", "-i", str(broll),
            "-i", str(c1),
            "-i", str(c2),
            "-i", str(c3),
            "-i", str(c4),
            "-i", str(music_file),
            "-filter_complex", filter_complex,
            "-map", "[vout]",
            "-map", "[aout]",
            "-t", str(t4),
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            str(out_mp4)
        ]

        print(f"[FACELESS ENGINE] Rendering Progressive Subtitle Video ({duration}s with {music_file.name})...")
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print("[FFmpeg Error]:", res.stderr)
            raise RuntimeError("Faceless video render failed")

        for c in [c1, c2, c3, c4]:
            if c.exists(): c.unlink()

        print(f"[SUCCESS] Faceless Trend Video Created: {out_mp4}")
        return {
            "media_path": str(out_mp4),
            "topic": topic,
            "music": music_file.name,
            "duration": duration,
            "caption": script["caption"]
        }

if __name__ == "__main__":
    eng = FastlaneFacelessEngine()
    r = eng.create_faceless_video(music_type="blok3")
    print("Output:", r["media_path"])
