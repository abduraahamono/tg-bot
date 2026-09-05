#!/usr/bin/env python3
"""
Arkadaş Consulting - Fastlane-Style UGC Vlogger Video Engine
Features:
1. Full-Motion Real Human Creator / Vlogger Footage
   - Creator speaks into podcast mic, moves hands, nods, natural facial expressions
2. Expressive Multi-Language Voiceover:
   - ElevenLabs / Copilot Ava Multilingual (+8% speed, +3Hz pitch)
3. Timed Kinetic Subtitles:
   - TikTok/CapCut-style bold highlight cards
4. Viral Background Music:
   - Blok3 "Ne Yapıyorsun" trend hook or chill acoustic ducked under speech
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
MILA_DIR = ASSETS_DIR / "influencer_mila"
AUDIO_DIR = ASSETS_DIR / "audio"
OUTPUT_DIR = BASE_DIR / "output"
FFMPEG_BIN = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"
FFPROBE_BIN = "/opt/homebrew/opt/ffmpeg-full/bin/ffprobe"

from templates.template5_video import get_font, wrap_text
from engine.ai_brain import AIBrain
from engine.voice_studio import VoiceStudio

class FastlaneUGCEngine:
    def __init__(self):
        self.ai = AIBrain()
        self.voice_studio = VoiceStudio()
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    def generate_ugc_script(self, topic: str = "Turkiyada 100% grant yutish siri", lang: str = "uz") -> dict:
        prompt = (
            f"Sen juda samimiy, quvnoq, TikTokda vlog olib boradigan talaba qizsan.\n"
            f"Mavzu: '{topic}'.\n"
            "Kameraga qarab xuddi do'sting bilan gaplashayotgandek jonli, his-tuyg'uli va baquvvat 3 ta jumla ayt:\n"
            "1. Hook: E'tiborni tortadigan qiziq savol (maksimum 6-7 so'z)\n"
            "2. Value: Asosiy foydali sir (maksimum 10-12 so'z)\n"
            "3. CTA: Arkadaş Consulting bilan bog'lanish (maksimum 6-7 so'z)\n\n"
            "Format:\n"
            "{\n"
            '  "hook": "...",\n'
            '  "value": "...",\n'
            '  "cta": "...",\n'
            '  "caption": "Post matni"\n'
            "}"
        )
        res = self.ai.think_and_generate(prompt)
        try:
            m = re.search(r'\{.*\}', res.get("text", ""), re.DOTALL)
            if m:
                return json.loads(m.group(0))
        except Exception:
            pass

        return {
            "hook": "Istanbulda o'qish qanchalik osonligini bilasizmi?",
            "value": "Arkadaş Consulting bilan imtihonsiz va oldindan to'lovsiz 100% grant yutishingiz mumkin!",
            "cta": "Hoziroq @arkadasuz ga yozing va talaba bo'ling!",
            "caption": "Orzuingizdagi universitetga Arkadaş Consulting bilan kiring! 🇹🇷🎓"
        }

    def render_ugc_caption_card(self, text: str, highlight_color: tuple, badge: str, output_png: Path):
        width, height = 1080, 1920
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        font_badge = get_font("Arial Bold", 32)
        font_main = get_font("Georgia Bold", 56)

        # Scrim at bottom third
        scrim = Image.new("RGBA", (width, 540), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(scrim)
        for y in range(scrim.height):
            alpha = int(210 * (y / scrim.height) ** 1.3)
            s_draw.line([(0, y), (width, y)], fill=(5, 12, 25, alpha))
        img.paste(scrim, (0, height - 600), scrim)

        current_y = height - 540

        # Pill badge
        if badge:
            badge_bbox = draw.textbbox((0, 0), badge, font=font_badge)
            bw = badge_bbox[2] - badge_bbox[0] + 44
            bh = badge_bbox[3] - badge_bbox[1] + 20
            bx = (width - bw) // 2
            draw.rounded_rectangle([bx, current_y, bx + bw, current_y + bh], radius=16, fill=(15, 30, 60, 230), outline=(0, 210, 255, 255), width=2)
            draw.text((bx + 22, current_y + 8), badge, font=font_badge, fill=(255, 255, 255, 255))
            current_y += bh + 30

        # Main Subtitle Lines
        wrapped = wrap_text(text.upper(), font_main, width - 160, draw)
        for line in wrapped:
            bbox = draw.textbbox((0, 0), line, font=font_main)
            lw = bbox[2] - bbox[0]
            lx = (width - lw) // 2
            draw.text((lx + 3, current_y + 3), line, font=font_main, fill=(0, 0, 0, 255))
            draw.text((lx, current_y), line, font=font_main, fill=highlight_color)
            current_y += 70

        # Brand logo
        sticker_path = ASSETS_DIR / "sticker_clean.png"
        if sticker_path.exists():
            stk = Image.open(sticker_path).convert("RGBA")
            sw = 260
            sh = int(stk.height * (sw / stk.width))
            stk = stk.resize((sw, sh), Image.Resampling.LANCZOS)
            img.paste(stk, ((width - sw) // 2, height - sh - 50), stk)

        img.save(output_png, "PNG")

    def create_ugc_video(
        self,
        topic: str = "Turkiyada 100% grant yutish",
        lang: str = "uz",
        music_type: str = "blok3",
        output_filename: str = None
    ) -> dict:
        """
        Creates a full-motion UGC Creator video (talking, gestures, dynamic energy).
        """
        out_name = output_filename or f"ugc_vlogger_{random.randint(1000, 9999)}.mp4"
        out_mp4 = OUTPUT_DIR / out_name

        # 1. Script
        script = self.generate_ugc_script(topic, lang=lang)
        h = script["hook"]
        v = script["value"]
        c = script["cta"]
        full_text = f"{h} {v} {c}"

        # 2. Expressive Voice
        temp_voice = OUTPUT_DIR / f"temp_voice_{random.randint(100, 999)}.mp3"
        self.voice_studio.generate_expressive_voice(full_text, temp_voice, lang=lang)

        # Get voice duration
        cmd = [FFPROBE_BIN, "-i", str(temp_voice), "-show_entries", "format=duration", "-v", "quiet", "-of", "csv=p=0"]
        dur = float(subprocess.run(cmd, capture_output=True, text=True).stdout.strip() or 12.0)
        dur = max(dur + 1.0, 8.0)

        t1 = round(dur * 0.32, 2)
        t2 = round(dur * 0.72, 2)
        t3 = round(dur, 2)

        # 3. Subtitle Cards
        c1 = OUTPUT_DIR / f"temp_ugc_c1_{random.randint(100, 999)}.png"
        c2 = OUTPUT_DIR / f"temp_ugc_c2_{random.randint(100, 999)}.png"
        c3 = OUTPUT_DIR / f"temp_ugc_c3_{random.randint(100, 999)}.png"

        self.render_ugc_caption_card(h, (255, 255, 255, 255), "💡 MIF YOKI HAQIQAT?", c1)
        self.render_ugc_caption_card(v, (255, 215, 0, 255), "🔥 ASL HAQIQAT", c2)
        self.render_ugc_caption_card(c, (0, 230, 255, 255), "🚀 ARKADAŞ BILAN KELING", c3)

        # 4. UGC Video File
        ugc_video = MILA_DIR / "ugc_vlogger_walking.mp4"
        if not ugc_video.exists():
            ugc_video = list(MILA_DIR.glob("*.mp4"))[0]

        # 5. Background Music (Blok3 or chill)
        if music_type == "blok3":
            bg_music = AUDIO_DIR / "trend_blok3_hook.mp3"
            if not bg_music.exists():
                bg_music = AUDIO_DIR / "inspiring_travel_vibe.mp3"
        else:
            bg_music = AUDIO_DIR / "inspiring_travel_vibe.mp3"

        whoosh = AUDIO_DIR / "whoosh_sfx.aac"
        pop = AUDIO_DIR / "pop_sfx.aac"

        filter_complex = (
            f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1/1[vbase];"
            f"[vbase][1:v]overlay=0:0:enable='between(t,0,{t1})'[vo1];"
            f"[vo1][2:v]overlay=0:0:enable='between(t,{t1},{t2})'[vo2];"
            f"[vo2][3:v]overlay=0:0:enable='between(t,{t2},{t3})'[vout];"
            f"[4:a]volume=1.0[voice];"
            f"[5:a]volume=0.15,afade=t=out:st={t3-1.5}:d=1.5[music];"
            f"[6:a]adelay={int(t1*1000)}|{int(t1*1000)},volume=0.40[sfx_whoosh];"
            f"[7:a]adelay={int(t2*1000)}|{int(t2*1000)},volume=0.35[sfx_pop];"
            f"[voice][music][sfx_whoosh][sfx_pop]amix=inputs=4:duration=first[aout]"
        )

        cmd = [
            FFMPEG_BIN, "-y",
            "-stream_loop", "-1", "-i", str(ugc_video),
            "-i", str(c1),
            "-i", str(c2),
            "-i", str(c3),
            "-i", str(temp_voice),
            "-i", str(bg_music),
            "-i", str(whoosh),
            "-i", str(pop),
            "-filter_complex", filter_complex,
            "-map", "[vout]",
            "-map", "[aout]",
            "-t", str(t3),
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            str(out_mp4)
        ]

        print(f"[FASTLANE UGC] Rendering Full-Motion Creator Video ({t3:.1f}s)...")
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print("[FFmpeg Error]:", res.stderr)
            raise RuntimeError("UGC video render failed")

        for tmp in [c1, c2, c3, temp_voice]:
            if tmp.exists(): tmp.unlink()

        print(f"[SUCCESS] UGC Creator Video Created: {out_mp4}")
        return {
            "media_path": str(out_mp4),
            "topic": topic,
            "duration": t3,
            "caption": script["caption"]
        }

if __name__ == "__main__":
    eng = FastlaneUGCEngine()
    res = eng.create_ugc_video(music_type="blok3")
    print("Rendered:", res["media_path"])
