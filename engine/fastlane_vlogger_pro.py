#!/usr/bin/env python3
"""
Arkadaş Consulting - Fastlane Pro Multi-Scene Real Human Vlogger Engine
Creates viral TikTok/Reels videos that look 100% like a real human vlogger:
- 4-Scene Rapid Cut Structure:
  * Act 1 (0-3.5s): Real Vlogger Hook (Selfie talk, gesturing, expressive face)
  * Act 2 (3.5-7.0s): B-Roll Cut (4K Istanbul/Campus drone with punch zoom)
  * Act 3 (7.0-10.5s): Real Vlogger Explains (Punch-in 1.15x angle, high energy)
  * Act 4 (10.5-13.0s): Call to Action Card + Arkadaş Logo
- Dynamic Audio Layer:
  * Expressive Voiceover (ElevenLabs / Copilot Ava Multilingual)
  * Blok3 "Ne Yapıyorsun" Trend Hook ducked cleanly (-18dB under speech)
  * Whoosh SFX on scene cuts
  * Pop Chime SFX on badge reveals
- Kinetic Styled Subtitles:
  * High-contrast gradient cards, bold typography, glowing accents
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
CLEAN_VIDEOS_DIR = ASSETS_DIR / "clean_videos"
AUDIO_DIR = ASSETS_DIR / "audio"
OUTPUT_DIR = BASE_DIR / "output"
FFMPEG_BIN = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"
FFPROBE_BIN = "/opt/homebrew/opt/ffmpeg-full/bin/ffprobe"

from templates.template5_video import get_font, wrap_text
from engine.ai_brain import AIBrain
from engine.voice_studio import VoiceStudio

class FastlaneVloggerPro:
    def __init__(self):
        self.ai = AIBrain()
        self.voice_studio = VoiceStudio()
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    def generate_viral_script(self, topic: str = "Turkiyada 100% grant yutish", lang: str = "uz") -> dict:
        prompt = (
            f"Sen juda mashhur, quvnoq va harakatchan TikTok vlogger qizsan.\n"
            f"Mavzu: '{topic}'.\n"
            "Kameraga qarab xuddi do'sting bilan ko'chada ketayotgandek jonli, his-tuyg'uli 3 ta jumla ayt:\n"
            "1. Hook (0-3.5s): E'tiborni tortadigan provokatsion savol (maks 6-7 so'z)\n"
            "2. Value (3.5-7s): Hech kim bilmaydigan haqiqat va imkoniyat (maks 10 so'z)\n"
            "3. CTA (7-11s): Qanday murojaat qilish kerakligi (maks 7 so'z)\n\n"
            "Format:\n"
            "{\n"
            '  "hook": "...",\n'
            '  "value": "...",\n'
            '  "cta": "...",\n'
            '  "caption": "Reels matni hashtaglar bilan"\n'
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
            "hook": "Turkiyada tekinga o'qish mumkin desam ishonmaysizmi?",
            "value": "Arkadaş Consulting bilan faqat attestat baholaringiz orqali 100% grant yuta olasiz!",
            "cta": "Oldindan to'lov yo'q — @arkadasuz ga hoziroq yozing!",
            "caption": "Turkiyada talabalik hayotini boshlang! 🇹🇷🎓\n\nArkadaş Consulting orqali kafolatli qabul!"
        }

    def render_overlay_card(
        self,
        badge_text: str,
        main_text: str,
        text_color: tuple,
        output_png: Path,
        style: str = "card" # "card" or "lower_third"
    ):
        width, height = 1080, 1920
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        font_badge = get_font("Arial Bold", 32)
        font_main = get_font("Georgia Bold", 54)

        if style == "card":
            # Center frosted card
            card_w = 980
            card_x1 = (width - card_w) // 2
            card_y1 = height // 2 - 280
            card_h = 560
            card_x2 = card_x1 + card_w
            card_y2 = card_y1 + card_h

            card_overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            c_draw = ImageDraw.Draw(card_overlay)
            c_draw.rounded_rectangle([card_x1, card_y1, card_x2, card_y2], radius=32, fill=(10, 18, 30, 220), outline=(0, 210, 255, 230), width=3)
            img = Image.alpha_composite(img, card_overlay)
            draw = ImageDraw.Draw(img)

            # Badge pill
            badge_bbox = draw.textbbox((0, 0), badge_text, font=font_badge)
            bw = badge_bbox[2] - badge_bbox[0] + 44
            bh = badge_bbox[3] - badge_bbox[1] + 20
            bx = (width - bw) // 2
            by = card_y1 + 35
            draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=16, fill=(0, 210, 255, 255))
            draw.text((bx + 22, by + 8), badge_text, font=font_badge, fill=(10, 15, 25, 255))

            current_y = by + bh + 40
            wrapped = wrap_text(main_text.upper(), font_main, card_w - 90, draw)
            for line in wrapped:
                bbox = draw.textbbox((0, 0), line, font=font_main)
                lw = bbox[2] - bbox[0]
                lx = (width - lw) // 2
                draw.text((lx + 3, current_y + 3), line, font=font_main, fill=(0, 0, 0, 255))
                draw.text((lx, current_y), line, font=font_main, fill=text_color)
                current_y += 72

        else:
            # Lower-third kinetic subtitles
            scrim = Image.new("RGBA", (width, 500), (0, 0, 0, 0))
            s_draw = ImageDraw.Draw(scrim)
            for y in range(scrim.height):
                alpha = int(210 * (y / scrim.height) ** 1.3)
                s_draw.line([(0, y), (width, y)], fill=(5, 12, 25, alpha))
            img.paste(scrim, (0, height - 560), scrim)

            current_y = height - 500
            badge_bbox = draw.textbbox((0, 0), badge_text, font=font_badge)
            bw = badge_bbox[2] - badge_bbox[0] + 44
            bh = badge_bbox[3] - badge_bbox[1] + 20
            bx = (width - bw) // 2
            draw.rounded_rectangle([bx, current_y, bx + bw, current_y + bh], radius=16, fill=(15, 30, 60, 240), outline=(0, 210, 255, 255), width=2)
            draw.text((bx + 22, current_y + 8), badge_text, font=font_badge, fill=(255, 255, 255, 255))

            current_y += bh + 30
            wrapped = wrap_text(main_text.upper(), font_main, width - 160, draw)
            for line in wrapped:
                bbox = draw.textbbox((0, 0), line, font=font_main)
                lw = bbox[2] - bbox[0]
                lx = (width - lw) // 2
                draw.text((lx + 3, current_y + 3), line, font=font_main, fill=(0, 0, 0, 255))
                draw.text((lx, current_y), line, font=font_main, fill=text_color)
                current_y += 70

        # Brand logo
        sticker_path = ASSETS_DIR / "sticker_clean.png"
        if sticker_path.exists():
            stk = Image.open(sticker_path).convert("RGBA")
            sw = 270
            sh = int(stk.height * (sw / stk.width))
            stk = stk.resize((sw, sh), Image.Resampling.LANCZOS)
            img.paste(stk, ((width - sw) // 2, height - sh - 55), stk)

        img.save(output_png, "PNG")

    def create_vlogger_pro_video(
        self,
        topic: str = "Turkiyada 100% grant yutish",
        lang: str = "uz",
        music_type: str = "blok3",
        output_filename: str = None
    ) -> dict:
        """
        Builds a multi-scene Fastlane Pro UGC Vlogger Video:
        - Act 1 (0 to 3.5s): Real Vlogger talking directly to camera (Handheld vlog)
        - Act 2 (3.5 to 7.2s): 4K Drone B-roll cut with punch zoom + whoosh
        - Act 3 (7.2 to 10.8s): Real Vlogger explains value proposition
        - Act 4 (10.8 to 13.5s): Final CTA card & Arkadaş logo
        """
        out_name = output_filename or f"fastlane_pro_{random.randint(1000, 9999)}.mp4"
        out_mp4 = OUTPUT_DIR / out_name

        # 1. Script
        script = self.generate_viral_script(topic, lang=lang)
        h = script["hook"]
        v = script["value"]
        c = script["cta"]
        full_text = f"{h} {v} {c}"

        # 2. Expressive Audio
        temp_voice = OUTPUT_DIR / f"temp_voice_pro_{random.randint(100, 999)}.mp3"
        self.voice_studio.generate_expressive_voice(full_text, temp_voice, lang=lang)

        # Measure voice duration
        cmd = [FFPROBE_BIN, "-i", str(temp_voice), "-show_entries", "format=duration", "-v", "quiet", "-of", "csv=p=0"]
        dur = float(subprocess.run(cmd, capture_output=True, text=True).stdout.strip() or 12.0)
        total_dur = max(dur + 1.2, 12.5)

        t1 = round(total_dur * 0.28, 2)  # Act 1 end (e.g. 3.5s)
        t2 = round(total_dur * 0.62, 2)  # Act 2 end (e.g. 7.8s)
        t3 = round(total_dur * 0.88, 2)  # Act 3 end (e.g. 11.0s)
        t4 = round(total_dur, 2)         # Act 4 end (e.g. 12.5s)

        # 3. Subtitle Cards
        card1 = OUTPUT_DIR / f"temp_c1_{random.randint(100, 999)}.png"
        card2 = OUTPUT_DIR / f"temp_c2_{random.randint(100, 999)}.png"
        card3 = OUTPUT_DIR / f"temp_c3_{random.randint(100, 999)}.png"
        card4 = OUTPUT_DIR / f"temp_c4_{random.randint(100, 999)}.png"

        self.render_overlay_card("🔥 VIRAL SAVOL", h, (255, 255, 255, 255), card1, style="lower_third")
        self.render_overlay_card("💡 ASL HAQIQAT", v, (255, 215, 0, 255), card2, style="card")
        self.render_overlay_card("🚀 IMTIHONSIZ QABUL", v, (0, 230, 255, 255), card3, style="lower_third")
        self.render_overlay_card("📲 HOZIROQ YOZING", c, (100, 255, 150, 255), card4, style="card")

        # 4. Video Clips (Vlogger + Drone B-Roll)
        vlogger_clip = MILA_DIR / "ugc_vlogger_walking.mp4"
        drone_clips = list(CLEAN_VIDEOS_DIR.glob("*.mp4"))
        drone_clip = random.choice(drone_clips) if drone_clips else vlogger_clip

        # 5. Audio tracks
        music_file = AUDIO_DIR / "trend_blok3_hook.mp3" if music_type == "blok3" else AUDIO_DIR / "inspiring_travel_vibe.mp3"
        whoosh = AUDIO_DIR / "whoosh_sfx.aac"
        pop = AUDIO_DIR / "pop_sfx.aac"

        # FFmpeg Filter Graph with Fastlane Multi-Scene Rapid Cuts:
        # [0:v] = Vlogger clip
        # [1:v] = Drone b-roll
        # [2:v] = Card 1
        # [3:v] = Card 2
        # [4:v] = Card 3
        # [5:v] = Card 4
        # [6:a] = Voice
        # [7:a] = Music
        # [8:a] = Whoosh
        # [9:a] = Pop
        filter_complex = (
            f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1/1,trim=0:{t1},setpts=PTS-STARTPTS[v1];"
            f"[1:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1/1,trim=0:{t2-t1},setpts=PTS-STARTPTS[v2];"
            f"[0:v]scale=1240:2204:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1/1,trim={t1}:{t1+t3-t2},setpts=PTS-STARTPTS[v3];"
            f"[1:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1/1,trim={t2-t1}:{t2-t1+t4-t3},setpts=PTS-STARTPTS[v4];"
            f"[v1][v2][v3][v4]concat=n=4:v=1:a=0[vbase];"
            f"[vbase][2:v]overlay=0:0:enable='between(t,0,{t1})'[vo1];"
            f"[vo1][3:v]overlay=0:0:enable='between(t,{t1},{t2})'[vo2];"
            f"[vo2][4:v]overlay=0:0:enable='between(t,{t2},{t3})'[vo3];"
            f"[vo3][5:v]overlay=0:0:enable='between(t,{t3},{t4})'[vout];"
            f"[6:a]volume=1.0[voice];"
            f"[7:a]volume=0.15,afade=t=out:st={t4-1.5}:d=1.5[music];"
            f"[8:a]adelay={int(t1*1000)}|{int(t1*1000)},volume=0.40[sfx1];"
            f"[8:a]adelay={int(t2*1000)}|{int(t2*1000)},volume=0.40[sfx2];"
            f"[9:a]adelay={int(t3*1000)}|{int(t3*1000)},volume=0.35[sfx3];"
            f"[voice][music][sfx1][sfx2][sfx3]amix=inputs=5:duration=first[aout]"
        )

        cmd = [
            FFMPEG_BIN, "-y",
            "-stream_loop", "-1", "-i", str(vlogger_clip),
            "-stream_loop", "-1", "-i", str(drone_clip),
            "-i", str(card1),
            "-i", str(card2),
            "-i", str(card3),
            "-i", str(card4),
            "-i", str(temp_voice),
            "-i", str(music_file),
            "-i", str(whoosh),
            "-i", str(pop),
            "-filter_complex", filter_complex,
            "-map", "[vout]",
            "-map", "[aout]",
            "-t", str(t4),
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            str(out_mp4)
        ]

        print(f"[FASTLANE PRO] Rendering 4-Scene Rapid Cut Vlogger Reel ({t4:.1f}s)...")
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print("[FFmpeg Error]:", res.stderr)
            raise RuntimeError("Vlogger Pro video render failed")

        for tmp in [card1, card2, card3, card4, temp_voice]:
            if tmp.exists(): tmp.unlink()

        print(f"[SUCCESS] Fastlane Pro Vlogger Video Created: {out_mp4}")
        return {
            "media_path": str(out_mp4),
            "topic": topic,
            "duration": t4,
            "caption": script["caption"]
        }

if __name__ == "__main__":
    vpro = FastlaneVloggerPro()
    res = vpro.create_vlogger_pro_video(music_type="blok3")
    print("Vlogger Pro Video:", res["media_path"])
