#!/usr/bin/env python3
"""
Arkadaş Consulting - Meaningful Storytelling Reels Engine (Ma'noli Reels Motoru)
Creates high-retention, educational & inspiring 9:16 vertical Reels:
1. 3-Act Narrative Rhythm:
   - Act 1 (Hook/Myth): Provocative question addressing student fears (0s - ~3.5s)
   - Act 2 (Insight/Value): Real solutions, 100% grants & university benefits (~3.5s - ~7.5s)
   - Act 3 (Proof & CTA): Arkadaş Consulting guarantees (0 advance payment) & action (~7.5s - end)
2. Clean, unbranded stock vertical video background (StockVideoEngine).
3. Dynamic, time-coded subtitle cards synchronized to the spoken words via FFmpeg enable='between(t,...)'.
4. Authentic Uzbek Neural Voiceover (uz-UZ-MadinaNeural).
5. Balanced acoustic / lo-fi background music with smart audio ducking.
6. Clean Arkadaş Consulting trust badge & branding.
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
AUDIO_DIR = ASSETS_DIR / "audio"
OUTPUT_DIR = BASE_DIR / "output"
FFMPEG_BIN = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"
FFPROBE_BIN = "/opt/homebrew/opt/ffmpeg-full/bin/ffprobe"

from engine.ai_brain import AIBrain
from engine.stock_video_engine import StockVideoEngine
from templates.template5_video import get_font, wrap_text

class StoryReelsEngine:
    def __init__(self):
        self.ai = AIBrain()
        self.stock = StockVideoEngine()
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    def generate_story_script(self, topic: str = "Turkiyada grant va kafolatli qabul") -> dict:
        """
        Uses AI Brain to generate a 3-act storytelling Reels script.
        """
        prompt = (
            "Sen Arkadaş Consulting kompaniyasining bosh kreativ kopyrayterisan.\n"
            f"Mavzu: '{topic}'.\n\n"
            "Instagram Reels va TikTok uchun o'ta ma'noli, yoshlar e'tiborini 1-sekunddayoq "
            "tortib oluvchi 3 bosqichli 'Storytelling' (hikoyaviy) ssenariy yoz:\n\n"
            "1. ACT 1 (HOOK / MIF): Talabalarni qo'rqitadigan mashhur xato fikr yoki qiziq savol (maksimum 6-7 so'z).\n"
            "2. ACT 2 (INSIGHT / HAQIQAT): Vaziyatning asl yechimi, grantlar, imtihonsiz qabul haqida qat'iy ma'lumot (maksimum 8-10 so'z).\n"
            "3. ACT 3 (CTA / HARAKAT): Arkadaş Consulting kafolati (oldindan to'lov yo'q) va harakatga chaqiruv (maksimum 6-7 so'z).\n"
            "4. CAPTION: To'liq Telegram/Instagram post matni (foydali maslahatlar, emojilar va hashtaglar bilan).\n\n"
            "Javobni aniq JSON formatida qaytar:\n"
            "{\n"
            '  "act1_hook": "...",\n'
            '  "act2_insight": "...",\n'
            '  "act3_cta": "...",\n'
            '  "caption": "..."\n'
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
            "act1_hook": "Turkiyada o'qish qimmat deb o'ylaysizmi?",
            "act2_insight": "Faqat attestat bilan 100% grant yutish mumkin!",
            "act3_cta": "Oldindan to'lov yo'q — @arkadasuz ga yozing!",
            "caption": (
                "Ko'pchilik Turkiyada ta'lim olish uchun minglab dollar kerak deb xato o'ylaydi ❌\n\n"
                "Aslida esa faqatgina maktab attestati yoki kollej diplomi baholari orqali nufuzli "
                "davlat universitetlariga 100% gacha grant asosida kirish imkoni mavjud! 🇹🇷🎓\n\n"
                "Arkadaş Consulting bilan:\n"
                "✅ Imtihonsiz qabul\n"
                "✅ 0$ oldindan to'lov — qabul xati qo'lingizga tekkandan keyin to'laysiz!\n"
                "✅ Yotoqxona, viza va aeroportda kutib olish kafolati\n\n"
                "Batafsil ma'lumot uchun profilga kiring yoki @arkadasuz ga yozing! 🚀"
            )
        }

    def render_overlay_card(
        self,
        headline: str,
        subtext: str,
        badge_text: str,
        output_png: Path,
        accent_color: str = "#FFD700"
    ):
        """Renders an aesthetic transparent PNG subtitle card with contrast scrim."""
        width, height = 1080, 1920
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Top contrast gradient scrim for maximum text legibility
        gradient = Image.new("RGBA", (width, int(height * 0.55)), (0, 0, 0, 0))
        g_draw = ImageDraw.Draw(gradient)
        for y in range(gradient.height):
            alpha = int(185 * (1.0 - (y / gradient.height) ** 1.5))
            g_draw.line([(0, y), (width, y)], fill=(10, 15, 25, alpha))
        img.paste(gradient, (0, 0), gradient)

        # Fonts
        font_badge = get_font("Arial Bold", 36)
        font_head = get_font("Georgia Bold", 62)
        font_sub = get_font("Georgia Italic", 44)

        current_y = 260

        # 1. Badge Pill
        if badge_text:
            badge_clean = re.sub(r'[^\w\s\-\.\!\?\:\/]', '', badge_text).strip()
            bbox = draw.textbbox((0, 0), badge_clean, font=font_badge)
            bw = bbox[2] - bbox[0] + 50
            bh = bbox[3] - bbox[1] + 24
            bx = (width - bw) // 2
            draw.rounded_rectangle(
                [bx, current_y, bx + bw, current_y + bh],
                radius=18,
                fill=(20, 45, 90, 220),
                outline=(0, 210, 255, 255),
                width=2
            )
            draw.text((bx + 25, current_y + 10), badge_clean, font=font_badge, fill=(255, 255, 255, 255))
            current_y += bh + 45

        # 2. Main Headline
        lines = wrap_text(headline, font_head, width - 160, draw)
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font_head)
            lw = bbox[2] - bbox[0]
            lx = (width - lw) // 2
            # Drop shadow
            draw.text((lx + 3, current_y + 3), line, font=font_head, fill=(0, 0, 0, 240))
            draw.text((lx, current_y), line, font=font_head, fill=accent_color)
            current_y += 76

        current_y += 20

        # 3. Subtext
        if subtext:
            sub_lines = wrap_text(subtext, font_sub, width - 180, draw)
            for sline in sub_lines:
                bbox = draw.textbbox((0, 0), sline, font=font_sub)
                sw = bbox[2] - bbox[0]
                sx = (width - sw) // 2
                draw.text((sx + 2, current_y + 2), sline, font=font_sub, fill=(0, 0, 0, 220))
                draw.text((sx, current_y), sline, font=font_sub, fill=(255, 255, 255, 255))
                current_y += 56

        # Bottom Arkadaş Brand Sticker
        sticker_path = ASSETS_DIR / "sticker_clean.png"
        if sticker_path.exists():
            stk = Image.open(sticker_path).convert("RGBA")
            stk_w = 340
            stk_h = int(stk.height * (stk_w / stk.width))
            stk = stk.resize((stk_w, stk_h), Image.Resampling.LANCZOS)
            img.paste(stk, ((width - stk_w) // 2, height - stk_h - 100), stk)

        img.save(output_png, "PNG")

    def generate_spoken_audio(self, full_text: str, output_path: Path) -> bool:
        """Generates Uzbek voiceover via edge-tts."""
        try:
            clean = re.sub(r'[*#_~`@]', '', full_text)
            clean = clean.replace('@arkadasuz', 'Arkadaş Consulting')
            cmd = [
                "edge-tts",
                "--voice", "uz-UZ-MadinaNeural",
                "--text", clean,
                "--write-media", str(output_path)
            ]
            res = subprocess.run(cmd, capture_output=True)
            return res.returncode == 0 and output_path.exists()
        except Exception as e:
            print(f"[TTS Error] {e}")
            return False

    def get_audio_duration(self, audio_path: Path) -> float:
        """Calculates audio duration using ffprobe."""
        cmd = [
            FFPROBE_BIN,
            "-i", str(audio_path),
            "-show_entries", "format=duration",
            "-v", "quiet", "-of", "csv=p=0"
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            return float(res.stdout.strip())
        except Exception:
            return 10.0

    def create_meaningful_reel(
        self,
        topic: str = "Turkiyada 100% grant va bepul yotoqxona",
        output_filename: str = None
    ) -> dict:
        """
        Renders a full 3-Act storytelling Reel using clean stock video B-roll,
        dynamic time-coded captions, and authentic voiceover.
        """
        out_name = output_filename or f"story_reel_{random.randint(1000, 9999)}.mp4"
        out_mp4 = OUTPUT_DIR / out_name

        temp_ov1 = OUTPUT_DIR / f"temp_act1_{random.randint(100, 999)}.png"
        temp_ov2 = OUTPUT_DIR / f"temp_act2_{random.randint(100, 999)}.png"
        temp_ov3 = OUTPUT_DIR / f"temp_act3_{random.randint(100, 999)}.png"
        temp_voice = OUTPUT_DIR / f"temp_voice_{random.randint(100, 999)}.mp3"

        # 1. Generate Narrative Script
        print(f"[STORY REELS] Writing 3-act narrative on: '{topic}'...")
        script = self.generate_story_script(topic)
        act1 = script.get("act1_hook", "Turkiyada o'qish qimmatmi?")
        act2 = script.get("act2_insight", "Attestat bilan 100% grant yutish mumkin!")
        act3 = script.get("act3_cta", "Oldindan to'lov yo'q — @arkadasuz ga yozing!")

        # 2. Select Clean Video B-Roll (Never ChatExport)
        bg_video = self.stock.get_clean_video(topic)
        print(f"[STORY REELS] Selected clean B-roll footage: {bg_video.name}")

        # 3. Generate Voiceover
        spoken_script = f"{act1}. {act2}. {act3}."
        voice_success = self.generate_spoken_audio(spoken_script, temp_voice)
        total_duration = self.get_audio_duration(temp_voice) if voice_success else 10.0
        total_duration = max(total_duration + 1.0, 9.0)

        # Dynamic Act Timestamps
        t1 = round(total_duration * 0.33, 2)
        t2 = round(total_duration * 0.70, 2)
        t3 = round(total_duration, 2)

        # 4. Render 3 Overlays for the 3 Acts
        self.render_overlay_card(
            headline=act1.upper(),
            subtext="Ko'pchilik shunday deb o'ylaydi...",
            badge_text="💡 FAQAT TALABALAR UCHUN",
            output_png=temp_ov1,
            accent_color="#FFFFFF"
        )
        self.render_overlay_card(
            headline=act2.upper(),
            subtext="Imtihonsiz va rasmiy qabul xati bilan!",
            badge_text="🔥 ASL HAQIQAT",
            output_png=temp_ov2,
            accent_color="#FFD700"
        )
        self.render_overlay_card(
            headline=act3.upper(),
            subtext="Kafolatli va rasmiy shartnoma asosida",
            badge_text="🚀 ARKADAŞ BILAN BOSHLANG",
            output_png=temp_ov3,
            accent_color="#00D2FF"
        )

        # 5. Background music selection
        audios = list(AUDIO_DIR.glob("*.mp3"))
        chosen_audio = random.choice(audios) if audios else None

        # 6. Composite with FFmpeg (Timed Subtitles & Audio Ducking)
        filter_complex = (
            f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[vbg];"
            f"[vbg][1:v]overlay=0:0:enable='between(t,0,{t1})'[v1];"
            f"[v1][2:v]overlay=0:0:enable='between(t,{t1},{t2})'[v2];"
            f"[v2][3:v]overlay=0:0:enable='between(t,{t2},{t3})'[vout]"
        )

        ffmpeg_cmd = [
            FFMPEG_BIN, "-y",
            "-stream_loop", "-1",
            "-i", str(bg_video),
            "-i", str(temp_ov1),
            "-i", str(temp_ov2),
            "-i", str(temp_ov3),
            "-i", str(temp_voice)
        ]

        if chosen_audio:
            ffmpeg_cmd.extend([
                "-i", str(chosen_audio),
                "-filter_complex", (
                    f"{filter_complex};"
                    f"[4:a]volume=1.0[voice];"
                    f"[5:a]volume=0.15,afade=t=out:st={t3-1.5}:d=1.5[music];"
                    f"[voice][music]amix=inputs=2:duration=first[aout]"
                ),
                "-map", "[vout]",
                "-map", "[aout]"
            ])
        else:
            ffmpeg_cmd.extend([
                "-filter_complex", filter_complex,
                "-map", "[vout]",
                "-map", "4:a"
            ])

        ffmpeg_cmd.extend([
            "-t", str(t3),
            "-c:v", "libx264", "-preset", "fast", "-crf", "21",
            "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            str(out_mp4)
        ])

        print(f"[STORY REELS] Rendering high-retention 3-Act Reel ({total_duration:.1f}s)...")
        res = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print("[FFmpeg Error]:", res.stderr)
            raise RuntimeError("Story Reel rendering failed")

        # Cleanup temp overlays
        for tmp in [temp_ov1, temp_ov2, temp_ov3, temp_voice]:
            if tmp.exists():
                tmp.unlink()

        print(f"[SUCCESS] Meaningful Storytelling Reel Created: {out_mp4}")

        return {
            "type": "story_reel",
            "media_path": str(out_mp4),
            "topic": topic,
            "broll_used": bg_video.name,
            "duration": t3,
            "caption": script.get("caption", "")
        }

if __name__ == "__main__":
    engine = StoryReelsEngine()
    res = engine.create_meaningful_reel()
    print("Test finished:", res["media_path"])
